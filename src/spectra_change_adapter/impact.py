"""Classify bounded HW-SW change impact without geometry or suitability claims."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


CONTRACT_VERSION = "CHANGE_IMPACT_RECEIPT_1.0.0"
DOMAIN_ORDER = ("CAD", "HARDWARE", "SOFTWARE", "EVIDENCE", "ASSURANCE")
REVIEW_BY_DOMAIN = {
    "CAD": "CAD_CHANGE_REVIEW",
    "HARDWARE": "HARDWARE_CHANGE_REVIEW",
    "SOFTWARE": "SOFTWARE_CHANGE_REVIEW",
    "EVIDENCE": "EVIDENCE_GAP_REVIEW",
    "ASSURANCE": "ASSURANCE_BOUNDARY_REVIEW",
}
CAD_AXES = frozenset(
    {"GEOMETRY_REVISION", "COMPONENT_POSITION", "MATERIAL_THICKNESS_MAPPING"}
)
REVISION_AXES = frozenset(
    {"HARDWARE_MITIGATION", "SOFTWARE_MITIGATION", "ASSURANCE_POLICY"}
)
EVIDENCE_GAP_CODES = frozenset(
    {
        "STAGE3_INPUT_UNAVAILABLE",
        "STAGE4_INPUT_UNAVAILABLE",
        "BOM_APPROVAL_MISSING",
        "RIGHTS_UNRESOLVED",
        "MISSION_APPLICABILITY_NOT_EVALUATED",
        "DESTRUCTIVE_SEE_EVIDENCE_MISSING",
        "ENVIRONMENT_CONTRACT_NOT_ISSUED",
        "PART_EVIDENCE_NOT_ISSUED",
    }
)
TOP_KEYS = frozenset(
    {
        "change_class",
        "cad_change_receipt",
        "mitigation_policy_revision",
        "evidence_gap_codes",
        "requested_outcome",
    }
)
CAD_KEYS = frozenset(
    {"receipt_sha256", "change_axes", "linkage_status", "used_for_decision"}
)
REVISION_KEYS = frozenset(
    {"revision_sha256", "revision_axes", "dependency_status", "used_for_decision"}
)
OUTCOME_KEYS = frozenset(
    {
        "impact_status",
        "engineering_gate",
        "assurance_decision",
        "suitability",
        "used_for_decision",
    }
)


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _exact_object(value: Any, keys: frozenset[str], errors: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.add("INPUT_SHAPE_INVALID")
        return {}
    if set(value) != keys:
        errors.add("INPUT_FIELD_FORBIDDEN")
    return value


def _axis_list(
    value: Any, allowed: frozenset[str], unknown_code: str, errors: set[str]
) -> list[str]:
    if not isinstance(value, list):
        errors.add("INPUT_SHAPE_INVALID")
        return []
    if any(not isinstance(item, str) for item in value):
        errors.add("INPUT_SHAPE_INVALID")
        return []
    if len(value) != len(set(value)):
        errors.add("DEPENDENCY_DUPLICATE")
    if any(item not in allowed for item in value):
        errors.add(unknown_code)
    return value


def _validate_cad(value: Any, errors: set[str]) -> tuple[list[str], str]:
    projection = _exact_object(value, CAD_KEYS, errors)
    axes = _axis_list(
        projection.get("change_axes"), CAD_AXES, "CAD_DEPENDENCY_UNKNOWN", errors
    )
    if projection.get("linkage_status") != "NOT_EVALUATED":
        errors.add("OPTIMISTIC_CAD_LINKAGE_FORBIDDEN")
    if projection.get("used_for_decision") is not False:
        errors.add("DECISION_USE_FORBIDDEN")
    declared = projection.get("receipt_sha256")
    material = {
        "change_axes": projection.get("change_axes"),
        "linkage_status": projection.get("linkage_status"),
        "used_for_decision": projection.get("used_for_decision"),
    }
    if not _is_sha256(declared) or declared != _sha256(material):
        errors.add("CAD_RECEIPT_HASH_MISMATCH")
    return axes, declared if _is_sha256(declared) else "UNAVAILABLE"


def _validate_revision(value: Any, errors: set[str]) -> tuple[list[str], str]:
    projection = _exact_object(value, REVISION_KEYS, errors)
    axes = _axis_list(
        projection.get("revision_axes"),
        REVISION_AXES,
        "REVISION_DEPENDENCY_UNKNOWN",
        errors,
    )
    if projection.get("dependency_status") != "NOT_EVALUATED":
        errors.add("OPTIMISTIC_DEPENDENCY_STATUS_FORBIDDEN")
    if projection.get("used_for_decision") is not False:
        errors.add("DECISION_USE_FORBIDDEN")
    declared = projection.get("revision_sha256")
    material = {
        "revision_axes": projection.get("revision_axes"),
        "dependency_status": projection.get("dependency_status"),
        "used_for_decision": projection.get("used_for_decision"),
    }
    if not _is_sha256(declared) or declared != _sha256(material):
        errors.add("REVISION_RECEIPT_HASH_MISMATCH")
    return axes, declared if _is_sha256(declared) else "UNAVAILABLE"


def _validate_gaps(value: Any, errors: set[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.add("INPUT_SHAPE_INVALID")
        return []
    if len(value) != len(set(value)):
        errors.add("EVIDENCE_GAP_DUPLICATE")
    if any(item not in EVIDENCE_GAP_CODES for item in value):
        errors.add("EVIDENCE_GAP_UNKNOWN")
    return value


def _validate_outcome(value: Any, errors: set[str]) -> None:
    outcome = _exact_object(value, OUTCOME_KEYS, errors)
    required = {
        "impact_status": "REVIEW_REQUIRED",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    if any(outcome.get(field) != expected for field, expected in required.items()):
        errors.add("OPTIMISTIC_OUTCOME_FORBIDDEN")


def classify_change_impact(payload: Any) -> dict[str, Any]:
    """Return a deterministic fail-closed impact receipt.

    The result identifies review domains only.  It does not calculate geometry,
    radiation, hardware performance, suitability, approval, or assurance PASS.
    """

    errors: set[str] = set()
    projection = _exact_object(payload, TOP_KEYS, errors)
    if projection.get("change_class") != "SYNTHETIC_CONTROL":
        errors.add("CHANGE_CLASS_FORBIDDEN")

    cad_axes, cad_hash = _validate_cad(projection.get("cad_change_receipt"), errors)
    revision_axes, revision_hash = _validate_revision(
        projection.get("mitigation_policy_revision"), errors
    )
    gap_codes = _validate_gaps(projection.get("evidence_gap_codes"), errors)
    _validate_outcome(projection.get("requested_outcome"), errors)

    if not cad_axes and not revision_axes and not gap_codes:
        errors.add("CHANGE_DEPENDENCY_MISSING")

    if errors:
        affected_domains = list(DOMAIN_ORDER)
        required_reviews = [REVIEW_BY_DOMAIN[domain] for domain in DOMAIN_ORDER]
        processing_status = (
            "PROVENANCE_FAILURE"
            if errors.intersection(
                {"CAD_RECEIPT_HASH_MISMATCH", "REVISION_RECEIPT_HASH_MISMATCH"}
            )
            else "INVALID_INPUT"
        )
        impact_status = "DATA_UNAVAILABLE"
        cad_hash = "UNAVAILABLE"
        revision_hash = "UNAVAILABLE"
        gap_codes_out: list[str] = []
    else:
        affected: set[str] = {"ASSURANCE"}
        if cad_axes:
            affected.update({"CAD", "HARDWARE"})
        if "HARDWARE_MITIGATION" in revision_axes:
            affected.add("HARDWARE")
        if "SOFTWARE_MITIGATION" in revision_axes:
            affected.add("SOFTWARE")
        if gap_codes:
            affected.update({"EVIDENCE", "ASSURANCE"})
        affected_domains = [domain for domain in DOMAIN_ORDER if domain in affected]
        required_reviews = [REVIEW_BY_DOMAIN[domain] for domain in affected_domains]
        processing_status = "VALID"
        impact_status = "REVIEW_REQUIRED"
        gap_codes_out = sorted(gap_codes)

    body = {
        "contract_version": CONTRACT_VERSION,
        "processing_status": processing_status,
        "impact_status": impact_status,
        "affected_domains": affected_domains,
        "required_reviews": required_reviews,
        "source_receipt_hashes": {
            "cad_change_receipt_sha256": cad_hash,
            "mitigation_policy_revision_sha256": revision_hash,
        },
        "evidence_gap_codes": gap_codes_out,
        "error_codes": sorted(errors),
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    receipt = dict(body)
    receipt["receipt_sha256"] = _sha256(body)
    return receipt
