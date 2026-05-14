"""Template gallery discovery and rendering."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TEMPLATES_DIR = Path("examples/templates")
TEMPLATE_FIXTURE_FILES = (
    "holdings.csv",
    "config.json",
    "catalysts.json",
    "scenario.json",
)


@dataclass(frozen=True)
class PortfolioTemplate:
    slug: str
    name: str
    description: str
    fixture_dir: Path

    @property
    def fixture_files(self) -> tuple[str, ...]:
        return TEMPLATE_FIXTURE_FILES


_TEMPLATE_METADATA = {
    "etf-core": {
        "name": "ETF Core",
        "description": (
            "Diversified stock, bond, and Treasury-bill core allocation with "
            "global equity and duration review points."
        ),
    },
    "leveraged-sleeve": {
        "name": "Leveraged Sleeve",
        "description": (
            "Core equity book with a capped leveraged growth sleeve, liquidity "
            "buffer, and tighter review cadence."
        ),
    },
    "cash-rebalance": {
        "name": "Cash Rebalance",
        "description": (
            "High-cash portfolio staged for tax-aware deployment after drift or "
            "market pullback triggers."
        ),
    },
}


def list_templates(templates_dir: Path = DEFAULT_TEMPLATES_DIR) -> list[PortfolioTemplate]:
    """Return known templates that have complete fixture files."""

    templates = []
    for slug in sorted(_TEMPLATE_METADATA):
        fixture_dir = templates_dir / slug
        missing = [
            filename
            for filename in TEMPLATE_FIXTURE_FILES
            if not (fixture_dir / filename).is_file()
        ]
        if missing:
            continue
        metadata = _TEMPLATE_METADATA[slug]
        templates.append(
            PortfolioTemplate(
                slug=slug,
                name=metadata["name"],
                description=metadata["description"],
                fixture_dir=fixture_dir,
            )
        )
    return templates


def template_manifest(templates_dir: Path = DEFAULT_TEMPLATES_DIR) -> dict:
    templates = list_templates(templates_dir)
    return {
        "schema_version": 1,
        "template_count": len(templates),
        "templates_dir": templates_dir.as_posix(),
        "templates": [
            {
                "slug": template.slug,
                "name": template.name,
                "description": template.description,
                "fixture_dir": template.fixture_dir.as_posix(),
                "fixture_files": list(template.fixture_files),
            }
            for template in templates
        ],
    }


def render_template_list_json(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def render_template_list_markdown(manifest: dict) -> str:
    lines = [
        "# Portfolio Templates",
        "",
        f"- Templates directory: {manifest['templates_dir']}",
        f"- Template count: {manifest['template_count']}",
        "",
        "| Slug | Name | Fixtures | Description |",
        "| --- | --- | --- | --- |",
    ]
    for template in manifest["templates"]:
        fixtures = ", ".join(template["fixture_files"])
        lines.append(
            "| {slug} | {name} | {fixtures} | {description} |".format(
                slug=template["slug"],
                name=template["name"],
                fixtures=fixtures,
                description=template["description"],
            )
        )
    return "\n".join(lines) + "\n"
