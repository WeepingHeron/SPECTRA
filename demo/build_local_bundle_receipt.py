#!/usr/bin/env python3
"""Export a deterministic local bundle-binding receipt for the Product demo."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_source_adapter import evaluate_local_bundle  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/local-bundle-binding-receipt.json"


def _rights(artifact_id: str) -> list[dict]:
    actions = (
        "LOCATOR",
        "FETCH",
        "PRIVATE_STORE",
        "PROCESS_LOCAL_AI",
        "DISPLAY_INTERNAL",
        "DISPLAY_EXTERNAL",
        "REDISTRIBUTE",
        "COMMERCIAL_USE",
    )
    return [
        {
            "action": action,
            "status": "SYNTHETIC_ONLY",
            "scope_artifact_id": artifact_id,
        }
        for action in actions
    ]


def build_receipt() -> dict:
    artifacts = [
        ("synthetic-job-output", "outputs/job-summary.txt", b"synthetic dose output\n"),
        ("synthetic-job-config", "inputs/job-config.json", b'{"mission":"DEMO_ONLY"}\n'),
    ]
    manifest = {
        "bundle_class": "SYNTHETIC_CONTROL",
        "bundle_id": "spenvis-demo-bundle-001",
        "manifest_revision": "rev-001",
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "relative_path": relative_path,
                "declared_sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
                "source_class": "SYNTHETIC_CONTROL",
                "rights": _rights(artifact_id),
            }
            for artifact_id, relative_path, content in artifacts
        ],
        "claimed_use_status": "NOT_FOR_DECISION",
        "claimed_assurance_decision": "HOLD",
        "claimed_suitability": "NOT_EVALUATED",
    }
    raw_artifacts = [
        {
            "artifact_id": artifact_id,
            "relative_path": relative_path,
            "content_bytes": content,
        }
        for artifact_id, relative_path, content in artifacts
    ]
    return evaluate_local_bundle(manifest, raw_artifacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_receipt(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
