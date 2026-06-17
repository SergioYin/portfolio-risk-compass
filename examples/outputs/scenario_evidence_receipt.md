# Portfolio Risk Compass Scenario Evidence Receipt

Deterministic receipt for static scenario, guardrail, and dashboard review artifacts.

Safety boundary: Static portfolio review artifact only; not investment advice, trading guidance, live market data, or broker execution.
Public safety notice: Audit receipt only; not investment advice, trading guidance, live market data, broker connectivity, account access, order entry, or trade execution.
Review scope: Hashes static fixture inputs and generated local review artifacts. Missing sidecar artifacts are reported as missing and are not fetched from external services.

## Boundaries

- No broker connection
- No live market data
- No account access
- No order entry
- No trade execution
- No portfolio recommendations
- No investment advice

## Regeneration Commands

- `PYTHONPATH=src python -m portfolio_risk_compass demo-bundle`
- `PYTHONPATH=src python -m portfolio_risk_compass guardrails examples/fixtures/holdings.csv --config examples/fixtures/config.json --snapshot-date 2026-05-15 --json examples/outputs/guardrails.json --markdown examples/outputs/guardrails.md`
- `PYTHONPATH=src python -m portfolio_risk_compass stress examples/fixtures/holdings.csv examples/fixtures/scenario.json --json examples/outputs/stress.json --markdown examples/outputs/stress.md`
- `PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html`
- `PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt`

## Case: base-demo

- Fixture directory: `examples/fixtures`
- Output prefix: ``

### Fixture Hashes

| Path | Status | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [examples/fixtures/holdings.csv](examples/fixtures/holdings.csv) | present | 423 | `c93c9c4b852d80e5b54cdd952c7f2d63ccebbe1854c8161130d94ba134021a7c` |
| [examples/fixtures/config.json](examples/fixtures/config.json) | present | 440 | `f61c58f945f8028f7090076515b3789aeb3fdaae0282a7319d81d7cea355befc` |
| [examples/fixtures/scenario.json](examples/fixtures/scenario.json) | present | 497 | `82284bfd0be70c3053b6a694da15c2ac106bc9607d79103ede0ca023996a8d46` |

### Artifact Hashes

| Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [stress.json](stress.json) | present | json | 4029 | `d7693910dc7c2b6e90c5d4029b41e557be9d26a2ef2c22999e452c0e11c9e58c` |
| [stress.md](stress.md) | present | markdown | 1024 | `1066d939df0e190691409dc8b028033f077211f45a464db466703b241b86adb8` |
| [guardrails.json](guardrails.json) | present | json | 2644 | `bdf5d7a60bfb35244cb4e86173316fbcd5d58750b222d5915331e3e7b5451c82` |
| [guardrails.md](guardrails.md) | present | markdown | 1227 | `36cacf3305c25f59d63816ebc2201a217f10fb72df8be2344fad28c3e7344e3c` |
| [dashboard.html](dashboard.html) | present | html | 17770 | `236d5d8d14dc3e950716f7d62fa5b8c78629c8cb16a8b34148dbb6631f4c248e` |
| [dashboard_preview.md](dashboard_preview.md) | present | markdown | 1244 | `e47d97af20592889bf1e1b43b55a24260585da950465cd8392b3f5916855ff4b` |
| [dashboard_snippet.html](dashboard_snippet.html) | present | html | 876 | `2493dfe2d60c043cbf26ac5f3f2ef81fe266e9eba89bde9adeb846c445a5eb77` |
| [gallery.md](gallery.md) | present | markdown | 2189 | `d7c5b1261c32106afe47f75bda871ff629f9779d551cb6e989f2c9c28f21465e` |
| [walkthrough.md](walkthrough.md) | present | markdown | 3568 | `85169963cfbefa4ad317fd458e9109dbbca23050acd4d4230eeb6fec9c89a932` |
| [walkthrough.json](walkthrough.json) | present | json | 7501 | `b4a718dfcf5050ae918a64be2b19ddd224d78e9613fbeaf1d4bed21fca0ea4ba` |

## Case: cash-rebalance

- Fixture directory: `examples/templates/cash-rebalance`
- Output prefix: `templates/cash-rebalance/`

### Fixture Hashes

| Path | Status | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [examples/templates/cash-rebalance/holdings.csv](examples/templates/cash-rebalance/holdings.csv) | present | 555 | `32b87398502c5db37fde3951930b041018e7e8cc83850575984b952a31a2ba84` |
| [examples/templates/cash-rebalance/config.json](examples/templates/cash-rebalance/config.json) | present | 600 | `6bf02470ead55e402896e585acb2e1d4f2a2ae8d611e7453d06d56776fbddbc7` |
| [examples/templates/cash-rebalance/scenario.json](examples/templates/cash-rebalance/scenario.json) | present | 532 | `dec52116f05a459d230eafa07d43ca9a9f4fdfe361dd934f73f231d4cf29d7ca` |

