"""Deterministic, fail-closed document intake adapters."""

from .candidate_intake import evaluate_document_intake
from .candidate_bundle import evaluate_candidate_bundle
from .evidence_candidates import link_event_candidates
from .mission_package import MissionPackageError, adapt_mission_package

__all__ = [
    "MissionPackageError",
    "adapt_mission_package",
    "evaluate_document_intake",
    "evaluate_candidate_bundle",
    "link_event_candidates",
]
