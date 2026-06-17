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
recommendations, suitability analysis, current quotes, or execution
instructions. The bundled fixtures use static example data and should not be
treated as live prices or model portfolios.

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
active Python environment. If `setuptools` is not already installed, install it
before running the editable install.

You can also run the CLI without installing the console script:

```bash
PYTHONPATH=src python -m portfolio_risk_compass analyze examples/fixtures/holdings.csv
```

When no `--json` or `--markdown` path is provided, the JSON report is printed to
stdout.

For a full demo bundle with all supported report types:

```bash
portfolio-risk-compass template-list --format markdown
portfolio-risk-compass demo-bundle
portfolio-risk-compass case-study
portfolio-risk-compass showcase
portfolio-risk-compass dashboard examples/outputs/index.json examples/outputs/dashboard.html
portfolio-risk-compass reviewer-evidence
portfolio-risk-compass scenario-evidence-receipt
portfolio-risk-compass public-review
```

## Example Outputs

The repository includes generated artifacts under
[`examples/outputs`](examples/outputs):

| Output | Use |
| --- | --- |
| [`exposure_report.md`](examples/outputs/exposure_report.md) | Allocation, concentration, and target drift summary |
| [`guardrails.md`](examples/outputs/guardrails.md) | PASS/WARN/FAIL policy checks |
| [`stress.md`](examples/outputs/stress.md) | Scenario shock impacts by rule and holding |
| [`rebalance_watchlist.md`](examples/outputs/rebalance_watchlist.md) | Educational review watchlist with severity and reason codes |
| [`review_memo.md`](examples/outputs/review_memo.md) | Human review memo combining exposure, guardrails, stress, catalysts, history, and watchlist artifacts |
| [`history.md`](examples/outputs/history.md) | Snapshot ledger trends for value, drift, guardrails, and catalysts |
| [`catalysts.md`](examples/outputs/catalysts.md) | Date-ordered thesis event checklist |
| [`dashboard.html`](examples/outputs/dashboard.html) | Self-contained static dashboard export |
| [`gallery.md`](examples/outputs/gallery.md) | Static gallery index for dashboard and demo artifacts |
| [`case_study_comparison.md`](examples/outputs/case_study_comparison.md) | Deterministic base-demo and template case-study comparison |
| [`case_study_comparison.json`](examples/outputs/case_study_comparison.json) | Machine-readable case-study metrics and source artifact links |
| [`reviewer_evidence.md`](examples/outputs/reviewer_evidence.md) | Public trace from dashboard and case-study artifacts back to static source fixtures |
| [`reviewer_evidence.json`](examples/outputs/reviewer_evidence.json) | Machine-readable reviewer evidence for generated artifact and fixture verification |
| [`scenario_evidence_receipt.md`](examples/outputs/scenario_evidence_receipt.md) | Deterministic receipt tying static scenario fixtures to stress, guardrail, and dashboard artifact hashes |
| [`scenario_evidence_receipt.json`](examples/outputs/scenario_evidence_receipt.json) | Machine-readable scenario evidence receipt with regeneration commands and no-broker/no-live-data/no-advice boundaries |
| [`public_review_walkthrough.md`](examples/outputs/public_review_walkthrough.md) | Public static dashboard walkthrough with exact rerun commands, hashes, and no-live-data/no-broker/no-advice boundaries |
| [`public_review_walkthrough.json`](examples/outputs/public_review_walkthrough.json) | Machine-readable public review packet for static dashboard evidence verification |
| [`walkthrough.md`](examples/outputs/walkthrough.md) | Guided base-demo and multi-template walkthrough for cold users |
| [`walkthrough.json`](examples/outputs/walkthrough.json) | Machine-readable showcase walkthrough metrics and artifact links |
| [`dashboard_preview.md`](examples/outputs/dashboard_preview.md) | Text-based dashboard preview table suitable for README or release notes |
| [`dashboard_snippet.html`](examples/outputs/dashboard_snippet.html) | Small embeddable HTML showcase snippet for docs pages |
| [`index.json`](examples/outputs/index.json) | Demo bundle manifest for generated artifacts |
| [`invest_thesis_ledger_adapter.json`](examples/outputs/invest_thesis_ledger_adapter.json) | Optional adapter payload for thesis-ledger style consumers |
| [`leveraged_etp_risk_lab_adapter.json`](examples/outputs/leveraged_etp_risk_lab_adapter.json) | Optional adapter payload for leveraged ETP stress-review consumers |
| [`release_manifest.md`](examples/outputs/release_manifest.md) | Release artifact inventory with SHA-256 hashes |
| [`release_manifest.json`](examples/outputs/release_manifest.json) | Machine-readable release artifact inventory |

