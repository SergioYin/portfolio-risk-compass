# portfolio-risk-compass

Broker-free portfolio risk review from a holdings CSV, built for investors who
want deterministic exposure, guardrail, stress, catalyst, and dashboard outputs
without connecting an account or pulling live market data.

`portfolio-risk-compass` is a zero-runtime-dependency Python package that reads
plain holdings data, aggregates exposure by asset class, sector, region, and
currency, then writes deterministic JSON and Markdown reports.

It is designed for cold, repeatable portfolio review workflows: bring your own
CSV, run locally, inspect the artifacts, and commit or share the outputs as
plain files.

Agent-facing usage is documented in
[`skills/agent/portfolio-risk-compass/SKILL.md`](skills/agent/portfolio-risk-compass/SKILL.md).

## Why Star This

- Review portfolio concentration before a rebalance or investment committee
  meeting.
- Turn holdings CSVs into stable JSON, Markdown, and static HTML artifacts that
  are easy to diff in Git.
- Run guardrail checks for max position size, sector exposure, cash minimums,
  leverage, and review cadence.
- Model simple scenario shocks without a broker login, notebook, or live data
  subscription.
- Track thesis catalysts next to exposures so portfolio reviews are tied to
  upcoming events.
- Package a deterministic demo bundle for agents, CI, docs, or release review.

## Safety Boundary

This project does not connect to brokers, place trades, fetch live market data,
or provide investment advice. Prices come from your holdings CSV, and scenario
shocks come from your JSON files. Outputs are portfolio review artifacts, not
recommendations or execution instructions.

## Quickstart

```bash
python -m pip install --no-build-isolation -e .
portfolio-risk-compass analyze examples/fixtures/holdings.csv \
  --config examples/fixtures/config.json \
  --json report.json \
  --markdown report.md
```

`--no-build-isolation` keeps the editable install usable in offline or
network-restricted environments when `setuptools` is already available in the
active Python environment.

You can also run the CLI without installing the console script:

```bash
PYTHONPATH=src python -m portfolio_risk_compass analyze examples/fixtures/holdings.csv
```

When no `--json` or `--markdown` path is provided, the JSON report is printed to
stdout.

For a full demo bundle with all supported report types:

```bash
portfolio-risk-compass demo-bundle
portfolio-risk-compass dashboard examples/outputs/index.json examples/outputs/dashboard.html
```

## Example Outputs

The repository includes generated artifacts under
[`examples/outputs`](examples/outputs):

| Output | Use |
| --- | --- |
| [`exposure_report.md`](examples/outputs/exposure_report.md) | Allocation, concentration, and target drift summary |
| [`guardrails.md`](examples/outputs/guardrails.md) | PASS/WARN/FAIL policy checks |
| [`stress.md`](examples/outputs/stress.md) | Scenario shock impacts by rule and holding |
| [`catalysts.md`](examples/outputs/catalysts.md) | Date-ordered thesis event checklist |
| [`dashboard.html`](examples/outputs/dashboard.html) | Self-contained static dashboard export |
| [`index.json`](examples/outputs/index.json) | Demo bundle manifest for generated artifacts |
| [`release_manifest.md`](examples/outputs/release_manifest.md) | Release artifact inventory with SHA-256 hashes |
| [`release_manifest.json`](examples/outputs/release_manifest.json) | Machine-readable release artifact inventory |

Sample exposure output:

```markdown
## Concentration

| Symbol | Market value | Portfolio % | Limit % |
| --- | ---: | ---: | ---: |
| MSFT | 2100.00 | 28.5714% | 25.0000% |
| AAPL | 1900.00 | 25.8503% | 25.0000% |
```

Sample guardrail output:

```markdown
| Status | Check | Actual | Limit | Message |
| --- | --- | ---: | ---: | --- |
| FAIL | max_sector_pct | 54.4218 | 50.0000 | Technology sector is 54.4218% of portfolio. |
```

## Compared With Spreadsheets

Spreadsheets are flexible, but review logic can become hidden in cells, workbook
versions, and manual copy/paste steps. `portfolio-risk-compass` keeps the inputs
and outputs as plain files, makes calculations deterministic, and produces
review artifacts that can be tested, diffed, committed, and regenerated.

Use a spreadsheet when you want ad hoc modeling or interactive exploration. Use
this package when you want a repeatable local check that survives handoff,
automation, and release review.

## Snapshots and Diffs

Save dated portfolio snapshots when you want to compare analyzed states over
time:

