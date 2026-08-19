"""Deterministic TID comparison for the explicitly synthetic baseline."""

import math

from .units import duration_years, tid_krad_si


class OutOfModelScope(ValueError):
    """Raised when an input would require interpolation or extrapolation."""


def shielding_factor(thickness_mm: float, factors: dict[str, float]) -> float:
    thickness_mm = float(thickness_mm)
    if not math.isfinite(thickness_mm) or thickness_mm <= 0:
        raise OutOfModelScope("shielding thickness must be finite and greater than zero")
    key = f"{float(thickness_mm):g}"
    if key not in factors:
        raise OutOfModelScope(
            f"shielding {thickness_mm:g} mm is outside the discrete synthetic model"
        )
    return float(factors[key])


def calculate_tid(
    environment_tid: dict,
    mission_duration: dict,
    shielding_thickness: dict,
    design_factor: float,
    model: dict,
) -> dict:
    if shielding_thickness.get("unit") != "mm_Al_equivalent":
        raise OutOfModelScope("only mm_Al_equivalent shielding is supported")
    years = duration_years(mission_duration["value"], mission_duration["unit"])
    reference_years = float(model["reference_duration_years"])
    if not math.isfinite(reference_years) or reference_years <= 0:
        raise ValueError("reference duration must be finite and greater than zero")
    unshielded_krad = tid_krad_si(environment_tid["value"], environment_tid["unit"])
    attenuation = shielding_factor(
        shielding_thickness["value"], model["shielding_factors_by_mm"]
    )
    if not math.isfinite(attenuation) or not 0 < attenuation <= 1:
        raise ValueError("synthetic shielding factor must be greater than zero and at most one")
    design_factor = float(design_factor)
    if not math.isfinite(design_factor) or design_factor < 1:
        raise ValueError("TID design factor must be finite and at least one")
    shielded = unshielded_krad * (years / reference_years) * attenuation
    required = shielded * design_factor
    return {
        "duration_years": years,
        "shielding_factor": attenuation,
        "shielded_tid_krad_si": shielded,
        "required_tid_krad_si": required,
    }
