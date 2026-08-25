"""Deterministic, fail-closed document intake adapters."""

from .candidate_intake import evaluate_document_intake
from .candidate_bundle import evaluate_candidate_bundle
from .evidence_candidates import link_event_candidates
from .mission_package import MissionPackageError, adapt_mission_package
from .review_packet import build_candidate_review_packet

__all__ = [
    "MissionPackageError",
    "adapt_mission_package",
    "evaluate_document_intake",
    "evaluate_candidate_bundle",
    "build_candidate_review_packet",
    "link_event_candidates",
]
