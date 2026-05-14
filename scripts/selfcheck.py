#!/usr/bin/env python3
"""Run the repository verification suite."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src_path = str(root / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else src_path + os.pathsep + env["PYTHONPATH"]
    )
    with tempfile.TemporaryDirectory() as skill_target:
        checks = [
            [
                sys.executable,
                "scripts/sync_local_skill.py",
                "--target-dir",
                skill_target,
            ],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            [sys.executable, "-m", "portfolio_risk_compass", "demo-bundle"],
            [
                sys.executable,
                "-m",
                "portfolio_risk_compass",
                "dashboard",
                "examples/outputs/index.json",
                "examples/outputs/dashboard.html",
            ],
            [sys.executable, "-m", "portfolio_risk_compass", "release-manifest"],
            [sys.executable, "scripts/privacy_scan.py"],
            [sys.executable, "-m", "portfolio_risk_compass", "package-audit"],
        ]
        for command in checks:
            result = subprocess.run(command, check=False, cwd=root, env=env)
            if result.returncode != 0:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
