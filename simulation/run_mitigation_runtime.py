#!/usr/bin/env python3
"""Evaluate one H06 WATCHDOG, TMR, or SEL_PROTECTION EvidencePacket."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import canonical_runtime_json, evaluate_runtime_mitigation  # noqa: E402
from spectra_sim.contracts import load_contract_fixture  # noqa: E402

DEFAULT_FIXTURE = ROOT / "tests/schema/fixtures/valid/synthetic-v2-hold.json"


def _load_input(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict) and set(value) == {"base", "operations"}:
        return load_contract_fixture(path.resolve())
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--summary", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        packet = _load_input(Path(args.input))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = evaluate_runtime_mitigation({"input_load_error": str(exc)})
    else:
        result = evaluate_runtime_mitigation(packet)
    if args.summary:
        output = {
            "assurance_decision": result["assurance_decision"],
            "engineering_gate": result["engineering_gate"],
            "method": result["method"],
            "processing_status": result["processing_status"],
            "projection": result["computed_projection"],
            "result_id": result["result_id"],
            "stable_error_codes": result["stable_error_codes"],
        }
        print(canonical_runtime_json(output))
    else:
        print(canonical_runtime_json(result))
    return 0 if result["processing_status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
