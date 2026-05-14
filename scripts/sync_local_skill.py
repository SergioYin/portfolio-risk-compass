#!/usr/bin/env python3
"""Copy the public agent skill into a configurable local skills directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence


DEFAULT_SKILL_NAME = "portfolio-risk-compass"
DEFAULT_SOURCE = Path("skills/agent/portfolio-risk-compass/SKILL.md")
PUBLIC_README_LINK = "[README](../../../README.md)"


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    source = _resolve_from_root(root, args.source)
    target_dir = _resolve_user_path(args.target_dir)
    target_skill_dir = target_dir / args.skill_name
    target = target_skill_dir / "SKILL.md"

    text = source.read_text(encoding="utf-8")
    adapted = adapt_skill_text(text, root / "README.md", target_skill_dir)

    if args.dry_run:
        print(f"would write {target}")
        return 0

    target_skill_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(adapted, encoding="utf-8")
    print(f"wrote {target}")
    return 0


def adapt_skill_text(text: str, readme_path: Path, target_skill_dir: Path) -> str:
    """Return skill text with repository links adapted for the target location."""

    relative_readme = _relative_link(readme_path, target_skill_dir)
    return text.replace(PUBLIC_README_LINK, f"[README]({relative_readme})")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy skills/agent/portfolio-risk-compass/SKILL.md into a local "
            "skills directory and adapt repository-relative links."
        )
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        type=Path,
        help="Local skills root to receive the copied skill.",
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        type=Path,
        help="Public skill file to copy, relative to the repository root by default.",
    )
    parser.add_argument(
        "--skill-name",
        default=DEFAULT_SKILL_NAME,
        help="Directory name to create under --target-dir.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the target path without writing files.",
    )
    return parser


def _resolve_from_root(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _resolve_user_path(path: Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(path)))).resolve()


def _relative_link(path: Path, start: Path) -> str:
    relative = os.path.relpath(path.resolve(), start.resolve())
    return Path(relative).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
