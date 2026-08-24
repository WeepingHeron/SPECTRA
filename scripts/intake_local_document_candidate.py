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
    }
    receipt["review_summary"] = review_summary(receipt)
    return receipt


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
    }
    facts = [
        f"{labels.get(item['field'], item['field'])}: {item['value']}"
        for item in receipt.get("candidates", [])
    ]
    return {
        "headline": "후보를 추출했지만 승인 대상과 대조되지 않아 HOLD했습니다.",
        "problem_location": "4 · 승인 대상 대조",
        "confirmed_facts": facts,
        "blocking_reason": (
            "비교할 승인 BOM target이 없습니다. 공정·다이·로트, 시험 조건, "
            "임무 적용성과 파괴성 SEE coverage도 확인 전입니다."
        ),
        "next_action": (
            "사람이 승인 BOM을 연결하고 후보의 identity와 시험 조건을 대조합니다."
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
    receipt["review_summary"] = review_summary(receipt)
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
