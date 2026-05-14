from decimal import Decimal
import unittest

from portfolio_risk_compass.analysis import analyze_portfolio
from portfolio_risk_compass.config import AnalysisConfig
from portfolio_risk_compass.holdings import Holding


class AnalyzePortfolioTests(unittest.TestCase):
    def test_exposure_math_is_grouped_and_sorted(self):
        holdings = [
            Holding("AAA", Decimal("2"), Decimal("100"), "Equity", "Tech", "US", "USD"),
            Holding("BBB", Decimal("1"), Decimal("300"), "Bond", "Gov", "US", "USD"),
            Holding("CCC", Decimal("5"), Decimal("20"), "Equity", "Tech", "EU", "EUR"),
        ]

        report = analyze_portfolio(
            holdings,
            AnalysisConfig(
                group_by=("asset_class", "region"),
                concentration_limit_pct=Decimal("50"),
            ),
        )

        self.assertEqual(report["metadata"]["total_market_value"], "600.00")
        self.assertEqual(
            report["exposures"]["asset_class"],
            [
                {
                    "bucket": "Bond",
                    "market_value": "300.00",
                    "pct_of_portfolio": "50.0000",
                },
                {
                    "bucket": "Equity",
                    "market_value": "300.00",
                    "pct_of_portfolio": "50.0000",
                },
            ],
        )
        self.assertEqual(
            report["concentration"],
            [
                {
                    "symbol": "BBB",
                    "market_value": "300.00",
                    "pct_of_portfolio": "50.0000",
                    "limit_pct": "50.0000",
                }
            ],
        )

    def test_target_drift_includes_missing_buckets(self):
        report = analyze_portfolio(
            [Holding("AAA", Decimal("1"), Decimal("100"), "Equity", "Tech", "US", "USD")],
            AnalysisConfig(
                group_by=("asset_class",),
                target_allocations={
                    "asset_class": {
                        "Equity": Decimal("80"),
                        "Cash": Decimal("20"),
                    }
                },
            ),
        )

        self.assertEqual(
            report["target_drift"]["asset_class"],
            [
                {
                    "bucket": "Cash",
                    "actual_pct": "0.0000",
                    "target_pct": "20.0000",
                    "drift_pct": "-20.0000",
                },
                {
                    "bucket": "Equity",
                    "actual_pct": "100.0000",
                    "target_pct": "80.0000",
                    "drift_pct": "20.0000",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
