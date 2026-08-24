"""Create a value-redacted scientific crosscheck candidate for SPENVIS.

This module can establish internal consistency of one reviewed bundle.  It
cannot turn that bundle into an independently crosschecked environment
contract: a second approved model/tool, pre-approved criteria, and an
independent reviewer remain mandatory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .spenvis_shieldose2 import DoseParseError, parse_shieldose2_file


RECORD_KIND = "SPECTRA_SPENVIS_CROSSCHECK_CANDIDATE"
RECORD_VERSION = "1.0.0"


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _check(check_id: str, passed: bool, locator: str, detail: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": "PASSED" if passed else "FAILED",
        "source_locator": locator,
        "detail": detail,
    }


def _contains_all(path: Path, markers: tuple[str, ...]) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in markers)


def _provider_time_to_iso(value: str) -> str:
    parsed = datetime.strptime(value, "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc)
    return parsed.isoformat().replace("+00:00", "Z")


def build_spenvis_crosscheck_candidate(bundle_root: Path, profile_path: Path) -> dict[str, Any]:
    """Assess value-redacted internal consistency and retain NOT_EVALUATED."""

    bundle_root = bundle_root.resolve()
    profile = _load_json(profile_path)
    manifest_path = bundle_root / "local-evidence-manifest.json"
    manifest = _load_json(manifest_path)
    raw = bundle_root / "raw"
    parsed = parse_shieldose2_file(raw / "spenvis_s2o.txt")

    expected_mission = profile["mission"]
    expected_depths = [float(point["thickness"]["value"]) for point in profile["shielding_points"]]
    observed_depths = [row["thickness_mm_al"] for row in parsed["rows"]]
    total_doses = [row["total_rad_si"] for row in parsed["rows"]]

    checks = [
        _check(
            "PROJECT_ID_MATCH",
            parsed["project"] == manifest["provider"]["project_id"],
            "raw/spenvis_s2o.txt + local-evidence-manifest.json#/provider/project_id",
            "Dose output project identity matches the local tracking manifest.",
        ),
        _check(
            "PLATFORM_BUILD_MATCH",
            parsed["provider"]["platform_build"] == manifest["provider"]["platform_build"],
            "raw/spenvis_s2o.txt + local-evidence-manifest.json#/provider/platform_build",
            "SPENVIS build signatures agree inside the reviewed bundle.",
        ),
        _check(
            "MISSION_SCOPE_MATCH",
            _provider_time_to_iso(parsed["mission"]["start"]) == expected_mission["start_at"]
            and _provider_time_to_iso(parsed["mission"]["end"]) == expected_mission["end_at"]
            and parsed["mission"]["days"] == expected_mission["duration"]["value"]
            and manifest["mission"]["duration_days"] == expected_mission["duration"]["value"],
            "raw/spenvis_s2o.txt + raw/spenvis_sap.html + environment/reference-path-v1.json#/mission",
            "Mission duration agrees with the assumed product baseline; timestamps remain provider text.",
        ),
        _check(
            "ORBIT_REPORT_SIGNATURE",
            _contains_all(
                raw / "spenvis_sap.html",
                (
                    "Mission start: 01/01/2027 00:00:00",
                    "Mission end: 01/01/2028 00:00:00",
                    "Apogee:</TD><TD>      550.00 km",
                    "Perigee:</TD><TD>      550.00 km",
                    "Inclination:</TD><TD>       97.60&deg;",
                ),
            ),
            "raw/spenvis_sap.html + environment/reference-path-v1.json#/mission",
            "Circular 550 km, 97.6 degree LEO and mission interval markers are present in the orbit report.",
        ),
        _check(
            "DOSE_SIGNATURE_MATCH",
            parsed["geometry"] == "CENTRE_OF_AL_SPHERES_4PI"
            and parsed["target_material"] == profile["target_material"]
            and parsed["dose_unit"] == "rad(Si)",
            "raw/spenvis_s2o.txt + raw/spenvis_s2p.html",
            "Geometry, target material, and dose unit signatures are present and consistent.",
        ),
        _check(
            "TRAPPED_MODEL_REPORT_SIGNATURE",
            _contains_all(
                raw / "spenvis_ae9ap9.html",
                ("Trapped  proton  model: AP9", "Trapped electron model: AE9", "Model run mode: mean"),
            ),
            "raw/spenvis_ae9ap9.html",
            "AE9/AP9 model-family and mean-mode report markers are present; exact version remains unverified.",
        ),
        _check(
            "SOLAR_MODEL_REPORT_SIGNATURE",
            _contains_all(
                raw / "spenvis_sep.html",
                ("Solar particle model: SAPPHIRE total fluence", "95.00% probability of fluences not being exceeded"),
            ),
            "raw/spenvis_sep.html",
            "SAPPHIRE total-fluence and 95 percent report markers are present.",
        ),
        _check(
            "SHIELDOSE_REPORT_SIGNATURE",
            _contains_all(
                raw / "spenvis_s2p.html",
                ("SHIELDOSE-2 Version 2.10", "Target material: Si", "Shield configuration: Centre of Al spheres"),
            ),
            "raw/spenvis_s2p.html",
            "SHIELDOSE-2 version, silicon target, and spherical aluminium configuration markers are present.",
        ),
        _check(
            "SOURCE_COMPONENT_COLUMNS_PRESENT",
            all(
                all(
                    key in row
                    for key in (
                        "electrons_rad_si",
                        "bremsstrahlung_rad_si",
                        "trapped_protons_rad_si",
                        "solar_protons_rad_si",
                    )
                )
                for row in parsed["rows"]
            ),
            "raw/spenvis_s2o.txt",
            "Trapped-electron, bremsstrahlung, trapped-proton, and solar-proton columns are structurally present.",
        ),
        _check(
            "SHIELDING_POINTS_EXACT",
            observed_depths == expected_depths,
            "raw/spenvis_s2o.txt + environment/reference-path-v1.json#/shielding_points",
            "The four reviewed aluminium shielding depths appear once and in the expected order.",
        ),
        _check(
            "SHIELDING_DIRECTION_NONINCREASING",
            all(current <= previous for previous, current in zip(total_doses, total_doses[1:])),
            "raw/spenvis_s2o.txt",
            "Total silicon dose is non-increasing as aluminium shielding increases; numeric values are redacted.",
        ),
    ]

    failed = [item["check_id"] for item in checks if item["status"] == "FAILED"]
    inherited_blockers = [
        "PROVIDER_JOB_REFERENCE_MISSING",
        "RIGHTS_APPROVAL_MISSING",
        "RAW_ARTIFACT_MANIFEST_V2_MISSING",
        "MODEL_VERSION_NOT_INDEPENDENTLY_VERIFIED",
        "INDEPENDENT_COMPARATOR_MISSING",
        "APPROVED_TOLERANCE_MISSING",
        "INDEPENDENT_REVIEWER_MISSING",
        "SCIENTIFIC_CROSSCHECK_NOT_EVALUATED",
    ]
    result: dict[str, Any] = {
        "record_kind": RECORD_KIND,
        "record_version": RECORD_VERSION,
        "evidence_class": "ACTUAL_REVIEW",
        "decision_use": False,
        "bundle_identity": {
            "bundle_id": manifest["bundle_id"],
            "artifact_set_sha256": "sha256:" + manifest["artifact_set_sha256"],
            "local_manifest_sha256": _canonical_sha256(manifest),
        },
        "internal_consistency": {
            "status": "PASSED" if not failed else "FAILED",
            "check_count": len(checks),
            "failed_check_ids": failed,
            "checks": checks,
            "dose_values_included": False,
        },
        "independent_crosscheck": {
            "status": "NOT_EVALUATED",
            "comparator": None,
            "approved_criteria": None,
            "independent_reviewer": None,
            "result_hash": None,
        },
        "issuance_status": "HOLD_NOT_ISSUED",
        "assurance_decision": "HOLD",
        "error_codes": failed + inherited_blockers,
    }
    result["canonical_payload_sha256"] = _canonical_sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = build_spenvis_crosscheck_candidate(args.bundle_root, args.profile)
    except (DoseParseError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "internal_consistency": result["internal_consistency"]["status"],
                "check_count": result["internal_consistency"]["check_count"],
                "independent_crosscheck": result["independent_crosscheck"]["status"],
                "issuance_status": result["issuance_status"],
                "dose_values_included": result["internal_consistency"]["dose_values_included"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
