import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.dashboard import build_dashboard_html
from portfolio_risk_compass.demo import build_demo_bundle


class DashboardTests(unittest.TestCase):
    def test_build_dashboard_from_demo_manifest_includes_sections_without_js(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            html = build_dashboard_html(output_dir / "index.json")

        self.assertIn("<!doctype html>", html)
        self.assertIn('href="#summary"', html)
        self.assertIn('id="exposure"', html)
        self.assertIn('id="guardrails"', html)
        self.assertIn('id="stress"', html)
        self.assertIn('id="catalysts"', html)
        self.assertIn("Risk boundary: FAIL.", html)
        self.assertIn("Technology sector is 54.4218% of portfolio.", html)
        self.assertIn("exposure_report.json", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("https://cdn.", html.lower())

    def test_cli_dashboard_writes_html_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            html_path = Path(temp_dir) / "dashboard.html"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(["dashboard", str(output_dir / "index.json"), str(html_path)]),
                    0,
                )

            html = html_path.read_text(encoding="utf-8")

        self.assertEqual(stdout.write.call_args.args[0], str(html_path) + "\n")
        self.assertIn("Portfolio Risk Compass Dashboard", html)
        self.assertIn("Risk Boundaries", html)

    def test_dashboard_escapes_report_and_manifest_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = {
                "schema_version": 1,
                "bundle": "demo <bundle>",
                "as_of": "2026-05-15",
                "artifacts": [
                    {
                        "path": "exposure_report.json",
                        "format": "json",
                        "description": "<img src=x onerror=alert(1)>",
                        "bytes": 1,
                    },
                    {"path": "guardrails.json", "format": "json", "description": "", "bytes": 1},
                ],
            }
            exposure = {
                "metadata": {
                    "base_currency": "USD",
                    "holding_count": 1,
                    "total_market_value": "10.00",
                    "concentration_limit_pct": "25.0000",
                    "group_by": ["sector"],
                },
                "exposures": {
                    "sector": [
                        {
                            "bucket": "<script>alert(1)</script>",
                            "market_value": "10.00",
                            "pct_of_portfolio": "100.0000",
                        }
                    ]
                },
                "concentration": [
                    {
                        "symbol": 'AAA" onclick="alert(1)',
                        "market_value": "10.00",
                        "pct_of_portfolio": "100.0000",
                        "limit_pct": "25.0000",
                    }
                ],
            }
            guardrails = {
                "metadata": {"overall_status": "WARN", "snapshot_date": "2026-05-15"},
                "items": [
                    {
                        "status": "WARN",
                        "check": "max_position_pct",
                        "scope": "AAA",
                        "actual": "100.0000",
                        "limit": "25.0000",
                        "message": "<b>near boundary</b>",
                    }
                ],
            }
            (root / "index.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "exposure_report.json").write_text(
                json.dumps(exposure), encoding="utf-8"
            )
            (root / "guardrails.json").write_text(
                json.dumps(guardrails), encoding="utf-8"
            )

            html = build_dashboard_html(root / "index.json")

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("AAA&quot; onclick=&quot;alert(1)", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)
        self.assertIn("&lt;b&gt;near boundary&lt;/b&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertNotIn("<b>near boundary</b>", html)

    def test_dashboard_can_render_single_exposure_report_json(self):
        html = build_dashboard_html(Path("examples/outputs/exposure_report.json"))

        self.assertIn("Total Value", html)
        self.assertIn("Exposure", html)
        self.assertIn("No guardrail artifact was provided.", html)


if __name__ == "__main__":
    unittest.main()
