#!/usr/bin/env python3
"""Export the bounded H08 exact-part readiness receipt for the Product demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_parts_adapter import assess_exact_part_readiness  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/exact-part-readiness-receipt.json"


def synthetic_control_projection() -> dict:
    return {
        "candidate_class": "SYNTHETIC_CONTROL",
        "bom_approval": {},
        "identity": {"identity_status": "PARTIAL_UNRESOLVED"},
        "artifact_manifest": {},
        "rights": [],
        "events": [],
        "applicability": {},
        "review": {},
        "requested_outcome": {
            "use_status": "NOT_FOR_DECISION",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
        },
    }


def build_receipt() -> dict:
    return assess_exact_part_readiness(synthetic_control_projection())


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
