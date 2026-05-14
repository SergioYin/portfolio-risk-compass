"""Catalyst calendar parsing and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path


REQUIRED_FIELDS = ("symbol", "date", "title", "importance", "thesis_link", "action")


@dataclass(frozen=True)
class Catalyst:
    symbol: str
    date: date
    title: str
    importance: str
    thesis_link: str
    action: str


def read_catalysts_json(path: Path) -> list[Catalyst]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid catalysts JSON {path}: {exc}") from exc
    return parse_catalysts_payload(payload, source=str(path))


def parse_catalysts_payload(payload: object, source: str = "catalysts JSON") -> list[Catalyst]:
    if not isinstance(payload, list):
        raise ValueError(f"{source} must be a JSON array")

    catalysts = []
    for index, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{source} row {index} must be an object")
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            raise ValueError(f"{source} row {index} missing required field {missing[0]}")
        catalysts.append(_parse_catalyst(row, source, index))
    return catalysts


def build_catalyst_checklist(
    catalysts: list[Catalyst], as_of: str | date | None = None
) -> dict:
    as_of_date = _parse_date(as_of, "as_of") if isinstance(as_of, str) else as_of
    as_of_date = as_of_date or date.today()

    items = []
    for catalyst in sorted(catalysts, key=lambda item: (item.date, item.symbol, item.title)):
        days_from_as_of = (catalyst.date - as_of_date).days
        items.append(
            {
                "symbol": catalyst.symbol,
                "date": catalyst.date.isoformat(),
                "title": catalyst.title,
                "importance": catalyst.importance,
                "thesis_link": catalyst.thesis_link,
                "action": catalyst.action,
                "flag": _flag(days_from_as_of),
                "days_from_as_of": days_from_as_of,
            }
        )

    return {
        "metadata": {
            "as_of": as_of_date.isoformat(),
            "catalyst_count": len(items),
            "overdue_count": sum(1 for item in items if item["flag"] == "overdue"),
            "upcoming_count": sum(1 for item in items if item["flag"] == "upcoming"),
            "today_count": sum(1 for item in items if item["flag"] == "today"),
        },
        "catalysts": items,
    }


def render_catalyst_json(checklist: dict) -> str:
    return json.dumps(checklist, indent=2, sort_keys=True) + "\n"


def render_catalyst_markdown(checklist: dict) -> str:
    metadata = checklist["metadata"]
    lines = [
        "# Catalyst Checklist",
        "",
        f"- As of: {metadata['as_of']}",
        f"- Catalysts: {metadata['catalyst_count']}",
        f"- Overdue: {metadata['overdue_count']}",
        f"- Upcoming: {metadata['upcoming_count']}",
        f"- Today: {metadata['today_count']}",
        "",
    ]

    grouped = {
        "overdue": [item for item in checklist["catalysts"] if item["flag"] == "overdue"],
        "today": [item for item in checklist["catalysts"] if item["flag"] == "today"],
        "upcoming": [item for item in checklist["catalysts"] if item["flag"] == "upcoming"],
    }
    for flag, title in (("overdue", "Overdue"), ("today", "Today"), ("upcoming", "Upcoming")):
        lines.extend([f"## {title}", ""])
        if grouped[flag]:
            for item in grouped[flag]:
                lines.append(
                    f"- [ ] {item['date']} **{item['symbol']}** "
                    f"({item['importance']}) - {item['title']}"
                )
                lines.append(f"  Action: {item['action']}")
                lines.append(f"  Thesis: {item['thesis_link']}")
        else:
            lines.append("- None")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _parse_catalyst(row: dict, source: str, index: int) -> Catalyst:
    values = {}
    for field in REQUIRED_FIELDS:
        value = row[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{source} row {index} field {field} must be a non-empty string")
        values[field] = value.strip()

    return Catalyst(
        symbol=values["symbol"].upper(),
        date=_parse_date(values["date"], f"{source} row {index} date"),
        title=values["title"],
        importance=values["importance"],
        thesis_link=values["thesis_link"],
        action=values["action"],
    )


def _parse_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must use YYYY-MM-DD") from exc


def _flag(days_from_as_of: int) -> str:
    if days_from_as_of < 0:
        return "overdue"
    if days_from_as_of == 0:
        return "today"
    return "upcoming"
