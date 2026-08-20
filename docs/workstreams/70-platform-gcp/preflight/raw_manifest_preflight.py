#!/usr/bin/env python3
"""Fail-closed preflight for issuing a SPECTRA Raw Artifact Manifest v2.

The command is read-only: it validates a candidate manifest and synthetic object
creation receipts, then returns the candidate only when every issuance gate
passes. It never creates GCP resources, objects, or manifest files.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


BASE_REQUIRED_ACTIONS = {"FETCH", "PRIVATE_STORE"}
ISSUABLE_RIGHTS_STATUSES = {
    "PRIVATE_COPY_ALLOWED",
    "PROCESSING_ALLOWED",
    "DISPLAY_ALLOWED",
    "REDISTRIBUTION_ALLOWED",
    "CUSTOMER_RESTRICTED",
}
PLACEHOLDER_REFERENCES = {
    "", "UNKNOWN", "UNCONFIRMED", "N/A", "NA", "NONE", "MISSING",
    "LOCAL_ONLY", "TBD", "TODO", "PLACEHOLDER",
}
DECLARED_GAP_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _schema_errors(manifest: dict[str, Any], schema_root: Path) -> list[str]:
    registry = Registry()
    for path in sorted(schema_root.glob("*.schema.json")):
        document = _load(path)
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
    schema = _load(schema_root / "raw-artifact-manifest-v2.schema.json")
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    return sorted(
        f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in validator.iter_errors(manifest)
    )


def _request_errors(request: dict[str, Any]) -> list[str]:
    schema = _load(Path(__file__).resolve().with_name("preflight-request.schema.json"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(
        f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in validator.iter_errors(request)
    )


def _is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return True
    normalized = value.strip().upper()
    return normalized in PLACEHOLDER_REFERENCES or "PLACEHOLDER" in normalized


def _hold(
    codes: set[str],
    *,
    schema_errors: list[str] | None = None,
    input_errors: list[str] | None = None,
) -> dict[str, Any]:
    if "PREFLIGHT_INPUT_INVALID" in codes or "RAW_MANIFEST_SCHEMA_INVALID" in codes:
        processing_status = "INVALID_INPUT"
    elif "RIGHTS_SNAPSHOT_NOT_ACTIVE" in codes or "RIGHTS_ACTION_GRANT_STALE" in codes:
        processing_status = "STALE_EVIDENCE"
    else:
        processing_status = "PROVENANCE_FAILURE"
    result: dict[str, Any] = {
        "result_code": "RAW_MANIFEST_HOLD_NOT_ISSUED",
        "decision": "HOLD_NOT_ISSUED",
        "processing_status": processing_status,
        "assurance_decision": "HOLD",
        "error_codes": sorted(codes),
        "manifest": None,
    }
    if schema_errors:
        result["schema_errors"] = schema_errors
    if input_errors:
        result["input_errors"] = input_errors
    return result


def _allowed_declared_gaps(request: dict[str, Any]) -> set[str]:
    gaps = request.get("declared_preflight_gaps", [])
    if not isinstance(gaps, list):
        return {"PREFLIGHT_INPUT_INVALID"}
    return {
        gap for gap in gaps
        if isinstance(gap, str) and DECLARED_GAP_PATTERN.fullmatch(gap)
    }


def assess_preflight(
    request: dict[str, Any],
    *,
    schema_root: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return an issuance decision without writing the manifest anywhere."""

    now = now or datetime.now(timezone.utc)
    if not isinstance(request, dict):
        return _hold({"PREFLIGHT_INPUT_INVALID"})

    request_errors = _request_errors(request)
    if request_errors:
        return _hold({"PREFLIGHT_INPUT_INVALID"}, input_errors=request_errors)

    manifest = request.get("candidate_manifest")
    if not isinstance(manifest, dict):
        codes = _allowed_declared_gaps(request)
        codes.add("RAW_MANIFEST_CANDIDATE_MISSING")
        return _hold(codes)

    codes: set[str] = set()
    errors = _schema_errors(manifest, schema_root)
    if errors:
        schema_codes = {"RAW_MANIFEST_SCHEMA_INVALID"}
        if not isinstance(manifest.get("rights_snapshot"), dict):
            schema_codes.add("RIGHTS_SNAPSHOT_MISSING")
        return _hold(schema_codes, schema_errors=errors)

    context = request["request_context"]
    context_tenant = context.get("tenant_id")
    context_zone = context.get("zone")
    manifest_tenant = manifest.get("tenant_id")
    manifest_zone = manifest.get("zone")
    if not context_tenant or not manifest_tenant:
        codes.add("TENANT_CONTEXT_MISSING")
    elif context_tenant != manifest_tenant:
        codes.add("CROSS_TENANT_ACCESS_DENIED")
    if not context_zone or not manifest_zone:
        codes.add("RAW_ZONE_MISSING")
    elif context_zone != manifest_zone:
        codes.add("RAW_MANIFEST_ZONE_MISMATCH")

    provider = manifest.get("provider") if isinstance(manifest.get("provider"), dict) else {}
    provider_reference = provider.get("provider_job_reference")
    if not provider_reference:
        codes.add("PROVIDER_JOB_REFERENCE_MISSING")
    elif _is_placeholder(provider_reference):
        codes.add("PROVIDER_JOB_REFERENCE_PLACEHOLDER")

    if manifest.get("create_precondition") != "IF_GENERATION_MATCH_0":
        codes.add("CREATE_ONLY_PRECONDITION_MISSING")

    required_actions = request["required_actions"]
    required_action_set = set(required_actions)
    if not BASE_REQUIRED_ACTIONS.issubset(required_action_set):
        codes.add("REQUIRED_ACTION_SET_INCOMPLETE")

    rights = manifest["rights_snapshot"]
    if rights.get("tenant_id") != manifest_tenant:
        codes.add("RIGHTS_TENANT_MISMATCH")
    if not rights.get("approval_target_hash") or not rights.get("history_anchor_ref"):
        codes.add("RIGHTS_APPROVAL_MISSING")
    if rights.get("status") not in ISSUABLE_RIGHTS_STATUSES or rights.get("revoked_at"):
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")
    valid_from = _parse_time(rights.get("valid_from"))
    valid_until = _parse_time(rights.get("valid_until"))
    if valid_from is None or valid_from > now or (valid_until is not None and valid_until < now):
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")

    grants = rights["action_grants"]
    grant_names = [grant["action"] for grant in grants]
    if len(grant_names) != len(set(grant_names)):
        codes.add("DUPLICATE_RIGHTS_ACTION_GRANT")
    grant_map = {
        grant["action"]: grant
        for grant in grants
    }
    for action in required_action_set:
        grant = grant_map.get(action)
        if not grant or grant.get("grant_status") != "ALLOWED":
            codes.add("RIGHTS_ACTION_GRANT_MISSING")
            continue
        grant_until = _parse_time(grant.get("valid_until"))
        if grant_until is not None and grant_until < now:
            codes.add("RIGHTS_ACTION_GRANT_STALE")

    artifacts = manifest["artifacts"]
    artifact_keys: list[tuple[Any, Any]] = []
    storage_keys: list[tuple[Any, Any, Any, Any]] = []
    for artifact in artifacts:
        artifact_keys.append((artifact["artifact_id"], artifact["artifact_revision_id"]))
        storage = artifact["storage_ref"]
        storage_keys.append((
            storage.get("project_id"), storage.get("bucket_id"),
            storage.get("object_name"), storage.get("generation"),
        ))
        if artifact.get("tenant_id") != manifest_tenant:
            codes.add("CROSS_TENANT_ACCESS_DENIED")
        if artifact.get("zone") != manifest_zone:
            codes.add("RAW_MANIFEST_ZONE_MISMATCH")
        if artifact.get("rights_snapshot_id") != rights.get("rights_snapshot_id"):
            codes.add("RAW_RIGHTS_SNAPSHOT_MISMATCH")
        if not storage.get("generation"):
            codes.add("RAW_GENERATION_MISSING")
        validation = artifact["validation"]
        if validation.get("quarantine_status") != "VALIDATED":
            codes.add("RAW_ARTIFACT_NOT_VALIDATED")
        if validation.get("malware_scan", {}).get("status") != "PASS":
            codes.add("MALWARE_SCAN_NOT_PASSED")
        if validation.get("mime_check") != "MATCH":
            codes.add("MIME_CONTENT_MISMATCH")
        if validation.get("hash_check") != "MATCH":
            codes.add("ARTIFACT_HASH_MISMATCH")
        if not validation.get("reviewer") or not validation.get("reviewed_at"):
            codes.add("RAW_ARTIFACT_REVIEW_MISSING")

    if len(artifact_keys) != len(set(artifact_keys)):
        codes.add("DUPLICATE_ARTIFACT_ID")
    if len(storage_keys) != len(set(storage_keys)):
        codes.add("DUPLICATE_STORAGE_REF")

    receipts = request.get("object_creation_receipts", [])
    if not receipts:
        codes.add("OBJECT_CREATION_RECEIPT_MISSING")
    receipt_map: dict[tuple[Any, Any], list[dict[str, Any]]] = {}
    for receipt in receipts:
        key = (receipt["artifact_id"], receipt["artifact_revision_id"])
        receipt_map.setdefault(key, []).append(receipt)
    manifest_keys = set(artifact_keys)
    if any(key not in manifest_keys for key in receipt_map):
        codes.add("UNEXPECTED_OBJECT_CREATION_RECEIPT")
    if any(len(items) > 1 for items in receipt_map.values()):
        codes.add("DUPLICATE_OBJECT_CREATION_RECEIPT")
    for artifact in artifacts:
        key = (artifact["artifact_id"], artifact["artifact_revision_id"])
        matches = receipt_map.get(key, [])
        if not matches:
            codes.add("OBJECT_CREATION_RECEIPT_MISSING")
            continue
        if len(matches) > 1:
            continue
        receipt = matches[0]
        storage = artifact["storage_ref"]
        integrity = artifact["integrity"]
        if receipt.get("precondition") != "IF_GENERATION_MATCH_0":
            codes.add("CREATE_ONLY_PRECONDITION_MISSING")
        if receipt.get("outcome") != "CREATED":
            codes.add("RAW_OVERWRITE_ATTEMPT")
        if receipt.get("tenant_id") != manifest_tenant:
            codes.add("CROSS_TENANT_ACCESS_DENIED")
        if receipt.get("zone") != manifest_zone:
            codes.add("RAW_MANIFEST_ZONE_MISMATCH")
        if (
            receipt.get("project_id") != storage.get("project_id")
            or receipt.get("bucket_id") != storage.get("bucket_id")
            or receipt.get("object_name") != storage.get("object_name")
        ):
            codes.add("RAW_STORAGE_REF_MISMATCH")
        if receipt.get("generation") != storage.get("generation"):
            codes.add("RAW_STORAGE_REF_MISMATCH")
            codes.add("RAW_GENERATION_MISMATCH")
        if receipt.get("sha256") != integrity.get("sha256"):
            codes.add("ARTIFACT_HASH_MISMATCH")
        if receipt.get("byte_size") != integrity.get("byte_size"):
            codes.add("ARTIFACT_SIZE_MISMATCH")
        if receipt.get("detected_mime") != integrity.get("detected_mime"):
            codes.add("MIME_CONTENT_MISMATCH")

    parser = manifest.get("parser") if isinstance(manifest.get("parser"), dict) else {}
    if parser.get("input_bundle_hash") != manifest.get("bundle_hash"):
        codes.add("BUNDLE_HASH_MISMATCH")

    if codes:
        return _hold(codes, schema_errors=errors)
    return {
        "result_code": "RAW_MANIFEST_ISSUABLE",
        "decision": "ISSUE_ALLOWED",
        "processing_status": "VALID",
        "assurance_decision": "HOLD",
        "error_codes": [],
        "manifest": deepcopy(manifest),
    }


def assess_file(path: Path, *, schema_root: Path, now: datetime | None = None) -> dict[str, Any]:
    try:
        request = _load(path)
    except (OSError, json.JSONDecodeError):
        return _hold({"PREFLIGHT_INPUT_INVALID"})
    return assess_preflight(request, schema_root=schema_root, now=now)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--schema-root", type=Path, default=Path("schemas"))
    parser.add_argument("--now", help="ISO 8601 evaluation time; defaults to current UTC")
    args = parser.parse_args()
    evaluation_time = _parse_time(args.now) if args.now else None
    if args.now and evaluation_time is None:
        result = _hold({"PREFLIGHT_INPUT_INVALID"})
    else:
        result = assess_file(args.request, schema_root=args.schema_root.resolve(), now=evaluation_time)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["decision"] == "ISSUE_ALLOWED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