### Artifact Hashes

| Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [templates/cash-rebalance/stress.json](templates/cash-rebalance/stress.json) | present | json | 4947 | `b8a492b89f529b7628ddc7252ab53c4b641ec4d95c177ede4b89629b89431106` |
| [templates/cash-rebalance/stress.md](templates/cash-rebalance/stress.md) | present | markdown | 1121 | `b6b54c5519623a1129a0e4efbed254f39e1e02757553aac73c298ed1f6211697` |
| [templates/cash-rebalance/guardrails.json](templates/cash-rebalance/guardrails.json) | present | json | 3063 | `7f95da29d0fd028673ef0046b10f4b0028e9bb0decd1311fad3bf0d66ee051b3` |
| [templates/cash-rebalance/guardrails.md](templates/cash-rebalance/guardrails.md) | present | markdown | 1401 | `7bd2ca6bff41e85c1ed841203bd5cb8d00815f2ea528716bfc8a2a6f1d005890` |

## Case: etf-core

- Fixture directory: `examples/templates/etf-core`
- Output prefix: `templates/etf-core/`

### Fixture Hashes

| Path | Status | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [examples/templates/etf-core/holdings.csv](examples/templates/etf-core/holdings.csv) | present | 515 | `8d9ce7d73d3c5c382763097e2d306908c09395b5cfd1fe8758e24e570ec2e59f` |
| [examples/templates/etf-core/config.json](examples/templates/etf-core/config.json) | present | 518 | `853e9caa5549fa60b7691224466f929b4efe84cdee9a49a0838b4b9ce6179cf9` |
| [examples/templates/etf-core/scenario.json](examples/templates/etf-core/scenario.json) | present | 507 | `09c6898eff9cfb219d53a40e73748a6275bb1c4d6e2a02bd52d276afd2f1096c` |

### Artifact Hashes

| Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [templates/etf-core/stress.json](templates/etf-core/stress.json) | present | json | 4765 | `015a952180e48fd5a4e61d406d74095c99970f0a68dc442268e8151b6bca9dac` |
| [templates/etf-core/stress.md](templates/etf-core/stress.md) | present | markdown | 1054 | `3f434fd71a0ec5199f53f5bb79bd3d66a286b6911d66118b339bf0f16bb40e87` |
| [templates/etf-core/guardrails.json](templates/etf-core/guardrails.json) | present | json | 2437 | `8cb9fda70fd244ecc3535f592f3126ae69ae883e3d49ea8fd3f0451461ab68a7` |
| [templates/etf-core/guardrails.md](templates/etf-core/guardrails.md) | present | markdown | 1135 | `182b86b6181661f3ed2dd5e4d0f88f3efaa301cc7cc211fee152029bbc36dae7` |

## Case: leveraged-sleeve

- Fixture directory: `examples/templates/leveraged-sleeve`
- Output prefix: `templates/leveraged-sleeve/`

### Fixture Hashes

| Path | Status | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [examples/templates/leveraged-sleeve/holdings.csv](examples/templates/leveraged-sleeve/holdings.csv) | present | 516 | `778d7fa9d35f5384e28f504904742895281746a256e252341c6314e72c7ec5a9` |
| [examples/templates/leveraged-sleeve/config.json](examples/templates/leveraged-sleeve/config.json) | present | 595 | `79d503f25f08f4bc670d69b40920155f24f8dfc038a30bb7cfac7dd7c6acc05a` |
| [examples/templates/leveraged-sleeve/scenario.json](examples/templates/leveraged-sleeve/scenario.json) | present | 531 | `adc0cefc219892a4b887ae91e4dc18a0db12b0bf11f753c0e625a4b3af8e67b8` |

### Artifact Hashes

| Path | Status | Format | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [templates/leveraged-sleeve/stress.json](templates/leveraged-sleeve/stress.json) | present | json | 4930 | `99137b3a1c01c768332704ea10bb741dbdf7925062d8a9e301bd24f59d2eeb34` |
| [templates/leveraged-sleeve/stress.md](templates/leveraged-sleeve/stress.md) | present | markdown | 1129 | `070fa448f12cf1fd1e1e7f5101d32de99e69906220ebbd1115ba29a630d16b89` |
| [templates/leveraged-sleeve/guardrails.json](templates/leveraged-sleeve/guardrails.json) | present | json | 2820 | `b502ec1b19bb59d07e77af0eb609c8f936f020fa87edf97af2914582ba6682d3` |
| [templates/leveraged-sleeve/guardrails.md](templates/leveraged-sleeve/guardrails.md) | present | markdown | 1291 | `f43bed65e5a4dcd315d9d60f07a7f532133cc989a8895bd585879d373fade346` |
