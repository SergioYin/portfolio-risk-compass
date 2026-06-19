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
| 3 | screenshot_guide | [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md) | exact dashboard screenshot command, capture viewport, screenshot hash receipt path |
| 4 | scenario_evidence | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | scenario fixture hashes, stress and guardrail artifact hashes, prohibited capability list |
| 5 | reviewer_evidence | [reviewer_evidence.json](reviewer_evidence.json) | reviewer export path, fixture lineage, generated artifact coverage |

## Artifact Hashes

| Role | Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| static_dashboard | [dashboard.html](dashboard.html) | present | html | 18376 | `cfe55b4e94a5066b369fd76cc0838022a71c9f0f3370eca1a70499bf84c087ac` |
| dashboard_preview | [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| dashboard_snippet | [dashboard_snippet.html](dashboard_snippet.html) | present | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | present | markdown | 6952 | `5d29db5a1b71e300da6a92feeeb31c2f45a504722562625bf28312335aaaa740` |
| public_review_packet | [public_review_walkthrough.json](public_review_walkthrough.json) | present | json | 9032 | `0e7c364980c094d48ed7c17c8fd272518378f4d5792ee985c5e073aa1ea7c28e` |
| dashboard_screenshot_guide | [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | present | json | 3937 | `69969afc2e074954e562d414ca4552c869e8187229399c107ad025cb83b88ee3` |
| scenario_evidence_receipt | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | present | json | 10582 | `659e028eccbe9ae59d2d8817277b91030957699fa3b2d4b8a6cbcbf06394a296` |
| reviewer_evidence_export | [reviewer_evidence.json](reviewer_evidence.json) | present | json | 5754 | `572e774cb9c970c69974340704d64be506a172a8f928ab8213686541f3c26707` |

## Coverage

- Present: 8 of 8
- Complete: true
- Missing: none

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence`
- `PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass public-review`
- `PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`
