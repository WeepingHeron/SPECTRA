"""Small, explicit unit conversions supported by the Stage 2 baseline."""

import math

SECONDS_PER_DAY = 86_400.0
SYNTHETIC_DAYS_PER_YEAR = 365.0


class UnitError(ValueError):
    """Raised when the synthetic baseline cannot safely convert a unit."""


def duration_years(value: float, unit: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise UnitError("duration must be finite and greater than zero")
    if unit == "year":
        return value
    if unit == "day":
        return value / SYNTHETIC_DAYS_PER_YEAR
    if unit == "s":
        return value / (SYNTHETIC_DAYS_PER_YEAR * SECONDS_PER_DAY)
    raise UnitError(f"unsupported duration unit: {unit}")


def duration_seconds(value: float, unit: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise UnitError("duration must be finite and greater than zero")
    if unit == "s":
        return value
    if unit == "day":
        return value * SECONDS_PER_DAY
    if unit == "year":
        return value * SYNTHETIC_DAYS_PER_YEAR * SECONDS_PER_DAY
    raise UnitError(f"unsupported duration unit: {unit}")


def tid_krad_si(value: float, unit: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise UnitError("TID must be finite and non-negative")
    if unit == "krad(Si)":
        return value
    if unit == "rad(Si)":
        return value / 1_000.0
    if unit == "Gy(Si)":
        return value / 10.0
    raise UnitError(f"unsupported TID unit: {unit}")
