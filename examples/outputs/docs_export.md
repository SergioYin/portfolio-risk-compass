# Portfolio Risk Compass Docs Export

- Package: portfolio-risk-compass
- Version: 0.5.2
- Format: deterministic single-file Markdown, no JavaScript

## CLI Reference

### `analyze`

Analyze holdings exposure and write JSON or Markdown reports.

Usage: `portfolio-risk-compass analyze [-h] [--config CONFIG] [--json JSON] [--markdown MARKDOWN] holdings_csv`

| Argument | Required | Description |
| --- | --- | --- |
| `holdings_csv` | yes | Path to holdings CSV. |
| `--config` | no | Optional JSON config with grouping, targets, and limits. |
| `--json` | no | Write JSON report to this path. |
| `--markdown` | no | Write Markdown report to this path. |

### `case-study`

Read a demo-bundle index manifest and generated JSON artifacts, then write Markdown and JSON case-study comparison artifacts for the base demo, ETF core, leveraged sleeve, and cash rebalance examples. The comparison is static and does not provide investment advice.

Usage: `portfolio-risk-compass case-study [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown comparison. Defaults to examples/outputs/case_study_comparison.md. |
| `--json` | no | Path to write the machine-readable comparison. Defaults to examples/outputs/case_study_comparison.json. |

### `catalysts`

Read a catalysts JSON fixture and render a date-ordered checklist with overdue, today, and upcoming flags relative to --as-of.

Usage: `portfolio-risk-compass catalysts [-h] [--as-of AS_OF] [--json JSON] [--markdown MARKDOWN] catalysts_json`

| Argument | Required | Description |
| --- | --- | --- |
| `catalysts_json` | yes | Path to catalysts JSON. |
| `--as-of` | no | Reference date for overdue and upcoming flags. Defaults to today's date. |
| `--json` | no | Write JSON checklist to this path. |
| `--markdown` | no | Write Markdown checklist to this path. |

### `dashboard`

Read an exposure report JSON or demo-bundle index manifest and write a single self-contained HTML dashboard with no JavaScript.

Usage: `portfolio-risk-compass dashboard [-h] [--title TITLE] input_json output_html`

| Argument | Required | Description |
| --- | --- | --- |
| `input_json` | yes | Path to exposure_report.json or a demo-bundle index.json manifest. |
| `output_html` | yes | Path to write the static dashboard HTML. |
| `--title` | no | Dashboard title. Defaults to 'Portfolio Risk Compass Dashboard'. |

### `demo-bundle`

Regenerate examples/outputs artifacts from examples/fixtures, including reports, snapshot, catalyst checklist, guardrails, stress results, template gallery outputs, and index manifest.

Usage: `portfolio-risk-compass demo-bundle [-h] [--fixtures-dir FIXTURES_DIR] [--output-dir OUTPUT_DIR] [--as-of AS_OF] [--templates-dir TEMPLATES_DIR] [--no-templates]`

| Argument | Required | Description |
| --- | --- | --- |
| `--fixtures-dir` | no | Directory containing demo fixtures. Defaults to examples/fixtures. |
| `--output-dir` | no | Directory to write demo artifacts. Defaults to examples/outputs. |
| `--as-of` | no | Reference date for date-sensitive demo outputs. Defaults to 2026-05-15. |
| `--templates-dir` | no | Directory containing template fixtures. Defaults to examples/templates. |
| `--no-templates` | no | Only render the base demo fixtures, without template gallery outputs. |

### `diff`

Compare total value, allocation buckets, concentration, and target drift between two snapshot JSON files.

Usage: `portfolio-risk-compass diff [-h] [--json] before_snapshot after_snapshot`

| Argument | Required | Description |
| --- | --- | --- |
| `before_snapshot` | yes | Earlier snapshot JSON. |
| `after_snapshot` | yes | Later snapshot JSON. |
| `--json` | no | Print JSON instead of Markdown. |

### `docs-export`

Write CLI reference, input schemas, artifact inventory, safety boundary, and generated example output to one no-JavaScript Markdown or HTML file.

Usage: `portfolio-risk-compass docs-export [-h] [--output OUTPUT] [--outputs-dir OUTPUTS_DIR] [--format {markdown,html}] [--title TITLE]`

| Argument | Required | Description |
| --- | --- | --- |
| `--output` | no | Path to write the docs file. Defaults to examples/outputs/docs_export.md. |
| `--outputs-dir` | no | Directory to inventory. Defaults to examples/outputs. |
| `--format` | no | Docs format. Defaults to Markdown. |
| `--title` | no | Document title. |

### `guardrails`

Evaluate position, sector, cash, leverage, and review cadence guardrails against holdings and config.

Usage: `portfolio-risk-compass guardrails [-h] --config CONFIG [--snapshot-date SNAPSHOT_DATE] [--last-review-date LAST_REVIEW_DATE] [--format {json,markdown}] [--json JSON] [--markdown MARKDOWN] holdings_csv`

| Argument | Required | Description |
| --- | --- | --- |
| `holdings_csv` | yes | Path to holdings CSV. |
| `--config` | yes | JSON config with guardrail policy fields. |
| `--snapshot-date` | no | Portfolio snapshot date for review cadence checks. Defaults to today. |
| `--last-review-date` | no | Last completed portfolio review date. Overrides config last_review_date. |
| `--format` | no | Stdout format when no output path is provided. |
| `--json` | no | Write JSON review to this path. |
| `--markdown` | no | Write Markdown review to this path. |

### `history`

Read snapshot JSON files from a directory and render total value trends, target exposure drift, guardrail status when present, and catalyst counts when present.

Usage: `portfolio-risk-compass history [-h] [--format {json,markdown}] [--json JSON] [--markdown MARKDOWN] snapshots_dir`

| Argument | Required | Description |
| --- | --- | --- |
| `snapshots_dir` | yes | Directory containing snapshot JSON files. |
| `--format` | no | Stdout format when no output path is provided. |
| `--json` | no | Write JSON ledger to this path. |
| `--markdown` | no | Write Markdown ledger to this path. |

### `integration-export`

Read generated output artifacts and write deterministic adapter JSON for optional downstream workflows without importing or depending on them.

Usage: `portfolio-risk-compass integration-export [-h] [--outputs-dir OUTPUTS_DIR] [--json JSON] {invest-thesis-ledger,leveraged-etp-risk-lab}`

| Argument | Required | Description |
| --- | --- | --- |
| `profile` | yes | Adapter profile to render. |
| `--outputs-dir` | no | Directory containing generated artifacts. Defaults to examples/outputs. |
| `--json` | no | Path to write adapter JSON. Prints JSON to stdout when omitted. |

### `package-audit`

Report the package version, CLI command count, fixture count, output artifact count, missing packaging items, and optionally run tests.

Usage: `portfolio-risk-compass package-audit [-h] [--root ROOT] [--format {json,markdown}] [--run-tests]`

| Argument | Required | Description |
| --- | --- | --- |
| `--root` | no | Repository root to audit. Defaults to the current working directory. |
| `--format` | no | Report format. Defaults to JSON. |
| `--run-tests` | no | Run the unittest suite and include the result in the report. |

### `public-review`

Read a demo-bundle index manifest and write deterministic Markdown and JSON public-review artifacts with exact rerun commands, SHA-256 hashes, and no-live-data, no-broker, no-advice boundaries.

Usage: `portfolio-risk-compass public-review [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown public-review packet. Defaults to examples/outputs/public_review_walkthrough.md. |
| `--json` | no | Path to write the machine-readable public-review packet. Defaults to examples/outputs/public_review_walkthrough.json. |

### `rebalance-watchlist`

Combine target drift, guardrail WARN/FAIL items, concentration, and stress drawdowns into a broker-free educational review watchlist with reason codes and severity. The output does not recommend trades or quantities.

Usage: `portfolio-risk-compass rebalance-watchlist [-h] --config CONFIG [--snapshot-date SNAPSHOT_DATE] [--last-review-date LAST_REVIEW_DATE] [--format {json,markdown}] [--json JSON] [--markdown MARKDOWN] holdings_csv scenario_json`

| Argument | Required | Description |
| --- | --- | --- |
| `holdings_csv` | yes | Path to holdings CSV. |
| `scenario_json` | yes | Path to scenario JSON. |
| `--config` | yes | JSON config with targets and guardrail policy fields. |
| `--snapshot-date` | no | Portfolio snapshot date for review cadence checks. Defaults to today. |
| `--last-review-date` | no | Last completed portfolio review date. Overrides config last_review_date. |
| `--format` | no | Stdout format when no output path is provided. |
| `--json` | no | Write JSON watchlist to this path. |
| `--markdown` | no | Write Markdown watchlist to this path. |

### `release-manifest`

Create JSON and Markdown release artifact inventories for examples/outputs with byte sizes and SHA-256 hashes.

Usage: `portfolio-risk-compass release-manifest [-h] [--outputs-dir OUTPUTS_DIR] [--json JSON] [--markdown MARKDOWN]`

| Argument | Required | Description |
| --- | --- | --- |
| `--outputs-dir` | no | Directory to inventory. Defaults to examples/outputs. |
| `--json` | no | Path to write JSON manifest. Defaults to examples/outputs/release_manifest.json. |
| `--markdown` | no | Path to write Markdown manifest. Defaults to examples/outputs/release_manifest.md. |

### `review-memo`

Read exposure, guardrails, stress, catalysts, history, and rebalance watchlist JSON artifacts from an outputs directory and combine them into a single Markdown memo with assumptions and a non-advice boundary.

Usage: `portfolio-risk-compass review-memo [-h] [--outputs-dir OUTPUTS_DIR] [--markdown MARKDOWN] [--title TITLE]`

| Argument | Required | Description |
| --- | --- | --- |
| `--outputs-dir` | no | Directory containing generated JSON artifacts. Defaults to examples/outputs. |
| `--markdown` | no | Path to write the Markdown memo. Prints Markdown to stdout when omitted. |
| `--title` | no | Memo title. Defaults to 'Portfolio Review Memo'. |

### `reviewer-evidence`

Read a demo-bundle index manifest and write deterministic Markdown and JSON evidence showing which dashboard and case-study artifacts exist and which fixture files feed them.

Usage: `portfolio-risk-compass reviewer-evidence [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown evidence. Defaults to examples/outputs/reviewer_evidence.md. |
| `--json` | no | Path to write the machine-readable evidence. Defaults to examples/outputs/reviewer_evidence.json. |

### `scenario-evidence-receipt`

Read a demo-bundle index manifest and write deterministic Markdown and JSON receipts tying static holdings, config, and scenario fixtures to stress, guardrail, and dashboard artifacts. The receipt records hashes and broker-free, no-live-data, no-advice boundaries.

Usage: `portfolio-risk-compass scenario-evidence-receipt [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown receipt. Defaults to examples/outputs/scenario_evidence_receipt.md. |
| `--json` | no | Path to write the machine-readable receipt. Defaults to examples/outputs/scenario_evidence_receipt.json. |

### `screenshot-guide`

Read a demo-bundle index manifest and write deterministic Markdown and JSON guide artifacts tying the static public dashboard route to an exact Chromium screenshot command, source artifact hashes, screenshot hashes, and no-live-data, no-broker, no-advice boundaries.

Usage: `portfolio-risk-compass screenshot-guide [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON] [--screenshot-path SCREENSHOT_PATH]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown screenshot guide. Defaults to examples/outputs/dashboard_screenshot_guide.md. |
| `--json` | no | Path to write the machine-readable screenshot guide. Defaults to examples/outputs/dashboard_screenshot_guide.json. |
| `--screenshot-path` | no | Screenshot path relative to the manifest directory. Defaults to screenshots/dashboard-public-review-1365x900.png. |

### `showcase`

Read a demo-bundle index manifest and write deterministic Markdown and JSON walkthrough artifacts for the base demo plus every generated template. The walkthrough is a static review guide and does not provide investment advice.

Usage: `portfolio-risk-compass showcase [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown walkthrough. Defaults to examples/outputs/walkthrough.md. |
| `--json` | no | Path to write the machine-readable walkthrough. Defaults to examples/outputs/walkthrough.json. |

### `snapshot`

Analyze holdings and save a JSON snapshot with date and id metadata.

Usage: `portfolio-risk-compass snapshot [-h] [--config CONFIG] [--date DATE] [--id ID] holdings_csv output_json`

| Argument | Required | Description |
| --- | --- | --- |
| `holdings_csv` | yes | Path to holdings CSV. |
| `output_json` | yes | Path to write snapshot JSON. |
| `--config` | no | Optional JSON config with grouping, targets, and limits. |
| `--date` | no | Snapshot date metadata. Defaults to today's date. |
| `--id` | no | Snapshot id metadata. Defaults to a generated id. |

### `stress`

Apply named percentage price shocks by symbol, sector, asset_class, region, or currency and report stressed market value plus contribution deltas.

Usage: `portfolio-risk-compass stress [-h] [--format {json,markdown}] [--json JSON] [--markdown MARKDOWN] holdings_csv scenario_json`

| Argument | Required | Description |
| --- | --- | --- |
| `holdings_csv` | yes | Path to holdings CSV. |
| `scenario_json` | yes | Path to scenario JSON. |
| `--format` | no | Stdout format when no output path is provided. |
| `--json` | no | Write JSON stress report to this path. |
| `--markdown` | no | Write Markdown stress report to this path. |

### `template-list`

List named example portfolio templates with their holdings, config, catalysts, and scenario fixture files.

Usage: `portfolio-risk-compass template-list [-h] [--templates-dir TEMPLATES_DIR] [--format {json,markdown}]`

| Argument | Required | Description |
| --- | --- | --- |
| `--templates-dir` | no | Directory containing template fixtures. Defaults to examples/templates. |
| `--format` | no | Output format. Defaults to JSON. |

### `visual-evidence-receipt`

Read a demo-bundle index manifest and write deterministic Markdown and JSON receipts tying the static dashboard, public-review walkthrough, scenario evidence, reviewer evidence export, and broker-free/no-advice boundaries into one visual review route.

Usage: `portfolio-risk-compass visual-evidence-receipt [-h] [--manifest MANIFEST] [--markdown MARKDOWN] [--json JSON]`

| Argument | Required | Description |
| --- | --- | --- |
| `--manifest` | no | Demo-bundle manifest to read. Defaults to examples/outputs/index.json. |
| `--markdown` | no | Path to write the Markdown visual evidence receipt. Defaults to examples/outputs/visual_evidence_receipt.md. |
| `--json` | no | Path to write the machine-readable visual evidence receipt. Defaults to examples/outputs/visual_evidence_receipt.json. |

## Input Schemas

### holdings.csv

Portfolio holdings table consumed by analyze, snapshot, guardrails, stress, and rebalance-watchlist flows.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `symbol` | string | yes | Required ticker or identifier, normalized to uppercase. |
| `quantity` | decimal | yes | Required non-negative decimal. |
| `price` | decimal | yes | Required non-negative decimal. |
| `asset_class` | string | yes | Required exposure bucket. |
| `sector` | string | yes | Required exposure bucket. |
| `region` | string | yes | Required exposure bucket. |
| `currency` | string | yes | Required currency code, normalized to uppercase. |
| `name` | string | no | Optional display name. |

### config.json

Portfolio policy, grouping, targets, and guardrail settings.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `base_currency` | string | no | Defaults to USD and is normalized to uppercase. |
| `group_by` | array[string] | no | Defaults to asset_class, sector, region, currency. Supported values: asset_class, currency, region, sector. |
| `concentration_limit_pct` | decimal | no | Defaults to 25. |
| `max_position_pct` | decimal | no | Non-negative position guardrail limit. |
| `max_sector_pct` | decimal | no | Non-negative sector guardrail limit. |
| `min_cash_pct` | decimal | no | Non-negative cash floor guardrail. |
| `max_leverage_multiple` | decimal | no | Non-negative leverage guardrail. |
| `required_review_cadence_days` | integer | no | Positive integer review cadence. |
| `last_review_date` | date | no | ISO date in YYYY-MM-DD format. |
| `target_allocations` | object | no | Object keyed by supported group name, then bucket, with decimal target percentages. |

### scenario.json

Stress scenario with named price shocks.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | yes | Scenario name. |
| `shocks` | array[object] | yes | Non-empty array of shock objects. |
| `shocks[].name` | string | yes | Shock name. |
| `shocks[].selector` | string | yes | Exactly one selector field must be present: symbol, sector, asset_class, region, currency. |
| `shocks[].price_move_pct` | decimal | yes | Percentage price move, greater than or equal to -100. move_pct is accepted as an alias. |

### catalysts.json

Catalyst checklist fixture.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `symbol` | string | yes | Ticker or identifier, normalized to uppercase. |
| `date` | date | yes | ISO date in YYYY-MM-DD format. |
| `title` | string | yes | Non-empty string. |
| `importance` | string | yes | Non-empty string. |
| `thesis_link` | string | yes | Non-empty string. |
| `action` | string | yes | Non-empty string. |

### history/*.json

Directory of generated snapshot JSON files for the history ledger.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `snapshot.date` | date | yes | ISO date used for chronological ordering. |
| `snapshot.id` | string | yes | Snapshot identifier. |
| `report.metadata.total_market_value` | decimal string | yes | Snapshot portfolio value. |
| `report.target_drift` | object | no | Target drift rows copied from snapshot output. |
| `guardrails` | object | no | Optional guardrail review summary embedded in the snapshot fixture. |
| `catalysts` | object | no | Optional catalyst checklist summary embedded in the snapshot fixture. |

## Artifact Inventory

- Outputs directory: examples/outputs
- Artifact count: 70

| Path | Format | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| case_study_comparison.json | json | 8586 | `c095f5c612e59da2bf1322d75bcb8e179b45a4a31f96e9ccbc2e7b099b61e844` |
| case_study_comparison.md | markdown | 3190 | `1b8188a950bed8d61d767e9f48b5597f2482eb5e8a82458f87ba89853c82c781` |
| catalysts.json | json | 1198 | `4e6b573a6d29b4b0be1f0f5e9529dfc99be849dd760cfa3f8668f902a45a27c1` |
| catalysts.md | markdown | 711 | `6208400c99633ff86103cf3eafa12d6af7291fca0703e35f220fff2b96518da6` |
| dashboard.html | html | 18102 | `f716c91351ca9e645f80476ce8c1761d0b3d802b4fae41ea8e2a99bb24bb393f` |
| dashboard_preview.md | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| dashboard_screenshot_guide.json | json | 3937 | `50453e60f2ab429e3ab99dbf8fdbadd03409d1bed1af6c32e794e8becfbfc321` |
| dashboard_screenshot_guide.md | markdown | 3047 | `1b1d92fed27f9fb2b5e8bdefd1c2f47b42ddaf0134748ed649f1f72f6690e072` |
| dashboard_snippet.html | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| exposure_report.json | json | 3747 | `d63966a67e039b083d07cd4512d7e46d35b69d32c7afd02dc3001d3e23e9dd9c` |
| exposure_report.md | markdown | 1247 | `c0186b554d8659e42d0aa4b11bd6a37813fa1dc655982e3d940617599271c1b6` |
| gallery.md | markdown | 2189 | `d7c5b1261c32106afe47f75bda871ff629f9779d551cb6e989f2c9c28f21465e` |
| guardrails.json | json | 2644 | `bdf5d7a60bfb35244cb4e86173316fbcd5d58750b222d5915331e3e7b5451c82` |
| guardrails.md | markdown | 1227 | `36cacf3305c25f59d63816ebc2201a217f10fb72df8be2344fad28c3e7344e3c` |
| history.json | json | 5520 | `0a90df843340771135e341619be8880d93b9fc2cff4dedfb02c24fe80bc5b6f7` |
| history.md | markdown | 1219 | `782ac8b595ab43a3dcc684e84f019f8e774384b205763884d3f26b67b15cc186` |
| index.json | json | 17613 | `e65d032fd007f67b5fec5fa348c3f90eb5434d171f872b0042d2ccdb56385395` |
| invest_thesis_ledger_adapter.json | json | 2441 | `4c4351aaf1ad9a8930cee64a82163619170692ceacf7f2bbc05301eb8ab5ea0a` |
| leveraged_etp_risk_lab_adapter.json | json | 3954 | `866db8127afbabf788523aa45d66603810026fe947c901ff7626d08294a07170` |
| public_review_walkthrough.json | json | 9032 | `a60e13a73f2f0a16fe188b0ed4a8c6d375fa99e3d150628028bf1f2cf240fbef` |
| public_review_walkthrough.md | markdown | 6952 | `6222fd4e6b4404ac7cbc14bbf927c51c84230bdf7bb39635d860a1355c66cd60` |
| rebalance_watchlist.json | json | 6298 | `14986aed95f9287983dc71e5ea5bc36429c689aa8515d4e9aa8b7157474b5c80` |
| rebalance_watchlist.md | markdown | 2386 | `d36cea814fee02520e73f53bc164369c289e8dff97b7bc08d244e9eaf70253ae` |
| release_manifest.json | json | 13118 | `f571d906418a731bb8e09903452424c086729618810ae845865e4264b66c2254` |
| release_manifest.md | markdown | 8279 | `b482e1258a91a896e8c3d4dacc2af2caf9a833e017a483bf0222099b0d5e1e6c` |
| review_memo.md | markdown | 6337 | `cbe1ec3234c60993c26f3f9cd9be4cc91a02683f19ca408f7aaee2cf5f7889d8` |
| reviewer_evidence.json | json | 5754 | `2b0d5c7dd6c308591ce969f7b51a7f430bd4f0262d19c596b89e09ca9463de7a` |
| reviewer_evidence.md | markdown | 3455 | `9d548e90b209b2210f1d6e75818c2a368d2479e5e44a71910ccb88b762e5637c` |
| scenario_evidence_receipt.json | json | 10582 | `ce3a73a08bdd6e28d003f0f7edf5b718deb66b9fc7b7068371a84ec669210d35` |
| scenario_evidence_receipt.md | markdown | 8257 | `ae25215b7e5dd2a96bec73fe076d1e67e2d747ef0b28c26ee095939a602b69fc` |
| snapshot_current.json | json | 4167 | `86a21abdb6c48e054f7524858dbecec2f3f101506680cdaef1f23d4b0a52ff7b` |
| stress.json | json | 4029 | `d7693910dc7c2b6e90c5d4029b41e557be9d26a2ef2c22999e452c0e11c9e58c` |
| stress.md | markdown | 1024 | `1066d939df0e190691409dc8b028033f077211f45a464db466703b241b86adb8` |
| templates/cash-rebalance/catalysts.json | json | 1233 | `c856b823b725ca0925d2e2e5aed104e6831ae1ab38ad21d25beff558590d41b4` |
| templates/cash-rebalance/catalysts.md | markdown | 751 | `8fca7d5a4ffb4d421e6eaa71f8c6f0cb1d55b8c3a1cf89c3bb2ab24d1fb17c3f` |
| templates/cash-rebalance/exposure_report.json | json | 4711 | `11e054a432a49082656d7d906d7c0ddb4249ec8cb2b0def40c1f8acf818f685e` |
| templates/cash-rebalance/exposure_report.md | markdown | 1603 | `37261f53c042abdddebb9791f1f51fdc2b60303e3bce071125d9cc092e1f4191` |
| templates/cash-rebalance/guardrails.json | json | 3063 | `7f95da29d0fd028673ef0046b10f4b0028e9bb0decd1311fad3bf0d66ee051b3` |
| templates/cash-rebalance/guardrails.md | markdown | 1401 | `7bd2ca6bff41e85c1ed841203bd5cb8d00815f2ea528716bfc8a2a6f1d005890` |
| templates/cash-rebalance/rebalance_watchlist.json | json | 9243 | `e6fbe69d797f9ff2b75a96aa0e483865d54c7c26f551dc9d9bd24cf575db00ab` |
| templates/cash-rebalance/rebalance_watchlist.md | markdown | 3519 | `c6bcdc7dc3ee3f6974d413d71376f8f0bb5181446cc949c4437136468a04f205` |
| templates/cash-rebalance/snapshot_current.json | json | 5220 | `f0501512b7b91c3b598e7d3c59243e57fb10c64e234ec36c02749bd1e4c8fb63` |
| templates/cash-rebalance/stress.json | json | 4947 | `b8a492b89f529b7628ddc7252ab53c4b641ec4d95c177ede4b89629b89431106` |
| templates/cash-rebalance/stress.md | markdown | 1121 | `b6b54c5519623a1129a0e4efbed254f39e1e02757553aac73c298ed1f6211697` |
| templates/etf-core/catalysts.json | json | 1221 | `b50fbf2ec08df456f6322dff824e6a9d028d982983ab5f8aa574d972655eca31` |
| templates/etf-core/catalysts.md | markdown | 742 | `11740e73735df27e2a2c015c6da84ce09bbcec1debb55f5ab3ca8ae58a5fd825` |
| templates/etf-core/exposure_report.json | json | 3917 | `820c1680faa166cf6a55f1242e56e5f97f8116b5d8a063a213b993e7e90e4ad1` |
| templates/etf-core/exposure_report.md | markdown | 1384 | `73f29c1fa9ef9933b5047d40f0677ef09b0064ebe9c9ce27bb3395e5ab77b43f` |
| templates/etf-core/guardrails.json | json | 2437 | `8cb9fda70fd244ecc3535f592f3126ae69ae883e3d49ea8fd3f0451461ab68a7` |
| templates/etf-core/guardrails.md | markdown | 1135 | `182b86b6181661f3ed2dd5e4d0f88f3efaa301cc7cc211fee152029bbc36dae7` |
| templates/etf-core/rebalance_watchlist.json | json | 9512 | `12c35f366fcb9863550afcd0806d80c34ac3841e56653b0636e51ef325cb9efc` |
| templates/etf-core/rebalance_watchlist.md | markdown | 3456 | `05f1290fe6b74a77407844492b962405cce275f25d993ca8801555785bd56776` |
| templates/etf-core/snapshot_current.json | json | 4356 | `774d480e568d53ebc6c06dd246318139a309904e2b64194e195f60b7ee97749a` |
| templates/etf-core/stress.json | json | 4765 | `015a952180e48fd5a4e61d406d74095c99970f0a68dc442268e8151b6bca9dac` |
| templates/etf-core/stress.md | markdown | 1054 | `3f434fd71a0ec5199f53f5bb79bd3d66a286b6911d66118b339bf0f16bb40e87` |
| templates/leveraged-sleeve/catalysts.json | json | 1236 | `a3755874f1afa03e68cafb3de229413b8ded622a21dd8d3ea4780974dbce3a97` |
| templates/leveraged-sleeve/catalysts.md | markdown | 759 | `3cb4f7f4290348cb00a5c2b1ca1091f5e8d610bda0f8edbf2dd64b257b7fb232` |
| templates/leveraged-sleeve/exposure_report.json | json | 4669 | `f820d12ea644faddea454430d29488bbae983253dc979e985dd4837476fc2148` |
| templates/leveraged-sleeve/exposure_report.md | markdown | 1553 | `20b378d2af04c71f88f0c5d7300b0781c368d4a218fef4c703bb4afdd334267a` |
| templates/leveraged-sleeve/guardrails.json | json | 2820 | `b502ec1b19bb59d07e77af0eb609c8f936f020fa87edf97af2914582ba6682d3` |
| templates/leveraged-sleeve/guardrails.md | markdown | 1291 | `f43bed65e5a4dcd315d9d60f07a7f532133cc989a8895bd585879d373fade346` |
| templates/leveraged-sleeve/rebalance_watchlist.json | json | 10144 | `3f4f8700f450c90577e8711b324943da1d8a338343800bc14baa074e3e8b5e9b` |
| templates/leveraged-sleeve/rebalance_watchlist.md | markdown | 3701 | `56e873a049c0e213cabe1b015844e0a53e17b275018b9b83f28c65473121474c` |
| templates/leveraged-sleeve/snapshot_current.json | json | 5184 | `b453529a58df60e5a11e59593b3d3cd316cb0e781cfb1eef67b2208b35959217` |
| templates/leveraged-sleeve/stress.json | json | 4930 | `99137b3a1c01c768332704ea10bb741dbdf7925062d8a9e301bd24f59d2eeb34` |
| templates/leveraged-sleeve/stress.md | markdown | 1129 | `070fa448f12cf1fd1e1e7f5101d32de99e69906220ebbd1115ba29a630d16b89` |
| visual_evidence_receipt.json | json | 5519 | `fe6a08475103ec55faee443304ca57fac59bac763c66e4ca43e0ae87e58e291f` |
| visual_evidence_receipt.md | markdown | 3950 | `1f53c3c967d5139a73afd8edd839fad1b2fbcbb5070274f68e4df7bfc035c655` |
| walkthrough.json | json | 7585 | `11b4f0420d8c7f92c252b2307468e6467e30d3734c491d894034430fd4bcca02` |
| walkthrough.md | markdown | 3568 | `85169963cfbefa4ad317fd458e9109dbbca23050acd4d4230eeb6fec9c89a932` |

## Safety Boundary

- Review memo: This memo is for human portfolio review and education only. It is not investment, tax, legal, accounting, or trading advice, and it does not recommend buying, selling, holding, position sizes, order types, account transfers, or timing.
- Rebalance watchlist: Educational portfolio review only. This watchlist does not recommend trades, order types, position quantities, account transfers, or timing. Use it to decide what deserves human review against your own policy.
- Data boundary: This package reads user-provided CSV/JSON fixtures and generated local artifacts. It does not fetch market data, place orders, or connect to brokerage accounts.

## Generated Example Output

```bash
portfolio-risk-compass docs-export --output examples/outputs/docs_export.md
```

```markdown
# Portfolio Risk Compass Docs Export

- Package: portfolio-risk-compass
- Version: 0.2.0
- Format: deterministic single-file Markdown, no JavaScript

## CLI Reference
```
