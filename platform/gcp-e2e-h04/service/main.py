#!/usr/bin/env python3
"""Synthetic-only SPECTRA H05 role service for Cloud Run."""

from __future__ import annotations

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


SERVICE_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = SERVICE_DIR.parent
RUNTIME_ROOT = (
    BUNDLE_ROOT
    if (BUNDLE_ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json").is_file()
    else Path(__file__).resolve().parents[3]
)
for import_root in (BUNDLE_ROOT, RUNTIME_ROOT / "src"):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from shared.integrity import canonical_json_bytes, canonical_sha256  # noqa: E402
from spectra_sim.mvp_engine import MvpDecisionError, run_mvp_decision  # noqa: E402


ALLOWED_ROLES = {"mission", "parts", "assurance"}
REQUIRED_MISSION_FIELDS = (
    "mission_id",
    "model_name",
    "model_version",
    "source_ref",
    "input_hash",
    "core_case_id",
)
REQUIRED_PART_FIELDS = (
    "artifact_id",
    "manufacturer",
    "exact_orderable_part_number",
    "process",
    "die_revision",
    "lot_code",
    "evidence_hash",
    "expected_evidence_hash",
    "expected_identity_sha256",
)
PART_IDENTITY_FIELDS = (
    "manufacturer",
    "exact_orderable_part_number",
    "process",
    "die_revision",
    "lot_code",
)


def canonical_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value)


def sha256_uri(value: Any) -> str:
    return canonical_sha256(value)


def _base(envelope: dict[str, Any], role: str, started: float) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "run_id": envelope.get("run_id", "invalid-run"),
        "correlation_id": envelope.get("correlation_id", "invalid-correlation"),
        "agent": role,
        "data_class": "SYNTHETIC",
        "assurance_decision": "HOLD",
        "latency_ms": max(0, round((time.monotonic() - started) * 1000)),
    }


def _finish(result: dict[str, Any]) -> dict[str, Any]:
    result["stable_codes"] = sorted(set(result.get("stable_codes", [])))
    result["response_sha256"] = sha256_uri(result)
    return result


def _response_hash_valid(result: dict[str, Any]) -> bool:
    declared = result.get("response_sha256")
    if not isinstance(declared, str):
        return False
    content = {key: value for key, value in result.items() if key != "response_sha256"}
    return declared == sha256_uri(content)


def _failure(
    envelope: dict[str, Any], role: str, started: float, code: str, message: str
) -> dict[str, Any]:
    result = _base(envelope, role, started)
    result.update(
        {
            "processing_status": "INVALID_INPUT",
            "engineering_gate": "NOT_EVALUATED",
            "stable_codes": [code],
            "message": message,
        }
    )
    input_storage = envelope.get("input_storage")
    if isinstance(input_storage, dict) and isinstance(input_storage.get("expected_sha256"), str):
        result["input_sha256"] = input_storage["expected_sha256"]
    return _finish(result)


def _valid_envelope(envelope: Any) -> str | None:
    if not isinstance(envelope, dict):
        return "request must be a JSON object"
    for field in ("run_id", "correlation_id"):
        if not isinstance(envelope.get(field), str) or not envelope[field]:
            return f"{field} must be a non-empty string"
    storage = envelope.get("input_storage")
    if not isinstance(storage, dict):
        return "input_storage must be an object"
    for field in (
        "artifact_id", "project_id", "bucket_id", "object_name", "generation",
        "metadata_sha256", "expected_sha256",
    ):
        if not isinstance(storage.get(field), str) or not storage[field]:
            return f"input_storage.{field} must be a non-empty string"
    if not isinstance(envelope.get("fixture"), dict):
        return "fixture must be an object"
    return None


def _body_integrity_failure(
    envelope: dict[str, Any], role: str, started: float
) -> dict[str, Any] | None:
    storage = envelope["input_storage"]
    try:
        body_sha256 = canonical_sha256(envelope["fixture"])
    except (TypeError, ValueError) as exc:
        return _failure(envelope, role, started, "INPUT_CANONICALIZATION_FAILED", str(exc))
    if storage["metadata_sha256"] != storage["expected_sha256"]:
        return _failure(
            envelope, role, started, "INPUT_SHA256_METADATA_MISMATCH",
            "object metadata SHA-256 does not match the expected receipt",
        )
    if body_sha256 != storage["expected_sha256"]:
        result = _failure(
            envelope, role, started, "INPUT_BODY_SHA256_MISMATCH",
            "downloaded canonical body SHA-256 does not match metadata and expected receipt",
        )
        result["body_sha256"] = body_sha256
        result["body_hash_verified"] = False
        result["response_sha256"] = sha256_uri(
            {key: value for key, value in result.items() if key != "response_sha256"}
        )
        return result
    return None


