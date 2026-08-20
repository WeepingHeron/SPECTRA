"""Validate an external SPENVIS bundle before contract normalization."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .spenvis_shieldose2 import DoseParseError, normalize_tid_candidates, parse_shieldose2_file


REQUIRED_ACTIONS = {"FETCH", "PRIVATE_STORE"}
REQUIRED_ROLES = {
    "ORBIT_INPUT_REPORT",
    "TRAPPED_INPUT_REPORT",
    "TRAPPED_SPECTRUM",
    "SOLAR_INPUT_REPORT",
    "SOLAR_SPECTRUM",
    "DOSE_INPUT_REPORT",
    "DOSE_OUTPUT",
}
REFERENCE_MISSION = {
    "mission_id": "spectra-mvp-leo-001",
    "body": "EARTH",
    "orbit_class": "CIRCULAR_LEO",
    "segment_count": 1,
    "altitude": {"value": 550, "unit": "km"},
    "inclination": {"value": 97.6, "unit": "deg"},
    "start_at": "2027-01-01T00:00:00Z",
    "end_at": "2028-01-01T00:00:00Z",
    "duration": {"value": 365, "unit": "day"},
}


def _result(processing_status: str, *codes: str) -> dict[str, Any]:
    return {
        "gate_status": "HOLD",
        "processing_status": processing_status,
        "assurance_decision": "HOLD",
        "error_codes": sorted(set(codes)),
        "normalized_environment": None,
    }


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return f"sha256:{digest.hexdigest()}"


def _schema_errors(manifest: dict[str, Any], schema_root: Path) -> list[str]:
    documents = [_load(path) for path in sorted(schema_root.glob("*.schema.json"))]
    registry = Registry()
    for document in documents:
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
    schema = _load(schema_root / "raw-artifact-manifest-v2.schema.json")
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(manifest)]


def _rights_codes(rights: dict[str, Any], now: datetime) -> set[str]:
    codes: set[str] = set()
    if rights.get("status") in {"RIGHTS_UNCONFIRMED", "FORBIDDEN", "SYNTHETIC_TEST_ONLY"}:
        codes.add("RIGHTS_GATE_HOLD")
    if rights.get("revoked_at"):
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")
    valid_from = rights.get("valid_from")
    valid_until = rights.get("valid_until")
    if not valid_from or _parse_time(valid_from) > now:
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")
    if valid_until and _parse_time(valid_until) < now:
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")
    grants = {
        item.get("action"): item.get("grant_status")
        for item in rights.get("action_grants", [])
        if isinstance(item, dict)
    }
    for action in REQUIRED_ACTIONS:
        if grants.get(action) != "ALLOWED":
            codes.add("RIGHTS_ACTION_GRANT_MISSING")
    return codes


def _duplicate_manifest_artifact_ids(manifest: dict[str, Any]) -> set[str]:
    """Return duplicate IDs without first collapsing the artifact array."""

    artifact_ids = [item.get("artifact_id") for item in manifest.get("artifacts", [])]
    return {
        artifact_id
        for artifact_id, count in Counter(artifact_ids).items()
        if isinstance(artifact_id, str) and count > 1
    }


def _validate_artifact_index(
    role_entries: Any,
    *,
    raw_root: Path,
    by_artifact: dict[str, dict[str, Any]],
) -> tuple[set[str], list[tuple[str, dict[str, Any], Path]]]:
    """Validate source-role cardinality and identity before reading artifacts."""

    if not isinstance(role_entries, list):
        return {"ARTIFACT_INDEX_MISSING"}, []

    codes: set[str] = set()
    valid_entries: list[tuple[str, dict[str, Any], Path]] = []
    role_counts: Counter[str] = Counter()
    artifact_roles: dict[str, set[str]] = {}
    resolved_path_roles: dict[Path, set[str]] = {}

    for entry in role_entries:
        if not isinstance(entry, dict):
            codes.add("ARTIFACT_INDEX_INVALID")
            continue

        role = entry.get("role")
        artifact_id = entry.get("artifact_id")
        relative_path = entry.get("path")
        if not isinstance(role, str) or not isinstance(artifact_id, str) or not isinstance(relative_path, str):
            codes.add("ARTIFACT_INDEX_INVALID")
            continue
        if role not in REQUIRED_ROLES:
            codes.add("SOURCE_ROLE_UNEXPECTED")
            continue

        role_counts[role] += 1
        artifact = by_artifact.get(artifact_id)
        if artifact is None:
            codes.add("RAW_MANIFEST_REFERENCE_MISSING")
            continue

        if "\0" in relative_path:
            codes.add("ARTIFACT_PATH_INVALID")
            continue

        try:
            path = (raw_root / relative_path).resolve()
        except (OSError, RuntimeError, ValueError):
            codes.add("ARTIFACT_PATH_INVALID")
            continue

        artifact_roles.setdefault(artifact_id, set()).add(role)
        resolved_path_roles.setdefault(path, set()).add(role)
        valid_entries.append((role, artifact, path))

    if REQUIRED_ROLES - role_counts.keys():
        codes.add("SOURCE_ROLE_MISSING")
    if any(count > 1 for count in role_counts.values()):
        codes.add("SOURCE_ROLE_DUPLICATED")
    if any(len(roles) > 1 for roles in artifact_roles.values()):
        codes.add("ARTIFACT_ID_REUSED_ACROSS_ROLES")
    if any(len(roles) > 1 for roles in resolved_path_roles.values()):
        codes.add("RESOLVED_PATH_REUSED_ACROSS_ROLES")

    return codes, valid_entries


def assess_import(
    request_path: Path,
    *,
    schema_root: Path,
    repository_root: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Assess a user-supplied import request without writing files."""

    now = now or datetime.now(timezone.utc)
    if not request_path.is_file():
        return _result("PROVENANCE_FAILURE", "IMPORT_REQUEST_MISSING")

    try:
        request = _load(request_path)
    except (OSError, json.JSONDecodeError):
        return _result("INVALID_INPUT", "IMPORT_REQUEST_INVALID")

    if not isinstance(request, dict):
        return _result("INVALID_INPUT", "IMPORT_REQUEST_INVALID")
    if request.get("mission") != REFERENCE_MISSION:
        return _result("OUT_OF_MODEL_SCOPE", "REFERENCE_MISSION_MISMATCH")

    raw_root_value = request.get("raw_root")
    manifest_value = request.get("manifest_path")
    if not isinstance(raw_root_value, str) or not isinstance(manifest_value, str):
        return _result("PROVENANCE_FAILURE", "RAW_BUNDLE_LOCATION_MISSING")

    if "\0" in raw_root_value or "\0" in manifest_value:
        return _result("PROVENANCE_FAILURE", "RAW_BUNDLE_LOCATION_INVALID")
    try:
        raw_root = Path(raw_root_value).expanduser().resolve()
        manifest_path = (raw_root / manifest_value).resolve()
    except (OSError, RuntimeError, ValueError):
        return _result("PROVENANCE_FAILURE", "RAW_BUNDLE_LOCATION_INVALID")
    if _inside(repository_root, raw_root):
        return _result("PROVENANCE_FAILURE", "RAW_BUNDLE_INSIDE_GIT_WORKTREE")
    if not _inside(raw_root, manifest_path) or not manifest_path.is_file():
        return _result("PROVENANCE_FAILURE", "RAW_MANIFEST_MISSING")

    try:
        manifest = _load(manifest_path)
    except (OSError, json.JSONDecodeError):
        return _result("INVALID_INPUT", "RAW_MANIFEST_INVALID")

    errors = _schema_errors(manifest, schema_root)
    if errors:
        return _result("PROVENANCE_FAILURE", "RAW_MANIFEST_SCHEMA_INVALID") | {
            "schema_errors": errors
        }

    if _duplicate_manifest_artifact_ids(manifest):
        return _result("PROVENANCE_FAILURE", "DUPLICATE_ARTIFACT_ID_IN_MANIFEST")

    # Build the lookup only after duplicate IDs have been rejected.
    by_artifact = {item["artifact_id"]: item for item in manifest["artifacts"]}
    index_codes, validated_entries = _validate_artifact_index(
        request.get("artifact_files"), raw_root=raw_root, by_artifact=by_artifact
    )
    if index_codes:
        return _result("PROVENANCE_FAILURE", *index_codes)

    rights_codes = _rights_codes(manifest["rights_snapshot"], now)
    if rights_codes:
        status = "STALE_EVIDENCE" if "RIGHTS_SNAPSHOT_NOT_ACTIVE" in rights_codes else "PROVENANCE_FAILURE"
        return _result(status, *rights_codes)

    codes: set[str] = set()
    dose_output_path: Path | None = None
    for role, artifact, path in validated_entries:
        if not _inside(raw_root, path) or not path.is_file():
            codes.add("RAW_ARTIFACT_MISSING")
            continue
        try:
            byte_size = path.stat().st_size
            artifact_hash = _sha256(path)
        except (OSError, RuntimeError, ValueError):
            codes.add("RAW_ARTIFACT_UNREADABLE")
            continue
        if role == "DOSE_OUTPUT":
            dose_output_path = path
        if byte_size != artifact["integrity"]["byte_size"]:
            codes.add("RAW_ARTIFACT_SIZE_MISMATCH")
        if artifact_hash != artifact["integrity"]["sha256"]:
            codes.add("RAW_ARTIFACT_HASH_MISMATCH")

    if codes:
        return _result("PROVENANCE_FAILURE", *codes)

    if manifest["provider"]["platform_name"] != "SPENVIS" or manifest["provider"]["platform_version"] != "4.6.14.3582":
        return _result("STALE_EVIDENCE", "PROVIDER_VERSION_NOT_APPROVED")

    if dose_output_path is None:
        return _result("PROVENANCE_FAILURE", "DOSE_OUTPUT_MISSING")
    try:
        candidates = normalize_tid_candidates(parse_shieldose2_file(dose_output_path))
    except (OSError, UnicodeError, DoseParseError) as exc:
        code = exc.code if isinstance(exc, DoseParseError) else "DOSE_OUTPUT_UNREADABLE"
        return _result("MODEL_FAILURE", code)

    # Parsing is calibrated, but common-contract emission needs separate review.
    # Numeric candidates are intentionally not returned through this fail-closed gate.
    return _result("MODEL_FAILURE", "CONTRACT_EMISSION_NOT_APPROVED") | {
        "parsed_candidate_count": len(candidates)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--schema-root", type=Path, default=Path("schemas"))
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = assess_import(
        args.request,
        schema_root=args.schema_root.resolve(),
        repository_root=args.repository_root.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 2 if result["gate_status"] == "HOLD" else 0


if __name__ == "__main__":
    raise SystemExit(main())
