# Portfolio Guardrail Review

- Snapshot date: 2026-05-15
- Last review date: 2026-05-01
- Overall status: FAIL

| Status | Check | Actual | Limit | Message |
| --- | --- | ---: | ---: | --- |
| PASS | max_position_pct | 25.8503 | 35.0000 | AAPL is 25.8503% of portfolio. |
| PASS | max_position_pct | 19.7279 | 35.0000 | BND is 19.7279% of portfolio. |
| PASS | max_position_pct | 13.6054 | 35.0000 | CASH is 13.6054% of portfolio. |
| PASS | max_position_pct | 28.5714 | 35.0000 | MSFT is 28.5714% of portfolio. |
| PASS | max_position_pct | 12.2449 | 35.0000 | VXUS is 12.2449% of portfolio. |
| PASS | max_sector_pct | 13.6054 | 50.0000 | Cash sector is 13.6054% of portfolio. |
| PASS | max_sector_pct | 12.2449 | 50.0000 | Diversified sector is 12.2449% of portfolio. |
| PASS | max_sector_pct | 19.7279 | 50.0000 | Government Bonds sector is 19.7279% of portfolio. |
| FAIL | max_sector_pct | 54.4218 | 50.0000 | Technology sector is 54.4218% of portfolio. |
| PASS | min_cash_pct | 13.6054 | 5.0000 | Cash is 13.6054% of portfolio. |
| PASS | max_leverage_multiple | 1.0000 | 1.2500 | Gross exposure is 1.0000x net value. |
| PASS | required_review_cadence_days | 14 | 30 | Last review was 14 day(s) before snapshot. |
