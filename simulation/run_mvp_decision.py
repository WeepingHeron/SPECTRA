#!/usr/bin/env python3
"""Run the deterministic MVP decision case and export result or EvidencePacket JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import MvpDecisionError, canonical_result_json, run_mvp_decision  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        default=str(ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json"),
    )
    parser.add_argument(
        "--evidence-packet", choices=("baseline", "variant"),
        help="Export only the selected generated EvidencePacket.",
    )
    parser.add_argument("--summary", action="store_true", help="Print a compact deterministic summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        case = load(Path(args.input))
        model = load(ROOT / "simulation/config/synthetic-model.json")
        result = run_mvp_decision(case, model)
    except (OSError, json.JSONDecodeError, MvpDecisionError) as exc:
        if isinstance(exc, MvpDecisionError):
            error_code = exc.code
            error_message = exc.message
        elif isinstance(exc, json.JSONDecodeError):
            error_code = "INVALID_JSON_INPUT"
            error_message = str(exc)
        else:
            error_code = "INPUT_FILE_ERROR"
            error_message = str(exc)
        print(json.dumps({
            "processing_status": "INVALID_INPUT",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "error_code": error_code,
            "error": error_message,
        }, sort_keys=True), file=sys.stderr)
        return 2
    if args.evidence_packet:
        print(canonical_result_json(result[args.evidence_packet]["evidence_packet"]))
    elif args.summary:
        summary = {
            "case_id": result["case_id"],
            "baseline": {
                "ecc_enabled": result["baseline"]["ecc_enabled"],
                "policy": result["baseline"]["policy_approval_status"],
                "residual": result["baseline"]["metrics"]["residual_logical_errors"]["value"],
                "engineering": result["baseline"]["engineering_gate"],
                "assurance": result["baseline"]["assurance_decision"],
            },
            "variant": {
                "ecc_enabled": result["variant"]["ecc_enabled"],
                "policy": result["variant"]["policy_approval_status"],
                "residual": result["variant"]["metrics"]["residual_logical_errors"]["value"],
                "engineering": result["variant"]["engineering_gate"],
                "assurance": result["variant"]["assurance_decision"],
            },
            "change_impact_id": result["change_impact"]["impact_id"],
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(canonical_result_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
