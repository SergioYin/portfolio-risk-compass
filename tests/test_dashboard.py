import json
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.dashboard import build_dashboard_html
from portfolio_risk_compass.dashboard import build_showcase_walkthrough
from portfolio_risk_compass.dashboard import render_dashboard_snippet_html
from portfolio_risk_compass.dashboard import render_gallery_markdown
from portfolio_risk_compass.dashboard import render_public_gallery_html
from portfolio_risk_compass.dashboard import render_showcase_walkthrough_markdown
from portfolio_risk_compass.demo import build_demo_bundle


class _HrefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.sources = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "href" in attributes:
            self.hrefs.append(attributes["href"])
        if "src" in attributes:
            self.sources.append(attributes["src"])


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

    def test_showcase_renderers_link_dashboard_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            manifest = build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

        gallery = render_gallery_markdown(manifest)
        snippet = render_dashboard_snippet_html(manifest)

        self.assertIn("# Dashboard Output Gallery", gallery)
        self.assertIn("[dashboard.html](dashboard.html)", gallery)
        self.assertIn("[walkthrough.md](walkthrough.md)", gallery)
        self.assertIn("[exposure_report.md](exposure_report.md)", gallery)
        self.assertIn("Template Galleries", gallery)
        self.assertIn("portfolio-risk-compass-showcase", snippet)
        self.assertIn('href="dashboard.html"', snippet)
        self.assertIn('href="walkthrough.md"', snippet)
        self.assertIn("JavaScript-free dashboard", snippet)
        self.assertIn("not investment advice", gallery)
        self.assertIn("not investment advice", snippet)
        self.assertNotIn("<script", snippet.lower())

    def test_public_gallery_html_ties_release_route_and_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            manifest = build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

        html = render_public_gallery_html(manifest)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Portfolio Risk Compass Public Gallery", html)
        self.assertIn('href="dashboard.html"', html)
        self.assertIn('href="index.json"', html)
        self.assertIn('href="visual_release_checklist.md"', html)
        self.assertIn('href="release_manifest.md"', html)
        self.assertIn('href="docs_export.md"', html)
        self.assertIn("PYTHONPATH=src python -m portfolio_risk_compass demo-bundle", html)
        self.assertIn("PYTHONPATH=src python scripts/selfcheck.py", html)
        self.assertIn("PYTHONPATH=src python scripts/privacy_scan.py", html)
        self.assertIn("Does not connect to brokers", html)
        self.assertIn("Does not fetch live market data", html)
        self.assertIn("Does not provide recommendations", html)
        self.assertNotIn("<script", html.lower())

    def test_public_gallery_html_escapes_content_and_rejects_unsafe_links(self):
        manifest = {
            "bundle": "demo",
            "as_of": "<img src=x onerror=alert(1)>",
            "artifacts": [
                {
                    "path": "exposure_report.md",
                    "format": 'markdown"><script>alert(1)</script>',
                    "description": "<b>unsafe</b>",
                }
            ],
        }

        html = render_public_gallery_html(
            manifest,
            dashboard_path="javascript:alert(1)",
        )
        parser = _HrefParser()
        parser.feed(html)

        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)
        self.assertIn("markdown&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;b&gt;unsafe&lt;/b&gt;", html)
        self.assertIn('<span class="link-label">Static dashboard</span>', html)
        self.assertNotIn('href="javascript:alert(1)"', html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("<b>unsafe</b>", html)
        self.assertEqual(parser.sources, [])

    def test_checked_in_public_gallery_links_are_local_and_resolve(self):
        gallery_path = Path("examples/outputs/gallery.html")
        parser = _HrefParser()
        parser.feed(gallery_path.read_text(encoding="utf-8"))

        self.assertEqual(parser.sources, [])
        for href in parser.hrefs:
            self.assertFalse(href.startswith(("http://", "https://", "file://", "//")))
            if href.startswith("#"):
                continue
            self.assertTrue(
                (gallery_path.parent / href).is_file(),
                f"missing public gallery target: {href}",
            )

    def test_showcase_walkthrough_summarizes_each_template_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            manifest = build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
            )

            walkthrough = build_showcase_walkthrough(manifest, output_dir)
            markdown = render_showcase_walkthrough_markdown(walkthrough)

        self.assertEqual(walkthrough["case_count"], 4)
        self.assertEqual(walkthrough["cases"][0]["name"], "Base Demo")
        self.assertEqual(walkthrough["cases"][1]["name"], "Cash Rebalance")
        self.assertEqual(walkthrough["cases"][0]["metrics"]["guardrail_status"], "FAIL")
        self.assertEqual(walkthrough["cases"][1]["metrics"]["guardrail_status"], "WARN")
        self.assertEqual(walkthrough["cases"][2]["metrics"]["guardrail_status"], "WARN")
        self.assertIn("Compare template risk postures", markdown)
        self.assertIn("[templates/leveraged-sleeve/stress.md]", markdown)
        self.assertIn("not investment advice", markdown)


if __name__ == "__main__":
    unittest.main()
