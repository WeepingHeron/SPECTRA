"""Validate a local NASA public-database snapshot candidate without fetching it.

This module does not connect to NASA, download records, issue an evidence
contract, or decide part suitability.  It checks caller-supplied bytes and
metadata, then returns a bounded review status that always ends in HOLD.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlsplit

CONTRACT_VERSION = "NASA_SNAPSHOT_GATE_1.0.0"
MAX_SNAPSHOT_AGE = timedelta(days=30)
MAX_CLOCK_SKEW = timedelta(minutes=5)
REQUIRED_ACTIONS = frozenset(
    {"LOCATOR_SHARE", "FETCH", "PRIVATE_STORE", "PROCESS_LOCAL", "DISPLAY_INTERNAL"}
)
EXPECTED_CANDIDATE_KEYS = frozenset(
    {
        "snapshot_class",
        "provider",
        "record_id",
        "official_locator",
        "redirect_chain",
        "captured_at",
        "last_modified",
        "source_revision",
        "content_sha256",
        "rights",
        "part_identity",
        "claimed_decision",
        "claimed_suitability",
    }
)
FORBIDDEN_APPROVAL_KEYS = frozenset(
    {"approval", "approved", "approved_by", "trusted_manifest", "trusted_rights", "trusted_bom"}
)
RECORD_ID = re.compile(r"^NASA-[A-Z0-9][A-Z0-9._:-]{2,79}$")
REVISION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/ -]{0,119}$")
PART_NUMBER = re.compile(r"^[A-Z0-9][A-Z0-9._/+()-]{1,79}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _is_text(value: Any, limit: int = 160) -> bool:
    return isinstance(value, str) and 0 < len(value) <= limit and "\x00" not in value


def _parse_time(value: Any, code: str, codes: list[str]) -> datetime | None:
    if not _is_text(value, 64):
        codes.append(code)
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        codes.append(code)
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        codes.append("TIMEZONE_REQUIRED")
        return None
    return parsed.astimezone(timezone.utc)


def _locator_codes(locator: Any, redirects: Any) -> list[str]:
    codes: list[str] = []
    if not _is_text(locator, 500):
        return ["OFFICIAL_LOCATOR_INVALID"]
    try:
        parsed = urlsplit(locator)
    except ValueError:
        return ["OFFICIAL_LOCATOR_INVALID"]
    try:
        port = parsed.port
    except ValueError:
        return ["OFFICIAL_LOCATOR_INVALID"]
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme != "https"
        or not host
        or not (host == "nasa.gov" or host.endswith(".nasa.gov"))
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or bool(parsed.fragment)
    ):
        codes.append("OFFICIAL_LOCATOR_NOT_ALLOWLISTED")
    if not isinstance(redirects, list):
        codes.append("REDIRECT_CHAIN_INVALID")
    elif redirects:
        codes.append("REDIRECT_NOT_ALLOWED")
    return codes


def _rights_codes(rights: Any, snapshot_class: Any) -> list[str]:
    if not isinstance(rights, list):
        return ["ACTION_RIGHTS_INVALID"]
    codes: list[str] = []
    seen: set[str] = set()
    for grant in rights:
        if not isinstance(grant, dict) or set(grant) != {
            "action",
            "grant_status",
            "grant_source",
            "inherited_from",
        }:
            codes.append("ACTION_RIGHTS_INVALID")
            continue
        action = grant.get("action")
        if not isinstance(action, str) or action not in REQUIRED_ACTIONS or action in seen:
            codes.append("ACTION_RIGHTS_INVALID")
            continue
        seen.add(action)
        if grant.get("inherited_from") is not None:
            codes.append("RIGHTS_INHERITANCE_FORBIDDEN")
        expected_source = (
            "SYNTHETIC_CONTROL_ONLY"
            if snapshot_class == "SYNTHETIC_CONTROL"
            else "NASA_DIRECT_GRANT"
        )
        if grant.get("grant_status") != "ALLOWED" or grant.get("grant_source") != expected_source:
            codes.append("ACTION_RIGHT_NOT_ACTIVE")
    if seen != REQUIRED_ACTIONS:
        codes.append("ACTION_RIGHTS_INCOMPLETE")
    return codes


def _part_codes(identity: Any) -> list[str]:
    if not isinstance(identity, dict) or set(identity) != {
        "manufacturer",
        "orderable_part_number",
        "identity_status",
    }:
        return ["PART_IDENTITY_INVALID"]
    codes: list[str] = []
    if identity.get("identity_status") != "EXACT_ORDERABLE":
        codes.append("FAMILY_ONLY_PART_REJECTED")
    if not _is_text(identity.get("manufacturer"), 100):
        codes.append("PART_MANUFACTURER_INVALID")
    part_number = identity.get("orderable_part_number")
    if not isinstance(part_number, str) or not PART_NUMBER.fullmatch(part_number):
        codes.append("ORDERABLE_PART_NUMBER_INVALID")
    return codes


def _anchor_codes(candidate: dict, anchors: Any) -> list[str]:
    if not isinstance(anchors, dict):
        return [
            "TRUSTED_MANIFEST_MISSING",
            "TRUSTED_RIGHTS_ANCHOR_MISSING",
            "APPROVED_BOM_ANCHOR_MISSING",
        ]
    codes: list[str] = []
    manifest = anchors.get("manifest")
    rights = anchors.get("rights")
    bom = anchors.get("bom")
    if not isinstance(manifest, dict):
        codes.append("TRUSTED_MANIFEST_MISSING")
    elif (
        manifest.get("record_id") != candidate.get("record_id")
        or manifest.get("official_locator") != candidate.get("official_locator")
        or manifest.get("content_sha256") != candidate.get("content_sha256")
        or manifest.get("captured_at") != candidate.get("captured_at")
        or manifest.get("last_modified") != candidate.get("last_modified")
        or manifest.get("source_revision") != candidate.get("source_revision")
        or not _is_text(manifest.get("manifest_id"))
    ):
        codes.append("TRUSTED_MANIFEST_MISMATCH")
    if not isinstance(rights, dict):
        codes.append("TRUSTED_RIGHTS_ANCHOR_MISSING")
    else:
        allowed_actions = rights.get("allowed_actions")
        valid_actions = (
            isinstance(allowed_actions, list)
            and all(isinstance(action, str) for action in allowed_actions)
            and set(allowed_actions) == REQUIRED_ACTIONS
        )
        if (
            rights.get("record_id") != candidate.get("record_id")
            or not valid_actions
            or rights.get("status") != "ACTIVE"
            or not _is_text(rights.get("anchor_id"))
        ):
            codes.append("TRUSTED_RIGHTS_ANCHOR_MISMATCH")
    identity = candidate.get("part_identity") if isinstance(candidate.get("part_identity"), dict) else {}
    if not isinstance(bom, dict):
        codes.append("APPROVED_BOM_ANCHOR_MISSING")
    elif (
        bom.get("manufacturer") != identity.get("manufacturer")
        or bom.get("orderable_part_number") != identity.get("orderable_part_number")
        or bom.get("approval_status") != "APPROVED"
        or not _is_text(bom.get("anchor_id"))
    ):
        codes.append("APPROVED_BOM_ANCHOR_MISMATCH")
    return codes


def evaluate_nasa_snapshot(
    candidate: Any,
    content_bytes: Any,
    *,
    trusted_anchors: Any = None,
    now: datetime | None = None,
) -> dict:
    """Return a deterministic review receipt for caller-supplied snapshot bytes."""

    codes: list[str] = []
    if not isinstance(candidate, dict):
        codes.append("CANDIDATE_SHAPE_INVALID")
        candidate = {}
    forbidden = sorted(set(candidate).intersection(FORBIDDEN_APPROVAL_KEYS))
    if forbidden:
        codes.append("SELF_DECLARED_APPROVAL_REJECTED")
    if set(candidate).difference(FORBIDDEN_APPROVAL_KEYS) != EXPECTED_CANDIDATE_KEYS:
        codes.append("CANDIDATE_SHAPE_INVALID")

    snapshot_class = candidate.get("snapshot_class")
    if snapshot_class not in {"SYNTHETIC_CONTROL", "ACTUAL_CANDIDATE"}:
        codes.append("SNAPSHOT_CLASS_INVALID")
    if candidate.get("provider") != "NASA":
        codes.append("PROVIDER_NOT_NASA")
    record_id = candidate.get("record_id")
    if not isinstance(record_id, str) or not RECORD_ID.fullmatch(record_id):
        codes.append("STABLE_RECORD_ID_INVALID")
    codes.extend(_locator_codes(candidate.get("official_locator"), candidate.get("redirect_chain")))

    captured = _parse_time(candidate.get("captured_at"), "CAPTURED_AT_INVALID", codes)
    modified = _parse_time(candidate.get("last_modified"), "LAST_MODIFIED_INVALID", codes)
    observed_now = now or datetime.now(timezone.utc)
    if observed_now.tzinfo is None or observed_now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    observed_now = observed_now.astimezone(timezone.utc)
    if captured is not None:
        if captured > observed_now + MAX_CLOCK_SKEW:
            codes.append("SNAPSHOT_TIME_IN_FUTURE")
        elif observed_now - captured > MAX_SNAPSHOT_AGE:
            codes.append("SNAPSHOT_STALE")
    if modified is not None and captured is not None and modified > captured + MAX_CLOCK_SKEW:
        codes.append("LAST_MODIFIED_AFTER_CAPTURE")
    revision = candidate.get("source_revision")
    if not isinstance(revision, str) or not REVISION.fullmatch(revision):
        codes.append("SOURCE_REVISION_INVALID")

    declared_hash = candidate.get("content_sha256")
    if not isinstance(content_bytes, bytes):
        codes.append("SNAPSHOT_BYTES_INVALID")
    elif not isinstance(declared_hash, str) or not SHA256.fullmatch(declared_hash):
        codes.append("CONTENT_SHA256_INVALID")
    else:
        observed_hash = "sha256:" + hashlib.sha256(content_bytes).hexdigest()
        if observed_hash != declared_hash:
            codes.append("CONTENT_SHA256_MISMATCH")

    codes.extend(_rights_codes(candidate.get("rights"), snapshot_class))
    codes.extend(_part_codes(candidate.get("part_identity")))
    if candidate.get("claimed_decision") != "HOLD":
        codes.append("OPTIMISTIC_DECISION_REJECTED")
    if candidate.get("claimed_suitability") != "NOT_EVALUATED":
        codes.append("SUITABILITY_PROMOTION_REJECTED")

    if snapshot_class == "ACTUAL_CANDIDATE":
        codes.extend(_anchor_codes(candidate, trusted_anchors))

    stable_codes = sorted(set(codes))
    if snapshot_class == "SYNTHETIC_CONTROL" and not stable_codes:
        issuance_status = "SYNTHETIC_CONTROL"
        use_status = "NOT_FOR_DECISION"
    elif snapshot_class == "ACTUAL_CANDIDATE" and not stable_codes:
        issuance_status = "READY_FOR_REVIEW"
        use_status = "NOT_FOR_DECISION"
    else:
        issuance_status = "HOLD_NOT_ISSUED"
        use_status = "NOT_FOR_DECISION"
    return {
        "contract_version": CONTRACT_VERSION,
        "snapshot_class": snapshot_class if snapshot_class in {"SYNTHETIC_CONTROL", "ACTUAL_CANDIDATE"} else "NOT_EVALUATED",
        "record_id": record_id if isinstance(record_id, str) and RECORD_ID.fullmatch(record_id) else None,
        "issuance_status": issuance_status,
        "use_status": use_status,
        "processing_status": "VALID" if not stable_codes else "PROVENANCE_FAILURE",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "suitability": "NOT_EVALUATED",
        "stable_codes": stable_codes,
    }