Template outputs are also generated under
[`examples/outputs/templates`](examples/outputs/templates) when the demo bundle
is refreshed.

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

## History Ledger

Build a stateful trend ledger from a directory of snapshot JSON files:

```bash
portfolio-risk-compass history examples/fixtures/history \
  --json examples/outputs/history.json \
  --markdown examples/outputs/history.md
```

When no `--json` or `--markdown` path is provided, JSON is printed to stdout.
Use `--format markdown` to print Markdown instead. Snapshot files are ordered by
snapshot date, id, and filename, so output is deterministic even when directory
iteration order differs by platform.

The ledger reports total market value by snapshot, period-over-period value
change, first-to-last target drift changes, guardrail status counts when a
snapshot contains a top-level `guardrails` or `guardrail_review` block, and
catalyst counts when a snapshot contains a top-level `catalysts` or
`catalyst_checklist` block.

Optional snapshot enrichment shape:

```json
{
  "snapshot": {"id": "ledger-2026-05-15", "date": "2026-05-15"},
  "report": {
    "metadata": {"total_market_value": "7350.00"},
    "target_drift": {
      "asset_class": [
        {"bucket": "Equity", "actual_pct": "66.6667", "target_pct": "70.0000", "drift_pct": "-3.3333"}
      ]
    }
  },
  "guardrails": {
    "metadata": {"overall_status": "FAIL", "configured_checks": 3},
    "items": [{"status": "PASS"}, {"status": "FAIL"}]
  },
  "catalysts": {
    "metadata": {"catalyst_count": 3, "overdue_count": 1, "today_count": 1, "upcoming_count": 1}
  }
}
```

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

## Rebalance Review Watchlist

Build a broker-free educational watchlist from target drift, guardrail WARN/FAIL
items, concentration, and stress drawdowns:

```bash
portfolio-risk-compass rebalance-watchlist examples/fixtures/holdings.csv examples/fixtures/scenario.json \
  --config examples/fixtures/config.json \
  --snapshot-date 2026-05-15 \
  --json rebalance_watchlist.json \
  --markdown rebalance_watchlist.md
```

When no `--json` or `--markdown` path is provided, JSON is printed to stdout.
Use `--format markdown` to print Markdown instead.

The watchlist groups review reasons by subject, assigns `high`, `medium`, or
`low` severity, and includes reason codes such as `TARGET_DRIFT`,
`GUARDRAIL_FAIL`, `CONCENTRATION_LIMIT`, and `STRESS_DRAWDOWN`.

Safety boundary: this command does not recommend trades, order types, position
quantities, account transfers, or timing. It only identifies topics that may
deserve human review against a documented allocation and risk policy.

Sample watchlist output:

```markdown
| Severity | Scope type | Scope | Reason codes | Evidence summary |
| --- | --- | --- | --- | --- |
| high | holding | AAPL | CONCENTRATION_LIMIT, STRESS_DRAWDOWN | concentration 25.8503% vs limit 25.0000%; Risk-off rotation stress move -15.0000% |
```

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

## Review Memo

Combine the generated JSON artifacts into one Markdown memo for human review:

```bash
portfolio-risk-compass review-memo \
  --outputs-dir examples/outputs \
  --markdown examples/outputs/review_memo.md
```

