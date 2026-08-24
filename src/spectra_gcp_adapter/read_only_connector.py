"""Authenticated, read-only GCP observation adapter for H06 events.

Only fixed deployment resources are queried.  The adapter never starts a
Workflow execution and never writes, copies, deletes, deploys, or changes IAM.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from typing import Any, Callable, Mapping

from .live_execution_events import (
    DEPLOYMENT_CONTRACT_VERSION,
    EVENT_CONTRACT_VERSION,
    canonical_event_sha256,
    reduce_live_execution_events,
)


CONNECTOR_CONTRACT_VERSION = "SPECTRA_READ_ONLY_GCP_CONNECTOR_RECEIPT_1.0.0"
_EXECUTION_ID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_ROLES = ("mission", "parts", "assurance")

CommandRunner = Callable[[list[str]], bytes | str]


class ConnectorFailure(ValueError):
    """Expected fail-closed connector rejection with a stable code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def subprocess_gcloud_runner(command: list[str]) -> bytes:
    """Run one already-allowlisted gcloud read command without a shell."""

    try:
        completed = subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr_raw = exc.stderr or b""
        stderr = (
            stderr_raw.decode("utf-8", errors="replace")
            if isinstance(stderr_raw, bytes)
            else str(stderr_raw)
        ).lower()
        if "reauthentication failed" in stderr or "gcloud auth login" in stderr:
            raise ConnectorFailure("GCLOUD_AUTH_REAUTH_REQUIRED") from None
        if "credentials.db" in stderr or "configuration directory may not be writable" in stderr:
            raise ConnectorFailure("GCLOUD_CONFIG_UNAVAILABLE") from None
        raise ConnectorFailure("GCLOUD_COMMAND_FAILED") from None
    return completed.stdout


def _fail(code: str, execution_id: Any = None) -> dict[str, Any]:
    return {
        "contract_version": CONNECTOR_CONTRACT_VERSION,
        "processing_status": "PROVENANCE_FAILURE",
        "connector_status": "NOT_OBSERVED",
        "observation_mode": "LIVE_API",
        "execution_id": execution_id if isinstance(execution_id, str) else None,
        "mutation_attempted": False,
        "api_transport_authentication": "NOT_ESTABLISHED",
        "event_receipt": None,
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "limitations": ["SCIENTIFIC_EVIDENCE_NOT_VALIDATED"],
        "stable_codes": [code],
    }


