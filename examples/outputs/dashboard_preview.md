# Dashboard Preview

[Open the static dashboard](dashboard.html)

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.

| Panel | What it shows | Source artifact |
| --- | --- | --- |
| Summary | Total value, holding count, concentration limit, risk boundary | `exposure_report.json`, `guardrails.json` |
| Exposure | Asset class, sector, region, and currency allocation tables | `exposure_report.json` |
| Concentration | Holdings above the configured concentration limit | `exposure_report.json` |
| Risk Boundaries | PASS/WARN/FAIL policy checks with actuals and limits | `guardrails.json` |
| Stress | Scenario value, shock impacts, and value delta | `stress.json` |
| Catalysts | Date-ordered thesis event checklist | `catalysts.json` |
| Bundle | Generated artifact inventory | `index.json` |
| Reviewer evidence | Dashboard and case-study artifact fixture trace | `reviewer_evidence.md` |

## Featured Files

| File | Format | Bytes |
| --- | --- | ---: |
| `exposure_report.md` | markdown | 1247 |
| `catalysts.md` | markdown | 711 |
| `guardrails.md` | markdown | 1227 |
| `stress.md` | markdown | 1024 |
| `rebalance_watchlist.md` | markdown | 2386 |
