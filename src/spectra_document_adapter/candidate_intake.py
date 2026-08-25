"""Bind caller-provided document candidates to bytes and exact text spans.

No OCR, PDF text extraction, LLM call, approval, or suitability decision is
performed here.  Candidate values are caller projections and remain explicitly
unapproved even when their deterministic bindings are complete.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping
from urllib.parse import urlsplit


CONTRACT_VERSION = "DOCUMENT_INTAKE_RECEIPT_1.0.0"
SUPPORTED_MIME_TYPES = frozenset({"text/plain", "application/pdf"})
RIGHTS_ACTIONS = frozenset(
    {"LOCATOR", "READ_LOCAL", "PROCESS_LOCAL", "DISPLAY_INTERNAL"}
)
CANDIDATE_FIELDS = frozenset(
    {
        "MANUFACTURER",
        "ORDERABLE_PART_NUMBER",
        "PROCESS",
        "DIE",
        "LOT",
        "TID_RATING",
        "TID_DOSE",
        "DOSE_RATE",
        "SEU_RESULT",
        "SEL_RESULT",
        "SEB_RESULT",
        "SEGR_RESULT",
        "SEE_LET",
        "SEE_CROSS_SECTION",
        "PARTICLE_FLUENCE",
        "PARTICLE_ENERGY",
        "TEST_TEMPERATURE",
        "SAMPLE_SIZE",
        "OBSERVED_EVENT_COUNT",
        "LOT_DATE_CODE",
        "SUPPLY_VOLTAGE",
        "MISSION_NAME",
        "ORBIT_REGIME",
        "ORBIT_ALTITUDE",
        "ORBIT_INCLINATION",
        "MISSION_DURATION",
        "SHIELDING_THICKNESS",
        "TEST_CONDITION",
        "EVIDENCE_EVENT_MENTION",
    }
)
STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,79}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+|any\s+|the\s+)?previous\s+instructions?", re.I),
    re.compile(r"ignore\s+(?:all\s+)?instructions?", re.I),
    re.compile(r"(?:reveal|print|return|show)\s+(?:the\s+)?system\s+prompt", re.I),
    re.compile(r"(?:system|developer|assistant)\s*:\s*", re.I),
    re.compile(r"<\s*/?\s*(?:system|developer|assistant)\b", re.I),
    re.compile(r"\bjailbreak\b", re.I),
    re.compile(r"이전\s*(?:지시|명령)(?:를|을)?\s*무시"),
    re.compile(r"(?:지시|명령)(?:를|을)?\s*무시"),
    re.compile(r"시스템\s*프롬프트"),
)

_DOCUMENT_KEYS = frozenset(
    {
        "candidate_class",
        "mime_type",
        "locator",
        "content_bytes",
        "extracted_text",
        "declared_content_sha256",
        "declared_text_sha256",
        "rights",
        "candidates",
        "claimed_use_status",
        "claimed_assurance_decision",
        "claimed_approval_status",
    }
)
_LOCATOR_KEYS = frozenset({"locator_id", "locator_type", "reference"})
_RIGHT_KEYS = frozenset({"action", "status", "scope_locator_id"})
_CANDIDATE_KEYS = frozenset(
    {"candidate_id", "field", "value", "unit", "text_start", "text_end"}
)


def _object(value: Any, allowed: frozenset[str], codes: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        codes.add("INPUT_SHAPE_INVALID")
        return {}
    if set(value) != allowed:
        codes.add("INPUT_SHAPE_INVALID")
    return value


def _stable_id(value: Any) -> bool:
    return isinstance(value, str) and STABLE_ID.fullmatch(value) is not None


def _sha256(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _valid_declared_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _contains_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in PROMPT_INJECTION_PATTERNS)


def _validate_locator(
    value: Any, candidate_class: Any, codes: set[str]
) -> tuple[str | None, str | None]:
    locator = _object(value, _LOCATOR_KEYS, codes)
    locator_id = locator.get("locator_id")
    locator_type = locator.get("locator_type")
    reference = locator.get("reference")
    if not _stable_id(locator_id):
        codes.add("LOCATOR_ID_INVALID")
    if not isinstance(reference, str) or not reference or "\x00" in reference:
        codes.add("LOCATOR_REFERENCE_INVALID")
        return (
            locator_id if _stable_id(locator_id) else None,
            locator_type if isinstance(locator_type, str) else None,
        )

    if locator_type == "SYNTHETIC_REFERENCE":
        if candidate_class != "SYNTHETIC_CONTROL" or not reference.startswith("synthetic://"):
            codes.add("LOCATOR_REFERENCE_INVALID")
    elif locator_type == "LOCAL_PRIVATE_REFERENCE":
        if candidate_class != "ACTUAL_CANDIDATE" or not reference.startswith("evidence://"):
            codes.add("LOCATOR_REFERENCE_INVALID")
        suffix = reference.removeprefix("evidence://")
        if not _stable_id(suffix):
            codes.add("LOCATOR_REFERENCE_INVALID")
    elif locator_type == "PUBLIC_HTTPS_REFERENCE":
        try:
            parsed = urlsplit(reference)
            port = parsed.port
        except ValueError:
            parsed = None
            port = None
        if (
            parsed is None
            or parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or port not in (None, 443)
            or bool(parsed.fragment)
        ):
            codes.add("LOCATOR_REFERENCE_INVALID")
    else:
        codes.add("LOCATOR_TYPE_UNSUPPORTED")

    return (
        locator_id if _stable_id(locator_id) else None,
        locator_type if isinstance(locator_type, str) else None,
    )


def _validate_rights(
    value: Any, locator_id: str | None, candidate_class: Any, codes: set[str]
) -> None:
    if not isinstance(value, list):
        codes.add("ACTION_RIGHTS_MISSING")
        return
    expected_status = (
        "SYNTHETIC_ONLY" if candidate_class == "SYNTHETIC_CONTROL" else "ALLOWED"
    )
    seen: set[str] = set()
    for raw_entry in value:
        entry = _object(raw_entry, _RIGHT_KEYS, codes)
        action = entry.get("action")
        if not isinstance(action, str) or action not in RIGHTS_ACTIONS:
            codes.add("RIGHTS_ACTION_UNKNOWN")
            continue
        if action in seen:
            codes.add("RIGHTS_ACTION_DUPLICATE")
        seen.add(action)
        if entry.get("scope_locator_id") != locator_id:
            codes.add("RIGHTS_SCOPE_MISMATCH")
        if entry.get("status") != expected_status:
            codes.add(f"RIGHTS_{action}_UNRESOLVED")
    for action in RIGHTS_ACTIONS.difference(seen):
        codes.add(f"RIGHTS_{action}_MISSING")


def _validate_content(
    document: Mapping[str, Any], codes: set[str]
) -> tuple[str | None, str | None, str | None]:
    mime_type = document.get("mime_type")
    if not isinstance(mime_type, str) or mime_type not in SUPPORTED_MIME_TYPES:
        codes.add("MIME_TYPE_UNSUPPORTED")

    content = document.get("content_bytes")
    extracted_text = document.get("extracted_text")
    content_hash: str | None = None
    text_hash: str | None = None

    if content is not None:
        if not isinstance(content, bytes):
            codes.add("CONTENT_BYTES_INVALID")
        else:
            content_hash = _sha256(content)
            declared_content_hash = document.get("declared_content_sha256")
            if not _valid_declared_hash(declared_content_hash):
                codes.add("DECLARED_CONTENT_HASH_INVALID")
            elif declared_content_hash != content_hash:
                codes.add("CONTENT_HASH_MISMATCH")
    elif document.get("declared_content_sha256") is not None:
        codes.add("CONTENT_BYTES_MISSING")

    if not isinstance(extracted_text, str) or not extracted_text or "\x00" in extracted_text:
        codes.add("EXTRACTED_TEXT_INVALID")
        extracted_text = None
    else:
        text_hash = _sha256(extracted_text.encode("utf-8"))
        declared_text_hash = document.get("declared_text_sha256")
        if not _valid_declared_hash(declared_text_hash):
            codes.add("DECLARED_TEXT_HASH_INVALID")
        elif declared_text_hash != text_hash:
            codes.add("TEXT_HASH_MISMATCH")
        if _contains_prompt_injection(extracted_text):
            codes.add("PROMPT_INJECTION_PATTERN_DETECTED")

    if mime_type == "application/pdf":
        if not isinstance(content, bytes):
            codes.add("PDF_BYTES_REQUIRED")
        elif not content.startswith(b"%PDF-"):
            codes.add("PDF_SIGNATURE_INVALID")
    elif mime_type == "text/plain" and isinstance(content, bytes) and extracted_text is not None:
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            codes.add("TEXT_BYTES_NOT_UTF8")
        else:
            if decoded != extracted_text:
                codes.add("TEXT_BYTES_PROJECTION_MISMATCH")

    return extracted_text, content_hash, text_hash


def _validate_candidates(
    value: Any, extracted_text: str | None, codes: set[str]
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        codes.add("CANDIDATES_SHAPE_INVALID")
        return []
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_spans: set[tuple[str, int, int]] = set()
    for raw_entry in value:
        entry = _object(raw_entry, _CANDIDATE_KEYS, codes)
        candidate_id = entry.get("candidate_id")
        field = entry.get("field")
        candidate_value = entry.get("value")
        unit = entry.get("unit")
        start = entry.get("text_start")
        end = entry.get("text_end")

        valid = True
        if not _stable_id(candidate_id):
            codes.add("CANDIDATE_ID_INVALID")
            valid = False
        elif candidate_id in seen_ids:
            codes.add("CANDIDATE_ID_DUPLICATE")
            valid = False
        else:
            seen_ids.add(candidate_id)
        if not isinstance(field, str) or field not in CANDIDATE_FIELDS:
            codes.add("CANDIDATE_FIELD_UNSUPPORTED")
            valid = False
        if (
            not isinstance(candidate_value, str)
            or not candidate_value
            or len(candidate_value) > 500
            or "\x00" in candidate_value
        ):
            codes.add("CANDIDATE_VALUE_INVALID")
            valid = False
        if unit is not None and (
            not isinstance(unit, str) or not unit or len(unit) > 32 or "\x00" in unit
        ):
            codes.add("CANDIDATE_UNIT_INVALID")
            valid = False
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or extracted_text is None
            or start < 0
            or end <= start
            or end > len(extracted_text)
        ):
            codes.add("CANDIDATE_SPAN_INVALID")
            valid = False
        elif not isinstance(candidate_value, str) or extracted_text[start:end] != candidate_value:
            codes.add("CANDIDATE_SPAN_MISMATCH")
            valid = False
        elif isinstance(field, str):
            span_key = (field, start, end)
            if span_key in seen_spans:
                codes.add("CANDIDATE_SPAN_DUPLICATE")
                valid = False
            seen_spans.add(span_key)

        if valid:
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "field": field,
                    "value": candidate_value,
                    "unit": unit,
                    "source_span": {"start": start, "end": end},
                    "candidate_status": "UNAPPROVED_CANDIDATE",
                }
            )
    return candidates


def evaluate_document_intake(document: Any) -> dict[str, Any]:
    """Return a deterministic, non-decision receipt for one local document."""

    codes: set[str] = set()
    document_object = _object(document, _DOCUMENT_KEYS, codes)
    candidate_class = document_object.get("candidate_class")
    actual = candidate_class == "ACTUAL_CANDIDATE"
    synthetic = candidate_class == "SYNTHETIC_CONTROL"
    if not actual and not synthetic:
        codes.add("CANDIDATE_CLASS_INVALID")

    locator_id, locator_type = _validate_locator(
        document_object.get("locator"), candidate_class, codes
    )
    _validate_rights(document_object.get("rights"), locator_id, candidate_class, codes)
    extracted_text, content_hash, text_hash = _validate_content(document_object, codes)
    candidates = _validate_candidates(document_object.get("candidates"), extracted_text, codes)

    if (
        document_object.get("claimed_use_status") != "NOT_FOR_DECISION"
        or document_object.get("claimed_assurance_decision") != "HOLD"
        or document_object.get("claimed_approval_status") != "NOT_EVALUATED"
    ):
        codes.add("OPTIMISTIC_OUTCOME_FORBIDDEN")

    if actual:
        codes.add("ACTUAL_CANDIDATE_NOT_ISSUED")
        intake_status = "HOLD_NOT_ISSUED"
    elif synthetic:
        codes.add("SYNTHETIC_ONLY")
        intake_status = "SYNTHETIC_CONTROL"
    else:
        intake_status = "HOLD_NOT_ISSUED"

    non_suppressing_codes = {"ACTUAL_CANDIDATE_NOT_ISSUED", "SYNTHETIC_ONLY"}
    if codes.difference(non_suppressing_codes):
        candidates = []

    if "PROMPT_INJECTION_PATTERN_DETECTED" in codes:
        processing_status = "CONTENT_REJECTED"
    elif "MIME_TYPE_UNSUPPORTED" in codes:
        processing_status = "CONTENT_REJECTED"
    elif any(
        code in codes
        for code in {
            "CONTENT_HASH_MISMATCH",
            "TEXT_HASH_MISMATCH",
            "TEXT_BYTES_PROJECTION_MISMATCH",
            "PDF_SIGNATURE_INVALID",
            "CANDIDATE_SPAN_MISMATCH",
        }
    ):
        processing_status = "INTEGRITY_FAILURE"
    elif "INPUT_SHAPE_INVALID" in codes or any(
        code.endswith(("_INVALID", "_UNSUPPORTED")) for code in codes
    ):
        processing_status = "INVALID_INPUT"
    elif any(code.startswith(("LOCATOR_", "RIGHTS_", "ACTION_RIGHTS_")) for code in codes):
        processing_status = "PROVENANCE_FAILURE"
    else:
        processing_status = "VALID"

    return {
        "contract_version": CONTRACT_VERSION,
        "candidate_class": candidate_class if actual or synthetic else "INVALID",
        "processing_status": processing_status,
        "intake_status": intake_status,
        "source": {
            "mime_type": document_object.get("mime_type"),
            "locator_id": locator_id,
            "locator_type": locator_type,
            "content_sha256": content_hash,
            "text_sha256": text_hash,
            "text_origin": "CALLER_PROVIDED",
            "ocr_performed": False,
            "llm_extraction_performed": False,
        },
        "candidates": candidates,
        "blocker_codes": sorted(codes),
        "approval_status": "NOT_EVALUATED",
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
