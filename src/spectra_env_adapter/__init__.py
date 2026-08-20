"""Fail-closed intake and parsing for the first environment evidence path."""


def assess_import(*args, **kwargs):
    """Load the intake gate lazily so ``python -m ...gate`` stays warning-free."""

    from .gate import assess_import as _assess_import

    return _assess_import(*args, **kwargs)


from .spenvis_shieldose2 import (
    DoseParseError,
    normalize_tid_candidates,
    parse_shieldose2_file,
    parse_shieldose2_text,
)

__all__ = [
    "DoseParseError",
    "assess_import",
    "normalize_tid_candidates",
    "parse_shieldose2_file",
    "parse_shieldose2_text",
]
