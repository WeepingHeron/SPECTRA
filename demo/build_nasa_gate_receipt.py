#!/usr/bin/env python3
"""Export the bounded NASA local-snapshot gate result for the Product demo."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_source_adapter.nasa_snapshot_gate import evaluate_nasa_snapshot  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/nasa-snapshot-gate-receipt.json"
FIXTURES = ROOT / "tests/source_adapters/fixtures"
CONTROL_NOW = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)


def build_receipt() -> dict:
    candidate = json.loads(
        (FIXTURES / "nasa-snapshot-control.json").read_text(encoding="utf-8")
    )
    content = (FIXTURES / "nasa-snapshot-control.txt").read_bytes()
    return evaluate_nasa_snapshot(candidate, content, now=CONTROL_NOW)


def canonical_bytes(payload: dict) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(build_receipt()))
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
