"""Parse the reviewed SPENVIS SHIELDOSE-2 text signature without publishing it.

The parser produces internal candidates only. Contract emission remains gated by
the raw-artifact manifest v2 and an action-specific rights approval.
"""

from __future__ import annotations

import math
import re
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HEADER = re.compile(r"^SPENVIS\s+(?P<build>\S+)\s+-\s+(?P<completed>.+)$")
MISSION_TIME = re.compile(r"^Mission (?P<edge>start|end): (?P<value>.+)$")


@dataclass(frozen=True)
class DoseParseError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _require(text: str, needle: str, code: str) -> None:
    if needle not in text:
        raise DoseParseError(code, f"required marker is missing: {needle}")


def _csv_fields(line: str) -> list[str]:
    return [field.strip() for field in next(csv.reader([line], quotechar="'", skipinitialspace=True))]


def parse_shieldose2_text(text: str) -> dict[str, Any]:
    """Parse one SPENVIS ``spenvis_s2o.txt`` file after signature review."""

    lines = [line.rstrip() for line in text.splitlines()]
    nonempty = [line.strip() for line in lines if line.strip()]
    if not nonempty:
        raise DoseParseError("DOSE_TABLE_MISSING", "file is empty")

    parsed_lines = [_csv_fields(line) for line in nonempty]
    header = None
    for fields in parsed_lines:
        if len(fields) == 1:
            header = HEADER.match(fields[0])
            if header:
                break
    if header is None:
        raise DoseParseError("UNRECOGNIZED_SPENVIS_HEADER", "SPENVIS build header is missing")

    _require(text, "4pi Dose at Centre of Al Spheres", "UNSUPPORTED_GEOMETRY")
    _require(text, "Thick", "DOSE_TABLE_MISSING")
    _require(text, "mm", "UNSUPPORTED_UNITS")
    _require(text, "Dose", "DOSE_TABLE_MISSING")
    _require(text, "rad", "UNSUPPORTED_UNITS")
    _require(text, "Aluminium Absorber Thickness", "UNSUPPORTED_GEOMETRY")
    _require(text, "Dose in Si", "UNSUPPORTED_TARGET")

    tagged = {fields[0]: fields[2] for fields in parsed_lines if len(fields) >= 3 and fields[0] in {"PRJ_DEF", "PRJ_HDR"}}
    project = tagged.get("PRJ_DEF")
    title = tagged.get("PRJ_HDR")
    mission_times: dict[str, str] = {}
    for fields in parsed_lines:
        if len(fields) != 1:
            continue
        match = MISSION_TIME.match(fields[0])
        if match:
            mission_times[match.group("edge")] = match.group("value")
    duration = next((fields for fields in parsed_lines if len(fields) >= 4 and fields[0] == "MIS_DUR"), None)
    if not project:
        raise DoseParseError("PROJECT_MISMATCH", "project identifier is missing")
    if set(mission_times) != {"start", "end"} or duration is None:
        raise DoseParseError("MISSION_MISMATCH", "mission interval is missing")
    if duration[3] != "days":
        raise DoseParseError("UNSUPPORTED_UNITS", "mission duration must be expressed in days")
    try:
        mission_days = int(round(float(duration[2])))
    except ValueError as exc:
        raise DoseParseError("MISSION_MISMATCH", "mission duration is not numeric") from exc

    if ["Thick", "mm", "1", "Aluminium Absorber Thickness"] not in parsed_lines:
        raise DoseParseError("UNSUPPORTED_UNITS", "exact aluminium thickness signature is missing")
    if ["Dose", "rad", "5", "Dose in Si"] not in parsed_lines:
        raise DoseParseError("UNSUPPORTED_UNITS", "exact silicon dose signature is missing")
    rows: list[dict[str, float]] = []
    for fields in parsed_lines:
        if len(fields) != 6:
            continue
        try:
            values = [float(field) for field in fields]
        except ValueError:
            continue
        if not all(math.isfinite(value) and value >= 0 for value in values):
            raise DoseParseError("NONFINITE_OR_NEGATIVE_VALUE", "dose table contains an invalid value")
        rows.append(dict(zip(
            ("thickness_mm_al", "total_rad_si", "electrons_rad_si", "bremsstrahlung_rad_si", "trapped_protons_rad_si", "solar_protons_rad_si"),
            values,
        )))
    if not rows:
        raise DoseParseError("DOSE_TABLE_MISSING", "no six-column dose rows were found")

    return {
        "provider": {"platform_name": "SPENVIS", "platform_build": header.group("build")},
        "completed_at_provider_text": header.group("completed"),
        "project": project,
        "title": title,
        "mission": {"start": mission_times["start"], "end": mission_times["end"], "days": mission_days},
        "geometry": "CENTRE_OF_AL_SPHERES_4PI",
        "target_material": "SILICON",
        "shielding_unit": "mm_Al_equivalent",
        "dose_unit": "rad(Si)",
        "rows": rows,
    }


def parse_shieldose2_file(path: Path) -> dict[str, Any]:
    return parse_shieldose2_text(path.read_text(encoding="utf-8"))


def normalize_tid_candidates(
    parsed: dict[str, Any], expected_depths: Iterable[float] = (1.0, 2.0, 3.0, 4.0)
) -> list[dict[str, Any]]:
    """Create non-contract TID candidates; callers must retain HOLD status."""

    expected = [float(value) for value in expected_depths]
    observed = [row["thickness_mm_al"] for row in parsed["rows"]]
    if observed != expected:
        raise DoseParseError("SHIELDING_POINTS_MISMATCH", f"expected {expected}, observed {observed}")
    return [
        {
            "candidate_kind": "TID_POINT_CANDIDATE",
            "shielding": {"value": row["thickness_mm_al"], "unit": "mm_Al_equivalent", "material": "ALUMINUM"},
            "target_material": "SILICON",
            "dose": {"value": row["total_rad_si"], "unit": "rad(Si)"},
            "data_class": "CALCULATED",
            "contract_status": "HOLD_PENDING_PROVENANCE_AND_RIGHTS",
        }
        for row in parsed["rows"]
    ]
