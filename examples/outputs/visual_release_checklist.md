# Portfolio Risk Compass Visual Release Checklist

Schema: `portfolio-risk-compass-visual-release-checklist.v1`
Root: `examples/outputs`
Audit schema: `portfolio-risk-compass-visual-capture-audit.v1`
Scope: Deterministic release-owner checklist for static dashboard/demo visual capture readiness. It reads local artifact metadata only.

## Boundaries

- manual review: records readiness checks only; capture and release ownership remain human-reviewed
- no advice: public finance-research artifact audit only; not investment advice
- no broker: does not connect to brokers or accounts
- no file contents: does not embed artifact contents; records relative paths, byte counts, and SHA-256 hashes only
- no live data: does not fetch or require live market data
- no orders: does not place, route, stage, or recommend orders
- no position sizing: does not calculate trade quantities or position sizing
- no private data: does not require, inspect, or emit private account data
- no recommendations: does not recommend portfolio actions
- scope: release-owner readiness checklist for static dashboard/demo visual evidence

## Summary

- Items: 10
- Required: 6
- Required missing: 0
- Recommended missing: 0
- Optional missing: 1
- Ready for release-owner review: true
- Audit complete: false

## Checklist

| Key | Status | Level | Evidence | Missing | Remediation |
| --- | --- | --- | --- | --- | --- |
| static_dashboard_present | pass | required | [dashboard.html](dashboard.html) | none | none |
| public_review_present | pass | required | [public_review_walkthrough.md](public_review_walkthrough.md), [public_review_walkthrough.json](public_review_walkthrough.json) | none | none |
| screenshot_guide_present | pass | required | [dashboard_screenshot_guide.md](dashboard_screenshot_guide.md), [dashboard_screenshot_guide.json](dashboard_screenshot_guide.json) | none | none |
| visual_evidence_present | pass | required | [visual_evidence_receipt.md](visual_evidence_receipt.md), [visual_evidence_receipt.json](visual_evidence_receipt.json) | none | none |
| demo_capture_present | pass | required | [demo_capture_receipt.md](demo_capture_receipt.md), [demo_capture_receipt.json](demo_capture_receipt.json) | none | none |
| visual_capture_audit_present | pass | required | [visual_capture_audit.md](visual_capture_audit.md), [visual_capture_audit.json](visual_capture_audit.json) | none | none |
| visual_capture_compare_present | pass | recommended | [visual_capture_compare.md](visual_capture_compare.md), [visual_capture_compare.json](visual_capture_compare.json) | none | none |
| release_manifest_present | pass | recommended | [release_manifest.md](release_manifest.md), [release_manifest.json](release_manifest.json) | none | none |
| docs_export_present | pass | recommended | [docs_export.md](docs_export.md) | none | none |
| dashboard_capture_image_present | missing | optional |  | [screenshots/dashboard-public-review-1365x900.png](screenshots/dashboard-public-review-1365x900.png) | Capture with the command recorded in dashboard_screenshot_guide.md when screenshot evidence is required. |

## Owner Steps

- Open dashboard.html from the generated outputs directory.
- Run or inspect dashboard_screenshot_guide.md before capture.
- Confirm public-review, scenario, reviewer, visual, and demo capture receipts are present.
- Compare visual_capture_audit.json against the prior release audit when available.
- Regenerate release_manifest and docs_export after checklist outputs are refreshed.
- Run the repository selfcheck and privacy scan before publishing artifacts.

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass public-review`
- `PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format json --output examples/outputs/visual_capture_audit.json`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format markdown --output examples/outputs/visual_capture_audit.md`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-compare --before examples/outputs/visual_capture_audit.json --after examples/outputs/visual_capture_audit.json --format json --output examples/outputs/visual_capture_compare.json`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-capture-compare --before examples/outputs/visual_capture_audit.json --after examples/outputs/visual_capture_audit.json --format markdown --output examples/outputs/visual_capture_compare.md`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-release-checklist --root examples/outputs --format json --output examples/outputs/visual_release_checklist.json`
- `PYTHONPATH=src python -m portfolio_risk_compass visual-release-checklist --root examples/outputs --format markdown --output examples/outputs/visual_release_checklist.md`
- `PYTHONPATH=src python -m portfolio_risk_compass release-manifest`
- `PYTHONPATH=src python -m portfolio_risk_compass docs-export`
