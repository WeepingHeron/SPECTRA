#!/usr/bin/env python3
"""Run the external environment intake gate tests."""

from __future__ import annotations

import unittest
from pathlib import Path


def main() -> int:
    suite = unittest.defaultTestLoader.discover(
        str(Path(__file__).resolve().parent), pattern="test_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
