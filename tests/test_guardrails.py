from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.config import AnalysisConfig
from portfolio_risk_compass.guardrails import (
    ReviewDates,
    evaluate_guardrails,
    render_guardrail_markdown,
)
from portfolio_risk_compass.holdings import Holding


class GuardrailTests(unittest.TestCase):
    def test_evaluate_guardrails_returns_pass_warn_and_fail_items(self):
        holdings = [
            Holding("AAA", Decimal("1"), Decimal("55"), "Equity", "Tech", "US", "USD"),
            Holding("BBB", Decimal("1"), Decimal("35"), "Equity", "Tech", "US", "USD"),
            Holding("CASH", Decimal("1"), Decimal("10"), "Cash", "Cash", "US", "USD"),
        ]

        review = evaluate_guardrails(
            holdings,
            AnalysisConfig(
                max_position_pct=Decimal("50"),
                max_sector_pct=Decimal("80"),
                min_cash_pct=Decimal("10"),
                max_leverage_multiple=Decimal("1.25"),
                required_review_cadence_days=30,
            ),
            _review_dates("2026-05-15", "2026-04-01"),
        )

        statuses = {(item["check"], item["scope"]): item["status"] for item in review["items"]}

        self.assertEqual(review["metadata"]["overall_status"], "FAIL")
        self.assertEqual(statuses[("max_position_pct", "AAA")], "FAIL")
        self.assertEqual(statuses[("max_sector_pct", "Tech")], "FAIL")
        self.assertEqual(statuses[("min_cash_pct", "Cash")], "WARN")
        self.assertEqual(statuses[("max_leverage_multiple", "portfolio")], "PASS")
        self.assertEqual(
            statuses[("required_review_cadence_days", "portfolio")], "FAIL"
        )

    def test_missing_last_review_date_warns_when_cadence_is_required(self):
        review = evaluate_guardrails(
            [Holding("CASH", Decimal("1"), Decimal("100"), "Cash", "Cash", "US", "USD")],
            AnalysisConfig(required_review_cadence_days=30),
            _review_dates("2026-05-15", None),
        )

        self.assertEqual(review["items"][0]["status"], "WARN")
        self.assertEqual(review["items"][0]["actual"], "unknown")

    def test_markdown_renderer_includes_status_table(self):
        review = evaluate_guardrails(
            [Holding("CASH", Decimal("1"), Decimal("100"), "Cash", "Cash", "US", "USD")],
            AnalysisConfig(min_cash_pct=Decimal("95")),
            _review_dates("2026-05-15", None),
        )

        markdown = render_guardrail_markdown(review)

        self.assertIn("# Portfolio Guardrail Review", markdown)
        self.assertIn("| WARN | min_cash_pct | 100.0000 | 95.0000 |", markdown)

    def test_cli_guardrails_prints_json_and_writes_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            holdings = root / "holdings.csv"
            config = root / "config.json"
            markdown = root / "guardrails.md"
            holdings.write_text(
                "\n".join(
                    [
                        "symbol,quantity,price,asset_class,sector,region,currency",
                        "AAA,1,100,Equity,Tech,US,USD",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            config.write_text(
                """
                {
                  "max_position_pct": "50",
                  "max_sector_pct": "80",
                  "required_review_cadence_days": 30,
                  "last_review_date": "2026-04-01"
                }
                """,
                encoding="utf-8",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "guardrails",
                            str(holdings),
                            "--config",
                            str(config),
                            "--snapshot-date",
                            "2026-05-15",
                            "--markdown",
                            str(markdown),
                        ]
                    ),
                    0,
                )

            printed = stdout.write.call_args
            markdown_text = markdown.read_text(encoding="utf-8")

        self.assertIsNone(printed)
        self.assertIn("# Portfolio Guardrail Review", markdown_text)


def _review_dates(snapshot_date: str, last_review_date: str | None) -> ReviewDates:
    return ReviewDates(
        snapshot_date=date.fromisoformat(snapshot_date),
        last_review_date=(
            date.fromisoformat(last_review_date)
            if last_review_date is not None
            else None
        ),
    )


if __name__ == "__main__":
    unittest.main()
