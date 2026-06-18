"""Screenshot guide and receipt for the public static dashboard route."""

from __future__ import annotations

import hashlib
import json
import shlex
from pathlib import Path
from urllib.parse import quote

from .dashboard import SAFETY_BOUNDARY_TEXT
from .public_review import BOUNDARY_FLAGS
from .scenario_evidence import PUBLIC_SAFETY_NOTICE

DEFAULT_SCREENSHOT_GUIDE_MARKDOWN = "dashboard_screenshot_guide.md"
DEFAULT_SCREENSHOT_GUIDE_JSON = "dashboard_screenshot_guide.json"
DEFAULT_SCREENSHOT_PATH = "screenshots/dashboard-public-review-1365x900.png"

SCREENSHOT_SOURCE_ARTIFACTS = (
    {
        "role": "static_dashboard_route",
        "path": "dashboard.html",
        "purpose": "Browser-rendered public dashboard route to capture.",
    },
    {
        "role": "public_review_walkthrough",
        "path": "public_review_walkthrough.md",
        "purpose": "Public reviewer route, rerun commands, and boundary checks.",
    },
)


def build_screenshot_guide(
    manifest: dict,
    output_dir: Path,
    screenshot_path: str = DEFAULT_SCREENSHOT_PATH,
) -> dict:
    """Build deterministic screenshot capture instructions and hash receipt."""

    dashboard_url = _dashboard_file_url(output_dir)
    screenshot_output = _display_path(output_dir / screenshot_path)
    screenshot_dir = _display_path(output_dir / Path(screenshot_path).parent)
    capture_command = (
        "python -m playwright screenshot --browser chromium "
        "--viewport-size=1365,900 "
        f"{_shell_arg(dashboard_url)} {_shell_arg(screenshot_output)}"
    )
    source_artifacts = [
        _artifact_entry(output_dir, item["path"], item["role"], item["purpose"])
        for item in SCREENSHOT_SOURCE_ARTIFACTS
    ]
    screenshot_artifacts = [
        _artifact_entry(
            output_dir,
            screenshot_path,
            "dashboard_screenshot",
            "Expected browser screenshot produced by the exact capture command.",
        )
    ]

    return {
        "schema_version": 1,
        "artifact": "portfolio-risk-compass-dashboard-screenshot-guide",
        "as_of": manifest.get("as_of", "unknown"),
        "safety_boundary": SAFETY_BOUNDARY_TEXT,
        "public_safety_notice": PUBLIC_SAFETY_NOTICE,
        "boundary_flags": BOUNDARY_FLAGS,
        "review_scope": (
            "Deterministic screenshot guide for the static public dashboard route. "
            "Public means generated demo/review artifacts that are suitable to share "
            "after review; it records local artifact hashes only and does not fetch "
            "live data, expose private account data, connect to brokers, place "
            "orders, or provide investment advice."
        ),
        "public_route": {
            "dashboard": "dashboard.html",
            "public_review": "public_review_walkthrough.md",
        },
        "capture_profile": {
            "browser": "chromium",
            "viewport_width": 1365,
            "viewport_height": 900,
            "full_page": False,
            "input_url": dashboard_url,
            "output_path": screenshot_output,
        },
        "capture_steps": [
            {
                "step": 1,
                "title": "Regenerate static review artifacts",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass demo-bundle",
            },
            {
                "step": 2,
                "title": "Render the public dashboard route",
                "command": (
                    "PYTHONPATH=src python -m portfolio_risk_compass dashboard "
                    "examples/outputs/index.json examples/outputs/dashboard.html"
                ),
            },
            {
                "step": 3,
                "title": "Refresh the public review packet",
                "command": "PYTHONPATH=src python -m portfolio_risk_compass public-review",
            },
            {
                "step": 4,
                "title": "Prepare screenshot output directory",
                "command": f"mkdir -p {_shell_arg(screenshot_dir)}",
            },
            {
                "step": 5,
                "title": "Capture the deterministic dashboard screenshot",
                "command": capture_command,
            },
            {
                "step": 6,
                "title": "Refresh this screenshot guide and visual receipt",
                "command": (
                    "PYTHONPATH=src python -m portfolio_risk_compass screenshot-guide && "
                    "PYTHONPATH=src python -m portfolio_risk_compass visual-evidence-receipt"
                ),
            },
        ],
        "source_artifacts": source_artifacts,
        "screenshot_artifacts": screenshot_artifacts,
        "artifact_coverage": _coverage(source_artifacts + screenshot_artifacts),
    }


def render_screenshot_guide_json(guide: dict) -> str:
    return json.dumps(guide, indent=2, sort_keys=True) + "\n"


