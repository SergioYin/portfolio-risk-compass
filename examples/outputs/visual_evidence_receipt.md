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
| static_dashboard | [dashboard.html](dashboard.html) | present | html | 18102 | `f716c91351ca9e645f80476ce8c1761d0b3d802b4fae41ea8e2a99bb24bb393f` |
| dashboard_preview | [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| dashboard_snippet | [dashboard_snippet.html](dashboard_snippet.html) | present | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | present | markdown | 6952 | `6222fd4e6b4404ac7cbc14bbf927c51c84230bdf7bb39635d860a1355c66cd60` |
| public_review_packet | [public_review_walkthrough.json](public_review_walkthrough.json) | present | json | 9032 | `a60e13a73f2f0a16fe188b0ed4a8c6d375fa99e3d150628028bf1f2cf240fbef` |
| dashboard_screenshot_guide | [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | present | json | 3937 | `50453e60f2ab429e3ab99dbf8fdbadd03409d1bed1af6c32e794e8becfbfc321` |
| scenario_evidence_receipt | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | present | json | 10582 | `ce3a73a08bdd6e28d003f0f7edf5b718deb66b9fc7b7068371a84ec669210d35` |
| reviewer_evidence_export | [reviewer_evidence.json](reviewer_evidence.json) | present | json | 5754 | `2b0d5c7dd6c308591ce969f7b51a7f430bd4f0262d19c596b89e09ca9463de7a` |

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
