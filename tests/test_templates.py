import json
from pathlib import Path
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.templates import (
    list_templates,
    render_template_list_markdown,
    template_manifest,
)


class TemplateGalleryTests(unittest.TestCase):
    def test_template_gallery_has_complete_named_fixtures(self):
        templates = list_templates(Path("examples/templates"))

        self.assertEqual(
            [template.slug for template in templates],
            ["cash-rebalance", "etf-core", "leveraged-sleeve"],
        )
        self.assertEqual(
            [template.name for template in templates],
            ["Cash Rebalance", "ETF Core", "Leveraged Sleeve"],
        )
        for template in templates:
            self.assertEqual(
                template.fixture_files,
                ("holdings.csv", "config.json", "catalysts.json", "scenario.json"),
            )
            for fixture_file in template.fixture_files:
                self.assertTrue((template.fixture_dir / fixture_file).is_file())

    def test_template_manifest_and_markdown(self):
        manifest = template_manifest(Path("examples/templates"))
        markdown = render_template_list_markdown(manifest)

        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["template_count"], 3)
        self.assertEqual(manifest["templates"][1]["slug"], "etf-core")
        self.assertIn("| etf-core | ETF Core |", markdown)
        self.assertIn("holdings.csv, config.json, catalysts.json, scenario.json", markdown)

    def test_template_list_cli_prints_json(self):
        with patch("sys.stdout") as stdout:
            self.assertEqual(
                main(["template-list", "--templates-dir", "examples/templates"]),
                0,
            )

        manifest = json.loads(stdout.write.call_args.args[0])
        self.assertEqual(manifest["template_count"], 3)
        self.assertEqual(manifest["templates"][2]["slug"], "leveraged-sleeve")

    def test_template_list_cli_prints_markdown(self):
        with patch("sys.stdout") as stdout:
            self.assertEqual(
                main(
                    [
                        "template-list",
                        "--templates-dir",
                        "examples/templates",
                        "--format",
                        "markdown",
                    ]
                ),
                0,
            )

        self.assertIn("# Portfolio Templates", stdout.write.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