The command reads `exposure_report.json`, `guardrails.json`, `stress.json`,
`catalysts.json`, `history.json`, and `rebalance_watchlist.json` from the output
directory. The memo includes source artifact paths, an executive summary,
exposure and concentration tables, guardrail results, stress impacts, catalysts,
history, explicit assumptions, and a non-advice boundary. When `--markdown` is
omitted, Markdown is printed to stdout.

Boundary: the memo is for educational human review only. It is not investment,
tax, legal, accounting, or trading advice, and it does not recommend buying,
selling, holding, position sizes, order types, account transfers, or timing.

## Demo Bundle and Dashboard Export

List the named example portfolio templates:

```bash
portfolio-risk-compass template-list --format markdown
```

The repository includes three realistic template fixture sets under
[`examples/templates`](examples/templates):

| Template | Focus | Fixture directory |
| --- | --- | --- |
| ETF Core | Diversified stock, bond, and Treasury-bill core allocation | [`examples/templates/etf-core`](examples/templates/etf-core) |
| Leveraged Sleeve | Core equity book with a capped leveraged growth sleeve and liquidity buffer | [`examples/templates/leveraged-sleeve`](examples/templates/leveraged-sleeve) |
| Cash Rebalance | High-cash portfolio staged for tax-aware deployment after drift or pullback triggers | [`examples/templates/cash-rebalance`](examples/templates/cash-rebalance) |

Each template has `holdings.csv`, `config.json`, `catalysts.json`, and
`scenario.json` fixtures, so the same `analyze`, `guardrails`, `catalysts`, and
`stress` commands work against every template.

Regenerate the deterministic demo artifact bundle from `examples/fixtures`:

```bash
portfolio-risk-compass demo-bundle \
  --fixtures-dir examples/fixtures \
  --output-dir examples/outputs \
  --as-of 2026-05-15
```

The command writes `examples/outputs/index.json`, a manifest for the generated
JSON and Markdown reports. It also refreshes
[`examples/outputs/history.json`](examples/outputs/history.json),
[`examples/outputs/history.md`](examples/outputs/history.md),
[`examples/outputs/review_memo.md`](examples/outputs/review_memo.md),
[`examples/outputs/gallery.md`](examples/outputs/gallery.md),
[`examples/outputs/case_study_comparison.md`](examples/outputs/case_study_comparison.md),
[`examples/outputs/case_study_comparison.json`](examples/outputs/case_study_comparison.json),
[`examples/outputs/dashboard_preview.md`](examples/outputs/dashboard_preview.md),
and
[`examples/outputs/dashboard_snippet.html`](examples/outputs/dashboard_snippet.html)
as static showcase material for README, docs, and release pages. By default it
also writes template gallery outputs under
`examples/outputs/templates/<template-slug>/`. Use `--no-templates` when you
only want the base demo fixture outputs.

Write or refresh just the case-study comparison from an existing bundle
manifest:

```bash
portfolio-risk-compass case-study \
  --manifest examples/outputs/index.json \
  --markdown examples/outputs/case_study_comparison.md \
  --json examples/outputs/case_study_comparison.json
```

The comparison uses the generated base-demo and template JSON artifacts to
summarize allocation posture, guardrail status, stress drawdown, catalyst count,
and watchlist severity counts. It links back to the source Markdown reports and
does not recommend trades, quantities, transfers, or timing.

Write or refresh the guided showcase walkthrough from an existing bundle
manifest:

```bash
portfolio-risk-compass showcase \
  --manifest examples/outputs/index.json \
  --markdown examples/outputs/walkthrough.md \
  --json examples/outputs/walkthrough.json
```

The walkthrough is designed for cold users reviewing the project for the first
time. It compares the base demo, ETF core, leveraged sleeve, and cash rebalance
templates in one deterministic artifact, links to the relevant Markdown reports,
and summarizes total value, guardrail status, stress delta, catalyst count, and
watchlist count. It is a static review guide only and does not recommend trades,
position sizes, account transfers, or timing.

Export a static dashboard from that manifest:

```bash
portfolio-risk-compass dashboard examples/outputs/index.json examples/outputs/dashboard.html
```

