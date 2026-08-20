"""Runtime JSON Schema validation for simulation inputs."""

from __future__ import annotations

import json
import importlib.util
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
STAGE1_VALIDATOR = ROOT / "tests" / "schema" / "validate_contracts.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def packet_validator() -> Draft202012Validator:
    schemas = [_load(path) for path in sorted(SCHEMA_DIR.glob("*.schema.json"))]
    registry = Registry().with_resources(
        [(schema["$id"], Resource.from_contents(schema)) for schema in schemas]
    )
    packet_schema = _load(SCHEMA_DIR / "evidence-packet.schema.json")
    return Draft202012Validator(
        packet_schema, registry=registry, format_checker=FormatChecker()
    )


def packet_schema_errors(packet: dict) -> list[str]:
    return [
        f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in packet_validator().iter_errors(packet)
    ]


@lru_cache(maxsize=1)
def _stage1_contract_module():
    """Load the integrated Stage 1 contract implementation without duplicating it."""
    spec = importlib.util.spec_from_file_location("spectra_stage1_contract", STAGE1_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Stage 1 semantic validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def packet_semantic_errors(packet: dict) -> list[str]:
    try:
        return sorted(_stage1_contract_module().semantic_codes(packet))
    except Exception as exc:  # fail closed if the canonical semantic gate cannot run
        return [f"SEMANTIC_VALIDATOR_FAILURE: {exc}"]


def packet_contract_errors(packet: dict) -> list[str]:
    schema_errors = packet_schema_errors(packet)
    if schema_errors:
        return schema_errors
    return [f"SEMANTIC: {code}" for code in packet_semantic_errors(packet)]


def load_contract_fixture(path: Path) -> dict:
    """Resolve a Stage 1 fixture and its declared base/operations chain."""
    return _stage1_contract_module().load_fixture(path.resolve())
