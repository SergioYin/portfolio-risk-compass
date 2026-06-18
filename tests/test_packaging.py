import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.9/3.10 compatibility
    tomllib = None

from portfolio_risk_compass.cli import COMMAND_NAMES, main
from portfolio_risk_compass.packaging import (
    build_package_audit,
    build_release_manifest,
    render_release_manifest_markdown,
)


class PackagingCommandTests(unittest.TestCase):
    def test_pyproject_has_release_metadata_and_console_script(self):
        if tomllib is None:
            self.skipTest("tomllib is unavailable before Python 3.11")

        root = Path(__file__).resolve().parents[1]
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        project = pyproject["project"]

        self.assertEqual(project["name"], "portfolio-risk-compass")
        self.assertEqual(
            project["scripts"]["portfolio-risk-compass"],
            "portfolio_risk_compass.cli:main",
        )
        self.assertEqual(project["requires-python"], ">=3.9")
        for version in ["3.9", "3.10", "3.11", "3.12", "3.13"]:
            self.assertIn(
                f"Programming Language :: Python :: {version}",
                project["classifiers"],
            )

    def test_package_audit_reports_counts_and_missing_items(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "examples/fixtures").mkdir(parents=True)
            (root / "examples/fixtures/holdings.csv").write_text("symbol\nAAPL\n")
            (root / "examples/outputs").mkdir(parents=True)
            (root / "examples/outputs/report.json").write_text("{}\n")
            (root / "pyproject.toml").write_text("[project]\n")
            (root / "README.md").write_text("# demo\n")

            report = build_package_audit(
                root,
                command_count=len(COMMAND_NAMES),
                run_tests=False,
            )

        self.assertEqual(report["version"], "0.5.2")
        self.assertEqual(report["command_count"], 23)
        self.assertEqual(report["fixture_count"], 1)
        self.assertEqual(report["output_artifact_count"], 1)
        self.assertFalse(report["tests"]["run"])
        self.assertEqual(
            report["tests"]["command"],
            ["python", "-m", "unittest", "discover", "-s", "tests"],
        )
        self.assertIn("LICENSE", report["missing_packaging_items"])
        self.assertIn("package module", report["missing_packaging_items"])

    def test_package_audit_cli_can_run_tests_optionally(self):
        completed = type(
            "Completed",
            (),
            {"returncode": 0, "stdout": "ok\n", "stderr": ""},
        )()
        with patch("portfolio_risk_compass.packaging.subprocess.run", return_value=completed):
            with patch("sys.stdout") as stdout:
                self.assertEqual(main(["package-audit", "--run-tests"]), 0)

        report = json.loads(stdout.write.call_args.args[0])
        self.assertTrue(report["tests"]["run"])
        self.assertTrue(report["tests"]["passed"])
        self.assertEqual(report["tests"]["stdout"], "ok\n")

    def test_release_manifest_inventories_outputs_with_hashes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            output_dir.mkdir()
            json_artifact = output_dir / "report.json"
            markdown_artifact = output_dir / "notes.md"
            json_artifact.write_text('{"ok": true}\n', encoding="utf-8")
            markdown_artifact.write_text("# Notes\n", encoding="utf-8")

            manifest = build_release_manifest(output_dir)
            markdown = render_release_manifest_markdown(manifest)

        self.assertEqual(manifest["artifact_count"], 2)
        self.assertEqual(manifest["outputs_dir"], output_dir.as_posix())
        self.assertEqual([artifact["path"] for artifact in manifest["artifacts"]], [
            "notes.md",
            "report.json",
        ])
        report = manifest["artifacts"][1]
        self.assertEqual(report["format"], "json")
        self.assertEqual(
            report["sha256"],
            hashlib.sha256(b'{"ok": true}\n').hexdigest(),
        )
        self.assertIn("| report.json | json | 13 |", markdown)

    def test_release_manifest_cli_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            output_dir.mkdir()
            (output_dir / "report.json").write_text("{}\n", encoding="utf-8")
            (output_dir / "docs_export.md").write_text("# Docs\n", encoding="utf-8")
            json_path = output_dir / "release_manifest.json"
            markdown_path = output_dir / "release_manifest.md"

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "release-manifest",
                            "--outputs-dir",
                            str(output_dir),
                            "--json",
                            str(json_path),
                            "--markdown",
                            str(markdown_path),
                        ]
                    ),
                    0,
                )

            manifest = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(manifest["artifact_count"], 1)
        self.assertEqual(manifest["artifacts"][0]["path"], "report.json")
        self.assertNotIn("docs_export.md", markdown)
        self.assertIn("# Release Manifest", markdown)
        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(json_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(markdown_path) + "\n",
        )


if __name__ == "__main__":
    unittest.main()
