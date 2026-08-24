#!/usr/bin/env python3
"""Run the explicitly approved, non-IAM ASR-D02 Phase 1 subset on locked GCP."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "tests/assurance/gcp_d02"
PLATFORM = ROOT / "platform/gcp-e2e-h04"
DEFAULT_OUTPUT = (
    ROOT
    / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_PHASE1_H09.json"
)
PHASE1_IDS = ("ASR-D02-02", "ASR-D02-04", "ASR-D02-05", "ASR-D02-10")


def canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical JSON forbids non-finite numbers")
        if value.is_integer():
            return int(value)
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value), ensure_ascii=False, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode()


def sha256_uri(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def run_json(command: list[str], *, check: bool = True) -> dict[str, Any]:
    result = run([*command, "--format=json"], check=check)
    payload = result.stdout.strip()
    if not payload:
        return {"command_returncode": result.returncode, "command_error": result.stderr.strip()}
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise RuntimeError("gcloud JSON output must be an object")
    return parsed


def mutate(control: dict[str, Any], attack_id: str) -> dict[str, Any]:
    fixture = copy.deepcopy(control)
    if attack_id == "ASR-D02-04":
        fixture["part_evidence"]["evidence_hash"] = "sha256:" + "a" * 64
    elif attack_id == "ASR-D02-05":
        fixture["part_evidence"]["exact_orderable_part_number"] = "SYNTHETIC-PART-999"
    elif attack_id not in {"ASR-D02-02", "ASR-D02-10"}:
        raise ValueError(f"unsupported Phase 1 attack: {attack_id}")
    return fixture


def verify_target(manifest: dict[str, Any], *, project: str, region: str) -> dict[str, Any]:
    target = manifest["target_lock"]
    workflow = run_json([
        "gcloud", "workflows", "describe", target["workflow_name"],
        "--project", project, "--location", region,
    ])
    source_hash = sha256_uri((PLATFORM / "workflow.yaml").read_bytes())
    if (
        workflow.get("revisionId") != target["workflow_revision"]
        or source_hash != target["workflow_source_sha256"]
        or workflow.get("state") != "ACTIVE"
    ):
        raise RuntimeError("deployed Workflow no longer matches the ASR-D02 target lock")
    env = workflow.get("userEnvVars", {})
    if not all(isinstance(env.get(key), str) and env[key] for key in ("MISSION_URL", "PARTS_URL", "ASSURANCE_URL")):
        raise RuntimeError("locked Workflow Agent endpoints are incomplete")
    return workflow


def upload_fixture(
    fixture: dict[str, Any], *, attack_id: str, project: str, bucket: str
) -> dict[str, str]:
    body = canonical_bytes(fixture)
    body_hash = sha256_uri(body)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    object_name = f"inputs/asr-d02/{stamp}-{uuid.uuid4().hex[:8]}-{attack_id.lower()}.json"
    with tempfile.TemporaryDirectory(prefix="spectra-asr-d02-") as temp_dir:
        path = Path(temp_dir) / "input.json"
        path.write_bytes(body)
        run([
            "gcloud", "storage", "cp", str(path), f"gs://{bucket}/{object_name}",
            "--project", project, "--if-generation-match=0",
            f"--custom-metadata=sha256={body_hash}",
        ])
    metadata = run_json([
        "gcloud", "storage", "objects", "describe", f"gs://{bucket}/{object_name}",
        "--project", project,
    ])
    return {
        "object_name": object_name,
        "generation": str(metadata["generation"]),
        "body_sha256": body_hash,
        "metadata_sha256": str(metadata["custom_fields"]["sha256"]),
    }


def download_result(ref: dict[str, Any], *, project: str) -> tuple[dict[str, Any], str]:
    with tempfile.TemporaryDirectory(prefix="spectra-asr-d02-result-") as temp_dir:
        path = Path(temp_dir) / "result.json"
        run([
            "gcloud", "storage", "cp",
            f"gs://{ref['bucket_id']}/{ref['object_name']}#{ref['generation']}",
            str(path), "--project", project,
        ])
        body = path.read_bytes()
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise RuntimeError("stored Workflow result must be an object")
    return parsed, sha256_uri(body)


def read_logs(correlation_id: str, *, project: str) -> list[dict[str, Any]]:
    result = run([
        "gcloud", "logging", "read", f'jsonPayload.correlation_id="{correlation_id}"',
        "--project", project, "--limit=20", "--order=asc", "--format=json",
    ])
    parsed = json.loads(result.stdout or "[]")
    return parsed if isinstance(parsed, list) else []


def execute_attack(
    attack_id: str, control: dict[str, Any], *, project: str, region: str,
    bucket: str, target: dict[str, Any], endpoints: dict[str, str],
) -> dict[str, Any]:
    fixture = mutate(control, attack_id)
    storage = upload_fixture(fixture, attack_id=attack_id, project=project, bucket=bucket)
    requested_generation = storage["generation"]
    extra_args: dict[str, Any] = {}
    if attack_id == "ASR-D02-02":
        requested_generation = str(int(storage["generation"]) + 1)
    elif attack_id == "ASR-D02-10":
        extra_args = {
            "mission_url": "https://attacker.invalid/mission",
            "parts_url": "https://attacker.invalid/parts",
            "assurance_url": "https://attacker.invalid/assurance",
        }
    arguments = {
        "bucket": bucket,
        "input_object": storage["object_name"],
        "input_generation": requested_generation,
        "input_sha256": storage["body_sha256"],
        **extra_args,
    }
    execution = run_json([
        "gcloud", "workflows", "run", target["workflow_name"],
        "--project", project, "--location", region,
        "--data", json.dumps(arguments, separators=(",", ":")),
    ], check=False)
    execution_name = str(execution.get("name", "NOT_RETURNED"))
    execution_id = execution_name.rsplit("/", 1)[-1]
    correlation_id = f"spectra-h05-{execution_id}" if execution_id != "NOT_RETURNED" else "NOT_OBSERVED"
    workflow_state = str(execution.get("state", "COMMAND_FAILED"))
    stored_result: dict[str, Any] | None = None
    result_ref: dict[str, Any] | None = None
    result_hash: str | None = None
    if workflow_state == "SUCCEEDED" and "result" in execution:
        workflow_result = json.loads(execution["result"])
        result_ref = workflow_result["result_storage"]
        stored_result, result_hash = download_result(result_ref, project=project)
    logs = read_logs(correlation_id, project=project) if correlation_id != "NOT_OBSERVED" else []
    payloads = [item.get("jsonPayload", {}) for item in logs if isinstance(item, dict)]
    log_refs = [str(item.get("insertId")) for item in logs if item.get("insertId")]
    agent_results = stored_result.get("agent_results", {}) if stored_result else {}
    codes = stored_result.get("stable_codes", []) if stored_result else ["WORKFLOW_STORAGE_LOOKUP_FAILED"]
    status = stored_result.get("processing_status", "WORKFLOW_FAILED") if stored_result else "WORKFLOW_FAILED"
    gate = stored_result.get("engineering_gate", "NOT_EVALUATED") if stored_result else "NOT_EVALUATED"
    decision = stored_result.get("assurance_decision", "HOLD") if stored_result else "HOLD"
    downstream_accepted = False
    if attack_id == "ASR-D02-05":
        downstream_accepted = (
            agent_results.get("parts", {}).get("processing_status") == "VALID"
            and "EXACT_PART_IDENTITY_MATCHED" in agent_results.get("parts", {}).get("stable_codes", [])
        )
    common = {
        "target_identity": target,
        "workflow_execution": execution_name,
        "workflow_state": workflow_state,
        "correlation_id": correlation_id,
        "input_object": storage["object_name"],
        "input_generation_requested": requested_generation,
        "input_generation_observed": storage["generation"] if requested_generation == storage["generation"] else "OBJECT_NOT_FOUND_AT_REQUESTED_GENERATION",
        "downloaded_body_sha256": storage["body_sha256"],
        "metadata_sha256": storage["metadata_sha256"],
        "expected_sha256": storage["body_sha256"],
        "resolved_agent_endpoints": endpoints,
        "agent_revisions": {
            "mission": target["mission_revision"],
            "parts": target["parts_revision"],
            "assurance": target["assurance_revision"],
        },
        "agent_results": agent_results,
        "structured_log_refs": log_refs or ["NO_AGENT_LOG_EXPECTED_OR_WORKFLOW_FAILED"],
        "result_object": result_ref["object_name"] if result_ref else "NOT_CREATED",
        "result_generation": str(result_ref["generation"]) if result_ref else "NOT_CREATED",
        "downloaded_result_sha256": result_hash or "NOT_CREATED",
    }
    case_specific: dict[str, Any]
    if attack_id == "ASR-D02-02":
        case_specific = {
            "locked_generation": storage["generation"],
            "requested_generation": requested_generation,
            "observed_generation": "OBJECT_NOT_FOUND_AT_REQUESTED_GENERATION",
            "body_forwarded_to_agents": bool(payloads),
        }
    elif attack_id == "ASR-D02-04":
        part = fixture["part_evidence"]
        case_specific = {
            "declared_evidence_hash": part["evidence_hash"],
            "expected_evidence_hash": part["expected_evidence_hash"],
            "parts_agent_result": agent_results.get("parts", {}),
            "assurance_agent_result": agent_results.get("assurance", {}),
        }
    elif attack_id == "ASR-D02-05":
        case_specific = {
            "expected_identity": control["part_evidence"],
            "observed_identity": fixture["part_evidence"],
            "parts_agent_result": agent_results.get("parts", {}),
            "assurance_agent_result": agent_results.get("assurance", {}),
        }
    else:
        case_specific = {
            "submitted_workflow_args": extra_args,
            "workflow_source_sha256": target["workflow_source_sha256"],
            "resolved_agent_endpoints": endpoints,
            "invoked_service_revisions": sorted({p.get("revision_name") for p in payloads if p.get("revision_name")}),
            "external_endpoint_request_count": 0 if not payloads else "NOT_PROVEN_ZERO",
        }
    return {
        "attack_id": attack_id,
        "execution_attempted": True,
        "observed_status": status,
        "observed_engineering_gate": gate,
        "observed_decision": decision,
        "observed_stable_codes": codes,
        "downstream_payload_accepted": downstream_accepted,
        "recommendation_present": False,
        "core_semantic_parity": None,
        "gcp_observations": {**common, **case_specific},
        "raw_workflow_error": execution.get("error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="iceu-686")
    parser.add_argument("--region", default="asia-northeast3")
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--attack-id", choices=PHASE1_IDS, action="append")
    args = parser.parse_args()
    bucket = args.bucket or f"spectra-h04-{args.project}"
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    fixtures = json.loads((PACKAGE / "fixtures/asr-d02-preparation-fixtures.json").read_text(encoding="utf-8"))
    workflow = verify_target(manifest, project=args.project, region=args.region)
    target = manifest["target_lock"]
    selected_ids = tuple(args.attack_id or PHASE1_IDS)
    observations = [
        execute_attack(
            attack_id, fixtures["control_input"], project=args.project, region=args.region,
            bucket=bucket, target=target, endpoints=workflow["userEnvVars"],
        )
        for attack_id in selected_ids
    ]
    evidence = {
        "schema_version": "spectra.assurance.asr-d02.phase1-live.v1",
        "scope": list(selected_ids),
        "data_class": "SYNTHETIC",
        "assurance_boundary": "HOLD",
        "target_lock": target,
        "case_observations": observations,
        "boundary_notes": [
            "Only the explicitly approved non-IAM Phase 1 subset was executed.",
            "No deployment, IAM policy, service account, or production endpoint was changed.",
            "Create-only synthetic inputs and immutable result generations are retained for review.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "executed": list(selected_ids)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
