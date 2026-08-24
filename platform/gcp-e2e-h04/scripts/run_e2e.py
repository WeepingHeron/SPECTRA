#!/usr/bin/env python3
"""Run the H05 synthetic control and fail-closed GCP attack cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared.integrity import canonical_json_bytes, canonical_sha256  # noqa: E402


CASE_NAMES = (
    "normal-production-core",
    "body-metadata-expected-forgery",
    "parts-evidence-hash-corruption",
    "malformed-agent-input",
    "endpoint-override",
    "production-test-control",
)


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def json_output(command: list[str]) -> dict[str, Any]:
    return json.loads(run([*command, "--format=json"]))


def execute_case(
    *, project: str, region: str, bucket: str, case_name: str,
    fixture: Path, metadata_sha256: str | None = None,
    expected_sha256: str | None = None, extra_args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    object_name = f"inputs/{timestamp}-{uuid.uuid4().hex[:8]}-{case_name}.json"
    fixture_value = json.loads(fixture.read_text(encoding="utf-8"))
    fixture_sha = canonical_sha256(fixture_value)
    declared_metadata_sha = metadata_sha256 or fixture_sha
    declared_expected_sha = expected_sha256 or fixture_sha
    with tempfile.TemporaryDirectory(prefix="spectra-h05-input-") as temp_dir:
        canonical_path = Path(temp_dir) / "input.json"
        canonical_path.write_bytes(canonical_json_bytes(fixture_value))
        run([
            "gcloud", "storage", "cp", str(canonical_path), f"gs://{bucket}/{object_name}",
            "--project", project, "--if-generation-match=0",
            f"--custom-metadata=sha256={declared_metadata_sha}",
        ])
    metadata = json_output([
        "gcloud", "storage", "objects", "describe", f"gs://{bucket}/{object_name}",
        "--project", project,
    ])
    arguments = {
        "bucket": bucket,
        "input_object": object_name,
        "input_generation": str(metadata["generation"]),
        "input_sha256": declared_expected_sha,
    }
    arguments.update(extra_args or {})
    execution = json_output([
        "gcloud", "workflows", "run", "spectra-h04-e2e",
        "--project", project, "--location", region,
        "--data", json.dumps(arguments, separators=(",", ":")),
    ])
    if execution.get("state") != "SUCCEEDED" or "result" not in execution:
        error = execution.get("error", {})
        context = error.get("context", "workflow did not return a result") if isinstance(error, dict) else "workflow did not return a result"
        raise RuntimeError(
            f"workflow execution {execution.get('name', 'unknown')} ended as "
            f"{execution.get('state', 'UNKNOWN')}: {context}"
        )
    workflow_result = json.loads(execution["result"])
    result_ref = workflow_result["result_storage"]
    with tempfile.TemporaryDirectory(prefix="spectra-h04-") as temp_dir:
        downloaded = Path(temp_dir) / "result.json"
        run([
            "gcloud", "storage", "cp",
            f"gs://{result_ref['bucket_id']}/{result_ref['object_name']}",
            str(downloaded), "--project", project,
        ])
        result_sha = sha256_file(downloaded)
        stored_result = json.loads(downloaded.read_text(encoding="utf-8"))
    return {
        "case": case_name,
        "workflow_execution": execution.get("name"),
        "workflow_state": execution.get("state"),
        "correlation_id": workflow_result["correlation_id"],
        "input_storage": {
            "bucket_id": bucket,
            "object_name": object_name,
            "generation": str(metadata["generation"]),
            "canonical_body_sha256": fixture_sha,
            "metadata_sha256": declared_metadata_sha,
            "expected_sha256": declared_expected_sha,
        },
        "result_storage": {**result_ref, "sha256": result_sha},
        "result_summary": {
            "processing_status": stored_result["processing_status"],
            "engineering_gate": stored_result["engineering_gate"],
            "assurance_decision": stored_result["assurance_decision"],
            "stable_codes": stored_result["stable_codes"],
            "agent_statuses": {
                role: value["processing_status"]
                for role, value in stored_result.get("agent_results", {}).items()
            },
            "agent_codes": {
                role: value["stable_codes"]
                for role, value in stored_result.get("agent_results", {}).items()
            },
            "mission_body_hash_verified": stored_result.get("agent_results", {}).get("mission", {}).get("body_hash_verified"),
            "production_core_run_id": stored_result.get("agent_results", {}).get("mission", {}).get("core_result", {}).get("run_id"),
            "production_core_output_hash": stored_result.get("agent_results", {}).get("mission", {}).get("core_result", {}).get("output_hash"),
            "production_core_result_sha256": stored_result.get("agent_results", {}).get("mission", {}).get("core_result_sha256"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="iceu-686")
    parser.add_argument("--region", default="asia-northeast3")
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=CASE_NAMES, action="append")
    args = parser.parse_args()
    bucket = args.bucket or f"spectra-h04-{args.project}"
    forged_sha = "sha256:" + ("0" * 64)
    case_specs = {
        "normal-production-core": {"fixture": ROOT / "fixtures/normal.json"},
        "body-metadata-expected-forgery": {
            "fixture": ROOT / "fixtures/normal.json",
            "metadata_sha256": forged_sha,
            "expected_sha256": forged_sha,
        },
        "parts-evidence-hash-corruption": {"fixture": ROOT / "fixtures/corrupted-evidence-hash.json"},
        "malformed-agent-input": {"fixture": ROOT / "fixtures/malformed-part.json"},
        "endpoint-override": {
            "fixture": ROOT / "fixtures/normal.json",
            "extra_args": {"mission_url": "https://example.invalid"},
        },
        "production-test-control": {
            "fixture": ROOT / "fixtures/normal.json",
            "extra_args": {"test_mode": "STRUCTURED_FAILURE", "failure_role": "parts"},
        },
    }
    selected = args.case or list(CASE_NAMES)
    cases = [
        execute_case(
            project=args.project, region=args.region, bucket=bucket,
            case_name=case_name, **case_specs[case_name],
        )
        for case_name in selected
    ]
    evidence = {
        "schema_version": "1.0.0",
        "project_id": args.project,
        "region": args.region,
        "data_class": "SYNTHETIC",
        "assurance_decision": "HOLD",
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
