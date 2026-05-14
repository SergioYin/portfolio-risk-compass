"""Educational rebalance review watchlist."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json

SAFETY_WORDING = (
    "Educational portfolio review only. This watchlist does not recommend "
    "trades, order types, position quantities, account transfers, or timing. "
    "Use it to decide what deserves human review against your own policy."
)

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_rebalance_watchlist(
    exposure_report: dict,
    guardrail_review: dict,
    stress_report: dict,
) -> dict:
    """Combine exposure, guardrail, and stress outputs into review subjects."""

    items: dict[tuple[str, str], dict] = {}

    for row in exposure_report.get("concentration", []):
        pct = _decimal(row.get("pct_of_portfolio"))
        limit = _decimal(row.get("limit_pct"))
        severity = "high" if limit > 0 and pct >= limit * Decimal("1.25") else "medium"
        _add_reason(
            items,
            scope_type="holding",
            scope=row.get("symbol", ""),
            severity=severity,
            code="CONCENTRATION_LIMIT",
            evidence={
                "portfolio_pct": row.get("pct_of_portfolio", ""),
                "limit_pct": row.get("limit_pct", ""),
                "market_value": row.get("market_value", ""),
            },
        )

    for group, rows in sorted(exposure_report.get("target_drift", {}).items()):
        for row in rows:
            drift = _decimal(row.get("drift_pct"))
            if drift == 0:
                continue
            abs_drift = abs(drift)
            if abs_drift >= Decimal("10"):
                severity = "high"
            elif abs_drift >= Decimal("5"):
                severity = "medium"
            else:
                severity = "low"
            _add_reason(
                items,
                scope_type=group,
                scope=row.get("bucket", ""),
                severity=severity,
                code="TARGET_DRIFT",
                evidence={
                    "actual_pct": row.get("actual_pct", ""),
                    "target_pct": row.get("target_pct", ""),
                    "drift_pct": row.get("drift_pct", ""),
                },
            )

    for item in guardrail_review.get("items", []):
        status = item.get("status")
        if status == "PASS":
            continue
        severity = "high" if status == "FAIL" else "medium"
        check = item.get("check", "")
        scope = item.get("scope", "")
        _add_reason(
            items,
            scope_type=_guardrail_scope_type(check),
            scope=scope,
            severity=severity,
            code=f"GUARDRAIL_{status}",
            evidence={
                "check": check,
                "status": status,
                "actual": item.get("actual", ""),
                "limit": item.get("limit", ""),
                "message": item.get("message", ""),
            },
        )

    metadata = stress_report.get("metadata", {})
    portfolio_drawdown = _decimal(metadata.get("market_value_delta_pct"))
    if portfolio_drawdown < 0:
        _add_reason(
            items,
            scope_type="portfolio",
            scope="portfolio",
            severity=_drawdown_severity(portfolio_drawdown),
            code="STRESS_PORTFOLIO_DRAWDOWN",
            evidence={
                "scenario": metadata.get("scenario_name", ""),
                "market_value_delta_pct": metadata.get("market_value_delta_pct", ""),
                "market_value_delta": metadata.get("market_value_delta", ""),
            },
        )

    for row in stress_report.get("holdings", []):
        move = _decimal(row.get("total_price_move_pct"))
        if move >= 0:
            continue
        _add_reason(
            items,
            scope_type="holding",
            scope=row.get("symbol", ""),
            severity=_drawdown_severity(move),
            code="STRESS_DRAWDOWN",
            evidence={
                "scenario": metadata.get("scenario_name", ""),
                "total_price_move_pct": row.get("total_price_move_pct", ""),
                "market_value_delta": row.get("market_value_delta", ""),
                "matched_shocks": [shock.get("name", "") for shock in row.get("shocks", [])],
            },
        )

    rows = [_finalize_item(item) for item in items.values()]
    rows.sort(
        key=lambda item: (
            SEVERITY_ORDER[item["severity"]],
            item["scope_type"],
            item["scope"],
        )
    )
    severity_counts = {
        severity: sum(1 for item in rows if item["severity"] == severity)
        for severity in ("high", "medium", "low")
    }
    return {
        "metadata": {
            "schema_version": 1,
            "review_type": "broker_free_rebalance_watchlist",
            "safety_wording": SAFETY_WORDING,
            "item_count": len(rows),
            "severity_counts": severity_counts,
            "source_artifacts": [
                "exposure_report",
                "guardrail_review",
                "stress_report",
            ],
        },
        "items": rows,
    }


def render_rebalance_watchlist_json(watchlist: dict) -> str:
    return json.dumps(watchlist, indent=2, sort_keys=True) + "\n"


def render_rebalance_watchlist_markdown(watchlist: dict) -> str:
    metadata = watchlist["metadata"]
    lines = [
        "# Rebalance Review Watchlist",
        "",
        f"Safety boundary: {metadata['safety_wording']}",
        "",
        f"- Items: {metadata['item_count']}",
        (
            "- Severity counts: "
            f"high {metadata['severity_counts']['high']}, "
            f"medium {metadata['severity_counts']['medium']}, "
            f"low {metadata['severity_counts']['low']}"
        ),
        "",
        "| Severity | Scope type | Scope | Reason codes | Evidence summary | Review prompt |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if not watchlist["items"]:
        lines.append(
            "| low | portfolio | portfolio | NONE | No review reasons were generated. | Continue scheduled policy review. |"
        )
    for item in watchlist["items"]:
        lines.append(
            f"| {item['severity']} | {item['scope_type']} | {item['scope']} | "
            f"{', '.join(item['reason_codes'])} | {item['evidence_summary']} | "
            f"{item['educational_review_prompt']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _add_reason(
    items: dict[tuple[str, str], dict],
    scope_type: str,
    scope: object,
    severity: str,
    code: str,
    evidence: dict,
) -> None:
    clean_scope_type = str(scope_type or "portfolio")
    clean_scope = str(scope or "portfolio")
    key = (clean_scope_type, clean_scope)
    item = items.setdefault(
        key,
        {
            "scope_type": clean_scope_type,
            "scope": clean_scope,
            "severity": severity,
            "reason_codes": [],
            "evidence": [],
        },
    )
    if SEVERITY_ORDER[severity] < SEVERITY_ORDER[item["severity"]]:
        item["severity"] = severity
    if code not in item["reason_codes"]:
        item["reason_codes"].append(code)
    item["evidence"].append({"reason_code": code, **evidence})


def _finalize_item(item: dict) -> dict:
    item["reason_codes"].sort()
    item["evidence_summary"] = _evidence_summary(item)
    item["educational_review_prompt"] = _review_prompt(item)
    return item


def _evidence_summary(item: dict) -> str:
    summaries = []
    for evidence in item["evidence"]:
        code = evidence["reason_code"]
        if code == "CONCENTRATION_LIMIT":
            summaries.append(
                "concentration {portfolio_pct}% vs limit {limit_pct}%".format(**evidence)
            )
        elif code == "TARGET_DRIFT":
            summaries.append(
                "drift {drift_pct}% vs target {target_pct}%".format(**evidence)
            )
        elif code.startswith("GUARDRAIL_"):
            summaries.append(
                "{check} {status}: actual {actual}, limit {limit}".format(**evidence)
            )
        elif code == "STRESS_PORTFOLIO_DRAWDOWN":
            summaries.append(
                "{scenario} portfolio stress {market_value_delta_pct}%".format(**evidence)
            )
        elif code == "STRESS_DRAWDOWN":
            summaries.append(
                "{scenario} stress move {total_price_move_pct}%".format(**evidence)
            )
    return "; ".join(summaries)


def _review_prompt(item: dict) -> str:
    scope = item["scope"]
    scope_type = item["scope_type"].replace("_", " ")
    if item["scope_type"] == "portfolio":
        subject = "the portfolio"
    else:
        subject = f"{scope_type} {scope}"
    return (
        f"Review whether {subject} still fits the documented allocation, "
        "risk, liquidity, and time-horizon policy before taking any action."
    )


def _guardrail_scope_type(check: str) -> str:
    if check == "max_position_pct":
        return "holding"
    if check == "max_sector_pct":
        return "sector"
    if check == "min_cash_pct":
        return "asset_class"
    return "portfolio"


def _drawdown_severity(value: Decimal) -> str:
    if value <= Decimal("-15"):
        return "high"
    if value <= Decimal("-7.5"):
        return "medium"
    return "low"


def _decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")
