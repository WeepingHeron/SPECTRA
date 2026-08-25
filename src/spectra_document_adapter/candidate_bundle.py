"""Cross-check three document candidate receipts without promoting evidence."""

from __future__ import annotations

from typing import Any, Mapping


CONTRACT_VERSION = "THREE_DOCUMENT_CANDIDATE_BUNDLE_1.0.0"
ROLES = ("MISSION_CONDITIONS", "PART_SPEC", "RADIATION_TEST")
MISSION_FIELDS = frozenset(
    {
        "MISSION_NAME",
        "ORBIT_REGIME",
        "ORBIT_ALTITUDE",
        "ORBIT_INCLINATION",
        "MISSION_DURATION",
        "SHIELDING_THICKNESS",
    }
)


def _values(receipt: Mapping[str, Any], field: str) -> list[str]:
    values = {
        str(item.get("value", "")).strip()
        for item in receipt.get("candidates", [])
        if isinstance(item, Mapping) and item.get("field") == field
    }
    return sorted(item for item in values if item)


def _identity_result(
    part: Mapping[str, Any], test: Mapping[str, Any], field: str
) -> dict[str, Any]:
    part_values = _values(part, field)
    test_values = _values(test, field)
    if len(part_values) > 1 or len(test_values) > 1:
        status = "AMBIGUOUS"
        code = f"{field}_CANDIDATE_AMBIGUOUS"
    elif not part_values or not test_values:
        status = "MISSING"
        code = f"{field}_CANDIDATE_MISSING"
    elif part_values[0].casefold() == test_values[0].casefold():
        status = "EXACT_TEXT_MATCH"
        code = f"{field}_EXACT_TEXT_MATCH"
    else:
        status = "CONFLICT"
        code = f"{field}_CONFLICT"
    return {
        "field": field,
        "status": status,
        "stable_code": code,
        "part_candidates": part_values,
        "test_candidates": test_values,
    }


def evaluate_candidate_bundle(receipts: Any) -> dict[str, Any]:
    """Evaluate explicit mission, part and radiation-test document roles."""

    if not isinstance(receipts, Mapping) or set(receipts) != set(ROLES):
        return {
            "contract_version": CONTRACT_VERSION,
            "processing_status": "INVALID_INPUT",
            "bundle_status": "DOCUMENT_ROLE_SET_INVALID",
            "questions": {},
            "validated_check_count": 0,
            "failed_check_count": 0,
            "not_evaluated_check_count": 3,
            "approval_status": "NOT_EVALUATED",
            "use_status": "NOT_FOR_DECISION",
            "assurance_decision": "HOLD",
            "used_for_decision": False,
        }

    typed = {role: receipts[role] if isinstance(receipts[role], Mapping) else {} for role in ROLES}
    intake_rows = [
        {
            "role": role,
            "processing_status": typed[role].get("processing_status", "INVALID_INPUT"),
            "content_sha256": typed[role].get("source", {}).get("content_sha256"),
            "candidate_count": typed[role].get("candidate_count", 0),
        }
        for role in ROLES
    ]
    intake_ok = all(item["processing_status"] == "VALID" for item in intake_rows)
    mission = typed["MISSION_CONDITIONS"]
    part = typed["PART_SPEC"]
    test = typed["RADIATION_TEST"]
    mission_present = sorted(MISSION_FIELDS.intersection(mission.get("candidate_fields", [])))
    mission_required = ["MISSION_DURATION", "ORBIT_CONTEXT"]
    mission_missing = []
    if "MISSION_DURATION" not in mission_present:
        mission_missing.append("MISSION_DURATION")
    if not set(mission_present).intersection(
        {"ORBIT_REGIME", "ORBIT_ALTITUDE", "ORBIT_INCLINATION"}
    ):
        mission_missing.append("ORBIT_CONTEXT")

    identity_rows = [
        _identity_result(part, test, "ORDERABLE_PART_NUMBER"),
        _identity_result(part, test, "MANUFACTURER"),
    ]
    identity_statuses = {item["status"] for item in identity_rows}
    if "CONFLICT" in identity_statuses:
        identity_status = "CONFLICT"
    elif "AMBIGUOUS" in identity_statuses:
        identity_status = "AMBIGUOUS"
    elif "MISSING" in identity_statuses:
        identity_status = "MISSING"
    else:
        identity_status = "EXACT_TEXT_MATCH"

    linkage = test.get("evidence_candidate_linkage", {})
    event_groups = linkage.get("event_groups", []) if isinstance(linkage, Mapping) else []
    complete_events = [
        item.get("event_type")
        for item in event_groups
        if isinstance(item, Mapping) and item.get("status") == "REQUIRED_FIELDS_PRESENT"
    ]
    incomplete_events = [
        item.get("event_type")
        for item in event_groups
        if isinstance(item, Mapping) and item.get("status") != "REQUIRED_FIELDS_PRESENT"
    ]
    if not event_groups:
        event_status = "MISSING"
    elif incomplete_events:
        event_status = "PARTIAL"
    else:
        event_status = "CANDIDATES_READY_FOR_REVIEW"

    validated = len(mission_present) + sum(
        item["status"] == "EXACT_TEXT_MATCH" for item in identity_rows
    ) + len(complete_events)
    failed = sum(item["status"] in {"CONFLICT", "AMBIGUOUS"} for item in identity_rows)
    missing = len(mission_missing) + sum(
        item["status"] == "MISSING" for item in identity_rows
    ) + len(incomplete_events) + (0 if event_groups else 1)
    if not intake_ok:
        bundle_status = "DOCUMENT_INTAKE_BLOCKED"
    elif failed:
        bundle_status = "CANDIDATE_CONFLICT"
    elif missing:
        bundle_status = "PARTIAL_CANDIDATE_LINK"
    else:
        bundle_status = "CANDIDATES_LINKED_FOR_REVIEW"

    return {
        "contract_version": CONTRACT_VERSION,
        "processing_status": "VALID" if intake_ok else "DATA_UNAVAILABLE",
        "bundle_status": bundle_status,
        "document_receipts": intake_rows,
        "questions": {
            "document_intake": {
                "status": "COMPLETE" if intake_ok else "BLOCKED",
                "documents": intake_rows,
            },
            "mission_context": {
                "status": "CANDIDATES_PRESENT" if not mission_missing else "MISSING",
                "required_fields": mission_required,
                "present_fields": mission_present,
                "missing_fields": mission_missing,
            },
            "part_test_identity": {
                "status": identity_status,
                "fields": identity_rows,
            },
            "event_evidence_candidates": {
                "status": event_status,
                "complete_events": complete_events,
                "incomplete_events": incomplete_events,
                "event_groups": event_groups,
            },
            "mission_test_applicability": {
                "status": "NOT_EVALUATED",
                "stable_code": "APPROVED_MISSION_EVIDENCE_BINDING_MISSING",
            },
        },
        "validated_check_count": validated,
        "failed_check_count": failed,
        "not_evaluated_check_count": missing + 1,
        "approval_status": "NOT_EVALUATED",
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "next_gate": "APPROVED_MANIFEST_RIGHTS_AND_MISSION_CASE_BINDING",
    }
