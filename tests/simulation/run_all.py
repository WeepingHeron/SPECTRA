#!/usr/bin/env python3
"""One-command Stage 1 contract + Stage 2 simulation verification."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    contract = subprocess.run(
        [sys.executable, str(ROOT / "tests/schema/validate_contracts.py")],
        cwd=ROOT,
        check=False,
    )
    if contract.returncode:
        return contract.returncode
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests/simulation"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    demo = subprocess.run([sys.executable, str(ROOT / "simulation/run_demo.py")], cwd=ROOT, check=False)
    if demo.returncode:
        return demo.returncode
    mvp_demo = subprocess.run(
        [sys.executable, str(ROOT / "simulation/run_mvp_decision.py"), "--summary"],
        cwd=ROOT,
        check=False,
    )
    return mvp_demo.returncode


if __name__ == "__main__":
    raise SystemExit(main())
