#!/usr/bin/env python3
"""Compare the stored deployed Mission Core result with a local production Core run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUNDLE_ROOT = SCRIPT.parents[1]
REPO_ROOT = SCRIPT.parents[3]
sys.path.insert(0, str(BUNDLE_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from shared.integrity import canonical_sha256  # noqa: E402
from spectra_sim.mvp_engine import run_mvp_decision  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="iceu-686")
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runs = load(args.runs)
    control_case = next(case for case in runs["cases"] if case["case"] == "normal-production-core")
    result_ref = control_case["result_storage"]
    with tempfile.TemporaryDirectory(prefix="spectra-h05-parity-") as temp_dir:
        stored_path = Path(temp_dir) / "result.json"
        subprocess.run(
            [
                "gcloud", "storage", "cp",
                f"gs://{result_ref['bucket_id']}/{result_ref['object_name']}",
                str(stored_path), "--project", args.project,
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        deployed = load(stored_path)["agent_results"]["mission"]["core_result"]

    local = run_mvp_decision(
        load(REPO_ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json"),
        load(REPO_ROOT / "simulation/config/synthetic-model.json"),
    )
    local_hash = canonical_sha256(local)
    deployed_hash = canonical_sha256(deployed)
    semantic_fields = (
        "run_id", "case_id", "data_class", "input_hash", "output_hash",
        "processing_status", "engineering_gate", "assurance_decision",
    )
    evidence = {
        "schema_version": "1.0.0",
        "data_class": "SYNTHETIC",
        "workflow_execution": control_case["workflow_execution"],
        "result_object": result_ref["object_name"],
        "result_generation": result_ref["generation"],
        "local_core_sha256": local_hash,
        "deployed_core_sha256": deployed_hash,
        "full_semantic_object_equal": local == deployed,
        "canonical_hash_equal": local_hash == deployed_hash,
        "semantic_payload_equal": all(local[field] == deployed[field] for field in semantic_fields),
        "semantic_payload": {field: local[field] for field in semantic_fields},
        "assurance_decision": "HOLD",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if all((evidence["full_semantic_object_equal"], evidence["canonical_hash_equal"], evidence["semantic_payload_equal"])) else 1


if __name__ == "__main__":
    raise SystemExit(main())
