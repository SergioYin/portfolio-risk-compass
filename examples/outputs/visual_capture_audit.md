# Portfolio Risk Compass Visual Capture Audit

Schema: `portfolio-risk-compass-visual-capture-audit.v1`
Root: `examples/outputs`
Scope: Deterministic audit of existing static visual/demo evidence artifacts. The audit reads local files only and identifies capture gaps.

## Boundaries

- no advice: public finance-research artifact audit only; not investment advice
- no broker: does not connect to brokers or accounts
- no file contents: does not embed artifact contents; records relative paths, byte counts, and SHA-256 hashes only
- no live data: does not fetch or require live market data
- no orders: does not place, route, stage, or recommend orders
- no position sizing: does not calculate trade quantities or position sizing
- no recommendations: does not recommend portfolio actions

## Summary

- Checked: 19
- Present: 18
- Missing: 1
- Complete: false
- Recommended capture items: 1

## Checked Artifacts

| Role | Path | Present | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| static_dashboard | [dashboard.html](dashboard.html) | true | 18376 | `cfe55b4e94a5066b369fd76cc0838022a71c9f0f3370eca1a70499bf84c087ac` |
| dashboard_preview | [dashboard_preview.md](dashboard_preview.md) | true | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| dashboard_snippet | [dashboard_snippet.html](dashboard_snippet.html) | true | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | true | 6952 | `5d29db5a1b71e300da6a92feeeb31c2f45a504722562625bf28312335aaaa740` |
| public_review_packet | [public_review_walkthrough.json](public_review_walkthrough.json) | true | 9032 | `0e7c364980c094d48ed7c17c8fd272518378f4d5792ee985c5e073aa1ea7c28e` |
| dashboard_screenshot_guide | [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md) | true | 3047 | `70c91400968a3d052556cba97e5ea0557f9074184c28787f48ddab800b1026cf` |
| dashboard_screenshot_guide_packet | [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | true | 3937 | `69969afc2e074954e562d414ca4552c869e8187229399c107ad025cb83b88ee3` |
| visual_evidence_receipt | [visual_evidence_receipt.md](visual_evidence_receipt.md) | true | 3950 | `277ea19fd12360129b56c0f3e888cf1787f84fe98c231727bd1ca631d8e027d8` |
| visual_evidence_receipt_packet | [visual_evidence_receipt.json](visual_evidence_receipt.json) | true | 5519 | `a9f86728802a7a16f721e2b6c659ab82579beec9ab93e5de250604c2e630f326` |
| demo_capture_receipt | [demo_capture_receipt.md](demo_capture_receipt.md) | true | 5971 | `357d3095f3fe1d4553d0319eecf6ac7ccf72b15af2e2412d94b147942bc497e8` |
| demo_capture_receipt_packet | [demo_capture_receipt.json](demo_capture_receipt.json) | true | 8631 | `c4a4d793d1813724c138639780eefc6afb2d8432b3c20f59a14e4257005e31c7` |
| scenario_evidence_receipt | [scenario_evidence_receipt.md](scenario_evidence_receipt.md) | true | 8257 | `c5194f3421474d88032b5f5de66deb067313ab438e72581a5283d2cc25db3b18` |
| scenario_evidence_receipt_packet | [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | true | 10582 | `659e028eccbe9ae59d2d8817277b91030957699fa3b2d4b8a6cbcbf06394a296` |
| reviewer_evidence | [reviewer_evidence.md](reviewer_evidence.md) | true | 3455 | `900a178c479c4708470bc4b3a5bc814216927b9b5ab099591e5e979f16f93127` |
| reviewer_evidence_packet | [reviewer_evidence.json](reviewer_evidence.json) | true | 5754 | `572e774cb9c970c69974340704d64be506a172a8f928ab8213686541f3c26707` |
| gallery | [gallery.md](gallery.md) | true | 2189 | `d7c5b1261c32106afe47f75bda871ff629f9779d551cb6e989f2c9c28f21465e` |
| public_gallery | [gallery.html](gallery.html) | true | 6744 | `e3220cc695d6761bee9db1cac97ae5aec9fae612a0a6ee2e402d2e4be3209d6e` |
| demo_manifest | [index.json](index.json) | true | 18249 | `7dfc4a6b6271ed35b95ecf57ba1af98be23159e10acb58ae5d8d60805de91eb4` |
| dashboard_capture_image | [screenshots/dashboard-public-review-1365x900.png](screenshots/dashboard-public-review-1365x900.png) | false | n/a | n/a |

## Recommended Capture Items

| Path | Role | Reason | Regenerate |
| --- | --- | --- | --- |
| [screenshots/dashboard-public-review-1365x900.png](screenshots/dashboard-public-review-1365x900.png) | dashboard_capture_image | missing static visual/demo evidence artifact | Capture with the command recorded in dashboard_screenshot_guide.md. |

## Source Artifacts

| Path | Present | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [index.json](index.json) | true | 18249 | `7dfc4a6b6271ed35b95ecf57ba1af98be23159e10acb58ae5d8d60805de91eb4` |
| [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md) | true | 3047 | `70c91400968a3d052556cba97e5ea0557f9074184c28787f48ddab800b1026cf` |
| [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | true | 3937 | `69969afc2e074954e562d414ca4552c869e8187229399c107ad025cb83b88ee3` |
| [visual_evidence_receipt.json](visual_evidence_receipt.json) | true | 5519 | `a9f86728802a7a16f721e2b6c659ab82579beec9ab93e5de250604c2e630f326` |
| [demo_capture_receipt.json](demo_capture_receipt.json) | true | 8631 | `c4a4d793d1813724c138639780eefc6afb2d8432b3c20f59a14e4257005e31c7` |
| [public_review_walkthrough.json](public_review_walkthrough.json) | true | 9032 | `0e7c364980c094d48ed7c17c8fd272518378f4d5792ee985c5e073aa1ea7c28e` |

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence`
- `PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass public-review`
- `PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format json --output examples/outputs/visual_capture_audit.json`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format markdown --output examples/outputs/visual_capture_audit.md`
