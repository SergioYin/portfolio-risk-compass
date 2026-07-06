import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main, visual_release_checklist_main
from portfolio_risk_compass.visual_release_checklist import (
    SCHEMA_LABEL,
    build_visual_release_checklist,
    render_visual_release_checklist_markdown,
)


class VisualReleaseChecklistTests(unittest.TestCase):
    def test_checklist_combines_audit_and_direct_artifact_presence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "dashboard.html").write_text("<html>demo</html>\n", encoding="utf-8")
            (root / "public_review_walkthrough.md").write_text("# Public\n", encoding="utf-8")
            (root / "public_review_walkthrough.json").write_text("{}\n", encoding="utf-8")
            (root / "release_manifest.md").write_text("# Release\n", encoding="utf-8")
            (root / "release_manifest.json").write_text("{}\n", encoding="utf-8")

            checklist = build_visual_release_checklist(root)

        self.assertEqual(checklist["schema"], SCHEMA_LABEL)
        self.assertEqual(checklist["artifact"], "portfolio-risk-compass-visual-release-checklist")
        self.assertFalse(checklist["summary"]["ready_for_release_owner_review"])
        self.assertEqual(checklist["root"], "<absolute-path>")
        self.assertNotIn(str(root), json.dumps(checklist, sort_keys=True))
        items = {item["key"]: item for item in checklist["checklist"]}
        self.assertEqual(items["static_dashboard_present"]["status"], "pass")
        self.assertEqual(items["public_review_present"]["status"], "pass")
        self.assertEqual(items["release_manifest_present"]["status"], "pass")
        self.assertEqual(items["screenshot_guide_present"]["status"], "missing")
        self.assertIn("dashboard_screenshot_guide.md", items["screenshot_guide_present"]["missing_paths"])
        self.assertIn("no_private_data", checklist["boundaries"])

    def test_cli_writes_json_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "outputs"
            root.mkdir()
            (root / "dashboard.html").write_text("<html>demo</html>\n", encoding="utf-8")
            output = Path(temp_dir) / "checklist.json"

            with patch("sys.stdout") as stdout:
                result = main(
                    [
                        "visual-release-checklist",
                        "--root",
                        str(root),
                        "--format",
                        "json",
                        "--output",
                        str(output),
                    ]
                )

            checklist = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(stdout.write.call_args.args[0], str(output) + "\n")
        self.assertEqual(checklist["schema"], SCHEMA_LABEL)

    def test_console_script_alias_preserves_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "checklist.md"

            with patch("sys.stdout") as stdout:
                result = visual_release_checklist_main(
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
        markdown = render_visual_release_checklist_markdown(
            {
                "schema": SCHEMA_LABEL,
                "root": "examples/outputs",
                "audit_schema": "audit|v1",
                "scope": "local | only",
                "boundaries": {"no_live_data": "none | never"},
                "summary": {
                    "items": 1,
                    "required": 1,
                    "required_missing": 1,
                    "recommended_missing": 0,
                    "optional_missing": 0,
                    "ready_for_release_owner_review": False,
                    "audit_complete": False,
                },
                "checklist": [
                    {
                        "key": "demo|key",
                        "status": "missing",
                        "level": "required",
                        "evidence_paths": [],
                        "missing_paths": ["docs/a|b.md"],
                        "remediation": "run | command",
                    }
                ],
                "owner_steps": ["review | release"],
                "regeneration_commands": ["echo `demo`"],
            }
        )

        self.assertIn("local \\| only", markdown)
        self.assertIn("demo\\|key", markdown)
        self.assertIn("docs/a\\|b.md", markdown)
        self.assertIn("run \\| command", markdown)
        self.assertIn("echo \\`demo\\`", markdown)

    def test_regeneration_commands_cover_checked_artifact_formats(self):
        checklist = build_visual_release_checklist(Path("examples/outputs"))
        commands = "\n".join(checklist["regeneration_commands"])

        self.assertIn("visual-capture-audit --root examples/outputs --format json", commands)
        self.assertIn("visual-capture-audit --root examples/outputs --format markdown", commands)
        self.assertIn("visual-capture-compare --before examples/outputs/visual_capture_audit.json", commands)
        self.assertIn("--format markdown --output examples/outputs/visual_capture_compare.md", commands)
        self.assertIn("portfolio_risk_compass release-manifest", commands)
        self.assertIn("portfolio_risk_compass docs-export", commands)


if __name__ == "__main__":
    unittest.main()