def _require_dict(value: Any, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConnectorFailure(code)
    return value


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ConnectorFailure(code)
    return value


def _load_json(raw: bytes | str, code: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(value)

    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(text, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        raise ConnectorFailure(code) from None


def _sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(raw)


def _anchor(value: Any) -> Mapping[str, Any]:
    anchor = _require_dict(value, "DEPLOYMENT_ANCHOR_INVALID")
    if (
        anchor.get("contract_version") != DEPLOYMENT_CONTRACT_VERSION
        or anchor.get("data_class") != "SYNTHETIC"
        or anchor.get("max_assurance_decision") != "HOLD"
    ):
        raise ConnectorFailure("DEPLOYMENT_ANCHOR_INVALID")
    for key in ("project_id", "region"):
        _require_text(anchor.get(key), "DEPLOYMENT_ANCHOR_INVALID")
    workflow = _require_dict(anchor.get("workflow"), "DEPLOYMENT_ANCHOR_INVALID")
    storage = _require_dict(anchor.get("storage"), "DEPLOYMENT_ANCHOR_INVALID")
    core = _require_dict(anchor.get("core"), "DEPLOYMENT_ANCHOR_INVALID")
    agents = _require_dict(anchor.get("agents"), "DEPLOYMENT_ANCHOR_INVALID")
    for item in (workflow.get("name"), workflow.get("revision"), storage.get("bucket"), core.get("id"), core.get("revision")):
        _require_text(item, "DEPLOYMENT_ANCHOR_INVALID")
    if set(agents) != set(_ROLES):
        raise ConnectorFailure("DEPLOYMENT_ANCHOR_INVALID")
    for role in _ROLES:
        agent = _require_dict(agents[role], "DEPLOYMENT_ANCHOR_INVALID")
        _require_text(agent.get("service"), "DEPLOYMENT_ANCHOR_INVALID")
        _require_text(agent.get("revision"), "DEPLOYMENT_ANCHOR_INVALID")
    return anchor


def build_read_only_commands(
    execution_id: str, *, trusted_deployment: Any
) -> dict[str, list[str]]:
    """Build the complete, fixed-resource gcloud command allowlist."""

    anchor = _anchor(trusted_deployment)
    if not isinstance(execution_id, str) or not _EXECUTION_ID.fullmatch(execution_id):
        raise ConnectorFailure("EXECUTION_ID_INVALID")
    project = anchor["project_id"]
    region = anchor["region"]
    workflow = anchor["workflow"]["name"]
    bucket = anchor["storage"]["bucket"]
    correlation = f"spectra-h05-{execution_id}"
    result_uri = f"gs://{bucket}/results/{execution_id}.json"
    log_filter = (
        'resource.type="cloud_run_revision" AND '
        'jsonPayload.message="spectra_h05_agent_result" AND '
        f'jsonPayload.correlation_id="{correlation}"'
    )
    return {
        "execution": [
            "gcloud", "workflows", "executions", "describe", execution_id,
            "--workflow", workflow, "--location", region, "--project", project,
            "--format=json",
        ],
        "logs": [
            "gcloud", "logging", "read", log_filter, "--project", project,
            "--limit=20", "--order=asc", "--format=json",
        ],
        "result_metadata": [
            "gcloud", "storage", "objects", "describe", result_uri,
            "--project", project, "--format=json",
        ],
        "result_body": [
            "gcloud", "storage", "cat", result_uri, "--project", project,
        ],
    }


def _run(runner: CommandRunner, command: list[str], code: str) -> bytes | str:
    try:
        return runner(list(command))
    except (OSError, subprocess.SubprocessError):
        raise ConnectorFailure(code) from None


def _parse_embedded_json(value: Any, code: str) -> Mapping[str, Any]:
    if isinstance(value, str):
        value = _load_json(value, code)
    return _require_dict(value, code)


def _event(
    *,
    sequence: int,
    occurred_at: str,
    execution: Mapping[str, Any],
    source: Mapping[str, Any],
    event_type: str,
    payload: Mapping[str, Any],
    previous: str,
) -> dict[str, Any]:
    event = {
        "contract_version": EVENT_CONTRACT_VERSION,
        "event_id": f"{execution['execution_id']}:{sequence:02d}",
        "sequence": sequence,
        "occurred_at": occurred_at,
        "execution": dict(execution),
        "source": dict(source),
        "event_type": event_type,
        "payload": dict(payload),
        "previous_event_sha256": previous,
        "event_sha256": "pending",
    }
    event["event_sha256"] = canonical_event_sha256(event)
    return event


def collect_read_only_execution(
    execution_id: str,
    *,
    trusted_deployment: Any,
    command_runner: CommandRunner = subprocess_gcloud_runner,
) -> dict[str, Any]:
    """Observe one completed execution and convert it to an H06 receipt."""

    try:
        anchor = _anchor(trusted_deployment)
        commands = build_read_only_commands(
            execution_id, trusted_deployment=anchor
        )
        execution_raw = _load_json(
            _run(command_runner, commands["execution"], "EXECUTION_READ_FAILED"),
            "EXECUTION_RESPONSE_INVALID",
        )
        observed = _require_dict(execution_raw, "EXECUTION_RESPONSE_INVALID")
        expected_name_suffix = (
            f"/locations/{anchor['region']}/workflows/"
            f"{anchor['workflow']['name']}/executions/{execution_id}"
        )
        if not str(observed.get("name", "")).endswith(expected_name_suffix):
            raise ConnectorFailure("EXECUTION_RESOURCE_MISMATCH")
        if observed.get("workflowRevisionId") != anchor["workflow"]["revision"]:
            raise ConnectorFailure("WORKFLOW_REVISION_MISMATCH")
        state = observed.get("state")
        if state != "SUCCEEDED":
            raise ConnectorFailure("EXECUTION_NOT_SUCCEEDED")
        start_time = _require_text(observed.get("startTime"), "EXECUTION_TIME_INVALID")
        end_time = _require_text(observed.get("endTime"), "EXECUTION_TIME_INVALID")
        argument = _parse_embedded_json(observed.get("argument"), "WORKFLOW_ARGUMENT_INVALID")
        workflow_result = _parse_embedded_json(observed.get("result"), "WORKFLOW_RESULT_INVALID")

        correlation = f"spectra-h05-{execution_id}"
        if workflow_result.get("execution_id") != execution_id or workflow_result.get("correlation_id") != correlation:
            raise ConnectorFailure("WORKFLOW_RESULT_IDENTITY_MISMATCH")
        result_ref = _require_dict(workflow_result.get("result_storage"), "RESULT_STORAGE_REFERENCE_INVALID")
        expected_object = f"results/{execution_id}.json"
        if (
            result_ref.get("bucket_id") != anchor["storage"]["bucket"]
            or result_ref.get("object_name") != expected_object
        ):
            raise ConnectorFailure("RESULT_STORAGE_REFERENCE_MISMATCH")
        expected_generation = _require_text(
            result_ref.get("generation"), "RESULT_STORAGE_REFERENCE_INVALID"
        )

        bounded_log_command = list(commands["logs"])
        bounded_log_command[3] = (
            bounded_log_command[3]
            + f' AND timestamp>="{start_time}" AND timestamp<="{end_time}"'
        )
        logs = _load_json(
            _run(command_runner, bounded_log_command, "LOG_READ_FAILED"),
            "LOG_RESPONSE_INVALID",
        )
        if not isinstance(logs, list):
            raise ConnectorFailure("LOG_RESPONSE_INVALID")
        metadata_before = _require_dict(
            _load_json(
                _run(command_runner, commands["result_metadata"], "RESULT_METADATA_READ_FAILED"),
                "RESULT_METADATA_INVALID",
            ),
            "RESULT_METADATA_INVALID",
        )
        body_raw = _run(command_runner, commands["result_body"], "RESULT_BODY_READ_FAILED")
        body_bytes = body_raw.encode("utf-8") if isinstance(body_raw, str) else body_raw
        metadata_after = _require_dict(
            _load_json(
                _run(command_runner, commands["result_metadata"], "RESULT_METADATA_READ_FAILED"),
                "RESULT_METADATA_INVALID",
            ),
            "RESULT_METADATA_INVALID",
        )
        generations = {str(metadata_before.get("generation")), str(metadata_after.get("generation"))}
        if generations != {expected_generation}:
            raise ConnectorFailure("RESULT_GENERATION_CHANGED_OR_MISMATCHED")
        stored = _require_dict(_load_json(body_bytes, "RESULT_BODY_INVALID"), "RESULT_BODY_INVALID")
        if workflow_result.get("result") != stored:
            raise ConnectorFailure("WORKFLOW_AND_STORAGE_RESULT_MISMATCH")
        if stored.get("run_id") != execution_id or stored.get("correlation_id") != correlation:
            raise ConnectorFailure("STORED_RESULT_IDENTITY_MISMATCH")
        if stored.get("data_class") != "SYNTHETIC" or stored.get("assurance_decision") != "HOLD":
            raise ConnectorFailure("STORED_RESULT_BOUNDARY_INVALID")

        input_storage = _require_dict(stored.get("input_storage"), "INPUT_STORAGE_BINDING_INVALID")
        input_hash = input_storage.get("expected_sha256")
        if (
            input_storage.get("project_id") != anchor["project_id"]
            or input_storage.get("bucket_id") != anchor["storage"]["bucket"]
            or not isinstance(input_hash, str)
            or not _SHA256.fullmatch(input_hash)
            or argument.get("bucket") != input_storage.get("bucket_id")
            or argument.get("input_object") != input_storage.get("object_name")
            or str(argument.get("input_generation")) != str(input_storage.get("generation"))
            or argument.get("input_sha256") != input_hash
        ):
            raise ConnectorFailure("INPUT_STORAGE_BINDING_INVALID")

        agent_results = _require_dict(stored.get("agent_results"), "AGENT_RESULTS_INVALID")
        if set(agent_results) != set(_ROLES):
            raise ConnectorFailure("AGENT_RESULTS_INCOMPLETE")
        log_by_role: dict[str, Mapping[str, Any]] = {}
        for raw_log in logs:
            log = _require_dict(raw_log, "LOG_RESPONSE_INVALID")
            payload = _require_dict(log.get("jsonPayload"), "LOG_RESPONSE_INVALID")
            labels = _require_dict(
                _require_dict(log.get("resource"), "LOG_RESPONSE_INVALID").get("labels"),
                "LOG_RESPONSE_INVALID",
            )
            role = payload.get("agent")
            if role not in _ROLES or role in log_by_role:
                raise ConnectorFailure("AGENT_LOG_SET_INVALID")
            if (
                payload.get("run_id") != execution_id
                or payload.get("correlation_id") != correlation
                or labels.get("service_name") != anchor["agents"][role]["service"]
                or labels.get("revision_name") != anchor["agents"][role]["revision"]
            ):
                raise ConnectorFailure("AGENT_LOG_IDENTITY_MISMATCH")
            log_by_role[role] = log
        if set(log_by_role) != set(_ROLES):
            raise ConnectorFailure("AGENT_LOG_SET_INVALID")

        identity = {
            "project_id": anchor["project_id"],
            "region": anchor["region"],
            "workflow_name": anchor["workflow"]["name"],
            "execution_id": execution_id,
            "correlation_id": correlation,
        }
        specs: list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]] = [
            (start_time, "WORKFLOW_STARTED", {"kind": "WORKFLOW", "id": anchor["workflow"]["name"], "revision": anchor["workflow"]["revision"]}, {"workflow_state": "RUNNING"}),
            (start_time, "STORAGE_INPUT_BOUND", {"kind": "CLOUD_STORAGE", "id": anchor["storage"]["bucket"], "revision": str(input_storage["generation"])}, {"bucket_id": input_storage["bucket_id"], "object_name": input_storage["object_name"], "generation": str(input_storage["generation"]), "sha256": input_hash}),
        ]
        mission = _require_dict(agent_results["mission"], "AGENT_RESULTS_INVALID")
        core = _require_dict(mission.get("core_result"), "CORE_RESULT_MISSING")
        for role in _ROLES:
            result = _require_dict(agent_results[role], "AGENT_RESULTS_INVALID")
            declared = result.get("response_sha256")
            content = {key: value for key, value in result.items() if key != "response_sha256"}
            if declared != _canonical_sha256(content):
                raise ConnectorFailure("AGENT_RESPONSE_SHA256_MISMATCH")
            log = log_by_role[role]
            payload = log["jsonPayload"]
            if (
                payload.get("processing_status") != result.get("processing_status")
                or payload.get("assurance_decision") != result.get("assurance_decision")
                or payload.get("stable_codes") != result.get("stable_codes")
            ):
                raise ConnectorFailure("AGENT_LOG_RESULT_MISMATCH")
            timestamp = _require_text(log.get("timestamp"), "LOG_TIMESTAMP_INVALID")
            specs.append((timestamp, "AGENT_COMPLETED", {"kind": "CLOUD_RUN_AGENT", "id": anchor["agents"][role]["service"], "revision": anchor["agents"][role]["revision"]}, {"role": role, "processing_status": result.get("processing_status"), "assurance_decision": result.get("assurance_decision"), "input_sha256": result.get("input_sha256"), "response_sha256": declared, "stable_codes": result.get("stable_codes")}))
            if role == "mission":
                if mission.get("core_result_sha256") != _canonical_sha256(core):
                    raise ConnectorFailure("CORE_RESULT_SHA256_MISMATCH")
                specs.append((timestamp, "CORE_COMPLETED", {"kind": "DETERMINISTIC_CORE", "id": anchor["core"]["id"], "revision": anchor["core"]["revision"]}, {"processing_status": core.get("processing_status"), "engineering_gate": core.get("engineering_gate"), "assurance_decision": core.get("assurance_decision"), "run_id": core.get("run_id"), "execution_input_sha256": input_hash, "core_input_sha256": core.get("input_hash"), "output_sha256": core.get("output_hash"), "result_sha256": mission.get("core_result_sha256"), "stable_codes": core.get("stable_codes", [])}))
        specs.extend([
            (end_time, "STORAGE_RESULT_BOUND", {"kind": "CLOUD_STORAGE", "id": anchor["storage"]["bucket"], "revision": expected_generation}, {"bucket_id": anchor["storage"]["bucket"], "object_name": expected_object, "generation": expected_generation, "sha256": _sha256_bytes(body_bytes)}),
            (end_time, "WORKFLOW_COMPLETED", {"kind": "WORKFLOW", "id": anchor["workflow"]["name"], "revision": anchor["workflow"]["revision"]}, {"workflow_state": "SUCCEEDED"}),
        ])
        # Logs are authoritative for Agent time. Mission/Core share one observation.
        specs[2:] = sorted(specs[2:-2], key=lambda item: (item[0], 0 if item[1] == "AGENT_COMPLETED" else 1)) + specs[-2:]
        events: list[dict[str, Any]] = []
        previous = "GENESIS"
        for sequence, (occurred_at, event_type, source, payload) in enumerate(specs):
            built = _event(sequence=sequence, occurred_at=occurred_at, execution=identity, source=source, event_type=event_type, payload=payload, previous=previous)
            events.append(built)
            previous = built["event_sha256"]
        receipt = reduce_live_execution_events(
            events, trusted_deployment=anchor, observation_mode="LIVE_API"
        )
        if receipt["processing_status"] != "VALID":
            raise ConnectorFailure("GENERATED_EVENT_STREAM_INVALID")
        return {
            "contract_version": CONNECTOR_CONTRACT_VERSION,
            "processing_status": "VALID",
            "connector_status": "OBSERVED",
            "observation_mode": "LIVE_API",
            "execution_id": execution_id,
            "mutation_attempted": False,
            "api_transport_authentication": "GCLOUD_CREDENTIAL_REQUIRED_IDENTITY_NOT_ATTESTED",
            "event_receipt": receipt,
            "assurance_decision": "HOLD",
            "used_for_decision": False,
            "limitations": ["SCIENTIFIC_EVIDENCE_NOT_VALIDATED"],
            "stable_codes": [],
        }
    except ConnectorFailure as exc:
        return _fail(exc.code, execution_id)
