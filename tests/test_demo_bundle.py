import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.demo import build_demo_bundle
from portfolio_risk_compass.reviewer_evidence import (
    build_reviewer_evidence,
    render_reviewer_evidence_markdown,
)


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
            self.assertTrue((output_dir / "gallery.md").is_file())
            self.assertTrue((output_dir / "dashboard_snippet.html").is_file())
            self.assertTrue((output_dir / "dashboard_preview.md").is_file())
            self.assertTrue((output_dir / "walkthrough.md").is_file())
            self.assertTrue((output_dir / "walkthrough.json").is_file())
            self.assertTrue((output_dir / "case_study_comparison.md").is_file())
            self.assertTrue((output_dir / "case_study_comparison.json").is_file())
            self.assertTrue((output_dir / "reviewer_evidence.md").is_file())
            self.assertTrue((output_dir / "reviewer_evidence.json").is_file())
            self.assertTrue((output_dir / "scenario_evidence_receipt.md").is_file())
            self.assertTrue((output_dir / "scenario_evidence_receipt.json").is_file())
            self.assertTrue((output_dir / "public_review_walkthrough.md").is_file())
            self.assertTrue((output_dir / "public_review_walkthrough.json").is_file())
            self.assertTrue((output_dir / "visual_evidence_receipt.md").is_file())
            self.assertTrue((output_dir / "visual_evidence_receipt.json").is_file())
            self.assertTrue((output_dir / "dashboard_screenshot_guide.md").is_file())
            self.assertTrue((output_dir / "dashboard_screenshot_guide.json").is_file())
            preview = (output_dir / "dashboard_preview.md").read_text(encoding="utf-8")
            self.assertIn("| Summary | Total value", preview)
            self.assertIn("[Open the static dashboard](dashboard.html)", preview)
            self.assertIn("Reviewer evidence", preview)
            comparison = json.loads(
                (output_dir / "case_study_comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(comparison["case_count"], 4)
            self.assertEqual(
                [case["slug"] for case in comparison["cases"]],
                ["base-demo", "etf-core", "leveraged-sleeve", "cash-rebalance"],
            )
            self.assertEqual(
                comparison["comparison_highlights"][0]["case"],
                "Cash Rebalance",
            )
            self.assertTrue(comparison["artifact_coverage"]["complete"])
            self.assertEqual(comparison["artifact_coverage"]["missing"], [])
            self.assertIn(
                "templates/leveraged-sleeve/stress.json",
                comparison["cases"][2]["source_artifacts"]["expected"],
            )
            self.assertEqual(comparison["cases"][2]["source_artifacts"]["missing"], [])
            self.assertIn("not investment advice", comparison["safety_boundary"])
            walkthrough = json.loads(
                (output_dir / "walkthrough.json").read_text(encoding="utf-8")
            )
            self.assertEqual(walkthrough["case_count"], 4)
            self.assertEqual(
                [case["slug"] for case in walkthrough["cases"]],
                ["base-demo", "cash-rebalance", "etf-core", "leveraged-sleeve"],
            )
            self.assertIn("not investment advice", walkthrough["safety_boundary"])
            self.assertIn(
                "reviewer_evidence.json",
                walkthrough["cases"][0]["artifact_paths"],
            )
            evidence = json.loads(
                (output_dir / "reviewer_evidence.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                evidence["artifact"],
                "portfolio-risk-compass-reviewer-evidence",
            )
            self.assertEqual(
                [item["path"] for item in evidence["review_paths"]["case_study"]],
                ["case_study_comparison.md", "case_study_comparison.json"],
            )
            self.assertEqual(evidence["review_paths"]["dashboard"][0]["path"], "gallery.md")
            self.assertEqual(evidence["review_paths"]["dashboard"][0]["status"], "sidecar")
            self.assertIn(
                "examples/templates/leveraged-sleeve/scenario.json",
                evidence["review_paths"]["case_study"][0]["source_paths"],
            )
            self.assertEqual(
                [source["case"] for source in evidence["source_fixture_sets"]],
                ["base-demo", "cash-rebalance", "etf-core", "leveraged-sleeve"],
            )
            receipt = json.loads(
                (output_dir / "scenario_evidence_receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                receipt["artifact"],
                "portfolio-risk-compass-scenario-evidence-receipt",
            )
            self.assertEqual(
                [case["case"] for case in receipt["cases"]],
                ["base-demo", "cash-rebalance", "etf-core", "leveraged-sleeve"],
            )
            self.assertIn(
                "investment_advice",
                receipt["prohibited_capabilities"],
            )
            self.assertEqual(
                receipt["prohibited_capabilities"],
                [
                    "broker_connection",
                    "live_market_data",
                    "account_access",
                    "order_entry",
                    "trade_execution",
                    "portfolio_recommendations",
                    "investment_advice",
                ],
            )
            self.assertIn("not investment advice", receipt["public_safety_notice"])
            self.assertIn("order entry", receipt["public_safety_notice"])
            self.assertIn("reported as missing", receipt["review_scope"])
            self.assertEqual(
                receipt["cases"][0]["fixtures"][0]["path"],
                "examples/fixtures/holdings.csv",
            )
            self.assertEqual(
                [fixture["path"] for fixture in receipt["cases"][0]["fixtures"]],
                [
                    "examples/fixtures/holdings.csv",
                    "examples/fixtures/config.json",
                    "examples/fixtures/scenario.json",
                ],
            )
            self.assertRegex(receipt["cases"][0]["fixtures"][0]["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                receipt["cases"][0]["artifacts"][0]["path"],
                "stress.json",
            )
            self.assertEqual(
                [artifact["path"] for artifact in receipt["cases"][0]["artifacts"]],
                [
                    "stress.json",
                    "stress.md",
                    "guardrails.json",
                    "guardrails.md",
                    "dashboard.html",
                    "dashboard_preview.md",
                    "dashboard_snippet.html",
                    "gallery.md",
                    "walkthrough.md",
                    "walkthrough.json",
                ],
            )
            self.assertRegex(receipt["cases"][0]["artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
            dashboard_entry = receipt["cases"][0]["artifacts"][4]
            self.assertEqual(dashboard_entry["path"], "dashboard.html")
            self.assertEqual(dashboard_entry["status"], "missing")
            self.assertIn(
                "scenario-evidence-receipt",
                receipt["regeneration_commands"][-1],
            )
            public_review = json.loads(
                (output_dir / "public_review_walkthrough.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                public_review["artifact"],
                "portfolio-risk-compass-public-review-walkthrough",
            )
            self.assertEqual(public_review["case_count"], 4)
            self.assertIn("advice", public_review["boundary_flags"])
            self.assertIn("broker", public_review["boundary_flags"])
            self.assertIn(
                "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
                [step["command"] for step in public_review["walkthrough_steps"]],
            )
            self.assertEqual(
                public_review["review_artifacts"][0]["path"],
                "dashboard.html",
            )
            self.assertEqual(
                public_review["review_artifacts"][0]["status"],
                "missing",
            )
            self.assertRegex(
                public_review["review_artifacts"][1]["sha256"],
                r"^[0-9a-f]{64}$",
            )
            self.assertEqual(
                public_review["fixture_inputs"][0]["path"],
                "examples/fixtures/holdings.csv",
            )
            self.assertRegex(
                public_review["fixture_inputs"][0]["sha256"],
                r"^[0-9a-f]{64}$",
            )
            visual = json.loads(
                (output_dir / "visual_evidence_receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                visual["artifact"],
                "portfolio-risk-compass-visual-evidence-receipt",
            )
            self.assertEqual(
                [step["label"] for step in visual["route"]],
                [
                    "dashboard",
                    "public_review",
                    "screenshot_guide",
                    "scenario_evidence",
                    "reviewer_evidence",
                ],
            )
            self.assertIn("broker", visual["boundary_flags"])
            self.assertIn("advice", visual["boundary_flags"])
            self.assertEqual(visual["artifacts"][0]["path"], "dashboard.html")
            self.assertEqual(visual["artifacts"][0]["status"], "missing")
            self.assertEqual(
                visual["artifact_coverage"]["missing"],
                ["dashboard.html"],
            )
            self.assertRegex(visual["artifacts"][1]["sha256"], r"^[0-9a-f]{64}$")
            screenshot = json.loads(
                (output_dir / "dashboard_screenshot_guide.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                screenshot["artifact"],
                "portfolio-risk-compass-dashboard-screenshot-guide",
            )
            self.assertEqual(screenshot["capture_profile"]["browser"], "chromium")
            self.assertEqual(screenshot["capture_profile"]["viewport_width"], 1365)
            self.assertEqual(screenshot["capture_profile"]["viewport_height"], 900)
            self.assertIn("live data", screenshot["review_scope"])
            self.assertIn("broker", screenshot["boundary_flags"])
            self.assertEqual(
                screenshot["source_artifacts"][0]["path"],
                "dashboard.html",
            )
            self.assertEqual(
                screenshot["source_artifacts"][0]["status"],
                "missing",
            )
            self.assertEqual(
                screenshot["screenshot_artifacts"][0]["path"],
                "screenshots/dashboard-public-review-1365x900.png",
            )
            self.assertEqual(
                screenshot["artifact_coverage"]["missing"],
                [
                    "dashboard.html",
                    "screenshots/dashboard-public-review-1365x900.png",
                ],
            )

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
            "rebalance_watchlist.json",
            "rebalance_watchlist.md",
            "history.json",
            "history.md",
            "review_memo.md",
            "templates/cash-rebalance/exposure_report.json",
            "templates/cash-rebalance/exposure_report.md",
            "templates/cash-rebalance/snapshot_current.json",
            "templates/cash-rebalance/catalysts.json",
            "templates/cash-rebalance/catalysts.md",
            "templates/cash-rebalance/guardrails.json",
            "templates/cash-rebalance/guardrails.md",
            "templates/cash-rebalance/stress.json",
            "templates/cash-rebalance/stress.md",
            "templates/cash-rebalance/rebalance_watchlist.json",
            "templates/cash-rebalance/rebalance_watchlist.md",
            "templates/etf-core/exposure_report.json",
            "templates/etf-core/exposure_report.md",
            "templates/etf-core/snapshot_current.json",
            "templates/etf-core/catalysts.json",
            "templates/etf-core/catalysts.md",
            "templates/etf-core/guardrails.json",
            "templates/etf-core/guardrails.md",
            "templates/etf-core/stress.json",
            "templates/etf-core/stress.md",
            "templates/etf-core/rebalance_watchlist.json",
            "templates/etf-core/rebalance_watchlist.md",
            "templates/leveraged-sleeve/exposure_report.json",
            "templates/leveraged-sleeve/exposure_report.md",
            "templates/leveraged-sleeve/snapshot_current.json",
            "templates/leveraged-sleeve/catalysts.json",
            "templates/leveraged-sleeve/catalysts.md",
            "templates/leveraged-sleeve/guardrails.json",
            "templates/leveraged-sleeve/guardrails.md",
            "templates/leveraged-sleeve/stress.json",
            "templates/leveraged-sleeve/stress.md",
            "templates/leveraged-sleeve/rebalance_watchlist.json",
            "templates/leveraged-sleeve/rebalance_watchlist.md",
            "case_study_comparison.json",
            "case_study_comparison.md",
            "reviewer_evidence.json",
            "reviewer_evidence.md",
            "scenario_evidence_receipt.json",
            "scenario_evidence_receipt.md",
            "public_review_walkthrough.json",
            "public_review_walkthrough.md",
            "visual_evidence_receipt.json",
            "visual_evidence_receipt.md",
            "dashboard_screenshot_guide.json",
            "dashboard_screenshot_guide.md",
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
            "history/*.json",
        ])
        self.assertEqual(index["templates"]["template_count"], 3)
        self.assertEqual(
            [template["slug"] for template in index["templates"]["templates"]],
            ["cash-rebalance", "etf-core", "leveraged-sleeve"],
        )
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
        self.assertIn(
            "templates/etf-core/stress.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )

    def test_demo_bundle_can_skip_template_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            manifest = build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
                include_templates=False,
            )

        self.assertEqual(manifest["templates"]["template_count"], 3)
        self.assertEqual(manifest["templates"]["templates"], [])
        self.assertEqual(len(manifest["artifacts"]), 26)
        self.assertIn(
            "case_study_comparison.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )
        self.assertIn(
            "reviewer_evidence.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )
        self.assertIn(
            "scenario_evidence_receipt.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )
        self.assertIn(
            "public_review_walkthrough.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )
        self.assertIn(
            "visual_evidence_receipt.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )
        self.assertIn(
            "dashboard_screenshot_guide.json",
            [artifact["path"] for artifact in manifest["artifacts"]],
        )

    def test_cli_showcase_writes_walkthrough_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "showcase.md"
            json_path = Path(temp_dir) / "showcase.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "showcase",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            walkthrough = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Guided Walkthrough", markdown)
        self.assertIn("Cash Rebalance", markdown)
        self.assertEqual(walkthrough["artifact"], "portfolio-risk-compass-showcase-walkthrough")
        self.assertEqual(walkthrough["cases"][2]["metrics"]["guardrail_status"], "WARN")

    def test_cli_case_study_writes_comparison_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "case-study.md"
            json_path = Path(temp_dir) / "case-study.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )
            bundled_comparison = json.loads(
                (output_dir / "case_study_comparison.json").read_text(encoding="utf-8")
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "case-study",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            comparison = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Case-Study Comparison", markdown)
        self.assertIn("Leveraged Sleeve", markdown)
        self.assertIn("- Manifest coverage: complete", markdown)
        self.assertEqual(
            comparison["artifact"],
            "portfolio-risk-compass-case-study-comparison",
        )
        self.assertEqual(comparison, bundled_comparison)
        self.assertTrue(comparison["artifact_coverage"]["complete"])
        self.assertEqual(comparison["artifact_coverage"]["manifest_artifact_count"], 55)
        self.assertEqual(
            comparison["cases"][2]["metrics"]["stress_market_value_delta_pct"],
            "-8.0097",
        )

    def test_cli_reviewer_evidence_writes_trace_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "reviewer-evidence.md"
            json_path = Path(temp_dir) / "reviewer-evidence.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "reviewer-evidence",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            evidence = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Reviewer Evidence", markdown)
        self.assertIn("examples/fixtures/holdings.csv", markdown)
        self.assertEqual(evidence["review_paths"]["dashboard"][0]["status"], "sidecar")
        self.assertEqual(
            evidence["review_paths"]["case_study"][1]["source_paths"][:2],
            ["index.json", "generated JSON artifacts"],
        )
        self.assertIn(
            "examples/fixtures/holdings.csv",
            evidence["review_paths"]["case_study"][1]["source_paths"],
        )

    def test_cli_scenario_evidence_receipt_writes_hash_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "scenario-evidence.md"
            json_path = Path(temp_dir) / "scenario-evidence.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "scenario-evidence-receipt",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            receipt = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Scenario Evidence Receipt", markdown)
        self.assertIn("No live market data", markdown)
        self.assertIn("Public safety notice: Audit receipt only", markdown)
        self.assertIn("Review scope: Hashes static fixture inputs", markdown)
        self.assertEqual(receipt["cases"][0]["case"], "base-demo")
        self.assertEqual(
            [case["case"] for case in receipt["cases"]],
            ["base-demo", "cash-rebalance", "etf-core", "leveraged-sleeve"],
        )
        self.assertEqual(receipt["cases"][0]["artifacts"][1]["path"], "stress.md")
        self.assertEqual(receipt["cases"][0]["artifacts"][2]["path"], "guardrails.json")
        self.assertRegex(receipt["cases"][0]["artifacts"][2]["sha256"], r"^[0-9a-f]{64}$")

    def test_cli_public_review_writes_walkthrough_and_hash_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "public-review.md"
            json_path = Path(temp_dir) / "public-review.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )
            main(
                [
                    "dashboard",
                    str(output_dir / "index.json"),
                    str(output_dir / "dashboard.html"),
                ]
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "public-review",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            packet = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Public Review Walkthrough", markdown)
        self.assertIn("No live data", markdown)
        self.assertIn("No broker", markdown)
        self.assertIn("No advice", markdown)
        self.assertIn(
            "dashboard examples/outputs/index.json examples/outputs/dashboard.html",
            markdown,
        )
        self.assertEqual(packet["review_artifacts"][0]["status"], "present")
        self.assertRegex(packet["review_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(packet["fixture_inputs"][0]["case"], "base-demo")

    def test_cli_visual_evidence_receipt_writes_visual_route_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "visual-evidence.md"
            json_path = Path(temp_dir) / "visual-evidence.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )
            main(
                [
                    "dashboard",
                    str(output_dir / "index.json"),
                    str(output_dir / "dashboard.html"),
                ]
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "visual-evidence-receipt",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            receipt = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Visual Evidence Receipt", markdown)
        self.assertIn("No broker", markdown)
        self.assertIn("No advice", markdown)
        self.assertIn("[dashboard.html](dashboard.html)", markdown)
        self.assertEqual(receipt["artifact_coverage"]["complete"], True)
        self.assertEqual(receipt["artifact_coverage"]["missing"], [])
        self.assertEqual(receipt["artifacts"][0]["status"], "present")
        self.assertRegex(receipt["artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_cli_screenshot_guide_writes_capture_receipt_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            markdown_path = Path(temp_dir) / "screenshot-guide.md"
            json_path = Path(temp_dir) / "screenshot-guide.json"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )
            main(
                [
                    "dashboard",
                    str(output_dir / "index.json"),
                    str(output_dir / "dashboard.html"),
                ]
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "screenshot-guide",
                            "--manifest",
                            str(output_dir / "index.json"),
                            "--markdown",
                            str(markdown_path),
                            "--json",
                            str(json_path),
                        ]
                    ),
                    0,
                )

            markdown = markdown_path.read_text(encoding="utf-8")
            guide = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(
            stdout.write.call_args_list[0].args[0],
            str(markdown_path) + "\n",
        )
        self.assertEqual(
            stdout.write.call_args_list[1].args[0],
            str(json_path) + "\n",
        )
        self.assertIn("# Portfolio Risk Compass Dashboard Screenshot Guide", markdown)
        self.assertIn("No live data", markdown)
        self.assertIn("No broker", markdown)
        self.assertIn("No advice", markdown)
        self.assertIn("python -m playwright screenshot", markdown)
        self.assertIn("1365x900", markdown)
        self.assertEqual(
            guide["artifact"],
            "portfolio-risk-compass-dashboard-screenshot-guide",
        )
        self.assertEqual(guide["source_artifacts"][0]["status"], "present")
        self.assertRegex(guide["source_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(guide["screenshot_artifacts"][0]["status"], "missing")
        self.assertEqual(
            guide["artifact_coverage"]["missing"],
            ["screenshots/dashboard-public-review-1365x900.png"],
        )

    def test_reviewer_evidence_markdown_escapes_table_cells(self):
        manifest = {
            "as_of": "2026-05-15",
            "fixtures": {
                "directory": "examples/fixtures",
                "files": ["holdings.csv"],
            },
            "templates": {
                "templates": [
                    {
                        "slug": "z|case",
                        "fixture_dir": "examples/templates/z|case",
                        "fixture_files": ["config|risk.json"],
                    },
                    {
                        "slug": "a-case",
                        "fixture_dir": "examples/templates/a-case",
                        "fixture_files": ["holdings.csv"],
                    },
                ],
            },
            "artifacts": [
                {
                    "path": "case_study_comparison.md",
                    "format": "markdown",
                    "description": "case study",
                    "source_fixtures": ["index.json", "generated JSON artifacts"],
                    "bytes": 1,
                }
            ],
        }

        evidence = build_reviewer_evidence(manifest)
        evidence["review_paths"]["dashboard"][0]["path"] = "odd name|a].md"
        markdown = render_reviewer_evidence_markdown(evidence)

        self.assertEqual(
            [source["case"] for source in evidence["source_fixture_sets"]],
            ["base-demo", "a-case", "z|case"],
        )
        self.assertIn("[odd name\\|a\\].md](odd%20name%7Ca%5D.md)", markdown)
        self.assertIn("| z\\|case | `examples/templates/z\\|case` |", markdown)
        self.assertIn("`config\\|risk.json`", markdown)


if __name__ == "__main__":
    unittest.main()
