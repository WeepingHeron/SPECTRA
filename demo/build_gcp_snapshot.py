#!/usr/bin/env python3
"""Build the deterministic read-only H05 GCP snapshot used by offline demos."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/workstreams/70-platform-gcp/evidence"
DEFAULT_JSON = ROOT / "demo/data/h05-gcp-snapshot.json"
DEFAULT_JS = ROOT / "demo/data/h05-gcp-snapshot.js"
JS_PREFIX = "globalThis.SPECTRA_GCP_H05_SNAPSHOT="


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def execution_id(case: dict) -> str:
    return case["workflow_execution"].rsplit("/", 1)[-1]


def build_snapshot() -> dict:
    runs = load("h05-e2e-runs.json")
    parity = load("h05-core-parity.json")
    inventory = load("h05-gcp-inventory-and-logs.json")
    cases = {item["case"]: item for item in runs["cases"]}
    normal = cases["normal-production-core"]
    forged = cases["body-metadata-expected-forgery"]
    endpoint = cases["endpoint-override"]
    services = {item["role"]: item for item in inventory["services"]}
    observed_at = max(item["timestamp"] for item in inventory["cloud_run_structured_logs"])

    body = {
        "schema_version": "1.0.0",
        "generated_at": observed_at,
        "source": {
            "paths": [
                "docs/workstreams/70-platform-gcp/evidence/h05-e2e-runs.json",
                "docs/workstreams/70-platform-gcp/evidence/h05-core-parity.json",
                "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json",
            ],
            "schema_versions": {
                "e2e_runs": runs["schema_version"],
                "core_parity": parity["schema_version"],
                "inventory_logs": inventory["schema_version"],
            },
            "classification": "CONTROL_TOWER_VERIFIED_H05_SNAPSHOT",
        },
        "data_class": runs["data_class"],
        "project_id": inventory["project_id"],
        "region": inventory["region"],
        "workflow": {
            "name": inventory["workflow"]["name"].rsplit("/", 1)[-1],
            "revision": inventory["workflow"]["revision_id"],
            "state": inventory["workflow"]["state"],
            "console_url": (
                "https://console.cloud.google.com/workflows/workflow/"
                f"{inventory['region']}/{inventory['workflow']['name'].rsplit('/', 1)[-1]}"
                f"?project={inventory['project_id']}"
            ),
        },
        "agents": [
            {
                "role": role,
                "service": services[role]["name"],
                "revision": services[role]["latest_ready_revision"],
                "public_iam_members": services[role]["public_iam_members"],
            }
            for role in ("mission", "parts", "assurance")
        ],
        "storage": {
            "bucket": inventory["bucket"]["name"],
            "public_access_prevention": inventory["bucket"]["public_access_prevention"],
            "uniform_bucket_level_access": inventory["bucket"]["uniform_bucket_level_access"],
            "normal_input_object": normal["input_storage"]["object_name"],
            "normal_input_generation": normal["input_storage"]["generation"],
            "normal_result_object": normal["result_storage"]["object_name"],
            "normal_result_generation": normal["result_storage"]["generation"],
        },
        "logging": {
            "structured_log_count": len(inventory["cloud_run_structured_logs"]),
            "normal_correlation_id": normal["correlation_id"],
            "observed_at": observed_at,
        },
        "iam": {
            "workflow_service_account": inventory["workflow"]["service_account"].rsplit("/", 1)[-1],
            "cloud_run_invoker_bindings": len(inventory["iam"]["cloud_run"]),
            "bucket_roles": [item["role"] for item in inventory["iam"]["bucket"]],
            "project_roles": [item["role"] for item in inventory["iam"]["project"]],
            "public_agent_members": sum(len(item["public_iam_members"]) for item in inventory["services"]),
        },
        "executions": {
            "normal": {
                "id": execution_id(normal),
                "workflow_state": normal["workflow_state"],
                "processing_status": normal["result_summary"]["processing_status"],
                "engineering_gate": normal["result_summary"]["engineering_gate"],
                "assurance_decision": normal["result_summary"]["assurance_decision"],
                "agent_statuses": normal["result_summary"]["agent_statuses"],
            },
            "body_hash_forgery": {
                "id": execution_id(forged),
                "workflow_state": forged["workflow_state"],
                "processing_status": forged["result_summary"]["processing_status"],
                "stable_code": forged["result_summary"]["stable_codes"][0],
                "assurance_decision": forged["result_summary"]["assurance_decision"],
            },
            "endpoint_override": {
                "id": execution_id(endpoint),
                "workflow_state": endpoint["workflow_state"],
                "processing_status": endpoint["result_summary"]["processing_status"],
                "stable_code": endpoint["result_summary"]["stable_codes"][0],
                "agent_call_count": len(endpoint["result_summary"]["agent_statuses"]),
                "assurance_decision": endpoint["result_summary"]["assurance_decision"],
            },
        },
        "core_parity": {
            "canonical_hash_equal": parity["canonical_hash_equal"],
            "semantic_payload_equal": parity["semantic_payload_equal"],
        },
        "real_evidence": {
            "environment_runs": 0,
            "approved_bom_and_test_sources": 0,
            "derivation_codes": [
                "REAL_ENVIRONMENT_EVIDENCE_MISSING",
                "REAL_PART_TEST_EVIDENCE_MISSING",
            ],
        },
        "cost_status": "NOT_QUERIED",
        "final_assurance": "HOLD",
    }
    preimage = canonical_bytes(body).decode().rstrip("\n")
    return {**body, "snapshot_hash_preimage": preimage, "snapshot_sha256": "sha256:" + hashlib.sha256(preimage.encode()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--javascript", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    payload = build_snapshot()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_bytes(canonical_bytes(payload))
    args.javascript.write_text(JS_PREFIX + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
