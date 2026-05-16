# Portfolio Risk Compass Guided Walkthrough

Deterministic walkthrough for the base demo and bundled portfolio templates.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.

- As of: 2026-05-15
- Case count: 4

## Guided Steps

1. Open the static dashboard: open `dashboard.html`. Start with the no-JavaScript overview before inspecting source files.
2. Compare template risk postures: open `walkthrough.md`. Use the case table to compare allocation, guardrail, stress, catalyst, and watchlist signals.
3. Trace every number to a file: open `index.json`. Use the manifest and linked Markdown reports to verify each generated artifact.

## Case Gallery

| Case | Focus | Total value | Guardrails | Stress delta | Catalysts | Watchlist | Start here |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| Base Demo | Repository demo fixture set. | 7350.00 | FAIL | -7.3197 | 3 | 8 | [exposure_report.md](exposure_report.md) |
| Cash Rebalance | High-cash portfolio staged for tax-aware deployment after drift or market pullback triggers. | 61510.60 | WARN | -2.1168 | 3 | 13 | [templates/cash-rebalance/exposure_report.md](templates/cash-rebalance/exposure_report.md) |
| ETF Core | Diversified stock, bond, and Treasury-bill core allocation with global equity and duration review points. | 62712.00 | WARN | -5.9837 | 3 | 12 | [templates/etf-core/exposure_report.md](templates/etf-core/exposure_report.md) |
| Leveraged Sleeve | Core equity book with a capped leveraged growth sleeve, liquidity buffer, and tighter review cadence. | 47307.25 | WARN | -8.0097 | 3 | 13 | [templates/leveraged-sleeve/exposure_report.md](templates/leveraged-sleeve/exposure_report.md) |

## Inspection Path

### Base Demo

- Exposure: [exposure_report.md](exposure_report.md)
- Guardrails: [guardrails.md](guardrails.md)
- Stress: [stress.md](stress.md)
- Catalysts: [catalysts.md](catalysts.md)
- Rebalance review watchlist: [rebalance_watchlist.md](rebalance_watchlist.md)

### Cash Rebalance

- Exposure: [templates/cash-rebalance/exposure_report.md](templates/cash-rebalance/exposure_report.md)
- Guardrails: [templates/cash-rebalance/guardrails.md](templates/cash-rebalance/guardrails.md)
- Stress: [templates/cash-rebalance/stress.md](templates/cash-rebalance/stress.md)
- Catalysts: [templates/cash-rebalance/catalysts.md](templates/cash-rebalance/catalysts.md)
- Rebalance review watchlist: [templates/cash-rebalance/rebalance_watchlist.md](templates/cash-rebalance/rebalance_watchlist.md)

### ETF Core

- Exposure: [templates/etf-core/exposure_report.md](templates/etf-core/exposure_report.md)
- Guardrails: [templates/etf-core/guardrails.md](templates/etf-core/guardrails.md)
- Stress: [templates/etf-core/stress.md](templates/etf-core/stress.md)
- Catalysts: [templates/etf-core/catalysts.md](templates/etf-core/catalysts.md)
- Rebalance review watchlist: [templates/etf-core/rebalance_watchlist.md](templates/etf-core/rebalance_watchlist.md)

### Leveraged Sleeve

- Exposure: [templates/leveraged-sleeve/exposure_report.md](templates/leveraged-sleeve/exposure_report.md)
- Guardrails: [templates/leveraged-sleeve/guardrails.md](templates/leveraged-sleeve/guardrails.md)
- Stress: [templates/leveraged-sleeve/stress.md](templates/leveraged-sleeve/stress.md)
- Catalysts: [templates/leveraged-sleeve/catalysts.md](templates/leveraged-sleeve/catalysts.md)
- Rebalance review watchlist: [templates/leveraged-sleeve/rebalance_watchlist.md](templates/leveraged-sleeve/rebalance_watchlist.md)

