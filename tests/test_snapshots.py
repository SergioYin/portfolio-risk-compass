import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.analysis import analyze_portfolio
from portfolio_risk_compass.cli import main
from portfolio_risk_compass.config import AnalysisConfig
from portfolio_risk_compass.holdings import Holding
from portfolio_risk_compass.snapshots import build_snapshot, diff_snapshots


def _report(price_a: str, price_b: str) -> dict:
    return analyze_portfolio(
        [
            Holding(
                "AAA", Decimal("1"), Decimal(price_a), "Equity", "Tech", "US", "USD"
            ),
            Holding(
                "BBB",
                Decimal("1"),
                Decimal(price_b),
                "Fixed Income",
                "Gov",
                "US",
                "USD",
            ),
        ],
        AnalysisConfig(
            group_by=("asset_class", "sector"),
            concentration_limit_pct=Decimal("60"),
            target_allocations={
                "asset_class": {
                    "Equity": Decimal("50"),
                    "Fixed Income": Decimal("50"),
                }
            },
        ),
    )


class SnapshotTests(unittest.TestCase):
    def test_build_snapshot_adds_supplied_metadata(self):
        snapshot = build_snapshot(
            _report("100", "100"),
            snapshot_date="2026-05-15",
            snapshot_id="close-2026-05-15",
        )

        self.assertEqual(
            snapshot["snapshot"],
            {"date": "2026-05-15", "id": "close-2026-05-15"},
        )
        self.assertEqual(snapshot["report"]["metadata"]["total_market_value"], "200.00")

    def test_diff_snapshots_compares_value_allocation_concentration_and_drift(self):
        before = build_snapshot(
            _report("100", "100"),
            snapshot_date="2026-05-14",
            snapshot_id="before",
        )
        after = build_snapshot(
            _report("300", "100"),
            snapshot_date="2026-05-15",
            snapshot_id="after",
        )

        diff = diff_snapshots(before, after)

        self.assertEqual(
            diff["total_market_value"],
            {
                "from": "200.00",
                "to": "400.00",
                "change": "200.00",
                "change_pct": "100.0000",
            },
        )
        self.assertEqual(
            diff["allocation_buckets"]["asset_class"],
            [
                {
                    "bucket": "Equity",
                    "from_market_value": "100.00",
                    "to_market_value": "300.00",
                    "market_value_change": "200.00",
                    "from_pct": "50.0000",
                    "to_pct": "75.0000",
                    "pct_point_change": "25.0000",
                },
                {
                    "bucket": "Fixed Income",
                    "from_market_value": "100.00",
                    "to_market_value": "100.00",
                    "market_value_change": "0.00",
                    "from_pct": "50.0000",
                    "to_pct": "25.0000",
                    "pct_point_change": "-25.0000",
                },
            ],
        )
        self.assertEqual(
            diff["concentration"],
            [
                {
                    "symbol": "AAA",
                    "status": "added",
                    "from_market_value": "0.00",
                    "to_market_value": "300.00",
                    "market_value_change": "300.00",
                    "from_pct": "0.0000",
                    "to_pct": "75.0000",
                    "pct_point_change": "75.0000",
                }
            ],
        )
        self.assertEqual(
            diff["target_drift"]["asset_class"][0],
            {
                "bucket": "Equity",
                "from_drift_pct": "0.0000",
                "to_drift_pct": "25.0000",
                "pct_point_change": "25.0000",
            },
        )

    def test_cli_snapshot_writes_json_and_diff_prints_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            holdings = root / "holdings.csv"
            config = root / "config.json"
            before = root / "before.json"
            after = root / "after.json"
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
                  "group_by": ["asset_class"],
                  "target_allocations": {
                    "asset_class": {
                      "Equity": "90",
                      "Cash": "10"
                    }
                  }
                }
                """,
                encoding="utf-8",
            )

            self.assertEqual(
                main(
                    [
                        "snapshot",
                        str(holdings),
                        str(before),
                        "--config",
                        str(config),
                        "--date",
                        "2026-05-14",
                        "--id",
                        "before",
                    ]
                ),
                0,
            )

            holdings.write_text(
                "\n".join(
                    [
                        "symbol,quantity,price,asset_class,sector,region,currency",
                        "AAA,2,100,Equity,Tech,US,USD",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(
                main(
                    [
                        "snapshot",
                        str(holdings),
                        str(after),
                        "--config",
                        str(config),
                        "--date",
                        "2026-05-15",
                        "--id",
                        "after",
                    ]
                ),
                0,
            )

            with patch("sys.stdout") as stdout:
                self.assertEqual(main(["diff", str(before), str(after), "--json"]), 0)

            written = json.loads(before.read_text(encoding="utf-8"))
            printed = json.loads(stdout.write.call_args.args[0])

        self.assertEqual(written["snapshot"]["id"], "before")
        self.assertEqual(printed["total_market_value"]["change"], "100.00")


if __name__ == "__main__":
    unittest.main()
