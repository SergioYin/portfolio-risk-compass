"""Visual evidence receipt tying static dashboard review artifacts together."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT
from .public_review import BOUNDARY_FLAGS
from .scenario_evidence import PUBLIC_SAFETY_NOTICE

DEFAULT_VISUAL_EVIDENCE_MARKDOWN = "visual_evidence_receipt.md"
DEFAULT_VISUAL_EVIDENCE_JSON = "visual_evidence_receipt.json"

VISUAL_EVIDENCE_ARTIFACTS = (
    {
        "role": "static_dashboard",
        "path": "dashboard.html",
        "purpose": "Self-contained no-JavaScript dashboard for visual review.",
    },
    {
        "role": "dashboard_preview",
        "path": "dashboard_preview.md",
        "purpose": "Text preview of the dashboard for release notes and reviewers.",
    },
    {
        "role": "dashboard_snippet",
        "path": "dashboard_snippet.html",
        "purpose": "Small static HTML route into the dashboard and walkthrough.",
    },
    {
        "role": "public_review_walkthrough",
        "path": "public_review_walkthrough.md",
        "purpose": "Public reviewer walkthrough with rerun commands and hashes.",
    },
    {
        "role": "public_review_packet",
        "path": "public_review_walkthrough.json",
        "purpose": "Machine-readable public-review packet.",
    },
    {
        "role": "dashboard_screenshot_guide",
        "path": "dashboard_screenshot_guide.json",
        "purpose": "Exact public dashboard screenshot capture instructions and hashes.",
    },
    {
        "role": "scenario_evidence_receipt",
        "path": "scenario_evidence_receipt.json",
        "purpose": "Scenario, guardrail, and dashboard evidence hashes.",
    },
    {
        "role": "reviewer_evidence_export",
        "path": "reviewer_evidence.json",
        "purpose": "Reviewer evidence export linking generated artifacts to fixtures.",
    },
)


def build_visual_evidence_receipt(manifest: dict, output_dir: Path) -> dict:
    """Build a deterministic visual-review receipt from generated local artifacts."""

    route = [
        {
            "step": 1,
            "label": "dashboard",
            "artifact": "dashboard.html",
            "verifies": [
                "static visual summary",
                "no JavaScript dashboard export",
                "broker-free review boundary",
            ],
        },
        {
            "step": 2,
            "label": "public_review",
            "artifact": "public_review_walkthrough.md",
            "verifies": [
                "public reviewer rerun path",
                "no-live-data boundary",
                "no-advice boundary",
            ],
        },
        {
            "step": 3,
            "label": "screenshot_guide",
            "artifact": "dashboard_screenshot_guide.md",
            "verifies": [
                "exact dashboard screenshot command",
                "capture viewport",
                "screenshot hash receipt path",
            ],
        },
        {
            "step": 4,
            "label": "scenario_evidence",
            "artifact": "scenario_evidence_receipt.json",
            "verifies": [
                "scenario fixture hashes",
                "stress and guardrail artifact hashes",
                "prohibited capability list",
            ],
        },
        {
            "step": 5,
            "label": "reviewer_evidence",
            "artifact": "reviewer_evidence.json",
            "verifies": [
                "reviewer export path",
                "fixture lineage",
                "generated artifact coverage",
            ],
        },
    ]
    artifacts = [
        _artifact_entry(output_dir, item["path"], item["role"], item["purpose"])
        for item in VISUAL_EVIDENCE_ARTIFACTS
    ]
    present_count = sum(1 for item in artifacts if item["status"] == "present")

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-visual-evidence-receipt",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "public_safety_notice": PUBLIC_SAFETY_NOTICE,
        "boundary_flags": BOUNDARY_FLAGS,
        "review_scope": (
            "Visual evidence route for static local dashboard artifacts only. "
            "The receipt does not fetch data, connect to brokers, or provide advice."
        ),
        "route": route,
        "artifacts": artifacts,
        "artifact_coverage": {
            "present": present_count,
            "expected": len(artifacts),
            "complete": present_count == len(artifacts),
            "missing": [
                item["path"] for item in artifacts if item["status"] != "present"
            ],
        },
        "regeneration_commands": [
            "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
            "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
            "PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence",
            "PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt",
            "PYTHONPATH=src python -m portfolio_risk_compass public-review",
            "PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide",
            "PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt",
        ],
    }


def render_visual_evidence_json(receipt: dict) -> str:
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def render_visual_evidence_markdown(receipt: dict) -> str:
    coverage = receipt.get("artifact_coverage", {})
    lines = [
        "# Portfolio Risk Compass Visual Evidence Receipt",
        "",
        "Deterministic route tying the static dashboard to public-review, scenario, and reviewer evidence artifacts.",
        "",
        f"Safety boundary: {receipt.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        f"Public safety notice: {receipt.get('public_safety_notice', PUBLIC_SAFETY_NOTICE)}",
        f"Review scope: {receipt.get('review_scope', '')}",
        "",
        "## Boundaries",
        "",
    ]
    for key, value in receipt.get("boundary_flags", {}).items():
        lines.append(f"- No {_table_cell(key).replace('_', ' ')}: {_table_cell(value)}")

    lines.extend(
        [
            "",
            "## Route",
            "",
            "| Step | Label | Artifact | Verifies |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for step in receipt.get("route", []):
        lines.append(
            "| {step} | {label} | {artifact} | {verifies} |".format(
                step=_table_cell(step.get("step", "")),
                label=_table_cell(step.get("label", "")),
                artifact=_markdown_link(step.get("artifact", "")),
                verifies=", ".join(
                    _table_cell(item) for item in step.get("verifies", [])
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Artifact Hashes",
            "",
            "| Role | Path | Status | Format | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for artifact in receipt.get("artifacts", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- Present: {coverage.get('present', 0)} of {coverage.get('expected', 0)}",
            f"- Complete: {str(coverage.get('complete', False)).lower()}",
            "- Missing: "
            + (
                ", ".join(_code_span(path) for path in coverage.get("missing", []))
                or "none"
            ),
            "",
            "## Regeneration Commands",
            "",
        ]
    )
    for command in receipt.get("regeneration_commands", []):
        lines.append(f"- `{command}`")
    return "\n".join(lines) + "\n"


def write_visual_evidence_receipt(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    receipt = build_visual_evidence_receipt(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_visual_evidence_markdown(receipt), encoding="utf-8")
    json_path.write_text(render_visual_evidence_json(receipt), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _artifact_entry(output_dir: Path, relative_path: str, role: str, purpose: str) -> dict:
    path = output_dir / relative_path
    result = {
        "role": role,
        "path": relative_path,
        "purpose": purpose,
        "status": "missing",
        "format": _format_from_path(relative_path),
        "bytes": "n/a",
        "sha256": "n/a",
    }
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
    return "| {role} | {path} | {status} | {format} | {bytes} | `{sha256}` |".format(
        role=_table_cell(entry.get("role", "")),
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        format=_table_cell(entry.get("format", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


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
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))
