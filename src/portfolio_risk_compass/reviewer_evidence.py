"""Reviewer evidence manifest for static demo artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT

DEFAULT_REVIEWER_EVIDENCE_MARKDOWN = "reviewer_evidence.md"
DEFAULT_REVIEWER_EVIDENCE_JSON = "reviewer_evidence.json"

DASHBOARD_REVIEW_PATHS = (
    "gallery.md",
    "dashboard_preview.md",
    "dashboard_snippet.html",
    "walkthrough.md",
    "walkthrough.json",
)
CASE_STUDY_REVIEW_PATHS = (
    "case_study_comparison.md",
    "case_study_comparison.json",
)


def build_reviewer_evidence(manifest: dict, output_dir: Path | None = None) -> dict:
    """Build deterministic evidence for cold review of generated demo artifacts."""

    artifact_index = {
        artifact.get("path", ""): artifact
        for artifact in manifest.get("artifacts", [])
        if isinstance(artifact, dict)
    }
    dashboard_artifacts = [
        _artifact_entry(path, artifact_index.get(path), manifest, output_dir)
        for path in DASHBOARD_REVIEW_PATHS
    ]
    case_study_artifacts = [
        _artifact_entry(path, artifact_index.get(path), manifest, output_dir)
        for path in CASE_STUDY_REVIEW_PATHS
    ]

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-reviewer-evidence",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "review_paths": {
            "dashboard": dashboard_artifacts,
            "case_study": case_study_artifacts,
        },
        "source_fixture_sets": _source_fixture_sets(manifest),
        "regeneration_commands": [
            "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
            "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
            "PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence",
        ],
    }


def render_reviewer_evidence_json(evidence: dict) -> str:
    return json.dumps(evidence, indent=2, sort_keys=True) + "\n"


def render_reviewer_evidence_markdown(evidence: dict) -> str:
    lines = [
        "# Portfolio Risk Compass Reviewer Evidence",
        "",
        "Deterministic trace for public dashboard and case-study demo artifacts.",
        "",
        f"Safety boundary: {evidence.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        "",
        f"- As of: {evidence.get('as_of', 'unknown')}",
        "",
        "## Regeneration Commands",
        "",
    ]
    for command in evidence.get("regeneration_commands", []):
        lines.append(f"- `{command}`")

    lines.extend(
        [
            "",
            "## Dashboard Evidence",
            "",
            "| Artifact | Status | Sources | Bytes |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for artifact in evidence.get("review_paths", {}).get("dashboard", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Case-Study Evidence",
            "",
            "| Artifact | Status | Sources | Bytes |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for artifact in evidence.get("review_paths", {}).get("case_study", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Source Fixture Sets",
            "",
            "| Case | Fixture directory | Fixture files |",
            "| --- | --- | --- |",
        ]
    )
    for source in evidence.get("source_fixture_sets", []):
        lines.append(
            "| {case} | `{fixture_dir}` | {files} |".format(
                case=_table_cell(source.get("case", "")),
                fixture_dir=_table_cell(source.get("fixture_dir", "")).replace(
                    "`", "\\`"
                ),
                files=", ".join(
                    _code_span(path) for path in source.get("fixture_files", [])
                ),
            )
        )

    return "\n".join(lines) + "\n"


def write_reviewer_evidence(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    evidence = build_reviewer_evidence(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_reviewer_evidence_markdown(evidence), encoding="utf-8")
    json_path.write_text(render_reviewer_evidence_json(evidence), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _artifact_entry(
    path: str,
    artifact: dict | None,
    manifest: dict,
    output_dir: Path | None,
) -> dict:
    if artifact is None:
        artifact_path = output_dir / path if output_dir else None
        exists = artifact_path.is_file() if artifact_path else False
        return {
            "path": path,
            "status": "sidecar" if exists else "external",
            "format": _format_from_path(path),
            "description": "Generated outside the demo manifest.",
            "source_fixtures": [],
            "source_paths": ["index.json"],
            "bytes": artifact_path.stat().st_size if artifact_path and exists else "n/a",
        }
    return {
        "path": artifact.get("path", path),
        "status": "manifested",
        "format": artifact.get("format", _format_from_path(path)),
        "description": artifact.get("description", ""),
        "source_fixtures": list(artifact.get("source_fixtures", [])),
        "source_paths": _source_paths_for_artifact(artifact, manifest),
        "bytes": artifact.get("bytes", "n/a"),
    }


def _artifact_row(artifact: dict) -> str:
    path = artifact.get("path", "")
    sources = artifact.get("source_paths", [])
    return "| {path} | {status} | {sources} | {bytes} |".format(
        path=_markdown_link(path),
        status=_table_cell(artifact.get("status", "")),
        sources=", ".join(_code_span(source) for source in sources) or "n/a",
        bytes=_table_cell(artifact.get("bytes", "n/a")),
    )


def _source_fixture_sets(manifest: dict) -> list[dict]:
    sources = [
        {
            "case": "base-demo",
            "fixture_dir": manifest.get("fixtures", {}).get("directory", ""),
            "fixture_files": manifest.get("fixtures", {}).get("files", []),
        }
    ]
    templates = sorted(
        manifest.get("templates", {}).get("templates", []),
        key=lambda template: template.get("slug", ""),
    )
    for template in templates:
        sources.append(
            {
                "case": template.get("slug", ""),
                "fixture_dir": template.get("fixture_dir", ""),
                "fixture_files": template.get("fixture_files", []),
            }
        )
    return sources


def _source_paths_for_artifact(artifact: dict, manifest: dict) -> list[str]:
    fixture_dir = _fixture_dir_for_artifact(artifact.get("path", ""), manifest)
    paths = []
    for source in artifact.get("source_fixtures", []):
        if source == "index.json":
            paths.append(source)
        elif source in {"generated JSON artifacts", "generated static artifacts"}:
            paths.append(source)
            paths.extend(_all_fixture_paths(manifest))
        elif fixture_dir:
            paths.append(f"{fixture_dir}/{source}")
        else:
            paths.append(source)
    return _dedupe(paths)


def _all_fixture_paths(manifest: dict) -> list[str]:
    paths = []
    for source in _source_fixture_sets(manifest):
        fixture_dir = source.get("fixture_dir", "")
        for filename in source.get("fixture_files", []):
            paths.append(f"{fixture_dir}/{filename}" if fixture_dir else filename)
    return paths


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))


def _dedupe(paths: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            deduped.append(path)
    return deduped


def _fixture_dir_for_artifact(path: str, manifest: dict) -> str:
    for template in manifest.get("templates", {}).get("templates", []):
        prefix = template.get("output_prefix", "")
        if prefix and path.startswith(prefix):
            return template.get("fixture_dir", "")
    return manifest.get("fixtures", {}).get("directory", "")


def _format_from_path(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "markdown"
    if suffix == ".html":
        return "html"
    return suffix.lstrip(".") or "unknown"


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data
