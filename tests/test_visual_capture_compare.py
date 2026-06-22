import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main, visual_capture_compare_main
from portfolio_risk_compass.visual_capture_compare import (
    SCHEMA_LABEL,
    compare_visual_capture_audits,
    read_visual_capture_audit,
    render_visual_capture_compare_markdown,
)


class VisualCaptureCompareTests(unittest.TestCase):
    def test_compare_reports_added_removed_changed_and_unchanged(self):
        before = {
            "schema": "portfolio-risk-compass-visual-capture-audit.v1",
            "root": "examples/outputs",
            "checked_artifacts": [
                {
                    "path": "dashboard.html",
                    "present": True,
                    "bytes": 10,
                    "sha256": "a" * 64,
                    "role": "static_dashboard",
                    "route": "dashboard",
                },
                {
                    "path": "old.md",
                    "present": True,
                    "bytes": 5,
                    "sha256": "b" * 64,
                    "role": "old",
                },
                {
                    "path": "same.md",
                    "present": False,
                    "bytes": None,
                    "sha256": None,
                    "role": "same",
                },
            ],
        }
        after = {
            "schema": "portfolio-risk-compass-visual-capture-audit.v1",
            "root": "examples/outputs",
            "checked_artifacts": [
                {
                    "path": "dashboard.html",
                    "present": True,
                    "bytes": 12,
                    "sha256": "c" * 64,
                    "role": "static_dashboard",
                    "route": "dashboard",
                    "render": "html",
                    "capture": {"capture_command": "chromium --screenshot"},
                },
                {
                    "path": "new.md",
                    "present": True,
                    "bytes": 7,
                    "sha256": "d" * 64,
                    "role": "new",
                },
                {
                    "path": "same.md",
                    "present": False,
                    "bytes": None,
                    "sha256": None,
                    "role": "same",
                },
            ],
        }

        comparison = compare_visual_capture_audits(before, after)

        self.assertEqual(comparison["schema"], SCHEMA_LABEL)
        self.assertEqual(
            comparison["summary"],
            {
                "before_entries": 3,
                "after_entries": 3,
                "added": 1,
                "removed": 1,
                "changed": 1,
                "unchanged": 1,
            },
        )
        self.assertEqual(comparison["added"][0]["path"], "new.md")
        self.assertEqual(comparison["removed"][0]["path"], "old.md")
        changed = comparison["changed"][0]
        self.assertEqual(changed["path"], "dashboard.html")
        self.assertEqual(
            {difference["field"] for difference in changed["differences"]},
            {"bytes", "sha256", "render", "capture_command"},
        )
        self.assertIn("no_private_data", comparison["boundaries"])

    def test_cli_writes_json_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            before = root / "before.json"
            after = root / "after.json"
            output = root / "compare.json"
            audit = {
                "checked_artifacts": [
                    {
                        "path": "dashboard.html",
                        "present": True,
                        "bytes": 1,
                        "sha256": "a" * 64,
                        "role": "static_dashboard",
                    }
                ]
            }
            before.write_text(json.dumps(audit), encoding="utf-8")
            after.write_text(json.dumps(audit), encoding="utf-8")

            with patch("sys.stdout") as stdout:
                result = main(
                    [
                        "visual-capture-compare",
                        "--before",
                        str(before),
                        "--after",
                        str(after),
                        "--format",
                        "json",
                        "--output",
                        str(output),
                    ]
                )

            comparison = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(stdout.write.call_args.args[0], str(output) + "\n")
        self.assertEqual(comparison["summary"]["unchanged"], 1)

    def test_console_script_alias_preserves_compare_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            before = root / "before.json"
            after = root / "after.json"
            output = root / "compare.md"
            audit = {"checked_artifacts": []}
            before.write_text(json.dumps(audit), encoding="utf-8")
            after.write_text(json.dumps(audit), encoding="utf-8")

            with patch("sys.stdout") as stdout:
                result = visual_capture_compare_main(
                    [
                        "--before",
                        str(before),
                        "--after",
                        str(after),
                        "--format",
                        "markdown",
                        "--output",
                        str(output),
                    ]
                )

        self.assertEqual(result, 0)
        self.assertEqual(stdout.write.call_args.args[0], str(output) + "\n")

    def test_markdown_escapes_changed_fields(self):
        markdown = render_visual_capture_compare_markdown(
            {
                "schema": SCHEMA_LABEL,
                "scope": "local | only",
                "boundaries": {"no_live_data": "none | never"},
                "summary": {
                    "before_entries": 1,
                    "after_entries": 1,
                    "added": 0,
                    "removed": 0,
                    "changed": 1,
                    "unchanged": 0,
                },
                "added": [],
                "removed": [],
                "changed": [
                    {
                        "path": "docs/a|b.md",
                        "role": "role|demo",
                        "differences": [
                            {"field": "render", "before": "old|view", "after": "new|view"}
                        ],
                    }
                ],
                "unchanged": [],
            }
        )

        self.assertIn("local \\| only", markdown)
        self.assertIn("role\\|demo", markdown)
        self.assertIn("old\\|view", markdown)

    def test_invalid_json_returns_clean_cli_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text("{bad\n", encoding="utf-8")
            after.write_text('{"checked_artifacts": []}\n', encoding="utf-8")

            with patch("sys.stderr") as stderr:
                result = main(
                    [
                        "visual-capture-compare",
                        "--before",
                        str(before),
                        "--after",
                        str(after),
                    ]
                )

        self.assertEqual(result, 2)
        message = stderr.write.call_args.args[0]
        self.assertIn("visual-capture-compare: invalid visual capture audit JSON", message)
        self.assertNotIn(str(before), message)
        self.assertNotIn("Traceback", message)

    def test_rejects_wrong_audit_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "audit.json"
            path.write_text("[]\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must be an object"):
                read_visual_capture_audit(path)

    def test_rejects_duplicate_entry_keys(self):
        audit = {
            "checked_artifacts": [
                {"path": "dashboard.html", "bytes": 1},
                {"path": "dashboard.html", "bytes": 2},
            ]
        }

        with self.assertRaisesRegex(ValueError, "duplicate visual capture audit entry key"):
            compare_visual_capture_audits(audit, {"checked_artifacts": []})


if __name__ == "__main__":
    unittest.main()
