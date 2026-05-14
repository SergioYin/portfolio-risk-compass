"""Demo artifact bundle generation."""

from __future__ import annotations

import json
from pathlib import Path

from .analysis import analyze_portfolio
from .catalysts import (
    build_catalyst_checklist,
    read_catalysts_json,
    render_catalyst_json,
    render_catalyst_markdown,
)
from .config import read_config_json
from .guardrails import (
    ReviewDates,
    evaluate_guardrails,
    parse_review_date,
    render_guardrail_json,
    render_guardrail_markdown,
)
from .holdings import read_holdings_csv
from .reports import render_json_report, render_markdown_report
from .snapshots import build_snapshot, render_snapshot_json
from .stress import (
    read_scenario_json,
    render_stress_json,
    render_stress_markdown,
    stress_portfolio,
)

DEFAULT_FIXTURES_DIR = Path("examples/fixtures")
DEFAULT_OUTPUT_DIR = Path("examples/outputs")
DEFAULT_AS_OF = "2026-05-15"


def build_demo_bundle(
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    as_of: str = DEFAULT_AS_OF,
) -> dict:
    """Regenerate deterministic demo outputs from repository fixtures."""

    holdings_path = fixtures_dir / "holdings.csv"
    config_path = fixtures_dir / "config.json"
    catalysts_path = fixtures_dir / "catalysts.json"
    scenario_path = fixtures_dir / "scenario.json"

    holdings = read_holdings_csv(holdings_path)
    config = read_config_json(config_path)
    exposure_report = analyze_portfolio(holdings, config)
    snapshot = build_snapshot(
        exposure_report,
        snapshot_date=as_of,
        snapshot_id="demo-current",
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

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = [
        _write_artifact(
            output_dir,
            "exposure_report.json",
            "json",
            "Portfolio exposure report as JSON.",
            ("holdings.csv", "config.json"),
            render_json_report(exposure_report),
        ),
        _write_artifact(
            output_dir,
            "exposure_report.md",
            "markdown",
            "Portfolio exposure report as Markdown.",
            ("holdings.csv", "config.json"),
            render_markdown_report(exposure_report),
        ),
        _write_artifact(
            output_dir,
            "snapshot_current.json",
            "json",
            "Current portfolio snapshot JSON.",
            ("holdings.csv", "config.json"),
            render_snapshot_json(snapshot),
        ),
        _write_artifact(
            output_dir,
            "catalysts.json",
            "json",
            "Catalyst checklist as JSON.",
            ("catalysts.json",),
            render_catalyst_json(catalyst_checklist),
        ),
        _write_artifact(
            output_dir,
            "catalysts.md",
            "markdown",
            "Catalyst checklist as Markdown.",
            ("catalysts.json",),
            render_catalyst_markdown(catalyst_checklist),
        ),
        _write_artifact(
            output_dir,
            "guardrails.json",
            "json",
            "Portfolio guardrail review as JSON.",
            ("holdings.csv", "config.json"),
            render_guardrail_json(guardrail_review),
        ),
        _write_artifact(
            output_dir,
            "guardrails.md",
            "markdown",
            "Portfolio guardrail review as Markdown.",
            ("holdings.csv", "config.json"),
            render_guardrail_markdown(guardrail_review),
        ),
        _write_artifact(
            output_dir,
            "stress.json",
            "json",
            "Stress scenario report as JSON.",
            ("holdings.csv", "scenario.json"),
            render_stress_json(stress_report),
        ),
        _write_artifact(
            output_dir,
            "stress.md",
            "markdown",
            "Stress scenario report as Markdown.",
            ("holdings.csv", "scenario.json"),
            render_stress_markdown(stress_report),
        ),
    ]

    manifest = {
        "schema_version": 1,
        "bundle": "portfolio-risk-compass-demo",
        "as_of": as_of,
        "fixtures": {
            "directory": str(fixtures_dir),
            "files": [
                "holdings.csv",
                "config.json",
                "catalysts.json",
                "scenario.json",
            ],
        },
        "artifacts": artifacts,
    }
    _write_text(
        output_dir / "index.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    return manifest


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
