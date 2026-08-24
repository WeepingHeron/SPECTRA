"""Classify bounded CAD manifest changes without parsing or calculating geometry."""

from __future__ import annotations

import re
from typing import Any, Mapping

CONTRACT_VERSION = "CAD_CHANGE_GATE_1.0.0"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,79}$")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,79}$")
UNITS = frozenset({"mm", "cm", "m"})

_ROOT_KEYS = frozenset({"candidate_class", "baseline", "variant", "requested_outcome"})
_MANIFEST_KEYS = frozenset(
    {
        "revision_id",
        "content_sha256",
        "length_unit",
        "coordinate_frame",
        "material_map",
        "shielding_region_ids",
    }
)
_MATERIAL_KEYS = frozenset({"region_id", "material_id"})
_OUTCOME_KEYS = frozenset(
    {"engineering_gate", "assurance_decision", "suitability", "geometry_calculated"}
)


def _object(value: Any, keys: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if set(value) != keys:
        codes.add("INPUT_FIELDS_INVALID")
    return value


def _safe_id(value: Any) -> bool:
    return isinstance(value, str) and SAFE_ID.fullmatch(value) is not None


def _manifest(value: Any, side: str, codes: set[str]) -> dict[str, Any]:
    manifest = _object(value, _MANIFEST_KEYS, codes)
    revision = manifest.get("revision_id")
    if not isinstance(revision, str) or REVISION.fullmatch(revision) is None:
        codes.add(f"{side}_REVISION_INVALID")
    digest = manifest.get("content_sha256")
    if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
        codes.add(f"{side}_HASH_INVALID")
    unit = manifest.get("length_unit")
    if unit not in UNITS:
        codes.add(f"{side}_UNIT_INVALID")
    frame = manifest.get("coordinate_frame")
    if not _safe_id(frame):
        codes.add(f"{side}_COORDINATE_FRAME_INVALID")

    materials_raw = manifest.get("material_map")
    materials: dict[str, str] = {}
    if not isinstance(materials_raw, list) or not materials_raw:
        codes.add(f"{side}_MATERIAL_MAP_INVALID")
    else:
        for item in materials_raw:
            entry = _object(item, _MATERIAL_KEYS, codes)
            region_id, material_id = entry.get("region_id"), entry.get("material_id")
            if not _safe_id(region_id) or not _safe_id(material_id):
                codes.add(f"{side}_MATERIAL_BINDING_INVALID")
                continue
            if region_id in materials:
                codes.add(f"{side}_MATERIAL_REGION_DUPLICATE")
            materials[region_id] = material_id

    regions_raw = manifest.get("shielding_region_ids")
    regions: list[str] = []
    if not isinstance(regions_raw, list) or not regions_raw:
        codes.add(f"{side}_SHIELDING_REGIONS_INVALID")
    else:
        for region in regions_raw:
            if not _safe_id(region):
                codes.add(f"{side}_SHIELDING_REGION_INVALID")
            elif region in regions:
                codes.add(f"{side}_SHIELDING_REGION_DUPLICATE")
            else:
                regions.append(region)
    if set(materials) != set(regions):
        codes.add(f"{side}_REGION_MATERIAL_BINDING_MISMATCH")
    return {
        "revision": revision,
        "hash": digest,
        "unit": unit,
        "frame": frame,
        "materials": materials,
        "regions": tuple(sorted(regions)),
    }


def assess_cad_change(payload: Any) -> dict[str, Any]:
    """Return a non-geometric, non-assurance CAD change receipt."""

    codes: set[str] = set()
    root = _object(payload, _ROOT_KEYS, codes)
    candidate_class = root.get("candidate_class")
    if candidate_class not in {"SYNTHETIC_CONTROL", "ACTUAL_CANDIDATE"}:
        codes.add("CANDIDATE_CLASS_INVALID")

    baseline = _manifest(root.get("baseline"), "BASELINE", codes)
    variant = _manifest(root.get("variant"), "VARIANT", codes)
    requested = _object(root.get("requested_outcome"), _OUTCOME_KEYS, codes)
    if (
        requested.get("engineering_gate") != "NOT_EVALUATED"
        or requested.get("assurance_decision") != "HOLD"
        or requested.get("suitability") != "NOT_EVALUATED"
        or requested.get("geometry_calculated") is not False
    ):
        codes.add("OPTIMISTIC_OUTCOME_FORBIDDEN")

    if baseline["revision"] == variant["revision"] and baseline["hash"] != variant["hash"]:
        codes.add("SAME_REVISION_HASH_MISMATCH")
    if baseline["unit"] != variant["unit"]:
        codes.add("LENGTH_UNIT_DRIFT")
    if baseline["frame"] != variant["frame"]:
        codes.add("COORDINATE_FRAME_DRIFT")
    if baseline["regions"] != variant["regions"]:
        codes.add("SHIELDING_REGION_SET_CHANGED")

    binding_codes = {
        code
        for code in codes
        if code.endswith(("_INVALID", "_MISMATCH", "_DRIFT", "_CHANGED"))
    }
    if binding_codes:
        category = "BINDING_INVALID"
    elif baseline["materials"] != variant["materials"]:
        category = "MATERIAL_CHANGED"
    elif baseline["hash"] != variant["hash"]:
        category = "GEOMETRY_CHANGED"
    else:
        category = "UNCHANGED"

    if candidate_class == "SYNTHETIC_CONTROL":
        codes.add("SYNTHETIC_ONLY")
    change_status = "CHANGE_DETECTED" if category in {"MATERIAL_CHANGED", "GEOMETRY_CHANGED"} else category
    processing_status = "INVALID_INPUT" if category == "BINDING_INVALID" else "VALID"
    return {
        "contract_version": CONTRACT_VERSION,
        "candidate_class": candidate_class if candidate_class in {"SYNTHETIC_CONTROL", "ACTUAL_CANDIDATE"} else "INVALID",
        "processing_status": processing_status,
        "change_status": change_status,
        "change_category": category,
        "geometry_calculated": False,
        "blocker_codes": sorted(codes),
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
