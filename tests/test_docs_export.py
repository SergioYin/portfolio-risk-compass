from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import _build_parser, main
from portfolio_risk_compass.docs_export import (
    build_docs_export,
    render_docs_html,
    render_docs_markdown,
)


class DocsExportTests(unittest.TestCase):
    def test_markdown_includes_cli_schemas_inventory_and_boundary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir) / "outputs"
            outputs_dir.mkdir()
            (outputs_dir / "exposure_report.json").write_text("{}\n", encoding="utf-8")
            docs_path = outputs_dir / "docs_export.md"

            export = build_docs_export(
                _build_parser(),
                outputs_dir=outputs_dir,
                output_path=docs_path,
            )
            markdown = render_docs_markdown(export)

        self.assertIn("## CLI Reference", markdown)
        self.assertIn("### `case-study`", markdown)
        self.assertIn("### `docs-export`", markdown)
        self.assertIn("## Input Schemas", markdown)
        self.assertIn("### holdings.csv", markdown)
        self.assertIn("`snapshot.date`", markdown)
        self.assertIn("`report.metadata.total_market_value`", markdown)
        self.assertNotIn("`metadata.snapshot_date`", markdown)
        self.assertIn("## Artifact Inventory", markdown)
        self.assertIn("| exposure_report.json | json | 3 |", markdown)
        self.assertNotIn("| docs_export.md |", markdown)
        self.assertIn("## Safety Boundary", markdown)
        self.assertIn("not investment, tax, legal, accounting, or trading advice", markdown)
        self.assertIn("## Generated Example Output", markdown)
        self.assertIn("portfolio-risk-compass docs-export", markdown)

    def test_cli_writes_markdown_docs_export(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "reference.md"
            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "docs-export",
                            "--outputs-dir",
                            "examples/outputs",
                            "--output",
                            str(output_path),
                        ]
                    ),
                    0,
                )

            markdown = output_path.read_text(encoding="utf-8")

        self.assertEqual(stdout.write.call_args.args[0], str(output_path) + "\n")
        self.assertIn("# Portfolio Risk Compass Docs Export", markdown)
        self.assertIn("### `analyze`", markdown)

    def test_html_export_is_single_file_without_javascript(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir) / "outputs"
            outputs_dir.mkdir()
            html_path = outputs_dir / "reference.html"

            with patch("sys.stdout"):
                self.assertEqual(
                    main(
                        [
                            "docs-export",
                            "--outputs-dir",
                            str(outputs_dir),
                            "--output",
                            str(html_path),
                            "--format",
                            "html",
                        ]
                    ),
                    0,
                )

            html_text = html_path.read_text(encoding="utf-8")

        self.assertIn("<!doctype html>", html_text)
        self.assertIn("<h1>Portfolio Risk Compass Docs Export</h1>", html_text)
        self.assertNotIn("<script", html_text.lower())

    def test_html_renderer_escapes_generated_content(self):
        export = build_docs_export(
            _build_parser(),
            outputs_dir=Path("does-not-exist"),
            title="Docs <Reference>",
        )
        html_text = render_docs_html(export)

        self.assertIn("Docs &lt;Reference&gt;", html_text)
        self.assertNotIn("<script", html_text.lower())


if __name__ == "__main__":
    unittest.main()
