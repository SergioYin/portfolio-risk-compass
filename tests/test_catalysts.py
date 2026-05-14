import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.catalysts import (
    build_catalyst_checklist,
    parse_catalysts_payload,
    render_catalyst_markdown,
)
from portfolio_risk_compass.cli import main


class CatalystTests(unittest.TestCase):
    def test_build_checklist_sorts_by_date_and_flags_relative_to_as_of(self):
        catalysts = parse_catalysts_payload(
            [
                {
                    "symbol": "bbb",
                    "date": "2026-05-20",
                    "title": "Product launch",
                    "importance": "medium",
                    "thesis_link": "https://example.com/bbb",
                    "action": "Check launch conversion readout",
                },
                {
                    "symbol": "AAA",
                    "date": "2026-05-10",
                    "title": "Earnings",
                    "importance": "high",
                    "thesis_link": "https://example.com/aaa",
                    "action": "Review margin guidance",
                },
                {
                    "symbol": "CCC",
                    "date": "2026-05-15",
                    "title": "FDA decision",
                    "importance": "critical",
                    "thesis_link": "https://example.com/ccc",
                    "action": "Decide whether to trim event risk",
                },
            ]
        )

        checklist = build_catalyst_checklist(catalysts, as_of="2026-05-15")

        self.assertEqual(
            [item["symbol"] for item in checklist["catalysts"]],
            ["AAA", "CCC", "BBB"],
        )
        self.assertEqual(
            [item["flag"] for item in checklist["catalysts"]],
            ["overdue", "today", "upcoming"],
        )
        self.assertEqual(checklist["metadata"]["overdue_count"], 1)
        self.assertEqual(checklist["metadata"]["today_count"], 1)
        self.assertEqual(checklist["metadata"]["upcoming_count"], 1)

    def test_parse_requires_fields_and_iso_date(self):
        with self.assertRaisesRegex(ValueError, "missing required field thesis_link"):
            parse_catalysts_payload(
                [
                    {
                        "symbol": "AAA",
                        "date": "2026-05-15",
                        "title": "Earnings",
                        "importance": "high",
                        "action": "Review guidance",
                    }
                ]
            )

        with self.assertRaisesRegex(ValueError, "must use YYYY-MM-DD"):
            parse_catalysts_payload(
                [
                    {
                        "symbol": "AAA",
                        "date": "05/15/2026",
                        "title": "Earnings",
                        "importance": "high",
                        "thesis_link": "https://example.com/aaa",
                        "action": "Review guidance",
                    }
                ]
            )

    def test_markdown_renders_grouped_checklist(self):
        catalysts = parse_catalysts_payload(
            [
                {
                    "symbol": "AAA",
                    "date": "2026-05-14",
                    "title": "Earnings",
                    "importance": "high",
                    "thesis_link": "https://example.com/aaa",
                    "action": "Review margin guidance",
                }
            ]
        )
        markdown = render_catalyst_markdown(
            build_catalyst_checklist(catalysts, as_of="2026-05-15")
        )

        self.assertIn("# Catalyst Checklist", markdown)
        self.assertIn("## Overdue", markdown)
        self.assertIn("- [ ] 2026-05-14 **AAA** (high) - Earnings", markdown)
        self.assertIn("Action: Review margin guidance", markdown)

    def test_cli_writes_markdown_and_prints_json_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "catalysts.json"
            markdown_path = root / "catalysts.md"
            fixture.write_text(
                json.dumps(
                    [
                        {
                            "symbol": "AAA",
                            "date": "2026-05-14",
                            "title": "Earnings",
                            "importance": "high",
                            "thesis_link": "https://example.com/aaa",
                            "action": "Review margin guidance",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                main(
                    [
                        "catalysts",
                        str(fixture),
                        "--as-of",
                        "2026-05-15",
                        "--markdown",
                        str(markdown_path),
                    ]
                ),
                0,
            )
            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(["catalysts", str(fixture), "--as-of", "2026-05-15"]),
                    0,
                )
            markdown = markdown_path.read_text(encoding="utf-8")

        self.assertIn("## Overdue", markdown)
        printed = json.loads(stdout.write.call_args.args[0])
        self.assertEqual(printed["catalysts"][0]["flag"], "overdue")


if __name__ == "__main__":
    unittest.main()
