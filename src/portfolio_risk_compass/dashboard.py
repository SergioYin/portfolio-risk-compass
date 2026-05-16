"""Static dashboard HTML export."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_DASHBOARD_TITLE = "Portfolio Risk Compass Dashboard"
DEFAULT_DASHBOARD_OUTPUT = "dashboard.html"
DEFAULT_GALLERY_MARKDOWN = "gallery.md"
DEFAULT_DASHBOARD_SNIPPET = "dashboard_snippet.html"
DEFAULT_DASHBOARD_PREVIEW = "dashboard_preview.md"
DEFAULT_WALKTHROUGH_MARKDOWN = "walkthrough.md"
DEFAULT_WALKTHROUGH_JSON = "walkthrough.json"
SAFETY_BOUNDARY_TEXT = (
    "Static portfolio review artifact only; not investment advice, trading "
    "guidance, live market data, or broker execution."
)


def build_dashboard_html(
    input_json: Path,
    title: str = DEFAULT_DASHBOARD_TITLE,
) -> str:
    """Render a self-contained, no-JS dashboard from a demo manifest or report."""

    source = _read_json(input_json)
    bundle_dir = input_json.parent
    if _is_manifest(source):
        manifest = source
        exposure = _load_artifact(bundle_dir, manifest, "exposure_report.json")
        catalysts = _load_artifact(bundle_dir, manifest, "catalysts.json")
        guardrails = _load_artifact(bundle_dir, manifest, "guardrails.json")
        stress = _load_artifact(bundle_dir, manifest, "stress.json")
    else:
        manifest = None
        exposure = source
        catalysts = None
        guardrails = None
        stress = None

    return render_dashboard_html(
        exposure=exposure,
        manifest=manifest,
        catalysts=catalysts,
        guardrails=guardrails,
        stress=stress,
        title=title,
    )


def render_dashboard_html(
    exposure: dict,
    manifest: dict | None = None,
    catalysts: dict | None = None,
    guardrails: dict | None = None,
    stress: dict | None = None,
    title: str = DEFAULT_DASHBOARD_TITLE,
) -> str:
    metadata = exposure.get("metadata", {})
    generated = manifest.get("as_of") if manifest else metadata.get("as_of", "unknown")
    base_currency = metadata.get("base_currency", "n/a")
    total_value = metadata.get("total_market_value", "n/a")
    risk_boundary = _risk_boundary_text(guardrails)

    nav = [
        ("summary", "Summary"),
        ("exposure", "Exposure"),
        ("concentration", "Concentration"),
    ]
    if guardrails:
        nav.append(("guardrails", "Risk Boundaries"))
    if stress:
        nav.append(("stress", "Stress"))
    if catalysts:
        nav.append(("catalysts", "Catalysts"))
    if manifest:
        nav.append(("bundle", "Bundle"))

    body = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_text(title)}</title>",
        f"<style>{_stylesheet()}</style>",
        "</head>",
        "<body>",
        '<header class="site-header">',
        f"<h1>{_text(title)}</h1>",
        f"<p>Generated from static JSON artifacts as of {_text(generated)}.</p>",
        '<nav aria-label="Dashboard sections">',
        "".join(
            f'<a href="#{_attr(section_id)}">{_text(label)}</a>'
            for section_id, label in nav
        ),
        "</nav>",
        "</header>",
        "<main>",
        '<section id="summary" class="section">',
        "<h2>Summary</h2>",
        '<div class="cards">',
        _card("Total Value", total_value, str(base_currency)),
        _card("Holdings", metadata.get("holding_count", "n/a"), "positions"),
        _card(
            "Concentration Limit",
            f"{metadata.get('concentration_limit_pct', 'n/a')}%",
            "configured boundary",
        ),
        _card("Risk Boundary", risk_boundary["status"], risk_boundary["detail"]),
        "</div>",
        f'<p class="boundary-text">Risk boundary: {_text(risk_boundary["sentence"])}</p>',
        "</section>",
        _exposure_section(exposure),
        _concentration_section(exposure),
    ]
    if guardrails:
        body.append(_guardrail_section(guardrails))
    if stress:
        body.append(_stress_section(stress))
    if catalysts:
        body.append(_catalyst_section(catalysts))
    if manifest:
        body.append(_bundle_section(manifest))
    body.extend(["</main>", "</body>", "</html>"])
    return "\n".join(body) + "\n"


def write_dashboard_html(
    input_json: Path,
    output_html: Path,
    title: str = DEFAULT_DASHBOARD_TITLE,
) -> None:
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(build_dashboard_html(input_json, title=title), encoding="utf-8")


def write_showcase_artifacts(
    manifest: dict,
    output_dir: Path,
    dashboard_path: str = DEFAULT_DASHBOARD_OUTPUT,
) -> dict[str, Path]:
    """Write static gallery and preview artifacts for generated dashboard outputs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "gallery_markdown": output_dir / DEFAULT_GALLERY_MARKDOWN,
        "dashboard_snippet": output_dir / DEFAULT_DASHBOARD_SNIPPET,
        "dashboard_preview": output_dir / DEFAULT_DASHBOARD_PREVIEW,
        "walkthrough_markdown": output_dir / DEFAULT_WALKTHROUGH_MARKDOWN,
        "walkthrough_json": output_dir / DEFAULT_WALKTHROUGH_JSON,
    }
    paths["gallery_markdown"].write_text(
        render_gallery_markdown(manifest, dashboard_path=dashboard_path),
        encoding="utf-8",
    )
    paths["dashboard_snippet"].write_text(
        render_dashboard_snippet_html(manifest, dashboard_path=dashboard_path),
        encoding="utf-8",
    )
    paths["dashboard_preview"].write_text(
        render_dashboard_preview_markdown(manifest, dashboard_path=dashboard_path),
        encoding="utf-8",
    )
    walkthrough = build_showcase_walkthrough(manifest, output_dir)
    paths["walkthrough_markdown"].write_text(
        render_showcase_walkthrough_markdown(walkthrough),
        encoding="utf-8",
    )
    paths["walkthrough_json"].write_text(
        json.dumps(walkthrough, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths


def write_showcase_walkthrough(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    """Write a guided, multi-template walkthrough from a demo manifest."""

    manifest = _read_json(manifest_json)
    output_dir = manifest_json.parent
    walkthrough = build_showcase_walkthrough(manifest, output_dir)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        render_showcase_walkthrough_markdown(walkthrough),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(walkthrough, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"markdown": markdown_path, "json": json_path}


def build_showcase_walkthrough(manifest: dict, output_dir: Path) -> dict:
    """Build deterministic guided walkthrough data for the base demo and templates."""

    cases = [_walkthrough_case("base-demo", "Base Demo", "Repository demo fixture set.", "", manifest, output_dir)]
    for template in manifest.get("templates", {}).get("templates", []):
        prefix = template.get("output_prefix", "")
        cases.append(
            _walkthrough_case(
                template.get("slug", prefix.strip("/") or "template"),
                template.get("name", template.get("slug", "Template")),
                template.get("description", ""),
                prefix,
                manifest,
                output_dir,
                fixture_dir=template.get("fixture_dir", ""),
            )
        )

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-showcase-walkthrough",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "case_count": len(cases),
        "guided_steps": [
            {
                "step": 1,
                "title": "Open the static dashboard",
                "artifact": DEFAULT_DASHBOARD_OUTPUT,
                "purpose": "Start with the no-JavaScript overview before inspecting source files.",
            },
            {
                "step": 2,
                "title": "Compare template risk postures",
                "artifact": DEFAULT_WALKTHROUGH_MARKDOWN,
                "purpose": "Use the case table to compare allocation, guardrail, stress, catalyst, and watchlist signals.",
            },
            {
                "step": 3,
                "title": "Trace every number to a file",
                "artifact": "index.json",
                "purpose": "Use the manifest and linked Markdown reports to verify each generated artifact.",
            },
        ],
        "cases": cases,
    }


def render_showcase_walkthrough_markdown(walkthrough: dict) -> str:
    lines = [
        "# Portfolio Risk Compass Guided Walkthrough",
        "",
        "Deterministic walkthrough for the base demo and bundled portfolio templates.",
        "",
        f"Safety boundary: {walkthrough.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        "",
        f"- As of: {walkthrough.get('as_of', 'unknown')}",
        f"- Case count: {walkthrough.get('case_count', 0)}",
        "",
        "## Guided Steps",
        "",
    ]
    for step in walkthrough.get("guided_steps", []):
        lines.append(
            "{step}. {title}: open `{artifact}`. {purpose}".format(
                step=step.get("step", ""),
                title=step.get("title", ""),
                artifact=step.get("artifact", ""),
                purpose=step.get("purpose", ""),
            )
        )

    lines.extend(
        [
            "",
            "## Case Gallery",
            "",
            "| Case | Focus | Total value | Guardrails | Stress delta | Catalysts | Watchlist | Start here |",
            "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for case in walkthrough.get("cases", []):
        metrics = case.get("metrics", {})
        links = case.get("links", {})
        lines.append(
            "| {name} | {description} | {value} | {guardrails} | {stress_delta} | {catalysts} | {watchlist} | [{start}]({start}) |".format(
                name=case.get("name", ""),
                description=case.get("description", ""),
                value=metrics.get("total_market_value", "n/a"),
                guardrails=metrics.get("guardrail_status", "n/a"),
                stress_delta=metrics.get("stress_market_value_delta_pct", "n/a"),
                catalysts=metrics.get("catalyst_count", "n/a"),
                watchlist=metrics.get("watchlist_item_count", "n/a"),
                start=links.get("exposure_markdown", ""),
            )
        )

    lines.extend(["", "## Inspection Path", ""])
    for case in walkthrough.get("cases", []):
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


def render_gallery_markdown(
    manifest: dict,
    dashboard_path: str = DEFAULT_DASHBOARD_OUTPUT,
) -> str:
    """Render a static gallery index for the demo dashboard and source artifacts."""

    artifacts = _select_gallery_artifacts(manifest)
    lines = [
        "# Dashboard Output Gallery",
        "",
        "Static showcase index for the deterministic demo bundle.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY_TEXT}",
        "",
        f"- Bundle: {manifest.get('bundle', 'unknown')}",
        f"- As of: {manifest.get('as_of', 'unknown')}",
        f"- Dashboard: [{dashboard_path}]({dashboard_path})",
        f"- Guided walkthrough: [{DEFAULT_WALKTHROUGH_MARKDOWN}]({DEFAULT_WALKTHROUGH_MARKDOWN})",
        f"- README preview: [{DEFAULT_DASHBOARD_PREVIEW}]({DEFAULT_DASHBOARD_PREVIEW})",
        f"- Embeddable snippet: [{DEFAULT_DASHBOARD_SNIPPET}]({DEFAULT_DASHBOARD_SNIPPET})",
        "",
        "## Featured Artifacts",
        "",
        "| Artifact | Format | Purpose |",
        "| --- | --- | --- |",
    ]
    for artifact in artifacts:
        path = artifact.get("path", "")
        lines.append(
            f"| [{path}]({path}) | {artifact.get('format', '')} | {artifact.get('description', '')} |"
        )

    template_entries = manifest.get("templates", {}).get("templates", [])
    if template_entries:
        lines.extend(
            [
                "",
                "## Template Galleries",
                "",
                "| Template | Outputs | Fixture directory |",
                "| --- | --- | --- |",
            ]
        )
        for template in template_entries:
            output_prefix = template.get("output_prefix", "")
            lines.append(
                "| [{name}]({prefix}exposure_report.md) | [{prefix}guardrails.md]({prefix}guardrails.md), "
                "[{prefix}stress.md]({prefix}stress.md), [{prefix}catalysts.md]({prefix}catalysts.md) | "
                "`{fixture_dir}` |".format(
                    name=template.get("name", template.get("slug", "")),
                    prefix=output_prefix,
                    fixture_dir=template.get("fixture_dir", ""),
                )
            )

    return "\n".join(lines) + "\n"


def render_dashboard_preview_markdown(
    manifest: dict,
    dashboard_path: str = DEFAULT_DASHBOARD_OUTPUT,
) -> str:
    """Render a text screenshot surrogate suitable for embedding in README."""

    lines = [
        "# Dashboard Preview",
        "",
        f"[Open the static dashboard]({dashboard_path})",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY_TEXT}",
        "",
        "| Panel | What it shows | Source artifact |",
        "| --- | --- | --- |",
        "| Summary | Total value, holding count, concentration limit, risk boundary | `exposure_report.json`, `guardrails.json` |",
        "| Exposure | Asset class, sector, region, and currency allocation tables | `exposure_report.json` |",
        "| Concentration | Holdings above the configured concentration limit | `exposure_report.json` |",
        "| Risk Boundaries | PASS/WARN/FAIL policy checks with actuals and limits | `guardrails.json` |",
        "| Stress | Scenario value, shock impacts, and value delta | `stress.json` |",
        "| Catalysts | Date-ordered thesis event checklist | `catalysts.json` |",
        "| Bundle | Generated artifact inventory | `index.json` |",
        "",
        "## Featured Files",
        "",
        "| File | Format | Bytes |",
        "| --- | --- | ---: |",
    ]
    for artifact in _select_gallery_artifacts(manifest):
        lines.append(
            "| `{path}` | {format} | {bytes} |".format(
                path=artifact.get("path", ""),
                format=artifact.get("format", ""),
                bytes=artifact.get("bytes", ""),
            )
        )
    return "\n".join(lines) + "\n"


def render_dashboard_snippet_html(
    manifest: dict,
    dashboard_path: str = DEFAULT_DASHBOARD_OUTPUT,
) -> str:
    """Render a small static HTML promo block for docs or release pages."""

    artifacts = _select_gallery_artifacts(manifest)
    links = "\n".join(
        "      <li><a href=\"{href}\">{label}</a> <span>{kind}</span></li>".format(
            href=_attr(artifact.get("path", "")),
            label=_text(artifact.get("path", "")),
            kind=_text(artifact.get("format", "")),
        )
        for artifact in artifacts
    )
    return (
        '<section class="portfolio-risk-compass-showcase">\n'
        "  <h2>Portfolio Risk Compass Dashboard</h2>\n"
        "  <p>Static, JavaScript-free dashboard generated from deterministic JSON and Markdown artifacts.</p>\n"
        f"  <p>{_text(SAFETY_BOUNDARY_TEXT)}</p>\n"
        f'  <p><a href="{_attr(dashboard_path)}">Open dashboard</a> '
        f'or <a href="{_attr(DEFAULT_WALKTHROUGH_MARKDOWN)}">view the guided walkthrough</a>.</p>\n'
        "  <ul>\n"
        f"{links}\n"
        "  </ul>\n"
        "</section>\n"
    )


def _walkthrough_case(
    slug: str,
    name: str,
    description: str,
    output_prefix: str,
    manifest: dict,
    output_dir: Path,
    fixture_dir: str = "",
) -> dict:
    exposure = _read_optional_artifact(output_dir, output_prefix + "exposure_report.json")
    guardrails = _read_optional_artifact(output_dir, output_prefix + "guardrails.json")
    stress = _read_optional_artifact(output_dir, output_prefix + "stress.json")
    catalysts = _read_optional_artifact(output_dir, output_prefix + "catalysts.json")
    watchlist = _read_optional_artifact(output_dir, output_prefix + "rebalance_watchlist.json")

    links = {
        "exposure_markdown": output_prefix + "exposure_report.md",
        "guardrails_markdown": output_prefix + "guardrails.md",
        "stress_markdown": output_prefix + "stress.md",
        "catalysts_markdown": output_prefix + "catalysts.md",
        "watchlist_markdown": output_prefix + "rebalance_watchlist.md",
    }
    return {
        "slug": slug,
        "name": name,
        "description": description,
        "fixture_dir": fixture_dir or manifest.get("fixtures", {}).get("directory", ""),
        "output_prefix": output_prefix,
        "links": links,
        "metrics": {
            "total_market_value": _nested(exposure, ("metadata", "total_market_value")),
            "holding_count": _nested(exposure, ("metadata", "holding_count")),
            "concentration_count": len(exposure.get("concentration", [])) if exposure else 0,
            "guardrail_status": _nested(guardrails, ("metadata", "overall_status")),
            "guardrail_fail_count": _status_count(guardrails, "FAIL"),
            "guardrail_warn_count": _status_count(guardrails, "WARN"),
            "stress_market_value_delta_pct": _nested(stress, ("metadata", "market_value_delta_pct")),
            "catalyst_count": _nested(catalysts, ("metadata", "catalyst_count")),
            "watchlist_item_count": len(watchlist.get("items", [])) if watchlist else 0,
        },
        "artifact_paths": _case_artifact_paths(manifest, output_prefix),
    }


def _case_artifact_paths(manifest: dict, output_prefix: str) -> list[str]:
    paths = [artifact.get("path", "") for artifact in manifest.get("artifacts", [])]
    if not output_prefix:
        return [path for path in paths if "/" not in path]
    return [path for path in paths if path.startswith(output_prefix)]


def _read_optional_artifact(output_dir: Path, relative_path: str) -> dict | None:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"artifact path must stay inside output directory: {relative_path}")
    artifact_path = output_dir / path
    if not artifact_path.is_file():
        return None
    return _read_json(artifact_path)


def _nested(data: dict | None, keys: tuple[str, ...]) -> object:
    current: object = data or {}
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return "n/a"
        current = current[key]
    return current


def _status_count(guardrails: dict | None, status: str) -> int:
    if not guardrails:
        return 0
    return sum(1 for item in guardrails.get("items", []) if item.get("status") == status)


def _is_manifest(data: dict) -> bool:
    return isinstance(data.get("artifacts"), list) and "bundle" in data


def _select_gallery_artifacts(manifest: dict) -> list[dict]:
    wanted = {
        "exposure_report.md",
        "guardrails.md",
        "stress.md",
        "rebalance_watchlist.md",
        "catalysts.md",
        "index.json",
    }
    return [
        artifact
        for artifact in manifest.get("artifacts", [])
        if artifact.get("path") in wanted
    ]


def _load_artifact(bundle_dir: Path, manifest: dict, path: str) -> dict | None:
    artifact = next(
        (
            item
            for item in manifest.get("artifacts", [])
            if item.get("path") == path and item.get("format") == "json"
        ),
        None,
    )
    if artifact is None:
        return None

    artifact_path = Path(artifact["path"])
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        raise ValueError(f"artifact path must stay inside bundle directory: {path}")
    return _read_json(bundle_dir / artifact_path)


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _exposure_section(report: dict) -> str:
    groups = report.get("metadata", {}).get("group_by", [])
    parts = ['<section id="exposure" class="section">', "<h2>Exposure</h2>"]
    for group in groups:
        rows = report.get("exposures", {}).get(group, [])
        title = str(group).replace("_", " ").title()
        parts.extend(
            [
                f"<h3>{_text(title)}</h3>",
                '<table><thead><tr><th>Bucket</th><th>Market Value</th><th>Portfolio %</th></tr></thead><tbody>',
            ]
        )
        if rows:
            for row in rows:
                parts.append(
                    "<tr>"
                    f"<td>{_text(row.get('bucket', ''))}</td>"
                    f"<td>{_text(row.get('market_value', ''))}</td>"
                    f"<td>{_text(row.get('pct_of_portfolio', ''))}%</td>"
                    "</tr>"
                )
        else:
            parts.append("<tr><td>None</td><td>0.00</td><td>0.0000%</td></tr>")
        parts.append("</tbody></table>")
    parts.append("</section>")
    return "\n".join(parts)


def _concentration_section(report: dict) -> str:
    rows = report.get("concentration", [])
    parts = [
        '<section id="concentration" class="section">',
        "<h2>Concentration</h2>",
        '<table><thead><tr><th>Symbol</th><th>Market Value</th><th>Portfolio %</th><th>Limit %</th></tr></thead><tbody>',
    ]
    if rows:
        for row in rows:
            parts.append(
                "<tr>"
                f"<td>{_text(row.get('symbol', ''))}</td>"
                f"<td>{_text(row.get('market_value', ''))}</td>"
                f"<td>{_text(row.get('pct_of_portfolio', ''))}%</td>"
                f"<td>{_text(row.get('limit_pct', ''))}%</td>"
                "</tr>"
            )
    else:
        parts.append("<tr><td>None</td><td>0.00</td><td>0.0000%</td><td>0.0000%</td></tr>")
    parts.extend(["</tbody></table>", "</section>"])
    return "\n".join(parts)


def _guardrail_section(guardrails: dict) -> str:
    metadata = guardrails.get("metadata", {})
    parts = [
        '<section id="guardrails" class="section">',
        "<h2>Risk Boundaries</h2>",
        f'<p class="boundary-text">Risk boundary: {_text(_risk_boundary_text(guardrails)["sentence"])}</p>',
        '<table><thead><tr><th>Status</th><th>Check</th><th>Scope</th><th>Actual</th><th>Limit</th><th>Message</th></tr></thead><tbody>',
    ]
    for item in guardrails.get("items", []):
        status = item.get("status", "")
        parts.append(
            "<tr>"
            f'<td><span class="status status-{_attr(str(status).lower())}">{_text(status)}</span></td>'
            f"<td>{_text(item.get('check', ''))}</td>"
            f"<td>{_text(item.get('scope', ''))}</td>"
            f"<td>{_text(item.get('actual', ''))}</td>"
            f"<td>{_text(item.get('limit', ''))}</td>"
            f"<td>{_text(item.get('message', ''))}</td>"
            "</tr>"
        )
    parts.extend(
        [
            "</tbody></table>",
            '<dl class="meta-list">',
            f"<dt>Snapshot Date</dt><dd>{_text(metadata.get('snapshot_date', 'n/a'))}</dd>",
            f"<dt>Last Review</dt><dd>{_text(metadata.get('last_review_date', 'n/a'))}</dd>",
            "</dl>",
            "</section>",
        ]
    )
    return "\n".join(parts)


def _stress_section(stress: dict) -> str:
    metadata = stress.get("metadata", {})
    parts = [
        '<section id="stress" class="section">',
        "<h2>Stress</h2>",
        '<div class="cards">',
        _card("Scenario", metadata.get("scenario_name", "n/a"), "configured shocks"),
        _card("Stressed Value", metadata.get("stressed_market_value", "n/a"), "after shocks"),
        _card("Value Delta", metadata.get("market_value_delta", "n/a"), f"{metadata.get('market_value_delta_pct', 'n/a')}%"),
        "</div>",
        '<table><thead><tr><th>Shock</th><th>Selector</th><th>Bucket</th><th>Move %</th><th>Value Delta</th></tr></thead><tbody>',
    ]
    for row in stress.get("shock_impacts", []):
        parts.append(
            "<tr>"
            f"<td>{_text(row.get('name', ''))}</td>"
            f"<td>{_text(row.get('selector', ''))}</td>"
            f"<td>{_text(row.get('bucket', ''))}</td>"
            f"<td>{_text(row.get('price_move_pct', ''))}%</td>"
            f"<td>{_text(row.get('market_value_delta', ''))}</td>"
            "</tr>"
        )
    parts.extend(["</tbody></table>", "</section>"])
    return "\n".join(parts)


def _catalyst_section(catalysts: dict) -> str:
    parts = [
        '<section id="catalysts" class="section">',
        "<h2>Catalysts</h2>",
        '<table><thead><tr><th>Date</th><th>Symbol</th><th>Flag</th><th>Importance</th><th>Title</th><th>Action</th><th>Thesis</th></tr></thead><tbody>',
    ]
    for row in catalysts.get("catalysts", []):
        link = _safe_href(row.get("thesis_link", ""))
        thesis = (
            f'<a href="{_attr(link)}">Open</a>'
            if link
            else ""
        )
        parts.append(
            "<tr>"
            f"<td>{_text(row.get('date', ''))}</td>"
            f"<td>{_text(row.get('symbol', ''))}</td>"
            f"<td>{_text(row.get('flag', ''))}</td>"
            f"<td>{_text(row.get('importance', ''))}</td>"
            f"<td>{_text(row.get('title', ''))}</td>"
            f"<td>{_text(row.get('action', ''))}</td>"
            f"<td>{thesis}</td>"
            "</tr>"
        )
    parts.extend(["</tbody></table>", "</section>"])
    return "\n".join(parts)


def _bundle_section(manifest: dict) -> str:
    parts = [
        '<section id="bundle" class="section">',
        "<h2>Bundle</h2>",
        '<table><thead><tr><th>Artifact</th><th>Format</th><th>Description</th><th>Bytes</th></tr></thead><tbody>',
    ]
    for item in manifest.get("artifacts", []):
        parts.append(
            "<tr>"
            f"<td>{_text(item.get('path', ''))}</td>"
            f"<td>{_text(item.get('format', ''))}</td>"
            f"<td>{_text(item.get('description', ''))}</td>"
            f"<td>{_text(item.get('bytes', ''))}</td>"
            "</tr>"
        )
    parts.extend(["</tbody></table>", "</section>"])
    return "\n".join(parts)


def _risk_boundary_text(guardrails: dict | None) -> dict[str, str]:
    if not guardrails:
        return {
            "status": "n/a",
            "detail": "No guardrail artifact provided.",
            "sentence": "No guardrail artifact was provided.",
        }

    status = str(guardrails.get("metadata", {}).get("overall_status", "UNKNOWN"))
    items = guardrails.get("items", [])
    failures = [item for item in items if item.get("status") == "FAIL"]
    warnings = [item for item in items if item.get("status") == "WARN"]
    if failures:
        leading = failures[0].get("message", "A configured limit was breached.")
        detail = f"{len(failures)} fail, {len(warnings)} warn"
        sentence = f"{status}. {detail}. {leading}"
    elif warnings:
        leading = warnings[0].get("message", "A configured limit is near its boundary.")
        detail = f"0 fail, {len(warnings)} warn"
        sentence = f"{status}. {detail}. {leading}"
    else:
        detail = "All configured checks passed."
        sentence = f"{status}. {detail}"
    return {"status": status, "detail": detail, "sentence": sentence}


def _card(label: str, value: object, detail: object) -> str:
    return (
        '<article class="card">'
        f"<h3>{_text(label)}</h3>"
        f'<p class="card-value">{_text(value)}</p>'
        f'<p class="card-detail">{_text(detail)}</p>'
        "</article>"
    )


def _safe_href(value: object) -> str:
    href = str(value)
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto"}:
        return href
    if href.startswith("#"):
        return href
    return ""


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _attr(value: object) -> str:
    return escape(str(value), quote=True)


def _stylesheet() -> str:
    return """
:root {
  color-scheme: light;
  --bg: #f5f7f9;
  --panel: #ffffff;
  --ink: #172026;
  --muted: #5d6973;
  --line: #d9e0e6;
  --accent: #116466;
  --fail: #a62323;
  --warn: #8a5a00;
  --pass: #1d6b3b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Arial, Helvetica, sans-serif;
  line-height: 1.45;
}
.site-header {
  background: #172026;
  color: #fff;
  padding: 32px max(24px, calc((100vw - 1180px) / 2));
}
.site-header h1 { margin: 0 0 8px; font-size: 32px; }
.site-header p { margin: 0 0 20px; color: #d4dde5; }
nav { display: flex; flex-wrap: wrap; gap: 10px; }
nav a {
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 6px;
  padding: 7px 10px;
  text-decoration: none;
}
main {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}
.section {
  margin: 0 0 24px;
  padding: 22px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
}
h2 { margin: 0 0 16px; font-size: 24px; }
h3 { margin: 18px 0 10px; font-size: 18px; }
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
}
.card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  background: #fbfcfd;
}
.card h3 {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 13px;
  text-transform: uppercase;
}
.card-value { margin: 0; font-size: 24px; font-weight: 700; }
.card-detail { margin: 6px 0 0; color: var(--muted); }
.boundary-text {
  border-left: 4px solid var(--accent);
  margin: 16px 0 0;
  padding: 8px 12px;
  background: #eef7f6;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 18px;
  font-size: 14px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 9px 8px;
  text-align: left;
  vertical-align: top;
}
th { color: var(--muted); font-size: 12px; text-transform: uppercase; }
.status {
  border-radius: 999px;
  display: inline-block;
  font-weight: 700;
  padding: 2px 8px;
}
.status-pass { color: var(--pass); background: #e7f4ec; }
.status-warn { color: var(--warn); background: #fff4d8; }
.status-fail { color: var(--fail); background: #fae7e7; }
.meta-list {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 6px 12px;
}
.meta-list dt { color: var(--muted); font-weight: 700; }
.meta-list dd { margin: 0; }
@media (max-width: 720px) {
  .site-header { padding: 24px 16px; }
  main { padding: 16px; }
  .section { padding: 16px; overflow-x: auto; }
  .site-header h1 { font-size: 26px; }
}
""".strip()
