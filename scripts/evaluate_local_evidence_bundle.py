#!/usr/bin/env python3
"""Evaluate a caller-owned local evidence bundle without copying raw files.

The command reads only artifact paths declared by the supplied manifest and
passes their bytes to the existing fail-closed local bundle gate.  The output
receipt contains no raw bytes, local paths, artifact identifiers, or hashes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_source_adapter import evaluate_local_bundle  # noqa: E402


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def _safe_artifacts(manifest: Any, artifact_root: Path) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("artifacts"), list):
        return []
    try:
        resolved_root = artifact_root.resolve(strict=True)
    except OSError:
        return []
    if not resolved_root.is_dir():
        return []

    raw_artifacts: list[dict[str, Any]] = []
    for entry in manifest["artifacts"]:
        if not isinstance(entry, dict):
            continue
        artifact_id = entry.get("artifact_id")
        relative_path = entry.get("relative_path")
        if not isinstance(artifact_id, str) or not isinstance(relative_path, str):
            continue
        if not relative_path or "\x00" in relative_path or "\\" in relative_path:
            continue
        parts = relative_path.split("/")
        if relative_path.startswith("/") or any(part in {"", ".", ".."} for part in parts):
            continue
        try:
            candidate = (resolved_root / relative_path).resolve(strict=True)
            if not candidate.is_relative_to(resolved_root) or not candidate.is_file():
                continue
            content = candidate.read_bytes()
        except OSError:
            continue
        raw_artifacts.append(
            {
                "artifact_id": artifact_id,
                "relative_path": relative_path,
                "content_bytes": content,
            }
        )
    return raw_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--approval-anchor", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    anchor = _load_json(args.approval_anchor) if args.approval_anchor else None
    receipt = evaluate_local_bundle(
        manifest,
        _safe_artifacts(manifest, args.artifact_root),
        external_approval_anchor=anchor,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "processing_status": receipt["processing_status"],
                "binding_status": receipt["binding_status"],
                "blocker_count": len(receipt["blocker_codes"]),
                "assurance_decision": receipt["assurance_decision"],
                "output": str(args.output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
