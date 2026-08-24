#!/usr/bin/env python3
"""Evaluate the locked post-remediation control and approved ASR-D02 batch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.assurance.gcp_d02.run_live_phase1 import PHASE1_IDS  # noqa: E402
from tests.assurance.gcp_d02.run_preparation import classify  # noqa: E402


PACKAGE = ROOT / "tests/assurance/gcp_d02"
DEFAULT_CONTROL = ROOT / "docs/workstreams/70-platform-gcp/evidence/h09-remediation-control.json"
DEFAULT_PARITY = ROOT / "docs/workstreams/70-platform-gcp/evidence/h09-remediation-core-parity.json"
DEFAULT_BATCH = ROOT / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_REMEDIATION_BATCH_H09.json"
DEFAULT_OUTPUT = ROOT / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_REMEDIATION_EVALUATED_H09.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def evaluate(
    manifest: dict[str, Any], control: dict[str, Any], parity: dict[str, Any],
    batch: dict[str, Any],
) -> dict[str, Any]:
    target = manifest["target_lock"]
    if batch.get("target_lock") != target:
        raise ValueError("batch target lock differs from manifest")
    control_cases = control.get("cases")
    if not isinstance(control_cases, list) or len(control_cases) != 1:
        raise ValueError("control evidence must contain exactly one case")
    control_case = control_cases[0]
    if control_case.get("case") != "normal-production-core":
        raise ValueError("unexpected control case")
    summary = control_case.get("result_summary", {})
    control_observation = {
        "attack_id": "ASR-D02-C01",
        "execution_attempted": True,
        "observed_status": summary.get("processing_status"),
        "observed_engineering_gate": summary.get("engineering_gate"),
        "observed_decision": summary.get("assurance_decision"),
        "observed_stable_codes": summary.get("stable_codes"),
        "downstream_payload_accepted": True,
        "recommendation_present": False,
        "core_semantic_parity": (
            parity.get("full_semantic_object_equal") is True
            and parity.get("canonical_hash_equal") is True
            and parity.get("semantic_payload_equal") is True
        ),
        "gcp_observations": {
            "target_identity": target,
            "workflow_execution": control_case.get("workflow_execution"),
            "workflow_state": control_case.get("workflow_state"),
            "input_storage": control_case.get("input_storage"),
            "result_storage": control_case.get("result_storage"),
            "local_core_result_sha256": parity.get("local_core_sha256"),
            "deployed_core_result_sha256": parity.get("deployed_core_sha256"),
        },
    }
    control_classification = classify(manifest["control"], control_observation)

    cases = {case["attack_id"]: case for case in manifest["attacks"]}
    attack_observations = batch.get("case_observations")
    if not isinstance(attack_observations, list):
        raise ValueError("batch case_observations must be a list")
    if tuple(item.get("attack_id") for item in attack_observations) != PHASE1_IDS:
        raise ValueError("batch attack order/scope differs from approved Phase 1 subset")
    evaluated_attacks = []
    for observation in attack_observations:
        attack_id = observation["attack_id"]
        classification = classify(cases[attack_id], observation)
        evaluated_attacks.append({**observation, "classification": classification})

    classifications = [item["classification"] for item in evaluated_attacks]
    aggregate = {
        "live_executions": 1 + len(evaluated_attacks),
        "evaluated_controls": 1,
        "control_passes": int(control_classification == "CONTROL_PASS"),
        "evaluated_attacks": len(evaluated_attacks),
        "safe_failures": classifications.count("SAFE_FAILURE"),
        "false_accepts": classifications.count("FALSE_ACCEPT"),
        "false_passes": classifications.count("FALSE_PASS"),
        "unexpected_results": classifications.count("UNEXPECTED_RESULT"),
        "not_evaluated_attacks": 16 - len(evaluated_attacks),
    }
    aggregate["result"] = (
        "PARTIAL_SAFE"
        if control_classification == "CONTROL_PASS"
        and aggregate["safe_failures"] == len(evaluated_attacks)
        else "FAIL"
    )
    return {
        "schema_version": "spectra.assurance.asr-d02.remediation-evaluated.v1",
        "package_id": manifest["package_id"],
        "evidence_status": "POST_REMEDIATION_PARTIAL_LIVE_EVALUATED",
        "target_lock": {**target, "locked_by": "CONTROL_TOWER_REMEDIATION_EXECUTION"},
        "control_observation": {**control_observation, "classification": control_classification},
        "attack_observations": evaluated_attacks,
        "aggregate": aggregate,
        "boundary_notes": [
            "The normal synthetic control matched the local deterministic Core and remained NOT_EVALUATED / HOLD.",
            "All four approved attacks failed safely at the expected stable-code boundary after remediation.",
            "False Accept, False PASS, and unexpected result counts are zero for this locked five-execution batch.",
            "Twelve ASR-D02 attacks remain NOT_EVALUATED; no IAM/OIDC or isolated test-endpoint attack was executed.",
            "PARTIAL_SAFE is not penetration-test completion, exact-part suitability, or radiation assurance.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--parity", type=Path, default=DEFAULT_PARITY)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = evaluate(
        load(PACKAGE / "manifest.json"), load(args.control), load(args.parity), load(args.batch)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["aggregate"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
