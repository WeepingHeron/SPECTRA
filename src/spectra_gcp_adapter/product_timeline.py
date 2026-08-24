"""Build a Product-safe live-or-snapshot GCP timeline model."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


TIMELINE_CONTRACT_VERSION = "SPECTRA_GCP_PRODUCT_TIMELINE_1.0.0"
CONNECTOR_CONTRACT_VERSION = "SPECTRA_READ_ONLY_GCP_CONNECTOR_RECEIPT_1.0.0"


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_snapshot(snapshot: Any) -> bool:
    if not isinstance(snapshot, Mapping):
        return False
    preimage = snapshot.get("snapshot_hash_preimage")
    declared = snapshot.get("snapshot_sha256")
    if not isinstance(preimage, str) or declared != _hash(preimage):
        return False
    try:
        parsed = json.loads(
            preimage,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
        _canonical(parsed)
    except (json.JSONDecodeError, TypeError, ValueError):
        return False
    body = {
        key: value
        for key, value in snapshot.items()
        if key not in {"snapshot_hash_preimage", "snapshot_sha256"}
    }
    normal = snapshot.get("executions", {}).get("normal", {})
    return (
        parsed == body
        and snapshot.get("data_class") == "SYNTHETIC"
        and snapshot.get("final_assurance") == "HOLD"
        and normal.get("workflow_state") == "SUCCEEDED"
        and normal.get("assurance_decision") == "HOLD"
    )


def _snapshot_steps(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    normal = snapshot["executions"]["normal"]
    agents = normal["agent_statuses"]
    storage = snapshot["storage"]
    return [
        {"stage": "WORKFLOW", "state": normal["workflow_state"], "occurred_at": None},
        {"stage": "STORAGE_INPUT", "state": "BOUND", "occurred_at": None, "generation": storage["normal_input_generation"]},
        {"stage": "MISSION", "state": agents["mission"], "occurred_at": None},
        {"stage": "CORE", "state": "PARITY_CONFIRMED" if snapshot["core_parity"]["canonical_hash_equal"] else "DATA_UNAVAILABLE", "occurred_at": None},
        {"stage": "PARTS", "state": agents["parts"], "occurred_at": None},
        {"stage": "ASSURANCE", "state": agents["assurance"], "occurred_at": None},
        {"stage": "STORAGE_RESULT", "state": "BOUND", "occurred_at": None, "generation": storage["normal_result_generation"]},
    ]


def _live_model(receipt: Mapping[str, Any]) -> dict[str, Any] | None:
    event = receipt.get("event_receipt")
    if (
        receipt.get("contract_version") != CONNECTOR_CONTRACT_VERSION
        or receipt.get("processing_status") != "VALID"
        or receipt.get("connector_status") != "OBSERVED"
        or receipt.get("observation_mode") != "LIVE_API"
        or receipt.get("assurance_decision") != "HOLD"
        or receipt.get("used_for_decision") is not False
        or not isinstance(event, Mapping)
        or event.get("processing_status") != "VALID"
        or event.get("stream_status") != "COMPLETE"
        or event.get("execution_status") != "SUCCEEDED"
        or event.get("workflow_success_is_business_pass") is not False
        or event.get("assurance_decision") != "HOLD"
        or not isinstance(event.get("timeline"), list)
        or not event.get("stream_sha256")
    ):
        return None
    execution = event.get("execution_ref")
    if not isinstance(execution, Mapping):
        return None
    try:
        _canonical(event["timeline"])
    except (TypeError, ValueError):
        return None
    return {
        "display_mode": "LIVE_API",
        "live_connection_status": "OBSERVED",
        "live_api_observed": True,
        "fallback_used": False,
        "timeline_kind": "AUTHENTICATED_API_OBSERVATION_IDENTITY_NOT_ATTESTED",
        "execution": dict(execution),
        "steps": event["timeline"],
        "stream_sha256": event["stream_sha256"],
        "source_codes": [],
    }


def build_product_timeline(
    live_receipt: Any, *, verified_snapshot: Any
) -> dict[str, Any]:
    """Prefer a valid live observation; otherwise label and use H05 fallback."""

    live = _live_model(live_receipt) if isinstance(live_receipt, Mapping) else None
    if live is None:
        if not _valid_snapshot(verified_snapshot):
            body = {
                "contract_version": TIMELINE_CONTRACT_VERSION,
                "processing_status": "PROVENANCE_FAILURE",
                "display_mode": "DATA_UNAVAILABLE",
                "live_connection_status": "NOT_OBSERVED",
                "live_api_observed": False,
                "fallback_used": False,
                "timeline_kind": "NONE",
                "execution": None,
                "steps": [],
                "workflow_success_is_business_pass": False,
                "assurance_decision": "HOLD",
                "used_for_decision": False,
                "source_codes": ["VERIFIED_SNAPSHOT_INVALID"],
            }
        else:
            failure_codes = []
            if isinstance(live_receipt, Mapping):
                raw_codes = live_receipt.get("stable_codes")
                if isinstance(raw_codes, list) and all(isinstance(item, str) for item in raw_codes):
                    failure_codes = sorted(set(raw_codes))
            normal = verified_snapshot["executions"]["normal"]
            body = {
                "contract_version": TIMELINE_CONTRACT_VERSION,
                "processing_status": "VALID",
                "display_mode": "VERIFIED_SNAPSHOT_FALLBACK",
                "live_connection_status": "NOT_OBSERVED",
                "live_api_observed": False,
                "fallback_used": True,
                "timeline_kind": "SUMMARY_NOT_EVENT_REPLAY",
                "execution": {
                    "project_id": verified_snapshot["project_id"],
                    "region": verified_snapshot["region"],
                    "workflow_name": verified_snapshot["workflow"]["name"],
                    "execution_id": normal["id"],
                    "correlation_id": verified_snapshot["logging"]["normal_correlation_id"],
                },
                "steps": _snapshot_steps(verified_snapshot),
                "workflow_success_is_business_pass": False,
                "assurance_decision": "HOLD",
                "used_for_decision": False,
                "snapshot_sha256": verified_snapshot["snapshot_sha256"],
                "source_codes": failure_codes or ["LIVE_RECEIPT_NOT_AVAILABLE"],
            }
    else:
        body = {
            "contract_version": TIMELINE_CONTRACT_VERSION,
            "processing_status": "VALID",
            **live,
            "workflow_success_is_business_pass": False,
            "assurance_decision": "HOLD",
            "used_for_decision": False,
        }
    preimage = _canonical(body)
    return {
        **body,
        "timeline_hash_preimage": preimage,
        "timeline_sha256": _hash(preimage),
    }
