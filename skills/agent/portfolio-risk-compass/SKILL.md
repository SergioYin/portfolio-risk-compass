# Portfolio Risk Compass Agent Protocol

Public reference: [README](../../../README.md)

## Triggers

Use this skill when a user asks an agent to inspect, analyze, compare, stress,
or package portfolio risk data with `portfolio-risk-compass`.

Typical requests include:

- Build an exposure report from a holdings CSV.
- Compare portfolio snapshots.
- Build a history ledger from a snapshot directory.
- Check configured guardrails.
- Run scenario stress analysis.
- Build an educational rebalance review watchlist without trade quantities.
- Prepare a catalyst checklist.
- Assemble generated artifacts into a human review memo.
- Generate the demo bundle, guided showcase walkthrough, static dashboard, or public review packet.
- Audit package readiness or create a release manifest.

## Task Routing

Route tasks to the command that matches the requested output:

- Exposure summaries: `portfolio-risk-compass analyze`.
- Dated portfolio state: `portfolio-risk-compass snapshot`.
- Snapshot comparison: `portfolio-risk-compass diff`.
- Snapshot ledger trends: `portfolio-risk-compass history`.
- Policy checks: `portfolio-risk-compass guardrails`.
- Scenario shocks: `portfolio-risk-compass stress`.
- Educational rebalance review watchlist: `portfolio-risk-compass rebalance-watchlist`.
- Catalyst tracking: `portfolio-risk-compass catalysts`.
- Human review memo: `portfolio-risk-compass review-memo`.
- Demo artifacts: `portfolio-risk-compass demo-bundle`.
- Guided showcase walkthrough: `portfolio-risk-compass showcase`.
- Dashboard export: `portfolio-risk-compass dashboard`.
- Public dashboard review packet: `portfolio-risk-compass public-review`.
- Package checks: `portfolio-risk-compass package-audit`.
- Output inventory: `portfolio-risk-compass release-manifest`.

If the console script is unavailable, use:

```bash
PYTHONPATH=src python -m portfolio_risk_compass --help
```

## Core Commands

Analyze holdings:

```bash
portfolio-risk-compass analyze examples/fixtures/holdings.csv \
  --config examples/fixtures/config.json \
  --json report.json \
  --markdown report.md
```

Create a snapshot:

```bash
portfolio-risk-compass snapshot examples/fixtures/holdings.csv snapshots/current.json \
  --config examples/fixtures/config.json \
  --date 2026-05-15 \
  --id close-2026-05-15
```

Compare snapshots:

```bash
portfolio-risk-compass diff snapshots/previous.json snapshots/current.json --json
```

Build a history ledger:

```bash
portfolio-risk-compass history examples/fixtures/history \
  --json history.json \
  --markdown history.md
```

Check guardrails:

```bash
portfolio-risk-compass guardrails examples/fixtures/holdings.csv \
  --config examples/fixtures/config.json \
  --json guardrails.json \
  --markdown guardrails.md
```

Run stress analysis:

```bash
portfolio-risk-compass stress examples/fixtures/holdings.csv examples/fixtures/scenario.json \
  --json stress.json \
  --markdown stress.md
```

Build an educational rebalance review watchlist:

```bash
portfolio-risk-compass rebalance-watchlist examples/fixtures/holdings.csv examples/fixtures/scenario.json \
  --config examples/fixtures/config.json \
  --json rebalance_watchlist.json \
  --markdown rebalance_watchlist.md
```

Treat watchlist output as review evidence only. It must not be converted into
trade instructions, order types, position quantities, account transfers, or
timing recommendations.

Build catalysts:

```bash
portfolio-risk-compass catalysts examples/fixtures/catalysts.json \
  --as-of 2026-05-15 \
  --json catalysts.json \
  --markdown catalysts.md
```

Assemble a human review memo from generated artifacts:

```bash
portfolio-risk-compass review-memo \
  --outputs-dir examples/outputs \
  --markdown review_memo.md
```

Treat memo output as educational review context only. It is not investment,
tax, legal, accounting, or trading advice and must not be converted into
buy, sell, hold, sizing, order type, transfer, or timing recommendations.

Build demo outputs and dashboard:

```bash
portfolio-risk-compass demo-bundle \
  --fixtures-dir examples/fixtures \
  --output-dir examples/outputs \
  --as-of 2026-05-15

portfolio-risk-compass showcase \
  --manifest examples/outputs/index.json \
  --markdown examples/outputs/walkthrough.md \
  --json examples/outputs/walkthrough.json

portfolio-risk-compass dashboard examples/outputs/index.json examples/outputs/dashboard.html

portfolio-risk-compass public-review \
  --manifest examples/outputs/index.json \
  --markdown examples/outputs/public_review_walkthrough.md \
  --json examples/outputs/public_review_walkthrough.json

portfolio-risk-compass visual-evidence-receipt
```

Validate the repository:

```bash
python scripts/selfcheck.py
```

## Inputs

Expected inputs are plain files:

- Holdings CSV with symbols, quantities, prices, and classification fields.
- Optional config JSON for targets, concentration limits, and guardrails.
- Scenario JSON with named price shocks and exactly one selector per shock.
- Catalyst JSON with symbol, date, title, importance, thesis link, and action.
- Snapshot JSON files previously generated by this package.
- Output manifest JSON generated by `demo-bundle` or `release-manifest`.

Use relative paths in examples and responses unless the user provides a
different path style.

## Outputs

Commands produce deterministic JSON, Markdown, or static HTML depending on the
flags supplied. If no output file is supplied for report commands, JSON is
printed to stdout unless the command supports and receives another format.

Summarize generated artifacts by relative path, format, and purpose. Mention
important warnings, failures, or validation errors before lower-risk details.

## Validation

Before reporting completion:

- Run `python scripts/selfcheck.py` when code, tests, examples, or packaged
  artifacts changed.
- Run targeted unit tests when only tests or documentation around a narrow
  behavior changed.
- For agent protocol edits, verify that
  `skills/agent/portfolio-risk-compass/SKILL.md` exists and includes the
  required public sections.
- Inspect generated JSON or Markdown enough to confirm that requested data is
  present and paths point to expected artifacts.

## Safety Boundaries

This package provides deterministic portfolio exposure tooling. It does not
provide personalized investment, tax, legal, or accounting advice.

Agents must:

- Treat outputs as analysis artifacts, not trade recommendations.
- Avoid inventing holdings, prices, classifications, dates, or catalysts.
- Preserve user-provided files unless explicitly asked to overwrite them.
- Avoid exposing secrets or credentials in reports, examples, logs, or docs.
- State when an input is missing, malformed, stale, or outside the supported
  schema.
- Keep generated examples generic and public-safe.

## Response Rules

When responding to users:

- Lead with the result, generated paths, or blocking validation issue.
- Use concise, factual language.
- Include the command that was run when it helps reproduce the result.
- Cite relative file paths for artifacts and source inputs.
- Call out `PASS`, `WARN`, and `FAIL` guardrail statuses explicitly.
- Use exact dates when discussing snapshots, catalysts, or review cadence.
- Do not claim live market accuracy unless the user provided live data and the
  command consumed it.

## Done Criteria

A task is done when:

- The requested command or edit has been completed.
- Required outputs exist at the expected relative paths.
- Validation has passed, or any skipped validation is stated with the reason.
- The final response lists material outputs, notable risk findings, and any
  remaining user action needed to proceed.
