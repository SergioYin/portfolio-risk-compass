# Portfolio Review Memo

Non-advice boundary: This memo is for human portfolio review and education only. It is not investment, tax, legal, accounting, or trading advice, and it does not recommend buying, selling, holding, position sizes, order types, account transfers, or timing.

## Source Artifacts

| Artifact | Path |
| --- | --- |
| exposure | exposure_report.json |
| guardrails | guardrails.json |
| stress | stress.json |
| catalysts | catalysts.json |
| history | history.json |
| watchlist | rebalance_watchlist.json |

## Executive Summary

- Portfolio value: 7350.00 USD
- Holdings: 5
- Guardrail status: FAIL
- Stress scenario: Risk-off rotation moved portfolio value -7.3197% (-538.00)
- Watchlist items: 8 (high 2, medium 2, low 4)
- Catalysts: 3 (overdue 1, today 1, upcoming 1)
- History total value change: 350.00 (5.0000%) across 3 snapshot(s)

## Exposure

| Group | Bucket | Market value | Portfolio % |
| --- | --- | ---: | ---: |
| asset_class | Equity | 4900.00 | 66.6667% |
| asset_class | Fixed Income | 1450.00 | 19.7279% |
| asset_class | Cash | 1000.00 | 13.6054% |
| sector | Technology | 4000.00 | 54.4218% |
| sector | Government Bonds | 1450.00 | 19.7279% |
| sector | Cash | 1000.00 | 13.6054% |
| sector | Diversified | 900.00 | 12.2449% |
| region | North America | 6450.00 | 87.7551% |
| region | Global ex-US | 900.00 | 12.2449% |
| currency | USD | 7350.00 | 100.0000% |

## Concentration

| Symbol | Market value | Portfolio % | Limit % |
| --- | ---: | ---: | ---: |
| MSFT | 2100.00 | 28.5714% | 25.0000% |
| AAPL | 1900.00 | 25.8503% | 25.0000% |

## Guardrails

| Status | Check | Scope | Actual | Limit | Message |
| --- | --- | --- | ---: | ---: | --- |
| PASS | max_position_pct | AAPL | 25.8503 | 35.0000 | AAPL is 25.8503% of portfolio. |
| PASS | max_position_pct | BND | 19.7279 | 35.0000 | BND is 19.7279% of portfolio. |
| PASS | max_position_pct | CASH | 13.6054 | 35.0000 | CASH is 13.6054% of portfolio. |
| PASS | max_position_pct | MSFT | 28.5714 | 35.0000 | MSFT is 28.5714% of portfolio. |
| PASS | max_position_pct | VXUS | 12.2449 | 35.0000 | VXUS is 12.2449% of portfolio. |
| PASS | max_sector_pct | Cash | 13.6054 | 50.0000 | Cash sector is 13.6054% of portfolio. |
| PASS | max_sector_pct | Diversified | 12.2449 | 50.0000 | Diversified sector is 12.2449% of portfolio. |
| PASS | max_sector_pct | Government Bonds | 19.7279 | 50.0000 | Government Bonds sector is 19.7279% of portfolio. |
| FAIL | max_sector_pct | Technology | 54.4218 | 50.0000 | Technology sector is 54.4218% of portfolio. |
| PASS | min_cash_pct | Cash | 13.6054 | 5.0000 | Cash is 13.6054% of portfolio. |
| PASS | max_leverage_multiple | portfolio | 1.0000 | 1.2500 | Gross exposure is 1.0000x net value. |
| PASS | required_review_cadence_days | portfolio | 14 | 30 | Last review was 14 day(s) before snapshot. |

## Stress

- Scenario: Risk-off rotation
- Base market value: 7350.00
- Stressed market value: 6812.00
- Market value delta: -538.00 (-7.3197%)

| Shock | Selector | Bucket | Price move % | Value delta |
| --- | --- | --- | ---: | ---: |
| Technology rerating | sector | Technology | -10.0000% | -400.00 |
| Apple idiosyncratic miss | symbol | AAPL | -5.0000% | -95.00 |
| Bond rally | asset_class | Fixed Income | 2.0000% | 29.00 |
| International equity drawdown | region | Global ex-US | -8.0000% | -72.00 |

## Rebalance Watchlist

Safety boundary: Educational portfolio review only. This watchlist does not recommend trades, order types, position quantities, account transfers, or timing. Use it to decide what deserves human review against your own policy.

| Severity | Scope type | Scope | Reason codes | Evidence summary |
| --- | --- | --- | --- | --- |
| high | holding | AAPL | CONCENTRATION_LIMIT, STRESS_DRAWDOWN | concentration 25.8503% vs limit 25.0000%; Risk-off rotation stress move -15.0000% |
| high | sector | Technology | GUARDRAIL_FAIL | max_sector_pct FAIL: actual 54.4218, limit 50.0000 |
| medium | holding | MSFT | CONCENTRATION_LIMIT, STRESS_DRAWDOWN | concentration 28.5714% vs limit 25.0000%; Risk-off rotation stress move -10.0000% |
| medium | holding | VXUS | STRESS_DRAWDOWN | Risk-off rotation stress move -8.0000% |
| low | asset_class | Cash | TARGET_DRIFT | drift 3.6054% vs target 10.0000% |
| low | asset_class | Equity | TARGET_DRIFT | drift -3.3333% vs target 70.0000% |
| low | asset_class | Fixed Income | TARGET_DRIFT | drift -0.2721% vs target 20.0000% |
| low | portfolio | portfolio | STRESS_PORTFOLIO_DRAWDOWN | Risk-off rotation portfolio stress -7.3197% |

## Catalysts

| Date | Symbol | Flag | Importance | Title | Action |
| --- | --- | --- | --- | --- | --- |
| 2026-05-12 | MSFT | overdue | high | Cloud segment investor update | Review Azure growth and margin commentary |
| 2026-05-15 | TSLA | today | critical | Robotaxi milestone review | Decide whether event risk still fits the position size |
| 2026-05-20 | AAPL | upcoming | medium | Developer conference product announcements | Check whether announcements support the services growth thesis |

## History

| Date | Snapshot | Total value | Change | Change % |
| --- | --- | ---: | ---: | ---: |
| 2026-05-13 | ledger-2026-05-13 | 7000.00 | 0.00 | 0.0000% |
| 2026-05-14 | ledger-2026-05-14 | 7250.00 | 250.00 | 3.5714% |
| 2026-05-15 | ledger-2026-05-15 | 7350.00 | 100.00 | 1.3793% |

## Assumptions

- The memo uses precomputed JSON artifacts and does not recalculate holdings, prices, classifications, guardrails, scenarios, catalysts, or history.
- Market values, prices, target allocations, and classification fields are assumed to be correct as captured in the exposure artifact.
- Stress results assume the named scenario 'Risk-off rotation' and its configured shock rules; they are not probability-weighted forecasts.
- Catalyst timing is evaluated relative to 2026-05-15.
- The rebalance watchlist identifies review subjects only and intentionally omits trade instructions.

## Human Review Checklist

- Confirm source artifacts were regenerated from the intended holdings, config, scenario, catalysts, and snapshot files.
- Review WARN and FAIL guardrails against the documented portfolio policy.
- Review high and medium watchlist items before considering any action outside this tool.
- Treat stress results as deterministic scenario math, not forecasts.
