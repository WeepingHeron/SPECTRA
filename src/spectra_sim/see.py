"""Deterministic SEE event comparison for synthetic inputs."""

import math

from .units import duration_seconds


def calculate_see(
    particle_flux: dict,
    cross_section: dict,
    component_count: int,
    mission_duration: dict,
    mitigation_factor: float,
    exposure_scale: float,
) -> dict:
    if particle_flux.get("unit") != "particles/cm2/s":
        raise ValueError("particle flux must use particles/cm2/s")
    if cross_section.get("unit") != "cm2/device":
        raise ValueError("Stage 2 baseline supports cm2/device only")
    numeric_inputs = {
        "particle flux": float(particle_flux["value"]),
        "cross section": float(cross_section["value"]),
        "mitigation factor": float(mitigation_factor),
        "synthetic exposure scale": float(exposure_scale),
    }
    if any(not math.isfinite(value) for value in numeric_inputs.values()):
        raise ValueError("SEE inputs must be finite")
    if numeric_inputs["particle flux"] < 0 or numeric_inputs["cross section"] < 0:
        raise ValueError("particle flux and cross section must be non-negative")
    if not 0 < numeric_inputs["mitigation factor"] <= 1:
        raise ValueError("mitigation factor must be greater than zero and at most one")
    if numeric_inputs["synthetic exposure scale"] <= 0:
        raise ValueError("synthetic exposure scale must be greater than zero")
    seconds = duration_seconds(mission_duration["value"], mission_duration["unit"])
    raw_events = (
        numeric_inputs["particle flux"]
        * numeric_inputs["cross section"]
        * int(component_count)
        * seconds
        * numeric_inputs["synthetic exposure scale"]
    )
    residual_events = raw_events * numeric_inputs["mitigation factor"]
    return {
        "duration_seconds": seconds,
        "raw_events_per_mission": raw_events,
        "residual_events_per_mission": residual_events,
    }