```bash
portfolio-risk-compass snapshot examples/fixtures/holdings.csv snapshots/2026-05-15.json \
  --config examples/fixtures/config.json \
  --date 2026-05-15 \
  --id close-2026-05-15
```

`--date` and `--id` are optional. If omitted, the snapshot uses today's date and
a generated id.

Compare two snapshots:

```bash
portfolio-risk-compass diff snapshots/2026-05-14.json snapshots/2026-05-15.json
```

Example Markdown output:

```markdown
# Portfolio Snapshot Diff

- From: close-2026-05-14 (2026-05-14)
- To: close-2026-05-15 (2026-05-15)

## Total Value

| From | To | Change | Change % |
| ---: | ---: | ---: | ---: |
| 100000.00 | 104500.00 | 4500.00 | 4.5000% |
```

Use `--json` for machine-readable output:

```bash
portfolio-risk-compass diff snapshots/2026-05-14.json snapshots/2026-05-15.json --json
```

The diff includes total market value, allocation bucket value and percentage
point changes, concentration entries added or removed from the configured limit,
and target drift percentage point changes.

## Guardrail Policy Checks

Run configured portfolio review guardrails against a holdings file:

```bash
portfolio-risk-compass guardrails examples/fixtures/holdings.csv \
  --config examples/fixtures/config.json \
  --snapshot-date 2026-05-15 \
  --json guardrails.json \
  --markdown guardrails.md
```

When no `--json` or `--markdown` path is provided, JSON is printed to stdout.
Use `--format markdown` to print Markdown instead. `--snapshot-date` defaults
to today. `--last-review-date` can override `last_review_date` from config for
review cadence checks.

Guardrail output contains one item per applicable check with `PASS`, `WARN`, or
`FAIL` status. `WARN` means a value is close to the configured threshold, while
`FAIL` means the threshold has been breached.

Supported policy fields:

| Field | Meaning |
| --- | --- |
| `max_position_pct` | Maximum percentage allowed for any single holding |
| `max_sector_pct` | Maximum percentage allowed for any sector bucket |
| `min_cash_pct` | Minimum cash allocation percentage |
| `max_leverage_multiple` | Maximum gross exposure divided by net portfolio value |
| `required_review_cadence_days` | Maximum days allowed since the last portfolio review |
| `last_review_date` | Optional ISO date used by the review cadence check |

## Scenario Stress Analysis

Estimate stressed market value under named percentage price shocks:

```bash
portfolio-risk-compass stress examples/fixtures/holdings.csv examples/fixtures/scenario.json \
  --json stress.json \
  --markdown stress.md
```

When no `--json` or `--markdown` path is provided, JSON is printed to stdout.
Use `--format markdown` to print Markdown instead.

Scenario JSON requires a `name` and a non-empty `shocks` array. Each shock
requires `name`, `price_move_pct`, and exactly one selector: `symbol`, `sector`,
`asset_class`, `region`, or `currency`. The shorter `move_pct` key is also
accepted for the price move.

```json
{
  "name": "Risk-off rotation",
  "shocks": [
    {
      "name": "Technology rerating",
      "sector": "Technology",
      "price_move_pct": "-10"
    },
    {
      "name": "Apple idiosyncratic miss",
      "symbol": "AAPL",
      "price_move_pct": "-5"
    },
    {
      "name": "Bond rally",
      "asset_class": "Fixed Income",
      "price_move_pct": "2"
    }
  ]
}
```

If multiple shocks match a holding, their percentage moves are added. Output
includes scenario totals, named shock market value impacts, per-holding stressed
market value, value deltas, total price move, and contribution percentage-point
deltas.

## Catalyst Calendar

Track thesis-relevant portfolio events with a plain JSON fixture:

```bash
portfolio-risk-compass catalysts examples/fixtures/catalysts.json \
  --as-of 2026-05-15 \
  --json catalyst-checklist.json \
  --markdown catalyst-checklist.md
```

When no `--json` or `--markdown` path is provided, the JSON checklist is printed
to stdout. `--as-of` is optional and defaults to today's date.

Each catalyst requires `symbol`, `date`, `title`, `importance`, `thesis_link`,
and `action`:

```json
[
  {
    "symbol": "MSFT",
    "date": "2026-05-12",
    "title": "Cloud segment investor update",
    "importance": "high",
    "thesis_link": "https://example.com/theses/msft-cloud-margin",
    "action": "Review Azure growth and margin commentary"
  }
]
```

