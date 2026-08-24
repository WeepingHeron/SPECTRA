"""Decide whether reviewed environment evidence is eligible for contract issuance.

This gate consumes approval metadata only. It never reads or returns dose values.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .gate import REFERENCE_MISSION, REQUIRED_ROLES


REQUIRED_ISSUANCE_ACTIONS = frozenset({
    "FETCH",
    "PRIVATE_STORE",
    "PROCESS_LOCAL",
    "DISPLAY_INTERNAL",
    "DISPLAY_EXTERNAL",
    "REDISTRIBUTE",
    "COMMERCIAL_USE",
    "AUTOMATION",
    "CLOUD_STORE",
})
ALLOWED_AUXILIARY_ROLES = {"ORBIT_OUTPUT", "SOLAR_ATTENUATION"}
EXPECTED_PLATFORM_BUILD = "4.6.14.3582"
EXPECTED_SHIELDING_DEPTHS = [1.0, 2.0, 3.0, 4.0]
TRUST_STORE_SCHEMA_VERSION = "1.0.0"
TRUST_STORE_AUDIENCE = "SPECTRA_ENVIRONMENT_ISSUANCE"
TRUST_STORE_SCOPE = "RADIATION_ENVIRONMENT"
TRUST_ANCHOR_FIELDS = frozenset({
    "anchor_id",
    "status",
    "approver",
    "history_anchor_ref",
    "review_payload_hash",
    "provider_record_hash",
    "provider_job_reference",
    "rights_snapshot_id",
    "rights_scope_hash",
    "raw_manifest_hash",
    "raw_bundle_hash",
    "raw_storage_generation",
    "scientific_crosscheck_result_hash",
    "emission_authorization_target_hash",
})
TRUST_STORE_FIELDS = frozenset({
    "store_schema_version",
    "snapshot_id",
    "snapshot_hash",
    "audience",
    "scope",
    "immutable",
    "entries",
})
TRUST_STORE_ENTRY_FIELDS = frozenset({
    "anchor_id",
    "anchor_digest",
    "approver",
    "audience",
    "scope",
    "evidence_class",
    "valid_from",
    "valid_until",
    "revoked",
})
PAYLOAD_TRUST_FIELDS = frozenset({
    "trusted_anchor",
    "deployment_trust_store",
    "trust_store",
    "trust_store_path",
    "issuance_allowlist",
    "allowlist",
})


@dataclass(frozen=True)
class DeploymentTrustStoreSnapshot:
    """Canonical immutable deployment configuration, never request payload."""

    canonical_json: str


def freeze_deployment_trust_store_snapshot(value: Any) -> DeploymentTrustStoreSnapshot | None:
    """Copy a deployment-owned JSON value into an immutable canonical snapshot."""

    if not isinstance(value, dict):
        return None
    try:
        canonical = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return None
    return DeploymentTrustStoreSnapshot(canonical_json=canonical)


def _canonical_sha256(value: Any) -> str | None:
    try:
        canonical = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def issuance_review_hash(evidence: dict[str, Any]) -> str:
    """Hash the exact review payload, including its evidence classification."""

    digest = _canonical_sha256(evidence)
    if digest is None:
        raise ValueError("review payload is not canonical JSON")
    return digest


def issuance_anchor_digest(anchor: Any) -> str | None:
    """Return the canonical digest used by the deployment trust store."""

    if not isinstance(anchor, dict) or set(anchor) != TRUST_ANCHOR_FIELDS:
        return None
    return _canonical_sha256(anchor)


def issuance_trust_store_hash(store: Any) -> str | None:
    """Hash a trust-store snapshot without its self-referential hash field."""

    if not isinstance(store, dict) or set(store) != TRUST_STORE_FIELDS:
        return None
    preimage = dict(store)
    preimage.pop("snapshot_hash", None)
    return _canonical_sha256(preimage)


def _result(codes: set[str], *, control_only: bool = False) -> dict[str, Any]:
    if not codes and not control_only:
        return {
            "gate_status": "READY_FOR_REVIEW",
            "issuance_status": "ISSUABLE_CANDIDATE",
            "processing_status": "VALID",
            "assurance_decision": "HOLD",
            "error_codes": [],
            "normalized_environment": None,
            "control_only": False,
        }
    if control_only and not codes:
        codes = {"SYNTHETIC_CONTROL_ONLY"}
        processing_status = "VALID"
    else:
        processing_status = "PROVENANCE_FAILURE"
    return {
        "gate_status": "HOLD",
        "issuance_status": "HOLD_NOT_ISSUED",
        "processing_status": processing_status,
        "assurance_decision": "HOLD",
        "error_codes": sorted(codes),
        "normalized_environment": None,
        "control_only": control_only,
    }


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _active_at(valid_from: Any, valid_until: Any, now: datetime) -> bool:
    start = _parse_time(valid_from)
    end = _parse_time(valid_until)
    if start is None or end is None or start.tzinfo is None or end.tzinfo is None:
        return False
    return start <= now <= end


def _is_aware_datetime(value: Any) -> bool:
    if not isinstance(value, datetime) or value.tzinfo is None:
        return False
    try:
        return value.utcoffset() is not None
    except (OverflowError, TypeError, ValueError):
        return False


def _provider_codes(provider: Any) -> set[str]:
    if not isinstance(provider, dict):
        return {"PROVIDER_JOB_REFERENCE_MISSING"}
    reference = provider.get("provider_job_reference")
    if not isinstance(reference, str) or not reference.strip():
        return {"PROVIDER_JOB_REFERENCE_MISSING"}
    required = ("source_locator", "source_location", "record_hash", "reviewer", "history_anchor_ref")
    if provider.get("reference_status") != "VERIFIED_PROVIDER_RECORD" or any(
        not isinstance(provider.get(field), str) or not provider[field]
        for field in required
    ):
        return {"PROVIDER_JOB_REFERENCE_UNVERIFIED"}
    return set()


def _rights_codes(rights: Any, now: datetime) -> set[str]:
    if not isinstance(rights, dict):
        return {"RIGHTS_ACTION_GRANT_MISSING", "RIGHTS_APPROVAL_MISSING"}

    codes: set[str] = set()
    snapshot_id = rights.get("rights_snapshot_id")
    scope_hash = rights.get("required_scope_hash")
    subject = rights.get("subject")
    approver = rights.get("approver")
    if rights.get("status") != "APPROVED" or not all(
        isinstance(value, str) and value
        for value in (snapshot_id, scope_hash, subject, approver)
    ):
        codes.add("RIGHTS_APPROVAL_MISSING")
    if not _active_at(rights.get("valid_from"), rights.get("valid_until"), now):
        codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")

    grants = rights.get("action_grants")
    if not isinstance(grants, list):
        return codes | {"RIGHTS_ACTION_GRANT_MISSING"}
    actions = [
        grant.get("action")
        for grant in grants
        if isinstance(grant, dict) and isinstance(grant.get("action"), str)
    ]
    if len(actions) != len(grants):
        codes.add("RIGHTS_ACTION_SET_INVALID")
    counts = Counter(actions)
    if any(count > 1 for count in counts.values()):
        codes.add("DUPLICATE_RIGHTS_ACTION_GRANT")
    if set(actions) - REQUIRED_ISSUANCE_ACTIONS:
        codes.add("RIGHTS_ACTION_SET_INVALID")
    if REQUIRED_ISSUANCE_ACTIONS - set(actions):
        codes.add("RIGHTS_ACTION_GRANT_MISSING")

    for action in REQUIRED_ISSUANCE_ACTIONS:
        matching = [grant for grant in grants if isinstance(grant, dict) and grant.get("action") == action]
        if len(matching) != 1 or matching[0].get("grant_status") != "ALLOWED":
            codes.add("RIGHTS_ACTION_GRANT_MISSING")
            continue
        grant = matching[0]
        if grant.get("scope_hash") != scope_hash or grant.get("subject") != subject:
            codes.add("RIGHTS_ACTION_SCOPE_MISMATCH")
        if grant.get("approver") != approver:
            codes.add("RIGHTS_APPROVAL_MISMATCH")
        if not all(
            isinstance(grant.get(field), str) and grant[field]
            for field in ("source_locator", "source_location")
        ):
            codes.add("RIGHTS_GRANT_PROVENANCE_MISSING")
        if not _active_at(grant.get("valid_from"), grant.get("valid_until"), now):
            codes.add("RIGHTS_ACTION_GRANT_STALE")
    return codes


def _artifact_codes(identity: Any, raw_manifest: Any) -> set[str]:
    if not isinstance(identity, dict):
        return {"ARTIFACT_IDENTITY_NOT_VERIFIED"}
    codes: set[str] = set()
    entries = identity.get("artifacts")
    if not isinstance(entries, list):
        return {"ARTIFACT_IDENTITY_NOT_VERIFIED", "SOURCE_ROLE_MISSING"}

    roles: Counter[str] = Counter()
    identities: dict[str, set[str]] = {}
    paths: dict[str, set[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            codes.add("ARTIFACT_IDENTITY_NOT_VERIFIED")
            continue
        role = entry.get("role")
        digest = entry.get("identity_sha256")
        resolved_path = entry.get("resolved_path")
        if not all(isinstance(value, str) and value for value in (role, digest, resolved_path)):
            codes.add("ARTIFACT_IDENTITY_NOT_VERIFIED")
            continue
        if role not in REQUIRED_ROLES | ALLOWED_AUXILIARY_ROLES:
            codes.add("SOURCE_ROLE_UNEXPECTED")
            continue
        if role in REQUIRED_ROLES:
            roles[role] += 1
            identities.setdefault(digest, set()).add(role)
            paths.setdefault(resolved_path, set()).add(role)

    if REQUIRED_ROLES - roles.keys():
        codes.add("SOURCE_ROLE_MISSING")
    if any(count > 1 for count in roles.values()):
        codes.add("SOURCE_ROLE_DUPLICATED")
    if any(len(role_set) > 1 for role_set in identities.values()):
        codes.add("ARTIFACT_ID_REUSED_ACROSS_ROLES")
    if any(len(role_set) > 1 for role_set in paths.values()):
        codes.add("RESOLVED_PATH_REUSED_ACROSS_ROLES")
    if identity.get("checksum_verified") is not True or identity.get("checksum_count") != 9:
        codes.add("ARTIFACT_IDENTITY_NOT_VERIFIED")
    if (
        isinstance(raw_manifest, dict)
        and isinstance(raw_manifest.get("bundle_hash"), str)
        and identity.get("artifact_set_hash") != raw_manifest.get("bundle_hash")
    ):
        codes.add("RAW_BUNDLE_HASH_MISMATCH")
    return codes


def _manifest_codes(raw_manifest: Any, storage: Any, rights: Any) -> set[str]:
    codes: set[str] = set()
    manifest_approved = isinstance(raw_manifest, dict) and raw_manifest.get("status") == "APPROVED"
    if not manifest_approved:
        codes.add("RAW_ARTIFACT_MANIFEST_V2_MISSING")
    if not isinstance(storage, dict) or storage.get("status") != "APPROVED" or storage.get("immutable") is not True:
        codes.add("APPROVED_STORAGE_UNAVAILABLE")
    else:
        storage_identity = storage.get("identity")
        if not isinstance(storage_identity, dict) or any(
            not isinstance(storage_identity.get(field), str) or not storage_identity[field]
            for field in ("project_id", "bucket_id", "object_name", "generation")
        ):
            codes.add("APPROVED_STORAGE_UNAVAILABLE")
        elif manifest_approved and raw_manifest.get("storage_generation") != storage_identity.get("generation"):
            codes.add("RAW_GENERATION_MISMATCH")
    if not manifest_approved:
        return codes
    if raw_manifest.get("contract_version") != "2.0.0" or not raw_manifest.get("manifest_hash"):
        codes.add("RAW_ARTIFACT_MANIFEST_V2_MISSING")
    if not isinstance(rights, dict) or raw_manifest.get("rights_snapshot_id") != rights.get("rights_snapshot_id"):
        codes.add("RAW_RIGHTS_SNAPSHOT_MISMATCH")
    if raw_manifest.get("parser_input_hash") != raw_manifest.get("bundle_hash"):
        codes.add("RAW_PARSER_INPUT_HASH_MISMATCH")
    if not raw_manifest.get("parser_output_hash"):
        codes.add("RAW_PARSER_OUTPUT_HASH_MISSING")
    if not raw_manifest.get("history_anchor_ref"):
        codes.add("RAW_HISTORY_ANCHOR_MISSING")
    validation = raw_manifest.get("validation")
    if not isinstance(validation, dict) or any(
        validation.get(field) != expected
        for field, expected in {
            "quarantine_status": "VALIDATED",
            "malware_scan": "PASS",
            "mime_check": "MATCH",
            "hash_check": "MATCH",
            "review_status": "APPROVED",
        }.items()
    ):
        codes.add("RAW_ARTIFACT_VALIDATION_INCOMPLETE")
    return codes


def _model_codes(model: Any) -> set[str]:
    if not isinstance(model, dict):
        return {"MODEL_CONFIGURATION_NOT_VERIFIED"}
    codes: set[str] = set()
    if model.get("mission") != REFERENCE_MISSION:
        codes.add("MODEL_CONFIGURATION_MISMATCH")
    if model.get("source_completeness") != "COMPLETE_MISSION":
        codes.add("SOURCE_COMPLETENESS_MISSING")
    if model.get("platform_build") != EXPECTED_PLATFORM_BUILD:
        codes.add("MODEL_VERSION_DRIFT")
    if model.get("geometry") != "CENTRE_OF_AL_SPHERES_4PI":
        codes.add("MODEL_CONFIGURATION_MISMATCH")
    if model.get("target_material") != "SILICON" or model.get("dose_unit") != "rad(Si)":
        codes.add("MODEL_CONFIGURATION_MISMATCH")
    if model.get("shielding_depths_mm_al") != EXPECTED_SHIELDING_DEPTHS:
        codes.add("SHIELDING_POINTS_MISMATCH")
    chain = model.get("model_chain")
    if not isinstance(chain, dict):
        return codes | {"MODEL_CONFIGURATION_NOT_VERIFIED"}
    if chain.get("trapped") != {"name": "AE9/AP9", "version": "1.50", "run_mode": "MEAN", "verification_status": "VERIFIED_REPORT"}:
        codes.add("MODEL_VERSION_NOT_VERIFIED")
    if chain.get("solar") != {"name": "SAPPHIRE", "mode": "TOTAL_FLUENCE", "confidence_percent": 95, "verification_status": "VERIFIED_REPORT"}:
        codes.add("MODEL_CONFIGURATION_NOT_VERIFIED")
    if chain.get("dose") != {"name": "SHIELDOSE-2", "version": "2.10", "verification_status": "VERIFIED_REPORT"}:
        codes.add("MODEL_VERSION_NOT_VERIFIED")
    return codes


def _crosscheck_codes(crosscheck: Any) -> set[str]:
    if not isinstance(crosscheck, dict) or crosscheck.get("status") == "NOT_EVALUATED":
        return {"SCIENTIFIC_CROSSCHECK_NOT_EVALUATED"}
    if crosscheck.get("status") != "PASSED":
        return {"SCIENTIFIC_CROSSCHECK_FAILED"}
    required = ("protocol_hash", "criteria_source", "reviewer", "result_hash")
    if crosscheck.get("protocol_status") != "APPROVED_BEFORE_RESULTS" or any(
        not isinstance(crosscheck.get(field), str) or not crosscheck[field]
        for field in required
    ):
        return {"SCIENTIFIC_CROSSCHECK_NOT_EVALUATED"}
    return set()


def _authorization_codes(authorization: Any, raw_manifest: Any) -> set[str]:
    if not isinstance(authorization, dict) or authorization.get("status") != "APPROVED":
        return {"CONTRACT_EMISSION_NOT_APPROVED"}
    if not isinstance(raw_manifest, dict) or authorization.get("approval_target_hash") != raw_manifest.get("manifest_hash"):
        return {"EMISSION_AUTHORIZATION_TARGET_MISMATCH"}
    if not all(isinstance(authorization.get(field), str) and authorization[field] for field in ("approver", "history_anchor_ref")):
        return {"CONTRACT_EMISSION_NOT_APPROVED"}
    return set()


def _trusted_anchor_binding_codes(evidence: dict[str, Any], trusted_anchor: Any) -> set[str]:
    codes: set[str] = set()
    if not isinstance(trusted_anchor, dict):
        codes.add("ISSUANCE_TRUST_ANCHOR_MISSING")
        return codes

    if set(trusted_anchor) != TRUST_ANCHOR_FIELDS or (
        not isinstance(trusted_anchor.get("anchor_id"), str)
        or not trusted_anchor["anchor_id"]
        or trusted_anchor.get("status") != "APPROVED"
        or not isinstance(trusted_anchor.get("approver"), str)
        or not trusted_anchor["approver"]
        or not isinstance(trusted_anchor.get("history_anchor_ref"), str)
        or not trusted_anchor["history_anchor_ref"]
    ):
        codes.add("ISSUANCE_TRUST_ANCHOR_INVALID")

    provider = evidence.get("provider")
    provider = provider if isinstance(provider, dict) else {}
    raw_manifest = evidence.get("raw_manifest")
    raw_manifest = raw_manifest if isinstance(raw_manifest, dict) else {}
    storage = evidence.get("approved_storage")
    storage = storage if isinstance(storage, dict) else {}
    storage_identity = storage.get("identity")
    storage_identity = storage_identity if isinstance(storage_identity, dict) else {}
    crosscheck = evidence.get("scientific_crosscheck")
    crosscheck = crosscheck if isinstance(crosscheck, dict) else {}
    authorization = evidence.get("emission_authorization")
    authorization = authorization if isinstance(authorization, dict) else {}

    target_pairs = (
        ("review_payload_hash", _canonical_sha256(evidence)),
        ("provider_record_hash", provider.get("record_hash")),
        ("provider_job_reference", provider.get("provider_job_reference")),
        ("raw_manifest_hash", raw_manifest.get("manifest_hash")),
        ("raw_bundle_hash", raw_manifest.get("bundle_hash")),
        ("scientific_crosscheck_result_hash", crosscheck.get("result_hash")),
        ("emission_authorization_target_hash", authorization.get("approval_target_hash")),
    )
    if any(
        not isinstance(expected, str)
        or not expected
        or trusted_anchor.get(anchor_key) != expected
        for anchor_key, expected in target_pairs
    ):
        codes.add("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH")

    expected_generation = raw_manifest.get("storage_generation")
    if (
        not isinstance(expected_generation, str)
        or not expected_generation
        or storage_identity.get("generation") != expected_generation
        or trusted_anchor.get("raw_storage_generation") != expected_generation
    ):
        codes.add("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH")

    rights = evidence.get("rights_snapshot")
    rights = rights if isinstance(rights, dict) else {}
    rights_pairs = (
        ("rights_snapshot_id", rights.get("rights_snapshot_id")),
        ("rights_scope_hash", rights.get("required_scope_hash")),
    )
    if any(
        not isinstance(expected, str)
        or not expected
        or trusted_anchor.get(anchor_key) != expected
        for anchor_key, expected in rights_pairs
    ):
        codes.add("ISSUANCE_TRUST_ANCHOR_RIGHTS_MISMATCH")
    return codes


def _deployment_trust_store_codes(
    evidence: dict[str, Any],
    trusted_anchor: Any,
    deployment_trust_store: Any,
    now: datetime,
) -> set[str]:
    codes = _trusted_anchor_binding_codes(evidence, trusted_anchor)
    if "trusted_anchor" in evidence:
        codes.add("ISSUANCE_TRUST_ANCHOR_IN_PAYLOAD")
    if PAYLOAD_TRUST_FIELDS & evidence.keys():
        codes.add("ISSUANCE_TRUST_STORE_IN_PAYLOAD")

    # Existing callers remain production-safe: a plain anchor is diagnostic
    # input only and cannot authenticate without deployment configuration.
    if deployment_trust_store is None:
        codes.add("ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED")
        return codes
    if not isinstance(deployment_trust_store, DeploymentTrustStoreSnapshot):
        return codes | {"ISSUANCE_TRUST_STORE_INVALID"}
    try:
        deployment_trust_store = json.loads(deployment_trust_store.canonical_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        return codes | {"ISSUANCE_TRUST_STORE_INVALID"}
    if not isinstance(deployment_trust_store, dict):
        return codes | {"ISSUANCE_TRUST_STORE_INVALID"}

    if set(deployment_trust_store) != TRUST_STORE_FIELDS:
        codes.add("ISSUANCE_TRUST_STORE_INVALID")
    if (
        deployment_trust_store.get("store_schema_version") != TRUST_STORE_SCHEMA_VERSION
        or not isinstance(deployment_trust_store.get("snapshot_id"), str)
        or not deployment_trust_store.get("snapshot_id")
        or deployment_trust_store.get("audience") != TRUST_STORE_AUDIENCE
        or deployment_trust_store.get("scope") != TRUST_STORE_SCOPE
        or deployment_trust_store.get("immutable") is not True
    ):
        codes.add("ISSUANCE_TRUST_STORE_INVALID")

    expected_store_hash = issuance_trust_store_hash(deployment_trust_store)
    if (
        expected_store_hash is None
        or deployment_trust_store.get("snapshot_hash") != expected_store_hash
    ):
        codes.add("ISSUANCE_TRUST_STORE_SNAPSHOT_MISMATCH")

    entries = deployment_trust_store.get("entries")
    if not isinstance(entries, list) or not entries:
        return codes | {"ISSUANCE_TRUST_STORE_INVALID"}

    entry_ids: list[str] = []
    entry_digests: list[str] = []
    valid_entries: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != TRUST_STORE_ENTRY_FIELDS:
            codes.add("ISSUANCE_TRUST_STORE_INVALID")
            continue
        anchor_id = entry.get("anchor_id")
        anchor_digest = entry.get("anchor_digest")
        approver = entry.get("approver")
        if not all(isinstance(value, str) and value for value in (anchor_id, anchor_digest, approver)):
            codes.add("ISSUANCE_TRUST_STORE_INVALID")
            continue
        if not isinstance(entry.get("revoked"), bool):
            codes.add("ISSUANCE_TRUST_STORE_INVALID")
            continue
        valid_from = _parse_time(entry.get("valid_from"))
        valid_until = _parse_time(entry.get("valid_until"))
        if (
            valid_from is None
            or valid_until is None
            or valid_from.tzinfo is None
            or valid_until.tzinfo is None
            or valid_from > valid_until
        ):
            codes.add("ISSUANCE_TRUST_STORE_INVALID")
            continue
        entry_ids.append(anchor_id)
        entry_digests.append(anchor_digest)
        valid_entries.append(entry)

    if any(count > 1 for count in Counter(entry_ids).values()):
        codes.add("ISSUANCE_TRUST_STORE_DUPLICATE_ANCHOR_ID")
    if any(count > 1 for count in Counter(entry_digests).values()):
        codes.add("ISSUANCE_TRUST_STORE_DUPLICATE_ANCHOR_DIGEST")

    if not isinstance(trusted_anchor, dict):
        return codes
    anchor_id = trusted_anchor.get("anchor_id")
    matching = [entry for entry in valid_entries if entry.get("anchor_id") == anchor_id]
    if len(matching) != 1:
        codes.add("ISSUANCE_TRUST_STORE_ANCHOR_UNKNOWN")
        return codes

    entry = matching[0]
    anchor_digest = issuance_anchor_digest(trusted_anchor)
    if anchor_digest is None or entry.get("anchor_digest") != anchor_digest:
        codes.add("ISSUANCE_TRUST_STORE_ANCHOR_DIGEST_MISMATCH")
    if entry.get("approver") != trusted_anchor.get("approver"):
        codes.add("ISSUANCE_TRUST_STORE_APPROVER_MISMATCH")
    if (
        entry.get("audience") != TRUST_STORE_AUDIENCE
        or entry.get("audience") != deployment_trust_store.get("audience")
        or entry.get("scope") != TRUST_STORE_SCOPE
        or entry.get("scope") != deployment_trust_store.get("scope")
    ):
        codes.add("ISSUANCE_TRUST_STORE_SCOPE_MISMATCH")
    if entry.get("evidence_class") != evidence.get("evidence_class"):
        codes.add("ISSUANCE_TRUST_STORE_EVIDENCE_CLASS_MISMATCH")
    if entry.get("revoked") is True:
        codes.add("ISSUANCE_TRUST_STORE_ENTRY_REVOKED")
    if not _active_at(entry.get("valid_from"), entry.get("valid_until"), now):
        codes.add("ISSUANCE_TRUST_STORE_ENTRY_NOT_ACTIVE")
    return codes


def assess_issuance(
    evidence: Any,
    *,
    now: Any = None,
    trusted_anchor: Any = None,
    deployment_trust_store: Any = None,
) -> dict[str, Any]:
    """Return issuance eligibility without emitting a radiation contract."""

    if not isinstance(evidence, dict):
        return _result({"ISSUANCE_EVIDENCE_INVALID"})
    control_only = evidence.get("evidence_class") == "SYNTHETIC_CONTROL"
    if evidence.get("evidence_class") not in {"ACTUAL_REVIEW", "SYNTHETIC_CONTROL"}:
        return _result({"ISSUANCE_EVIDENCE_INVALID"})
    if now is None:
        now = datetime.now(timezone.utc)
    elif not _is_aware_datetime(now):
        return _result({"ISSUANCE_EVALUATION_TIME_INVALID"}, control_only=control_only)

    raw_manifest = evidence.get("raw_manifest")
    rights = evidence.get("rights_snapshot")
    storage = evidence.get("approved_storage")
    codes = set()
    codes |= _provider_codes(evidence.get("provider"))
    codes |= _rights_codes(rights, now)
    codes |= _manifest_codes(raw_manifest, storage, rights)
    codes |= _artifact_codes(evidence.get("artifact_identity"), raw_manifest)
    codes |= _model_codes(evidence.get("model_conditions"))
    codes |= _crosscheck_codes(evidence.get("scientific_crosscheck"))
    codes |= _authorization_codes(evidence.get("emission_authorization"), raw_manifest)
    if evidence.get("evidence_class") == "ACTUAL_REVIEW":
        codes |= _deployment_trust_store_codes(
            evidence,
            trusted_anchor,
            deployment_trust_store,
            now,
        )
    return _result(codes, control_only=control_only)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument(
        "--trusted-anchor",
        type=Path,
        help="Out-of-band issuance trust anchor JSON for ACTUAL_REVIEW",
    )
    parser.add_argument(
        "--deployment-trust-store",
        type=Path,
        help="Deployment-owned immutable trust-store snapshot JSON",
    )
    args = parser.parse_args()
    try:
        evidence = json.loads(args.review.read_text(encoding="utf-8"))
    except (OSError, RuntimeError, ValueError, UnicodeError, json.JSONDecodeError):
        result = _result({"ISSUANCE_EVIDENCE_INVALID"})
    else:
        trusted_anchor = None
        if args.trusted_anchor is not None:
            try:
                trusted_anchor = json.loads(args.trusted_anchor.read_text(encoding="utf-8"))
            except (OSError, RuntimeError, ValueError, UnicodeError, json.JSONDecodeError):
                trusted_anchor = None
        deployment_trust_store = None
        if args.deployment_trust_store is not None:
            try:
                deployment_trust_store = freeze_deployment_trust_store_snapshot(
                    json.loads(args.deployment_trust_store.read_text(encoding="utf-8"))
                )
            except (OSError, RuntimeError, ValueError, UnicodeError, json.JSONDecodeError):
                deployment_trust_store = freeze_deployment_trust_store_snapshot(
                    {"invalid_deployment_trust_store": True}
                )
        result = assess_issuance(
            evidence,
            trusted_anchor=trusted_anchor,
            deployment_trust_store=deployment_trust_store,
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["issuance_status"] == "ISSUABLE_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
