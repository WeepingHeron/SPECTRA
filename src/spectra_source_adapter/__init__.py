"""Fail-closed adapters for external evidence-source candidates."""

from .nasa_snapshot_gate import evaluate_nasa_snapshot
from .local_bundle_gate import evaluate_local_bundle

__all__ = ["evaluate_local_bundle", "evaluate_nasa_snapshot"]
