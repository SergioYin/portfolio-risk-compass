from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.holdings import Holding
from portfolio_risk_compass.stress import (
    ScenarioShock,
    StressScenario,
    parse_scenario,
    render_stress_markdown,
    stress_portfolio,
)


class StressScenarioTests(unittest.TestCase):
    def test_stress_portfolio_applies_named_shocks_and_contribution_deltas(self):
        holdings = [
            Holding("AAA", Decimal("2"), Decimal("100"), "Equity", "Tech", "US", "USD"),
            Holding("BBB", Decimal("1"), Decimal("300"), "Bond", "Gov", "US", "USD"),
            Holding("CCC", Decimal("5"), Decimal("20"), "Equity", "Tech", "EU", "EUR"),
        ]
        scenario = StressScenario(
            "Mixed shock",
            (
                ScenarioShock("Tech selloff", "sector", "Tech", Decimal("-10")),
                ScenarioShock("AAA miss", "symbol", "AAA", Decimal("-5")),
                ScenarioShock("EUR rally", "currency", "EUR", Decimal("4")),
            ),
        )

        report = stress_portfolio(holdings, scenario)

        self.assertEqual(report["metadata"]["base_market_value"], "600.00")
        self.assertEqual(report["metadata"]["stressed_market_value"], "564.00")
        self.assertEqual(report["metadata"]["market_value_delta"], "-36.00")
        self.assertEqual(report["metadata"]["market_value_delta_pct"], "-6.0000")
        self.assertEqual(
            report["shock_impacts"],
            [
                {
                    "name": "Tech selloff",
                    "selector": "sector",
                    "bucket": "Tech",
                    "price_move_pct": "-10.0000",
                    "market_value_delta": "-30.00",
                },
                {
                    "name": "AAA miss",
                    "selector": "symbol",
                    "bucket": "AAA",
                    "price_move_pct": "-5.0000",
                    "market_value_delta": "-10.00",
                },
                {
                    "name": "EUR rally",
                    "selector": "currency",
                    "bucket": "EUR",
                    "price_move_pct": "4.0000",
                    "market_value_delta": "4.00",
                },
            ],
        )

        aaa = report["holdings"][0]
        self.assertEqual(aaa["symbol"], "AAA")
        self.assertEqual(aaa["stressed_market_value"], "170.00")
        self.assertEqual(aaa["total_price_move_pct"], "-15.0000")
        self.assertEqual(aaa["contribution_delta_pct"], "-3.1915")

    def test_parse_scenario_accepts_each_selector_and_move_pct_alias(self):
        scenario = parse_scenario(
            {
                "name": "Selector coverage",
                "shocks": [
                    {"name": "Symbol", "symbol": "aaa", "move_pct": "-1"},
                    {"name": "Sector", "sector": "Tech", "price_move_pct": "-2"},
                    {"name": "Asset", "asset_class": "Equity", "price_move_pct": "-3"},
                    {"name": "Region", "region": "US", "price_move_pct": "-4"},
                    {"name": "Currency", "currency": "usd", "price_move_pct": "-5"},
                ],
            }
        )

        self.assertEqual([shock.selector for shock in scenario.shocks], [
            "symbol",
            "sector",
            "asset_class",
            "region",
            "currency",
        ])
        self.assertEqual(scenario.shocks[0].bucket, "AAA")
        self.assertEqual(scenario.shocks[4].bucket, "USD")

    def test_parse_scenario_rejects_ambiguous_selector(self):
        with self.assertRaisesRegex(ValueError, "exactly one selector"):
            parse_scenario(
                {
                    "name": "Bad",
                    "shocks": [
                        {
                            "name": "Ambiguous",
                            "symbol": "AAA",
                            "sector": "Tech",
                            "price_move_pct": "-5",
                        }
                    ],
                }
            )

    def test_markdown_renderer_includes_shock_and_holding_tables(self):
        report = stress_portfolio(
            [Holding("AAA", Decimal("1"), Decimal("100"), "Equity", "Tech", "US", "USD")],
            StressScenario(
                "One shock",
                (ScenarioShock("Tech selloff", "sector", "Tech", Decimal("-10")),),
            ),
        )

        markdown = render_stress_markdown(report)

        self.assertIn("# Portfolio Stress Scenario", markdown)
        self.assertIn("| Tech selloff | sector | Tech | -10.0000% | -10.00 |", markdown)
        self.assertIn("| AAA | 100.00 | 90.00 | -10.00 | -10.0000% | 0.0000% |", markdown)

    def test_cli_stress_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            holdings = root / "holdings.csv"
            scenario = root / "scenario.json"
            json_path = root / "stress.json"
            markdown_path = root / "stress.md"
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
                            "stress",
                            str(holdings),
                            str(scenario),
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
        self.assertIn('"stressed_market_value": "90.00"', json_text)
        self.assertIn("# Portfolio Stress Scenario", markdown_text)


if __name__ == "__main__":
    unittest.main()
