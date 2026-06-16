"""Scenario evidence receipt for static portfolio review artifacts."""

from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT

DEFAULT_SCENARIO_EVIDENCE_MARKDOWN = "scenario_evidence_receipt.md"
DEFAULT_SCENARIO_EVIDENCE_JSON = "scenario_evidence_receipt.json"

BASE_REVIEW_ARTIFACTS = (
    "stress.json",
    "stress.md",
    "guardrails.json",
    "guardrails.md",
    "dashboard.html",
    "dashboard_preview.md",
    "dashboard_snippet.html",
    "gallery.md",
    "walkthrough.md",
    "walkthrough.json",
)
TEMPLATE_REVIEW_ARTIFACTS = (
    "stress.json",
    "stress.md",
    "guardrails.json",
    "guardrails.md",
)
SCENARIO_FIXTURES = ("holdings.csv", "config.json", "scenario.json")
PUBLIC_SAFETY_NOTICE = (
    "Audit receipt only; not investment advice, trading guidance, live market "
    "data, broker connectivity, account access, order entry, or trade execution."
)
REVIEW_SCOPE_TEXT = (
    "Hashes static fixture inputs and generated local review artifacts. Missing "
    "sidecar artifacts are reported as missing and are not fetched from external "
    "services."
)


def build_scenario_evidence_receipt(
    manifest: dict,
    output_dir: Path,
) -> dict:
    """Build deterministic evidence tying scenario artifacts to static fixtures."""

    cases = [_case_entry("base-demo", manifest["fixtures"]["directory"], "", output_dir)]
    for template in sorted(
        manifest.get("templates", {}).get("templates", []),
        key=lambda item: item.get("slug", ""),
    ):
        cases.append(
            _case_entry(
                template.get("slug", "template"),
                template.get("fixture_dir", ""),
                template.get("output_prefix", ""),
                output_dir,
                template=True,
            )
        )

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-scenario-evidence-receipt",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "public_safety_notice": PUBLIC_SAFETY_NOTICE,
        "review_scope": REVIEW_SCOPE_TEXT,
        "prohibited_capabilities": [
            "broker_connection",
            "live_market_data",
            "account_access",
            "order_entry",
            "trade_execution",
            "portfolio_recommendations",
            "investment_advice",
        ],
        "allowed_inputs": [
            "static holdings CSV fixtures",
            "static config JSON fixtures",
            "static scenario JSON fixtures",
            "generated local artifacts",
        ],
        "cases": cases,
        "regeneration_commands": [
            "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
            "PYTHONPATH=src python -m portfolio_risk_compass guardrails examples/fixtures/holdings.csv --config examples/fixtures/config.json --snapshot-date 2026-05-15 --json examples/outputs/guardrails.json --markdown examples/outputs/guardrails.md",
            "PYTHONPATH=src python -m portfolio_risk_compass stress examples/fixtures/holdings.csv examples/fixtures/scenario.json --json examples/outputs/stress.json --markdown examples/outputs/stress.md",
            "PYTHONPATH=src python -m portfolio_risk_compass dashboard examples/outputs/index.json examples/outputs/dashboard.html",
            "PYTHONPATH=src python -m portfolio_risk_compass scenario-evidence-receipt",
        ],
    }


def render_scenario_evidence_json(receipt: dict) -> str:
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def render_scenario_evidence_markdown(receipt: dict) -> str:
    lines = [
        "# Portfolio Risk Compass Scenario Evidence Receipt",
        "",
        "Deterministic receipt for static scenario, guardrail, and dashboard review artifacts.",
        "",
        f"Safety boundary: {receipt.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        f"Public safety notice: {receipt.get('public_safety_notice', PUBLIC_SAFETY_NOTICE)}",
        f"Review scope: {receipt.get('review_scope', REVIEW_SCOPE_TEXT)}",
        "",
        "## Boundaries",
        "",
    ]
    for capability in receipt.get("prohibited_capabilities", []):
        lines.append(f"- No {_table_cell(capability).replace('_', ' ')}")

    lines.extend(["", "## Regeneration Commands", ""])
    for command in receipt.get("regeneration_commands", []):
        lines.append(f"- `{command}`")

    for case in receipt.get("cases", []):
        lines.extend(
            [
                "",
                f"## Case: {_table_cell(case.get('case', ''))}",
                "",
                f"- Fixture directory: `{_table_cell(case.get('fixture_dir', ''))}`",
                f"- Output prefix: `{_table_cell(case.get('output_prefix', ''))}`",
                "",
                "### Fixture Hashes",
                "",
                "| Path | Status | Bytes | SHA-256 |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for fixture in case.get("fixtures", []):
            lines.append(_hash_row(fixture))
        lines.extend(
            [
                "",
                "### Artifact Hashes",
                "",
                "| Path | Status | Format | Bytes | SHA-256 |",
                "| --- | --- | --- | ---: | --- |",
            ]
        )
        for artifact in case.get("artifacts", []):
            lines.append(_artifact_row(artifact))

    return "\n".join(lines) + "\n"


def write_scenario_evidence_receipt(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    receipt = build_scenario_evidence_receipt(manifest, manifest_json.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        render_scenario_evidence_markdown(receipt),
        encoding="utf-8",
    )
    json_path.write_text(render_scenario_evidence_json(receipt), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _case_entry(
    case: str,
    fixture_dir: str,
    output_prefix: str,
    output_dir: Path,
    template: bool = False,
) -> dict:
    artifact_names = TEMPLATE_REVIEW_ARTIFACTS if template else BASE_REVIEW_ARTIFACTS
    return {
        "case": case,
        "fixture_dir": fixture_dir,
        "output_prefix": output_prefix,
        "fixtures": [
            _path_hash_entry(path)
            for name in SCENARIO_FIXTURES
            for path in [Path(fixture_dir) / name]
        ],
        "artifacts": [
            _artifact_hash_entry(output_dir, output_prefix + name)
            for name in artifact_names
        ],
    }


def _artifact_hash_entry(output_dir: Path, relative_path: str) -> dict:
    entry = _path_hash_entry(output_dir / relative_path, display_path=relative_path)
    entry["format"] = _format_from_path(relative_path)
    return entry


def _path_hash_entry(path: Path, display_path: str | None = None) -> dict:
    if any(char in path.as_posix() for char in "*?["):
        matches = sorted(Path(match) for match in glob.glob(path.as_posix()))
        content = b"".join(match.read_bytes() for match in matches if match.is_file())
        return {
            "path": display_path or path.as_posix(),
            "status": "present" if content else "missing",
            "bytes": len(content) if content else "n/a",
            "sha256": hashlib.sha256(content).hexdigest() if content else "n/a",
        }
    if not path.is_file():
        return {
            "path": display_path or path.as_posix(),
            "status": "missing",
            "bytes": "n/a",
            "sha256": "n/a",
        }
    content = path.read_bytes()
    return {
        "path": display_path or path.as_posix(),
        "status": "present",
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _hash_row(entry: dict) -> str:
    return "| {path} | {status} | {bytes} | `{sha256}` |".format(
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


def _artifact_row(entry: dict) -> str:
    return "| {path} | {status} | {format} | {bytes} | `{sha256}` |".format(
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        format=_table_cell(entry.get("format", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


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
