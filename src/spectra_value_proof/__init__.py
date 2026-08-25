"""Fail-closed review-impact classification for SPECTRA value proofs."""

from .review_impact import CONTRACT_VERSION, classify_review_impact, source_sha256

__all__ = ["CONTRACT_VERSION", "classify_review_impact", "source_sha256"]
