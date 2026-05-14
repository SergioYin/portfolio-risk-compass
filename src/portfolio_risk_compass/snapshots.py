"""Portfolio snapshot persistence and comparison."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from uuid import uuid4

MONEY_QUANT = Decimal("0.01")
PCT_QUANT = Decimal("0.0001")


def build_snapshot(
    report: dict, snapshot_date: str | None = None, snapshot_id: str | None = None
) -> dict:
    """Return a serializable snapshot for an analyzed report."""

    return {
        "snapshot": {
            "id": snapshot_id or uuid4().hex,
            "date": snapshot_date or date.today().isoformat(),
        },
        "report": report,
    }


def write_snapshot(path: Path, snapshot: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_snapshot_json(snapshot), encoding="utf-8")


def read_snapshot(path: Path) -> dict:
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid snapshot JSON {path}: {exc}") from exc
    _validate_snapshot(snapshot, path)
    return snapshot


def render_snapshot_json(snapshot: dict) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True) + "\n"


def diff_snapshots(before: dict, after: dict) -> dict:
    """Compare two snapshots and return deterministic deltas."""

    before_report = before["report"]
    after_report = after["report"]
    return {
        "from": before["snapshot"],
        "to": after["snapshot"],
        "total_market_value": _total_value_diff(before_report, after_report),
        "allocation_buckets": _allocation_bucket_diff(before_report, after_report),
        "concentration": _concentration_diff(before_report, after_report),
        "target_drift": _target_drift_diff(before_report, after_report),
    }


def render_diff_markdown(diff: dict) -> str:
    lines = [
        "# Portfolio Snapshot Diff",
        "",
        f"- From: {diff['from']['id']} ({diff['from']['date']})",
        f"- To: {diff['to']['id']} ({diff['to']['date']})",
        "",
        "## Total Value",
        "",
        "| From | To | Change | Change % |",
        "| ---: | ---: | ---: | ---: |",
    ]
    total = diff["total_market_value"]
    lines.append(
        f"| {total['from']} | {total['to']} | {total['change']} | {total['change_pct']}% |"
    )
    lines.append("")

    for group, rows in diff["allocation_buckets"].items():
        title = group.replace("_", " ").title()
        lines.extend(
            [
                f"## Allocation by {title}",
                "",
                "| Bucket | From value | To value | Value change | From % | To % | Pct point change |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['bucket']} | {row['from_market_value']} | {row['to_market_value']} | "
                f"{row['market_value_change']} | {row['from_pct']}% | {row['to_pct']}% | "
                f"{row['pct_point_change']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Concentration",
            "",
            "| Symbol | Status | From value | To value | Value change | From % | To % | Pct point change |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    if diff["concentration"]:
        for row in diff["concentration"]:
            lines.append(
                f"| {row['symbol']} | {row['status']} | {row['from_market_value']} | "
                f"{row['to_market_value']} | {row['market_value_change']} | "
                f"{row['from_pct']}% | {row['to_pct']}% | {row['pct_point_change']} |"
            )
    else:
        lines.append("| None | unchanged | 0.00 | 0.00 | 0.00 | 0.0000% | 0.0000% | 0.0000 |")
    lines.append("")

    for group, rows in diff["target_drift"].items():
        title = group.replace("_", " ").title()
        lines.extend(
            [
                f"## Target Drift by {title}",
                "",
                "| Bucket | From drift % | To drift % | Pct point change |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['bucket']} | {row['from_drift_pct']}% | "
                f"{row['to_drift_pct']}% | {row['pct_point_change']} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _validate_snapshot(snapshot: object, path: Path) -> None:
    if not isinstance(snapshot, dict):
        raise ValueError(f"snapshot JSON {path} must be an object")
    if not isinstance(snapshot.get("snapshot"), dict):
        raise ValueError(f"snapshot JSON {path} is missing snapshot metadata")
    if not isinstance(snapshot.get("report"), dict):
        raise ValueError(f"snapshot JSON {path} is missing report data")
    metadata = snapshot["snapshot"]
    if not metadata.get("id") or not metadata.get("date"):
        raise ValueError(f"snapshot JSON {path} requires snapshot id and date")


def _total_value_diff(before_report: dict, after_report: dict) -> dict:
    before_value = _decimal(before_report["metadata"]["total_market_value"])
    after_value = _decimal(after_report["metadata"]["total_market_value"])
    change = after_value - before_value
    return {
        "from": _format_money(before_value),
        "to": _format_money(after_value),
        "change": _format_money(change),
        "change_pct": _format_pct(_pct(change, before_value)),
    }


def _allocation_bucket_diff(
    before_report: dict, after_report: dict
) -> dict[str, list[dict]]:
    groups = sorted(
        set(before_report.get("exposures", {})) | set(after_report.get("exposures", {}))
    )
    return {
        group: _bucket_rows(
            _rows_by_key(before_report.get("exposures", {}).get(group, []), "bucket"),
            _rows_by_key(after_report.get("exposures", {}).get(group, []), "bucket"),
        )
        for group in groups
    }


def _bucket_rows(before_rows: dict[str, dict], after_rows: dict[str, dict]) -> list[dict]:
    rows = []
    for bucket in sorted(set(before_rows) | set(after_rows)):
        before = before_rows.get(bucket, {})
        after = after_rows.get(bucket, {})
        before_value = _decimal(before.get("market_value", "0"))
        after_value = _decimal(after.get("market_value", "0"))
        before_pct = _decimal(before.get("pct_of_portfolio", "0"))
        after_pct = _decimal(after.get("pct_of_portfolio", "0"))
        rows.append(
            {
                "bucket": bucket,
                "from_market_value": _format_money(before_value),
                "to_market_value": _format_money(after_value),
                "market_value_change": _format_money(after_value - before_value),
                "from_pct": _format_pct(before_pct),
                "to_pct": _format_pct(after_pct),
                "pct_point_change": _format_pct(after_pct - before_pct),
            }
        )
    return rows


def _concentration_diff(before_report: dict, after_report: dict) -> list[dict]:
    before_rows = _rows_by_key(before_report.get("concentration", []), "symbol")
    after_rows = _rows_by_key(after_report.get("concentration", []), "symbol")
    rows = []
    for symbol in sorted(set(before_rows) | set(after_rows)):
        before = before_rows.get(symbol, {})
        after = after_rows.get(symbol, {})
        before_value = _decimal(before.get("market_value", "0"))
        after_value = _decimal(after.get("market_value", "0"))
        before_pct = _decimal(before.get("pct_of_portfolio", "0"))
        after_pct = _decimal(after.get("pct_of_portfolio", "0"))
        rows.append(
            {
                "symbol": symbol,
                "status": _status(symbol, before_rows, after_rows, before, after),
                "from_market_value": _format_money(before_value),
                "to_market_value": _format_money(after_value),
                "market_value_change": _format_money(after_value - before_value),
                "from_pct": _format_pct(before_pct),
                "to_pct": _format_pct(after_pct),
                "pct_point_change": _format_pct(after_pct - before_pct),
            }
        )
    return rows


def _target_drift_diff(before_report: dict, after_report: dict) -> dict[str, list[dict]]:
    groups = sorted(
        set(before_report.get("target_drift", {}))
        | set(after_report.get("target_drift", {}))
    )
    return {
        group: _target_drift_rows(
            _rows_by_key(before_report.get("target_drift", {}).get(group, []), "bucket"),
            _rows_by_key(after_report.get("target_drift", {}).get(group, []), "bucket"),
        )
        for group in groups
    }


def _target_drift_rows(
    before_rows: dict[str, dict], after_rows: dict[str, dict]
) -> list[dict]:
    rows = []
    for bucket in sorted(set(before_rows) | set(after_rows)):
        before_drift = _decimal(before_rows.get(bucket, {}).get("drift_pct", "0"))
        after_drift = _decimal(after_rows.get(bucket, {}).get("drift_pct", "0"))
        rows.append(
            {
                "bucket": bucket,
                "from_drift_pct": _format_pct(before_drift),
                "to_drift_pct": _format_pct(after_drift),
                "pct_point_change": _format_pct(after_drift - before_drift),
            }
        )
    return rows


def _rows_by_key(rows: list[dict], key: str) -> dict[str, dict]:
    return {row[key]: row for row in rows}


def _status(
    key: str,
    before_rows: dict[str, dict],
    after_rows: dict[str, dict],
    before: dict,
    after: dict,
) -> str:
    if key in before_rows and key in after_rows:
        if before == after:
            return "unchanged"
        return "changed"
    if key in after_rows:
        return "added"
    return "removed"


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def _pct(value: Decimal, base: Decimal) -> Decimal:
    if base == 0:
        return Decimal("0")
    return (value / base) * Decimal("100")


def _format_money(value: Decimal) -> str:
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _format_pct(value: Decimal) -> str:
    return str(value.quantize(PCT_QUANT, rounding=ROUND_HALF_UP))
