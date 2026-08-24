"""Fail-closed adapters for Product-facing parts-evidence receipts."""


def assess_exact_part_readiness(*args, **kwargs):
    """Load the adapter lazily so module CLI execution stays warning-free."""

    from .exact_part_readiness import assess_exact_part_readiness as _assess

    return _assess(*args, **kwargs)

__all__ = ["assess_exact_part_readiness"]
