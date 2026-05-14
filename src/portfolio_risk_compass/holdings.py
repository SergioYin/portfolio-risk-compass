"""Holdings CSV parsing."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List

REQUIRED_COLUMNS = (
    "symbol",
    "quantity",
    "price",
    "asset_class",
    "sector",
    "region",
    "currency",
)


@dataclass(frozen=True)
class Holding:
    symbol: str
    quantity: Decimal
    price: Decimal
    asset_class: str
    sector: str
    region: str
    currency: str
    name: str = ""

    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.price


def read_holdings_csv(path: Path) -> List[Holding]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        _validate_columns(reader.fieldnames)
        return [_holding_from_row(row, line_number) for line_number, row in enumerate(reader, 2)]


def parse_holdings_rows(rows: Iterable[dict[str, str]]) -> List[Holding]:
    return [_holding_from_row(row, index) for index, row in enumerate(rows, 1)]


def _validate_columns(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("holdings CSV is missing a header row")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"holdings CSV is missing required column(s): {names}")


def _holding_from_row(row: dict[str, str], line_number: int) -> Holding:
    return Holding(
        symbol=_required_text(row, "symbol", line_number).upper(),
        quantity=_required_decimal(row, "quantity", line_number),
        price=_required_decimal(row, "price", line_number),
        asset_class=_required_text(row, "asset_class", line_number),
        sector=_required_text(row, "sector", line_number),
        region=_required_text(row, "region", line_number),
        currency=_required_text(row, "currency", line_number).upper(),
        name=(row.get("name") or "").strip(),
    )


def _required_text(row: dict[str, str], column: str, line_number: int) -> str:
    value = (row.get(column) or "").strip()
    if not value:
        raise ValueError(f"line {line_number}: {column} is required")
    return value


def _required_decimal(row: dict[str, str], column: str, line_number: int) -> Decimal:
    value = _required_text(row, column, line_number)
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"line {line_number}: {column} must be a decimal number") from exc
    if parsed < 0:
        raise ValueError(f"line {line_number}: {column} must be non-negative")
    return parsed
