"""Fail-closed adapters for external evidence-source candidates."""

from .nasa_snapshot_gate import evaluate_nasa_snapshot

__all__ = ["evaluate_nasa_snapshot"]
