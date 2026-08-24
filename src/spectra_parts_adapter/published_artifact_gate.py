"""Validate caller-supplied published source bytes and license metadata.

This gate binds a reference artifact to an allowlisted repository record,
content identity, and a reviewed CC BY 4.0 action scope.  Passing it makes the
artifact reviewable as a published reference only; it never makes the tested
part identity exact or the evidence decision-eligible.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping
from urllib.parse import urlsplit


CONTRACT_VERSION = "PUBLISHED_ARTIFACT_GATE_1.0.0"
EXPECTED_DOI = "10.22029/jlupub-19623"
EXPECTED_LICENSE = "CC-BY-4.0"
EXPECTED_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
EXPECTED_PROVIDER = "JLUpub"
EXPECTED_HOST = "jlupub.ub.uni-giessen.de"
EXPECTED_RECORD_URL = (
    "https://jlupub.ub.uni-giessen.de/items/"
    "bacfbfc4-a5e7-46b1-b2a0-332d8231cc49"
)
EXPECTED_ARTIFACT_URL = (
    "https://jlupub.ub.uni-giessen.de/server/api/core/bitstreams/"
    "ecc83730-096d-4083-94a1-bff6adf67f68/content"
)
REVIEWED_ARTIFACT_SIZE = 33_130_232
REVIEWED_ARTIFACT_SHA256 = (
    "a6cee9eb8eaca8dab8636caf0ad4cd4248fbfccfab57c9ce9af2c7324969f373"
)
REQUIRED_ACTIONS = frozenset(
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
REQUIRED_CONDITIONS = frozenset(
    {
        "ATTRIBUTION_REQUIRED",
        "LICENSE_NOTICE_REQUIRED",
        "CHANGE_NOTICE_REQUIRED_IF_MODIFIED",
        "NO_ENDORSEMENT",
    }
)

_CANDIDATE_KEYS = frozenset(
    {
        "contract_version",
        "source_class",
        "provider",
        "record_id",
        "doi",
        "official_record_url",
        "artifact_url",
        "file_name",
        "observed_at",
        "byte_size",
        "content_sha256",
        "license",
        "attribution",
        "rights",
        "claimed_use_status",
        "claimed_decision",
    }
)
_LICENSE_KEYS = frozenset({"id", "canonical_url", "declared_on_record"})
_ATTRIBUTION_KEYS = frozenset(
    {"title", "creator", "source_url", "license_url", "modified"}
)
_RIGHTS_KEYS = frozenset({"action_grants", "conditions", "scope_note"})
_GRANT_KEYS = frozenset({"action", "status", "basis"})
_ANCHOR_KEYS = frozenset({"manifest", "rights_review"})
_MANIFEST_ANCHOR_KEYS = frozenset(
    {
        "anchor_id",
        "record_id",
        "doi",
        "official_record_url",
        "artifact_url",
        "byte_size",
        "content_sha256",
        "license_id",
    }
)
_RIGHTS_ANCHOR_KEYS = frozenset(
    {
        "anchor_id",
        "record_id",
        "license_id",
        "license_url",
        "allowed_actions",
        "required_conditions",
        "status",
    }
)


def _text(value: Any, limit: int = 500) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= limit
        and "\x00" not in value
    )


def _sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _object(
    value: Any, allowed: frozenset[str], codes: set[str]
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if any(not isinstance(key, str) or key not in allowed for key in value):
        codes.add("INPUT_FIELD_FORBIDDEN")
    return value


def _official_url(value: Any, *, artifact: bool = False) -> bool:
    if not _text(value):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme != "https"
        or host != EXPECTED_HOST
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or bool(parsed.fragment)
    ):
        return False
    if artifact:
        return parsed.path.startswith("/server/api/core/bitstreams/")
    return parsed.path.startswith("/items/")


def _license_codes(candidate: Mapping[str, Any], codes: set[str]) -> None:
    license_value = _object(candidate.get("license"), _LICENSE_KEYS, codes)
    if (
        license_value.get("id") != EXPECTED_LICENSE
        or license_value.get("canonical_url") != EXPECTED_LICENSE_URL
        or license_value.get("declared_on_record") is not True
    ):
        codes.add("LICENSE_BINDING_INVALID")

    attribution = _object(
        candidate.get("attribution"), _ATTRIBUTION_KEYS, codes
    )
    if not all(
        _text(attribution.get(field))
        for field in ("title", "creator", "source_url", "license_url")
    ):
        codes.add("ATTRIBUTION_INCOMPLETE")
    elif (
        attribution.get("source_url") != candidate.get("official_record_url")
        or attribution.get("license_url") != EXPECTED_LICENSE_URL
    ):
        codes.add("ATTRIBUTION_BINDING_MISMATCH")
    if attribution.get("modified") is not False:
        codes.add("MODIFICATION_NOTICE_INVALID")


def _rights_codes(
    candidate: Mapping[str, Any], source_class: Any, codes: set[str]
) -> None:
    rights = _object(candidate.get("rights"), _RIGHTS_KEYS, codes)
    grants = rights.get("action_grants")
    if not isinstance(grants, list):
        codes.add("ACTION_RIGHTS_INVALID")
        grants = []
    seen: set[str] = set()
    expected_basis = (
        "SYNTHETIC_CONTROL_ONLY"
        if source_class == "SYNTHETIC_CONTROL"
        else "CC_BY_4_0_RECORD"
    )
    for raw_grant in grants:
        grant = _object(raw_grant, _GRANT_KEYS, codes)
        action = grant.get("action")
        if (
            not isinstance(action, str)
            or action not in REQUIRED_ACTIONS
            or action in seen
        ):
            codes.add("ACTION_RIGHTS_INVALID")
            continue
        seen.add(action)
        if (
            grant.get("status") != "ALLOWED_WITH_CONDITIONS"
            or grant.get("basis") != expected_basis
        ):
            codes.add("ACTION_RIGHT_NOT_ACTIVE")
    if seen != REQUIRED_ACTIONS:
        codes.add("ACTION_RIGHTS_INCOMPLETE")
    conditions = rights.get("conditions")
    if (
        not isinstance(conditions, list)
        or any(not isinstance(item, str) for item in conditions)
        or set(conditions) != REQUIRED_CONDITIONS
    ):
        codes.add("LICENSE_CONDITIONS_INCOMPLETE")
    if not _text(rights.get("scope_note")):
        codes.add("RIGHTS_SCOPE_NOTE_MISSING")


def _anchor_codes(
    candidate: Mapping[str, Any], trusted_anchors: Any, codes: set[str]
) -> None:
    anchors = _object(trusted_anchors, _ANCHOR_KEYS, codes)
    manifest = _object(
        anchors.get("manifest"), _MANIFEST_ANCHOR_KEYS, codes
    )
    manifest_pairs = (
        ("record_id", candidate.get("record_id")),
        ("doi", candidate.get("doi")),
        ("official_record_url", candidate.get("official_record_url")),
        ("artifact_url", candidate.get("artifact_url")),
        ("byte_size", candidate.get("byte_size")),
        ("content_sha256", candidate.get("content_sha256")),
        ("license_id", EXPECTED_LICENSE),
    )
    if not _text(manifest.get("anchor_id")) or any(
        manifest.get(key) != expected for key, expected in manifest_pairs
    ):
        codes.add("TRUSTED_MANIFEST_MISMATCH")

    rights = _object(
        anchors.get("rights_review"), _RIGHTS_ANCHOR_KEYS, codes
    )
    actions = rights.get("allowed_actions")
    conditions = rights.get("required_conditions")
    valid_actions = (
        isinstance(actions, list)
        and all(isinstance(item, str) for item in actions)
        and set(actions) == REQUIRED_ACTIONS
    )
    valid_conditions = (
        isinstance(conditions, list)
        and all(isinstance(item, str) for item in conditions)
        and set(conditions) == REQUIRED_CONDITIONS
    )
    if (
        not _text(rights.get("anchor_id"))
        or rights.get("record_id") != candidate.get("record_id")
        or rights.get("license_id") != EXPECTED_LICENSE
        or rights.get("license_url") != EXPECTED_LICENSE_URL
        or rights.get("status") != "REVIEWED_WITH_CONDITIONS"
        or not valid_actions
        or not valid_conditions
    ):
        codes.add("TRUSTED_RIGHTS_REVIEW_MISMATCH")


def evaluate_published_artifact(
    candidate: Any,
    content_bytes: Any,
    *,
    trusted_anchors: Any = None,
) -> dict[str, Any]:
    """Return an identity-free, fail-closed published-reference receipt."""

    codes: set[str] = set()
    value = _object(candidate, _CANDIDATE_KEYS, codes)
    if value.get("contract_version") != CONTRACT_VERSION:
        codes.add("CONTRACT_VERSION_UNSUPPORTED")
    source_class = value.get("source_class")
    if source_class not in {"PUBLISHED_ACTUAL", "SYNTHETIC_CONTROL"}:
        codes.add("SOURCE_CLASS_INVALID")
    if value.get("provider") != EXPECTED_PROVIDER:
        codes.add("PROVIDER_NOT_ALLOWLISTED")
    if value.get("doi") != EXPECTED_DOI or value.get("record_id") != EXPECTED_DOI:
        codes.add("SOURCE_RECORD_IDENTITY_MISMATCH")
    if not _official_url(value.get("official_record_url")):
        codes.add("OFFICIAL_RECORD_URL_INVALID")
    if not _official_url(value.get("artifact_url"), artifact=True):
        codes.add("ARTIFACT_URL_INVALID")
    if (
        value.get("official_record_url") != EXPECTED_RECORD_URL
        or value.get("artifact_url") != EXPECTED_ARTIFACT_URL
    ):
        codes.add("SOURCE_LOCATOR_IDENTITY_MISMATCH")
    if not _text(value.get("file_name")) or not _text(value.get("observed_at"), 64):
        codes.add("SOURCE_METADATA_INCOMPLETE")

    if not isinstance(content_bytes, bytes):
        codes.add("CONTENT_BYTES_INVALID")
        observed_size = None
        observed_hash = None
    else:
        observed_size = len(content_bytes)
        observed_hash = hashlib.sha256(content_bytes).hexdigest()
    declared_size = value.get("byte_size")
    if (
        not isinstance(declared_size, int)
        or isinstance(declared_size, bool)
        or declared_size <= 0
        or declared_size != observed_size
    ):
        codes.add("CONTENT_SIZE_MISMATCH")
    declared_hash = value.get("content_sha256")
    if not _sha256(declared_hash) or declared_hash != observed_hash:
        codes.add("CONTENT_SHA256_MISMATCH")
    if source_class == "PUBLISHED_ACTUAL" and (
        declared_size != REVIEWED_ARTIFACT_SIZE
        or declared_hash != REVIEWED_ARTIFACT_SHA256
    ):
        codes.add("REVIEWED_ARTIFACT_IDENTITY_MISMATCH")

    _license_codes(value, codes)
    _rights_codes(value, source_class, codes)
    _anchor_codes(value, trusted_anchors, codes)
    if (
        value.get("claimed_use_status") != "NOT_FOR_DECISION"
        or value.get("claimed_decision") != "HOLD"
    ):
        codes.add("OPTIMISTIC_USE_REJECTED")

    processing_status = "VALID" if not codes else "INVALID_INPUT"
    if codes:
        issuance_status = "HOLD_NOT_ISSUED"
    elif source_class == "SYNTHETIC_CONTROL":
        issuance_status = "SYNTHETIC_CONTROL"
    else:
        issuance_status = "READY_FOR_REFERENCE_REVIEW"

    return {
        "contract_version": CONTRACT_VERSION,
        "processing_status": processing_status,
        "issuance_status": issuance_status,
        "source_artifact_status": (
            "BYTES_AND_LICENSE_SCOPE_BOUND" if not codes else "NOT_BOUND"
        ),
        "rights_status": (
            "LICENSE_SCOPE_CONFIRMED_WITH_CONDITIONS"
            if not codes
            else "NOT_EVALUATED"
        ),
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "artifact_binding": (
            {
                "record_id": value.get("record_id"),
                "content_sha256": declared_hash,
                "byte_size": declared_size,
            }
            if not codes
            else None
        ),
        "limitations": [
            "NON_COPYRIGHT_RIGHTS_NOT_ASSESSED",
            "SCIENTIFIC_ACCURACY_NOT_ESTABLISHED",
            "EXACT_PART_IDENTITY_NOT_ESTABLISHED",
        ],
        "stable_codes": sorted(codes),
    }
