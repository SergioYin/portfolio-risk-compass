"""Deterministic case-study comparison artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from .dashboard import SAFETY_BOUNDARY_TEXT
from .reviewer_evidence import (
    DEFAULT_REVIEWER_EVIDENCE_JSON,
    DEFAULT_REVIEWER_EVIDENCE_MARKDOWN,
)

DEFAULT_CASE_STUDY_MARKDOWN = "case_study_comparison.md"
DEFAULT_CASE_STUDY_JSON = "case_study_comparison.json"

CASE_ORDER = {
    "base-demo": 0,
    "etf-core": 1,
    "leveraged-sleeve": 2,
    "cash-rebalance": 3,
}

CASE_SOURCE_FILENAMES = (
    "exposure_report.json",
    "exposure_report.md",
    "guardrails.json",
    "guardrails.md",
    "stress.json",
    "stress.md",
    "catalysts.json",
    "catalysts.md",
    "rebalance_watchlist.json",
    "rebalance_watchlist.md",
)


def build_case_study_comparison(manifest: dict, output_dir: Path) -> dict:
    """Build deterministic comparison data for base and template demo cases."""

    generated_paths = {
        DEFAULT_CASE_STUDY_JSON,
        DEFAULT_CASE_STUDY_MARKDOWN,
        DEFAULT_REVIEWER_EVIDENCE_JSON,
        DEFAULT_REVIEWER_EVIDENCE_MARKDOWN,
    }
    manifest_paths = {
        artifact.get("path", "")
        for artifact in manifest.get("artifacts", [])
        if isinstance(artifact, dict) and artifact.get("path") not in generated_paths
    }
    cases = [
        _case_entry(
            "base-demo",
            "Base Demo",
            "Repository demo fixture set.",
            "",
            output_dir,
            manifest_paths,
        )
    ]
    for template in manifest.get("templates", {}).get("templates", []):
        cases.append(
            _case_entry(
                template.get("slug", "template"),
                template.get("name", template.get("slug", "Template")),
                template.get("description", ""),
                template.get("output_prefix", ""),
                output_dir,
                manifest_paths,
            )
        )
    cases = sorted(cases, key=lambda case: (CASE_ORDER.get(case["slug"], 99), case["slug"]))
    missing_artifacts = sorted(
        {
            artifact
            for case in cases
            for artifact in case.get("source_artifacts", {}).get("missing", [])
        }
    )

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-case-study-comparison",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "case_count": len(cases),
        "artifact_coverage": {
            "manifest_artifact_count": len(manifest_paths),
            "expected_case_artifact_count": sum(
                len(case.get("source_artifacts", {}).get("expected", []))
                for case in cases
            ),
            "missing": missing_artifacts,
            "complete": not missing_artifacts,
        },
        "cases": cases,
        "comparison_highlights": _comparison_highlights(cases),
    }


def render_case_study_json(comparison: dict) -> str:
    return json.dumps(comparison, indent=2, sort_keys=True) + "\n"


def render_case_study_markdown(comparison: dict) -> str:
    lines = [
        "# Portfolio Risk Compass Case-Study Comparison",
        "",
        "Deterministic comparison of the base demo and bundled template outputs.",
        "",
        f"Safety boundary: {comparison.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        "",
        f"- As of: {comparison.get('as_of', 'unknown')}",
        f"- Case count: {comparison.get('case_count', 0)}",
        "- Manifest coverage: {status}".format(
            status="complete"
            if comparison.get("artifact_coverage", {}).get("complete")
            else "incomplete"
        ),
        "",
        "## Comparison Table",
        "",
        "| Case | Focus | Total value | Cash % | Equity % | Leveraged equity % | Guardrails | Stress delta % | Watchlist | Catalysts |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for case in comparison.get("cases", []):
        metrics = case.get("metrics", {})
        lines.append(
            "| {name} | {description} | {total} | {cash} | {equity} | {leveraged} | {guardrails} | {stress} | {watchlist} | {catalysts} |".format(
                name=case.get("name", ""),
                description=case.get("description", ""),
                total=metrics.get("total_market_value", "n/a"),
                cash=metrics.get("cash_pct", "n/a"),
                equity=metrics.get("equity_pct", "n/a"),
                leveraged=metrics.get("leveraged_equity_pct", "n/a"),
                guardrails=metrics.get("guardrail_status", "n/a"),
                stress=metrics.get("stress_market_value_delta_pct", "n/a"),
                watchlist=metrics.get("watchlist_item_count", "n/a"),
                catalysts=metrics.get("catalyst_count", "n/a"),
            )
        )

    lines.extend(["", "## Highlights", ""])
    for highlight in comparison.get("comparison_highlights", []):
        lines.append(
            "- {label}: {case} ({value})".format(
                label=highlight.get("label", ""),
                case=highlight.get("case", ""),
                value=highlight.get("value", ""),
            )
        )

    lines.extend(["", "## Source Artifacts", ""])
    for case in comparison.get("cases", []):
        links = case.get("links", {})
        lines.extend(
            [
                f"### {case.get('name', '')}",
                "",
                f"- Exposure: [{links.get('exposure_markdown', '')}]({links.get('exposure_markdown', '')})",
                f"- Guardrails: [{links.get('guardrails_markdown', '')}]({links.get('guardrails_markdown', '')})",
                f"- Stress: [{links.get('stress_markdown', '')}]({links.get('stress_markdown', '')})",
                f"- Catalysts: [{links.get('catalysts_markdown', '')}]({links.get('catalysts_markdown', '')})",
                f"- Rebalance review watchlist: [{links.get('watchlist_markdown', '')}]({links.get('watchlist_markdown', '')})",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def write_case_study_comparison(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    comparison = build_case_study_comparison(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_case_study_markdown(comparison), encoding="utf-8")
    json_path.write_text(render_case_study_json(comparison), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _case_entry(
    slug: str,
    name: str,
    description: str,
    output_prefix: str,
    output_dir: Path,
    manifest_paths: set[str],
) -> dict:
    exposure = _read_optional_artifact(output_dir, output_prefix + "exposure_report.json")
    guardrails = _read_optional_artifact(output_dir, output_prefix + "guardrails.json")
    stress = _read_optional_artifact(output_dir, output_prefix + "stress.json")
    catalysts = _read_optional_artifact(output_dir, output_prefix + "catalysts.json")
    watchlist = _read_optional_artifact(output_dir, output_prefix + "rebalance_watchlist.json")
    source_artifacts = _source_artifact_coverage(output_prefix, manifest_paths)

    return {
        "slug": slug,
        "name": name,
        "description": description,
        "output_prefix": output_prefix,
        "source_artifacts": source_artifacts,
        "links": {
            "exposure_markdown": output_prefix + "exposure_report.md",
            "guardrails_markdown": output_prefix + "guardrails.md",
            "stress_markdown": output_prefix + "stress.md",
            "catalysts_markdown": output_prefix + "catalysts.md",
            "watchlist_markdown": output_prefix + "rebalance_watchlist.md",
        },
        "metrics": {
            "total_market_value": _nested(exposure, ("metadata", "total_market_value")),
            "holding_count": _nested(exposure, ("metadata", "holding_count")),
            "cash_pct": _exposure_pct(exposure, "asset_class", "Cash"),
            "equity_pct": _exposure_pct(exposure, "asset_class", "Equity"),
            "leveraged_equity_pct": _exposure_pct(exposure, "asset_class", "Leveraged Equity"),
            "top_holding": _top_holding(exposure),
            "concentration_count": len(exposure.get("concentration", [])) if exposure else 0,
            "guardrail_status": _nested(guardrails, ("metadata", "overall_status")),
            "guardrail_fail_count": _status_count(guardrails, "FAIL"),
            "guardrail_warn_count": _status_count(guardrails, "WARN"),
            "stress_scenario": _nested(stress, ("metadata", "scenario_name")),
            "stress_market_value_delta_pct": _nested(stress, ("metadata", "market_value_delta_pct")),
            "catalyst_count": _nested(catalysts, ("metadata", "catalyst_count")),
            "watchlist_item_count": len(watchlist.get("items", [])) if watchlist else 0,
            "watchlist_severity_counts": _nested(watchlist, ("metadata", "severity_counts")),
        },
    }


def _source_artifact_coverage(output_prefix: str, manifest_paths: set[str]) -> dict:
    expected = [output_prefix + filename for filename in CASE_SOURCE_FILENAMES]
    return {
        "expected": expected,
        "missing": [path for path in expected if path not in manifest_paths],
    }


def _comparison_highlights(cases: list[dict]) -> list[dict]:
    return [
        _max_highlight(cases, "Highest cash allocation", "cash_pct", absolute=False),
        _min_highlight(cases, "Largest stress drawdown", "stress_market_value_delta_pct"),
        _max_highlight(cases, "Most watchlist items", "watchlist_item_count", absolute=False),
    ]


def _max_highlight(cases: list[dict], label: str, metric: str, absolute: bool) -> dict:
    return _extreme_highlight(cases, label, metric, reverse=True, absolute=absolute)


def _min_highlight(cases: list[dict], label: str, metric: str) -> dict:
    return _extreme_highlight(cases, label, metric, reverse=False, absolute=False)


def _extreme_highlight(
    cases: list[dict],
    label: str,
    metric: str,
    reverse: bool,
    absolute: bool,
) -> dict:
    candidates = []
    for case in cases:
        value = case.get("metrics", {}).get(metric)
        number = _as_float(value)
        if number is not None:
            candidates.append((abs(number) if absolute else number, case, value))
    if not candidates:
        return {"label": label, "case": "n/a", "value": "n/a", "metric": metric}
    _, case, value = sorted(candidates, key=lambda item: (item[0], item[1]["slug"]), reverse=reverse)[0]
    return {"label": label, "case": case["name"], "value": value, "metric": metric}


def _exposure_pct(exposure: dict | None, group: str, bucket: str) -> str:
    if not exposure:
        return "n/a"
    for row in exposure.get("exposures", {}).get(group, []):
        if row.get("bucket") == bucket:
            return row.get("pct_of_portfolio", "n/a")
    return "0.0000"


def _top_holding(exposure: dict | None) -> dict:
    holdings = exposure.get("holdings", []) if exposure else []
    if not holdings:
        return {"symbol": "n/a", "pct_of_portfolio": "n/a", "market_value": "n/a"}
    top = sorted(
        holdings,
        key=lambda holding: (
            _as_float(holding.get("market_value")) or 0.0,
            holding.get("symbol", ""),
        ),
        reverse=True,
    )[0]
    total = _as_float(_nested(exposure, ("metadata", "total_market_value"))) or 0.0
    market_value = top.get("market_value", "n/a")
    pct = "n/a" if total == 0.0 else f"{((_as_float(market_value) or 0.0) / total * 100):.4f}"
    return {
        "symbol": top.get("symbol", "n/a"),
        "market_value": market_value,
        "pct_of_portfolio": pct,
    }


def _status_count(guardrails: dict | None, status: str) -> int:
    if not guardrails:
        return 0
    return sum(1 for item in guardrails.get("items", []) if item.get("status") == status)


def _nested(data: dict | None, keys: tuple[str, ...]) -> object:
    current: object = data or {}
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return "n/a"
        current = current[key]
    return current


def _as_float(value: object) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _read_optional_artifact(output_dir: Path, relative_path: str) -> dict | None:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"artifact path must stay inside output directory: {relative_path}")
    artifact_path = output_dir / path
    if not artifact_path.is_file():
        return None
    return _read_json(artifact_path)


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data