def render_screenshot_guide_markdown(guide: dict) -> str:
    coverage = guide.get("artifact_coverage", {})
    profile = guide.get("capture_profile", {})
    lines = [
        "# Portfolio Risk Compass Dashboard Screenshot Guide",
        "",
        "Deterministic screenshot capture guide and receipt for the static public dashboard route.",
        "",
        f"Safety boundary: {guide.get('safety_boundary', SAFETY_BOUNDARY_TEXT)}",
        f"Public safety notice: {guide.get('public_safety_notice', PUBLIC_SAFETY_NOTICE)}",
        f"Review scope: {guide.get('review_scope', '')}",
        "",
        "## Boundaries",
        "",
    ]
    for key, value in guide.get("boundary_flags", {}).items():
        lines.append(f"- No {_table_cell(key).replace('_', ' ')}: {_table_cell(value)}")

    lines.extend(
        [
            "",
            "## Capture Profile",
            "",
            f"- Browser: `{_table_cell(profile.get('browser', ''))}`",
            f"- Viewport: `{_table_cell(profile.get('viewport_width', ''))}x{_table_cell(profile.get('viewport_height', ''))}`",
            f"- Full page: `{str(profile.get('full_page', False)).lower()}`",
            f"- Input URL: `{_table_cell(profile.get('input_url', ''))}`",
            f"- Output path: `{_table_cell(profile.get('output_path', ''))}`",
            "",
            "## Exact Commands",
            "",
        ]
    )
    for step in guide.get("capture_steps", []):
        lines.append(
            "{step}. {title}: `{command}`".format(
                step=_table_cell(step.get("step", "")),
                title=_table_cell(step.get("title", "")),
                command=_table_cell(step.get("command", "")),
            )
        )

    lines.extend(
        [
            "",
            "## Source Artifact Hashes",
            "",
            "| Role | Path | Status | Format | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for artifact in guide.get("source_artifacts", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Screenshot Hashes",
            "",
            "| Role | Path | Status | Format | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for artifact in guide.get("screenshot_artifacts", []):
        lines.append(_artifact_row(artifact))

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- Present: {coverage.get('present', 0)} of {coverage.get('expected', 0)}",
            f"- Complete: {str(coverage.get('complete', False)).lower()}",
            "- Missing: "
            + (
                ", ".join(_code_span(path) for path in coverage.get("missing", []))
                or "none"
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def write_screenshot_guide(
    manifest_json: Path,
    markdown_path: Path,
    json_path: Path,
    screenshot_path: str = DEFAULT_SCREENSHOT_PATH,
) -> dict[str, Path]:
    manifest = _read_json(manifest_json)
    guide = build_screenshot_guide(manifest, manifest_json.parent, screenshot_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_screenshot_guide_markdown(guide), encoding="utf-8")
    json_path.write_text(render_screenshot_guide_json(guide), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _artifact_entry(output_dir: Path, relative_path: str, role: str, purpose: str) -> dict:
    path = output_dir / relative_path
    result = {
        "role": role,
        "path": relative_path,
        "purpose": purpose,
        "status": "missing",
        "format": _format_from_path(relative_path),
        "bytes": "n/a",
        "sha256": "n/a",
    }
    if path.is_file():
        content = path.read_bytes()
        result.update(
            {
                "status": "present",
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return result


def _coverage(artifacts: list[dict]) -> dict:
    present_count = sum(1 for item in artifacts if item["status"] == "present")
    return {
        "present": present_count,
        "expected": len(artifacts),
        "complete": present_count == len(artifacts),
        "missing": [item["path"] for item in artifacts if item["status"] != "present"],
    }


def _artifact_row(entry: dict) -> str:
    return "| {role} | {path} | {status} | {format} | {bytes} | `{sha256}` |".format(
        role=_table_cell(entry.get("role", "")),
        path=_markdown_link(entry.get("path", "")),
        status=_table_cell(entry.get("status", "")),
        format=_table_cell(entry.get("format", "")),
        bytes=_table_cell(entry.get("bytes", "n/a")),
        sha256=_table_cell(entry.get("sha256", "n/a")),
    )


def _format_from_path(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "markdown"
    if suffix == ".html":
        return "html"
    if suffix == ".png":
        return "png"
    return suffix.lstrip(".") or "unknown"


def _dashboard_file_url(output_dir: Path) -> str:
    dashboard_path = output_dir / "dashboard.html"
    if dashboard_path.is_absolute():
        return dashboard_path.as_uri()
    return f"file://$PWD/{dashboard_path.as_posix()}"


def _shell_arg(value: str) -> str:
    if "$PWD" in value and all(char not in value for char in " \t\n'\""):
        return value
    return shlex.quote(value)


def _display_path(path: Path) -> str:
    return path.as_posix()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown_link(path: str) -> str:
    label = _table_cell(path).replace("[", "\\[").replace("]", "\\]")
    href = quote(path, safe="/._-#")
    return f"[{label}]({href})"


def _table_cell(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _code_span(value: object) -> str:
    return "`{}`".format(_table_cell(value).replace("`", "\\`"))
