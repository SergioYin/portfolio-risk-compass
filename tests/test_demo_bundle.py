import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.demo import build_demo_bundle


class DemoBundleTests(unittest.TestCase):
    def test_manifest_shape_and_artifact_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            manifest = build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            index = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
            for artifact in index["artifacts"]:
                self.assertTrue((output_dir / artifact["path"]).is_file())

        expected_paths = [
            "exposure_report.json",
            "exposure_report.md",
            "snapshot_current.json",
            "catalysts.json",
            "catalysts.md",
            "guardrails.json",
            "guardrails.md",
            "stress.json",
            "stress.md",
        ]
        self.assertEqual(index, manifest)
        self.assertEqual(index["schema_version"], 1)
        self.assertEqual(index["bundle"], "portfolio-risk-compass-demo")
        self.assertEqual(index["as_of"], "2026-05-15")
        self.assertEqual(index["fixtures"]["files"], [
            "holdings.csv",
            "config.json",
            "catalysts.json",
            "scenario.json",
        ])
        self.assertEqual(
            [artifact["path"] for artifact in index["artifacts"]],
            expected_paths,
        )
        for artifact in index["artifacts"]:
            self.assertEqual(
                set(artifact),
                {"path", "format", "description", "source_fixtures", "bytes"},
            )
            self.assertIn(artifact["format"], {"json", "markdown"})
            self.assertIsInstance(artifact["source_fixtures"], list)
            self.assertGreater(artifact["bytes"], 0)

    def test_cli_demo_bundle_writes_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "demo-bundle",
                            "--fixtures-dir",
                            "examples/fixtures",
                            "--output-dir",
                            str(output_dir),
                            "--as-of",
                            "2026-05-15",
                        ]
                    ),
                    0,
                )

            manifest_path = output_dir / "index.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(stdout.write.call_args.args[0], str(manifest_path) + "\n")
        self.assertEqual(manifest["artifacts"][0]["path"], "exposure_report.json")


if __name__ == "__main__":
    unittest.main()
