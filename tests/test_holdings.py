from decimal import Decimal
import tempfile
from pathlib import Path
import unittest

from portfolio_risk_compass.config import read_config_json
from portfolio_risk_compass.holdings import parse_holdings_rows, read_holdings_csv


class HoldingsParsingTests(unittest.TestCase):
    def test_parse_holdings_rows_normalizes_symbol_and_currency(self):
        holdings = parse_holdings_rows(
            [
                {
                    "symbol": " aapl ",
                    "quantity": "1.5",
                    "price": "200",
                    "asset_class": "Equity",
                    "sector": "Technology",
                    "region": "North America",
                    "currency": " usd ",
                    "name": "Apple",
                }
            ]
        )

        self.assertEqual(holdings[0].symbol, "AAPL")
        self.assertEqual(holdings[0].currency, "USD")
        self.assertEqual(holdings[0].market_value, Decimal("300.0"))

    def test_read_holdings_csv_requires_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "holdings.csv"
            csv_path.write_text("symbol,quantity\nAAPL,1\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required column"):
                read_holdings_csv(csv_path)

    def test_read_config_json_parses_decimal_targets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                """
                {
                  "base_currency": "usd",
                  "group_by": ["asset_class"],
                  "concentration_limit_pct": "12.5",
                  "max_position_pct": "20",
                  "max_sector_pct": "35",
                  "min_cash_pct": "5",
                  "max_leverage_multiple": "1.5",
                  "required_review_cadence_days": 45,
                  "last_review_date": "2026-05-01",
                  "target_allocations": {
                    "asset_class": {
                      "Equity": "60",
                      "Cash": "40"
                    }
                  }
                }
                """,
                encoding="utf-8",
            )

            config = read_config_json(config_path)

        self.assertEqual(config.base_currency, "USD")
        self.assertEqual(config.group_by, ("asset_class",))
        self.assertEqual(config.concentration_limit_pct, Decimal("12.5"))
        self.assertEqual(config.max_position_pct, Decimal("20"))
        self.assertEqual(config.max_sector_pct, Decimal("35"))
        self.assertEqual(config.min_cash_pct, Decimal("5"))
        self.assertEqual(config.max_leverage_multiple, Decimal("1.5"))
        self.assertEqual(config.required_review_cadence_days, 45)
        self.assertEqual(config.last_review_date.isoformat(), "2026-05-01")
        self.assertEqual(
            config.target_allocations["asset_class"]["Cash"], Decimal("40")
        )


if __name__ == "__main__":
    unittest.main()