Output is date ordered. Each item is flagged as `overdue`, `today`, or
`upcoming` relative to `--as-of`, and Markdown output groups items into checklist
sections.

## Demo Bundle and Dashboard Export

Regenerate the deterministic demo artifact bundle from `examples/fixtures`:

```bash
portfolio-risk-compass demo-bundle \
  --fixtures-dir examples/fixtures \
  --output-dir examples/outputs \
  --as-of 2026-05-15
```

The command writes `examples/outputs/index.json`, a manifest for the generated
JSON and Markdown reports.

Export a static dashboard from that manifest:

```bash
portfolio-risk-compass dashboard examples/outputs/index.json examples/outputs/dashboard.html
```

The dashboard export writes one self-contained HTML file with inline CSS and no
JavaScript. It includes summary cards, internal section links, exposure and
concentration tables, guardrail risk boundary text, stress results, catalysts,
and the source bundle artifact list. Dynamic values from the report and manifest
are HTML escaped before rendering.

You can also render a dashboard from a single exposure report JSON:

```bash
portfolio-risk-compass dashboard examples/outputs/exposure_report.json dashboard.html
```

## Package Audit and Release Manifest

Check packaging readiness and example artifact coverage:

```bash
portfolio-risk-compass package-audit
```

The audit reports the package version, CLI command count, fixture count, output
artifact count, and any missing packaging items. Tests are optional and only run
when requested:

```bash
portfolio-risk-compass package-audit --run-tests
portfolio-risk-compass package-audit --format markdown
```

Create deterministic JSON and Markdown inventories for `examples/outputs`:

```bash
portfolio-risk-compass release-manifest
```

By default this writes `examples/outputs/release_manifest.json` and
`examples/outputs/release_manifest.md`. Each inventory entry includes the
artifact path, format, byte size, and SHA-256 hash. Custom paths are supported:

```bash
portfolio-risk-compass release-manifest \
  --outputs-dir examples/outputs \
  --json dist/release_manifest.json \
  --markdown dist/release_manifest.md
```

## Roadmap

- Additional import examples for common broker and portfolio tracker CSV
  exports, still without broker connectivity.
- More guardrail templates for income, duration, currency, and liquidity review.
- Richer dashboard sections while keeping the export static and JavaScript-free.
- Optional CI examples for regenerating demo artifacts and release manifests.
- Expanded agent workflow docs for portfolio review handoffs.

## Holdings CSV

Required columns:

| Column | Meaning |
| --- | --- |
| `symbol` | Holding ticker or identifier |
| `quantity` | Number of units held |
| `price` | Price per unit |
| `asset_class` | Asset class bucket |
| `sector` | Sector bucket |
| `region` | Geographic bucket |
| `currency` | Pricing currency |

Optional columns:

| Column | Meaning |
| --- | --- |
| `name` | Human-readable holding name |

Market value is calculated as `quantity * price`. Values are reported as fixed
decimal strings so output remains stable across Python versions and platforms.

## Config JSON

All config fields are optional.

```json
{
  "base_currency": "USD",
  "group_by": ["asset_class", "sector", "region", "currency"],
  "concentration_limit_pct": "25",
  "max_position_pct": "35",
  "max_sector_pct": "50",
  "min_cash_pct": "5",
  "max_leverage_multiple": "1.25",
  "required_review_cadence_days": 30,
  "last_review_date": "2026-05-01",
  "target_allocations": {
    "asset_class": {
      "Equity": "70",
      "Fixed Income": "25",
      "Cash": "5"
    }
  }
}
```

`target_allocations` compares actual exposure percentages to configured target
percentages for the selected exposure group.

## Development

Run tests with the standard library test runner:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Run the full repository selfcheck:

```bash
python scripts/selfcheck.py
```

The selfcheck runs a temporary local-skill sync, unit tests, deterministic demo
bundle generation, dashboard export, release manifest generation, a privacy
scan over the refreshed repository artifacts, and the package audit command.

Scan repository text for local/private terms and token-like patterns:

```bash
python scripts/privacy_scan.py
python scripts/privacy_scan.py --term "internal-project-name"
```

The scanner reports only file locations and rule names. It does not print the
matched private term or token-like value.

Copy the public agent skill into a local skills directory:

```bash
python scripts/sync_local_skill.py --target-dir ~/.codex/skills
```

The sync command writes `portfolio-risk-compass/SKILL.md` under `--target-dir`
and adapts the README link for that target location. Use `--dry-run` to preview
the destination without writing files.
