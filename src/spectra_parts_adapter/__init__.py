"""Fail-closed adapters for Product-facing parts-evidence receipts."""


def assess_exact_part_readiness(*args, **kwargs):
    """Load the adapter lazily so module CLI execution stays warning-free."""

    from .exact_part_readiness import assess_exact_part_readiness as _assess

    return _assess(*args, **kwargs)


def assess_reference_comparison(*args, **kwargs):
    """Load the published-reference comparison gate lazily."""

    from .reference_comparison import assess_reference_comparison as _assess

    return _assess(*args, **kwargs)


def evaluate_published_artifact(*args, **kwargs):
    """Load the published-artifact source gate lazily."""

    from .published_artifact_gate import evaluate_published_artifact as _evaluate

    return _evaluate(*args, **kwargs)


def assess_published_reference_package(*args, **kwargs):
    """Load the composed published-reference package gate lazily."""

    from .published_reference_package import (
        assess_published_reference_package as _assess,
    )

    return _assess(*args, **kwargs)


__all__ = [
    "assess_exact_part_readiness",
    "assess_reference_comparison",
    "assess_published_reference_package",
    "evaluate_published_artifact",
]
