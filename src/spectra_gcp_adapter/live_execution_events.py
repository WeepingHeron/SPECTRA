"""Validate and reduce a GCP execution event stream for Product consumers.

The reducer observes orchestration integrity.  It does not call GCP, authorize
an execution, validate scientific evidence, or turn Workflow success into a
business or assurance pass.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any, Mapping


EVENT_CONTRACT_VERSION = "SPECTRA_LIVE_EXECUTION_EVENT_1.0.0"
RECEIPT_CONTRACT_VERSION = "SPECTRA_LIVE_EXECUTION_RECEIPT_1.0.0"
DEPLOYMENT_CONTRACT_VERSION = "SPECTRA_LIVE_DEPLOYMENT_ANCHOR_1.0.0"
OBSERVATION_MODES = frozenset({"LIVE_API", "SNAPSHOT_REPLAY"})
EVENT_TYPES = frozenset(
    {
        "WORKFLOW_STARTED",
        "STORAGE_INPUT_BOUND",
        "AGENT_COMPLETED",
        "CORE_COMPLETED",
        "STORAGE_RESULT_BOUND",
        "WORKFLOW_COMPLETED",
    }
)
AGENT_ROLES = frozenset({"mission", "parts", "assurance"})
PROCESSING_STATUSES = frozenset(
    {
        "VALID",
        "INVALID_INPUT",
        "PROVENANCE_FAILURE",
        "STALE_EVIDENCE",
        "OUT_OF_MODEL_SCOPE",
    }
)

_EVENT_KEYS = frozenset(
    {
        "contract_version",
        "event_id",
        "sequence",
        "occurred_at",
        "execution",
        "source",
        "event_type",
        "payload",
        "previous_event_sha256",
        "event_sha256",
    }
)
_EXECUTION_KEYS = frozenset(
    {
        "project_id",
        "region",
        "workflow_name",
        "execution_id",
        "correlation_id",
    }
)
_SOURCE_KEYS = frozenset({"kind", "id", "revision"})
_DEPLOYMENT_KEYS = frozenset(
    {
        "contract_version",
        "project_id",
        "region",
        "workflow",
        "agents",
        "storage",
        "core",
        "data_class",
        "max_assurance_decision",
    }
)
_WORKFLOW_ANCHOR_KEYS = frozenset({"name", "revision"})
_AGENT_ANCHOR_KEYS = frozenset({"service", "revision"})
_STORAGE_ANCHOR_KEYS = frozenset({"bucket"})
_CORE_ANCHOR_KEYS = frozenset({"id", "revision"})
_WORKFLOW_PAYLOAD_KEYS = frozenset({"workflow_state"})
_STORAGE_PAYLOAD_KEYS = frozenset(
    {"bucket_id", "object_name", "generation", "sha256"}
)
_AGENT_PAYLOAD_KEYS = frozenset(
    {
        "role",
        "processing_status",
        "assurance_decision",
        "input_sha256",
        "response_sha256",
        "stable_codes",
    }
)
_CORE_PAYLOAD_KEYS = frozenset(
    {
        "processing_status",
        "engineering_gate",
        "assurance_decision",
        "run_id",
        "execution_input_sha256",
        "core_input_sha256",
        "output_sha256",
        "result_sha256",
        "stable_codes",
    }
)


def _text(value: Any, limit: int = 300) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= limit
        and "\x00" not in value
    )


def _sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _canonical_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        if value.is_integer():
            return int(value)
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical_value(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_event_sha256(event: Mapping[str, Any]) -> str:
    """Hash an event while excluding its self-referential hash field."""

    body = {key: value for key, value in event.items() if key != "event_sha256"}
    return "sha256:" + hashlib.sha256(_canonical_bytes(body)).hexdigest()


def _object(
    value: Any, allowed: frozenset[str], codes: set[str]
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if any(not isinstance(key, str) or key not in allowed for key in value):
        codes.add("INPUT_FIELD_FORBIDDEN")
    return value


def _parse_time(value: Any, codes: set[str]) -> datetime | None:
    if not _text(value, 64):
        codes.add("EVENT_TIME_INVALID")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        codes.add("EVENT_TIME_INVALID")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        codes.add("EVENT_TIMEZONE_REQUIRED")
        return None
    return parsed.astimezone(timezone.utc)


def _deployment_anchor(value: Any, codes: set[str]) -> dict[str, Any]:
    anchor = _object(value, _DEPLOYMENT_KEYS, codes)
    if anchor.get("contract_version") != DEPLOYMENT_CONTRACT_VERSION:
        codes.add("DEPLOYMENT_CONTRACT_UNSUPPORTED")
    if not _text(anchor.get("project_id")) or not _text(anchor.get("region")):
        codes.add("DEPLOYMENT_IDENTITY_INVALID")
    if anchor.get("data_class") != "SYNTHETIC":
        codes.add("DEPLOYMENT_DATA_CLASS_UNSUPPORTED")
    if anchor.get("max_assurance_decision") != "HOLD":
        codes.add("DEPLOYMENT_ASSURANCE_BOUNDARY_INVALID")

    workflow = _object(
        anchor.get("workflow"), _WORKFLOW_ANCHOR_KEYS, codes
    )
    if not _text(workflow.get("name")) or not _text(workflow.get("revision")):
        codes.add("WORKFLOW_ANCHOR_INVALID")
    storage = _object(anchor.get("storage"), _STORAGE_ANCHOR_KEYS, codes)
    if not _text(storage.get("bucket")):
        codes.add("STORAGE_ANCHOR_INVALID")
    core = _object(anchor.get("core"), _CORE_ANCHOR_KEYS, codes)
    if not _text(core.get("id")) or not _text(core.get("revision")):
        codes.add("CORE_ANCHOR_INVALID")

    agents_value = anchor.get("agents")
    if not isinstance(agents_value, Mapping) or set(agents_value) != AGENT_ROLES:
        codes.add("AGENT_ANCHORS_INVALID")
        agents_value = {}
    agents: dict[str, Mapping[str, Any]] = {}
    for role in AGENT_ROLES:
        agent = _object(agents_value.get(role), _AGENT_ANCHOR_KEYS, codes)
        agents[role] = agent
        if not _text(agent.get("service")) or not _text(agent.get("revision")):
            codes.add("AGENT_ANCHORS_INVALID")
    return {
        "project_id": anchor.get("project_id"),
        "region": anchor.get("region"),
        "workflow": workflow,
        "storage": storage,
        "core": core,
        "agents": agents,
    }


def _stable_codes(value: Any, codes: set[str]) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not _text(item, 120) for item in value)
        or value != sorted(set(value))
    ):
        codes.add("STABLE_CODES_NON_CANONICAL")
        return []
    return value


def _validate_source(
    event_type: Any,
    source: Mapping[str, Any],
    payload: Mapping[str, Any],
    anchor: Mapping[str, Any],
    codes: set[str],
) -> None:
    if event_type in {"WORKFLOW_STARTED", "WORKFLOW_COMPLETED"}:
        expected = anchor["workflow"]
        if (
            source.get("kind") != "WORKFLOW"
            or source.get("id") != expected.get("name")
            or source.get("revision") != expected.get("revision")
        ):
            codes.add("WORKFLOW_SOURCE_MISMATCH")
    elif event_type in {"STORAGE_INPUT_BOUND", "STORAGE_RESULT_BOUND"}:
        if (
            source.get("kind") != "CLOUD_STORAGE"
            or source.get("id") != anchor["storage"].get("bucket")
            or source.get("revision") != payload.get("generation")
        ):
            codes.add("STORAGE_SOURCE_MISMATCH")
    elif event_type == "AGENT_COMPLETED":
        role = payload.get("role")
        expected = anchor["agents"].get(role, {})
        if (
            source.get("kind") != "CLOUD_RUN_AGENT"
            or source.get("id") != expected.get("service")
            or source.get("revision") != expected.get("revision")
        ):
            codes.add("AGENT_SOURCE_MISMATCH")
    elif event_type == "CORE_COMPLETED":
        if (
            source.get("kind") != "DETERMINISTIC_CORE"
            or source.get("id") != anchor["core"].get("id")
            or source.get("revision") != anchor["core"].get("revision")
        ):
            codes.add("CORE_SOURCE_MISMATCH")


def _validate_payload(
    event_type: Any, payload_value: Any, codes: set[str]
) -> tuple[Mapping[str, Any], list[str]]:
    reported: list[str] = []
    if event_type in {"WORKFLOW_STARTED", "WORKFLOW_COMPLETED"}:
        payload = _object(payload_value, _WORKFLOW_PAYLOAD_KEYS, codes)
        allowed = (
            {"RUNNING"}
            if event_type == "WORKFLOW_STARTED"
            else {"SUCCEEDED", "FAILED", "CANCELLED"}
        )
        if payload.get("workflow_state") not in allowed:
            codes.add("WORKFLOW_STATE_INVALID")
        return payload, reported
    if event_type in {"STORAGE_INPUT_BOUND", "STORAGE_RESULT_BOUND"}:
        payload = _object(payload_value, _STORAGE_PAYLOAD_KEYS, codes)
        if not all(
            _text(payload.get(field))
            for field in ("bucket_id", "object_name", "generation")
        ) or not _sha256(payload.get("sha256")):
            codes.add("STORAGE_BINDING_INVALID")
        return payload, reported
    if event_type == "AGENT_COMPLETED":
        payload = _object(payload_value, _AGENT_PAYLOAD_KEYS, codes)
        if payload.get("role") not in AGENT_ROLES:
            codes.add("AGENT_ROLE_INVALID")
        if payload.get("processing_status") not in PROCESSING_STATUSES:
            codes.add("PROCESSING_STATUS_INVALID")
        if payload.get("assurance_decision") != "HOLD":
            codes.add("SYNTHETIC_ASSURANCE_PROMOTION_REJECTED")
        if not _sha256(payload.get("input_sha256")) or not _sha256(
            payload.get("response_sha256")
        ):
            codes.add("AGENT_HASH_BINDING_INVALID")
        reported = _stable_codes(payload.get("stable_codes"), codes)
        return payload, reported
    if event_type == "CORE_COMPLETED":
        payload = _object(payload_value, _CORE_PAYLOAD_KEYS, codes)
        if payload.get("processing_status") not in PROCESSING_STATUSES:
            codes.add("PROCESSING_STATUS_INVALID")
        if payload.get("engineering_gate") not in {
            "PASS",
            "FAIL",
            "NOT_EVALUATED",
        }:
            codes.add("ENGINEERING_GATE_INVALID")
        if payload.get("assurance_decision") != "HOLD":
            codes.add("SYNTHETIC_ASSURANCE_PROMOTION_REJECTED")
        if not _text(payload.get("run_id")) or not all(
            _sha256(payload.get(field))
            for field in (
                "execution_input_sha256",
                "core_input_sha256",
                "output_sha256",
                "result_sha256",
            )
        ):
            codes.add("CORE_HASH_BINDING_INVALID")
        reported = _stable_codes(payload.get("stable_codes"), codes)
        return payload, reported
    codes.add("EVENT_TYPE_INVALID")
    return {}, reported


def _timeline_state(event_type: str, payload: Mapping[str, Any]) -> str:
    if event_type in {"WORKFLOW_STARTED", "WORKFLOW_COMPLETED"}:
        return str(payload.get("workflow_state", "INVALID"))
    if event_type in {"STORAGE_INPUT_BOUND", "STORAGE_RESULT_BOUND"}:
        return "BOUND"
    return str(payload.get("processing_status", "INVALID"))


def reduce_live_execution_events(
    events: Any,
    *,
    trusted_deployment: Any,
    observation_mode: Any,
) -> dict[str, Any]:
    """Reduce a hash-chained GCP event list to a Product-safe receipt."""

    codes: set[str] = set()
    if observation_mode not in OBSERVATION_MODES:
        codes.add("OBSERVATION_MODE_INVALID")
    anchor = _deployment_anchor(trusted_deployment, codes)
    if not isinstance(events, list) or not events or len(events) > 100:
        codes.add("EVENT_STREAM_SHAPE_INVALID")
        events = []

    seen_ids: set[str] = set()
    event_counts: dict[str, int] = {}
    event_positions: dict[str, list[int]] = {}
    agent_roles: set[str] = set()
    agent_positions: dict[str, int] = {}
    reported_codes: set[str] = set()
    timeline: list[dict[str, Any]] = []
    identity: Mapping[str, Any] | None = None
    input_sha256: str | None = None
    previous_hash = "GENESIS"
    previous_time: datetime | None = None
    terminal_state: str | None = None

    for index, raw_event in enumerate(events):
        event = _object(raw_event, _EVENT_KEYS, codes)
        if event.get("contract_version") != EVENT_CONTRACT_VERSION:
            codes.add("EVENT_CONTRACT_UNSUPPORTED")
        event_id = event.get("event_id")
        if not _text(event_id) or event_id in seen_ids:
            codes.add("EVENT_ID_INVALID_OR_DUPLICATE")
        else:
            seen_ids.add(event_id)
        sequence = event.get("sequence")
        if (
            not isinstance(sequence, int)
            or isinstance(sequence, bool)
            or sequence != index
        ):
            codes.add("EVENT_SEQUENCE_INVALID")
        occurred = _parse_time(event.get("occurred_at"), codes)
        if occurred is not None and previous_time is not None and occurred < previous_time:
            codes.add("EVENT_TIME_REGRESSION")
        if occurred is not None:
            previous_time = occurred

        execution = _object(event.get("execution"), _EXECUTION_KEYS, codes)
        if not all(_text(execution.get(field)) for field in _EXECUTION_KEYS):
            codes.add("EXECUTION_IDENTITY_INVALID")
        elif (
            execution.get("project_id") != anchor.get("project_id")
            or execution.get("region") != anchor.get("region")
            or execution.get("workflow_name") != anchor["workflow"].get("name")
        ):
            codes.add("DEPLOYMENT_EXECUTION_MISMATCH")
        if identity is None:
            identity = execution
        elif dict(execution) != dict(identity):
            codes.add("MIXED_EXECUTION_STREAM")

        if event.get("previous_event_sha256") != previous_hash:
            codes.add("EVENT_CHAIN_PREDECESSOR_MISMATCH")
        try:
            calculated_hash = canonical_event_sha256(event)
        except (TypeError, ValueError):
            calculated_hash = None
            codes.add("EVENT_CANONICALIZATION_FAILED")
        if calculated_hash is None or event.get("event_sha256") != calculated_hash:
            codes.add("EVENT_SHA256_MISMATCH")
        else:
            previous_hash = calculated_hash

        event_type = event.get("event_type")
        if event_type not in EVENT_TYPES:
            codes.add("EVENT_TYPE_INVALID")
            event_type = "INVALID"
        source = _object(event.get("source"), _SOURCE_KEYS, codes)
        payload, event_reported_codes = _validate_payload(
            event_type, event.get("payload"), codes
        )
        reported_codes.update(event_reported_codes)
        _validate_source(event_type, source, payload, anchor, codes)
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        event_positions.setdefault(event_type, []).append(index)

        if event_type == "STORAGE_INPUT_BOUND":
            input_sha256 = payload.get("sha256")
        elif event_type in {"AGENT_COMPLETED", "CORE_COMPLETED"}:
            bound_input = (
                payload.get("execution_input_sha256")
                if event_type == "CORE_COMPLETED"
                else payload.get("input_sha256")
            )
            if input_sha256 is None or bound_input != input_sha256:
                codes.add("EXECUTION_INPUT_HASH_MISMATCH")
            if event_type == "AGENT_COMPLETED" and payload.get("role") in AGENT_ROLES:
                role = str(payload["role"])
                if role in agent_roles:
                    codes.add("AGENT_EVENT_DUPLICATE")
                agent_roles.add(role)
                agent_positions[role] = index
        elif event_type == "WORKFLOW_COMPLETED":
            terminal_state = payload.get("workflow_state")

        timeline.append(
            {
                "sequence": sequence,
                "occurred_at": event.get("occurred_at"),
                "event_type": event_type,
                "source_kind": source.get("kind"),
                "source_id": source.get("id"),
                "state": _timeline_state(event_type, payload),
            }
        )

    singleton_types = EVENT_TYPES - {"AGENT_COMPLETED"}
    if any(event_counts.get(event_type, 0) > 1 for event_type in singleton_types):
        codes.add("EVENT_CARDINALITY_INVALID")
    if terminal_state == "SUCCEEDED":
        required = EVENT_TYPES - {"AGENT_COMPLETED"}
        if any(event_counts.get(event_type) != 1 for event_type in required):
            codes.add("TERMINAL_EVENT_SET_INCOMPLETE")
        if agent_roles != AGENT_ROLES:
            codes.add("TERMINAL_AGENT_SET_INCOMPLETE")
    if event_counts.get("WORKFLOW_STARTED", 0) != 1:
        codes.add("WORKFLOW_START_MISSING")
    if events:
        first_type = timeline[0]["event_type"]
        last_type = timeline[-1]["event_type"]
        if first_type != "WORKFLOW_STARTED":
            codes.add("EVENT_CAUSAL_ORDER_INVALID")
        if terminal_state is not None and last_type != "WORKFLOW_COMPLETED":
            codes.add("EVENT_CAUSAL_ORDER_INVALID")

    def first_position(event_type: str) -> int | None:
        positions = event_positions.get(event_type, [])
        return positions[0] if positions else None

    input_position = first_position("STORAGE_INPUT_BOUND")
    core_position = first_position("CORE_COMPLETED")
    result_position = first_position("STORAGE_RESULT_BOUND")
    terminal_position = first_position("WORKFLOW_COMPLETED")
    processing_positions = [
        *agent_positions.values(),
        *([] if core_position is None else [core_position]),
    ]
    if input_position is not None and any(
        position <= input_position for position in processing_positions
    ):
        codes.add("EVENT_CAUSAL_ORDER_INVALID")
    assurance_position = agent_positions.get("assurance")
    prerequisite_positions = [
        agent_positions.get("mission"),
        agent_positions.get("parts"),
        core_position,
    ]
    if assurance_position is not None and any(
        position is not None and position >= assurance_position
        for position in prerequisite_positions
    ):
        codes.add("EVENT_CAUSAL_ORDER_INVALID")
    if result_position is not None and any(
        position is not None and position >= result_position
        for position in (core_position, assurance_position)
    ):
        codes.add("EVENT_CAUSAL_ORDER_INVALID")
    if (
        terminal_position is not None
        and result_position is not None
        and result_position >= terminal_position
    ):
        codes.add("EVENT_CAUSAL_ORDER_INVALID")

    processing_status = "INVALID_INPUT" if codes else "VALID"
    if codes:
        stream_status = "INVALID"
        execution_status = "NOT_EVALUATED"
    elif terminal_state is None:
        stream_status = "IN_PROGRESS"
        execution_status = "RUNNING"
    else:
        stream_status = "COMPLETE"
        execution_status = terminal_state

    return {
        "contract_version": RECEIPT_CONTRACT_VERSION,
        "processing_status": processing_status,
        "observation_mode": (
            observation_mode if observation_mode in OBSERVATION_MODES else None
        ),
        "stream_status": stream_status,
        "execution_status": execution_status,
        "workflow_succeeded": terminal_state == "SUCCEEDED" and not codes,
        "workflow_success_is_business_pass": False,
        "event_chain_authenticity": "INTEGRITY_ONLY_NOT_AUTHENTICATED",
        "evidence_status": "SYNTHETIC_ONLY" if not codes else "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "execution_ref": dict(identity) if identity is not None and not codes else None,
        "timeline": timeline if not codes else [],
        "stream_sha256": previous_hash if events and not codes else None,
        "reported_codes": sorted(reported_codes),
        "limitations": [
            "GCP_API_NOT_CALLED_BY_REDUCER",
            "LIVE_TRANSPORT_AUTHENTICITY_NOT_ESTABLISHED",
            "SCIENTIFIC_EVIDENCE_NOT_VALIDATED",
        ],
        "stable_codes": sorted(codes),
    }
