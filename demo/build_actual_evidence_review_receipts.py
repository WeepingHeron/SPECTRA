#!/usr/bin/env python3
"""Export value-redacted actual-candidate review receipts for the demo.

The output is not an environment contract or part Evidence Packet.  It contains
only categorical gate results that are already fail-closed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "demo/data/actual-evidence-review-receipts.json"


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def build_receipt(environment_record: dict[str, Any], part_record: dict[str, Any]) -> dict[str, Any]:
    internal = environment_record.get("internal_consistency")
    independent = environment_record.get("independent_crosscheck")
    _require(environment_record.get("record_kind") == "SPECTRA_SPENVIS_CROSSCHECK_CANDIDATE", "ENVIRONMENT_RECORD_KIND_INVALID")
    _require(environment_record.get("decision_use") is False, "ENVIRONMENT_DECISION_USE_FORBIDDEN")
    _require(environment_record.get("issuance_status") == "HOLD_NOT_ISSUED", "ENVIRONMENT_ISSUANCE_STATUS_FORBIDDEN")
    _require(isinstance(internal, dict) and internal.get("dose_values_included") is False, "ENVIRONMENT_VALUE_REDACTION_REQUIRED")
    _require(isinstance(independent, dict) and independent.get("status") == "NOT_EVALUATED", "ENVIRONMENT_CROSSCHECK_CLAIM_FORBIDDEN")

    _require(part_record.get("candidate_class") == "ACTUAL_CANDIDATE", "PART_RECORD_CLASS_INVALID")
    _require(part_record.get("readiness_status") == "HOLD_NOT_ISSUED", "PART_READINESS_STATUS_FORBIDDEN")
    _require(part_record.get("assurance_decision") == "HOLD", "PART_ASSURANCE_STATUS_FORBIDDEN")
    _require(part_record.get("used_for_decision") is False, "PART_DECISION_USE_FORBIDDEN")

    part_blockers = part_record.get("blocker_codes")
    event_coverage = part_record.get("event_coverage")
    _require(isinstance(part_blockers, list) and all(isinstance(code, str) for code in part_blockers), "PART_BLOCKERS_INVALID")
    _require(isinstance(event_coverage, list), "PART_EVENT_COVERAGE_INVALID")

    return {
        "contract_version": "ACTUAL_EVIDENCE_REVIEW_RECEIPTS_1.0.0",
        "data_class": "ACTUAL_REVIEW_CANDIDATE",
        "decision_use": False,
        "case_context": {
            "case_label": "TI exact-part + SPENVIS environment review",
            "environment": {
                "provider": "SPENVIS",
                "project_label": "SPECTRA_MVP_LEO_001",
            },
            "part": {
                "manufacturer": "Texas Instruments",
                "orderable_part_number": "5962L1420901VXC",
                "evidence_documents": ["SLLK019", "SLLA381"],
                "reported_candidate_events": ["TID", "SEL"],
                "unresolved_events": ["SEU", "SEB", "SEGR"],
            },
        },
        "environment": {
            "source_kind": "SPENVIS_PRIVATE_BUNDLE",
            "internal_consistency": internal.get("status"),
            "internal_check_count": internal.get("check_count"),
            "independent_crosscheck": independent.get("status"),
            "issuance_status": environment_record.get("issuance_status"),
            "assurance_decision": environment_record.get("assurance_decision"),
            "dose_values_included": False,
            "blocker_codes": environment_record.get("error_codes", []),
        },
        "exact_part": {
            "source_kind": "TI_PUBLIC_REPORT_CANDIDATE",
            "processing_status": part_record.get("processing_status"),
            "readiness_status": part_record.get("readiness_status"),
            "identity_status": part_record.get("identity_status"),
            "applicability_status": part_record.get("applicability_status"),
            "event_coverage": event_coverage,
            "blocker_count": len(part_blockers),
            "blocker_codes": part_blockers,
            "assurance_decision": "HOLD",
            "used_for_decision": False,
        },
        "source_acknowledgements": [
            {
                "label": "SPENVIS — ESA/BIRA-IASB",
                "url": "https://www.spenvis.oma.be/",
                "display_scope": "SERVICE_ACKNOWLEDGEMENT_AND_LOCATOR_ONLY",
            },
            {
                "label": "Texas Instruments SN55HVD233-SP radiation reports",
                "url": "https://www.ti.com/product/SN55HVD233-SP",
                "display_scope": "PUBLIC_LOCATOR_AND_CATEGORICAL_GATE_STATUS_ONLY",
            },
        ],
        "overall": {
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
            "used_for_decision": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment-record", required=True, type=Path)
    parser.add_argument("--part-record", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        receipt = build_receipt(_load_object(args.environment_record), _load_object(args.part_record))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "data_class": receipt["data_class"],
                "environment": receipt["environment"]["issuance_status"],
                "exact_part": receipt["exact_part"]["readiness_status"],
                "overall": receipt["overall"]["assurance_decision"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
