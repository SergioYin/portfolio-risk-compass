"""Release-to-release visual capture audit comparison."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from urllib.parse import quote

from .visual_capture_audit import BOUNDARIES


SCHEMA_LABEL = "portfolio-risk-compass-visual-capture-compare.v1"

DEFAULT_VISUAL_CAPTURE_COMPARE_JSON = "visual_capture_compare.json"
DEFAULT_VISUAL_CAPTURE_COMPARE_MARKDOWN = "visual_capture_compare.md"

COMPARE_FIELDS = (
    "bytes",
    "sha256",
    "hash",
    "present",
    "role",
    "route",
    "render",
    "capture_command",
)

COMPARE_BOUNDARIES = {
    "scope": "static/local demo visual capture audit artifacts only",
    **BOUNDARIES,
    "no_private_data": "does not require, inspect, or emit private account data",
}


def read_visual_capture_audit(path: Path) -> dict:
    """Read a visual capture audit JSON file."""

    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        reason = exc.strerror or exc.__class__.__name__
        raise ValueError(f"could not read visual capture audit JSON: {reason}") from exc
    try:
        audit = json.loads(text)
    except JSONDecodeError as exc:
        raise ValueError(
            "invalid visual capture audit JSON "
            f"at line {exc.lineno} column {exc.colno}"
        ) from exc
    _validate_visual_capture_audit(audit)
    return audit


def compare_visual_capture_audits(before: dict, after: dict) -> dict:
    """Compare two visual capture audits by stable relative artifact path."""

    _validate_visual_capture_audit(before)
    _validate_visual_capture_audit(after)
    before_entries = _entry_map(before)
    after_entries = _entry_map(after)
    before_keys = set(before_entries)
    after_keys = set(after_entries)

    added_keys = sorted(after_keys - before_keys)
    removed_keys = sorted(before_keys - after_keys)
    common_keys = sorted(before_keys & after_keys)

    changed = []
    unchanged = []
    for key in common_keys:
        differences = _entry_differences(before_entries[key], after_entries[key])
        if differences:
            changed.append(
                {
                    "key": key,
                    "path": after_entries[key].get("path", before_entries[key].get("path", key)),
                    "role": after_entries[key].get("role", before_entries[key].get("role")),
                    "differences": differences,
                }
            )
        else:
            unchanged.append(key)

    return {
        "schema": SCHEMA_LABEL,
        "artifact": "portfolio-risk-compass-visual-capture-compare",
        "scope": (
            "Release-to-release comparison of static local visual/demo capture audit "
            "entries keyed by relative path or artifact key."
        ),
        "boundaries": COMPARE_BOUNDARIES,
        "inputs": {
            "before_schema": before.get("schema"),
            "after_schema": after.get("schema"),
            "before_root": before.get("root"),
            "after_root": after.get("root"),
        },
        "summary": {
            "before_entries": len(before_entries),
            "after_entries": len(after_entries),
            "added": len(added_keys),
            "removed": len(removed_keys),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
        "added": [_entry_summary(after_entries[key], key) for key in added_keys],
        "removed": [_entry_summary(before_entries[key], key) for key in removed_keys],
        "changed": changed,
        "unchanged": unchanged,
        "compared_fields": list(COMPARE_FIELDS),
    }


def render_visual_capture_compare_json(comparison: dict) -> str:
    return json.dumps(comparison, indent=2, sort_keys=True) + "\n"


def render_visual_capture_compare_markdown(comparison: dict) -> str:
    summary = comparison.get("summary", {})
    lines = [
        "# Portfolio Risk Compass Visual Capture Compare",
        "",
        f"Schema: `{_table_cell(comparison.get('schema', SCHEMA_LABEL))}`",
        f"Scope: {_table_cell(comparison.get('scope', ''))}",
        "",
        "## Boundaries",
        "",
    ]
    for key in sorted(comparison.get("boundaries", {})):
        lines.append(f"- {_table_cell(key).replace('_', ' ')}: {_table_cell(comparison['boundaries'][key])}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Before entries: {summary.get('before_entries', 0)}",
            f"- After entries: {summary.get('after_entries', 0)}",
            f"- Added: {summary.get('added', 0)}",
            f"- Removed: {summary.get('removed', 0)}",
            f"- Changed: {summary.get('changed', 0)}",
            f"- Unchanged: {summary.get('unchanged', 0)}",
            "",
            "## Added",
            "",
        ]
    )
    _append_entry_table(lines, comparison.get("added", []))

    lines.extend(["", "## Removed", ""])
    _append_entry_table(lines, comparison.get("removed", []))

    lines.extend(["", "## Changed", ""])
    changed = comparison.get("changed", [])
    if changed:
        lines.extend(["| Path | Role | Differences |", "| --- | --- | --- |"])
        for item in changed:
            diff_text = "; ".join(
                f"{_table_cell(diff.get('field', ''))}: "
                f"{_display_value(diff.get('before'))} -> {_display_value(diff.get('after'))}"
                for diff in item.get("differences", [])
            )
            lines.append(
                "| {path} | {role} | {diffs} |".format(
                    path=_markdown_link(item.get("path", item.get("key", ""))),
                    role=_table_cell(item.get("role", "")),
                    diffs=_table_cell(diff_text),
                )
            )
    else:
        lines.append("None.")

    lines.extend(["", "## Unchanged", ""])
    unchanged = comparison.get("unchanged", [])
    if unchanged:
        lines.extend(f"- `{_table_cell(key)}`" for key in unchanged)
    else:
        lines.append("None.")

    return "\n".join(lines) + "\n"


def write_visual_capture_compare(
    before_path: Path,
    after_path: Path,
    output: Path,
    output_format: str,
) -> dict:
    comparison = compare_visual_capture_audits(
        read_visual_capture_audit(before_path),
        read_visual_capture_audit(after_path),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        output.write_text(render_visual_capture_compare_markdown(comparison), encoding="utf-8")
    else:
        output.write_text(render_visual_capture_compare_json(comparison), encoding="utf-8")
    return comparison


def _entry_map(audit: dict) -> dict[str, dict]:
    entries = {}
    for item in audit.get("checked_artifacts", []):
        key = _entry_key(item)
        if key:
            if key in entries:
                raise ValueError("duplicate visual capture audit entry key")
            entries[key] = item
    return entries


def _validate_visual_capture_audit(audit: object) -> None:
    if not isinstance(audit, dict):
        raise ValueError("visual capture audit JSON must be an object")
    entries = audit.get("checked_artifacts", [])
    if not isinstance(entries, list):
        raise ValueError("visual capture audit checked_artifacts must be a list")
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(
                "visual capture audit checked_artifacts "
                f"entry {index} must be an object"
            )


def _entry_key(item: dict) -> str:
    for field in ("path", "artifact_key", "key"):
        value = item.get(field)
        if isinstance(value, str) and value:
            return value
    return ""


def _entry_differences(before: dict, after: dict) -> list[dict]:
    differences = []
    for field in COMPARE_FIELDS:
        before_value = _field_value(before, field)
        after_value = _field_value(after, field)
        if before_value != after_value:
            differences.append(
                {
                    "field": field,
                    "before": before_value,
                    "after": after_value,
                }
            )
    return differences


def _field_value(item: dict, field: str) -> object:
    if field in item:
        return item[field]
    capture = item.get("capture")
    if isinstance(capture, dict) and field in capture:
        return capture[field]
    command = item.get("command")
    if field == "capture_command" and command is not None:
        return command
    return None


def _entry_summary(item: dict, key: str) -> dict:
    return {
        "key": key,
        "path": item.get("path", key),
        "role": item.get("role"),
        "present": item.get("present"),
        "bytes": item.get("bytes"),
        "sha256": item.get("sha256", item.get("hash")),
    }


def _append_entry_table(lines: list[str], entries: list[dict]) -> None:
    if not entries:
        lines.append("None.")
        return
    lines.extend(["| Path | Role | Present | Bytes | SHA-256 |", "| --- | --- | --- | ---: | --- |"])
    for item in entries:
        lines.append(
            "| {path} | {role} | {present} | {bytes} | {sha256} |".format(
                path=_markdown_link(item.get("path", item.get("key", ""))),
                role=_table_cell(item.get("role", "")),
                present=_table_cell(item.get("present")),
                bytes=_table_cell(_display_value(item.get("bytes"))),
                sha256=_code_span(item["sha256"]) if item.get("sha256") else "n/a",
            )
        )


def _display_value(value: object) -> str:
    if value is None:
        return "n/a"
    return str(value)


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return _display_value(value).replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`" + _table_cell(value).replace("`", "\\`") + "`"
