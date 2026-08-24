"""Bind caller-supplied local artifact bytes to a manifest without issuing evidence."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any, Mapping


CONTRACT_VERSION = "LOCAL_BUNDLE_BINDING_RECEIPT_1.0.0"
ARTIFACT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,79}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
SOURCE_CLASSES = frozenset(
    {
        "PROVIDER_ORIGINAL",
        "MANUFACTURER_ORIGINAL",
        "PUBLIC_AGENCY_RECORD",
        "DERIVED_ARTIFACT",
        "SYNTHETIC_CONTROL",
    }
)
RIGHTS_ACTIONS = frozenset(
    {
        "LOCATOR",
        "FETCH",
        "PRIVATE_STORE",
        "PROCESS_LOCAL_AI",
        "DISPLAY_INTERNAL",
        "DISPLAY_EXTERNAL",
        "REDISTRIBUTE",
        "COMMERCIAL_USE",
    }
)

_MANIFEST_KEYS = frozenset(
    {
        "bundle_class",
        "bundle_id",
        "manifest_revision",
        "artifacts",
        "claimed_use_status",
        "claimed_assurance_decision",
        "claimed_suitability",
    }
)
_MANIFEST_ARTIFACT_KEYS = frozenset(
    {"artifact_id", "relative_path", "declared_sha256", "source_class", "rights"}
)
_RAW_ARTIFACT_KEYS = frozenset({"artifact_id", "relative_path", "content_bytes"})
_RIGHT_KEYS = frozenset({"action", "status", "scope_artifact_id"})
_ANCHOR_KEYS = frozenset(
    {
        "anchor_status",
        "anchor_id",
        "bundle_id",
        "manifest_sha256",
        "approved_artifact_ids",
    }
)


def _object(value: Any, allowed: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if set(value) != allowed:
        codes.add("INPUT_SHAPE_INVALID")
    return value


def _is_stable_id(value: Any) -> bool:
    return isinstance(value, str) and ARTIFACT_ID.fullmatch(value) is not None


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _path_is_safe(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 512:
        return False
    if "\x00" in value or "\\" in value or value.startswith("/"):
        return False
    parts = value.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _canonical_manifest_hash(manifest: Mapping[str, Any], codes: set[str]) -> str | None:
    try:
        encoded = json.dumps(
            manifest,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError):
        codes.add("MANIFEST_CANONICALIZATION_FAILED")
        return None
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _validate_rights(
    value: Any, artifact_id: Any, bundle_class: Any, codes: set[str]
) -> None:
    if not isinstance(value, list):
        codes.add("ACTION_RIGHTS_INVALID")
        return
    seen: set[str] = set()
    expected_status = "SYNTHETIC_ONLY" if bundle_class == "SYNTHETIC_CONTROL" else "ALLOWED"
    for raw_right in value:
        right = _object(raw_right, _RIGHT_KEYS, codes)
        action = right.get("action")
        if not isinstance(action, str) or action not in RIGHTS_ACTIONS:
            codes.add("RIGHTS_ACTION_UNKNOWN")
            continue
        if action in seen:
            codes.add("RIGHTS_ACTION_DUPLICATE")
        seen.add(action)
        if right.get("scope_artifact_id") != artifact_id:
            codes.add("RIGHTS_SCOPE_MISMATCH")
        if right.get("status") != expected_status:
            codes.add(f"RIGHTS_{action}_UNRESOLVED")
    for action in RIGHTS_ACTIONS.difference(seen):
        codes.add(f"RIGHTS_{action}_MISSING")


def _manifest_entries(
    manifest: Mapping[str, Any], bundle_class: Any, codes: set[str]
) -> dict[str, Mapping[str, Any]]:
    raw_entries = manifest.get("artifacts")
    if not isinstance(raw_entries, list):
        codes.add("MANIFEST_ARTIFACTS_INVALID")
        return {}
    if not raw_entries:
        codes.add("BUNDLE_EMPTY")

    entries: dict[str, Mapping[str, Any]] = {}
    declared_hashes: set[str] = set()
    for raw_entry in raw_entries:
        entry = _object(raw_entry, _MANIFEST_ARTIFACT_KEYS, codes)
        artifact_id = entry.get("artifact_id")
        if not _is_stable_id(artifact_id):
            codes.add("ARTIFACT_ID_INVALID")
            continue
        if artifact_id in entries:
            codes.add("DUPLICATE_ARTIFACT_ID")
            continue
        entries[artifact_id] = entry

        if not _path_is_safe(entry.get("relative_path")):
            codes.add("ARTIFACT_PATH_INVALID")
        declared_hash = entry.get("declared_sha256")
        if not _is_sha256(declared_hash):
            codes.add("DECLARED_HASH_INVALID")
        elif declared_hash in declared_hashes:
            codes.add("DUPLICATE_ARTIFACT_HASH")
        else:
            declared_hashes.add(declared_hash)

        source_class = entry.get("source_class")
        if not isinstance(source_class, str) or source_class not in SOURCE_CLASSES:
            codes.add("SOURCE_CLASS_INVALID")
        elif bundle_class == "ACTUAL_CANDIDATE" and source_class == "SYNTHETIC_CONTROL":
            codes.add("ACTUAL_SOURCE_CLASS_INVALID")
        elif bundle_class == "SYNTHETIC_CONTROL" and source_class != "SYNTHETIC_CONTROL":
            codes.add("SYNTHETIC_SOURCE_CLASS_INVALID")
        _validate_rights(entry.get("rights"), artifact_id, bundle_class, codes)
    return entries


def _raw_entries(value: Any, codes: set[str]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, list):
        codes.add("RAW_ARTIFACTS_INVALID")
        return {}
    entries: dict[str, Mapping[str, Any]] = {}
    computed_hashes: set[str] = set()
    for raw_entry in value:
        entry = _object(raw_entry, _RAW_ARTIFACT_KEYS, codes)
        artifact_id = entry.get("artifact_id")
        if not _is_stable_id(artifact_id):
            codes.add("ARTIFACT_ID_INVALID")
            continue
        if artifact_id in entries:
            codes.add("DUPLICATE_RAW_ARTIFACT_ID")
            continue
        entries[artifact_id] = entry
        if not _path_is_safe(entry.get("relative_path")):
            codes.add("ARTIFACT_PATH_INVALID")
        content = entry.get("content_bytes")
        if not isinstance(content, bytes):
            codes.add("ARTIFACT_BYTES_INVALID")
        else:
            computed_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
            if computed_hash in computed_hashes:
                codes.add("DUPLICATE_ARTIFACT_HASH")
            computed_hashes.add(computed_hash)
    return entries


def _bind_artifacts(
    manifest_entries: Mapping[str, Mapping[str, Any]],
    raw_entries: Mapping[str, Mapping[str, Any]],
    codes: set[str],
) -> tuple[int, set[str]]:
    manifest_ids = set(manifest_entries)
    raw_ids = set(raw_entries)
    if manifest_ids.difference(raw_ids):
        codes.add("ARTIFACT_MISSING")
    if raw_ids.difference(manifest_ids):
        codes.add("EXTRA_ARTIFACT")

    bound_count = 0
    for artifact_id in sorted(manifest_ids.intersection(raw_ids)):
        manifest_entry = manifest_entries[artifact_id]
        raw_entry = raw_entries[artifact_id]
        content = raw_entry.get("content_bytes")
        if not isinstance(content, bytes):
            continue
        if raw_entry.get("relative_path") != manifest_entry.get("relative_path"):
            codes.add("ARTIFACT_PATH_MISMATCH")
            continue
        computed_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
        if computed_hash != manifest_entry.get("declared_sha256"):
            codes.add("ARTIFACT_HASH_MISMATCH")
            continue
        bound_count += 1
    return bound_count, manifest_ids


def _validate_anchor(
    value: Any,
    manifest: Mapping[str, Any],
    manifest_hash: str | None,
    artifact_ids: set[str],
    codes: set[str],
) -> None:
    if value is None:
        codes.add("EXTERNAL_APPROVAL_ANCHOR_MISSING")
        return
    anchor = _object(value, _ANCHOR_KEYS, codes)
    if not anchor:
        codes.add("EXTERNAL_APPROVAL_ANCHOR_MISSING")
        return
    approved_ids = anchor.get("approved_artifact_ids")
    ids_match = (
        isinstance(approved_ids, list)
        and all(_is_stable_id(item) for item in approved_ids)
        and len(approved_ids) == len(set(approved_ids))
        and set(approved_ids) == artifact_ids
    )
    if (
        anchor.get("anchor_status") != "APPROVED"
        or not _is_stable_id(anchor.get("anchor_id"))
        or anchor.get("bundle_id") != manifest.get("bundle_id")
        or manifest_hash is None
        or anchor.get("manifest_sha256") != manifest_hash
        or not ids_match
    ):
        codes.add("EXTERNAL_APPROVAL_ANCHOR_MISMATCH")


def evaluate_local_bundle(
    manifest: Any,
    raw_artifacts: Any,
    *,
    external_approval_anchor: Any = None,
) -> dict[str, Any]:
    """Return a bounded binding receipt for an in-memory local bundle.

    The receipt never returns raw bytes, paths, identifiers, or hashes.  Even a
    complete actual candidate is only ready for independent review; it is not
    issued evidence and cannot be used for a decision.
    """

    codes: set[str] = set()
    manifest_object = _object(manifest, _MANIFEST_KEYS, codes)
    bundle_class = manifest_object.get("bundle_class")
    actual = bundle_class == "ACTUAL_CANDIDATE"
    synthetic = bundle_class == "SYNTHETIC_CONTROL"
    if not actual and not synthetic:
        codes.add("BUNDLE_CLASS_INVALID")
    if not _is_stable_id(manifest_object.get("bundle_id")):
        codes.add("BUNDLE_ID_INVALID")
    if not _is_stable_id(manifest_object.get("manifest_revision")):
        codes.add("MANIFEST_REVISION_INVALID")
    if (
        manifest_object.get("claimed_use_status") != "NOT_FOR_DECISION"
        or manifest_object.get("claimed_assurance_decision") != "HOLD"
        or manifest_object.get("claimed_suitability") != "NOT_EVALUATED"
    ):
        codes.add("OPTIMISTIC_DECISION_FORBIDDEN")

    manifest_entries = _manifest_entries(manifest_object, bundle_class, codes)
    raw_entries = _raw_entries(raw_artifacts, codes)
    bound_count, artifact_ids = _bind_artifacts(manifest_entries, raw_entries, codes)
    manifest_hash = _canonical_manifest_hash(manifest_object, codes)
    if actual:
        _validate_anchor(
            external_approval_anchor,
            manifest_object,
            manifest_hash,
            artifact_ids,
            codes,
        )
    elif synthetic:
        codes.add("SYNTHETIC_ONLY")

    source_counts = Counter(
        entry.get("source_class")
        for entry in manifest_entries.values()
        if isinstance(entry.get("source_class"), str)
        and entry.get("source_class") in SOURCE_CLASSES
    )
    source_coverage = [
        {"source_class": source_class, "artifact_count": source_counts[source_class]}
        for source_class in sorted(source_counts)
    ]

    if synthetic:
        binding_status = "SYNTHETIC_CONTROL"
    elif actual and not codes:
        binding_status = "READY_FOR_REVIEW"
    else:
        binding_status = "HOLD_NOT_ISSUED"

    if "INPUT_SHAPE_INVALID" in codes or "MANIFEST_CANONICALIZATION_FAILED" in codes:
        processing_status = "INVALID_INPUT"
    elif any("HASH" in code or "ARTIFACT_MISSING" == code or "EXTRA_ARTIFACT" == code for code in codes):
        processing_status = "INTEGRITY_FAILURE"
    elif any(code.startswith(("RIGHTS_", "EXTERNAL_APPROVAL_")) for code in codes):
        processing_status = "PROVENANCE_FAILURE"
    else:
        processing_status = "VALID"

    return {
        "contract_version": CONTRACT_VERSION,
        "bundle_class": bundle_class if actual or synthetic else "INVALID",
        "processing_status": processing_status,
        "binding_status": binding_status,
        "coverage": {
            "manifest_artifact_count": len(manifest_entries),
            "bound_artifact_count": bound_count,
            "source_classes": source_coverage,
        },
        "blocker_codes": sorted(codes),
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
