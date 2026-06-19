# Portfolio Risk Compass Public Review Walkthrough

Deterministic static dashboard walkthrough and evidence packet for public reviewers.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.
Public safety notice: Audit receipt only; not investment advice, trading guidance, live market data, broker connectivity, account access, order entry, or trade execution.

## Boundaries

- No live data: none; all values come from static CSV/JSON fixtures or generated local artifacts
- No broker: none; no account access, order entry, execution, or broker connectivity
- No advice: none; artifact is a review walkthrough, not investment advice or trading guidance

## Rerun Commands

1. Regenerate the deterministic bundle: `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`. Evidence: `index.json`.
2. Render the static dashboard: `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`. Evidence: `dashboard.html`, `dashboard_preview.md`, `dashboard_snippet.html`.
3. Refresh review evidence: `PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence`. Evidence: `reviewer_evidence.md`, `reviewer_evidence.json`.
4. Refresh scenario evidence receipt: `PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt`. Evidence: `scenario_evidence_receipt.md`, `scenario_evidence_receipt.json`.
5. Refresh this public packet: `PYTHONPATH=src python -m portfolio_risk_compass public-review`. Evidence: `public_review_walkthrough.md`, `public_review_walkthrough.json`.

## Dashboard Evidence Hashes

| Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [dashboard.html](dashboard.html) | present | html | 18376 | `cfe55b4e94a5066b369fd76cc0838022a71c9f0f3370eca1a70499bf84c087ac` |
| [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| [dashboard_snippet.html](dashboard_snippet.html) | present | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| [gallery.md](gallery.md) | present | markdown | 2189 | `d7c5b1261c32106afe47f75bda871ff629f9779d551cb6e989f2c9c28f21465e` |
| [walkthrough.md](walkthrough.md) | present | markdown | 3568 | `85169963cfbefa4ad317fd458e9109dbbca23050acd4d4230eeb6fec9c89a932` |
| [walkthrough.json](walkthrough.json) | present | json | 7657 | `a7580a81bf9c21dc96e3a52ce884e53b2603390a1495eb74823b57205ece4b1a` |
| [reviewer_evidence.md](reviewer_evidence.md) | present | markdown | 3455 | `900a178c479c4708470bc4b3a5bc814216927b9b5ab099591e5e979f16f93127` |
| [reviewer_evidence.json](reviewer_evidence.json) | present | json | 5754 | `572e774cb9c970c69974340704d64be506a172a8f928ab8213686541f3c26707` |
| [scenario_evidence_receipt.md](scenario_evidence_receipt.md) | present | markdown | 8257 | `c5194f3421474d88032b5f5de66deb067313ab438e72581a5283d2cc25db3b18` |
| [scenario_evidence_receipt.json](scenario_evidence_receipt.json) | present | json | 10582 | `659e028eccbe9ae59d2d8817277b91030957699fa3b2d4b8a6cbcbf06394a296` |
| [case_study_comparison.md](case_study_comparison.md) | present | markdown | 3190 | `1b8188a950bed8d61d767e9f48b5597f2482eb5e8a82458f87ba89853c82c781` |
| [case_study_comparison.json](case_study_comparison.json) | present | json | 8586 | `8e57db407c4270d33e299b35c89f152473cfe6fa87ea4c11ee7c750bc152f0f8` |
| [index.json](index.json) | present | json | 18249 | `7dfc4a6b6271ed35b95ecf57ba1af98be23159e10acb58ae5d8d60805de91eb4` |

## Fixture Input Hashes

| Case | Path | Status | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| base-demo | [examples/fixtures/holdings.csv](examples/fixtures/holdings.csv) | present | 423 | `c93c9c4b852d80e5b54cdd952c7f2d63ccebbe1854c8161130d94ba134021a7c` |
| base-demo | [examples/fixtures/config.json](examples/fixtures/config.json) | present | 440 | `f61c58f945f8028f7090076515b3789aeb3fdaae0282a7319d81d7cea355befc` |
| base-demo | [examples/fixtures/catalysts.json](examples/fixtures/catalysts.json) | present | 827 | `d37900eab554ffecf6c0c427a760aa667c24501d4f76f39c4742e05eb65cef5f` |
| base-demo | [examples/fixtures/scenario.json](examples/fixtures/scenario.json) | present | 497 | `82284bfd0be70c3053b6a694da15c2ac106bc9607d79103ede0ca023996a8d46` |
| base-demo | [examples/fixtures/history/*.json](examples/fixtures/history/%2A.json) | present | 3379 | `e945232aa8712dad53477c4a77e6bc3929e998a24652fbb813d95cfd92f41086` |
| cash-rebalance | [examples/templates/cash-rebalance/holdings.csv](examples/templates/cash-rebalance/holdings.csv) | present | 555 | `32b87398502c5db37fde3951930b041018e7e8cc83850575984b952a31a2ba84` |
| cash-rebalance | [examples/templates/cash-rebalance/config.json](examples/templates/cash-rebalance/config.json) | present | 600 | `6bf02470ead55e402896e585acb2e1d4f2a2ae8d611e7453d06d56776fbddbc7` |
| cash-rebalance | [examples/templates/cash-rebalance/catalysts.json](examples/templates/cash-rebalance/catalysts.json) | present | 860 | `50bfcceef469878494317c9cf67be7e27e400e511423ab37aa4ffbee1613573e` |
| cash-rebalance | [examples/templates/cash-rebalance/scenario.json](examples/templates/cash-rebalance/scenario.json) | present | 532 | `dec52116f05a459d230eafa07d43ca9a9f4fdfe361dd934f73f231d4cf29d7ca` |
| etf-core | [examples/templates/etf-core/holdings.csv](examples/templates/etf-core/holdings.csv) | present | 515 | `8d9ce7d73d3c5c382763097e2d306908c09395b5cfd1fe8758e24e570ec2e59f` |
| etf-core | [examples/templates/etf-core/config.json](examples/templates/etf-core/config.json) | present | 518 | `853e9caa5549fa60b7691224466f929b4efe84cdee9a49a0838b4b9ce6179cf9` |
| etf-core | [examples/templates/etf-core/catalysts.json](examples/templates/etf-core/catalysts.json) | present | 844 | `cd0b5b9d950afce4fcb587f09570cf81f4f82fb262de32736de4bfffa2197ab0` |
| etf-core | [examples/templates/etf-core/scenario.json](examples/templates/etf-core/scenario.json) | present | 507 | `09c6898eff9cfb219d53a40e73748a6275bb1c4d6e2a02bd52d276afd2f1096c` |
| leveraged-sleeve | [examples/templates/leveraged-sleeve/holdings.csv](examples/templates/leveraged-sleeve/holdings.csv) | present | 516 | `778d7fa9d35f5384e28f504904742895281746a256e252341c6314e72c7ec5a9` |
| leveraged-sleeve | [examples/templates/leveraged-sleeve/config.json](examples/templates/leveraged-sleeve/config.json) | present | 595 | `79d503f25f08f4bc670d69b40920155f24f8dfc038a30bb7cfac7dd7c6acc05a` |
| leveraged-sleeve | [examples/templates/leveraged-sleeve/catalysts.json](examples/templates/leveraged-sleeve/catalysts.json) | present | 861 | `2bc47ce43d39d1b4bd7903636e1e37f0e4a7e3867a9957caac14310c6cb70ff1` |
| leveraged-sleeve | [examples/templates/leveraged-sleeve/scenario.json](examples/templates/leveraged-sleeve/scenario.json) | present | 531 | `adc0cefc219892a4b887ae91e4dc18a0db12b0bf11f753c0e625a4b3af8e67b8` |
