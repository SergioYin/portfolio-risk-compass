# Optional Artifact Integrations

`portfolio-risk-compass` can emit deterministic adapter JSON for tools that want
to consume its generated artifacts. These exports are intentionally file based:
they do not import, clone, shell out to, or depend on downstream repositories.

The adapter command reads JSON artifacts already produced by this package:

- `exposure_report.json`
- `guardrails.json`
- `stress.json`
- `catalysts.json`

Missing artifacts are allowed. The export includes only data that can be derived
from the files present in the selected output directory.

## Command

Generate an adapter payload for thesis tracking:

```bash
portfolio-risk-compass integration-export invest-thesis-ledger \
  --outputs-dir examples/outputs \
  --json examples/outputs/invest_thesis_ledger_adapter.json
```

Generate an adapter payload for leveraged ETP stress review:

```bash
portfolio-risk-compass integration-export leveraged-etp-risk-lab \
  --outputs-dir examples/outputs \
  --json examples/outputs/leveraged_etp_risk_lab_adapter.json
```

Omit `--json` to print the same deterministic JSON to stdout.

## Common Envelope

Both profiles use the same neutral envelope:

```json
{
  "schema_version": 1,
  "adapter": "portfolio-risk-compass.integration-export",
  "profile": "invest-thesis-ledger",
  "source_package": "portfolio-risk-compass",
  "source_artifacts": [
    {
      "path": "exposure_report.json",
      "bytes": 2168,
      "sha256": "..."
    }
  ],
  "payload": {}
}
```

`source_artifacts` contains relative artifact paths, byte counts, and SHA-256
hashes so downstream jobs can decide whether an export matches the source files
they expected. The adapter does not include local absolute paths.

## `invest-thesis-ledger` Profile

This profile is shaped for a ledger that tracks thesis events beside portfolio
risk context. It exports:

- `portfolio_context`: base currency, total market value, overall guardrail
  status, and symbols over the concentration threshold.
- `risk_flags`: non-`PASS` guardrail items.
- `thesis_review_items`: catalyst checklist entries with dates, importance,
  status flags, thesis links, and requested actions.

Example payload excerpt:

```json
{
  "portfolio_context": {
    "base_currency": "USD",
    "total_market_value": "7350.00",
    "overall_guardrail_status": "FAIL",
    "concentration_symbols": ["MSFT", "AAPL"]
  },
  "risk_flags": [
    {
      "status": "FAIL",
      "check": "max_sector_pct",
      "scope": "Technology",
      "actual": "54.4218",
      "limit": "50.0000",
      "message": "Technology sector is 54.4218% of portfolio."
    }
  ],
  "thesis_review_items": [
    {
      "symbol": "MSFT",
      "catalyst_date": "2026-05-12",
      "title": "Cloud segment investor update",
      "importance": "high",
      "flag": "overdue",
      "days_from_as_of": -3,
      "thesis_link": "https://example.com/theses/msft-cloud-margin",
      "action": "Review Azure growth and margin commentary"
    }
  ]
}
```

## `leveraged-etp-risk-lab` Profile

This profile is shaped for a stress-review workflow focused on leverage and
scenario impact. It exports:

- `portfolio_stress_summary`: scenario totals from `stress.json`.
- `asset_class_exposures`: asset-class exposure buckets from
  `exposure_report.json`.
- `leverage_guardrails`: `max_leverage_multiple` guardrail results.
- `shock_impacts`: named stress shock impacts.
- `stressed_holdings`: per-holding stressed value, value delta, total price
  move, and applied shock names.

Example payload excerpt:

```json
{
  "portfolio_stress_summary": {
    "scenario_name": "Risk-off rotation",
    "base_market_value": "7350.00",
    "stressed_market_value": "6812.00",
    "market_value_delta": "-538.00",
    "market_value_delta_pct": "-7.3197"
  },
  "leverage_guardrails": [
    {
      "status": "PASS",
      "scope": "portfolio",
      "actual": "1.0000",
      "limit": "1.2500",
      "message": "Gross exposure is 1.0000x net value."
    }
  ],
  "stressed_holdings": [
    {
      "symbol": "AAPL",
      "base_market_value": "1900.00",
      "stressed_market_value": "1615.00",
      "market_value_delta": "-285.00",
      "total_price_move_pct": "-15.0000",
      "shock_names": ["Technology rerating", "Apple idiosyncratic miss"]
    }
  ]
}
```

## Boundary

These profiles are examples of stable artifact shapes, not a compatibility
claim for another project's private APIs. Consumers should treat the generated
JSON as an interchange file and validate the fields they require.

The exports are still portfolio review artifacts. They do not contain live
quotes, broker connectivity, trade instructions, suitability analysis, or
investment advice; downstream tools should preserve that boundary when they
display or transform the payloads.
