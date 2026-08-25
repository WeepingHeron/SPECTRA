"""Classify review impact without duplicating radiation calculations or policy.

Every comparison leaf is bound to a caller-supplied source locator and digest.
The module only says which existing inputs, evidence, and rules need review.  It
does not calculate TID/SEU, decide that a new test must be run, or issue an
approval/suitability/assurance claim.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping


CONTRACT_VERSION = "REVIEW_IMPACT_1.0.0"
EVENTS = ("TID", "SEU", "SEL", "SEB", "SEGR")
IDENTITY_FIELDS = (
    "manufacturer",
    "orderable_part_number",
    "package",
    "process",
    "die",
    "lot",
)
MISSION_FIELDS = ("orbit_regime", "altitude_km", "inclination_deg")
SNAPSHOT_FIELDS = (
    *MISSION_FIELDS,
    "duration_days",
    "shielding_mm_al_equivalent",
    *IDENTITY_FIELDS,
    *EVENTS,
)
VALUE_FIELDS = frozenset({"value", "source_locator", "source_sha256"})
SNAPSHOT_KEYS = frozenset(
    {"mission_orbit_context", "duration_days", "shielding_mm_al_equivalent", "approved_component_identity", "event_coverage"}
)
OUTCOME_KEYS = frozenset(
    {"engineering_gate", "evaluation_status", "assurance_decision", "suitability", "used_for_decision"}
)
TOP_KEYS = frozenset(
    {"contract_version", "data_class", "baseline", "candidate", "requested_outcome"}
)

EVENT_REQUIREMENTS = {
    "TID": (
        "EXACT_PART_TID_TEST_EVIDENCE",
        "REVIEW_EVIDENCE_REQUIRED",
        "Locate and review exact-part TID evidence and its mission applicability; do not infer that a new test is required.",
    ),
    "SEU": (
        "EXACT_PART_SEU_CROSS_SECTION_OR_RATE_EVIDENCE",
        "REVIEW_EVIDENCE_REQUIRED",
        "Locate and review exact-part SEU evidence and its mission applicability; do not infer destructive-event coverage.",
    ),
    "SEL": (
        "EXACT_PART_SEL_TEST_EVIDENCE",
        "TEST_EVIDENCE_REQUIRED",
        "Provide applicable exact-part SEL test evidence for review; this receipt does not decide whether a new test must be run.",
    ),
    "SEB": (
        "EXACT_PART_SEB_TEST_EVIDENCE",
        "TEST_EVIDENCE_REQUIRED",
        "Provide applicable exact-part SEB test evidence for review; this receipt does not decide whether a new test must be run.",
    ),
    "SEGR": (
        "EXACT_PART_SEGR_TEST_EVIDENCE",
        "TEST_EVIDENCE_REQUIRED",
        "Provide applicable exact-part SEGR test evidence for review; this receipt does not decide whether a new test must be run.",
    ),
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def source_sha256(value: Any, source_locator: str) -> str:
    """Return the contract digest binding one value to its source locator."""

    return hashlib.sha256(
        _canonical_bytes({"source_locator": source_locator, "value": value})
    ).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _object(value: Any, keys: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if set(value) != keys:
        codes.add("INPUT_FIELD_FORBIDDEN_OR_MISSING")
    return value


def _field_pointer(field: str) -> str:
    if field in MISSION_FIELDS:
        return f"mission_orbit_context.{field}"
    if field in IDENTITY_FIELDS:
        return f"approved_component_identity.{field}"
    if field in EVENTS:
        return f"event_coverage.{field}"
    return field


def _flatten_snapshot(value: Any, side: str, codes: set[str], provenance: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    snapshot = _object(value, SNAPSHOT_KEYS, codes)
    groups = {
        "mission_orbit_context": (MISSION_FIELDS, snapshot.get("mission_orbit_context")),
        "approved_component_identity": (IDENTITY_FIELDS, snapshot.get("approved_component_identity")),
        "event_coverage": (EVENTS, snapshot.get("event_coverage")),
    }
    flattened: dict[str, dict[str, Any]] = {}
    for group, (fields, raw_group) in groups.items():
        group_object = _object(raw_group, frozenset(fields), codes)
        for field in fields:
            flattened[field] = _validate_leaf(
                group_object.get(field), side, f"{group}.{field}", codes, provenance
            )
    for field in ("duration_days", "shielding_mm_al_equivalent"):
        flattened[field] = _validate_leaf(
            snapshot.get(field), side, field, codes, provenance
        )
    return flattened


def _validate_leaf(
    value: Any,
    side: str,
    pointer: str,
    codes: set[str],
    provenance: list[dict[str, str]],
) -> dict[str, Any]:
    leaf = _object(value, VALUE_FIELDS, codes)
    locator = leaf.get("source_locator")
    digest = leaf.get("source_sha256")
    valid_locator = isinstance(locator, str) and bool(locator.strip())
    valid_digest = _is_sha256(digest)
    digest_matches = False
    if valid_locator and valid_digest and "value" in leaf:
        try:
            digest_matches = digest == source_sha256(leaf.get("value"), locator)
        except (TypeError, ValueError):
            digest_matches = False
    if not (valid_locator and valid_digest and digest_matches):
        codes.add("SOURCE_PROVENANCE_INVALID")
        provenance.append(
            {
                "side": side,
                "field_pointer": pointer,
                "source_locator": "UNAVAILABLE",
                "problem": "SOURCE_LOCATOR_OR_HASH_INVALID",
            }
        )
    return dict(leaf)


def _validate_values(snapshot: Mapping[str, dict[str, Any]], codes: set[str]) -> None:
    for field in ("altitude_km", "inclination_deg", "duration_days", "shielding_mm_al_equivalent"):
        value = snapshot.get(field, {}).get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            codes.add("FIELD_VALUE_INVALID")
    for field in ("orbit_regime", *IDENTITY_FIELDS):
        value = snapshot.get(field, {}).get("value")
        if not isinstance(value, str) or not value.strip():
            codes.add("FIELD_VALUE_INVALID")
    for event in EVENTS:
        if snapshot.get(event, {}).get("value") is not True and snapshot.get(event, {}).get("value") is not False:
            codes.add("FIELD_VALUE_INVALID")


def _validate_outcome(value: Any, codes: set[str]) -> None:
    outcome = _object(value, OUTCOME_KEYS, codes)
    required = {
        "engineering_gate": "NOT_EVALUATED",
        "evaluation_status": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    if any(outcome.get(field) != expected for field, expected in required.items()):
        codes.add("OPTIMISTIC_OUTCOME_FORBIDDEN")


def _change_record(field: str, baseline: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "field_pointer": _field_pointer(field),
        "baseline": {"value": baseline["value"], "source_locator": baseline["source_locator"]},
        "candidate": {"value": candidate["value"], "source_locator": candidate["source_locator"]},
    }


def classify_review_impact(payload: Any) -> dict[str, Any]:
    """Return a deterministic, synthetic-only, fail-closed review receipt."""

    codes: set[str] = set()
    provenance: list[dict[str, str]] = []
    top = _object(payload, TOP_KEYS, codes)
    if top.get("contract_version") != CONTRACT_VERSION:
        codes.add("CONTRACT_VERSION_UNSUPPORTED")
    if top.get("data_class") != "SYNTHETIC":
        codes.add("DATA_CLASS_FORBIDDEN")
    baseline = _flatten_snapshot(top.get("baseline"), "baseline", codes, provenance)
    candidate = _flatten_snapshot(top.get("candidate"), "candidate", codes, provenance)
    _validate_values(baseline, codes)
    _validate_values(candidate, codes)
    _validate_outcome(top.get("requested_outcome"), codes)

    if "SOURCE_PROVENANCE_INVALID" in codes:
        return _failed_receipt("PROVENANCE_FAILURE", codes, provenance)
    if codes:
        return _failed_receipt("INVALID_INPUT", codes, [])

    changed = [
        field for field in SNAPSHOT_FIELDS if baseline[field]["value"] != candidate[field]["value"]
    ]
    changed_fields = [_change_record(field, baseline[field], candidate[field]) for field in changed]
    affected_calculations: set[str] = set()
    invalidated_evidence: list[dict[str, str]] = []
    required_rechecks: set[str] = set()
    blocker_codes: set[str] = set()
    next_actions: list[dict[str, Any]] = []

    if any(field in MISSION_FIELDS for field in changed):
        required_rechecks.add("ENVIRONMENT_CONTRACT_REFRESH_REQUIRED")
        blocker_codes.add("ENVIRONMENT_CONTRACT_REFRESH_REQUIRED")
        next_actions.append(
            {
                "action_code": "REFRESH_ENVIRONMENT_CONTRACT",
                "scope": [f"mission_orbit_context.{field}" for field in MISSION_FIELDS if field in changed],
                "blocker_code": "ENVIRONMENT_CONTRACT_REFRESH_REQUIRED",
                "instruction": "Refresh the authoritative environment input contract; this module does not derive environment values from altitude or inclination.",
            }
        )
    if "duration_days" in changed:
        affected_calculations.update({"TID", "SEU"})
        required_rechecks.update({"TID_RECALCULATION_REQUIRED", "SEU_RECALCULATION_REQUIRED"})
        blocker_codes.add("RADIATION_RECALCULATION_REQUIRED")
        next_actions.append(
            {
                "action_code": "RERUN_EXISTING_TID_SEU_CALCULATIONS",
                "scope": ["duration_days"],
                "blocker_code": "RADIATION_RECALCULATION_REQUIRED",
                "instruction": "Re-run the authoritative existing TID and SEU calculation paths with the refreshed mission duration; no physics is calculated here.",
            }
        )
    if "shielding_mm_al_equivalent" in changed:
        affected_calculations.add("TID")
        required_rechecks.add("TID_RECALCULATION_REQUIRED")
        blocker_codes.add("RADIATION_RECALCULATION_REQUIRED")
        next_actions.append(
            {
                "action_code": "RERUN_EXISTING_TID_CALCULATION",
                "scope": ["shielding_mm_al_equivalent"],
                "blocker_code": "RADIATION_RECALCULATION_REQUIRED",
                "instruction": "Re-run the authoritative existing TID calculation path with the refreshed Al-equivalent shielding input; shielding is not an input to the current SEE calculation path.",
            }
        )
    identity_changed = any(field in IDENTITY_FIELDS for field in changed)
    if identity_changed:
        required_rechecks.update({"EXACT_PART_IDENTITY_REVIEW_REQUIRED", "EVENT_COVERAGE_REVIEW_REQUIRED"})
        blocker_codes.add("EXACT_PART_EVIDENCE_REVIEW_REQUIRED")
        for event in EVENTS:
            invalidated_evidence.append(
                {"event": event, "evidence": EVENT_REQUIREMENTS[event][0], "reason": "APPROVED_COMPONENT_IDENTITY_CHANGED"}
            )
        next_actions.append(
            {
                "action_code": "REVIEW_EXACT_PART_EVIDENCE",
                "scope": [f"approved_component_identity.{field}" for field in IDENTITY_FIELDS if field in changed],
                "events": list(EVENTS),
                "blocker_code": "EXACT_PART_EVIDENCE_REVIEW_REQUIRED",
                "instruction": "Re-bind exact-part evidence and event coverage to the candidate manufacturer, orderable PN, package, process, die, and lot identity.",
            }
        )

    evidence_gaps: list[dict[str, Any]] = []
    for event in EVENTS:
        if candidate[event]["value"] is False:
            evidence, action_code, instruction = EVENT_REQUIREMENTS[event]
            blocker = f"EVENT_COVERAGE_MISSING_{event}"
            blocker_codes.add(blocker)
            required_rechecks.add(action_code)
            gap = {
                "event": event,
                "field_pointer": f"event_coverage.{event}",
                "source_locator": candidate[event]["source_locator"],
                "required_evidence": evidence,
                "requirement_code": action_code,
                "blocker_code": blocker,
            }
            evidence_gaps.append(gap)
            next_actions.append(
                {
                    "action_code": action_code,
                    "scope": {"event": event, "condition": "candidate exact-part mission applicability"},
                    "blocker_code": blocker,
                    "instruction": instruction,
                }
            )

    body = {
        "contract_version": CONTRACT_VERSION,
        "data_class": "SYNTHETIC",
        "processing_status": "VALID",
        "impact_status": "REVIEW_REQUIRED" if blocker_codes else "NO_REVIEW_IMPACT_DETECTED",
        "changed_fields": changed_fields,
        "affected_calculations": sorted(affected_calculations),
        "invalidated_evidence": invalidated_evidence,
        "required_rechecks": sorted(required_rechecks),
        "evidence_gaps": evidence_gaps,
        "blocker_codes": sorted(blocker_codes),
        "next_actions": next_actions,
        "error_codes": [],
        "engineering_gate": "NOT_EVALUATED",
        "evaluation_status": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    return _with_hash(body)


def _failed_receipt(
    processing_status: str, codes: set[str], problem_locations: list[dict[str, str]]
) -> dict[str, Any]:
    body = {
        "contract_version": CONTRACT_VERSION,
        "data_class": "SYNTHETIC",
        "processing_status": processing_status,
        "impact_status": "DATA_UNAVAILABLE",
        "changed_fields": [],
        "affected_calculations": [],
        "invalidated_evidence": [],
        "required_rechecks": ["SOURCE_INTEGRITY_REVIEW_REQUIRED"] if problem_locations else [],
        "evidence_gaps": [],
        "blocker_codes": ["SOURCE_PROVENANCE_INVALID"] if problem_locations else [],
        "next_actions": ([{
            "action_code": "REPAIR_SOURCE_BINDING",
            "scope": [item["field_pointer"] for item in problem_locations],
            "blocker_code": "SOURCE_PROVENANCE_INVALID",
            "instruction": "Restore a non-empty source locator and matching value-to-locator SHA-256 before comparing or trusting any affected value.",
        }] if problem_locations else []),
        "problem_locations": problem_locations,
        "error_codes": sorted(codes),
        "engineering_gate": "NOT_EVALUATED",
        "evaluation_status": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    return _with_hash(body)


def _with_hash(body: Mapping[str, Any]) -> dict[str, Any]:
    receipt = dict(body)
    receipt["receipt_sha256"] = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    return receipt