def _load_core_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    case_path = RUNTIME_ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json"
    model_path = RUNTIME_ROOT / "simulation/config/synthetic-model.json"
    return (
        json.loads(case_path.read_text(encoding="utf-8")),
        json.loads(model_path.read_text(encoding="utf-8")),
    )


def mission_agent(envelope: dict[str, Any], started: float) -> dict[str, Any]:
    fixture = envelope["fixture"]
    mission = fixture.get("mission")
    if fixture.get("data_class") != "SYNTHETIC":
        return _failure(envelope, "mission", started, "NON_SYNTHETIC_INPUT_FORBIDDEN", "H04 accepts SYNTHETIC fixtures only")
    if not isinstance(mission, dict) or any(
        not isinstance(mission.get(field), str) or not mission[field]
        for field in REQUIRED_MISSION_FIELDS
    ):
        return _failure(envelope, "mission", started, "MISSION_PROVENANCE_INVALID", "mission/model provenance is incomplete")
    try:
        case, model = _load_core_inputs()
    except (OSError, json.JSONDecodeError) as exc:
        return _failure(envelope, "mission", started, "PRODUCTION_CORE_INPUT_UNAVAILABLE", str(exc))
    if mission["core_case_id"] != case.get("case_id"):
        return _failure(envelope, "mission", started, "PRODUCTION_CORE_CASE_MISMATCH", "fixture is not bound to the staged production Core case")
    if mission["model_name"] != model.get("model_name") or mission["model_version"] != model.get("model_version"):
        return _failure(envelope, "mission", started, "PRODUCTION_CORE_MODEL_MISMATCH", "fixture model identity does not match the staged model")
    try:
        core_result = run_mvp_decision(case, model)
    except MvpDecisionError as exc:
        return _failure(envelope, "mission", started, exc.code, exc.message)
    result = _base(envelope, "mission", started)
    result.update(
        {
            "processing_status": "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "stable_codes": ["PRODUCTION_CORE_BOUND", "REAL_ENVIRONMENT_EVIDENCE_MISSING"],
            "input_sha256": envelope["input_storage"]["expected_sha256"],
            "body_sha256": envelope["input_storage"]["expected_sha256"],
            "body_hash_verified": True,
            "core_result": core_result,
            "core_result_sha256": sha256_uri(core_result),
        }
    )
    return _finish(result)


def parts_agent(envelope: dict[str, Any], started: float) -> dict[str, Any]:
    fixture = envelope["fixture"]
    part = fixture.get("part_evidence")
    if fixture.get("data_class") != "SYNTHETIC":
        return _failure(envelope, "parts", started, "NON_SYNTHETIC_INPUT_FORBIDDEN", "H04 accepts SYNTHETIC fixtures only")
    if not isinstance(part, dict) or any(
        not isinstance(part.get(field), str) or not part[field]
        for field in REQUIRED_PART_FIELDS
    ):
        return _failure(envelope, "parts", started, "EXACT_PART_IDENTITY_INVALID", "exact-part identity or evidence locator is incomplete")
    event_types = part.get("event_types")
    if not isinstance(event_types, list) or not event_types or any(
        not isinstance(item, str) for item in event_types
    ):
        return _failure(envelope, "parts", started, "EVIDENCE_EVENT_COVERAGE_INVALID", "event_types must be a non-empty string list")
    if part["evidence_hash"] != part["expected_evidence_hash"]:
        return _failure(envelope, "parts", started, "PART_EVIDENCE_HASH_MISMATCH", "evidence hash does not match the declared exact-part evidence")
    if part.get("rights_status") != "SYNTHETIC_FIXTURE_ONLY":
        return _failure(envelope, "parts", started, "PART_EVIDENCE_RIGHTS_INVALID", "H04 requires synthetic fixture rights status")

    identity = {field: part[field] for field in PART_IDENTITY_FIELDS}
    if sha256_uri(identity) != part["expected_identity_sha256"]:
        return _failure(
            envelope, "parts", started, "PART_IDENTITY_MISMATCH",
            "observed exact-part identity does not match the fixed expected identity",
        )
    result = _base(envelope, "parts", started)
    result.update(
        {
            "processing_status": "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "stable_codes": ["EXACT_PART_IDENTITY_MATCHED", "SYNTHETIC_EVIDENCE_ONLY", "REAL_PART_TEST_EVIDENCE_MISSING"],
            "input_sha256": envelope["input_storage"]["expected_sha256"],
            "identity_sha256": sha256_uri(identity),
            "evidence_hash": part["evidence_hash"],
            "event_types": sorted(set(event_types)),
        }
    )
    return _finish(result)


