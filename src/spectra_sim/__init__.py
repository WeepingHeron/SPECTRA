"""Deterministic, synthetic-only SPECTRA simulation baseline."""

from .engine import SimulationOptions, run_simulation
from .mvp_engine import MvpDecisionError, canonical_result_json, run_mvp_decision
from .mission_case import canonical_mission_case_result, synthesize_mission_case
from .runtime_mitigation import canonical_runtime_json, evaluate_runtime_mitigation

__all__ = [
    "MvpDecisionError",
    "SimulationOptions",
    "canonical_result_json",
    "canonical_mission_case_result",
    "canonical_runtime_json",
    "evaluate_runtime_mitigation",
    "run_mvp_decision",
    "run_simulation",
    "synthesize_mission_case",
]
