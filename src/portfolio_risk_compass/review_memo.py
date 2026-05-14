"""Human review memo assembled from generated artifacts."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .rebalance_watchlist import SAFETY_WORDING

REQUIRED_ARTIFACTS = {
    "exposure": "exposure_report.json",
    "guardrails": "guardrails.json",
    "stress": "stress.json",
    "catalysts": "catalysts.json",
    "history": "history.json",
    "watchlist": "rebalance_watchlist.json",
}

NON_ADVICE_BOUNDARY = (
    "This memo is for human portfolio review and education only. It is not "
    "investment, tax, legal, accounting, or trading advice, and it does not "
    "recommend buying, selling, holding, position sizes, order types, account "
    "transfers, or timing."
)


def build_review_memo(outputs_dir: Path, title: str = "Portfolio Review Memo") -> dict:
    """Read generated JSON artifacts from a directory and return memo inputs."""

    artifacts = {
        name: _read_json(outputs_dir / filename)
        for name, filename in REQUIRED_ARTIFACTS.items()
    }
    return {
        "title": title,
        "outputs_dir": outputs_dir.as_posix(),
        "source_artifacts": {
            name: filename for name, filename in REQUIRED_ARTIFACTS.items()
        },
        "artifacts": artifacts,
        "assumptions": _assumptions(artifacts),
        "boundary": NON_ADVICE_BOUNDARY,
    }


def render_review_memo_markdown(memo: dict) -> str:
    artifacts = memo["artifacts"]
    exposure = artifacts["exposure"]
    guardrails = artifacts["guardrails"]
    stress = artifacts["stress"]
    catalysts = artifacts["catalysts"]
    history = artifacts["history"]
    watchlist = artifacts["watchlist"]

    exposure_meta = exposure["metadata"]
    guardrail_meta = guardrails["metadata"]
    stress_meta = stress["metadata"]
    catalyst_meta = catalysts["metadata"]
    history_trend = history["trends"]["total_market_value"]
    watchlist_meta = watchlist["metadata"]

    lines = [
        f"# {memo['title']}",
        "",
        f"Non-advice boundary: {memo['boundary']}",
        "",
        "## Source Artifacts",
        "",
        "| Artifact | Path |",
        "| --- | --- |",
    ]
    for name, path in memo["source_artifacts"].items():
        lines.append(f"| {name} | {path} |")

    lines.extend(
        [
            "",
            "## Executive Summary",
            "",
            f"- Portfolio value: {exposure_meta['total_market_value']} {exposure_meta['base_currency']}",
            f"- Holdings: {exposure_meta['holding_count']}",
            f"- Guardrail status: {guardrail_meta['overall_status']}",
            (
                "- Stress scenario: "
                f"{stress_meta['scenario_name']} moved portfolio value "
                f"{stress_meta['market_value_delta_pct']}% "
                f"({stress_meta['market_value_delta']})"
            ),
            (
                "- Watchlist items: "
                f"{watchlist_meta['item_count']} "
                f"(high {watchlist_meta['severity_counts']['high']}, "
                f"medium {watchlist_meta['severity_counts']['medium']}, "
                f"low {watchlist_meta['severity_counts']['low']})"
            ),
            (
                "- Catalysts: "
                f"{catalyst_meta['catalyst_count']} "
                f"(overdue {catalyst_meta['overdue_count']}, "
                f"today {catalyst_meta['today_count']}, "
                f"upcoming {catalyst_meta['upcoming_count']})"
            ),
            (
                "- History total value change: "
                f"{history_trend['change']} ({history_trend['change_pct']}%) "
                f"across {history['snapshot_count']} snapshot(s)"
            ),
            "",
            "## Exposure",
            "",
            "| Group | Bucket | Market value | Portfolio % |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for group in exposure_meta["group_by"]:
        for row in _top_rows(exposure["exposures"].get(group, []), 5):
            lines.append(
                f"| {group} | {row['bucket']} | {row['market_value']} | "
                f"{row['pct_of_portfolio']}% |"
            )

    lines.extend(["", "## Concentration", ""])
    if exposure["concentration"]:
        lines.extend(
            [
                "| Symbol | Market value | Portfolio % | Limit % |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for row in exposure["concentration"]:
            lines.append(
                f"| {row['symbol']} | {row['market_value']} | "
                f"{row['pct_of_portfolio']}% | {row['limit_pct']}% |"
            )
    else:
        lines.append("- No concentration items exceeded the configured limit.")

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "| Status | Check | Scope | Actual | Limit | Message |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in guardrails["items"]:
        lines.append(
            f"| {item['status']} | {item['check']} | {item['scope']} | "
            f"{item['actual']} | {item['limit']} | {item['message']} |"
        )
    if not guardrails["items"]:
        lines.append("| PASS | configured_checks | portfolio | 0 | 0 | No guardrails configured. |")

    lines.extend(
        [
            "",
            "## Stress",
            "",
            f"- Scenario: {stress_meta['scenario_name']}",
            f"- Base market value: {stress_meta['base_market_value']}",
            f"- Stressed market value: {stress_meta['stressed_market_value']}",
            f"- Market value delta: {stress_meta['market_value_delta']} ({stress_meta['market_value_delta_pct']}%)",
            "",
            "| Shock | Selector | Bucket | Price move % | Value delta |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in stress["shock_impacts"]:
        lines.append(
            f"| {row['name']} | {row['selector']} | {row['bucket']} | "
            f"{row['price_move_pct']}% | {row['market_value_delta']} |"
        )

    lines.extend(
        [
            "",
            "## Rebalance Watchlist",
            "",
            f"Safety boundary: {watchlist_meta.get('safety_wording', SAFETY_WORDING)}",
            "",
            "| Severity | Scope type | Scope | Reason codes | Evidence summary |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if watchlist["items"]:
        for item in watchlist["items"]:
            lines.append(
                f"| {item['severity']} | {item['scope_type']} | {item['scope']} | "
                f"{', '.join(item['reason_codes'])} | {item['evidence_summary']} |"
            )
    else:
        lines.append("| low | portfolio | portfolio | NONE | No review reasons were generated. |")

    lines.extend(
        [
            "",
            "## Catalysts",
            "",
            "| Date | Symbol | Flag | Importance | Title | Action |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if catalysts["catalysts"]:
        for item in catalysts["catalysts"]:
            lines.append(
                f"| {item['date']} | {item['symbol']} | {item['flag']} | "
                f"{item['importance']} | {item['title']} | {item['action']} |"
            )
    else:
        lines.append("| | | | | No catalysts provided. | |")

    lines.extend(
        [
            "",
            "## History",
            "",
            "| Date | Snapshot | Total value | Change | Change % |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in history["snapshots"]:
        total = row["total_market_value"]
        lines.append(
            f"| {row['date']} | {row['id']} | {total['value']} | "
            f"{total['change']} | {total['change_pct']}% |"
        )

    lines.extend(["", "## Assumptions", ""])
    for assumption in memo["assumptions"]:
        lines.append(f"- {assumption}")

    lines.extend(
        [
            "",
            "## Human Review Checklist",
            "",
            "- Confirm source artifacts were regenerated from the intended holdings, config, scenario, catalysts, and snapshot files.",
            "- Review WARN and FAIL guardrails against the documented portfolio policy.",
            "- Review high and medium watchlist items before considering any action outside this tool.",
            "- Treat stress results as deterministic scenario math, not forecasts.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"review memo missing required artifact: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid review memo artifact JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"review memo artifact must be a JSON object: {path}")
    return payload


def _assumptions(artifacts: dict) -> list[str]:
    stress = artifacts["stress"]["metadata"]
    catalysts = artifacts["catalysts"]["metadata"]
    return [
        "The memo uses precomputed JSON artifacts and does not recalculate holdings, prices, classifications, guardrails, scenarios, catalysts, or history.",
        "Market values, prices, target allocations, and classification fields are assumed to be correct as captured in the exposure artifact.",
        f"Stress results assume the named scenario '{stress['scenario_name']}' and its configured shock rules; they are not probability-weighted forecasts.",
        f"Catalyst timing is evaluated relative to {catalysts['as_of']}.",
        "The rebalance watchlist identifies review subjects only and intentionally omits trade instructions.",
    ]


def _top_rows(rows: list[dict], limit: int) -> list[dict]:
    return sorted(rows, key=lambda row: _decimal(row["pct_of_portfolio"]), reverse=True)[
        :limit
    ]


def _decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")
