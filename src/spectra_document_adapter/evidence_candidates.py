"""Conservatively group source-bound document candidates by radiation event.

Candidates on the same extracted-text line as an event mention are linked.  A
single document-wide TID dose may also bind to TID because that field is not
shared with another event type.  Ambiguous or repeated values stay unassigned.
The result is a review packet, never approved evidence or a suitability decision.
"""

from __future__ import annotations

from typing import Any, Mapping


CONTRACT_VERSION = "EVENT_CANDIDATE_LINKAGE_1.0.0"
EVENT_TYPES = ("TID", "SEU", "SEL", "SEB", "SEGR")
EVENT_REQUIRED_FIELDS = {
    "TID": ("TID_DOSE",),
    "SEU": ("SEE_CROSS_SECTION",),
    "SEL": ("PARTICLE_FLUENCE", "SAMPLE_SIZE", "OBSERVED_EVENT_COUNT"),
    "SEB": ("PARTICLE_FLUENCE", "SAMPLE_SIZE", "OBSERVED_EVENT_COUNT"),
    "SEGR": ("PARTICLE_FLUENCE", "SAMPLE_SIZE", "OBSERVED_EVENT_COUNT"),
}
IDENTITY_FIELDS = frozenset(
    {"MANUFACTURER", "ORDERABLE_PART_NUMBER", "PROCESS", "DIE", "LOT", "LOT_DATE_CODE"}
)


def _span(candidate: Mapping[str, Any]) -> tuple[int, int] | None:
    source_span = candidate.get("source_span")
    if not isinstance(source_span, Mapping):
        return None
    start = source_span.get("start")
    end = source_span.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start < 0
        or end <= start
    ):
        return None
    return start, end


def _line_span(text: str, start: int, end: int) -> tuple[int, int]:
    line_start = text.rfind("\n", 0, start) + 1
    next_break = text.find("\n", end)
    line_end = len(text) if next_break < 0 else next_break
    return line_start, line_end


def link_event_candidates(
    extracted_text: str, candidates: list[Mapping[str, Any]]
) -> dict[str, Any]:
    """Return a non-decision event linkage receipt for validated candidates."""

    if not isinstance(extracted_text, str):
        extracted_text = ""
    safe_candidates = [item for item in candidates if isinstance(item, Mapping)]
    identity_candidates = [
        {
            "candidate_id": item.get("candidate_id"),
            "field": item.get("field"),
            "source_span": item.get("source_span"),
        }
        for item in safe_candidates
        if item.get("field") in IDENTITY_FIELDS and _span(item) is not None
    ]
    groups: list[dict[str, Any]] = []
    for mention in safe_candidates:
        if mention.get("field") != "EVIDENCE_EVENT_MENTION":
            continue
        event_type = str(mention.get("value", "")).upper()
        mention_span = _span(mention)
        if event_type not in EVENT_TYPES or mention_span is None:
            continue
        line_start, line_end = _line_span(extracted_text, *mention_span)
        linked = []
        for candidate in safe_candidates:
            if candidate is mention or candidate.get("field") == "EVIDENCE_EVENT_MENTION":
                continue
            candidate_span = _span(candidate)
            if candidate_span is None:
                continue
            if line_start <= candidate_span[0] and candidate_span[1] <= line_end:
                linked.append(
                    {
                        "candidate_id": candidate.get("candidate_id"),
                        "field": candidate.get("field"),
                        "value": candidate.get("value"),
                        "unit": candidate.get("unit"),
                        "source_span": candidate.get("source_span"),
                        "link_basis": "SAME_SOURCE_LINE",
                    }
                )
        if event_type == "TID" and not any(
            item["field"] == "TID_DOSE" for item in linked
        ):
            document_tid_doses = [
                item
                for item in safe_candidates
                if item.get("field") == "TID_DOSE" and _span(item) is not None
            ]
            if len(document_tid_doses) == 1:
                item = document_tid_doses[0]
                linked.append(
                    {
                        "candidate_id": item.get("candidate_id"),
                        "field": item.get("field"),
                        "value": item.get("value"),
                        "unit": item.get("unit"),
                        "source_span": item.get("source_span"),
                        "link_basis": "UNIQUE_DOCUMENT_TID_DOSE",
                    }
                )
        linked.sort(key=lambda item: (item["source_span"]["start"], str(item["field"])))
        present_fields = sorted({str(item["field"]) for item in linked})
        required_fields = list(EVENT_REQUIRED_FIELDS[event_type])
        missing_fields = [item for item in required_fields if item not in present_fields]
        groups.append(
            {
                "event_type": event_type,
                "mention_candidate_id": mention.get("candidate_id"),
                "mention_source_span": mention.get("source_span"),
                "line_source_span": {"start": line_start, "end": line_end},
                "required_fields": required_fields,
                "present_fields": present_fields,
                "missing_fields": missing_fields,
                "linked_candidates": linked,
                "status": (
                    "REQUIRED_FIELDS_PRESENT"
                    if not missing_fields
                    else "MISSING_REQUIRED_FIELDS"
                ),
            }
        )

    groups.sort(
        key=lambda item: (
            EVENT_TYPES.index(item["event_type"]),
            item["mention_source_span"]["start"],
        )
    )
    complete = sum(item["status"] == "REQUIRED_FIELDS_PRESENT" for item in groups)
    incomplete = len(groups) - complete
    unassigned_measurements = [
        {
            "candidate_id": item.get("candidate_id"),
            "field": item.get("field"),
            "source_span": item.get("source_span"),
        }
        for item in safe_candidates
        if item.get("field") not in IDENTITY_FIELDS
        and item.get("field") != "EVIDENCE_EVENT_MENTION"
        and _span(item) is not None
        and not any(
            item.get("candidate_id") == linked.get("candidate_id")
            for group in groups
            for linked in group["linked_candidates"]
        )
    ]
    if not groups:
        linkage_status = "NO_EVENT_MENTION"
    elif incomplete:
        linkage_status = "PARTIAL_EVENT_CANDIDATES"
    else:
        linkage_status = "EVENT_CANDIDATES_READY_FOR_REVIEW"
    return {
        "contract_version": CONTRACT_VERSION,
        "linkage_status": linkage_status,
        "event_group_count": len(groups),
        "complete_event_group_count": complete,
        "incomplete_event_group_count": incomplete,
        "event_groups": groups,
        "identity_candidates": identity_candidates,
        "unassigned_measurement_candidates": unassigned_measurements,
        "link_rule": "SAME_SOURCE_LINE_OR_UNIQUE_DOCUMENT_TID_DOSE",
        "approval_status": "NOT_EVALUATED",
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "next_gate": "APPROVED_BOM_AND_MISSION_CASE_LINK",
    }
