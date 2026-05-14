"""Core exposure calculations."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Mapping

from .config import AnalysisConfig
from .holdings import Holding

MONEY_QUANT = Decimal("0.01")
PCT_QUANT = Decimal("0.0001")


def analyze_portfolio(
    holdings: Iterable[Holding], config: AnalysisConfig | None = None
) -> dict:
    """Return a deterministic exposure report dictionary."""

    resolved_config = config or AnalysisConfig()
    holdings_list = list(holdings)
    total_value = sum((holding.market_value for holding in holdings_list), Decimal("0"))

    holding_rows = [
        {
            "symbol": holding.symbol,
            "name": holding.name,
            "quantity": _format_decimal(holding.quantity),
            "price": _format_money(holding.price),
            "market_value": _format_money(holding.market_value),
            "asset_class": holding.asset_class,
            "sector": holding.sector,
            "region": holding.region,
            "currency": holding.currency,
        }
        for holding in sorted(holdings_list, key=lambda item: item.symbol)
    ]

    exposures = {
        group: _exposure_rows(holdings_list, group, total_value)
        for group in resolved_config.group_by
    }
    concentration = _concentration_rows(
        holdings_list, total_value, resolved_config.concentration_limit_pct
    )
    target_drift = _target_drift_rows(
        exposures, resolved_config.target_allocations
    )

    return {
        "metadata": {
            "base_currency": resolved_config.base_currency,
            "holding_count": len(holdings_list),
            "total_market_value": _format_money(total_value),
            "group_by": list(resolved_config.group_by),
            "concentration_limit_pct": _format_pct(
                resolved_config.concentration_limit_pct
            ),
        },
        "holdings": holding_rows,
        "exposures": exposures,
        "concentration": concentration,
        "target_drift": target_drift,
    }


def _exposure_rows(
    holdings: Iterable[Holding], attribute: str, total_value: Decimal
) -> List[dict]:
    buckets: Dict[str, Decimal] = defaultdict(Decimal)
    for holding in holdings:
        buckets[getattr(holding, attribute)] += holding.market_value

    rows = [
        {
            "bucket": bucket,
            "market_value": _format_money(value),
            "pct_of_portfolio": _format_pct(_pct(value, total_value)),
        }
        for bucket, value in buckets.items()
    ]
    return sorted(rows, key=lambda row: (-Decimal(row["market_value"]), row["bucket"]))


def _concentration_rows(
    holdings: Iterable[Holding], total_value: Decimal, limit_pct: Decimal
) -> List[dict]:
    rows = []
    for holding in holdings:
        pct = _pct(holding.market_value, total_value)
        if pct >= limit_pct:
            rows.append(
                {
                    "symbol": holding.symbol,
                    "market_value": _format_money(holding.market_value),
                    "pct_of_portfolio": _format_pct(pct),
                    "limit_pct": _format_pct(limit_pct),
                }
            )
    return sorted(rows, key=lambda row: (-Decimal(row["pct_of_portfolio"]), row["symbol"]))


def _target_drift_rows(
    exposures: Mapping[str, List[dict]],
    targets: Mapping[str, Mapping[str, Decimal]],
) -> Dict[str, List[dict]]:
    drift: Dict[str, List[dict]] = {}
    for group, group_targets in sorted(targets.items()):
        actual_rows = {
            row["bucket"]: Decimal(row["pct_of_portfolio"])
            for row in exposures.get(group, [])
        }
        buckets = sorted(set(actual_rows) | set(group_targets))
        drift[group] = [
            {
                "bucket": bucket,
                "actual_pct": _format_pct(actual_rows.get(bucket, Decimal("0"))),
                "target_pct": _format_pct(group_targets.get(bucket, Decimal("0"))),
                "drift_pct": _format_pct(
                    actual_rows.get(bucket, Decimal("0"))
                    - group_targets.get(bucket, Decimal("0"))
                ),
            }
            for bucket in buckets
        ]
    return drift


def _pct(value: Decimal, total_value: Decimal) -> Decimal:
    if total_value == 0:
        return Decimal("0")
    return (value / total_value) * Decimal("100")


def _format_money(value: Decimal) -> str:
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _format_pct(value: Decimal) -> str:
    return str(value.quantize(PCT_QUANT, rounding=ROUND_HALF_UP))


def _format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")
