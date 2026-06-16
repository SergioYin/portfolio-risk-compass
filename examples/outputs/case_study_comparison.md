# Portfolio Risk Compass Case-Study Comparison

Deterministic comparison of the base demo and bundled template outputs.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.

- As of: 2026-05-15
- Case count: 4
- Manifest coverage: complete

## Comparison Table

| Case | Focus | Total value | Cash % | Equity % | Leveraged equity % | Guardrails | Stress delta % | Watchlist | Catalysts |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Base Demo | Repository demo fixture set. | 7350.00 | 13.6054 | 66.6667 | 0.0000 | FAIL | -7.3197 | 8 | 3 |
| ETF Core | Diversified stock, bond, and Treasury-bill core allocation with global equity and duration review points. | 62712.00 | 8.0064 | 66.4514 | 0.0000 | WARN | -5.9837 | 12 | 3 |
| Leveraged Sleeve | Core equity book with a capped leveraged growth sleeve, liquidity buffer, and tighter review cadence. | 47307.25 | 5.2846 | 68.1138 | 12.6165 | WARN | -8.0097 | 13 | 3 |
| Cash Rebalance | High-cash portfolio staged for tax-aware deployment after drift or market pullback triggers. | 61510.60 | 39.4657 | 40.0728 | 0.0000 | WARN | -2.1168 | 13 | 3 |

## Highlights

- Highest cash allocation: Cash Rebalance (39.4657)
- Largest stress drawdown: Leveraged Sleeve (-8.0097)
- Most watchlist items: Leveraged Sleeve (13)

## Source Artifacts

### Base Demo

- Exposure: [exposure_report.md](exposure_report.md)
- Guardrails: [guardrails.md](guardrails.md)
- Stress: [stress.md](stress.md)
- Catalysts: [catalysts.md](catalysts.md)
- Rebalance review watchlist: [rebalance_watchlist.md](rebalance_watchlist.md)

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

### Cash Rebalance

- Exposure: [templates/cash-rebalance/exposure_report.md](templates/cash-rebalance/exposure_report.md)
- Guardrails: [templates/cash-rebalance/guardrails.md](templates/cash-rebalance/guardrails.md)
- Stress: [templates/cash-rebalance/stress.md](templates/cash-rebalance/stress.md)
- Catalysts: [templates/cash-rebalance/catalysts.md](templates/cash-rebalance/catalysts.md)
- Rebalance review watchlist: [templates/cash-rebalance/rebalance_watchlist.md](templates/cash-rebalance/rebalance_watchlist.md)

