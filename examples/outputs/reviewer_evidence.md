# Portfolio Risk Compass Reviewer Evidence

Deterministic trace for public dashboard and case-study demo artifacts.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.

- As of: 2026-05-15

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence`

## Dashboard Evidence

| Artifact | Status | Sources | Bytes |
| --- | --- | --- | ---: |
| [gallery.md](gallery.md) | sidecar | `index.json` | 2189 |
| [dashboard_preview.md](dashboard_preview.md) | sidecar | `index.json` | 1244 |
| [dashboard_snippet.html](dashboard_snippet.html) | sidecar | `index.json` | 876 |
| [walkthrough.md](walkthrough.md) | sidecar | `index.json` | 3568 |
| [walkthrough.json](walkthrough.json) | sidecar | `index.json` | 7259 |

## Case-Study Evidence

| Artifact | Status | Sources | Bytes |
| --- | --- | --- | ---: |
| [case_study_comparison.md](case_study_comparison.md) | manifested | `index.json`, `generated JSON artifacts`, `examples/fixtures/holdings.csv`, `examples/fixtures/config.json`, `examples/fixtures/catalysts.json`, `examples/fixtures/scenario.json`, `examples/fixtures/history/*.json`, `examples/templates/cash-rebalance/holdings.csv`, `examples/templates/cash-rebalance/config.json`, `examples/templates/cash-rebalance/catalysts.json`, `examples/templates/cash-rebalance/scenario.json`, `examples/templates/etf-core/holdings.csv`, `examples/templates/etf-core/config.json`, `examples/templates/etf-core/catalysts.json`, `examples/templates/etf-core/scenario.json`, `examples/templates/leveraged-sleeve/holdings.csv`, `examples/templates/leveraged-sleeve/config.json`, `examples/templates/leveraged-sleeve/catalysts.json`, `examples/templates/leveraged-sleeve/scenario.json` | 3190 |
| [case_study_comparison.json](case_study_comparison.json) | manifested | `index.json`, `generated JSON artifacts`, `examples/fixtures/holdings.csv`, `examples/fixtures/config.json`, `examples/fixtures/catalysts.json`, `examples/fixtures/scenario.json`, `examples/fixtures/history/*.json`, `examples/templates/cash-rebalance/holdings.csv`, `examples/templates/cash-rebalance/config.json`, `examples/templates/cash-rebalance/catalysts.json`, `examples/templates/cash-rebalance/scenario.json`, `examples/templates/etf-core/holdings.csv`, `examples/templates/etf-core/config.json`, `examples/templates/etf-core/catalysts.json`, `examples/templates/etf-core/scenario.json`, `examples/templates/leveraged-sleeve/holdings.csv`, `examples/templates/leveraged-sleeve/config.json`, `examples/templates/leveraged-sleeve/catalysts.json`, `examples/templates/leveraged-sleeve/scenario.json` | 8586 |

## Source Fixture Sets

| Case | Fixture directory | Fixture files |
| --- | --- | --- |
| base-demo | `examples/fixtures` | `holdings.csv`, `config.json`, `catalysts.json`, `scenario.json`, `history/*.json` |
| cash-rebalance | `examples/templates/cash-rebalance` | `holdings.csv`, `config.json`, `catalysts.json`, `scenario.json` |
| etf-core | `examples/templates/etf-core` | `holdings.csv`, `config.json`, `catalysts.json`, `scenario.json` |
| leveraged-sleeve | `examples/templates/leveraged-sleeve` | `holdings.csv`, `config.json`, `catalysts.json`, `scenario.json` |
