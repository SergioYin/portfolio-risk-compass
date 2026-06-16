"""Demo artifact bundle generation."""

from __future__ import annotations

import json
from pathlib import Path

from .analysis import analyze_portfolio
from .case_study import (
    DEFAULT_CASE_STUDY_JSON,
    DEFAULT_CASE_STUDY_MARKDOWN,
    build_case_study_comparison,
    render_case_study_json,
    render_case_study_markdown,
)
from .catalysts import (
    build_catalyst_checklist,
    read_catalysts_json,
    render_catalyst_json,
    render_catalyst_markdown,
)
from .config import read_config_json
from .dashboard import write_showcase_artifacts
from .guardrails import (
    ReviewDates,
    evaluate_guardrails,
    parse_review_date,
    render_guardrail_json,
    render_guardrail_markdown,
)
from .holdings import read_holdings_csv
from .history import build_history_ledger, render_history_json, render_history_markdown
from .rebalance_watchlist import (
    build_rebalance_watchlist,
    render_rebalance_watchlist_json,
    render_rebalance_watchlist_markdown,
)
from .reports import render_json_report, render_markdown_report
from .review_memo import build_review_memo, render_review_memo_markdown
from .snapshots import build_snapshot, render_snapshot_json
from .stress import (
    read_scenario_json,
    render_stress_json,
    render_stress_markdown,
    stress_portfolio,
)
from .templates import DEFAULT_TEMPLATES_DIR, list_templates, template_manifest

DEFAULT_FIXTURES_DIR = Path("examples/fixtures")
DEFAULT_OUTPUT_DIR = Path("examples/outputs")
DEFAULT_AS_OF = "2026-05-15"


