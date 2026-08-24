"""Product-facing exact-part Evidence Packet readiness assessment.

This module deliberately does not issue evidence, calculate radiation values, or
decide part suitability.  It converts a caller-supplied readiness projection
into a small, identity-free receipt.  All decision-bearing fields remain
fail-closed until a separate, authoritative integration accepts the packet.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_VERSION = "PARTS_READINESS_RECEIPT_1.0.0"
EVENT_TYPES = ("TID", "SEU", "SEL", "SEB", "SEGR")
DESTRUCTIVE_EVENTS = frozenset({"SEL", "SEB", "SEGR"})
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
SHA256_HEX_LENGTH = 64

_TOP_LEVEL_KEYS = frozenset(
    {
        "candidate_class",
        "bom_approval",
        "identity",
        "artifact_manifest",
        "rights",
        "events",
        "applicability",
        "review",
        "requested_outcome",
    }
)
_BOM_KEYS = frozenset(
    {
        "approval_status",
        "approval_id",
        "approval_version",
        "component_pointer",
        "target_hash",
        "history_anchor",
        "immutable",
    }
)
_IDENTITY_KEYS = frozenset(
    {
        "identity_status",
        "manufacturer",
        "orderable_part_number",
        "package",
        "grade",
        "process",
        "die",
        "lot",
    }
)
_ARTIFACT_KEYS = frozenset(
    {
        "manifest_id",
        "artifact_revision_id",
        "source_locator_id",
        "content_sha256",
        "observed_sha256",
    }
)
_RIGHT_KEYS = frozenset({"action", "status", "scope_hash", "inherited"})
_EVENT_KEYS = frozenset(
    {
        "event_type",
        "evidence_status",
        "source_event_type",
        "test_article_identity",
        "applicability_status",
        "zero_event_claim",
        "statistical_bound_present",
    }
)
_APPLICABILITY_KEYS = frozenset(
    {"status", "mission_context_bound", "review_anchor"}
)
_REVIEW_KEYS = frozenset(
    {
        "status",
        "history_anchor",
        "reviewed_projection_hash",
        "immutable",
    }
)
_OUTCOME_KEYS = frozenset(
    {"use_status", "engineering_gate", "assurance_decision", "suitability"}
)


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != SHA256_HEX_LENGTH:
        return False
    return all(character in "0123456789abcdef" for character in value)


def _as_object(value: Any, allowed: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if any(not isinstance(key, str) or key not in allowed for key in value):
        codes.add("INPUT_FIELD_FORBIDDEN")
    return value


def _required_texts(value: Mapping[str, Any], fields: tuple[str, ...]) -> bool:
    return all(_is_text(value.get(field)) for field in fields)


def _validate_bom(value: Any, actual: bool, codes: set[str]) -> None:
    bom = _as_object(value, _BOM_KEYS, codes)
    if not actual:
        return
    if bom.get("approval_status") != "APPROVED":
        codes.add("BOM_APPROVAL_MISSING")
    if not _required_texts(
        bom, ("approval_id", "approval_version", "component_pointer")
    ):
        codes.add("BOM_APPROVAL_IDENTITY_MISSING")
    if not _is_sha256(bom.get("target_hash")):
        codes.add("BOM_APPROVAL_TARGET_ANCHOR_MISSING")
    if not _is_sha256(bom.get("history_anchor")) or bom.get("immutable") is not True:
        codes.add("BOM_APPROVAL_HISTORY_INVALID")


def _validate_identity(value: Any, actual: bool, codes: set[str]) -> str:
    identity = _as_object(value, _IDENTITY_KEYS, codes)
    status = identity.get("identity_status")
    if status == "CONTRADICTED":
        codes.add("IDENTITY_CONTRADICTED")
        return "CONTRADICTED"
    if status == "FAMILY_ONLY":
        codes.add("FAMILY_ONLY_PART_REJECTED")
        return "FAMILY_ONLY"
    if not actual:
        return "PARTIAL_UNRESOLVED"
    if status != "EXACT_ORDERABLE":
        codes.add("EXACT_ORDERABLE_IDENTITY_MISSING")
        return "PARTIAL_UNRESOLVED"
    if not _required_texts(
        identity,
        (
            "manufacturer",
            "orderable_part_number",
            "package",
            "grade",
            "process",
            "die",
            "lot",
        ),
    ):
        codes.add("EXACT_IDENTITY_FIELD_MISSING")
        return "PARTIAL_UNRESOLVED"
    return "EXACT_MATCH"


def _validate_artifact(value: Any, actual: bool, codes: set[str]) -> None:
    artifact = _as_object(value, _ARTIFACT_KEYS, codes)
    if not actual:
        return
    if not _required_texts(
        artifact, ("manifest_id", "artifact_revision_id", "source_locator_id")
    ):
        codes.add("RAW_ARTIFACT_MANIFEST_MISSING")
    declared = artifact.get("content_sha256")
    observed = artifact.get("observed_sha256")
    if not _is_sha256(declared) or not _is_sha256(observed):
        codes.add("ARTIFACT_HASH_INVALID")
    elif declared != observed:
        codes.add("ARTIFACT_HASH_MISMATCH")


def _validate_rights(value: Any, actual: bool, codes: set[str]) -> None:
    if not isinstance(value, list):
        codes.add("INPUT_SHAPE_INVALID")
        if actual:
            codes.add("RIGHTS_MANIFEST_MISSING")
        return

    seen: set[str] = set()
    for raw_entry in value:
        entry = _as_object(raw_entry, _RIGHT_KEYS, codes)
        action = entry.get("action")
        if action not in RIGHTS_ACTIONS:
            codes.add("RIGHTS_ACTION_UNKNOWN")
            continue
        if action in seen:
            codes.add("RIGHTS_ACTION_DUPLICATE")
        seen.add(action)
        if not actual:
            continue
        if entry.get("inherited") is not False:
            codes.add("RIGHTS_INHERITANCE_FORBIDDEN")
        if entry.get("status") != "ALLOWED":
            codes.add(f"RIGHTS_{action}_UNRESOLVED")
        if not _is_sha256(entry.get("scope_hash")):
            codes.add(f"RIGHTS_{action}_SCOPE_INVALID")

    if actual:
        for action in RIGHTS_ACTIONS:
            if action not in seen:
                codes.add(f"RIGHTS_{action}_MISSING")


def _validate_events(value: Any, actual: bool, codes: set[str]) -> list[dict[str, str]]:
    coverage = [
        {"event_type": event_type, "status": "NOT_EVALUATED"}
        for event_type in EVENT_TYPES
    ]
    if not isinstance(value, list):
        codes.add("INPUT_SHAPE_INVALID")
        if actual:
            codes.update(f"{event_type}_EVIDENCE_MISSING" for event_type in EVENT_TYPES)
        return coverage

    by_type: dict[str, Mapping[str, Any]] = {}
    for raw_entry in value:
        entry = _as_object(raw_entry, _EVENT_KEYS, codes)
        event_type = entry.get("event_type")
        if event_type not in EVENT_TYPES:
            codes.add("EVENT_TYPE_UNKNOWN")
            continue
        if event_type in by_type:
            codes.add("EVENT_COVERAGE_DUPLICATE")
            continue
        by_type[event_type] = entry

    for output_entry in coverage:
        event_type = output_entry["event_type"]
        entry = by_type.get(event_type)
        if entry is None:
            if actual:
                codes.add(f"{event_type}_EVIDENCE_MISSING")
            continue

        status = entry.get("evidence_status")
        if status == "NOT_APPLICABLE" and entry.get("applicability_status") == "NOT_APPLICABLE":
            output_entry["status"] = "NOT_APPLICABLE"
            if actual:
                codes.add(f"{event_type}_COVERAGE_GAP")
            continue
        if not actual:
            continue
        if status != "EVIDENCE_PRESENT":
            codes.add(f"{event_type}_EVIDENCE_MISSING")
            continue
        if entry.get("source_event_type") != event_type:
            codes.add("EVIDENCE_TYPE_SUBSTITUTION")
            continue
        if entry.get("applicability_status") != "APPLICABLE":
            codes.add(f"{event_type}_APPLICABILITY_UNRESOLVED")
            continue
        if event_type in DESTRUCTIVE_EVENTS and entry.get("test_article_identity") != "EXACT_MATCH":
            codes.add(f"{event_type}_TEST_ARTICLE_IDENTITY_UNRESOLVED")
            continue
        if entry.get("zero_event_claim") is True:
            codes.add(f"{event_type}_ZERO_EVENT_IMMUNITY_UNSUPPORTED")
            if entry.get("statistical_bound_present") is not True:
                codes.add(f"{event_type}_STATISTICAL_BOUND_MISSING")
            continue
        output_entry["status"] = "EVIDENCE_PRESENT"

    return coverage


def _validate_applicability(value: Any, actual: bool, codes: set[str]) -> str:
    applicability = _as_object(value, _APPLICABILITY_KEYS, codes)
    if not actual:
        return "NOT_EVALUATED"
    status = applicability.get("status")
    if status not in {"APPLICABLE", "NOT_APPLICABLE"}:
        codes.add("MISSION_APPLICABILITY_NOT_EVALUATED")
        return "NOT_EVALUATED"
    if applicability.get("mission_context_bound") is not True or not _is_sha256(
        applicability.get("review_anchor")
    ):
        codes.add("MISSION_APPLICABILITY_ANCHOR_INVALID")
        return "NOT_EVALUATED"
    if status == "NOT_APPLICABLE":
        codes.add("MISSION_APPLICABILITY_REJECTED")
    return status


def _validate_review(value: Any, actual: bool, codes: set[str]) -> None:
    review = _as_object(value, _REVIEW_KEYS, codes)
    if not actual:
        return
    if review.get("status") != "APPROVED":
        codes.add("REVIEW_APPROVAL_MISSING")
    if (
        not _is_sha256(review.get("history_anchor"))
        or not _is_sha256(review.get("reviewed_projection_hash"))
        or review.get("immutable") is not True
    ):
        codes.add("REVIEW_HISTORY_INVALID")


def _validate_requested_outcome(value: Any, codes: set[str]) -> None:
    outcome = _as_object(value, _OUTCOME_KEYS, codes)
    required = {
        "use_status": "NOT_FOR_DECISION",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
    }
    for field, fail_closed_value in required.items():
        if outcome.get(field) != fail_closed_value:
            codes.add("OPTIMISTIC_OUTCOME_FORBIDDEN")


def assess_exact_part_readiness(payload: Any) -> dict[str, Any]:
    """Return an identity-free, fail-closed readiness receipt.

    ``READY_FOR_REVIEW`` only means the supplied projection is structurally
    complete enough for an independent reviewer.  It never means that evidence
    was issued, the part is suitable, or a decision is permitted.
    """

    codes: set[str] = set()
    projection = _as_object(payload, _TOP_LEVEL_KEYS, codes)
    candidate_class = projection.get("candidate_class")
    actual = candidate_class == "ACTUAL_CANDIDATE"
    synthetic = candidate_class == "SYNTHETIC_CONTROL"
    if not actual and not synthetic:
        codes.add("CANDIDATE_CLASS_INVALID")

    _validate_bom(projection.get("bom_approval"), actual, codes)
    identity_status = _validate_identity(projection.get("identity"), actual, codes)
    _validate_artifact(projection.get("artifact_manifest"), actual, codes)
    _validate_rights(projection.get("rights"), actual, codes)
    coverage = _validate_events(projection.get("events"), actual, codes)
    applicability_status = _validate_applicability(
        projection.get("applicability"), actual, codes
    )
    _validate_review(projection.get("review"), actual, codes)
    _validate_requested_outcome(projection.get("requested_outcome"), codes)

    if synthetic:
        codes.add("SYNTHETIC_ONLY")
        readiness_status = "SYNTHETIC_CONTROL"
    elif actual and not codes:
        readiness_status = "READY_FOR_REVIEW"
    else:
        readiness_status = "HOLD_NOT_ISSUED"

    if "INPUT_SHAPE_INVALID" in codes or "INPUT_FIELD_FORBIDDEN" in codes:
        processing_status = "INVALID_INPUT"
    elif any(
        code.startswith(("BOM_", "ARTIFACT_", "RAW_ARTIFACT_", "RIGHTS_", "REVIEW_"))
        for code in codes
    ):
        processing_status = "PROVENANCE_FAILURE"
    else:
        processing_status = "VALID"

    return {
        "contract_version": CONTRACT_VERSION,
        "candidate_class": candidate_class if actual or synthetic else "INVALID",
        "processing_status": processing_status,
        "readiness_status": readiness_status,
        "identity_status": identity_status,
        "applicability_status": applicability_status,
        "event_coverage": coverage,
        "blocker_codes": sorted(codes),
        "use_status": "NOT_FOR_DECISION",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an identity-free exact-part readiness receipt."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    receipt = assess_exact_part_readiness(payload)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "processing_status": receipt["processing_status"],
                "readiness_status": receipt["readiness_status"],
                "blocker_count": len(receipt["blocker_codes"]),
                "assurance_decision": receipt["assurance_decision"],
                "used_for_decision": receipt["used_for_decision"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
