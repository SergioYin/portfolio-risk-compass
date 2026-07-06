import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main, visual_capture_audit_main
from portfolio_risk_compass.visual_capture_audit import (
    CHECKED_ARTIFACTS,
    SCHEMA_LABEL,
    build_visual_capture_audit,
    render_visual_capture_audit_markdown,
)


class VisualCaptureAuditTests(unittest.TestCase):
    def test_audit_hashes_present_artifacts_and_reports_missing_capture(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "dashboard.html").write_text("<html>demo</html>\n", encoding="utf-8")
            (root / "dashboard_preview.md").write_text("preview\n", encoding="utf-8")
            audit = build_visual_capture_audit(root)

        self.assertEqual(audit["schema"], SCHEMA_LABEL)
        self.assertEqual(audit["summary"]["checked"], len(CHECKED_ARTIFACTS))
        self.assertEqual(audit["summary"]["present"], 2)
        self.assertEqual(audit["summary"]["missing"], len(CHECKED_ARTIFACTS) - 2)
        self.assertFalse(audit["summary"]["complete"])
        self.assertEqual(audit["checked_artifacts"][0]["path"], "dashboard.html")
        self.assertTrue(audit["checked_artifacts"][0]["present"])
        self.assertRegex(audit["checked_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
        self.assertIn("gallery.html", [item["path"] for item in audit["checked_artifacts"]])
        self.assertIn(
            "screenshots/dashboard-public-review-1365x900.png",
            audit["missing"],
        )
        self.assertEqual(
            set(audit["boundaries"]),
            {
                "no_live_data",
                "no_broker",
                "no_orders",
                "no_position_sizing",
                "no_recommendations",
                "no_file_contents",
                "no_advice",
            },
        )
        self.assertEqual(audit["root"], "<absolute-path>")
        self.assertNotIn(str(root), json.dumps(audit, sort_keys=True))

    def test_cli_writes_json_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "outputs"
            root.mkdir()
            (root / "index.json").write_text("{}\n", encoding="utf-8")
            output = Path(temp_dir) / "audit.json"

            with patch("sys.stdout") as stdout:
                result = main(
                    [
                        "visual-capture-audit",
                        "--root",
                        str(root),
                        "--format",
                        "json",
                        "--output",
                        str(output),
                    ]
                )

            audit = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(stdout.write.call_args.args[0], str(output) + "\n")
        self.assertEqual(audit["artifact"], "portfolio-risk-compass-visual-capture-audit")
        self.assertTrue(audit["source_artifacts"][0]["present"])

    def test_console_script_alias_preserves_visual_capture_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "audit.md"

            with patch("sys.stdout") as stdout:
                result = visual_capture_audit_main(
                    [
                        "--root",
                        "examples/outputs",
                        "--format",
                        "markdown",
                        "--output",
                        str(output),
                    ]
                )

        self.assertEqual(result, 0)
        self.assertEqual(stdout.write.call_args.args[0], str(output) + "\n")

    def test_markdown_escapes_table_cells(self):
        markdown = render_visual_capture_audit_markdown(
            {
                "schema": SCHEMA_LABEL,
                "root": "examples/outputs",
                "scope": "local only",
                "boundaries": {"no_live_data": "none | never"},
                "summary": {
                    "checked": 1,
                    "present": 0,
                    "missing": 1,
                    "complete": False,
                    "recommended_capture_items": 1,
                },
                "checked_artifacts": [
                    {
                        "role": "dashboard|route",
                        "path": "docs/a|b.md",
                        "present": False,
                        "bytes": None,
                        "sha256": None,
                    }
                ],
                "recommended_capture_items": [
                    {
                        "path": "docs/a|b.md",
                        "role": "dashboard|route",
                        "reason": "missing | needed",
                        "regenerate": "run | command",
                    }
                ],
                "source_artifacts": [],
                "regeneration_commands": ["echo `demo`"],
            }
        )

        self.assertIn("none \\| never", markdown)
        self.assertIn("dashboard\\|route", markdown)
        self.assertIn("missing \\| needed", markdown)
        self.assertIn("echo \\`demo\\`", markdown)


if __name__ == "__main__":
    unittest.main()
