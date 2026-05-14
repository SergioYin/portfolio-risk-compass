"""Configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping

DEFAULT_GROUPS = ("asset_class", "sector", "region", "currency")
SUPPORTED_GROUPS = frozenset(DEFAULT_GROUPS)


@dataclass(frozen=True)
class AnalysisConfig:
    base_currency: str = "USD"
    group_by: tuple[str, ...] = DEFAULT_GROUPS
    concentration_limit_pct: Decimal = Decimal("25")
    max_position_pct: Decimal | None = None
    max_sector_pct: Decimal | None = None
    min_cash_pct: Decimal | None = None
    max_leverage_multiple: Decimal | None = None
    required_review_cadence_days: int | None = None
    last_review_date: date | None = None
    target_allocations: Mapping[str, Mapping[str, Decimal]] = field(
        default_factory=dict
    )


def read_config_json(path: Path) -> AnalysisConfig:
    try:
        raw_config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON config {path}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ValueError("config JSON must be an object")

    base_currency = str(raw_config.get("base_currency", "USD")).upper()
    group_by = tuple(raw_config.get("group_by", DEFAULT_GROUPS))
    _validate_groups(group_by)

    concentration_limit_pct = _decimal_field(
        raw_config.get("concentration_limit_pct", "25"),
        "concentration_limit_pct",
    )
    max_position_pct = _optional_decimal_field(
        raw_config.get("max_position_pct"), "max_position_pct"
    )
    max_sector_pct = _optional_decimal_field(
        raw_config.get("max_sector_pct"), "max_sector_pct"
    )
    min_cash_pct = _optional_decimal_field(
        raw_config.get("min_cash_pct"), "min_cash_pct"
    )
    max_leverage_multiple = _optional_decimal_field(
        raw_config.get("max_leverage_multiple"), "max_leverage_multiple"
    )
    required_review_cadence_days = _optional_positive_int_field(
        raw_config.get("required_review_cadence_days"),
        "required_review_cadence_days",
    )
    last_review_date = _optional_date_field(
        raw_config.get("last_review_date"), "last_review_date"
    )
    target_allocations = _target_allocations(raw_config.get("target_allocations", {}))

    return AnalysisConfig(
        base_currency=base_currency,
        group_by=group_by,
        concentration_limit_pct=concentration_limit_pct,
        max_position_pct=max_position_pct,
        max_sector_pct=max_sector_pct,
        min_cash_pct=min_cash_pct,
        max_leverage_multiple=max_leverage_multiple,
        required_review_cadence_days=required_review_cadence_days,
        last_review_date=last_review_date,
        target_allocations=target_allocations,
    )


def _validate_groups(groups: tuple[str, ...]) -> None:
    if not groups:
        raise ValueError("group_by must include at least one exposure group")
    unsupported = sorted(set(groups) - SUPPORTED_GROUPS)
    if unsupported:
        names = ", ".join(unsupported)
        raise ValueError(f"unsupported exposure group(s): {names}")


def _target_allocations(raw_targets: object) -> dict[str, dict[str, Decimal]]:
    if not isinstance(raw_targets, dict):
        raise ValueError("target_allocations must be an object")

    parsed: dict[str, dict[str, Decimal]] = {}
    for group, targets in raw_targets.items():
        if group not in SUPPORTED_GROUPS:
            raise ValueError(f"unsupported target allocation group: {group}")
        if not isinstance(targets, dict):
            raise ValueError(f"target_allocations.{group} must be an object")
        parsed[group] = {
            str(bucket): _decimal_field(value, f"target_allocations.{group}.{bucket}")
            for bucket, value in targets.items()
        }
    return parsed


def _decimal_field(value: object, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a decimal number") from exc


def _optional_decimal_field(value: object, field_name: str) -> Decimal | None:
    if value is None:
        return None
    parsed = _decimal_field(value, field_name)
    if parsed < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return parsed


def _optional_positive_int_field(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return parsed


def _optional_date_field(value: object, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc
