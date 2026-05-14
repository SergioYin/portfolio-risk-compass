"""Scenario shock analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable, List

from .holdings import Holding

MONEY_QUANT = Decimal("0.01")
PCT_QUANT = Decimal("0.0001")
SELECTORS = ("symbol", "sector", "asset_class", "region", "currency")


@dataclass(frozen=True)
class ScenarioShock:
    name: str
    selector: str
    bucket: str
    price_move_pct: Decimal


@dataclass(frozen=True)
class StressScenario:
    name: str
    shocks: tuple[ScenarioShock, ...]


def read_scenario_json(path: Path) -> StressScenario:
    try:
        raw_scenario = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON scenario {path}: {exc}") from exc

    return parse_scenario(raw_scenario)


def parse_scenario(raw_scenario: object) -> StressScenario:
    if not isinstance(raw_scenario, dict):
        raise ValueError("scenario JSON must be an object")

    name = _required_text(raw_scenario, "name", "scenario")
    raw_shocks = raw_scenario.get("shocks")
    if not isinstance(raw_shocks, list) or not raw_shocks:
        raise ValueError("scenario.shocks must be a non-empty array")

    return StressScenario(
        name=name,
        shocks=tuple(
            _parse_shock(raw_shock, index)
            for index, raw_shock in enumerate(raw_shocks)
        ),
    )


def stress_portfolio(
    holdings: Iterable[Holding], scenario: StressScenario
) -> dict:
    holdings_list = sorted(list(holdings), key=lambda item: item.symbol)
    base_total = sum((holding.market_value for holding in holdings_list), Decimal("0"))

    holding_results: List[dict] = []
    shock_deltas = {shock.name: Decimal("0") for shock in scenario.shocks}
    shocked_values = []

    for holding in holdings_list:
        matched = []
        total_move_pct = Decimal("0")
        for shock in scenario.shocks:
            if _shock_matches(holding, shock):
                value_delta = holding.market_value * shock.price_move_pct / Decimal("100")
                shock_deltas[shock.name] += value_delta
                total_move_pct += shock.price_move_pct
                matched.append(
                    {
                        "name": shock.name,
                        "selector": shock.selector,
                        "bucket": shock.bucket,
                        "price_move_pct": _format_pct(shock.price_move_pct),
                        "market_value_delta": _format_money(value_delta),
                    }
                )

        if total_move_pct < Decimal("-100"):
            raise ValueError(
                f"combined shocks move {holding.symbol} below -100% price change"
            )

        stressed_market_value = holding.market_value * (
            Decimal("1") + total_move_pct / Decimal("100")
        )
        shocked_values.append(stressed_market_value)
        holding_results.append(
            {
                "symbol": holding.symbol,
                "name": holding.name,
                "base_market_value": _format_money(holding.market_value),
                "stressed_market_value": _format_money(stressed_market_value),
                "market_value_delta": _format_money(
                    stressed_market_value - holding.market_value
                ),
                "total_price_move_pct": _format_pct(total_move_pct),
                "shocks": matched,
            }
        )

    stressed_total = sum(shocked_values, Decimal("0"))
    for row, holding, stressed_market_value in zip(
        holding_results, holdings_list, shocked_values
    ):
        row["base_contribution_pct"] = _format_pct(_pct(holding.market_value, base_total))
        row["stressed_contribution_pct"] = _format_pct(
            _pct(stressed_market_value, stressed_total)
        )
        row["contribution_delta_pct"] = _format_pct(
            _pct(stressed_market_value, stressed_total)
            - _pct(holding.market_value, base_total)
        )

    shock_rows = [
        {
            "name": shock.name,
            "selector": shock.selector,
            "bucket": shock.bucket,
            "price_move_pct": _format_pct(shock.price_move_pct),
            "market_value_delta": _format_money(shock_deltas[shock.name]),
        }
        for shock in scenario.shocks
    ]

    return {
        "metadata": {
            "scenario_name": scenario.name,
            "holding_count": len(holdings_list),
            "shock_count": len(scenario.shocks),
            "base_market_value": _format_money(base_total),
            "stressed_market_value": _format_money(stressed_total),
            "market_value_delta": _format_money(stressed_total - base_total),
            "market_value_delta_pct": _format_pct(
                _pct(stressed_total - base_total, base_total)
            ),
        },
        "shock_impacts": shock_rows,
        "holdings": holding_results,
    }


def render_stress_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_stress_markdown(report: dict) -> str:
    metadata = report["metadata"]
    lines = [
        "# Portfolio Stress Scenario",
        "",
        f"- Scenario: {metadata['scenario_name']}",
        f"- Holdings: {metadata['holding_count']}",
        f"- Shocks: {metadata['shock_count']}",
        f"- Base market value: {metadata['base_market_value']}",
        f"- Stressed market value: {metadata['stressed_market_value']}",
        (
            f"- Market value delta: {metadata['market_value_delta']} "
            f"({metadata['market_value_delta_pct']}%)"
        ),
        "",
        "## Shock Impacts",
        "",
        "| Shock | Selector | Bucket | Price move | Market value delta |",
        "| --- | --- | --- | ---: | ---: |",
    ]

    for shock in report["shock_impacts"]:
        lines.append(
            f"| {shock['name']} | {shock['selector']} | {shock['bucket']} | "
            f"{shock['price_move_pct']}% | {shock['market_value_delta']} |"
        )

    lines.extend(
        [
            "",
            "## Holding Deltas",
            "",
            "| Symbol | Base value | Stressed value | Value delta | Price move | Contribution delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for holding in report["holdings"]:
        lines.append(
            f"| {holding['symbol']} | {holding['base_market_value']} | "
            f"{holding['stressed_market_value']} | {holding['market_value_delta']} | "
            f"{holding['total_price_move_pct']}% | {holding['contribution_delta_pct']}% |"
        )

    return "\n".join(lines).rstrip() + "\n"


def _parse_shock(raw_shock: object, index: int) -> ScenarioShock:
    field_prefix = f"scenario.shocks[{index}]"
    if not isinstance(raw_shock, dict):
        raise ValueError(f"{field_prefix} must be an object")

    selectors = [selector for selector in SELECTORS if selector in raw_shock]
    if len(selectors) != 1:
        names = ", ".join(SELECTORS)
        raise ValueError(f"{field_prefix} must include exactly one selector: {names}")

    selector = selectors[0]
    bucket = _required_text(raw_shock, selector, field_prefix)
    if selector in {"symbol", "currency"}:
        bucket = bucket.upper()

    raw_move = raw_shock.get("price_move_pct", raw_shock.get("move_pct"))
    price_move_pct = _decimal_value(raw_move, f"{field_prefix}.price_move_pct")
    if price_move_pct < Decimal("-100"):
        raise ValueError(
            f"{field_prefix}.price_move_pct must be greater than or equal to -100"
        )

    return ScenarioShock(
        name=_required_text(raw_shock, "name", field_prefix),
        selector=selector,
        bucket=bucket,
        price_move_pct=price_move_pct,
    )


def _shock_matches(holding: Holding, shock: ScenarioShock) -> bool:
    value = getattr(holding, shock.selector)
    if shock.selector in {"symbol", "currency"}:
        value = value.upper()
    return value == shock.bucket


def _required_text(raw: dict, field: str, prefix: str) -> str:
    value = raw.get(field)
    if value is None or str(value).strip() == "":
        raise ValueError(f"{prefix}.{field} is required")
    return str(value).strip()


def _decimal_value(value: object, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a decimal number") from exc


def _pct(value: Decimal, total_value: Decimal) -> Decimal:
    if total_value == 0:
        return Decimal("0")
    return (value / total_value) * Decimal("100")


def _format_money(value: Decimal) -> str:
    return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))


def _format_pct(value: Decimal) -> str:
    return str(value.quantize(PCT_QUANT, rounding=ROUND_HALF_UP))
