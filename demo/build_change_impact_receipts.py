#!/usr/bin/env python3
"""Build deterministic synthetic HW-SW change-impact receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_change_adapter import classify_change_impact  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/change-impact-receipts.json"


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def projection_hash(value: dict) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def cad_projection(change_axes: list[str]) -> dict:
    material = {
        "change_axes": change_axes,
        "linkage_status": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    return {"receipt_sha256": projection_hash(material), **material}


def revision_projection(revision_axes: list[str]) -> dict:
    material = {
        "revision_axes": revision_axes,
        "dependency_status": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    return {"revision_sha256": projection_hash(material), **material}


def input_projection(
    cad_axes: list[str], revision_axes: list[str], gap_codes: list[str]
) -> dict:
    return {
        "change_class": "SYNTHETIC_CONTROL",
        "cad_change_receipt": cad_projection(cad_axes),
        "mitigation_policy_revision": revision_projection(revision_axes),
        "evidence_gap_codes": gap_codes,
        "requested_outcome": {
            "impact_status": "REVIEW_REQUIRED",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
            "used_for_decision": False,
        },
    }


def build_bundle() -> dict:
    scenarios = [
        (
            "CAD_CHANGE_CONTROL",
            input_projection(["GEOMETRY_REVISION"], [], []),
        ),
        (
            "HW_SW_POLICY_CONTROL",
            input_projection(
                [],
                [
                    "HARDWARE_MITIGATION",
                    "SOFTWARE_MITIGATION",
                    "ASSURANCE_POLICY",
                ],
                [],
            ),
        ),
        (
            "COMBINED_GAP_CONTROL",
            input_projection(
                ["COMPONENT_POSITION", "MATERIAL_THICKNESS_MAPPING"],
                ["SOFTWARE_MITIGATION", "ASSURANCE_POLICY"],
                ["STAGE3_INPUT_UNAVAILABLE", "STAGE4_INPUT_UNAVAILABLE"],
            ),
        ),
    ]
    return {
        "bundle_format": "spectra-change-impact-receipts-demo-v1",
        "data_class": "SYNTHETIC_CONTROL",
        "receipts": [
            {"scenario_id": scenario_id, "receipt": classify_change_impact(payload)}
            for scenario_id, payload in scenarios
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(build_bundle()) + b"\n")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
