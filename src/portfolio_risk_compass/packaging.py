"""Packaging audit and release artifact manifest helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

from . import __version__

DEFAULT_RELEASE_OUTPUTS_DIR = Path("examples/outputs")
DEFAULT_RELEASE_MANIFEST_JSON = DEFAULT_RELEASE_OUTPUTS_DIR / "release_manifest.json"
DEFAULT_RELEASE_MANIFEST_MARKDOWN = DEFAULT_RELEASE_OUTPUTS_DIR / "release_manifest.md"
DEFAULT_DOCS_EXPORT = DEFAULT_RELEASE_OUTPUTS_DIR / "docs_export.md"
TEST_COMMAND_DISPLAY = ["python", "-m", "unittest", "discover", "-s", "tests"]

_PACKAGING_ITEMS = (
    ("pyproject.toml", "pyproject.toml"),
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
    ("package module", "src/portfolio_risk_compass/__init__.py"),
    ("tests", "tests"),
    ("example fixtures", "examples/fixtures"),
    ("example outputs", "examples/outputs"),
)


def build_package_audit(
    root: Path,
    command_count: int,
    run_tests: bool = False,
) -> dict:
    """Build a repository packaging audit report."""

    root = root.resolve()
    report = {
        "schema_version": 1,
        "package": "portfolio-risk-compass",
        "version": __version__,
        "command_count": command_count,
        "fixture_count": _count_files(root / "examples/fixtures"),
        "output_artifact_count": _count_files(root / "examples/outputs"),
        "missing_packaging_items": _missing_packaging_items(root),
        "tests": {
            "run": False,
            "command": TEST_COMMAND_DISPLAY,
        },
    }
    if run_tests:
        report["tests"].update(_run_tests(root))
    return report


def render_package_audit_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_package_audit_markdown(report: dict) -> str:
    lines = [
        "# Package Audit",
        "",
        f"- Package: {report['package']}",
        f"- Version: {report['version']}",
        f"- Command count: {report['command_count']}",
        f"- Fixture count: {report['fixture_count']}",
        f"- Output artifact count: {report['output_artifact_count']}",
        "",
        "## Missing Packaging Items",
        "",
    ]
    missing = report["missing_packaging_items"]
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- None")

    tests = report["tests"]
    lines.extend(["", "## Tests", ""])
    if tests["run"]:
        status = "passed" if tests["passed"] else "failed"
        lines.append(f"- Status: {status}")
        lines.append(f"- Return code: {tests['returncode']}")
    else:
        lines.append("- Status: not run")
    return "\n".join(lines) + "\n"


def build_release_manifest(
    outputs_dir: Path = DEFAULT_RELEASE_OUTPUTS_DIR,
    exclude_paths: Iterable[Path] = (),
) -> dict:
    """Build a deterministic artifact inventory for an output directory."""

    display_outputs_dir = outputs_dir.as_posix()
    resolved_outputs_dir = outputs_dir.resolve()
    excludes = {path.resolve() for path in exclude_paths}
    artifacts = []
    if resolved_outputs_dir.exists():
        for path in sorted(p for p in resolved_outputs_dir.rglob("*") if p.is_file()):
            if path.resolve() in excludes:
                continue
            artifacts.append(_artifact_entry(resolved_outputs_dir, path))

    return {
        "schema_version": 1,
        "bundle": "portfolio-risk-compass-release",
        "outputs_dir": display_outputs_dir,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def render_release_manifest_json(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def render_release_manifest_markdown(manifest: dict) -> str:
    lines = [
        "# Release Manifest",
        "",
        f"- Outputs directory: {manifest['outputs_dir']}",
        f"- Artifact count: {manifest['artifact_count']}",
        "",
        "| Path | Format | Bytes | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for artifact in manifest["artifacts"]:
        lines.append(
            "| {path} | {format} | {bytes} | `{sha256}` |".format(**artifact)
        )
    return "\n".join(lines) + "\n"


def write_release_manifest(
    outputs_dir: Path,
    json_path: Path,
    markdown_path: Path,
) -> dict:
    manifest = build_release_manifest(
        outputs_dir,
        exclude_paths=(json_path, markdown_path, _default_docs_export_for(outputs_dir)),
    )
    _write_text(json_path, render_release_manifest_json(manifest))
    _write_text(markdown_path, render_release_manifest_markdown(manifest))
    return manifest


def _default_docs_export_for(outputs_dir: Path) -> Path:
    return outputs_dir / DEFAULT_DOCS_EXPORT.name


def _artifact_entry(outputs_dir: Path, path: Path) -> dict:
    content = path.read_bytes()
    return {
        "path": path.relative_to(outputs_dir).as_posix(),
        "format": _artifact_format(path),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _artifact_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "md":
        return "markdown"
    if suffix == "html":
        return "html"
    if suffix == "json":
        return "json"
    return suffix or "unknown"


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def _missing_packaging_items(root: Path) -> list[str]:
    missing = []
    for name, relative_path in _PACKAGING_ITEMS:
        if not (root / relative_path).exists():
            missing.append(name)
    return missing


def _run_tests(root: Path) -> dict:
    env = os.environ.copy()
    src_path = str(root / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else src_path + os.pathsep + env["PYTHONPATH"]
    )
    command: Sequence[str] = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
    ]
    result = subprocess.run(
        command,
        check=False,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    return {
        "run": True,
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
