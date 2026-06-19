# Portfolio Risk Compass Demo Capture Receipt

Deterministic public demo capture receipt and evidence index for the static portfolio dashboard.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.
Public safety notice: Audit receipt only; not investment advice, trading guidance, live market data, broker connectivity, account access, order entry, or trade execution.
Review scope: Public-safe static demo capture receipt for generated local artifacts. It indexes dashboard screenshot/capture evidence and hashes existing review receipts without fetching data, connecting to brokers, sizing positions, placing orders, or providing recommendations or advice.

## Boundaries

- No live data: none; all values come from static CSV/JSON fixtures or generated local artifacts
- No broker: none; no account access, order entry, execution, or broker connectivity
- No advice: none; artifact is a review walkthrough, not investment advice or trading guidance
- No orders: none; no order entry, execution, or broker workflow is present
- No position sizing: none; output records evidence only and does not size positions
- No recommendations: none; output is an evidence index, not portfolio recommendations
- Prohibited: broker connection
- Prohibited: live market data
- Prohibited: account access
- Prohibited: order entry
- Prohibited: trade execution
- Prohibited: position sizing
- Prohibited: portfolio recommendations
- Prohibited: investment advice

## Capture Profile

- Browser: `chromium`
- Viewport: `1365x900`
- Full page: `false`
- Input URL: `file://$PWD/examples/outputs/dashboard.html`
- Output path: `examples/outputs/screenshots/dashboard-public-review-1365x900.png`

## Evidence Index

| Label | Artifacts | Verifies |
| --- | --- | --- |
| capture_instructions | [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md), [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | exact dashboard capture command, viewport and browser profile, screenshot output path |
| visual_route | [visual_evidence_receipt.md](visual_evidence_receipt.md), [visual_evidence_receipt.json](visual_evidence_receipt.json) | static dashboard route, public review link, scenario and reviewer evidence links |
| public_review | [public_review_walkthrough.md](public_review_walkthrough.md), [public_review_walkthrough.json](public_review_walkthrough.json) | rerun commands, fixture hashes, public-safe review boundaries |
| scenario_receipt | [scenario_evidence_receipt.md](scenario_evidence_receipt.md), [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | static scenario fixture hashes, stress and guardrail artifact hashes, prohibited capability list |
| reviewer_evidence | [reviewer_evidence.md](reviewer_evidence.md), [reviewer_evidence.json](reviewer_evidence.json) | fixture lineage, generated artifact coverage, reviewer export path |

## Artifact Hashes

| Role | Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| static_dashboard_route | [dashboard.html](dashboard.html) | present | html | 18376 | `cfe55b4e94a5066b369fd76cc0838022a71c9f0f3370eca1a70499bf84c087ac` |
| dashboard_capture_slot | [screenshots/dashboard-public-review-1365x900.png](screenshots/dashboard-public-review-1365x900.png) | missing | png | n/a | `n/a` |
| dashboard_screenshot_guide | [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md) | present | markdown | 3047 | `70c91400968a3d052556cba97e5ea0557f9074184c28787f48ddab800b1026cf` |
| dashboard_screenshot_guide_packet | [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | present | json | 3937 | `69969afc2e074954e562d414ca4552c869e8187229399c107ad025cb83b88ee3` |
| visual_evidence_receipt | [visual_evidence_receipt.md](visual_evidence_receipt.md) | present | markdown | 3950 | `277ea19fd12360129b56c0f3e888cf1787f84fe98c231727bd1ca631d8e027d8` |
| visual_evidence_receipt_packet | [visual_evidence_receipt.json](visual_evidence_receipt.json) | present | json | 5519 | `a9f86728802a7a16f721e2b6c659ab82579beec9ab93e5de250604c2e630f326` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | present | markdown | 6952 | `5d29db5a1b71e300da6a92feeeb31c2f45a504722562625bf28312335aaaa740` |
| public_review_walkthrough_packet | [public_review_walkthrough.json](public_review_walkthrough.json) | present | json | 9032 | `0e7c364980c094d48ed7c17c8fd272518378f4d5792ee985c5e073aa1ea7c28e` |
| scenario_evidence_receipt | [scenario_evidence_receipt.md](scenario_evidence_receipt.md) | present | markdown | 8257 | `c5194f3421474d88032b5f5de66deb067313ab438e72581a5283d2cc25db3b18` |
| scenario_evidence_receipt_packet | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | present | json | 10582 | `659e028eccbe9ae59d2d8817277b91030957699fa3b2d4b8a6cbcbf06394a296` |
| reviewer_evidence | [reviewer_evidence.md](reviewer_evidence.md) | present | markdown | 3455 | `900a178c479c4708470bc4b3a5bc814216927b9b5ab099591e5e979f16f93127` |
| reviewer_evidence_packet | [reviewer_evidence.json](reviewer_evidence.json) | present | json | 5754 | `572e774cb9c970c69974340704d64be506a172a8f928ab8213686541f3c26707` |
| dashboard_preview | [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |

## Coverage

- Present: 12 of 13
- Complete: false
- Missing: `screenshots/dashboard-public-review-1365x900.png`

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt`
