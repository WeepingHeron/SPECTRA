"""Build a deterministic, review-only packet from a three-document bundle."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


CONTRACT_VERSION = "CANDIDATE_REVIEW_PACKET_1.0.0"


def _span(value: Any) -> dict[str, int] | None:
    if not isinstance(value, Mapping):
        return None
    start, end = value.get("start"), value.get("end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start:
        return None
    return {"start": start, "end": end}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def _event_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        linked: list[dict[str, Any]] = []
        for candidate in item.get("linked_candidates", []):
            if not isinstance(candidate, Mapping):
                continue
            linked.append(
                {
                    "field": str(candidate.get("field", "")),
                    "value": str(candidate.get("value", "")),
                    "unit": candidate.get("unit"),
                    "source_span": _span(candidate.get("source_span")),
                    "link_basis": str(candidate.get("link_basis", "")),
                }
            )
        rows.append(
            {
                "event_type": str(item.get("event_type", "")),
                "status": str(item.get("status", "")),
                "mention_source_span": _span(item.get("mention_source_span")),
                "required_fields": _strings(item.get("required_fields")),
                "present_fields": _strings(item.get("present_fields")),
                "missing_fields": _strings(item.get("missing_fields")),
                "linked_candidates": linked,
            }
        )
    return rows


def build_candidate_review_packet(
    bundle_result: Mapping[str, Any], summary: Mapping[str, Any]
) -> dict[str, Any]:
    """Return an allowlisted packet that cannot be mistaken for approval evidence."""

    if not isinstance(bundle_result, Mapping) or not isinstance(summary, Mapping):
        raise ValueError("REVIEW_PACKET_INPUT_INVALID")
    questions = bundle_result.get("questions")
    if not isinstance(questions, Mapping):
        raise ValueError("REVIEW_PACKET_QUESTIONS_INVALID")

    documents: list[dict[str, Any]] = []
    for item in bundle_result.get("document_receipts", []):
        if not isinstance(item, Mapping):
            continue
        documents.append(
            {
                "role": str(item.get("role", "")),
                "content_sha256": str(item.get("content_sha256", "")),
                "processing_status": str(item.get("processing_status", "")),
                "candidate_count": int(item.get("candidate_count", 0)),
            }
        )

    identity = questions.get("part_test_identity", {})
    identity_fields: list[dict[str, Any]] = []
    if isinstance(identity, Mapping):
        for item in identity.get("fields", []):
            if not isinstance(item, Mapping):
                continue
            identity_fields.append(
                {
                    "field": str(item.get("field", "")),
                    "status": str(item.get("status", "")),
                    "stable_code": str(item.get("stable_code", "")),
                    "part_candidates": _strings(item.get("part_candidates")),
                    "test_candidates": _strings(item.get("test_candidates")),
                }
            )

    mission = questions.get("mission_context", {})
    mission = mission if isinstance(mission, Mapping) else {}
    event_review = questions.get("event_evidence_candidates", {})
    event_review = event_review if isinstance(event_review, Mapping) else {}

    packet: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "packet_class": "CANDIDATE_REVIEW_ONLY",
        "source_bundle_contract_version": str(bundle_result.get("contract_version", "")),
        "boundaries": {
            "raw_documents_included": False,
            "raw_text_included": False,
            "file_names_included": False,
            "local_paths_included": False,
            "decision_use": False,
        },
        "document_hashes": documents,
        "mission_context_review": {
            "status": str(mission.get("status", "")),
            "required_fields": _strings(mission.get("required_fields")),
            "present_fields": _strings(mission.get("present_fields")),
            "missing_fields": _strings(mission.get("missing_fields")),
        },
        "part_test_identity_review": {
            "status": str(identity.get("status", "")) if isinstance(identity, Mapping) else "",
            "fields": identity_fields,
        },
        "event_evidence_review": {
            "status": str(event_review.get("status", "")),
            "complete_events": _strings(event_review.get("complete_events")),
            "incomplete_events": _strings(event_review.get("incomplete_events")),
            "event_groups": _event_rows(event_review.get("event_groups")),
        },
        "final_review": {
            "bundle_status": str(bundle_result.get("bundle_status", "")),
            "validated_check_count": int(bundle_result.get("validated_check_count", 0)),
            "failed_check_count": int(bundle_result.get("failed_check_count", 0)),
            "not_evaluated_check_count": int(
                bundle_result.get("not_evaluated_check_count", 0)
            ),
            "approval_status": str(bundle_result.get("approval_status", "NOT_EVALUATED")),
            "use_status": str(bundle_result.get("use_status", "NOT_FOR_DECISION")),
            "assurance_decision": str(bundle_result.get("assurance_decision", "HOLD")),
            "blocking_reason": str(summary.get("blocking_reason", "")),
            "next_action": str(summary.get("next_action", "")),
            "next_gate": str(bundle_result.get("next_gate", "")),
        },
    }
    canonical = json.dumps(
        packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    packet["review_packet_sha256"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return packet
