import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.history import (
    build_history_ledger,
    render_history_markdown,
)


def _write_snapshot(path: Path, snapshot_id: str, date: str, value: str, drift: str) -> None:
    actual_pct = Decimal("70") + Decimal(drift)
    path.write_text(
        json.dumps(
            {
                "snapshot": {"id": snapshot_id, "date": date},
                "report": {
                    "metadata": {"total_market_value": value},
                    "target_drift": {
                        "asset_class": [
                            {
                                "bucket": "Equity",
                                "actual_pct": str(actual_pct),
                                "target_pct": "70",
                                "drift_pct": drift,
                            }
                        ]
                    },
                },
                "guardrails": {
                    "metadata": {
                        "overall_status": "FAIL",
                        "configured_checks": 2,
                    },
                    "items": [{"status": "PASS"}, {"status": "FAIL"}],
                },
                "catalysts": {
                    "metadata": {
                        "catalyst_count": 3,
                        "overdue_count": 1,
                        "today_count": 0,
                        "upcoming_count": 2,
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class HistoryTests(unittest.TestCase):
    def test_build_history_ledger_sorts_snapshots_and_computes_trends(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_snapshot(root / "b.json", "later", "2026-05-15", "120.00", "5")
            _write_snapshot(root / "a.json", "earlier", "2026-05-14", "100.00", "0")

            ledger = build_history_ledger(root)

        self.assertEqual(ledger["snapshot_count"], 2)
        self.assertEqual([row["id"] for row in ledger["snapshots"]], ["earlier", "later"])
        self.assertEqual(
            ledger["trends"]["total_market_value"],
            {
                "first": "100.00",
                "last": "120.00",
                "change": "20.00",
                "change_pct": "20.0000",
            },
        )
        self.assertEqual(
            ledger["snapshots"][1]["total_market_value"],
            {"value": "120.00", "change": "20.00", "change_pct": "20.0000"},
        )
        self.assertEqual(
            ledger["trends"]["exposure_drift"]["asset_class"],
            [
                {
                    "bucket": "Equity",
                    "first_drift_pct": "0.0000",
                    "last_drift_pct": "5.0000",
                    "pct_point_change": "5.0000",
                }
            ],
        )
        self.assertEqual(ledger["trends"]["guardrail_status"][0]["overall_status"], "FAIL")
        self.assertEqual(ledger["trends"]["catalyst_counts"][0]["catalyst_count"], 3)

    def test_markdown_renders_history_sections(self):
        ledger = build_history_ledger(Path("examples/fixtures/history"))
        markdown = render_history_markdown(ledger)

        self.assertIn("# Portfolio History Ledger", markdown)
        self.assertIn("| 2026-05-15 | ledger-2026-05-15 | 7350.00 | 100.00 | 1.3793% |", markdown)
        self.assertIn("| asset_class | Cash | 2.0000% | 3.6054% | 1.6054 |", markdown)
        self.assertIn("| 2026-05-15 | ledger-2026-05-15 | FAIL | 2 | 0 | 1 |", markdown)
        self.assertIn("| 2026-05-15 | ledger-2026-05-15 | 3 | 1 | 1 | 1 |", markdown)

    def test_cli_history_writes_markdown_and_prints_json_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path = Path(temp_dir) / "history.md"
            self.assertEqual(
                main(
                    [
                        "history",
                        "examples/fixtures/history",
                        "--markdown",
                        str(markdown_path),
                    ]
                ),
                0,
            )
            with patch("sys.stdout") as stdout:
                self.assertEqual(main(["history", "examples/fixtures/history"]), 0)
            markdown = markdown_path.read_text(encoding="utf-8")

        printed = json.loads(stdout.write.call_args.args[0])
        self.assertIn("## Total Value", markdown)
        self.assertEqual(printed["snapshot_count"], 3)
        self.assertEqual(printed["trends"]["total_market_value"]["change"], "350.00")


if __name__ == "__main__":
    unittest.main()
