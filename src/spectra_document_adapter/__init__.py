"""Deterministic, fail-closed document intake adapters."""

from .candidate_intake import evaluate_document_intake
from .mission_package import MissionPackageError, adapt_mission_package

__all__ = ["MissionPackageError", "adapt_mission_package", "evaluate_document_intake"]
