# Portfolio Risk Compass Dashboard Screenshot Guide

Deterministic screenshot capture guide and receipt for the static public dashboard route.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.
Public safety notice: Audit receipt only; not investment advice, trading guidance, live market data, broker connectivity, account access, order entry, or trade execution.
Review scope: Deterministic screenshot guide for the static public dashboard route. Public means generated demo/review artifacts that are suitable to share after review; it records local artifact hashes only and does not fetch live data, expose private account data, connect to brokers, place orders, or provide investment advice.

## Boundaries

- No live data: none; all values come from static CSV/JSON fixtures or generated local artifacts
- No broker: none; no account access, order entry, execution, or broker connectivity
- No advice: none; artifact is a review walkthrough, not investment advice or trading guidance

## Capture Profile

- Browser: `chromium`
- Viewport: `1365x900`
- Full page: `false`
- Input URL: `file://$PWD/examples/outputs/dashboard.html`
- Output path: `examples/outputs/screenshots/dashboard-public-review-1365x900.png`

## Exact Commands

1. Regenerate static review artifacts: `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
2. Render the public dashboard route: `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
3. Refresh the public review packet: `PYTHONPATH=src python -m portfolio_risk_compass public-review`
4. Prepare screenshot output directory: `mkdir -p examples/outputs/screenshots`
5. Capture the deterministic dashboard screenshot: `python -m playwright screenshot --browser chromium --viewport-size=1365,900 file://$PWD/examples/outputs/dashboard.html examples/outputs/screenshots/dashboard-public-review-1365x900.png`
6. Refresh this screenshot guide and visual receipt: `PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide && PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`

## Source Artifact Hashes

| Role | Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| static_dashboard_route | [dashboard.html](dashboard.html) | present | html | 18376 | `cfe55b4e94a5066b369fd76cc0838022a71c9f0f3370eca1a70499bf84c087ac` |
| public_review_walkthrough | [public_review_walkthrough.md](public_review_walkthrough.md) | present | markdown | 6952 | `5d29db5a1b71e300da6a92feeeb31c2f45a504722562625bf28312335aaaa740` |

## Screenshot Hashes

| Role | Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| dashboard_screenshot | [screenshots/dashboard-public-review-1365x900.png](screenshots/dashboard-public-review-1365x900.png) | missing | png | n/a | `n/a` |

## Coverage

- Present: 2 of 3
- Complete: false
- Missing: `screenshots/dashboard-public-review-1365x900.png`
