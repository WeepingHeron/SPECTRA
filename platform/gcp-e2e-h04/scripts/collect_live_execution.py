#!/usr/bin/env python3
"""Collect one fixed-resource H07 read-only execution receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.spectra_gcp_adapter import collect_read_only_execution  # noqa: E402


DEFAULT_ANCHOR = ROOT / "platform/gcp-e2e-h04/live-deployment-anchor.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution", required=True)
    parser.add_argument("--anchor", type=Path, default=DEFAULT_ANCHOR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    anchor = json.loads(args.anchor.read_text(encoding="utf-8"))
    receipt = collect_read_only_execution(
        args.execution,
        trusted_deployment=anchor,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "processing_status": receipt["processing_status"],
                "connector_status": receipt["connector_status"],
                "assurance_decision": receipt["assurance_decision"],
                "stable_codes": receipt["stable_codes"],
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )
    return 0 if receipt["processing_status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