def build_demo_bundle(
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    as_of: str = DEFAULT_AS_OF,
    templates_dir: Path = DEFAULT_TEMPLATES_DIR,
    include_templates: bool = True,
) -> dict:
    """Regenerate deterministic demo outputs from repository fixtures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _build_fixture_artifacts(
        fixtures_dir=fixtures_dir,
        output_dir=output_dir,
        output_prefix="",
        as_of=as_of,
        snapshot_id="demo-current",
    )

    template_entries = []
    if include_templates:
        for template in list_templates(templates_dir):
            template_prefix = f"templates/{template.slug}/"
            artifacts.extend(
                _build_fixture_artifacts(
                    fixtures_dir=template.fixture_dir,
                    output_dir=output_dir,
                    output_prefix=template_prefix,
                    as_of=as_of,
                    snapshot_id=f"template-{template.slug}-current",
                )
            )
            template_entries.append(
                {
                    "slug": template.slug,
                    "name": template.name,
                    "description": template.description,
                    "fixture_dir": template.fixture_dir.as_posix(),
                    "output_prefix": template_prefix,
                    "fixture_files": list(template.fixture_files),
                }
            )

    manifest = {
        "schema_version": 1,
        "bundle": "portfolio-risk-compass-demo",
        "as_of": as_of,
        "fixtures": {
            "directory": str(fixtures_dir),
            "files": _fixture_files(fixtures_dir),
        },
        "templates": {
            **template_manifest(templates_dir),
            "templates": template_entries,
        },
        "artifacts": artifacts,
    }
    comparison = build_case_study_comparison(manifest, output_dir)
    artifacts.extend(
        [
            _write_artifact(
                output_dir,
                DEFAULT_CASE_STUDY_JSON,
                "json",
                "Deterministic base and template case-study comparison as JSON.",
                ("index.json", "generated JSON artifacts"),
                render_case_study_json(comparison),
            ),
            _write_artifact(
                output_dir,
                DEFAULT_CASE_STUDY_MARKDOWN,
                "markdown",
                "Deterministic base and template case-study comparison as Markdown.",
                ("index.json", "generated JSON artifacts"),
                render_case_study_markdown(comparison),
            ),
        ]
    )
    _write_text(
        output_dir / "index.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    write_showcase_artifacts(manifest, output_dir)
    return manifest


def _build_fixture_artifacts(
    fixtures_dir: Path,
    output_dir: Path,
    output_prefix: str,
    as_of: str,
    snapshot_id: str,
) -> list[dict]:
    holdings_path = fixtures_dir / "holdings.csv"
    config_path = fixtures_dir / "config.json"
    catalysts_path = fixtures_dir / "catalysts.json"
    scenario_path = fixtures_dir / "scenario.json"
    history_dir = fixtures_dir / "history"

    holdings = read_holdings_csv(holdings_path)
    config = read_config_json(config_path)
    exposure_report = analyze_portfolio(holdings, config)
    snapshot = build_snapshot(
        exposure_report,
        snapshot_date=as_of,
        snapshot_id=snapshot_id,
    )

    catalysts = read_catalysts_json(catalysts_path)
    catalyst_checklist = build_catalyst_checklist(catalysts, as_of=as_of)

    guardrail_review = evaluate_guardrails(
        holdings,
        config,
        ReviewDates(snapshot_date=parse_review_date(as_of, "as_of")),
    )

    scenario = read_scenario_json(scenario_path)
    stress_report = stress_portfolio(holdings, scenario)
    rebalance_watchlist = build_rebalance_watchlist(
        exposure_report,
        guardrail_review,
        stress_report,
    )

    artifacts = [
        _write_artifact(
            output_dir,
            f"{output_prefix}exposure_report.json",
            "json",
            "Portfolio exposure report as JSON.",
            ("holdings.csv", "config.json"),
            render_json_report(exposure_report),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}exposure_report.md",
            "markdown",
            "Portfolio exposure report as Markdown.",
            ("holdings.csv", "config.json"),
            render_markdown_report(exposure_report),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}snapshot_current.json",
            "json",
            "Current portfolio snapshot JSON.",
            ("holdings.csv", "config.json"),
            render_snapshot_json(snapshot),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}catalysts.json",
            "json",
            "Catalyst checklist as JSON.",
            ("catalysts.json",),
            render_catalyst_json(catalyst_checklist),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}catalysts.md",
            "markdown",
            "Catalyst checklist as Markdown.",
            ("catalysts.json",),
            render_catalyst_markdown(catalyst_checklist),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}guardrails.json",
            "json",
            "Portfolio guardrail review as JSON.",
            ("holdings.csv", "config.json"),
            render_guardrail_json(guardrail_review),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}guardrails.md",
            "markdown",
            "Portfolio guardrail review as Markdown.",
            ("holdings.csv", "config.json"),
            render_guardrail_markdown(guardrail_review),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}stress.json",
            "json",
            "Stress scenario report as JSON.",
            ("holdings.csv", "scenario.json"),
            render_stress_json(stress_report),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}stress.md",
            "markdown",
            "Stress scenario report as Markdown.",
            ("holdings.csv", "scenario.json"),
            render_stress_markdown(stress_report),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}rebalance_watchlist.json",
            "json",
            "Educational rebalance review watchlist as JSON.",
            ("holdings.csv", "config.json", "scenario.json"),
            render_rebalance_watchlist_json(rebalance_watchlist),
        ),
        _write_artifact(
            output_dir,
            f"{output_prefix}rebalance_watchlist.md",
            "markdown",
            "Educational rebalance review watchlist as Markdown.",
            ("holdings.csv", "config.json", "scenario.json"),
            render_rebalance_watchlist_markdown(rebalance_watchlist),
        ),
    ]
    if history_dir.is_dir():
        history_ledger = build_history_ledger(history_dir)
        artifacts.extend(
            [
                _write_artifact(
                    output_dir,
                    f"{output_prefix}history.json",
                    "json",
                    "Portfolio history ledger as JSON.",
                    ("history/*.json",),
                    render_history_json(history_ledger),
                ),
                _write_artifact(
                    output_dir,
                    f"{output_prefix}history.md",
                    "markdown",
                    "Portfolio history ledger as Markdown.",
                    ("history/*.json",),
                    render_history_markdown(history_ledger),
                ),
            ]
        )
        artifacts.append(
            _write_artifact(
                output_dir,
                f"{output_prefix}review_memo.md",
                "markdown",
                "Human review memo combining generated portfolio artifacts.",
                (
                    "holdings.csv",
                    "config.json",
                    "scenario.json",
                    "catalysts.json",
                    "history/*.json",
                ),
                render_review_memo_markdown(
                    build_review_memo(
                        output_dir / output_prefix,
                        title="Portfolio Review Memo",
                    )
                ),
            )
        )
    return artifacts


def _fixture_files(fixtures_dir: Path) -> list[str]:
    files = [
        "holdings.csv",
        "config.json",
        "catalysts.json",
        "scenario.json",
    ]
    if (fixtures_dir / "history").is_dir():
        files.append("history/*.json")
    return files


def _write_artifact(
    output_dir: Path,
    filename: str,
    artifact_format: str,
    description: str,
    source_fixtures: tuple[str, ...],
    content: str,
) -> dict:
    path = output_dir / filename
    _write_text(path, content)
    return {
        "path": filename,
        "format": artifact_format,
        "description": description,
        "source_fixtures": list(source_fixtures),
        "bytes": path.stat().st_size,
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
