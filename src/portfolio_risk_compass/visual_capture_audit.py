"""Static visual/demo capture artifact audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote


SCHEMA_LABEL = "portfolio-risk-compass-visual-capture-audit.v1"

DEFAULT_VISUAL_CAPTURE_AUDIT_JSON = "visual_capture_audit.json"
DEFAULT_VISUAL_CAPTURE_AUDIT_MARKDOWN = "visual_capture_audit.md"

BOUNDARIES = {
    "no_live_data": "does not fetch or require live market data",
    "no_broker": "does not connect to brokers or accounts",
    "no_orders": "does not place, route, stage, or recommend orders",
    "no_position_sizing": "does not calculate trade quantities or position sizing",
    "no_recommendations": "does not recommend portfolio actions",
    "no_file_contents": "does not embed artifact contents; records relative paths, byte counts, and SHA-256 hashes only",
    "no_advice": "public finance-research artifact audit only; not investment advice",
}

CHECKED_ARTIFACTS = (
    ("static_dashboard", "dashboard.html", "Regenerate with the dashboard command from index.json."),
    ("dashboard_preview", "dashboard_preview.md", "Regenerate with demo-bundle."),
    ("dashboard_snippet", "dashboard_snippet.html", "Regenerate with demo-bundle."),
    ("public_review_walkthrough", "public_review_walkthrough.md", "Regenerate with public-review."),
    ("public_review_packet", "public_review_walkthrough.json", "Regenerate with public-review."),
    ("dashboard_screenshot_guide", "dashboard_screenshot_guide.md", "Regenerate with screenshot-guide."),
    ("dashboard_screenshot_guide_packet", "dashboard_screenshot_guide.json", "Regenerate with screenshot-guide."),
    ("visual_evidence_receipt", "visual_evidence_receipt.md", "Regenerate with visual-evidence-receipt."),
    ("visual_evidence_receipt_packet", "visual_evidence_receipt.json", "Regenerate with visual-evidence-receipt."),
    ("demo_capture_receipt", "demo_capture_receipt.md", "Regenerate with demo-capture-receipt."),
    ("demo_capture_receipt_packet", "demo_capture_receipt.json", "Regenerate with demo-capture-receipt."),
    ("scenario_evidence_receipt", "scenario_evidence_receipt.md", "Regenerate with scenario-evidence-receipt."),
    ("scenario_evidence_receipt_packet", "scenario_evidence_receipt.json", "Regenerate with scenario-evidence-receipt."),
    ("reviewer_evidence", "reviewer_evidence.md", "Regenerate with reviewer-evidence."),
    ("reviewer_evidence_packet", "reviewer_evidence.json", "Regenerate with reviewer-evidence."),
    ("gallery", "gallery.md", "Regenerate with demo-bundle."),
    ("demo_manifest", "index.json", "Regenerate with demo-bundle."),
    (
        "dashboard_capture_image",
        "screenshots/dashboard-public-review-1365x900.png",
        "Capture with the command recorded in dashboard_screenshot_guide.md.",
    ),
)

REGENERATION_COMMANDS = (
    "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
    "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
    "PYTHONPATH=src python -m portfolio_risk_compass reviewer-evidence",
    "PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt",
    "PYTHONPATH=src python -m portfolio_risk_compass public-review",
    "PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt",
    "PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format json --output examples/outputs/visual_capture_audit.json",
    "PYTHONPATH=src python -m portfolio_risk_compass visual-capture-audit --root examples/outputs --format markdown --output examples/outputs/visual_capture_audit.md",
)

SOURCE_ARTIFACTS = (
    "index.json",
    "dashboard_screenshot_guide.md",
    "dashboard_screenshot_guide.json",
    "visual_evidence_receipt.json",
    "demo_capture_receipt.json",
    "public_review_walkthrough.json",
)


def build_visual_capture_audit(root: Path) -> dict:
    """Build a deterministic audit of static visual and demo capture artifacts."""

    root = Path(root)
    artifacts = [_artifact_entry(root, role, path, note) for role, path, note in CHECKED_ARTIFACTS]
    missing = [item for item in artifacts if not item["present"]]
    present = len(artifacts) - len(missing)
    recommended = [_recommended_item(item) for item in missing]

    return {
        "schema": SCHEMA_LABEL,
        "artifact": "portfolio-risk-compass-visual-capture-audit",
        "root": _public_root_label(root),
        "scope": (
            "Deterministic audit of existing static visual/demo evidence artifacts. "
            "The audit reads local files only and identifies capture gaps."
        ),
        "boundaries": BOUNDARIES,
        "summary": {
            "checked": len(artifacts),
            "present": present,
            "missing": len(missing),
            "complete": len(missing) == 0,
            "recommended_capture_items": len(recommended),
        },
        "checked_artifacts": artifacts,
        "missing": [item["path"] for item in missing],
        "recommended_capture_items": recommended,
        "source_artifacts": [_source_entry(root, path) for path in SOURCE_ARTIFACTS],
        "regeneration_commands": list(REGENERATION_COMMANDS),
    }


def render_visual_capture_audit_json(audit: dict) -> str:
    return json.dumps(audit, indent=2, sort_keys=True) + "\n"


def render_visual_capture_audit_markdown(audit: dict) -> str:
    summary = audit.get("summary", {})
    lines = [
        "# Portfolio Risk Compass Visual Capture Audit",
        "",
        f"Schema: `{_table_cell(audit.get('schema', SCHEMA_LABEL))}`",
        f"Root: `{_table_cell(audit.get('root', ''))}`",
        f"Scope: {_table_cell(audit.get('scope', ''))}",
        "",
        "## Boundaries",
        "",
    ]
    for key in sorted(audit.get("boundaries", {})):
        lines.append(f"- {_table_cell(key).replace('_', ' ')}: {_table_cell(audit['boundaries'][key])}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Checked: {summary.get('checked', 0)}",
            f"- Present: {summary.get('present', 0)}",
            f"- Missing: {summary.get('missing', 0)}",
            f"- Complete: {str(summary.get('complete', False)).lower()}",
            f"- Recommended capture items: {summary.get('recommended_capture_items', 0)}",
            "",
            "## Checked Artifacts",
            "",
            "| Role | Path | Present | Bytes | SHA-256 |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for item in audit.get("checked_artifacts", []):
        lines.append(
            "| {role} | {path} | {present} | {bytes} | {sha256} |".format(
                role=_table_cell(item.get("role", "")),
                path=_markdown_link(item.get("path", "")),
                present=str(bool(item.get("present", False))).lower(),
                bytes=_table_cell(_display_bytes(item.get("bytes"))),
                sha256=_code_span(item["sha256"]) if item.get("sha256") else "n/a",
            )
        )

    lines.extend(["", "## Recommended Capture Items", ""])
    recommended = audit.get("recommended_capture_items", [])
    if recommended:
        lines.extend(["| Path | Role | Reason | Regenerate |", "| --- | --- | --- | --- |"])
        for item in recommended:
            lines.append(
                "| {path} | {role} | {reason} | {regenerate} |".format(
                    path=_markdown_link(item.get("path", "")),
                    role=_table_cell(item.get("role", "")),
                    reason=_table_cell(item.get("reason", "")),
                    regenerate=_table_cell(item.get("regenerate", "")),
                )
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            "| Path | Present | Bytes | SHA-256 |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for item in audit.get("source_artifacts", []):
        lines.append(
            "| {path} | {present} | {bytes} | {sha256} |".format(
                path=_markdown_link(item.get("path", "")),
                present=str(bool(item.get("present", False))).lower(),
                bytes=_table_cell(_display_bytes(item.get("bytes"))),
                sha256=_code_span(item["sha256"]) if item.get("sha256") else "n/a",
            )
        )

    lines.extend(["", "## Regeneration Commands", ""])
    for command in audit.get("regeneration_commands", []):
        escaped_command = _table_cell(command).replace("`", "\\`")
        lines.append(f"- `{escaped_command}`")
    return "\n".join(lines) + "\n"


def write_visual_capture_audit(root: Path, output: Path, output_format: str) -> dict:
    audit = build_visual_capture_audit(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        output.write_text(render_visual_capture_audit_markdown(audit), encoding="utf-8")
    else:
        output.write_text(render_visual_capture_audit_json(audit), encoding="utf-8")
    return audit


def _artifact_entry(root: Path, role: str, relative_path: str, note: str) -> dict:
    path = root / relative_path
    result = {
        "path": relative_path,
        "present": False,
        "bytes": None,
        "sha256": None,
        "role": role,
        "regenerate": note,
    }
    if path.is_file():
        content = path.read_bytes()
        result.update(
            {
                "present": True,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return result


def _source_entry(root: Path, relative_path: str) -> dict:
    entry = _artifact_entry(root, "source_artifact", relative_path, "")
    del entry["regenerate"]
    return entry


def _recommended_item(artifact: dict) -> dict:
    return {
        "path": artifact["path"],
        "role": artifact["role"],
        "reason": "missing static visual/demo evidence artifact",
        "regenerate": artifact["regenerate"],
    }


def _public_root_label(root: Path) -> str:
    if root.is_absolute():
        return "<absolute-path>"
    value = root.as_posix()
    return value or "."


def _display_bytes(value: object) -> object:
    return "n/a" if value is None else value


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))
