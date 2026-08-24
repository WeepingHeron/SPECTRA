"""Identity-free, fail-closed receipts for bounded human review actions."""

from .review_audit import record_review_action

__all__ = ["record_review_action"]
