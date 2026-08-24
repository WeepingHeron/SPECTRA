#!/usr/bin/env python3
"""Assemble the approved ASR-D02 Phase 1 observations into one review file."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.assurance.gcp_d02.run_preparation import classify  # noqa: E402


PACKAGE = ROOT / "tests/assurance/gcp_d02"
EVIDENCE = ROOT / "docs/workstreams/60-assurance-evals/evidence"
DEFAULT_OUTPUT = EVIDENCE / "ASR_D02_DEPLOYED_GCP_PHASE1_EVALUATED_H09.json"
D02_EXECUTION = "e1a73100-1db2-4602-b86b-46e6b3b49551"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def run_json(command: list[str]) -> dict[str, Any]:
    parsed = json.loads(run([*command, "--format=json"]))
    if not isinstance(parsed, dict):
        raise RuntimeError("gcloud JSON output must be an object")
    return parsed


def sha256_uri(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


def d02_observation(
    *, project: str, region: str, workflow_name: str, target: dict[str, Any],
    endpoints: dict[str, str],
) -> dict[str, Any]:
    execution = run_json([
        "gcloud", "workflows", "executions", "describe", D02_EXECUTION,
        "--workflow", workflow_name, "--project", project, "--location", region,
    ])
    if execution.get("state") != "FAILED" or execution.get("workflowRevisionId") != target["workflow_revision"]:
        raise RuntimeError("D02-02 execution identity or state differs from the observed failure")
    argument = json.loads(execution["argument"])
    object_url = f"gs://{argument['bucket']}/{argument['input_object']}"
    metadata = run_json([
        "gcloud", "storage", "objects", "describe", object_url, "--project", project,
    ])
    actual_generation = str(metadata["generation"])
    with tempfile.TemporaryDirectory(prefix="spectra-d02-02-") as temp_dir:
        path = Path(temp_dir) / "input.json"
        run([
            "gcloud", "storage", "cp", f"{object_url}#{actual_generation}", str(path),
            "--project", project,
        ])
        downloaded_hash = sha256_uri(path.read_bytes())
    correlation_id = f"spectra-h05-{D02_EXECUTION}"
    return {
        "attack_id": "ASR-D02-02",
        "execution_attempted": True,
        "observed_status": "WORKFLOW_FAILED",
        "observed_engineering_gate": "NOT_EVALUATED",
        "observed_decision": "HOLD",
        "observed_stable_codes": ["WORKFLOW_STORAGE_LOOKUP_FAILED"],
        "downstream_payload_accepted": False,
        "recommendation_present": False,
        "core_semantic_parity": None,
        "gcp_observations": {
            "target_identity": target,
            "workflow_execution": execution["name"],
            "workflow_state": execution["state"],
            "correlation_id": correlation_id,
            "input_object": argument["input_object"],
            "input_generation_requested": str(argument["input_generation"]),
            "input_generation_observed": "OBJECT_NOT_FOUND_AT_REQUESTED_GENERATION",
            "downloaded_body_sha256": downloaded_hash,
            "metadata_sha256": metadata["custom_fields"]["sha256"],
            "expected_sha256": argument["input_sha256"],
            "resolved_agent_endpoints": endpoints,
            "agent_revisions": {
                "mission": target["mission_revision"],
                "parts": target["parts_revision"],
                "assurance": target["assurance_revision"],
            },
            "agent_results": {},
            "structured_log_refs": ["NO_AGENT_INVOCATION_GET_INPUT_METADATA_404"],
            "result_object": "NOT_CREATED",
            "result_generation": "NOT_CREATED",
            "downloaded_result_sha256": "NOT_CREATED",
            "locked_generation": actual_generation,
            "requested_generation": str(argument["input_generation"]),
            "observed_generation": "OBJECT_NOT_FOUND_AT_REQUESTED_GENERATION",
            "body_forwarded_to_agents": False,
        },
        "raw_workflow_error": execution["error"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="iceu-686")
    parser.add_argument("--region", default="asia-northeast3")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = load(PACKAGE / "manifest.json")
    reconciled = load(EVIDENCE / "ASR_D02_EXISTING_EVIDENCE_RECONCILIATION.json")
    selected = {
        "ASR-D02-04": load(EVIDENCE / "ASR_D02_DEPLOYED_GCP_D02_04_RETRY.json")["case_observations"][0],
        "ASR-D02-05": load(EVIDENCE / "ASR_D02_DEPLOYED_GCP_D02_05_RETRY.json")["case_observations"][0],
        "ASR-D02-10": load(EVIDENCE / "ASR_D02_DEPLOYED_GCP_D02_10.json")["case_observations"][0],
    }
    endpoints = selected["ASR-D02-10"]["gcp_observations"]["resolved_agent_endpoints"]
    selected["ASR-D02-02"] = d02_observation(
        project=args.project, region=args.region,
        workflow_name=manifest["target_lock"]["workflow_name"],
        target=manifest["target_lock"], endpoints=endpoints,
    )
    cases = {manifest["control"]["attack_id"]: manifest["control"]}
    cases.update({case["attack_id"]: case for case in manifest["attacks"]})
    observations = []
    classifications: dict[str, str] = {}
    for base in reconciled["case_observations"]:
        attack_id = base["attack_id"]
        observation = selected.get(attack_id, base)
        if observation.get("execution_attempted") is True:
            classification = classify(cases[attack_id], observation)
            observation = {**observation, "classification": classification}
            classifications[attack_id] = classification
        observations.append(observation)
    evaluated_attacks = [key for key in classifications if key != "ASR-D02-C01"]
    counts = {
        "safe_failures": sum(classifications[key] == "SAFE_FAILURE" for key in evaluated_attacks),
        "false_accepts": sum(classifications[key] == "FALSE_ACCEPT" for key in evaluated_attacks),
        "false_passes": sum(classifications[key] == "FALSE_PASS" for key in evaluated_attacks),
        "unexpected_results": sum(classifications[key] == "UNEXPECTED_RESULT" for key in evaluated_attacks),
    }
    output = {
        "schema_version": "spectra.assurance.asr-d02.phase1-evaluated.v1",
        "package_id": manifest["package_id"],
        "evidence_status": "PARTIAL_LIVE_EVALUATED_WITH_FAILURES",
        "target_lock": {**manifest["target_lock"], "locked_by": "CONTROL_TOWER_PHASE1_EXECUTION"},
        "required_permissions_observed": {
            **reconciled["required_permissions_observed"],
            "workflow_execute": True,
            "storage_object_create": True,
        },
        "case_observations": observations,
        "aggregate": {
            "live_executions": 5,
            "evaluated_controls": 1,
            "evaluated_attacks": len(evaluated_attacks),
            **counts,
            "not_evaluated_attacks": 16 - len(evaluated_attacks),
            "result": "FAIL" if any(counts[key] for key in ("false_accepts", "false_passes", "unexpected_results")) else "PARTIAL_SAFE",
        },
        "nonqualifying_attempts": [
            {
                "attack_id": "ASR-D02-04",
                "execution_id": "f03b86c2-de1e-442d-9721-61c4956de409",
                "reason": "RUNNER_CANONICALIZATION_DRIFT_BLOCKED_AT_MISSION_NOT_PARTS",
            },
            {
                "attack_id": "ASR-D02-05",
                "execution_id": "dade902f-b19e-4dbd-99db-6d400b80e0fd",
                "reason": "RUNNER_CANONICALIZATION_DRIFT_BLOCKED_AT_MISSION_NOT_PARTS",
            },
        ],
        "boundary_notes": [
            "ASR-D02-04 and ASR-D02-10 failed safely at their intended boundaries.",
            "ASR-D02-05 is FALSE_ACCEPT: a changed exact orderable part number was reported as matched and consumed by Assurance, although the synthetic final decision remained HOLD.",
            "ASR-D02-02 stopped before Agents but returned Workflow 404 instead of the required stable INPUT_GENERATION_MISMATCH result, so it is UNEXPECTED_RESULT.",
            "No optimistic decision or engineering PASS was observed; False PASS count is zero for the four evaluated attacks.",
            "Twelve attacks remain NOT_EVALUATED. No IAM/OIDC probe or isolated test endpoint attack was executed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output["aggregate"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
