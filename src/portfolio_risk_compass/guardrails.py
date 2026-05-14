"""Portfolio guardrail policy checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
from typing import Iterable

from .config import AnalysisConfig
from .holdings import Holding

PCT_QUANT = Decimal("0.0001")
MULTIPLE_QUANT = Decimal("0.0001")
WARN_RATIO = Decimal("0.90")


@dataclass(frozen=True)
class ReviewDates:
    snapshot_date: date | None = None
    last_review_date: date | None = None


def evaluate_guardrails(
    holdings: Iterable[Holding],
    config: AnalysisConfig,
    review_dates: ReviewDates | None = None,
) -> dict:
    holdings_list = list(holdings)
    dates = review_dates or ReviewDates()
    snapshot_date = dates.snapshot_date or date.today()
    last_review_date = dates.last_review_date or config.last_review_date
    total_value = sum((holding.market_value for holding in holdings_list), Decimal("0"))

    items = []
    if config.max_position_pct is not None:
        items.extend(_position_items(holdings_list, total_value, config.max_position_pct))
    if config.max_sector_pct is not None:
        items.extend(_sector_items(holdings_list, total_value, config.max_sector_pct))
    if config.min_cash_pct is not None:
        items.append(_cash_item(holdings_list, total_value, config.min_cash_pct))
    if config.max_leverage_multiple is not None:
        items.append(
            _leverage_item(holdings_list, total_value, config.max_leverage_multiple)
        )
    if config.required_review_cadence_days is not None:
        items.append(
            _review_cadence_item(
                snapshot_date,
                last_review_date,
                config.required_review_cadence_days,
            )
        )

    return {
        "metadata": {
            "snapshot_date": snapshot_date.isoformat(),
            "last_review_date": (
                last_review_date.isoformat() if last_review_date is not None else None
            ),
            "configured_checks": len(items),
            "overall_status": _overall_status(items),
        },
        "items": items,
    }


def render_guardrail_json(review: dict) -> str:
    return json.dumps(review, indent=2, sort_keys=True) + "\n"


def render_guardrail_markdown(review: dict) -> str:
    metadata = review["metadata"]
    lines = [
        "# Portfolio Guardrail Review",
        "",
        f"- Snapshot date: {metadata['snapshot_date']}",
        f"- Last review date: {metadata['last_review_date'] or 'Not provided'}",
        f"- Overall status: {metadata['overall_status']}",
        "",
        "| Status | Check | Actual | Limit | Message |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for item in review["items"]:
        lines.append(
            f"| {item['status']} | {item['check']} | {item['actual']} | "
            f"{item['limit']} | {item['message']} |"
        )
    if not review["items"]:
        lines.append("| PASS | configured_checks | 0 | 0 | No guardrails configured. |")
    return "\n".join(lines).rstrip() + "\n"


def parse_review_date(value: str | None, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc


def _position_items(
    holdings: list[Holding], total_value: Decimal, limit_pct: Decimal
) -> list[dict]:
    rows = []
    for holding in sorted(holdings, key=lambda item: item.symbol):
        actual_pct = _pct(holding.market_value, total_value)
        rows.append(
            _threshold_item(
                "max_position_pct",
                holding.symbol,
                actual_pct,
                limit_pct,
                "max",
                f"{holding.symbol} is {_format_pct(actual_pct)}% of portfolio.",
            )
        )
    return rows


def _sector_items(
    holdings: list[Holding], total_value: Decimal, limit_pct: Decimal
) -> list[dict]:
    sectors: dict[str, Decimal] = {}
    for holding in holdings:
        sectors[holding.sector] = sectors.get(holding.sector, Decimal("0")) + holding.market_value

    return [
        _threshold_item(
            "max_sector_pct",
            sector,
            _pct(value, total_value),
            limit_pct,
            "max",
            f"{sector} sector is {_format_pct(_pct(value, total_value))}% of portfolio.",
        )
        for sector, value in sorted(sectors.items())
    ]


def _cash_item(
    holdings: list[Holding], total_value: Decimal, limit_pct: Decimal
) -> dict:
    cash_value = sum(
        (
            holding.market_value
            for holding in holdings
            if holding.asset_class.casefold() == "cash"
            or holding.symbol.casefold() == "cash"
        ),
        Decimal("0"),
    )
    actual_pct = _pct(cash_value, total_value)
    return _threshold_item(
        "min_cash_pct",
        "Cash",
        actual_pct,
        limit_pct,
        "min",
        f"Cash is {_format_pct(actual_pct)}% of portfolio.",
    )


def _leverage_item(
    holdings: list[Holding], total_value: Decimal, limit_multiple: Decimal
) -> dict:
    gross_value = sum((abs(holding.market_value) for holding in holdings), Decimal("0"))
    actual_multiple = Decimal("0") if total_value == 0 else gross_value / total_value
    status = _max_status(actual_multiple, limit_multiple)
    return {
        "status": status,
        "check": "max_leverage_multiple",
        "scope": "portfolio",
        "actual": _format_multiple(actual_multiple),
        "limit": _format_multiple(limit_multiple),
        "message": f"Gross exposure is {_format_multiple(actual_multiple)}x net value.",
    }


def _review_cadence_item(
    snapshot_date: date, last_review_date: date | None, cadence_days: int
) -> dict:
    if last_review_date is None:
        return {
            "status": "WARN",
            "check": "required_review_cadence_days",
            "scope": "portfolio",
            "actual": "unknown",
            "limit": str(cadence_days),
            "message": "Last review date was not provided.",
        }

    days_since_review = (snapshot_date - last_review_date).days
    status = _max_status(Decimal(days_since_review), Decimal(cadence_days))
    return {
        "status": status,
        "check": "required_review_cadence_days",
        "scope": "portfolio",
        "actual": str(days_since_review),
        "limit": str(cadence_days),
        "message": f"Last review was {days_since_review} day(s) before snapshot.",
    }


def _threshold_item(
    check: str,
    scope: str,
    actual: Decimal,
    limit: Decimal,
    direction: str,
    message: str,
) -> dict:
    status = _max_status(actual, limit) if direction == "max" else _min_status(actual, limit)
    return {
        "status": status,
        "check": check,
        "scope": scope,
        "actual": _format_pct(actual),
        "limit": _format_pct(limit),
        "message": message,
    }


def _max_status(actual: Decimal, limit: Decimal) -> str:
    if actual > limit:
        return "FAIL"
    if limit > 0 and actual >= limit * WARN_RATIO:
        return "WARN"
    return "PASS"


def _min_status(actual: Decimal, limit: Decimal) -> str:
    if actual < limit:
        return "FAIL"
    if limit > 0 and actual <= limit / WARN_RATIO:
        return "WARN"
    return "PASS"


def _overall_status(items: list[dict]) -> str:
    statuses = {item["status"] for item in items}
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def _pct(value: Decimal, total_value: Decimal) -> Decimal:
    if total_value == 0:
        return Decimal("0")
    return (value / total_value) * Decimal("100")


def _format_pct(value: Decimal) -> str:
    return str(value.quantize(PCT_QUANT, rounding=ROUND_HALF_UP))


def _format_multiple(value: Decimal) -> str:
    return str(value.quantize(MULTIPLE_QUANT, rounding=ROUND_HALF_UP))
