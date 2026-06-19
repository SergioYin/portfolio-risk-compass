"""Public demo capture receipt and evidence index."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT
from .public_review import BOUNDARY_FLAGS
from .scenario_evidence import PUBLIC_SAFETY_NOTICE
from .screenshot_guide import DEFAULT_SCREENSHOT_PATH

DEFAULT_DEMO_CAPTURE_RECEIPT_MARKDOWN = "demo_capture_receipt.md"
DEFAULT_DEMO_CAPTURE_RECEIPT_JSON = "demo_capture_receipt.json"

CAPTURE_EVIDENCE_ARTIFACTS = (
    ("static_dashboard_route", "dashboard.html", "Static portfolio dashboard route used for public demo capture."),
    ("dashboard_capture_slot", DEFAULT_SCREENSHOT_PATH, "Expected screenshot path produced by the screenshot guide command."),
    ("dashboard_screenshot_guide", "dashboard_screenshot_guide.md", "Human-readable dashboard screenshot capture instructions and hash receipt."),
    ("dashboard_screenshot_guide_packet", "dashboard_screenshot_guide.json", "Machine-readable dashboard screenshot capture profile and artifact hashes."),
    ("visual_evidence_receipt", "visual_evidence_receipt.md", "Human-readable visual evidence route for the static dashboard review."),
    ("visual_evidence_receipt_packet", "visual_evidence_receipt.json", "Machine-readable visual evidence route and artifact hashes."),
    ("public_review_walkthrough", "public_review_walkthrough.md", "Human-readable public review walkthrough and rerun commands."),
    ("public_review_walkthrough_packet", "public_review_walkthrough.json", "Machine-readable public review packet."),
    ("scenario_evidence_receipt", "scenario_evidence_receipt.md", "Human-readable static scenario, guardrail, and dashboard receipt."),
    ("scenario_evidence_receipt_packet", "scenario_evidence_receipt.json", "Machine-readable scenario evidence receipt."),
    ("reviewer_evidence", "reviewer_evidence.md", "Human-readable reviewer evidence trace to fixtures and generated artifacts."),
    ("reviewer_evidence_packet", "reviewer_evidence.json", "Machine-readable reviewer evidence trace."),
    ("dashboard_preview", "dashboard_preview.md", "Text preview of the static dashboard for review notes."),
)

PROHIBITED_CAPABILITIES = (
    "broker_connection",
    "live_market_data",
    "account_access",
    "order_entry",
    "trade_execution",
    "position_sizing",
    "portfolio_recommendations",
    "investment_advice",
)


def build_demo_capture_receipt(manifest: dict, output_dir: Path) -> dict:
    """Build a deterministic public demo capture evidence index."""

    artifacts = [
        _artifact_entry(output_dir, path, role, purpose)
        for role, path, purpose in CAPTURE_EVIDENCE_ARTIFACTS
    ]
    screenshot_guide = _read_optional_json(output_dir / "dashboard_screenshot_guide.json")
    profile = screenshot_guide.get("capture_profile", {})

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-demo-capture-receipt",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "public_safety_notice": PUBLIC_SAFETY_NOTICE,
        "boundary_flags": {
            **BOUNDARY_FLAGS,
            "orders": "none; no order entry, execution, or broker workflow is present",
            "position_sizing": "none; output records evidence only and does not size positions",
            "recommendations": "none; output is an evidence index, not portfolio recommendations",
        },
        "prohibited_capabilities": list(PROHIBITED_CAPABILITIES),
        "review_scope": (
            "Public-safe static demo capture receipt for generated local artifacts. "
            "It indexes dashboard screenshot/capture evidence and hashes existing "
            "review receipts without fetching data, connecting to brokers, sizing "
            "positions, placing orders, or providing recommendations or advice."
        ),
        "capture_profile": {
            "browser": profile.get("browser", "chromium"),
            "viewport_width": profile.get("viewport_width", 1365),
            "viewport_height": profile.get("viewport_height", 900),
            "full_page": profile.get("full_page", False),
            "input_url": profile.get("input_url", "dashboard.html"),
            "output_path": profile.get(
                "output_path",
                (output_dir / DEFAULT_SCREENSHOT_PATH).as_posix(),
            ),
        },
        "evidence_index": [
            _evidence_item(
                "capture_instructions",
                ("dashboard_screenshot_guide.md", "dashboard_screenshot_guide.json"),
                ("exact dashboard capture command", "viewport and browser profile", "screenshot output path"),
            ),
            _evidence_item(
                "visual_route",
                ("visual_evidence_receipt.md", "visual_evidence_receipt.json"),
                ("static dashboard route", "public review link", "scenario and reviewer evidence links"),
            ),
            _evidence_item(
                "public_review",
                ("public_review_walkthrough.md", "public_review_walkthrough.json"),
                ("rerun commands", "fixture hashes", "public-safe review boundaries"),
            ),
            _evidence_item(
                "scenario_receipt",
                ("scenario_evidence_receipt.md", "scenario_evidence_receipt.json"),
                ("static scenario fixture hashes", "stress and guardrail artifact hashes", "prohibited capability list"),
            ),
            _evidence_item(
                "reviewer_evidence",
                ("reviewer_evidence.md", "reviewer_evidence.json"),
                ("fixture lineage", "generated artifact coverage", "reviewer export path"),
            ),
        ],
        "artifacts": artifacts,
        "screenshot_artifacts": screenshot_guide.get("screenshot_artifacts", []),
        "artifact_coverage": _coverage(artifacts),
        "regeneration_commands": [
            "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
            "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
            "PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide",
            "PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt",
            "PYTHONPATH=src python -m portfolio_risk_compass demo-capture-receipt",
        ],
    }


def render_demo_capture_receipt_json(receipt: dict) -> str:
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def render_demo_capture_receipt_markdown(receipt: dict) -> str:
    coverage = receipt.get("artifact_coverage", {})
    profile = receipt.get("capture_profile", {})
    lines = [
        "# Portfolio Risk Compass Demo Capture Receipt",
        "",
        "Deterministic public demo capture receipt and evidence index for the static portfolio dashboard.",
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
    for capability in receipt.get("prohibited_capabilities", []):
        lines.append(f"- Prohibited: {_table_cell(capability).replace('_', ' ')}")

    lines.extend(
        [
            "",
            "## Capture Profile",
            "",
            f"- Browser: `{_table_cell(profile.get('browser', ''))}`",
            f"- Viewport: `{_table_cell(profile.get('viewport_width', ''))}x{_table_cell(profile.get('viewport_height', ''))}`",
            f"- Full page: `{str(profile.get('full_page', False)).lower()}`",
            f"- Input URL: `{_table_cell(profile.get('input_url', ''))}`",
            f"- Output path: `{_table_cell(profile.get('output_path', ''))}`",
            "",
            "## Evidence Index",
            "",
            "| Label | Artifacts | Verifies |",
            "| --- | --- | --- |",
        ]
    )
    for item in receipt.get("evidence_index", []):
        lines.append(
            "| {label} | {artifacts} | {verifies} |".format(
                label=_table_cell(item.get("label", "")),
                artifacts=", ".join(_markdown_link(path) for path in item.get("artifacts", [])),
                verifies=", ".join(_table_cell(value) for value in item.get("verifies", [])),
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
            + (", ".join(_code_span(path) for path in coverage.get("missing", [])) or "none"),
            "",
            "## Regeneration Commands",
            "",
        ]
    )
    for command in receipt.get("regeneration_commands", []):
        lines.append(f"- `{command}`")
    return "\n".join(lines) + "\n"


def write_demo_capture_receipt(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    receipt = build_demo_capture_receipt(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_demo_capture_receipt_markdown(receipt), encoding="utf-8")
    json_path.write_text(render_demo_capture_receipt_json(receipt), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _evidence_item(label: str, artifacts: tuple[str, ...], verifies: tuple[str, ...]) -> dict:
    return {"label": label, "artifacts": list(artifacts), "verifies": list(verifies)}


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
        result.update({"status": "present", "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    return result


def _coverage(artifacts: list[dict]) -> dict:
    present_count = sum(1 for item in artifacts if item["status"] == "present")
    return {
        "present": present_count,
        "expected": len(artifacts),
        "complete": present_count == len(artifacts),
        "missing": [item["path"] for item in artifacts if item["status"] != "present"],
    }


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
    if suffix == ".png":
        return "png"
    return suffix.lstrip(".") or "unknown"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return _read_json(path)


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))
