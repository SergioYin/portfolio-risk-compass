"""Optional artifact adapter exports for adjacent local tools."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

INTEGRATION_PROFILES = ("invest-thesis-ledger", "leveraged-etp-risk-lab")

_ARTIFACT_FILENAMES = (
    "exposure_report.json",
    "guardrails.json",
    "stress.json",
    "catalysts.json",
)


def build_integration_export(outputs_dir: Path, profile: str) -> dict:
    """Build a deterministic JSON adapter payload from output artifacts."""

    if profile not in INTEGRATION_PROFILES:
        raise ValueError(f"unsupported integration profile: {profile}")

    artifacts = _read_artifacts(outputs_dir)
    payload_builders = {
        "invest-thesis-ledger": _build_invest_thesis_payload,
        "leveraged-etp-risk-lab": _build_leveraged_etp_payload,
    }
    return {
        "schema_version": 1,
        "adapter": "portfolio-risk-compass.integration-export",
        "profile": profile,
        "source_package": "portfolio-risk-compass",
        "source_artifacts": _source_artifact_entries(outputs_dir),
        "payload": payload_builders[profile](artifacts),
    }


def render_integration_export_json(export: dict) -> str:
    return json.dumps(export, indent=2, sort_keys=True) + "\n"


def write_integration_export(outputs_dir: Path, profile: str, output_json: Path) -> dict:
    export = build_integration_export(outputs_dir, profile)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(render_integration_export_json(export), encoding="utf-8")
    return export


def _read_artifacts(outputs_dir: Path) -> dict[str, dict]:
    artifacts = {}
    for filename in _ARTIFACT_FILENAMES:
        path = outputs_dir / filename
        if path.exists():
            artifacts[filename] = json.loads(path.read_text(encoding="utf-8"))
    return artifacts


def _source_artifact_entries(outputs_dir: Path) -> list[dict]:
    entries = []
    for filename in _ARTIFACT_FILENAMES:
        path = outputs_dir / filename
        if path.exists():
            content = path.read_bytes()
            entries.append(
                {
                    "path": filename,
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    return entries


def _build_invest_thesis_payload(artifacts: dict[str, dict]) -> dict:
    exposure = artifacts.get("exposure_report.json", {})
    guardrails = artifacts.get("guardrails.json", {})
    catalysts = artifacts.get("catalysts.json", {})

    concentration = exposure.get("concentration", [])
    risk_flags = [
        {
            "status": item.get("status", ""),
            "check": item.get("check", ""),
            "scope": item.get("scope", ""),
            "actual": item.get("actual", ""),
            "limit": item.get("limit", ""),
            "message": item.get("message", ""),
        }
        for item in guardrails.get("items", [])
        if item.get("status") != "PASS"
    ]
    thesis_review_items = [
        {
            "symbol": item.get("symbol", ""),
            "catalyst_date": item.get("date", ""),
            "title": item.get("title", ""),
            "importance": item.get("importance", ""),
            "flag": item.get("flag", ""),
            "days_from_as_of": item.get("days_from_as_of", 0),
            "thesis_link": item.get("thesis_link", ""),
            "action": item.get("action", ""),
        }
        for item in catalysts.get("catalysts", [])
    ]

    return {
        "portfolio_context": {
            "base_currency": exposure.get("metadata", {}).get("base_currency", ""),
            "total_market_value": exposure.get("metadata", {}).get(
                "total_market_value", ""
            ),
            "overall_guardrail_status": guardrails.get("metadata", {}).get(
                "overall_status", ""
            ),
            "concentration_symbols": [
                item.get("symbol", "") for item in concentration
            ],
        },
        "risk_flags": risk_flags,
        "thesis_review_items": thesis_review_items,
    }


def _build_leveraged_etp_payload(artifacts: dict[str, dict]) -> dict:
    exposure = artifacts.get("exposure_report.json", {})
    guardrails = artifacts.get("guardrails.json", {})
    stress = artifacts.get("stress.json", {})

    leverage_guardrails = [
        {
            "status": item.get("status", ""),
            "scope": item.get("scope", ""),
            "actual": item.get("actual", ""),
            "limit": item.get("limit", ""),
            "message": item.get("message", ""),
        }
        for item in guardrails.get("items", [])
        if item.get("check") == "max_leverage_multiple"
    ]
    stressed_holdings = [
        {
            "symbol": item.get("symbol", ""),
            "base_market_value": item.get("base_market_value", ""),
            "stressed_market_value": item.get("stressed_market_value", ""),
            "market_value_delta": item.get("market_value_delta", ""),
            "total_price_move_pct": item.get("total_price_move_pct", ""),
            "shock_names": [shock.get("name", "") for shock in item.get("shocks", [])],
        }
        for item in stress.get("holdings", [])
    ]

    return {
        "portfolio_stress_summary": stress.get("metadata", {}),
        "asset_class_exposures": exposure.get("exposures", {}).get("asset_class", []),
        "leverage_guardrails": leverage_guardrails,
        "shock_impacts": stress.get("shock_impacts", []),
        "stressed_holdings": stressed_holdings,
    }