Write the scenario evidence receipt after the stress, guardrail, and dashboard
artifacts have been refreshed:

```bash
portfolio-risk-compass scenario-evidence-receipt
```

Write the public reviewer packet after the dashboard and evidence artifacts have
been refreshed:

```bash
portfolio-risk-compass public-review \
  --manifest examples/outputs/index.json \
  --markdown examples/outputs/public_review_walkthrough.md \
  --json examples/outputs/public_review_walkthrough.json
```

The public review packet combines a static dashboard walkthrough with SHA-256
hashes for the dashboard, walkthrough, reviewer evidence, scenario evidence,
case-study, manifest, and fixture inputs. It records exact rerun commands and
states the no-live-data, no-broker, and no-advice boundaries for public review.

The dashboard export writes one self-contained HTML file with inline CSS and no
JavaScript. It includes summary cards, internal section links, exposure and
concentration tables, guardrail risk boundary text, stress results, catalysts,
and the source bundle artifact list. Dynamic values from the report and manifest
are HTML escaped before rendering.

Text preview surrogate:

| Panel | What it shows | Source artifact |
| --- | --- | --- |
| Summary | Total value, holding count, concentration limit, risk boundary | `exposure_report.json`, `guardrails.json` |
| Exposure | Asset class, sector, region, and currency allocation tables | `exposure_report.json` |
| Concentration | Holdings above the configured concentration limit | `exposure_report.json` |
| Risk Boundaries | PASS/WARN/FAIL policy checks with actuals and limits | `guardrails.json` |
| Stress | Scenario value, shock impacts, and value delta | `stress.json` |
| Catalysts | Date-ordered thesis event checklist | `catalysts.json` |
| Bundle | Generated artifact inventory | `index.json` |

You can also render a dashboard from a single exposure report JSON:

```bash
portfolio-risk-compass dashboard examples/outputs/exposure_report.json dashboard.html
```

## Optional Artifact Integrations

Generate neutral adapter JSON for adjacent local tools without importing or
depending on those repositories:

```bash
portfolio-risk-compass integration-export invest-thesis-ledger \
  --outputs-dir examples/outputs \
  --json examples/outputs/invest_thesis_ledger_adapter.json

portfolio-risk-compass integration-export leveraged-etp-risk-lab \
  --outputs-dir examples/outputs \
  --json examples/outputs/leveraged_etp_risk_lab_adapter.json
```

The command reads existing JSON artifacts, emits relative source artifact paths
with SHA-256 hashes, and writes profile-shaped payloads for optional downstream
consumers. See [`docs/integrations.md`](docs/integrations.md) for field examples
and boundary notes. These adapter files are generated artifacts; rerun the
commands after refreshing `examples/outputs`.

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

Export a deterministic single-file reference for CLI usage, accepted input
schemas, generated artifact inventory, safety boundaries, and a generated
example snippet:

```bash
portfolio-risk-compass docs-export
```

By default this writes
[`examples/outputs/docs_export.md`](examples/outputs/docs_export.md). The export
is Markdown or no-JavaScript HTML:

```bash
portfolio-risk-compass docs-export \
  --outputs-dir examples/outputs \
  --output dist/portfolio-risk-compass-reference.html \
  --format html
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
bundle generation, dashboard export, adapter export regeneration, release
manifest generation, a privacy scan over the refreshed repository artifacts,
and the package audit command.

Scan repository text for local/private terms and token-like patterns:

```bash
python scripts/privacy_scan.py
python scripts/privacy_scan.py --term "internal-project-name"
python scripts/privacy_scan.py --exclude "examples/fixtures/public-demo-*"
```

The scanner reports only file locations and rule names. It does not print the
matched private term or token-like value. Use `--exclude` only for paths that
are intentionally public fixtures or generated examples.

Copy the public agent skill into a local skills directory:

```bash
python scripts/sync_local_skill.py --target-dir ~/.codex/skills
```

The sync command writes `portfolio-risk-compass/SKILL.md` under `--target-dir`
and adapts the README link for that target location. Use `--dry-run` to preview
the destination without writing files.
