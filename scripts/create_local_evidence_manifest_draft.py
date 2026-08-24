#!/usr/bin/env python3
"""Create a non-approved ACTUAL_CANDIDATE manifest draft for local files.

The draft records hashes and explicit unresolved action rights.  It is not an
approval manifest and is expected to produce HOLD_NOT_ISSUED until an evidence
owner supplies valid rights and an external approval anchor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RIGHTS_ACTIONS = (
    "LOCATOR",
    "FETCH",
    "PRIVATE_STORE",
    "PROCESS_LOCAL_AI",
    "DISPLAY_INTERNAL",
    "DISPLAY_EXTERNAL",
    "REDISTRIBUTE",
    "COMMERCIAL_USE",
)


def _safe_file(root: Path, relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path or "\\" in relative_path:
        raise ValueError(f"unsafe relative path: {relative_path!r}")
    parts = relative_path.split("/")
    if relative_path.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe relative path: {relative_path!r}")
    candidate = (root / relative_path).resolve(strict=True)
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ValueError(f"file is outside artifact root: {relative_path!r}")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--file", action="append", required=True, dest="files")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--manifest-revision", required=True)
    parser.add_argument(
        "--source-class",
        choices=(
            "PROVIDER_ORIGINAL",
            "MANUFACTURER_ORIGINAL",
            "PUBLIC_AGENCY_RECORD",
            "DERIVED_ARTIFACT",
        ),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.artifact_root.resolve(strict=True)
    if not root.is_dir():
        parser.error("--artifact-root must be a directory")

    artifacts = []
    for index, relative_path in enumerate(args.files, start=1):
        try:
            candidate = _safe_file(root, relative_path)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        artifact_id = f"candidate-artifact-{index:02d}"
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "relative_path": relative_path,
                "declared_sha256": "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest(),
                "source_class": args.source_class,
                "rights": [
                    {
                        "action": action,
                        "status": "UNRESOLVED",
                        "scope_artifact_id": artifact_id,
                    }
                    for action in RIGHTS_ACTIONS
                ],
            }
        )

    manifest = {
        "bundle_class": "ACTUAL_CANDIDATE",
        "bundle_id": args.bundle_id,
        "manifest_revision": args.manifest_revision,
        "artifacts": artifacts,
        "claimed_use_status": "NOT_FOR_DECISION",
        "claimed_assurance_decision": "HOLD",
        "claimed_suitability": "NOT_EVALUATED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "artifact_count": len(artifacts),
                "rights_status": "UNRESOLVED",
                "decision_use": False,
                "output": str(args.output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
