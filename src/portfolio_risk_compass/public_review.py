"""Public reviewer walkthrough and evidence packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT
from .scenario_evidence import PUBLIC_SAFETY_NOTICE

DEFAULT_PUBLIC_REVIEW_MARKDOWN = "public_review_walkthrough.md"
DEFAULT_PUBLIC_REVIEW_JSON = "public_review_walkthrough.json"

REVIEW_ARTIFACT_PATHS = (
    "dashboard.html",
    "dashboard_preview.md",
    "dashboard_snippet.html",
    "gallery.md",
    "walkthrough.md",
    "walkthrough.json",
    "reviewer_evidence.md",
    "reviewer_evidence.json",
    "scenario_evidence_receipt.md",
    "scenario_evidence_receipt.json",
    "case_study_comparison.md",
    "case_study_comparison.json",
    "index.json",
)

BOUNDARY_FLAGS = {
    "live_data": "none; all values come from static CSV/JSON fixtures or generated local artifacts",
    "broker": "none; no account access, order entry, execution, or broker connectivity",
    "advice": "none; artifact is a review walkthrough, not investment advice or trading guidance",
}


def build_public_review_walkthrough(manifest: dict, output_dir: Path) -> dict:
    """Build deterministic public-review evidence for the static dashboard flow."""

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-public-review-walkthrough",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "public_safety_notice": PUBLIC_SAFETY_NOTICE,
        "boundary_flags": BOUNDARY_FLAGS,
        "review_scope": (
            "Static dashboard walkthrough and evidence packet for public reviewers. "
            "It hashes local fixture inputs and generated local artifacts only."
        ),
        "walkthrough_steps": [
            {
                "step": 1,
                "title": "Regenerate the deterministic bundle",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
                "evidence": ["index.json"],
            },
            {
                "step": 2,
                "title": "Render the static dashboard",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
                "evidence": ["dashboard.html", "dashboard_preview.md", "dashboard_snippet.html"],
            },
            {
                "step": 3,
                "title": "Refresh review evidence",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence",
                "evidence": ["reviewer_evidence.md", "reviewer_evidence.json"],
            },
            {
                "step": 4,
                "title": "Refresh scenario evidence receipt",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt",
                "evidence": ["scenario_evidence_receipt.md", "scenario_evidence_receipt.json"],
            },
            {
                "step": 5,
                "title": "Refresh this public packet",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass public-review",
                "evidence": [DEFAULT_PUBLIC_REVIEW_MARKDOWN, DEFAULT_PUBLIC_REVIEW_JSON],
            },
        ],
        "review_artifacts": [
            _artifact_entry(output_dir, path) for path in REVIEW_ARTIFACT_PATHS
        ],
        "fixture_inputs": _fixture_entries(manifest),
        "case_count": 1 + len(manifest.get("templates", {}).get("templates", [])),
        "manifest_artifact_count": len(manifest.get("artifacts", [])),
    }


def render_public_review_json(packet: dict) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def render_public_review_markdown(packet: dict) -> str:
    lines = [
        "# Portfolio Risk Compass Public Review Walkthrough",
        "",
        "Deterministic static dashboard walkthrough and evidence packet for public reviewers.",
        "",
        f"Safety boundary: {packet.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        f"Public safety notice: {packet.get('public_safety_notice', PUBLIC_SAFETY_NOTICE)}",
        "",
        "## Boundaries",
        "",
    ]
    for key, value in packet.get("boundary_flags", {}).items():
        lines.append(f"- No {_table_cell(key).replace('_', ' ')}: {_table_cell(value)}")

    lines.extend(["", "## Rerun Commands", ""])
    for step in packet.get("walkthrough_steps", []):
        evidence = ", ".join(_code_span(path) for path in step.get("evidence", []))
        lines.append(
            "{step}. {title}: `{command}`. Evidence: {evidence}.".format(
                step=step.get("step", ""),
                title=_table_cell(step.get("title", "")),
                command=_table_cell(step.get("command", "")),
                evidence=evidence or "n/a",
            )
        )

    lines.extend(
        [
            "",
            "## Dashboard Evidence Hashes",
            "",
            "| Path | Status | Format | Bytes | SHA-256 |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for artifact in packet.get("review_artifacts", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Fixture Input Hashes",
            "",
            "| Case | Path | Status | Bytes | SHA-256 |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for fixture in packet.get("fixture_inputs", []):
        lines.append(_fixture_row(fixture))

    return "\n".join(lines) + "\n"


def write_public_review_walkthrough(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    packet = build_public_review_walkthrough(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_public_review_markdown(packet), encoding="utf-8")
    json_path.write_text(render_public_review_json(packet), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _fixture_entries(manifest: dict) -> list[dict]:
    entries = []
    sources = [
        {
            "case": "base-demo",
            "fixture_dir": manifest.get("fixtures", {}).get("directory", ""),
            "fixture_files": manifest.get("fixtures", {}).get("files", []),
        }
    ]
    sources.extend(
        sorted(
            manifest.get("templates", {}).get("templates", []),
            key=lambda item: item.get("slug", ""),
        )
    )
    for source in sources:
        case = source.get("case") or source.get("slug", "")
        fixture_dir = source.get("fixture_dir", "")
        for name in source.get("fixture_files", []):
            entries.append(_path_hash_entry(Path(fixture_dir) / name, case=case))
    return entries


def _artifact_entry(output_dir: Path, relative_path: str) -> dict:
    entry = _path_hash_entry(output_dir / relative_path, display_path=relative_path)
    entry["format"] = _format_from_path(relative_path)
    return entry


def _path_hash_entry(
    path: Path,
    display_path: str | None = None,
    case: str | None = None,
) -> dict:
    result = {
        "path": display_path or path.as_posix(),
        "status": "missing",
        "bytes": "n/a",
        "sha256": "n/a",
    }
    if case is not None:
        result["case"] = case
    if "*" in path.as_posix():
        matches = sorted(candidate for candidate in path.parent.glob(path.name) if candidate.is_file())
        content = b"".join(candidate.read_bytes() for candidate in matches)
        if content:
            result.update(
                {
                    "status": "present",
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        return result
    if path.is_file():
        content = path.read_bytes()
        result.update(
            {
                "status": "present",
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return result


def _artifact_row(entry: dict) -> str:
    return "| {path} | {status} | {format} | {bytes} | `{sha256}` |".format(
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        format=_table_cell(entry.get("format", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


def _fixture_row(entry: dict) -> str:
    return "| {case} | {path} | {status} | {bytes} | `{sha256}` |".format(
        case=_table_cell(entry.get("case", "")),
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))


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
