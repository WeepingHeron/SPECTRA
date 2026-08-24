"""Fail-closed gate for published-reference versus SPECTRA comparisons.

The gate only checks whether a bounded numerical comparison is internally
consistent and whether it may be used as direct validation.  It does not issue
an EvidencePacket, establish mission applicability, or approve a part.
"""

from __future__ import annotations

import math
from typing import Any, Mapping


INPUT_CONTRACT_VERSION = "SPECTRA_REFERENCE_COMPARISON_1.0.0"
RESULT_CONTRACT_VERSION = "PUBLISHED_REFERENCE_GATE_RESULT_1.0.0"
SHA256_HEX_LENGTH = 64

_TOP_LEVEL_KEYS = frozenset(
    {
        "contract_version",
        "comparison_id",
        "created_at",
        "processing_status",
        "comparison_status",
        "assurance_decision",
        "used_for_decision",
        "approved_catalog_target",
        "published_observation",
        "spectra_synthetic_reference",
        "numeric_comparison",
        "blocking_codes",
    }
)
_TARGET_KEYS = frozenset(
    {"manufacturer", "orderable_part_number", "package", "identity_status"}
)
_PUBLISHED_KEYS = frozenset(
    {
        "data_class",
        "source",
        "locator",
        "tested_identity",
        "test_conditions",
        "result",
        "additional_screening_observation",
    }
)
_SOURCE_KEYS = frozenset(
    {
        "title",
        "author",
        "publication_type",
        "doi",
        "record_url",
        "artifact_url",
        "license",
        "observed_artifact_sha256",
    }
)
_IDENTITY_KEYS = frozenset(
    {
        "manufacturer",
        "part_family",
        "orderable_part_number",
        "package",
        "lot_id",
        "die_revision",
        "process_nm_stated",
        "identity_status",
    }
)
_RESULT_KEYS = frozenset({"event_type", "cross_section", "mcu_observed"})
_CROSS_SECTION_KEYS = frozenset({"value", "uncertainty", "unit"})
_SYNTHETIC_KEYS = frozenset(
    {
        "data_class",
        "case_file",
        "part_evidence_file",
        "tested_identity",
        "cross_section",
        "see_exposure_scale",
        "raw_seu_events_per_mission",
        "physical_model_status",
    }
)
_NUMERIC_KEYS = frozenset(
    {
        "metric",
        "synthetic_divided_by_published",
        "interpretation",
        "direct_validation_allowed",
    }
)
_SCREENING_KEYS = frozenset(
    {
        "radiation_source",
        "reported_dose",
        "reported_outcome",
        "direct_tid_comparison_allowed",
        "reason",
    }
)


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == SHA256_HEX_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _object(
    value: Any,
    allowed: frozenset[str],
    invalid_codes: set[str],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        invalid_codes.add("INPUT_SHAPE_INVALID")
        return {}
    if any(not isinstance(key, str) or key not in allowed for key in value):
        invalid_codes.add("INPUT_FIELD_FORBIDDEN")
    return value


def _validate_declared_boundary(
    record: Mapping[str, Any], invalid_codes: set[str]
) -> None:
    if record.get("contract_version") != INPUT_CONTRACT_VERSION:
        invalid_codes.add("CONTRACT_VERSION_UNSUPPORTED")
    if not _is_text(record.get("comparison_id")):
        invalid_codes.add("COMPARISON_ID_MISSING")
    if not _is_text(record.get("created_at")):
        invalid_codes.add("CREATED_AT_MISSING")
    if record.get("processing_status") != "VALID":
        invalid_codes.add("DECLARED_PROCESSING_STATUS_INVALID")
    if (
        record.get("comparison_status") != "NOT_COMPARABLE"
        or record.get("assurance_decision") != "HOLD"
        or record.get("used_for_decision") is not False
    ):
        invalid_codes.add("OPTIMISTIC_COMPARISON_REJECTED")


def _validate_source(
    published: Mapping[str, Any], invalid_codes: set[str], blockers: set[str]
) -> None:
    if published.get("data_class") != "PUBLISHED":
        invalid_codes.add("PUBLISHED_DATA_CLASS_INVALID")
    source = _object(published.get("source"), _SOURCE_KEYS, invalid_codes)
    required = ("title", "doi", "record_url", "artifact_url", "license")
    if not all(_is_text(source.get(field)) for field in required):
        invalid_codes.add("PUBLISHED_SOURCE_INCOMPLETE")
    if not _is_sha256(source.get("observed_artifact_sha256")):
        invalid_codes.add("PUBLISHED_ARTIFACT_HASH_INVALID")

    # A lone observed hash is not an approved raw-artifact manifest binding.
    blockers.add("SOURCE_ARTIFACT_MANIFEST_MISSING")


def _validate_identity(
    target: Mapping[str, Any],
    tested: Mapping[str, Any],
    invalid_codes: set[str],
    blockers: set[str],
) -> None:
    if not all(
        _is_text(target.get(field))
        for field in ("manufacturer", "orderable_part_number", "package")
    ):
        invalid_codes.add("APPROVED_TARGET_IDENTITY_INVALID")
        return
    if target.get("identity_status") != "EXACT_CATALOG_TARGET":
        invalid_codes.add("APPROVED_TARGET_IDENTITY_INVALID")

    if tested.get("manufacturer") != target.get("manufacturer"):
        blockers.add("MANUFACTURER_MISMATCH")
    tested_orderable = tested.get("orderable_part_number")
    if not _is_text(tested_orderable):
        blockers.add("PART_IDENTITY_PARTIAL")
    elif tested_orderable != target.get("orderable_part_number"):
        blockers.add("PART_IDENTITY_MISMATCH")
    if tested.get("package") != target.get("package"):
        blockers.add("PACKAGE_MISMATCH")
    if not _is_text(tested.get("lot_id")) or not _is_text(
        tested.get("die_revision")
    ):
        blockers.add("LOT_DIE_UNRESOLVED")


def _cross_section(
    value: Any,
    invalid_codes: set[str],
    *,
    uncertainty_required: bool = False,
) -> tuple[float | None, str | None]:
    cross_section = _object(value, _CROSS_SECTION_KEYS, invalid_codes)
    numeric = cross_section.get("value")
    unit = cross_section.get("unit")
    if not _is_positive_finite(numeric):
        invalid_codes.add("CROSS_SECTION_INVALID")
        numeric = None
    if not _is_text(unit):
        invalid_codes.add("CROSS_SECTION_UNIT_INVALID")
        unit = None
    if uncertainty_required and not _is_positive_finite(
        cross_section.get("uncertainty")
    ):
        invalid_codes.add("CROSS_SECTION_UNCERTAINTY_INVALID")
    return numeric, unit


def assess_reference_comparison(record: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute a deterministic, fail-closed reference-comparison receipt."""

    invalid_codes: set[str] = set()
    blockers: set[str] = {
        "DESTRUCTIVE_SEE_EVIDENCE_MISSING",
        "MISSION_ENVIRONMENT_UNAVAILABLE",
        "PARTICLE_SPECTRUM_MISMATCH",
        "RIGHTS_SCOPE_UNRESOLVED",
        "TID_EVIDENCE_MISSING",
    }
    root = _object(record, _TOP_LEVEL_KEYS, invalid_codes)
    _validate_declared_boundary(root, invalid_codes)

    target = _object(root.get("approved_catalog_target"), _TARGET_KEYS, invalid_codes)
    published = _object(
        root.get("published_observation"), _PUBLISHED_KEYS, invalid_codes
    )
    synthetic = _object(
        root.get("spectra_synthetic_reference"), _SYNTHETIC_KEYS, invalid_codes
    )
    numeric = _object(root.get("numeric_comparison"), _NUMERIC_KEYS, invalid_codes)

    _validate_source(published, invalid_codes, blockers)
    tested = _object(published.get("tested_identity"), _IDENTITY_KEYS, invalid_codes)
    _validate_identity(target, tested, invalid_codes, blockers)

    published_result = _object(
        published.get("result"), _RESULT_KEYS, invalid_codes
    )
    if published_result.get("event_type") != "SEU":
        invalid_codes.add("PUBLISHED_EVENT_TYPE_INVALID")
    published_value, published_unit = _cross_section(
        published_result.get("cross_section"),
        invalid_codes,
        uncertainty_required=True,
    )
    synthetic_value, synthetic_unit = _cross_section(
        synthetic.get("cross_section"), invalid_codes
    )

    if synthetic.get("data_class") != "SYNTHETIC":
        invalid_codes.add("SYNTHETIC_DATA_CLASS_INVALID")
    if synthetic.get("physical_model_status") != "SYNTHETIC_NOT_PHYSICAL":
        invalid_codes.add("SYNTHETIC_MODEL_STATUS_INVALID")
    blockers.add("SYNTHETIC_PART_MISMATCH")
    exposure_scale = synthetic.get("see_exposure_scale")
    if not _is_positive_finite(exposure_scale):
        invalid_codes.add("SYNTHETIC_EXPOSURE_SCALE_INVALID")
    elif exposure_scale != 1:
        blockers.add("SYNTHETIC_EXPOSURE_SCALE")

    screening = _object(
        published.get("additional_screening_observation"),
        _SCREENING_KEYS,
        invalid_codes,
    )
    if screening.get("direct_tid_comparison_allowed") is not False:
        invalid_codes.add("OPTIMISTIC_TID_COMPARISON_REJECTED")
    if numeric.get("direct_validation_allowed") is not False:
        invalid_codes.add("OPTIMISTIC_COMPARISON_REJECTED")

    computed_ratio: float | None = None
    if published_unit is not None and synthetic_unit is not None:
        if published_unit != synthetic_unit or published_unit != "cm2/device":
            blockers.add("CROSS_SECTION_UNIT_MISMATCH")
        elif published_value is not None and synthetic_value is not None:
            computed_ratio = synthetic_value / published_value

    recorded_ratio = numeric.get("synthetic_divided_by_published")
    if computed_ratio is not None:
        if not _is_positive_finite(recorded_ratio) or recorded_ratio != computed_ratio:
            invalid_codes.add("RECORDED_RATIO_MISMATCH")

    codes = invalid_codes | blockers
    processing_status = "INVALID_INPUT" if invalid_codes else "VALID"
    if invalid_codes or computed_ratio is None:
        computed_ratio = None
        ratio_status = "NOT_COMPUTED"
    else:
        ratio_status = "CALCULATED_REFERENCE_ONLY"

    return {
        "contract_version": RESULT_CONTRACT_VERSION,
        "processing_status": processing_status,
        "comparison_status": "NOT_COMPARABLE",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "direct_validation_allowed": False,
        "numeric_comparison": {
            "status": ratio_status,
            "synthetic_divided_by_published": computed_ratio,
            "unit": "cm2/device" if computed_ratio is not None else None,
        },
        "stable_codes": sorted(codes),
    }
