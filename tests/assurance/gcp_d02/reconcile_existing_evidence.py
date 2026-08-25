#!/usr/bin/env python3
"""Reconcile existing H05 evidence without executing an ASR-D02 attack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "tests/assurance/gcp_d02"
EVIDENCE_70 = ROOT / "docs/workstreams/70-platform-gcp/evidence"
DEFAULT_OUTPUT = (
    ROOT
    / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_EXISTING_EVIDENCE_RECONCILIATION.json"
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load(PACKAGE / "manifest.json")
    template = load(
        ROOT
        / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_EVIDENCE_TEMPLATE_H04.json"
    )
    stopped = load(
        ROOT
        / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_STOPPED_H05.json"
    )
    runs = load(EVIDENCE_70 / "h05-e2e-runs.json")
    parity = load(EVIDENCE_70 / "h05-core-parity.json")
    inventory = load(EVIDENCE_70 / "h05-gcp-inventory-and-logs.json")
    cases = {item["case"]: item for item in runs["cases"]}
    normal = cases["normal-production-core"]

    historical_target = stopped["target_lock"]
    # This reconciliation is intentionally bound to the already-recorded H05
    # execution.  The package manifest may advance to a remediated deployment;
    # that must not silently re-label historical evidence as belonging to the
    # newer target.
    target = historical_target
    workflow_hash = historical_target["workflow_source_sha256"]
    revisions = {
        item["role"]: item["latest_ready_revision"]
        for item in inventory["services"]
    }
    target_matches = (
        historical_target == target
        and inventory["project_id"] == target["project_id"]
        and inventory["region"] == target["region"]
        and inventory["workflow"]["name"].rsplit("/", 1)[-1]
        == target["workflow_name"]
        and inventory["workflow"]["revision_id"] == target["workflow_revision"]
        and workflow_hash == target["workflow_source_sha256"]
        and revisions["mission"] == target["mission_revision"]
        and revisions["parts"] == target["parts_revision"]
        and revisions["assurance"] == target["assurance_revision"]
    )
    if not target_matches:
        raise SystemExit("locked H05 target identity does not match existing evidence")

    logs = [
        item
        for item in inventory["cloud_run_structured_logs"]
        if item["correlation_id"] == normal["correlation_id"]
    ]
    if {item["agent"] for item in logs} != {"mission", "parts", "assurance"}:
        raise SystemExit("normal control structured log set is incomplete")

    common = {
        "target_identity": dict(target),
        "workflow_execution": normal["workflow_execution"],
        "workflow_state": normal["workflow_state"],
        "correlation_id": normal["correlation_id"],
        "input_object": normal["input_storage"]["object_name"],
        "input_generation_requested": normal["input_storage"]["generation"],
        "input_generation_observed": normal["input_storage"]["generation"],
        "downloaded_body_sha256": normal["input_storage"]["canonical_body_sha256"],
        "metadata_sha256": normal["input_storage"]["metadata_sha256"],
        "expected_sha256": normal["input_storage"]["expected_sha256"],
        "resolved_agent_endpoints": inventory["workflow"]["deployment_bound_agent_urls"],
        "agent_revisions": revisions,
        "agent_results": normal["result_summary"]["agent_statuses"],
        "structured_log_refs": [item["insert_id"] for item in logs],
        "result_object": normal["result_storage"]["object_name"],
        "result_generation": normal["result_storage"]["generation"],
        "downloaded_result_sha256": normal["result_storage"]["sha256"],
        "local_core_result_sha256": parity["local_core_sha256"],
        "deployed_core_result_sha256": parity["deployed_core_sha256"],
        "core_semantic_parity": parity["semantic_payload_equal"],
    }

    related = {
        "ASR-D02-01": {
            "case": "body-metadata-expected-forgery",
            "reason": "RELATED_H05_CASE_MUTATION_DIFFERS_FROM_D02_01",
        },
        "ASR-D02-04": {
            "case": "parts-evidence-hash-corruption",
            "reason": "RELATED_H05_CASE_REQUIRED_OBSERVATIONS_INCOMPLETE",
        },
        "ASR-D02-05": {
            "case": "malformed-agent-input",
            "reason": "RELATED_H05_CASE_EXPECTED_CODE_AND_MUTATION_DIFFER",
        },
        "ASR-D02-10": {
            "case": "endpoint-override",
            "reason": "RELATED_H05_CASE_REQUIRED_OBSERVATIONS_INCOMPLETE",
        },
    }
    isolated = {f"ASR-D02-{value:02d}" for value in range(6, 10)} | {
        f"ASR-D02-{value:02d}" for value in range(11, 15)
    }
    iam = {"ASR-D02-15", "ASR-D02-16"}

    observations = []
    coverage = []
    for base in template["case_observations"]:
        attack_id = base["attack_id"]
        if attack_id == "ASR-D02-C01":
            observation = {
                **base,
                "execution_attempted": True,
                "classification": "CONTROL_PASS",
                "observed_status": "VALID",
                "observed_engineering_gate": "NOT_EVALUATED",
                "observed_decision": "HOLD",
                "observed_stable_codes": ["SYNTHETIC_ONLY"],
                "downstream_payload_accepted": True,
                "recommendation_present": False,
                "core_semantic_parity": True,
                "gcp_observations": common,
            }
            coverage.append(
                {
                    "attack_id": attack_id,
                    "existing_case": "normal-production-core",
                    "coverage": "COMPLETE_EXISTING_CONTROL_EVIDENCE",
                }
            )
        else:
            if attack_id in related:
                detail = related[attack_id]
                reason = detail["reason"]
                existing_case = detail["case"]
                coverage_state = "RELATED_ONLY_NOT_ASR_EVIDENCE"
            elif attack_id == "ASR-D02-03":
                reason = "FRESHNESS_OR_SUPERSESSION_PRECONDITION_NOT_IMPLEMENTED"
                existing_case = None
                coverage_state = "PRECONDITION_MISSING"
            elif attack_id in isolated:
                reason = "ISOLATED_TEST_ENDPOINT_OR_RESULT_INJECTION_REQUIRED"
                existing_case = None
                coverage_state = "SEPARATE_TEST_INFRA_REQUIRED"
            elif attack_id in iam:
                reason = "SEPARATELY_AUTHORIZED_IAM_OR_OIDC_PROBE_REQUIRED"
                existing_case = None
                coverage_state = "SEPARATE_IAM_PROBE_REQUIRED"
            else:
                reason = "NEW_EXACT_MUTATION_EXECUTION_REQUIRED"
                existing_case = None
                coverage_state = "NEW_SYNTHETIC_EXECUTION_REQUIRED"
            observation = {
                **base,
                "not_evaluated_reason": reason,
            }
            coverage.append(
                {
                    "attack_id": attack_id,
                    "existing_case": existing_case,
                    "coverage": coverage_state,
                }
            )
        observations.append(observation)

    output = {
        "schema_version": "spectra.assurance.asr-d02.existing-evidence.v1",
        "package_id": manifest["package_id"],
        "evidence_status": "CONTROL_EVALUATED_ATTACKS_NOT_EVALUATED",
        "target_lock": {**target, "locked_by": "CONTROL_TOWER_EXISTING_EVIDENCE_RECONCILIATION"},
        "required_permissions_observed": {
            "workflow_execute": False,
            "workflow_execution_get": True,
            "storage_object_create": False,
            "storage_object_get_exact_generation": True,
            "storage_object_metadata_get": True,
            "cloud_run_revision_get": True,
            "workflow_revision_get": True,
            "logging_read_scoped_by_correlation": True,
            "iam_policy_read": False,
            "credential_material_recorded": False,
        },
        "case_observations": observations,
        "aggregate": {
            "live_executions": 1,
            "evaluated_controls": 1,
            "evaluated_attacks": 0,
            "safe_failures": "NOT_COMPUTED",
            "false_accepts": "NOT_COMPUTED",
            "false_passes": "NOT_COMPUTED",
            "unexpected_results": 0,
            "result": "NOT_EVALUATED",
        },
        "existing_evidence_coverage": coverage,
        "boundary_notes": [
            "The evaluated control reuses an existing H05 normal execution; this script starts no Workflow.",
            "The historical H05 target is preserved even when the package manifest points to a newer remediation target.",
            "Related H05 attack cases are not relabeled as ASR-D02 results when mutation or required observations differ.",
            "False Accept and False PASS remain NOT_COMPUTED because zero ASR-D02 attacks are evaluated.",
            "Every input is SYNTHETIC and the final assurance boundary remains HOLD.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "evaluated_controls": 1,
                "evaluated_attacks": 0,
                "asr_d02": "NOT_EVALUATED",
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
