"""Portfolio history ledger aggregation."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

from .snapshots import read_snapshot

MONEY_QUANT = Decimal("0.01")
PCT_QUANT = Decimal("0.0001")


def build_history_ledger(snapshots_dir: Path) -> dict:
    """Read snapshot JSON files from a directory and return trend data."""

    snapshot_paths = _snapshot_paths(snapshots_dir)
    entries = [_entry(path, read_snapshot(path)) for path in snapshot_paths]
    entries.sort(key=lambda item: (item["date"], item["id"], item["source_file"]))
    trends = {
        "total_market_value": _total_value_trend(entries),
        "exposure_drift": _exposure_drift_trend(entries),
        "guardrail_status": _guardrail_status_trend(entries),
        "catalyst_counts": _catalyst_count_trend(entries),
    }

    return {
        "schema_version": 1,
        "snapshot_directory": snapshots_dir.as_posix(),
        "snapshot_count": len(entries),
        "snapshots": entries,
        "trends": trends,
    }


def render_history_json(ledger: dict) -> str:
    return json.dumps(ledger, indent=2, sort_keys=True) + "\n"


def render_history_markdown(ledger: dict) -> str:
    lines = [
        "# Portfolio History Ledger",
        "",
        f"- Snapshot directory: {ledger['snapshot_directory']}",
        f"- Snapshots: {ledger['snapshot_count']}",
        "",
        "## Total Value",
        "",
        "| Date | Snapshot | Total value | Change | Change % |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in ledger["snapshots"]:
        total = row["total_market_value"]
        lines.append(
            f"| {row['date']} | {row['id']} | {total['value']} | "
            f"{total['change']} | {total['change_pct']}% |"
        )

    lines.extend(["", "## Exposure Drift", ""])
    drift = ledger["trends"]["exposure_drift"]
    if drift:
        lines.extend(
            [
                "| Group | Bucket | First drift % | Last drift % | Pct point change |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for group, rows in drift.items():
            for row in rows:
                lines.append(
                    f"| {group} | {row['bucket']} | {row['first_drift_pct']}% | "
                    f"{row['last_drift_pct']}% | {row['pct_point_change']} |"
                )
    else:
        lines.append("- No target drift data found.")

    guardrails = ledger["trends"]["guardrail_status"]
    lines.extend(["", "## Guardrails", ""])
    if guardrails:
        lines.extend(
            [
                "| Date | Snapshot | Overall | PASS | WARN | FAIL |",
                "| --- | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for row in guardrails:
            lines.append(
                f"| {row['date']} | {row['id']} | {row['overall_status']} | "
                f"{row['pass_count']} | {row['warn_count']} | {row['fail_count']} |"
            )
    else:
        lines.append("- No guardrail data found.")

    catalysts = ledger["trends"]["catalyst_counts"]
    lines.extend(["", "## Catalysts", ""])
    if catalysts:
        lines.extend(
            [
                "| Date | Snapshot | Total | Overdue | Today | Upcoming |",
                "| --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in catalysts:
            lines.append(
                f"| {row['date']} | {row['id']} | {row['catalyst_count']} | "
                f"{row['overdue_count']} | {row['today_count']} | {row['upcoming_count']} |"
            )
    else:
        lines.append("- No catalyst data found.")

    return "\n".join(lines).rstrip() + "\n"


def _snapshot_paths(snapshots_dir: Path) -> list[Path]:
    if not snapshots_dir.exists():
        raise ValueError(f"history directory does not exist: {snapshots_dir}")
    if not snapshots_dir.is_dir():
        raise ValueError(f"history path must be a directory: {snapshots_dir}")
    paths = sorted(path for path in snapshots_dir.iterdir() if path.suffix == ".json")
    if not paths:
        raise ValueError(f"history directory has no snapshot JSON files: {snapshots_dir}")
    return paths


def _entry(path: Path, snapshot: dict) -> dict:
    report = snapshot["report"]
    metadata = snapshot["snapshot"]
    total_value = _decimal(report["metadata"]["total_market_value"])
    return {
        "id": metadata["id"],
        "date": metadata["date"],
        "source_file": path.name,
        "total_market_value": {
            "value": _format_money(total_value),
            "change": "0.00",
            "change_pct": "0.0000",
        },
        "exposure_drift": _snapshot_drift(report),
        "guardrails": _guardrail_summary(snapshot),
        "catalysts": _catalyst_summary(snapshot),
    }


def _total_value_trend(entries: list[dict]) -> dict:
    previous_value = None
    for entry in entries:
        value = _decimal(entry["total_market_value"]["value"])
        if previous_value is not None:
            change = value - previous_value
            entry["total_market_value"]["change"] = _format_money(change)
            entry["total_market_value"]["change_pct"] = _format_pct(
                _pct(change, previous_value)
            )
        previous_value = value

    first = _decimal(entries[0]["total_market_value"]["value"])
    last = _decimal(entries[-1]["total_market_value"]["value"])
    change = last - first
    return {
        "first": _format_money(first),
        "last": _format_money(last),
        "change": _format_money(change),
        "change_pct": _format_pct(_pct(change, first)),
    }


def _snapshot_drift(report: dict) -> dict[str, list[dict]]:
    groups = {}
    for group, rows in sorted(report.get("target_drift", {}).items()):
        groups[group] = [
            {
                "bucket": row["bucket"],
                "actual_pct": _format_pct(_decimal(row.get("actual_pct", "0"))),
                "target_pct": _format_pct(_decimal(row.get("target_pct", "0"))),
                "drift_pct": _format_pct(_decimal(row.get("drift_pct", "0"))),
            }
            for row in sorted(rows, key=lambda item: item["bucket"])
        ]
    return groups


def _exposure_drift_trend(entries: list[dict]) -> dict[str, list[dict]]:
    groups = sorted(
        {
            group
            for entry in entries
            for group in entry["exposure_drift"]
        }
    )
    trends = {}
    for group in groups:
        buckets = sorted(
            {
                row["bucket"]
                for entry in entries
                for row in entry["exposure_drift"].get(group, [])
            }
        )
        rows = []
        for bucket in buckets:
            first = _drift_for_bucket(entries[0], group, bucket)
            last = _drift_for_bucket(entries[-1], group, bucket)
            rows.append(
                {
                    "bucket": bucket,
                    "first_drift_pct": _format_pct(first),
                    "last_drift_pct": _format_pct(last),
                    "pct_point_change": _format_pct(last - first),
                }
            )
        trends[group] = rows
    return trends


def _drift_for_bucket(entry: dict, group: str, bucket: str) -> Decimal:
    for row in entry["exposure_drift"].get(group, []):
        if row["bucket"] == bucket:
            return _decimal(row["drift_pct"])
    return Decimal("0")


def _guardrail_summary(snapshot: dict) -> dict | None:
    review = snapshot.get("guardrails") or snapshot.get("guardrail_review")
    if not isinstance(review, dict):
        return None
    metadata = review.get("metadata", {})
    items = review.get("items", [])
    if not isinstance(items, list):
        items = []
    return {
        "overall_status": metadata.get("overall_status", "UNKNOWN"),
        "pass_count": _status_count(items, "PASS"),
        "warn_count": _status_count(items, "WARN"),
        "fail_count": _status_count(items, "FAIL"),
        "configured_checks": metadata.get("configured_checks", len(items)),
    }


def _guardrail_status_trend(entries: list[dict]) -> list[dict]:
    rows = []
    for entry in entries:
        guardrails = entry["guardrails"]
        if guardrails is None:
            continue
        rows.append({"date": entry["date"], "id": entry["id"], **guardrails})
    return rows


def _status_count(items: list[dict], status: str) -> int:
    return sum(1 for item in items if item.get("status") == status)


def _catalyst_summary(snapshot: dict) -> dict | None:
    checklist = snapshot.get("catalysts") or snapshot.get("catalyst_checklist")
    if not isinstance(checklist, dict):
        return None
    metadata = checklist.get("metadata", {})
    return {
        "catalyst_count": int(metadata.get("catalyst_count", 0)),
        "overdue_count": int(metadata.get("overdue_count", 0)),
        "today_count": int(metadata.get("today_count", 0)),
        "upcoming_count": int(metadata.get("upcoming_count", 0)),
    }


def _catalyst_count_trend(entries: list[dict]) -> list[dict]:
    rows = []
    for entry in entries:
        catalysts = entry["catalysts"]
        if catalysts is None:
            continue
        rows.append({"date": entry["date"], "id": entry["id"], **catalysts})
    return rows


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
