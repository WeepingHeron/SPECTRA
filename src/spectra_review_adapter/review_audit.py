"""Create a deterministic, identity-free audit receipt for a review action.

The adapter records a bounded human-review event.  It does not authenticate a
reviewer, approve evidence, execute prompt-like content, or make a part or
assurance decision.  Caller-supplied subject anchors are used only to reject
self-review and are never copied into the receipt.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping


CONTRACT_VERSION = "REVIEW_AUDIT_RECEIPT_1.0.0"
GENESIS = "GENESIS"
SHA256_LENGTH = 64
ALLOWED_ACTIONS = frozenset(
    {"REQUEST_EVIDENCE", "EXCLUDE_CANDIDATE", "RECORD_REVIEW"}
)
ALLOWED_REVIEWER_ROLES = frozenset(
    {"EVIDENCE_REVIEWER", "INDEPENDENT_REVIEWER"}
)
ACTION_REASON_CODES = {
    "REQUEST_EVIDENCE": frozenset(
        {"EVIDENCE_GAP_UNRESOLVED", "PROVENANCE_GAP_UNRESOLVED"}
    ),
    "EXCLUDE_CANDIDATE": frozenset(
        {"CANDIDATE_NOT_DECISION_ELIGIBLE", "CANDIDATE_CONFLICT_UNRESOLVED"}
    ),
    "RECORD_REVIEW": frozenset(
        {"REVIEW_OBSERVATION_RECORDED", "REVIEW_BOUNDARY_RECORDED"}
    ),
}
INPUT_KEYS = frozenset(
    {
        "candidate_content_sha256",
        "reviewer_action",
        "review_reason_code",
        "reviewer_role",
        "reviewer_subject_sha256",
        "candidate_author_subject_sha256",
        "sequence",
        "prior_receipt_sha256",
        "recorded_at",
    }
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _canonical_timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or not value or len(value) > 64:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    utc = parsed.astimezone(timezone.utc)
    if utc.microsecond:
        return utc.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return utc.isoformat(timespec="seconds").replace("+00:00", "Z")


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _receipt_body(
    *,
    processing_status: str,
    review_status: str,
    candidate_content_sha256: str,
    reviewer_action: str,
    review_reason_code: str,
    reviewer_role: str,
    sequence: int,
    prior_receipt_sha256: str,
    recorded_at: str,
    error_codes: list[str],
) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "processing_status": processing_status,
        "review_status": review_status,
        "candidate_content_sha256": candidate_content_sha256,
        "reviewer_action": reviewer_action,
        "review_reason_code": review_reason_code,
        "reviewer_role": reviewer_role,
        "sequence": sequence,
        "prior_receipt_sha256": prior_receipt_sha256,
        "recorded_at": recorded_at,
        "error_codes": error_codes,
        "use_status": "NOT_FOR_DECISION",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }


def record_review_action(payload: Any) -> dict[str, Any]:
    """Return a deterministic audit receipt for one bounded review action.

    ``REVIEW_RECORDED`` confirms only that a structurally valid action was
    bound to the supplied candidate hash and chain position.  Authentication,
    approval, suitability, PASS, and decision use remain outside this adapter.
    """

    errors: set[str] = set()
    if not isinstance(payload, Mapping):
        projection: Mapping[str, Any] = {}
        errors.add("INPUT_SHAPE_INVALID")
    else:
        projection = payload
        if set(projection) != INPUT_KEYS:
            errors.add("INPUT_FIELD_FORBIDDEN")

    candidate_hash = projection.get("candidate_content_sha256")
    if not _is_sha256(candidate_hash):
        errors.add("CANDIDATE_CONTENT_HASH_INVALID")

    action = projection.get("reviewer_action")
    if not isinstance(action, str) or action not in ALLOWED_ACTIONS:
        errors.add("REVIEW_ACTION_NOT_ALLOWED")

    reason_code = projection.get("review_reason_code")
    if (
        isinstance(action, str)
        and action in ALLOWED_ACTIONS
        and (
            not isinstance(reason_code, str)
            or reason_code not in ACTION_REASON_CODES[action]
        )
    ):
        errors.add("REVIEW_REASON_NOT_ALLOWED")

    reviewer_role = projection.get("reviewer_role")
    if not isinstance(reviewer_role, str) or reviewer_role not in ALLOWED_REVIEWER_ROLES:
        errors.add("REVIEWER_ROLE_NOT_ALLOWED")

    reviewer_subject = projection.get("reviewer_subject_sha256")
    candidate_author_subject = projection.get("candidate_author_subject_sha256")
    if not _is_sha256(reviewer_subject) or not _is_sha256(candidate_author_subject):
        errors.add("SUBJECT_ANCHOR_INVALID")
    elif reviewer_subject == candidate_author_subject:
        errors.add("SELF_REVIEW_FORBIDDEN")

    sequence = projection.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        errors.add("REVIEW_SEQUENCE_INVALID")

    prior_hash = projection.get("prior_receipt_sha256")
    if isinstance(sequence, int) and not isinstance(sequence, bool) and sequence >= 1:
        if sequence == 1 and prior_hash != GENESIS:
            errors.add("GENESIS_RECEIPT_REQUIRED")
        elif sequence > 1 and not _is_sha256(prior_hash):
            errors.add("PRIOR_RECEIPT_HASH_INVALID")
    elif prior_hash != GENESIS and not _is_sha256(prior_hash):
        errors.add("PRIOR_RECEIPT_HASH_INVALID")

    recorded_at = _canonical_timestamp(projection.get("recorded_at"))
    if recorded_at is None:
        errors.add("REVIEW_TIMESTAMP_INVALID")

    valid = not errors
    if valid:
        body = _receipt_body(
            processing_status="VALID",
            review_status="REVIEW_RECORDED",
            candidate_content_sha256=candidate_hash,
            reviewer_action=action,
            review_reason_code=reason_code,
            reviewer_role=reviewer_role,
            sequence=sequence,
            prior_receipt_sha256=prior_hash,
            recorded_at=recorded_at,
            error_codes=[],
        )
    else:
        chain_failure = any(
            code
            in {
                "GENESIS_RECEIPT_REQUIRED",
                "PRIOR_RECEIPT_HASH_INVALID",
                "SELF_REVIEW_FORBIDDEN",
            }
            for code in errors
        )
        body = _receipt_body(
            processing_status="PROVENANCE_FAILURE" if chain_failure else "INVALID_INPUT",
            review_status="REVIEW_REJECTED",
            candidate_content_sha256="UNAVAILABLE",
            reviewer_action="UNAVAILABLE",
            review_reason_code="UNAVAILABLE",
            reviewer_role="UNAVAILABLE",
            sequence=0,
            prior_receipt_sha256="UNAVAILABLE",
            recorded_at="UNAVAILABLE",
            error_codes=sorted(errors),
        )

    receipt = dict(body)
    receipt["receipt_sha256"] = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    return receipt
