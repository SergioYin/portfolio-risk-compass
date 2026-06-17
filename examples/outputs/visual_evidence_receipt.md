# Portfolio Risk Compass Visual Evidence Receipt

Deterministic route tying the static dashboard to public-review, scenario, and reviewer evidence artifacts.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.
Public safety notice: Audit receipt only; not investment advice, trading guidance, live market data, broker connectivity, account access, order entry, or trade execution.
Review scope: Visual evidence route for static local dashboard artifacts only. The receipt does not fetch data, connect to brokers, or provide advice.

## Boundaries

- No live data: none; all values come from static CSV/JSON fixtures or generated local artifacts
- No broker: none; no account access, order entry, execution, or broker connectivity
- No advice: none; artifact is a review walkthrough, not investment advice or trading guidance

## Route

| Step | Label | Artifact | Verifies |
| ---: | --- | --- | --- |
| 1 | dashboard | [dashboard.html](dashboard.html) | static visual summary, no JavaScript dashboard export, broker-free review boundary |
| 2 | public_review | [public_review_walkthrough.md](public_review_walkthrough.md) | public reviewer rerun path, no-live-data boundary, no-advice boundary |
| 3 | scenario_evidence | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | scenario fixture hashes, stress and guardrail artifact hashes, prohibited capability list |
| 4 | reviewer_evidence | [reviewer_evidence.json](reviewer_evidence.json) | reviewer export path, fixture lineage, generated artifact coverage |

## Artifact Hashes

| Role | Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| static_dashboard | [dashboard.html](dashboard.html) | present | html | 17770 | `236d5d8d14dc3e950716f7d62fa5b8c78629c8cb16a8b34148dbb6631f4c248e` |
| dashboard_preview | [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| dashboard_snippet | [dashboard_snippet.html](dashboard_snippet.html) | present | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | present | markdown | 6952 | `f205869c7ea480f6f13b971bdf3f2dc90cb507e44272e0f196d4205e76c57d4b` |
| public_review_packet | [public_review_walkthrough.json](public_review_walkthrough.json) | present | json | 9032 | `ac71404067c51d566fbe9b96bafa3fcc98c8063e971632ca1ed56ddc846ed461` |
| scenario_evidence_receipt | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | present | json | 10582 | `25e962b6c84d2ed6d21b1b15c4a2e1f9664a3eaf085154a34195e32a8dfcef3e` |
| reviewer_evidence_export | [reviewer_evidence.json](reviewer_evidence.json) | present | json | 5754 | `a96c4fe2f368c806d876b38b09666aa46d66bcee08683bbab7625889c971c561` |

## Coverage

- Present: 7 of 7
- Complete: true
- Missing: none

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence`
- `PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass public-review`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`
