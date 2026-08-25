"""Deterministic multi-document mission-case synthesis.

The synthesizer binds caller-structured document claims to one mission case.  It
does not parse documents, approve evidence, or infer missing radiation values.
TID and SEU calculations delegate to the existing synthetic simulation Core;
all assurance outcomes remain fail-closed.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping

from .engine import model_errors, sha256
from .see import calculate_see
from .tid import calculate_tid
from .units import tid_krad_si


CONTRACT_VERSION = "MISSION_CASE_1.0.0"
RESULT_VERSION = "MISSION_CASE_RESULT_1.0.0"
EVENT_TYPES = ("TID", "SEU", "SEL", "SEB", "SEGR")
DESTRUCTIVE_EVENTS = frozenset({"SEL", "SEB", "SEGR"})
IDENTITY_FIELDS = (
    "manufacturer",
    "orderable_part_number",
    "package",
    "process",
    "die",
    "lot",
)
UNSUPPORTED_CONDITIONS = ("species", "energy", "let", "fluence", "temperature", "bias")
_IDENTITY_KEYS = frozenset(IDENTITY_FIELDS)
_CONDITION_KEYS = frozenset(UNSUPPORTED_CONDITIONS)

_ROOT_KEYS = frozenset(
    {"contract_version", "mission_case_id", "data_class", "mission_conditions", "approved_bom_targets", "sources"}
)
_MISSION_KEYS = frozenset(
    {"mission_id", "duration", "environment_tid", "particle_flux", "shielding", "tid_design_factor", "analysis_device_count"}
)
_TARGET_KEYS = frozenset({"component_id", "approval_status", "identity"})
_SOURCE_KEYS = frozenset(
    {
        "source_id",
        "document_id",
        "mission_case_id",
        "data_class",
        "artifact_sha256",
        "observed_artifact_sha256",
        "locator",
        "claims",
    }
)
_CLAIM_KEYS = frozenset(
    {"claim_id", "component_id", "tested_identity", "test_conditions", "event_evidence"}
)
_EVENT_KEYS = frozenset(
    {"event_type", "source_event_type", "locator", "tid_test_limit", "cross_section"}
)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def _object(value: Any, allowed: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if any(not isinstance(key, str) or key not in allowed for key in value):
        codes.add("INPUT_FIELD_FORBIDDEN")
    return value


def _quantity_shape(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and isinstance(value.get("value"), (int, float))
        and not isinstance(value.get("value"), bool)
        and math.isfinite(value["value"])
        and _text(value.get("unit"))
    )


def _trace(source: Mapping[str, Any], claim: Mapping[str, Any] | None = None, event: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "source_id": source.get("source_id"),
        "document_id": source.get("document_id"),
        "artifact_sha256": source.get("artifact_sha256"),
        "observed_artifact_sha256": source.get("observed_artifact_sha256"),
        "source_locator": source.get("locator"),
        "data_class": source.get("data_class"),
    }
    if claim is not None:
        result["claim_id"] = claim.get("claim_id")
        result["component_id"] = claim.get("component_id")
    if event is not None:
        result["event_type"] = event.get("event_type")
        result["event_locator"] = event.get("locator")
    return result


def _question(status: str, codes: set[str], traces: list[dict[str, Any]], action_code: str, action: str) -> dict[str, Any]:
    return {
        "status": status,
        "blocker_codes": sorted(codes),
        "source_trace": traces,
        "next_action": {"action_code": action_code, "description": action},
    }


def _safe_input_hash(value: Any) -> str:
    try:
        return sha256(value)
    except (TypeError, ValueError):
        return "sha256:" + "0" * 64


def synthesize_mission_case(case: Any, model: Any) -> dict[str, Any]:
    """Synthesize source-local claims without merging or overwriting their values."""

    invalid: set[str] = set()
    blockers: set[str] = {"SYNTHETIC_OR_PUBLISHED_NOT_APPROVED_ASSURANCE"}
    root = _object(case, _ROOT_KEYS, invalid)
    mission_case_id = root.get("mission_case_id")
    if root.get("contract_version") != CONTRACT_VERSION:
        invalid.add("CONTRACT_VERSION_UNSUPPORTED")
    if not _text(mission_case_id):
        invalid.add("MISSION_CASE_ID_MISSING")
    if root.get("data_class") != "SYNTHETIC":
        invalid.add("MISSION_CASE_DATA_CLASS_INVALID")

    mission = _object(root.get("mission_conditions"), _MISSION_KEYS, invalid)
    required_quantities = ("duration", "environment_tid", "particle_flux", "shielding")
    if not _text(mission.get("mission_id")) or not all(_quantity_shape(mission.get(key)) for key in required_quantities):
        invalid.add("MISSION_CONDITIONS_INVALID")
    design_factor = mission.get("tid_design_factor")
    device_count = mission.get("analysis_device_count")
    if (
        not isinstance(design_factor, (int, float))
        or isinstance(design_factor, bool)
        or not math.isfinite(design_factor)
        or design_factor < 1
        or not isinstance(device_count, int)
        or isinstance(device_count, bool)
        or device_count < 1
    ):
        invalid.add("MISSION_CONDITIONS_INVALID")

    if model_errors(model):
        invalid.add("MODEL_CONFIG_INVALID")

    targets_raw = root.get("approved_bom_targets")
    sources_raw = root.get("sources")
    targets = targets_raw if isinstance(targets_raw, list) else []
    sources = sources_raw if isinstance(sources_raw, list) else []
    if not targets:
        invalid.add("APPROVED_BOM_TARGET_MISSING")
    if not sources:
        invalid.add("SOURCE_DOCUMENT_MISSING")

    targets_by_component: dict[str, Mapping[str, Any]] = {}
    for raw_target in targets:
        target = _object(raw_target, _TARGET_KEYS, invalid)
        component_id = target.get("component_id")
        if not _text(component_id) or component_id in targets_by_component:
            invalid.add("BOM_COMPONENT_ID_INVALID")
            continue
        if target.get("approval_status") != "APPROVED":
            blockers.add("BOM_TARGET_NOT_APPROVED")
        identity = target.get("identity")
        if not isinstance(identity, Mapping):
            invalid.add("BOM_IDENTITY_INVALID")
        else:
            _object(identity, _IDENTITY_KEYS, invalid)
        targets_by_component[component_id] = target

    identity_rows: list[dict[str, Any]] = []
    identity_traces: list[dict[str, Any]] = []
    coverage_sources: dict[str, list[dict[str, Any]]] = {event: [] for event in EVENT_TYPES}
    coverage_invalid: dict[str, list[dict[str, Any]]] = {event: [] for event in EVENT_TYPES}
    calculations: list[dict[str, Any]] = []
    condition_comparisons: list[dict[str, Any]] = []
    applicability_codes: set[str] = set()
    identity_codes: set[str] = set()
    seen_sources: set[str] = set()
    seen_documents: set[str] = set()
    seen_claims: set[str] = set()

    tid_requirement: dict[str, Any] | None = None
    if not invalid:
        try:
            tid_requirement = calculate_tid(
                mission["environment_tid"], mission["duration"], mission["shielding"], design_factor, model
            )
        except (KeyError, TypeError, ValueError) as exc:
            invalid.add("TID_MODEL_INPUT_INVALID")
            applicability_codes.add("TID_MODEL_INPUT_INVALID")
            tid_requirement = {"error": str(exc)}

    for raw_source in sources:
        source = _object(raw_source, _SOURCE_KEYS, invalid)
        source_id = source.get("source_id")
        document_id = source.get("document_id")
        source_valid = True
        if not _text(source_id) or source_id in seen_sources:
            invalid.add("SOURCE_ID_INVALID")
            source_valid = False
        else:
            seen_sources.add(source_id)
        if not _text(document_id) or document_id in seen_documents:
            invalid.add("DOCUMENT_ID_INVALID")
            source_valid = False
        else:
            seen_documents.add(document_id)
        if source.get("mission_case_id") != mission_case_id:
            invalid.add("MISSION_CASE_ID_MIXED")
            source_valid = False
        if source.get("data_class") not in {"SYNTHETIC", "PUBLISHED"}:
            invalid.add("SOURCE_DATA_CLASS_INVALID")
            source_valid = False
        if not _sha256(source.get("artifact_sha256")):
            invalid.add("SOURCE_ARTIFACT_HASH_INVALID")
            source_valid = False
        if not _sha256(source.get("observed_artifact_sha256")):
            invalid.add("SOURCE_OBSERVED_ARTIFACT_HASH_INVALID")
            source_valid = False
        elif source.get("artifact_sha256") != source.get("observed_artifact_sha256"):
            invalid.add("SOURCE_ARTIFACT_HASH_MISMATCH")
            source_valid = False
        if not _text(source.get("locator")):
            invalid.add("SOURCE_LOCATOR_INVALID")
            source_valid = False
        claims = source.get("claims")
        if not isinstance(claims, list) or not claims:
            invalid.add("SOURCE_CLAIMS_MISSING")
            continue

        for raw_claim in claims:
            claim = _object(raw_claim, _CLAIM_KEYS, invalid)
            claim_id = claim.get("claim_id")
            if not _text(claim_id) or claim_id in seen_claims:
                invalid.add("CLAIM_ID_INVALID")
            else:
                seen_claims.add(claim_id)
            component_id = claim.get("component_id")
            target = targets_by_component.get(component_id)
            if target is None:
                invalid.add("CLAIM_COMPONENT_NOT_IN_APPROVED_BOM")
                continue
            target_identity = target.get("identity") if isinstance(target.get("identity"), Mapping) else {}
            tested_identity = _object(claim.get("tested_identity"), _IDENTITY_KEYS, invalid)
            field_results: list[dict[str, Any]] = []
            for field in IDENTITY_FIELDS:
                approved_value = target_identity.get(field)
                tested_value = tested_identity.get(field)
                if not _text(approved_value) or not _text(tested_value):
                    status = "MISSING"
                    identity_codes.add(f"IDENTITY_{field.upper()}_MISSING")
                elif approved_value == tested_value:
                    status = "EXACT_MATCH"
                else:
                    status = "CONFLICT"
                    identity_codes.add(f"IDENTITY_{field.upper()}_CONFLICT")
                field_results.append({"field": field, "status": status})
            statuses = {row["status"] for row in field_results}
            identity_status = "CONFLICT" if "CONFLICT" in statuses else ("MISSING" if "MISSING" in statuses else "EXACT_MATCH")
            trace = _trace(source, claim)
            identity_rows.append(
                {"component_id": component_id, "claim_id": claim_id, "status": identity_status, "fields": field_results, "source_trace": trace}
            )
            identity_traces.append(trace)

            if not isinstance(claim.get("test_conditions"), Mapping):
                invalid.add("TEST_CONDITIONS_INVALID")
                conditions = {}
            else:
                conditions = _object(claim.get("test_conditions"), _CONDITION_KEYS, invalid)
            for dimension in UNSUPPORTED_CONDITIONS:
                if conditions.get(dimension) is None:
                    condition_status = "MISSING"
                    condition_code = f"{dimension.upper()}_TEST_CONDITION_MISSING"
                else:
                    condition_status = "UNSUPPORTED_BY_CURRENT_MODEL"
                    condition_code = f"{dimension.upper()}_COMPARISON_UNSUPPORTED"
                applicability_codes.add(condition_code)
                condition_comparisons.append(
                    {
                        "dimension": dimension,
                        "status": condition_status,
                        "blocker_code": condition_code,
                        "source_trace": trace,
                    }
                )

            events = claim.get("event_evidence")
            if not isinstance(events, list):
                invalid.add("EVENT_EVIDENCE_INVALID")
                continue
            for raw_event in events:
                event = _object(raw_event, _EVENT_KEYS, invalid)
                event_type = event.get("event_type")
                if event_type not in EVENT_TYPES:
                    invalid.add("EVENT_TYPE_INVALID")
                    continue
                event_trace = _trace(source, claim, event)
                if not _text(event.get("locator")):
                    invalid.add("EVENT_LOCATOR_INVALID")
                    coverage_invalid[event_type].append(event_trace)
                    continue
                if event.get("source_event_type") != event_type:
                    blockers.add("EVENT_TYPE_SUBSTITUTION")
                    coverage_invalid[event_type].append(event_trace)
                    continue
                if not source_valid:
                    coverage_invalid[event_type].append(event_trace)
                    continue
                coverage_sources[event_type].append(event_trace)

                if event_type in DESTRUCTIVE_EVENTS:
                    applicability_codes.add(f"{event_type}_APPLICABILITY_UNSUPPORTED")
                    continue
                if event_type == "TID":
                    limit = event.get("tid_test_limit")
                    if not _quantity_shape(limit) or not isinstance(tid_requirement, Mapping) or "required_tid_krad_si" not in tid_requirement:
                        invalid.add("TID_TEST_LIMIT_INVALID")
                        continue
                    try:
                        tested_limit = tid_krad_si(limit["value"], limit["unit"])
                    except (KeyError, TypeError, ValueError):
                        invalid.add("TID_TEST_LIMIT_INVALID")
                        continue
                    required = tid_requirement["required_tid_krad_si"]
                    status = "WITHIN_TESTED_RANGE" if tested_limit >= required else "OUTSIDE_TESTED_RANGE"
                    if status == "OUTSIDE_TESTED_RANGE":
                        applicability_codes.add("TID_TEST_RANGE_INSUFFICIENT")
                    calculations.append(
                        {"event_type": "TID", "status": status, "required_tid_krad_si": required, "tested_limit_krad_si": tested_limit, "source_trace": event_trace}
                    )
                elif event_type == "SEU":
                    cross_section = event.get("cross_section")
                    if not _quantity_shape(cross_section):
                        invalid.add("SEU_CROSS_SECTION_INVALID")
                        continue
                    try:
                        see = calculate_see(
                            mission["particle_flux"], cross_section, device_count, mission["duration"], 1.0, model["see_exposure_scale"]
                        )
                    except (KeyError, TypeError, ValueError):
                        invalid.add("SEU_MODEL_INPUT_INVALID")
                        continue
                    calculations.append(
                        {"event_type": "SEU", "status": "BOUNDED_SYNTHETIC_CALCULATION", "raw_events_per_mission": see["raw_events_per_mission"], "source_trace": event_trace}
                    )

    coverage_rows: list[dict[str, Any]] = []
    coverage_codes: set[str] = set()
    coverage_traces: list[dict[str, Any]] = []
    for event_type in EVENT_TYPES:
        traces = coverage_sources[event_type]
        invalid_traces = coverage_invalid[event_type]
        if traces:
            status = "PRESENT"
            coverage_traces.extend(traces)
        elif invalid_traces:
            status = "INVALID"
            coverage_codes.add(f"{event_type}_COVERAGE_INVALID")
            coverage_traces.extend(invalid_traces)
        else:
            status = "MISSING"
            coverage_codes.add(f"{event_type}_EVIDENCE_MISSING")
        coverage_rows.append({"event_type": event_type, "status": status, "source_trace": traces or invalid_traces})

    blockers.update(identity_codes)
    blockers.update(applicability_codes)
    blockers.update(coverage_codes)
    blockers.update(invalid)
    identity_statuses = {row["status"] for row in identity_rows}
    identity_status = "CONFLICT" if "CONFLICT" in identity_statuses else ("MISSING" if "MISSING" in identity_statuses or not identity_rows else "EXACT_MATCH")
    if invalid:
        identity_status = "NOT_EVALUATED"
        applicability_status = "NOT_EVALUATED"
        coverage_status = "NOT_EVALUATED"
    elif "BOM_TARGET_NOT_APPROVED" in blockers:
        identity_status = "NOT_EVALUATED"
        applicability_status = "NOT_EVALUATED"
        coverage_status = "COMPLETE" if not coverage_codes else "PARTIAL"
    else:
        applicability_status = "NOT_EVALUATED" if applicability_codes else "BOUNDED_TID_SEU_ONLY"
        coverage_status = "COMPLETE" if not coverage_codes else "PARTIAL"

    identity_question_codes = identity_codes | invalid
    if "BOM_TARGET_NOT_APPROVED" in blockers:
        identity_question_codes.add("BOM_TARGET_NOT_APPROVED")
    applicability_question_codes = applicability_codes | invalid
    coverage_question_codes = coverage_codes | invalid
    if "EVENT_TYPE_SUBSTITUTION" in blockers:
        coverage_question_codes.add("EVENT_TYPE_SUBSTITUTION")

    questions = {
        "exact_part_identity": _question(
            identity_status, identity_question_codes, identity_traces, "RESOLVE_EXACT_IDENTITY",
            "Provide field-complete approved BOM and test-article identity for every claim.",
        ),
        "mission_test_applicability": _question(
            applicability_status,
            applicability_question_codes,
            [item["source_trace"] for item in calculations]
            + [item["source_trace"] for item in condition_comparisons],
            "REVIEW_TEST_TO_MISSION_APPLICABILITY",
            "Resolve unsupported conditions and destructive-SEE applicability without extrapolation.",
        ),
        "event_coverage": _question(
            coverage_status, coverage_question_codes,
            coverage_traces, "ACQUIRE_EVENT_SPECIFIC_EVIDENCE",
            "Acquire independently traceable evidence for every missing or invalid event type.",
        ),
    }
    result = {
        "result_version": RESULT_VERSION,
        "mission_case_id": mission_case_id,
        "data_class": "SYNTHETIC",
        "processing_status": "INVALID_INPUT" if invalid else "VALID",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "stable_codes": sorted(blockers),
        "questions": questions,
        "identity_comparisons": identity_rows,
        "applicability_calculations": calculations,
        "test_condition_comparisons": condition_comparisons,
        "event_coverage": coverage_rows,
        "input_hash": _safe_input_hash(case),
    }
    result["output_hash"] = sha256({key: value for key, value in result.items() if key != "output_hash"})
    return result


def canonical_mission_case_result(result: Mapping[str, Any]) -> str:
    """Return the same canonical JSON representation used by the existing Core."""

    from .engine import canonical_bytes

    return canonical_bytes(copy.deepcopy(result)).decode("utf-8")
