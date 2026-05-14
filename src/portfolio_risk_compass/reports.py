"""Report rendering."""

from __future__ import annotations

import json


def render_json_report(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_markdown_report(report: dict) -> str:
    metadata = report["metadata"]
    lines = [
        "# Portfolio Exposure Report",
        "",
        f"- Base currency: {metadata['base_currency']}",
        f"- Holdings: {metadata['holding_count']}",
        f"- Total market value: {metadata['total_market_value']}",
        f"- Concentration limit: {metadata['concentration_limit_pct']}%",
        "",
    ]

    for group in metadata["group_by"]:
        title = group.replace("_", " ").title()
        lines.extend(
            [
                f"## Exposure by {title}",
                "",
                "| Bucket | Market value | Portfolio % |",
                "| --- | ---: | ---: |",
            ]
        )
        rows = report["exposures"].get(group, [])
        if rows:
            for row in rows:
                lines.append(
                    f"| {row['bucket']} | {row['market_value']} | {row['pct_of_portfolio']}% |"
                )
        else:
            lines.append("| None | 0.00 | 0.0000% |")
        lines.append("")

    lines.extend(
        [
            "## Concentration",
            "",
            "| Symbol | Market value | Portfolio % | Limit % |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    if report["concentration"]:
        for row in report["concentration"]:
            lines.append(
                f"| {row['symbol']} | {row['market_value']} | "
                f"{row['pct_of_portfolio']}% | {row['limit_pct']}% |"
            )
    else:
        lines.append("| None | 0.00 | 0.0000% | 0.0000% |")
    lines.append("")

    if report["target_drift"]:
        for group, rows in report["target_drift"].items():
            title = group.replace("_", " ").title()
            lines.extend(
                [
                    f"## Target Drift by {title}",
                    "",
                    "| Bucket | Actual % | Target % | Drift % |",
                    "| --- | ---: | ---: | ---: |",
                ]
            )
            for row in rows:
                lines.append(
                    f"| {row['bucket']} | {row['actual_pct']}% | "
                    f"{row['target_pct']}% | {row['drift_pct']}% |"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
