"""Release-owner visual evidence checklist for static dashboard capture."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from .visual_capture_audit import (
    BOUNDARIES,
    DEFAULT_VISUAL_CAPTURE_AUDIT_JSON,
    build_visual_capture_audit,
)
from .visual_capture_compare import read_visual_capture_audit


SCHEMA_LABEL = "portfolio-risk-compass-visual-release-checklist.v1"

DEFAULT_VISUAL_RELEASE_CHECKLIST_JSON = "visual_release_checklist.json"
DEFAULT_VISUAL_RELEASE_CHECKLIST_MARKDOWN = "visual_release_checklist.md"

CHECKLIST_BOUNDARIES = {
    "scope": "release-owner readiness checklist for static dashboard/demo visual evidence",
    **BOUNDARIES,
    "no_private_data": "does not require, inspect, or emit private account data",
    "manual_review": "records readiness checks only; capture and release ownership remain human-reviewed",
}

READINESS_ITEMS = (
    (
        "static_dashboard_present",
        "Static dashboard route is present",
        ("dashboard.html",),
        "required",
        "Regenerate with the dashboard command from index.json.",
    ),
    (
        "public_gallery_present",
        "Public gallery landing page is present",
        ("gallery.html",),
        "required",
        "Regenerate with demo-bundle.",
    ),
    (
        "public_review_present",
        "Public review walkthrough is present",
        ("public_review_walkthrough.md", "public_review_walkthrough.json"),
        "required",
        "Regenerate with public-review.",
    ),
    (
        "screenshot_guide_present",
        "Screenshot capture guide is present",
        ("dashboard_screenshot_guide.md", "dashboard_screenshot_guide.json"),
        "required",
        "Regenerate with screenshot-guide.",
    ),
    (
        "visual_evidence_present",
        "Visual evidence receipt is present",
        ("visual_evidence_receipt.md", "visual_evidence_receipt.json"),
        "required",
        "Regenerate with visual-evidence-receipt.",
    ),
    (
        "demo_capture_present",
        "Demo capture receipt is present",
        ("demo_capture_receipt.md", "demo_capture_receipt.json"),
        "required",
        "Regenerate with demo-capture-receipt.",
    ),
    (
        "visual_capture_audit_present",
        "Visual capture audit artifacts are present",
        ("visual_capture_audit.md", "visual_capture_audit.json"),
        "required",
        "Regenerate with visual-capture-audit.",
    ),
    (
        "visual_capture_compare_present",
        "Release-to-release visual compare artifacts are present",
        ("visual_capture_compare.md", "visual_capture_compare.json"),
        "recommended",
        "Regenerate with visual-capture-compare.",
    ),
    (
        "release_manifest_present",
        "Release manifest includes current output inventory",
        ("release_manifest.md", "release_manifest.json"),
        "recommended",
        "Regenerate with release-manifest after visual checklist outputs are written.",
    ),
    (
        "docs_export_present",
        "Docs export includes current CLI and artifact reference",
        ("docs_export.md",),
        "recommended",
        "Regenerate with docs-export after release artifacts are refreshed.",
    ),
    (
        "dashboard_capture_image_present",
        "Dashboard screenshot capture image is present",
        ("screenshots/dashboard-public-review-1365x900.png",),
        "optional",
        "Capture with the command recorded in dashboard_screenshot_guide.md when screenshot evidence is required.",
    ),
)

OWNER_STEPS = (
    "Open gallery.html from the generated outputs directory.",
    "Open dashboard.html from the generated outputs directory.",
    "Run or inspect dashboard_screenshot_guide.md before capture.",
    "Confirm public-review, scenario, reviewer, visual, and demo capture receipts are present.",
    "Compare visual_capture_audit.json against the prior release audit when available.",
    "Regenerate release_manifest and docs_export after checklist outputs are refreshed.",
    "Run the repository selfcheck and privacy scan before publishing artifacts.",
)

REGENERATION_COMMANDS = (
    "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
    "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
    "PYTHONPATH=src python -m portfolio_risk_compass public-review",
    "PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt",
    "PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format json --output examples/outputs/visual_capture_audit.json",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format markdown --output examples/outputs/visual_capture_audit.md",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-compare --before examples/outputs/visual_capture_audit.json --after examples/outputs/visual_capture_audit.json --format json --output examples/outputs/visual_capture_compare.json",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-compare --before examples/outputs/visual_capture_audit.json --after examples/outputs/visual_capture_audit.json --format markdown --output examples/outputs/visual_capture_compare.md",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-release-checklist --root examples/outputs --format json --output examples/outputs/visual_release_checklist.json",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-release-checklist --root examples/outputs --format markdown --output examples/outputs/visual_release_checklist.md",
    "PYTHONPATH=src python -m portfolio_risk_compass release-manifest",
    "PYTHONPATH=src python -m portfolio_risk_compass docs-export",
)


def build_visual_release_checklist(root: Path, audit_path: Path | None = None) -> dict:
    """Build a deterministic release-owner visual evidence readiness checklist."""

    root = Path(root)
    audit = _load_or_build_audit(root, audit_path)
    artifacts = _artifact_map(root, audit)
    items = [
        _checklist_item(artifacts, key, title, paths, level, remediation)
        for key, title, paths, level, remediation in READINESS_ITEMS
    ]
    required = [item for item in items if item["level"] == "required"]
    missing_required = [item for item in required if item["status"] != "pass"]
    missing_recommended = [
        item for item in items if item["level"] == "recommended" and item["status"] != "pass"
    ]
    optional_missing = [
        item for item in items if item["level"] == "optional" and item["status"] != "pass"
    ]

    return {
        "schema": SCHEMA_LABEL,
        "artifact": "portfolio-risk-compass-visual-release-checklist",
        "root": audit.get("root", _public_root_label(root)),
        "audit_schema": audit.get("schema"),
        "scope": (
            "Deterministic release-owner checklist for static dashboard/demo visual "
            "capture readiness. It reads local artifact metadata only."
        ),
        "boundaries": CHECKLIST_BOUNDARIES,
        "summary": {
            "items": len(items),
            "required": len(required),
            "required_missing": len(missing_required),
            "recommended_missing": len(missing_recommended),
            "optional_missing": len(optional_missing),
            "ready_for_release_owner_review": len(missing_required) == 0,
            "audit_complete": bool(audit.get("summary", {}).get("complete", False)),
        },
        "checklist": items,
        "owner_steps": list(OWNER_STEPS),
        "regeneration_commands": list(REGENERATION_COMMANDS),
    }


def render_visual_release_checklist_json(checklist: dict) -> str:
    return json.dumps(checklist, indent=2, sort_keys=True) + "\n"


def render_visual_release_checklist_markdown(checklist: dict) -> str:
    summary = checklist.get("summary", {})
    lines = [
        "# Portfolio Risk Compass Visual Release Checklist",
        "",
        f"Schema: `{_table_cell(checklist.get('schema', SCHEMA_LABEL))}`",
        f"Root: `{_table_cell(checklist.get('root', ''))}`",
        f"Audit schema: `{_table_cell(checklist.get('audit_schema', 'unknown'))}`",
        f"Scope: {_table_cell(checklist.get('scope', ''))}",
        "",
        "## Boundaries",
        "",
    ]
    for key in sorted(checklist.get("boundaries", {})):
        lines.append(f"- {_table_cell(key).replace('_', ' ')}: {_table_cell(checklist['boundaries'][key])}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Items: {summary.get('items', 0)}",
            f"- Required: {summary.get('required', 0)}",
            f"- Required missing: {summary.get('required_missing', 0)}",
            f"- Recommended missing: {summary.get('recommended_missing', 0)}",
            f"- Optional missing: {summary.get('optional_missing', 0)}",
            f"- Ready for release-owner review: {str(summary.get('ready_for_release_owner_review', False)).lower()}",
            f"- Audit complete: {str(summary.get('audit_complete', False)).lower()}",
            "",
            "## Checklist",
            "",
            "| Key | Status | Level | Evidence | Missing | Remediation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in checklist.get("checklist", []):
        lines.append(
            "| {key} | {status} | {level} | {evidence} | {missing} | {remediation} |".format(
                key=_table_cell(item.get("key", "")),
                status=_table_cell(item.get("status", "")),
                level=_table_cell(item.get("level", "")),
                evidence=", ".join(_markdown_link(path) for path in item.get("evidence_paths", [])),
                missing=", ".join(_markdown_link(path) for path in item.get("missing_paths", [])) or "none",
                remediation=_table_cell(item.get("remediation", "")),
            )
        )

    lines.extend(["", "## Owner Steps", ""])
    for step in checklist.get("owner_steps", []):
        lines.append(f"- {_table_cell(step)}")

    lines.extend(["", "## Regeneration Commands", ""])
    for command in checklist.get("regeneration_commands", []):
        escaped_command = _table_cell(command).replace("`", "\\`")
        lines.append(f"- `{escaped_command}`")
    return "\n".join(lines) + "\n"


def write_visual_release_checklist(
    root: Path,
    output: Path,
    output_format: str,
    audit_path: Path | None = None,
) -> dict:
    checklist = build_visual_release_checklist(root, audit_path=audit_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        output.write_text(render_visual_release_checklist_markdown(checklist), encoding="utf-8")
    else:
        output.write_text(render_visual_release_checklist_json(checklist), encoding="utf-8")
    return checklist


def _load_or_build_audit(root: Path, audit_path: Path | None) -> dict:
    if audit_path is not None:
        return read_visual_capture_audit(audit_path)
    default_audit = root / DEFAULT_VISUAL_CAPTURE_AUDIT_JSON
    if default_audit.is_file():
        return read_visual_capture_audit(default_audit)
    return build_visual_capture_audit(root)


def _artifact_map(root: Path, audit: dict) -> dict[str, dict]:
    artifacts = {
        item["path"]: item
        for item in audit.get("checked_artifacts", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for _, _, paths, _, _ in READINESS_ITEMS:
        for path in paths:
            artifacts.setdefault(path, {"path": path, "present": (root / path).is_file()})
    return artifacts


def _checklist_item(
    artifacts: dict[str, dict],
    key: str,
    title: str,
    paths: tuple[str, ...],
    level: str,
    remediation: str,
) -> dict:
    missing = [path for path in paths if not bool(artifacts.get(path, {}).get("present", False))]
    evidence = [path for path in paths if path not in missing]
    return {
        "key": key,
        "title": title,
        "level": level,
        "status": "pass" if not missing else "missing",
        "evidence_paths": evidence,
        "missing_paths": missing,
        "remediation": "none" if not missing else remediation,
    }


def _public_root_label(root: Path) -> str:
    if root.is_absolute():
        return "<absolute-path>"
    value = root.as_posix()
    return value or "."


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
