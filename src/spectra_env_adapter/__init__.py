"""Fail-closed intake and parsing for the first environment evidence path."""


def assess_import(*args, **kwargs):
    """Load the intake gate lazily so ``python -m ...gate`` stays warning-free."""

    from .gate import assess_import as _assess_import

    return _assess_import(*args, **kwargs)


def assess_issuance(*args, **kwargs):
    """Load the issuance gate lazily so module CLI execution stays warning-free."""

    from .issuance_gate import assess_issuance as _assess_issuance

    return _assess_issuance(*args, **kwargs)


def freeze_deployment_trust_store_snapshot(*args, **kwargs):
    """Freeze deployment configuration before passing it to issuance."""

    from .issuance_gate import freeze_deployment_trust_store_snapshot as _freeze

    return _freeze(*args, **kwargs)


from .spenvis_shieldose2 import (
    DoseParseError,
    normalize_tid_candidates,
    parse_shieldose2_file,
    parse_shieldose2_text,
)

__all__ = [
    "DoseParseError",
    "assess_import",
    "assess_issuance",
    "freeze_deployment_trust_store_snapshot",
    "normalize_tid_candidates",
    "parse_shieldose2_file",
    "parse_shieldose2_text",
]
