#!/usr/bin/env python3
"""Extract exact, review-only candidates from one local document.

The source file stays in place.  The JSON output contains no raw bytes, raw
text, or filesystem path.  PDF extraction uses the optional ``pypdf`` package;
plain UTF-8 text and JSON need only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_document_adapter import evaluate_document_intake  # noqa: E402


MAX_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARACTERS = 2_000_000
EVENT_FIELDS = {
    "TID": "EVIDENCE_EVENT_MENTION",
    "SEU": "EVIDENCE_EVENT_MENTION",
    "SEL": "EVIDENCE_EVENT_MENTION",
    "SEB": "EVIDENCE_EVENT_MENTION",
    "SEGR": "EVIDENCE_EVENT_MENTION",
}
MAX_NUMERIC_CANDIDATES = 64

NUMERIC_FIELD_RULES: dict[str, tuple[str, float | None, float | None]] = {
    "ORBIT_ALTITUDE": ("MISSION_AGENT", 0.0, None),
    "ORBIT_INCLINATION": ("MISSION_AGENT", 0.0, 180.0),
    "MISSION_DURATION": ("MISSION_AGENT", 0.0, None),
    "SHIELDING_THICKNESS": ("MISSION_AGENT", 0.0, None),
    "TID_DOSE": ("PARTS_AGENT", 0.0, None),
    "DOSE_RATE": ("PARTS_AGENT", 0.0, None),
    "SEE_LET": ("PARTS_AGENT", 0.0, None),
    "SEE_CROSS_SECTION": ("PARTS_AGENT", 0.0, None),
    "PARTICLE_FLUENCE": ("PARTS_AGENT", 0.0, None),
    "PARTICLE_ENERGY": ("PARTS_AGENT", 0.0, None),
    "TEST_TEMPERATURE": ("PARTS_AGENT", -273.15, None),
    "SUPPLY_VOLTAGE": ("PARTS_AGENT", 0.0, None),
    "SAMPLE_SIZE": ("PARTS_AGENT", 1.0, None),
}

MISSION_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "MISSION_NAME",
        re.compile(r"(?:mission\s*name|mission)\s*[:=]\s*(?P<value>[^\n\r]{2,120})", re.I),
    ),
    (
        "ORBIT_REGIME",
        re.compile(
            r"(?:orbit(?:\s*regime|\s*type)?)\s*[:=]\s*(?P<value>(?:(?:near[- ]polar|polar),?\s*)?sun[- ]synchronous|near[- ]polar|polar|LEO|MEO|GEO)\b",
            re.I,
        ),
    ),
)


def _unit_text(value: str) -> str:
    """Normalize typography only; do not convert or reinterpret a quantity."""
    return re.sub(r"\s+", "", value).replace("²", "2").replace("·", "-").replace("⋅", "-")


NUMERIC_PATTERNS: tuple[tuple[str, str | None, re.Pattern[str]], ...] = (
    (
        "ORBIT_ALTITUDE",
        "km",
        re.compile(
            r"(?:orbit(?:al)?\s+altitude|altitude)\s*[:=]?\s*(?P<value>\d+(?:\.\d+)?\s*km)\b",
            re.I,
        ),
    ),
    (
        "ORBIT_INCLINATION",
        "deg",
        re.compile(
            r"(?:orbit(?:al)?\s+inclination|inclination)\s*[:=]?\s*(?P<value>\d+(?:\.\d+)?\s*(?:°|deg(?:rees?)?))",
            re.I,
        ),
    ),
    (
        "MISSION_DURATION",
        None,
        re.compile(
            r"(?:design\s+life|mission\s+(?:design\s+)?life|mission\s+duration|lifetime)\s*[:=]?\s*(?:minimum\s+(?:of\s+)?)?(?P<value>\d+(?:\.\d+)?\s*(?P<unit>years?|months?|days?))",
            re.I,
        ),
    ),
    (
        "SHIELDING_THICKNESS",
        None,
        re.compile(
            r"(?:shield(?:ing)?(?:\s+thickness)?|aluminum\s+equivalent)\s*[:=]?\s*(?P<value>\d+(?:\.\d+)?\s*(?P<unit>mm\s*(?:Al(?:uminum)?(?:\s+equivalent)?|aluminum\s+equivalent)))",
            re.I,
        ),
    ),
    (
        "DOSE_RATE",
        None,
        re.compile(
            r"(?P<value>(?:(?:[<>]=?|[~≈])\s*)?\d+(?:\.\d+)?\s*(?P<unit>(?:M|k)?rad(?:\s*\(\s*Si\s*\))?\s*/\s*(?:seconds?|sec|s)))",
            re.I,
        ),
    ),
    (
        "TID_DOSE",
        None,
        re.compile(
            r"(?P<value>(?:(?:[<>]=?|[~≈])\s*)?\d+(?:\.\d+)?\s*(?P<unit>(?:M|k)?rad(?:\s*\(\s*Si\s*\))?))(?!\s*/)",
            re.I,
        ),
    ),
    (
        "SEE_LET",
        None,
        re.compile(
            r"(?P<value>(?:(?:[<>]=?|[~≈])\s*)?\d+(?:\.\d+)?(?:\s*(?:to|[-–])\s*\d+(?:\.\d+)?)?\s*(?P<unit>MeV\s*[-·⋅]?\s*cm(?:\^?2|²)\s*/\s*mg))",
            re.I,
        ),
    ),
    (
        "SEE_CROSS_SECTION",
        None,
        re.compile(
            r"(?P<value>(?:(?:[<>]=?|[~≈])\s*)?\d+(?:\.\d+)?\s*(?:(?:[x×]\s*10\s*(?:\^|\*\*)?\s*[+-]?\d+)|(?:[eE][+-]?\d+))?\s*(?P<unit>cm(?:\^?2|²)\s*/\s*(?:bit|byte|device)))",
            re.I,
        ),
    ),
    (
        "PARTICLE_FLUENCE",
        None,
        re.compile(
            r"(?P<value>(?:(?:[<>]=?|[~≈])\s*)?\d+(?:\.\d+)?\s*(?:(?:[x×]\s*10\s*(?:\^|\*\*)?\s*[+-]?\d+)|(?:[eE][+-]?\d+))?\s*(?P<unit>(?:p|protons?|particles?)\s*/\s*cm(?:\^?2|²)))(?!\s*/)",
            re.I,
        ),
    ),
    (
        "PARTICLE_ENERGY",
        None,
        re.compile(
            r"(?P<value>\d+(?:\.\d+)?\s*(?P<unit>keV|MeV|GeV))(?!\s*[-·⋅]?\s*cm)",
            re.I,
        ),
    ),
    (
        "TEST_TEMPERATURE",
        "degC",
        re.compile(
            r"(?P<value>[+-]?\d+(?:\.\d+)?\s*(?:°\s*C|degC|degrees?\s*C)(?:\s*(?:to|[-–])\s*[+-]?\d+(?:\.\d+)?\s*(?:°\s*C|degC|degrees?\s*C))?)",
            re.I,
        ),
    ),
    (
        "SUPPLY_VOLTAGE",
        "V",
        re.compile(
            r"(?P<value>\d+(?:\.\d+)?\s*V?\s*(?:-|–|to)\s*\d+(?:\.\d+)?\s*V)",
            re.I,
        ),
    ),
    (
        "SAMPLE_SIZE",
        "devices",
        re.compile(r"(?:sample\s*size|samples?|DUTs?)\s*[:=]?\s*(?P<value>\d{1,4})\b", re.I),
    ),
    (
        "LOT_DATE_CODE",
        None,
        re.compile(
            r"(?:LDC|lot\s*date\s*code|lot\s*code)\s*[:;=]?\s*(?:is\s+)?(?P<value>(?!as\b|is\b)[A-Za-z0-9][A-Za-z0-9._/-]{1,31}|unknown|n/?a)\b",
            re.I,
        ),
    ),
)


class ExtractionUnavailable(RuntimeError):
    """Raised when a bounded local extraction cannot be performed."""


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _stable_suffix(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()[:24]


def _extract_pdf(content: bytes) -> tuple[str, str, str, int]:
    try:
        import pypdf  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise ExtractionUnavailable("PDF_EXTRACTOR_UNAVAILABLE") from exc
    try:
        reader = pypdf.PdfReader(io.BytesIO(content), strict=True)
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # pypdf exposes multiple parser exception types.
        raise ExtractionUnavailable("PDF_TEXT_EXTRACTION_FAILED") from exc
    text = "\n".join(pages)
    version = str(getattr(pypdf, "__version__", "UNKNOWN"))
    return text, "application/pdf", f"pypdf-{version}", len(pages)


def extract_text(path: Path, content: bytes) -> tuple[str, str, str, int]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(content)
    if suffix not in {".txt", ".json"}:
        raise ExtractionUnavailable("DOCUMENT_TYPE_UNSUPPORTED")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExtractionUnavailable("TEXT_NOT_UTF8") from exc
    return text, "text/plain", "utf8-direct-1", 1


def _exact_span(text: str, expected: str) -> tuple[int, int] | None:
    if not expected or len(expected) > 500:
        return None
    match = re.search(re.escape(expected), text, flags=re.IGNORECASE)
    return match.span() if match else None


def _candidate(
    *, candidate_id: str, field: str, text: str, span: tuple[int, int], unit: str | None = None
) -> dict[str, Any]:
    start, end = span
    return {
        "candidate_id": candidate_id,
        "field": field,
        "value": text[start:end],
        "unit": unit,
        "text_start": start,
        "text_end": end,
    }


def _numeric_components(field: str, value: str, unit: str | None) -> list[float]:
    numeric_text = value.replace(unit, "") if unit and unit in value else value
    scientific = re.search(
        r"(?P<base>\d+(?:\.\d+)?)\s*[x×]\s*10\s*(?:\^|\*\*)?\s*(?P<exp>[+-]?\d+)",
        numeric_text,
        re.I,
    )
    if scientific is not None:
        return [float(scientific.group("base")) * (10 ** int(scientific.group("exp")))]
    exponential = re.search(r"\d+(?:\.\d+)?[eE][+-]?\d+", numeric_text)
    if exponential is not None:
        return [float(exponential.group(0))]
    if field == "TEST_TEMPERATURE":
        return [float(item) for item in re.findall(r"[+-]?\d+(?:\.\d+)?", numeric_text)]
    return [float(item) for item in re.findall(r"\d+(?:\.\d+)?", numeric_text)]


def _partial_evaluation(
    receipt: dict[str, Any], expected_part: str, manufacturer: str | None
) -> dict[str, Any]:
    """Continue bounded checks even when the final assurance decision is HOLD."""
    if receipt.get("processing_status") != "VALID":
        return {
            "contract_version": "PARTIAL_EVALUATION_LEDGER_1.0.0",
            "status": "STOPPED_AT_DOCUMENT_GATE",
            "validated_checks": [],
            "failed_checks": [],
            "not_evaluated_checks": [],
            "hold_agent": "LOCAL_DOCUMENT_GATE",
            "assurance_decision": "HOLD",
        }

    validated: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    fields = set(receipt.get("candidate_fields", []))
    for candidate in receipt.get("candidates", []):
        field = candidate["field"]
        if field not in NUMERIC_FIELD_RULES:
            continue
        agent, minimum, maximum = NUMERIC_FIELD_RULES[field]
        values = _numeric_components(field, candidate["value"], candidate.get("unit"))
        codes = ["SOURCE_SPAN_BOUND", "UNIT_RECOGNIZED"]
        valid = bool(values)
        if valid and minimum is not None:
            valid = all(item >= minimum for item in values)
            codes.append("DOMAIN_MINIMUM_CHECKED")
        if valid and maximum is not None:
            valid = all(item <= maximum for item in values)
            codes.append("DOMAIN_MAXIMUM_CHECKED")
        if valid and len(values) > 1:
            valid = values[0] <= values[-1]
            codes.append("RANGE_ORDER_CHECKED")
        if field == "SAMPLE_SIZE" and valid:
            valid = all(item.is_integer() for item in values)
            codes.append("INTEGER_CHECKED")
        item = {
            "check_id": f"NUMERIC_{field}",
            "agent_role": agent,
            "field": field,
            "observed_value": candidate["value"],
            "unit": candidate.get("unit"),
            "status": "VALIDATED" if valid else "FAILED",
            "stable_codes": codes if valid else codes + ["NUMERIC_DOMAIN_INVALID"],
            "claim_boundary": "STRUCTURE_UNIT_AND_DOMAIN_ONLY",
        }
        (validated if valid else failed).append(item)

    if "LOT_DATE_CODE" in fields:
        lot_candidate = next(
            item for item in receipt["candidates"] if item["field"] == "LOT_DATE_CODE"
        )
        validated.append(
            {
                "check_id": "LOT_DATE_CODE_STRUCTURE",
                "agent_role": "PARTS_AGENT",
                "field": "LOT_DATE_CODE",
                "observed_value": lot_candidate["value"],
                "unit": None,
                "status": "VALIDATED",
                "stable_codes": ["SOURCE_SPAN_BOUND", "IDENTIFIER_STRUCTURE_VALID"],
                "claim_boundary": "IDENTIFIER_STRUCTURE_ONLY",
            }
        )

    identity_target = expected_part.strip()
    if identity_target and identity_target != "NOT-APPLICABLE":
        identity_ok = "ORDERABLE_PART_NUMBER" in fields
        identity_check = {
            "check_id": "EXPECTED_PART_TEXT_MATCH",
            "agent_role": "PARTS_AGENT",
            "field": "ORDERABLE_PART_NUMBER",
            "observed_value": identity_target if identity_ok else None,
            "unit": None,
            "status": "VALIDATED" if identity_ok else "FAILED",
            "stable_codes": [
                "EXPECTED_PART_TEXT_FOUND" if identity_ok else "EXPECTED_PART_TEXT_NOT_FOUND"
            ],
            "claim_boundary": "TEXT_MATCH_NOT_APPROVED_BOM_IDENTITY",
        }
        (validated if identity_ok else failed).append(identity_check)
    if manufacturer:
        manufacturer_ok = "MANUFACTURER" in fields
        manufacturer_check = {
            "check_id": "EXPECTED_MANUFACTURER_TEXT_MATCH",
            "agent_role": "PARTS_AGENT",
            "field": "MANUFACTURER",
            "observed_value": manufacturer if manufacturer_ok else None,
            "unit": None,
            "status": "VALIDATED" if manufacturer_ok else "FAILED",
            "stable_codes": [
                "EXPECTED_MANUFACTURER_TEXT_FOUND"
                if manufacturer_ok
                else "EXPECTED_MANUFACTURER_TEXT_NOT_FOUND"
            ],
            "claim_boundary": "TEXT_MATCH_NOT_APPROVED_BOM_IDENTITY",
        }
        (validated if manufacturer_ok else failed).append(manufacturer_check)

    mission_fields = {
        "MISSION_NAME",
        "ORBIT_REGIME",
        "ORBIT_ALTITUDE",
        "ORBIT_INCLINATION",
        "MISSION_DURATION",
        "SHIELDING_THICKNESS",
    }
    radiation_fields = set(NUMERIC_FIELD_RULES) - mission_fields
    if fields & mission_fields and not fields & radiation_fields:
        withheld = [{
            "check_id": "MISSION_RADIATION_ENVIRONMENT_LINK",
            "agent_role": "MISSION_AGENT",
            "status": "NOT_EVALUATED",
            "stable_code": "RADIATION_ENVIRONMENT_MISSING",
        }]
        hold_agent = "MISSION_AGENT"
    elif fields & {"ORDERABLE_PART_NUMBER", "MANUFACTURER", "SUPPLY_VOLTAGE"} and not fields & {
        "TID_DOSE", "DOSE_RATE", "SEE_LET", "SEE_CROSS_SECTION", "PARTICLE_FLUENCE", "PARTICLE_ENERGY"
    }:
        withheld = [{
            "check_id": "PART_RADIATION_TEST_LINK",
            "agent_role": "PARTS_AGENT",
            "status": "NOT_EVALUATED",
            "stable_code": "RADIATION_TEST_EVIDENCE_MISSING",
        }]
        hold_agent = "PARTS_AGENT"
    else:
        withheld = [
            {
                "check_id": "APPROVED_BOM_EXACT_IDENTITY",
                "agent_role": "PARTS_AGENT",
                "status": "NOT_EVALUATED",
                "stable_code": "APPROVED_BOM_TARGET_MISSING",
            },
            {
                "check_id": "MISSION_TEST_APPLICABILITY",
                "agent_role": "MISSION_AGENT",
                "status": "NOT_EVALUATED",
                "stable_code": "MISSION_REQUIREMENT_MISSING",
            },
        ]
        hold_agent = "PARTS_AGENT"
    return {
        "contract_version": "PARTIAL_EVALUATION_LEDGER_1.0.0",
        "status": "PARTIAL_EVALUATION_COMPLETE",
        "validated_checks": validated,
        "failed_checks": failed,
        "not_evaluated_checks": withheld,
        "hold_agent": hold_agent,
        "assurance_decision": "HOLD",
    }


def extract_candidates(text: str, expected_part: str, manufacturer: str | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    part_span = _exact_span(text, expected_part)
    if part_span is not None:
        candidates.append(
            _candidate(
                candidate_id="exact-part-candidate",
                field="ORDERABLE_PART_NUMBER",
                text=text,
                span=part_span,
            )
        )
    if manufacturer:
        manufacturer_span = _exact_span(text, manufacturer)
        if manufacturer_span is not None:
            candidates.append(
                _candidate(
                    candidate_id="manufacturer-candidate",
                    field="MANUFACTURER",
                    text=text,
                    span=manufacturer_span,
                )
            )
    for event, field in EVENT_FIELDS.items():
        event_span = _exact_span(text, event)
        if event_span is not None:
            candidates.append(
                _candidate(
                    candidate_id=f"event-{event.lower()}-candidate",
                    field=field,
                    text=text,
                    span=event_span,
                )
            )
    for field, pattern in MISSION_TEXT_PATTERNS:
        match = pattern.search(text)
        if match is not None:
            candidates.append(
                _candidate(
                    candidate_id=f"mission-{field.lower()}-candidate",
                    field=field,
                    text=text,
                    span=match.span("value"),
                )
            )
    numeric_count = 0
    seen_numeric: set[tuple[str, int, int]] = set()
    seen_numeric_values: set[tuple[str, str]] = set()
    for field, fixed_unit, pattern in NUMERIC_PATTERNS:
        for match in pattern.finditer(text):
            span = match.span("value")
            key = (field, *span)
            if key in seen_numeric:
                continue
            seen_numeric.add(key)
            value_key = (field, re.sub(r"\s+", "", match.group("value")).casefold())
            if value_key in seen_numeric_values:
                continue
            seen_numeric_values.add(value_key)
            raw_unit = match.groupdict().get("unit")
            unit = fixed_unit or (_unit_text(raw_unit) if raw_unit else None)
            candidates.append(
                _candidate(
                    candidate_id=f"numeric-{field.lower()}-{numeric_count + 1}",
                    field=field,
                    text=text,
                    span=span,
                    unit=unit,
                )
            )
            numeric_count += 1
            if numeric_count >= MAX_NUMERIC_CANDIDATES:
                return candidates
    return candidates


def fail_closed_receipt(code: str) -> dict[str, Any]:
    receipt = {
        "contract_version": "LOCAL_DOCUMENT_EXTRACTION_RECEIPT_1.0.0",
        "processing_status": "DATA_UNAVAILABLE",
        "extraction_status": "HOLD_NOT_EXTRACTED",
        "candidate_count": 0,
        "candidate_fields": [],
        "blocker_codes": [code],
        "approval_status": "NOT_EVALUATED",
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
        "partial_evaluation": {
            "contract_version": "PARTIAL_EVALUATION_LEDGER_1.0.0",
            "status": "STOPPED_AT_DOCUMENT_GATE",
            "validated_checks": [],
            "failed_checks": [],
            "not_evaluated_checks": [],
            "hold_agent": "LOCAL_DOCUMENT_GATE",
            "assurance_decision": "HOLD",
        },
    }
    receipt["review_summary"] = review_summary(receipt)
    _enrich_review_summary(receipt)
    return receipt


def _enrich_review_summary(receipt: dict[str, Any]) -> None:
    ledger = receipt["partial_evaluation"]
    summary = receipt["review_summary"]
    validated = ledger["validated_checks"]
    failed = ledger["failed_checks"]
    withheld = ledger["not_evaluated_checks"]
    agent_labels = {
        "LOCAL_DOCUMENT_GATE": "문서 입력·추출 단계",
        "MISSION_AGENT": "임무 조건 검토 역할",
        "PARTS_AGENT": "부품·시험 근거 검토 역할",
        "ASSURANCE_AGENT": "최종 보류 검토 역할",
    }
    field_labels = {
        "ORDERABLE_PART_NUMBER": "주문형번 후보",
        "MANUFACTURER": "제조사 후보",
        "TID_DOSE": "누적선량",
        "DOSE_RATE": "선량률",
        "SEE_LET": "LET",
        "SEE_CROSS_SECTION": "사건 단면적",
        "PARTICLE_FLUENCE": "입자 fluence",
        "PARTICLE_ENERGY": "입자 에너지",
        "TEST_TEMPERATURE": "시험 온도",
        "SUPPLY_VOLTAGE": "공급 전압",
        "SAMPLE_SIZE": "시험 시료 수",
        "LOT_DATE_CODE": "로트·날짜 코드",
        "ORBIT_ALTITUDE": "궤도 고도",
        "ORBIT_INCLINATION": "궤도 경사각",
        "MISSION_DURATION": "임무 기간",
        "SHIELDING_THICKNESS": "차폐 두께",
    }
    results: list[str] = []
    for item in validated:
        role = agent_labels.get(item["agent_role"], item["agent_role"])
        field = field_labels.get(item["field"], item["field"])
        if item["claim_boundary"] == "STRUCTURE_UNIT_AND_DOMAIN_ONLY":
            detail = "원문 위치·숫자 형식·단위·기본 입력 범위 확인 · 임무 적합성 판정 아님"
        elif item["claim_boundary"] == "IDENTIFIER_STRUCTURE_ONLY":
            detail = "원문 위치·식별자 형식 확인 · 실제 로트 일치 판정 아님"
        else:
            detail = "입력한 후보 문자열을 원문에서 확인 · 승인 BOM 대조 아님"
        results.append(
            f"확인 완료 · {role} · {field} {item['observed_value']} · {detail}"
        )

    failure_labels = {
        "EXPECTED_PART_TEXT_NOT_FOUND": "입력한 주문형번 후보를 원문에서 찾지 못함",
        "EXPECTED_MANUFACTURER_TEXT_NOT_FOUND": "입력한 제조사 후보를 원문에서 찾지 못함",
        "NUMERIC_DOMAIN_INVALID": "숫자 형식 또는 기본 입력 범위를 확인하지 못함",
    }
    for item in failed:
        code = item["stable_codes"][-1]
        results.append(
            f"불일치 · {agent_labels.get(item['agent_role'], item['agent_role'])} · "
            f"{failure_labels.get(code, code)}"
        )

    withheld_labels = {
        "APPROVED_BOM_TARGET_MISSING": "승인된 비교 대상 부품 정보가 없어 정확한 부품 식별 대조는 진행하지 못함",
        "MISSION_REQUIREMENT_MISSING": "임무 조건이 없어 시험 결과의 임무 적용성은 판단하지 못함",
        "RADIATION_ENVIRONMENT_MISSING": "방사선 환경 입력이 없어 임무 조건과 환경을 연결하지 못함",
        "RADIATION_TEST_EVIDENCE_MISSING": "방사선 시험 결과가 없어 부품 명세와 시험 근거를 연결하지 못함",
    }
    for item in withheld:
        code = item["stable_code"]
        results.append(
            f"추가 입력 필요 · {agent_labels.get(item['agent_role'], item['agent_role'])} · "
            f"{withheld_labels.get(code, code)}"
        )
    summary["validation_results"] = results
    summary["validated_check_count"] = len(validated)
    summary["failed_check_count"] = len(failed)
    summary["not_evaluated_check_count"] = len(withheld)
    summary["hold_agent"] = ledger["hold_agent"]
    if receipt.get("processing_status") == "VALID" and (validated or failed):
        summary["headline"] = (
            f"확인 가능한 {len(validated) + len(failed)}개 항목을 끝까지 검사했습니다. "
            f"{len(validated)}개 확인 · {len(failed)}개 불일치 · "
            f"{len(withheld)}개 추가 입력 필요로 최종 판단을 보류했습니다."
        )


def review_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    """Explain the first blocking boundary without upgrading candidates."""
    if receipt.get("processing_status") != "VALID":
        codes = set(receipt.get("blocker_codes") or ["DATA_UNAVAILABLE"])
        code = next(
            (
                item
                for item in (
                    "PROMPT_INJECTION_PATTERN_DETECTED",
                    "RIGHTS_PROCESS_LOCAL_UNRESOLVED",
                    "DOCUMENT_TYPE_UNSUPPORTED",
                    "DOCUMENT_SIZE_OUT_OF_RANGE",
                )
                if item in codes
            ),
            sorted(codes)[0],
        )
        reason = {
            "RIGHTS_PROCESS_LOCAL_UNRESOLVED": "로컬 문서 처리 권리가 확인되지 않았습니다.",
            "PROMPT_INJECTION_PATTERN_DETECTED": "문서에서 지시문 주입 패턴을 발견해 후보 추출을 중단했습니다.",
            "DOCUMENT_TYPE_UNSUPPORTED": "현재 파서가 지원하지 않는 파일 형식입니다.",
            "DOCUMENT_SIZE_OUT_OF_RANGE": "파일 크기가 허용 범위를 벗어났습니다.",
        }.get(code, "문서를 안전하게 읽거나 검증할 수 없습니다.")
        return {
            "headline": "이 문서는 판단 입력으로 사용할 수 없습니다.",
            "problem_location": "문서 입력·출처 검증",
            "confirmed_facts": [],
            "blocking_reason": reason,
            "next_action": "원본 파일, 처리 권리와 입력 조건을 확인한 뒤 다시 제출합니다.",
        }

    labels = {
        "ORDERABLE_PART_NUMBER": "주문형번 후보",
        "MANUFACTURER": "제조사 후보",
        "EVIDENCE_EVENT_MENTION": "시험 사건 언급",
        "TID_DOSE": "누적선량 값 후보",
        "DOSE_RATE": "선량률 후보",
        "SEE_LET": "LET 값 후보",
        "SEE_CROSS_SECTION": "사건 단면적 후보",
        "PARTICLE_FLUENCE": "입자 fluence 후보",
        "PARTICLE_ENERGY": "입자 에너지 후보",
        "TEST_TEMPERATURE": "시험 온도 후보",
        "SAMPLE_SIZE": "시험 시료 수 후보",
        "LOT_DATE_CODE": "로트·날짜 코드 후보",
        "SUPPLY_VOLTAGE": "공급 전압 후보",
        "MISSION_NAME": "임무명 후보",
        "ORBIT_REGIME": "궤도 유형 후보",
        "ORBIT_ALTITUDE": "궤도 고도 후보",
        "ORBIT_INCLINATION": "궤도 경사각 후보",
        "MISSION_DURATION": "임무 기간 후보",
        "SHIELDING_THICKNESS": "차폐 두께 후보",
    }
    facts = [
        f"{labels.get(item['field'], item['field'])}: {item['value']}"
        for item in receipt.get("candidates", [])
    ]
    fields = set(receipt.get("candidate_fields", []))
    mission_fields = {
        "MISSION_NAME",
        "ORBIT_REGIME",
        "ORBIT_ALTITUDE",
        "ORBIT_INCLINATION",
        "MISSION_DURATION",
        "SHIELDING_THICKNESS",
    }
    part_fields = {"ORDERABLE_PART_NUMBER", "MANUFACTURER", "SUPPLY_VOLTAGE"}
    radiation_fields = {
        "TID_DOSE",
        "DOSE_RATE",
        "SEE_LET",
        "SEE_CROSS_SECTION",
        "PARTICLE_FLUENCE",
        "PARTICLE_ENERGY",
        "EVIDENCE_EVENT_MENTION",
    }
    if fields & mission_fields and not fields & (part_fields | radiation_fields):
        return {
            "headline": "임무 조건 후보를 추출했지만 방사선 환경과 연결되지 않아 HOLD했습니다.",
            "problem_location": "2 · 임무 조건과 방사선 환경 연결",
            "confirmed_facts": facts,
            "blocking_reason": (
                "궤도·기간은 확인했지만 같은 임무의 방사선 환경 계산 결과가 없습니다."
            ),
            "next_action": (
                "출처가 확인된 방사선 환경 계산을 같은 Mission Case에 연결합니다."
            ),
        }
    if fields & part_fields and not fields & radiation_fields:
        return {
            "headline": "부품 명세 후보를 추출했지만 방사선 시험과 연결되지 않아 HOLD했습니다.",
            "problem_location": "3 · 부품 명세와 시험 근거 연결",
            "confirmed_facts": facts,
            "blocking_reason": (
                "상용 제품 특성은 확인했지만 정확한 주문형번의 TID·SEE 시험 근거가 없습니다."
            ),
            "next_action": (
                "동일 주문형번·공정·로트의 시험 자료를 연결하고 시험 조건을 대조합니다."
            ),
        }
    failed_checks = receipt.get("partial_evaluation", {}).get("failed_checks", [])
    if failed_checks:
        return {
            "headline": "확인 가능한 값은 검사했고 입력한 부품 식별값은 문서에서 찾지 못했습니다.",
            "problem_location": "부품·시험 근거 검토 · 정확한 부품 식별",
            "confirmed_facts": facts,
            "blocking_reason": "입력한 주문형번 또는 제조사 후보가 원문과 일치하지 않습니다.",
            "next_action": (
                "문서에 적힌 실제 주문형번·제조사를 입력해 다시 대조하고, 승인된 부품 목록(BOM)과 연결합니다."
            ),
        }
    return {
        "headline": "후보를 추출했지만 승인 대상과 대조되지 않아 HOLD했습니다.",
        "problem_location": "4 · 승인 대상 대조",
        "confirmed_facts": facts,
        "blocking_reason": (
            "승인된 비교 대상 부품 정보가 없습니다. 공정·다이·로트, 시험 조건, "
            "임무 적용성과 파괴성 단일사건 시험 범위도 확인 전입니다."
        ),
        "next_action": (
            "승인된 부품 목록을 연결하고 후보의 정확한 식별 정보와 시험 조건을 대조합니다."
        ),
    }


def intake_document(
    path: Path,
    *,
    expected_part: str,
    manufacturer: str | None = None,
    local_review_rights_confirmed: bool = False,
) -> dict[str, Any]:
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_file():
            return fail_closed_receipt("DOCUMENT_NOT_A_FILE")
        size = resolved.stat().st_size
        if size <= 0 or size > MAX_BYTES:
            return fail_closed_receipt("DOCUMENT_SIZE_OUT_OF_RANGE")
        content = resolved.read_bytes()
        text, mime_type, engine, page_count = extract_text(resolved, content)
    except FileNotFoundError:
        return fail_closed_receipt("DOCUMENT_NOT_FOUND")
    except OSError:
        return fail_closed_receipt("DOCUMENT_READ_FAILED")
    except ExtractionUnavailable as exc:
        return fail_closed_receipt(str(exc))

    if not text or len(text) > MAX_TEXT_CHARACTERS:
        return fail_closed_receipt("EXTRACTED_TEXT_SIZE_OUT_OF_RANGE")

    content_hash = _sha256(content)
    text_hash = _sha256(text.encode("utf-8"))
    locator_id = "local-doc-" + _stable_suffix(content)
    rights_status = "ALLOWED" if local_review_rights_confirmed else "UNRESOLVED"
    candidates = extract_candidates(text, expected_part, manufacturer)
    document = {
        "candidate_class": "ACTUAL_CANDIDATE",
        "mime_type": mime_type,
        "locator": {
            "locator_id": locator_id,
            "locator_type": "LOCAL_PRIVATE_REFERENCE",
            "reference": "evidence://" + locator_id,
        },
        "content_bytes": content,
        "extracted_text": text,
        "declared_content_sha256": content_hash,
        "declared_text_sha256": text_hash,
        "rights": [
            {
                "action": action,
                "status": rights_status,
                "scope_locator_id": locator_id,
            }
            for action in ("LOCATOR", "READ_LOCAL", "PROCESS_LOCAL", "DISPLAY_INTERNAL")
        ],
        "candidates": candidates,
        "claimed_use_status": "NOT_FOR_DECISION",
        "claimed_assurance_decision": "HOLD",
        "claimed_approval_status": "NOT_EVALUATED",
    }
    intake = evaluate_document_intake(document)
    receipt = {
        "contract_version": "LOCAL_DOCUMENT_EXTRACTION_RECEIPT_1.0.0",
        "processing_status": intake["processing_status"],
        "extraction_status": (
            "CANDIDATES_READY_FOR_REVIEW"
            if intake["candidates"]
            else "HOLD_NOT_EXTRACTED"
        ),
        "source": {
            "mime_type": mime_type,
            "byte_count": len(content),
            "page_count": page_count,
            "content_sha256": content_hash,
            "text_sha256": text_hash,
            "extraction_engine": engine,
            "raw_path_included": False,
            "raw_text_included": False,
        },
        "candidate_count": len(intake["candidates"]),
        "candidate_fields": [item["field"] for item in intake["candidates"]],
        "candidates": intake["candidates"],
        "blocker_codes": intake["blocker_codes"],
        "approval_status": "NOT_EVALUATED",
        "use_status": "NOT_FOR_DECISION",
        "assurance_decision": "HOLD",
        "suitability": "NOT_EVALUATED",
        "used_for_decision": False,
    }
    receipt["partial_evaluation"] = _partial_evaluation(
        receipt, expected_part, manufacturer
    )
    receipt["review_summary"] = review_summary(receipt)
    _enrich_review_summary(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--expected-part", required=True)
    parser.add_argument("--manufacturer")
    parser.add_argument("--confirm-local-review-rights", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = intake_document(
        args.document,
        expected_part=args.expected_part,
        manufacturer=args.manufacturer,
        local_review_rights_confirmed=args.confirm_local_review_rights,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "processing_status": receipt["processing_status"],
                "extraction_status": receipt["extraction_status"],
                "candidate_count": receipt["candidate_count"],
                "assurance_decision": receipt["assurance_decision"],
                "review_summary": receipt["review_summary"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
