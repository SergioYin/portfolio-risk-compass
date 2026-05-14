#!/usr/bin/env python3
"""Scan repository text for local/private terms and token-like strings."""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


SKIPPED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
SKIPPED_SUFFIXES = {
    ".gif",
    ".ico",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".png",
    ".pyc",
    ".sqlite",
    ".zip",
}
TOKEN_RULES = {
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_bearer": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "private_key_header": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.root.resolve()
    terms = _private_terms(args.term)
    findings = list(scan_repository(root, terms, exclude_patterns=args.exclude))

    for finding in findings:
        print(f"{finding.path.relative_to(root)}:{finding.line}: {finding.rule}")

    if findings:
        print(f"privacy scan failed: {len(findings)} finding(s)")
        return 1

    print("privacy scan passed")
    return 0


def scan_repository(
    root: Path,
    terms: Iterable[str],
    exclude_patterns: Sequence[str] = (),
) -> Iterator[Finding]:
    term_rules = [
        (f"private_term:{index + 1}", re.compile(re.escape(term), re.IGNORECASE))
        for index, term in enumerate(dict.fromkeys(term for term in terms if term))
    ]
    for path in _iter_text_paths(root, exclude_patterns=exclude_patterns):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule_name, pattern in term_rules:
                if pattern.search(line):
                    yield Finding(path, line_number, rule_name)
            for rule_name, pattern in TOKEN_RULES.items():
                if pattern.search(line):
                    yield Finding(path, line_number, rule_name)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Scan repository text for private local paths, local usernames, and "
            "token-like patterns. Findings report locations only, not matched text."
        )
    )
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--term",
        action="append",
        default=[],
        help="Additional private term to flag. Can be supplied more than once.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help=(
            "Relative path glob to skip, for known public fixtures. Can be supplied "
            "more than once."
        ),
    )
    return parser


def _private_terms(extra_terms: Sequence[str]) -> list[str]:
    terms = list(extra_terms)
    home = os.environ.get("HOME")
    if home:
        terms.append(home)
    user = os.environ.get("USER") or os.environ.get("USERNAME")
    if user and user.lower() not in {"root", "user", "runner"}:
        terms.append(user)
    return terms


def _iter_text_paths(root: Path, exclude_patterns: Sequence[str] = ()) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if any(part in SKIPPED_DIRS for part in relative_path.parts):
            continue
        if path.suffix.lower() in SKIPPED_SUFFIXES:
            continue
        if any(relative_path.match(pattern) for pattern in exclude_patterns):
            continue
        yield path


if __name__ == "__main__":
    raise SystemExit(main())
