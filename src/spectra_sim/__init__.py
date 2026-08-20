"""Deterministic, synthetic-only SPECTRA simulation baseline."""

from .engine import SimulationOptions, run_simulation
from .mvp_engine import MvpDecisionError, canonical_result_json, run_mvp_decision

__all__ = [
    "MvpDecisionError",
    "SimulationOptions",
    "canonical_result_json",
    "run_mvp_decision",
    "run_simulation",
]
