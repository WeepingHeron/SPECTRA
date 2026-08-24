"""Canonical JSON byte and SHA-256 contract for the synthetic H05 path."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def canonical_value(value: Any) -> Any:
    """Normalize only JSON numeric representations changed by Workflows."""
    if isinstance(value, dict):
        return {key: canonical_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical JSON forbids non-finite numbers")
        if value.is_integer():
            return int(value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_uri_from_bytes(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_uri_from_bytes(canonical_json_bytes(value))
