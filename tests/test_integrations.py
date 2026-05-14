import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.integrations import (
    build_integration_export,
    render_integration_export_json,
)


class IntegrationExportTests(unittest.TestCase):
    def test_invest_thesis_ledger_export_maps_catalysts_and_risk_flags(self):
        export = build_integration_export(Path("examples/outputs"), "invest-thesis-ledger")

        self.assertEqual(export["schema_version"], 1)
        self.assertEqual(export["profile"], "invest-thesis-ledger")
        self.assertEqual(export["source_package"], "portfolio-risk-compass")
        self.assertEqual(
            [artifact["path"] for artifact in export["source_artifacts"]],
            [
                "exposure_report.json",
                "guardrails.json",
                "stress.json",
                "catalysts.json",
            ],
        )
        payload = export["payload"]
        self.assertEqual(
            payload["portfolio_context"]["concentration_symbols"],
            ["MSFT", "AAPL"],
        )
        self.assertEqual(payload["risk_flags"][0]["check"], "max_sector_pct")
        self.assertEqual(payload["risk_flags"][0]["status"], "FAIL")
        self.assertEqual(
            payload["thesis_review_items"][0]["thesis_link"],
            "https://example.com/theses/msft-cloud-margin",
        )

    def test_leveraged_etp_risk_lab_export_maps_stress_and_leverage_fields(self):
        export = build_integration_export(Path("examples/outputs"), "leveraged-etp-risk-lab")
        payload = export["payload"]

        self.assertEqual(
            payload["portfolio_stress_summary"]["scenario_name"],
            "Risk-off rotation",
        )
        self.assertEqual(payload["leverage_guardrails"][0]["actual"], "1.0000")
        self.assertEqual(payload["stressed_holdings"][0]["symbol"], "AAPL")
        self.assertEqual(
            payload["stressed_holdings"][0]["shock_names"],
            ["Technology rerating", "Apple idiosyncratic miss"],
        )
        self.assertEqual(payload["asset_class_exposures"][0]["bucket"], "Equity")

    def test_integration_export_cli_writes_deterministic_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            output_dir.mkdir()
            (output_dir / "exposure_report.json").write_text(
                json.dumps(
                    {
                        "metadata": {
                            "base_currency": "USD",
                            "total_market_value": "100.00",
                        },
                        "concentration": [],
                        "exposures": {"asset_class": []},
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            output_json = Path(temp_dir) / "adapter.json"

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "integration-export",
                            "invest-thesis-ledger",
                            "--outputs-dir",
                            str(output_dir),
                            "--json",
                            str(output_json),
                        ]
                    ),
                    0,
                )

            export = json.loads(output_json.read_text(encoding="utf-8"))
            rendered = render_integration_export_json(export)

        self.assertEqual(stdout.write.call_args.args[0], str(output_json) + "\n")
        self.assertEqual(export["payload"]["portfolio_context"]["base_currency"], "USD")
        self.assertEqual(
            export["source_artifacts"][0]["sha256"],
            hashlib.sha256(
                b'{"concentration": [], "exposures": {"asset_class": []}, '
                b'"metadata": {"base_currency": "USD", "total_market_value": "100.00"}}\n'
            ).hexdigest(),
        )
        self.assertEqual(rendered, json.dumps(export, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    unittest.main()