def assurance_agent(envelope: dict[str, Any], started: float) -> dict[str, Any]:
    prior = envelope.get("prior_results")
    if not isinstance(prior, dict):
        return _failure(envelope, "assurance", started, "PRIOR_RESULTS_INVALID", "prior_results must be an object")
    mission = prior.get("mission")
    parts = prior.get("parts")
    if not isinstance(mission, dict) or not isinstance(parts, dict):
        return _failure(envelope, "assurance", started, "PRIOR_RESULTS_MISSING", "mission and parts results are required")

    expected_hash = envelope["input_storage"]["expected_sha256"]
    codes = ["SYNTHETIC_ONLY"]
    if mission.get("input_sha256") != expected_hash or parts.get("input_sha256") != expected_hash:
        codes.append("AGENT_INPUT_HASH_MISMATCH")
    if mission.get("processing_status") != "VALID":
        codes.append("MISSION_AGENT_NOT_VALID")
        if isinstance(mission.get("stable_codes"), list):
            codes.extend(code for code in mission["stable_codes"] if isinstance(code, str))
    if parts.get("processing_status") != "VALID":
        codes.append("PARTS_AGENT_NOT_VALID")
        if isinstance(parts.get("stable_codes"), list):
            codes.extend(code for code in parts["stable_codes"] if isinstance(code, str))
    if mission.get("data_class") != "SYNTHETIC" or parts.get("data_class") != "SYNTHETIC":
        codes.append("AGENT_DATA_CLASS_MISMATCH")
    if not _response_hash_valid(mission) or not _response_hash_valid(parts):
        codes.append("AGENT_RESPONSE_HASH_MISMATCH")

    blocked = len(codes) > 1
    result = _base(envelope, "assurance", started)
    result.update(
        {
            "processing_status": "INVALID_INPUT" if blocked else "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "stable_codes": codes,
            "input_sha256": expected_hash,
            "reviewed_response_hashes": {
                "mission": mission.get("response_sha256"),
                "parts": parts.get("response_sha256"),
            },
            "message": "fail-closed independent review" if blocked else "synthetic chain is internally consistent; real assurance remains withheld",
        }
    )
    return _finish(result)


def evaluate(envelope: Any, role: str | None = None) -> dict[str, Any]:
    started = time.monotonic()
    selected_role = role or os.environ.get("ROLE", "")
    if selected_role not in ALLOWED_ROLES:
        return _failure(envelope if isinstance(envelope, dict) else {}, "unknown", started, "AGENT_ROLE_INVALID", "ROLE must be mission, parts, or assurance")
    error = _valid_envelope(envelope)
    if error:
        return _failure(envelope if isinstance(envelope, dict) else {}, selected_role, started, "AGENT_REQUEST_INVALID", error)
    integrity_failure = _body_integrity_failure(envelope, selected_role, started)
    if integrity_failure is not None:
        return integrity_failure
    if selected_role == "mission":
        return mission_agent(envelope, started)
    if selected_role == "parts":
        return parts_agent(envelope, started)
    return assurance_agent(envelope, started)


class Handler(BaseHTTPRequestHandler):
    server_version = "SPECTRA-H05"

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = canonical_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send(200, {"status": "ok", "role": os.environ.get("ROLE", "unset")})
        else:
            self._send(404, {"status": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/", "/evaluate"}:
            self._send(404, {"status": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                raise ValueError("request body size is invalid")
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError) as exc:
            result = _failure({}, os.environ.get("ROLE", "unknown"), time.monotonic(), "AGENT_REQUEST_INVALID", str(exc))
            self._send(400, result)
            return
        result = evaluate(payload)
        print(json.dumps({
            "severity": "INFO",
            "message": "spectra_h05_agent_result",
            "run_id": result.get("run_id"),
            "correlation_id": result.get("correlation_id"),
            "agent": result.get("agent"),
            "processing_status": result.get("processing_status"),
            "assurance_decision": result.get("assurance_decision"),
            "stable_codes": result.get("stable_codes"),
            "body_hash_verified": result.get("body_hash_verified"),
            "core_run_id": (result.get("core_result") or {}).get("run_id") if isinstance(result.get("core_result"), dict) else None,
            "latency_ms": result.get("latency_ms"),
        }), flush=True)
        self._send(200, result)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
