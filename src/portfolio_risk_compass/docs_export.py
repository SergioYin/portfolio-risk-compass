"""Deterministic single-file documentation export."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from . import __version__
from .catalysts import REQUIRED_FIELDS as CATALYST_FIELDS
from .config import DEFAULT_GROUPS, SUPPORTED_GROUPS
from .demo import DEFAULT_OUTPUT_DIR
from .holdings import REQUIRED_COLUMNS
from .packaging import build_release_manifest
from .rebalance_watchlist import SAFETY_WORDING
from .review_memo import NON_ADVICE_BOUNDARY
from .stress import SELECTORS

DEFAULT_DOCS_EXPORT = DEFAULT_OUTPUT_DIR / "docs_export.md"


def build_docs_export(
    parser: argparse.ArgumentParser,
    outputs_dir: Path = DEFAULT_OUTPUT_DIR,
    output_path: Path | None = None,
    title: str = "Portfolio Risk Compass Docs Export",
) -> dict:
    """Build the complete docs export model."""

    excluded = (output_path,) if output_path else ()
    return {
        "title": title,
        "version": __version__,
        "cli_reference": _cli_reference(parser),
        "input_schemas": _input_schemas(),
        "artifact_inventory": build_release_manifest(outputs_dir, exclude_paths=excluded),
        "safety_boundary": _safety_boundary(),
        "example_output": _example_output(),
    }


def render_docs_markdown(export: dict) -> str:
    lines = [
        f"# {export['title']}",
        "",
        f"- Package: portfolio-risk-compass",
        f"- Version: {export['version']}",
        "- Format: deterministic single-file Markdown, no JavaScript",
        "",
        "## CLI Reference",
        "",
    ]
    for command in export["cli_reference"]:
        lines.extend(
            [
                f"### `{command['name']}`",
                "",
                command["help"],
                "",
                f"Usage: `{command['usage']}`",
                "",
            ]
        )
        if command["arguments"]:
            lines.extend(["| Argument | Required | Description |", "| --- | --- | --- |"])
            for argument in command["arguments"]:
                lines.append(
                    f"| `{argument['name']}` | {argument['required']} | {argument['help']} |"
                )
            lines.append("")

    lines.extend(["## Input Schemas", ""])
    for schema in export["input_schemas"]:
        lines.extend([f"### {schema['name']}", "", schema["description"], ""])
        lines.extend(["| Field | Type | Required | Notes |", "| --- | --- | --- | --- |"])
        for field in schema["fields"]:
            lines.append(
                f"| `{field['name']}` | {field['type']} | {field['required']} | {field['notes']} |"
            )
        lines.append("")

    inventory = export["artifact_inventory"]
    lines.extend(
        [
            "## Artifact Inventory",
            "",
            f"- Outputs directory: {inventory['outputs_dir']}",
            f"- Artifact count: {inventory['artifact_count']}",
            "",
            "| Path | Format | Bytes | SHA-256 |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for artifact in inventory["artifacts"]:
        lines.append(
            "| {path} | {format} | {bytes} | `{sha256}` |".format(**artifact)
        )

    safety = export["safety_boundary"]
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            f"- Review memo: {safety['review_memo']}",
            f"- Rebalance watchlist: {safety['rebalance_watchlist']}",
            (
                "- Data boundary: This package reads user-provided CSV/JSON fixtures "
                "and generated local artifacts. It does not fetch market data, place "
                "orders, or connect to brokerage accounts."
            ),
            "",
            "## Generated Example Output",
            "",
            "```bash",
            export["example_output"]["command"],
            "```",
            "",
            "```markdown",
            *export["example_output"]["markdown_lines"],
            "```",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_docs_html(export: dict) -> str:
    markdown = render_docs_markdown(export)
    body = _markdown_subset_to_html(markdown)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{html.escape(export['title'])}</title>",
            "<style>",
            "body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.5;max-width:1120px;margin:0 auto;padding:32px;color:#1f2933;background:#fff}",
            "h1,h2,h3{line-height:1.2}table{border-collapse:collapse;width:100%;margin:16px 0}th,td{border:1px solid #ccd5df;padding:6px 8px;text-align:left;vertical-align:top}th{background:#eef3f8}code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}pre{background:#f5f7fa;border:1px solid #d9e2ec;padding:12px;overflow:auto}",
            "</style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
            "",
        ]
    )


def write_docs_export(
    parser: argparse.ArgumentParser,
    output_path: Path,
    outputs_dir: Path = DEFAULT_OUTPUT_DIR,
    output_format: str = "markdown",
    title: str = "Portfolio Risk Compass Docs Export",
) -> dict:
    export = build_docs_export(
        parser,
        outputs_dir=outputs_dir,
        output_path=output_path,
        title=title,
    )
    if output_format == "html":
        content = render_docs_html(export)
    else:
        content = render_docs_markdown(export)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return export


def _cli_reference(parser: argparse.ArgumentParser) -> list[dict]:
    subparsers_action = next(
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    commands = []
    for name in sorted(subparsers_action.choices):
        command_parser = subparsers_action.choices[name]
        commands.append(
            {
                "name": name,
                "help": _clean_help(command_parser.description or ""),
                "usage": _clean_usage(command_parser.format_usage()),
                "arguments": _argument_reference(command_parser),
            }
        )
    return commands


def _argument_reference(parser: argparse.ArgumentParser) -> list[dict]:
    arguments = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            continue
        if action.dest == "command":
            continue
        name = ", ".join(action.option_strings) if action.option_strings else action.dest
        required = "yes" if _is_required(action) else "no"
        arguments.append(
            {
                "name": name,
                "required": required,
                "help": _clean_help(action.help or ""),
            }
        )
    return arguments


def _is_required(action: argparse.Action) -> bool:
    if not action.option_strings:
        return True
    return bool(getattr(action, "required", False))


def _input_schemas() -> list[dict]:
    return [
        {
            "name": "holdings.csv",
            "description": "Portfolio holdings table consumed by analyze, snapshot, guardrails, stress, and rebalance-watchlist flows.",
            "fields": [
                _field(column, "decimal" if column in {"quantity", "price"} else "string", "yes", _holdings_note(column))
                for column in REQUIRED_COLUMNS
            ]
            + [_field("name", "string", "no", "Optional display name.")],
        },
        {
            "name": "config.json",
            "description": "Portfolio policy, grouping, targets, and guardrail settings.",
            "fields": [
                _field("base_currency", "string", "no", "Defaults to USD and is normalized to uppercase."),
                _field("group_by", "array[string]", "no", f"Defaults to {', '.join(DEFAULT_GROUPS)}. Supported values: {', '.join(sorted(SUPPORTED_GROUPS))}."),
                _field("concentration_limit_pct", "decimal", "no", "Defaults to 25."),
                _field("max_position_pct", "decimal", "no", "Non-negative position guardrail limit."),
                _field("max_sector_pct", "decimal", "no", "Non-negative sector guardrail limit."),
                _field("min_cash_pct", "decimal", "no", "Non-negative cash floor guardrail."),
                _field("max_leverage_multiple", "decimal", "no", "Non-negative leverage guardrail."),
                _field("required_review_cadence_days", "integer", "no", "Positive integer review cadence."),
                _field("last_review_date", "date", "no", "ISO date in YYYY-MM-DD format."),
                _field("target_allocations", "object", "no", "Object keyed by supported group name, then bucket, with decimal target percentages."),
            ],
        },
        {
            "name": "scenario.json",
            "description": "Stress scenario with named price shocks.",
            "fields": [
                _field("name", "string", "yes", "Scenario name."),
                _field("shocks", "array[object]", "yes", "Non-empty array of shock objects."),
                _field("shocks[].name", "string", "yes", "Shock name."),
                _field("shocks[].selector", "string", "yes", f"Exactly one selector field must be present: {', '.join(SELECTORS)}."),
                _field("shocks[].price_move_pct", "decimal", "yes", "Percentage price move, greater than or equal to -100. move_pct is accepted as an alias."),
            ],
        },
        {
            "name": "catalysts.json",
            "description": "Catalyst checklist fixture.",
            "fields": [
                _field(field, "date" if field == "date" else "string", "yes", _catalyst_note(field))
                for field in CATALYST_FIELDS
            ],
        },
        {
            "name": "history/*.json",
            "description": "Directory of generated snapshot JSON files for the history ledger.",
            "fields": [
                _field("snapshot.date", "date", "yes", "ISO date used for chronological ordering."),
                _field("snapshot.id", "string", "yes", "Snapshot identifier."),
                _field("report.metadata.total_market_value", "decimal string", "yes", "Snapshot portfolio value."),
                _field("report.target_drift", "object", "no", "Target drift rows copied from snapshot output."),
                _field("guardrails", "object", "no", "Optional guardrail review summary embedded in the snapshot fixture."),
                _field("catalysts", "object", "no", "Optional catalyst checklist summary embedded in the snapshot fixture."),
            ],
        },
    ]


def _field(name: str, field_type: str, required: str, notes: str) -> dict:
    return {"name": name, "type": field_type, "required": required, "notes": notes}


def _holdings_note(column: str) -> str:
    notes = {
        "symbol": "Required ticker or identifier, normalized to uppercase.",
        "quantity": "Required non-negative decimal.",
        "price": "Required non-negative decimal.",
        "asset_class": "Required exposure bucket.",
        "sector": "Required exposure bucket.",
        "region": "Required exposure bucket.",
        "currency": "Required currency code, normalized to uppercase.",
    }
    return notes[column]


def _catalyst_note(field: str) -> str:
    if field == "date":
        return "ISO date in YYYY-MM-DD format."
    if field == "symbol":
        return "Ticker or identifier, normalized to uppercase."
    return "Non-empty string."


def _safety_boundary() -> dict:
    return {
        "review_memo": NON_ADVICE_BOUNDARY,
        "rebalance_watchlist": SAFETY_WORDING,
    }


def _example_output() -> dict:
    return {
        "command": (
            "portfolio-risk-compass docs-export --output examples/outputs/docs_export.md"
        ),
        "markdown_lines": [
            "# Portfolio Risk Compass Docs Export",
            "",
            "- Package: portfolio-risk-compass",
            "- Version: 0.2.0",
            "- Format: deterministic single-file Markdown, no JavaScript",
            "",
            "## CLI Reference",
        ],
    }


def _clean_help(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _clean_usage(value: str) -> str:
    return _clean_help(value.replace("usage: ", ""))


def _markdown_subset_to_html(markdown: str) -> str:
    html_lines = []
    in_code = False
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("```"):
            html_lines.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            html_lines.append(html.escape(line))
            continue
        if line.startswith("| ") and line.endswith(" |"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if set(cells) == {"---"} or all(cell.startswith("---") for cell in cells):
                continue
            if not in_table:
                html_lines.append("<table>")
                in_table = True
                tag = "th"
            else:
                tag = "td"
            html_lines.append(
                "<tr>"
                + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in cells)
                + "</tr>"
            )
            continue
        if in_table:
            html_lines.append("</table>")
            in_table = False
        if line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            html_lines.append(f"<p>{html.escape(line)}</p>")
        elif line:
            html_lines.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        html_lines.append("</table>")
    return "\n".join(html_lines)
