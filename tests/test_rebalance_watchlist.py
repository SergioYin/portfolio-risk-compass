from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.analysis import analyze_portfolio
from portfolio_risk_compass.cli import main
from portfolio_risk_compass.config import AnalysisConfig
from portfolio_risk_compass.guardrails import ReviewDates, evaluate_guardrails
from portfolio_risk_compass.holdings import Holding
from portfolio_risk_compass.rebalance_watchlist import (
    SAFETY_WORDING,
    build_rebalance_watchlist,
    render_rebalance_watchlist_json,
    render_rebalance_watchlist_markdown,
)
from portfolio_risk_compass.stress import ScenarioShock, StressScenario, stress_portfolio


class RebalanceWatchlistTests(unittest.TestCase):
    def test_watchlist_combines_reasons_by_review_subject(self):
        holdings = [
            Holding("AAA", Decimal("1"), Decimal("60"), "Equity", "Tech", "US", "USD"),
            Holding("BBB", Decimal("1"), Decimal("30"), "Bond", "Gov", "US", "USD"),
            Holding("CASH", Decimal("1"), Decimal("10"), "Cash", "Cash", "US", "USD"),
        ]
        config = AnalysisConfig(
            concentration_limit_pct=Decimal("40"),
            max_position_pct=Decimal("50"),
            max_sector_pct=Decimal("50"),
            min_cash_pct=Decimal("15"),
            target_allocations={
                "asset_class": {
                    "Equity": Decimal("45"),
                    "Bond": Decimal("40"),
                    "Cash": Decimal("15"),
                }
            },
        )
        exposure = analyze_portfolio(holdings, config)
        guardrails = evaluate_guardrails(holdings, config, ReviewDates())
        stress = stress_portfolio(
            holdings,
            StressScenario(
                "Review shock",
                (ScenarioShock("AAA decline", "symbol", "AAA", Decimal("-20")),),
            ),
        )

        watchlist = build_rebalance_watchlist(exposure, guardrails, stress)

        aaa = next(
            item
            for item in watchlist["items"]
            if item["scope_type"] == "holding" and item["scope"] == "AAA"
        )
        self.assertEqual(aaa["severity"], "high")
        self.assertEqual(
            aaa["reason_codes"],
            ["CONCENTRATION_LIMIT", "GUARDRAIL_FAIL", "STRESS_DRAWDOWN"],
        )
        self.assertIn("concentration 60.0000% vs limit 40.0000%", aaa["evidence_summary"])
        self.assertIn("trades", watchlist["metadata"]["safety_wording"])

        equity = next(
            item
            for item in watchlist["items"]
            if item["scope_type"] == "asset_class" and item["scope"] == "Equity"
        )
        self.assertIn("TARGET_DRIFT", equity["reason_codes"])
        self.assertIn("documented allocation", equity["educational_review_prompt"])

    def test_renderers_include_safety_wording_and_no_trade_quantities(self):
        watchlist = {
            "metadata": {
                "schema_version": 1,
                "review_type": "broker_free_rebalance_watchlist",
                "safety_wording": SAFETY_WORDING,
                "item_count": 1,
                "severity_counts": {"high": 1, "medium": 0, "low": 0},
                "source_artifacts": ["exposure_report", "guardrail_review", "stress_report"],
            },
            "items": [
                {
                    "severity": "high",
                    "scope_type": "holding",
                    "scope": "AAA",
                    "reason_codes": ["STRESS_DRAWDOWN"],
                    "evidence": [
                        {
                            "reason_code": "STRESS_DRAWDOWN",
                            "scenario": "Shock",
                            "total_price_move_pct": "-20.0000",
                        }
                    ],
                    "evidence_summary": "Shock stress move -20.0000%",
                    "educational_review_prompt": "Review whether holding AAA still fits policy.",
                }
            ],
        }

        json_text = render_rebalance_watchlist_json(watchlist)
        markdown = render_rebalance_watchlist_markdown(watchlist)

        self.assertIn('"review_type": "broker_free_rebalance_watchlist"', json_text)
        self.assertIn("# Rebalance Review Watchlist", markdown)
        self.assertIn("does not recommend trades", markdown)
        self.assertNotIn("shares", markdown.lower())

    def test_cli_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            holdings = root / "holdings.csv"
            config = root / "config.json"
            scenario = root / "scenario.json"
            json_path = root / "rebalance_watchlist.json"
            markdown_path = root / "rebalance_watchlist.md"
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
                  "concentration_limit_pct": "50",
                  "max_position_pct": "50",
                  "target_allocations": {"asset_class": {"Equity": "80", "Cash": "20"}}
                }
                """,
                encoding="utf-8",
            )
            scenario.write_text(
                """
                {
                  "name": "CLI shock",
                  "shocks": [
                    {"name": "Tech selloff", "sector": "Tech", "price_move_pct": "-10"}
                  ]
                }
                """,
                encoding="utf-8",
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "rebalance-watchlist",
                            str(holdings),
                            str(scenario),
                            "--config",
                            str(config),
                            "--json",
                            str(json_path),
                            "--markdown",
                            str(markdown_path),
                        ]
                    ),
                    0,
                )

            printed = stdout.write.call_args
            json_text = json_path.read_text(encoding="utf-8")
            markdown_text = markdown_path.read_text(encoding="utf-8")

        self.assertIsNone(printed)
        self.assertIn('"reason_codes"', json_text)
        self.assertIn("Safety boundary:", markdown_text)


if __name__ == "__main__":
    unittest.main()
