#!/usr/bin/env python3
"""Build bounded synthetic document-intake receipts for the offline demo."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spectra_document_adapter import evaluate_document_intake  # noqa: E402


OUTPUT_PATH = REPO_ROOT / "demo" / "data" / "document-intake-receipts.json"
SYNTHETIC_TEXT = (
    "SYNTHETIC DOCUMENT CONTROL — NOT A REAL DATASHEET\n"
    "Manufacturer candidate: SYNTHETIC-MFR\n"
    "Orderable part candidate: SYNTHETIC-PN-001\n"
)


def _sha256(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _candidate(candidate_id: str, field: str, value: str) -> dict:
    start = SYNTHETIC_TEXT.index(value)
    return {
        "candidate_id": candidate_id,
        "field": field,
        "value": value,
        "unit": None,
        "text_start": start,
        "text_end": start + len(value),
    }


def build_receipts() -> dict:
    content = SYNTHETIC_TEXT.encode("utf-8")
    locator_id = "SYNTHETIC-DOC-001"
    document = {
        "candidate_class": "SYNTHETIC_CONTROL",
        "mime_type": "text/plain",
        "locator": {
            "locator_id": locator_id,
            "locator_type": "SYNTHETIC_REFERENCE",
            "reference": "synthetic://document-control-001",
        },
        "content_bytes": content,
        "extracted_text": SYNTHETIC_TEXT,
        "declared_content_sha256": _sha256(content),
        "declared_text_sha256": _sha256(content),
        "rights": [
            {
                "action": action,
                "status": "SYNTHETIC_ONLY",
                "scope_locator_id": locator_id,
            }
            for action in sorted(
                {"LOCATOR", "READ_LOCAL", "PROCESS_LOCAL", "DISPLAY_INTERNAL"}
            )
        ],
        "candidates": [
            _candidate("SYN-CANDIDATE-MFR", "MANUFACTURER", "SYNTHETIC-MFR"),
            _candidate(
                "SYN-CANDIDATE-PN", "ORDERABLE_PART_NUMBER", "SYNTHETIC-PN-001"
            ),
        ],
        "claimed_use_status": "NOT_FOR_DECISION",
        "claimed_assurance_decision": "HOLD",
        "claimed_approval_status": "NOT_EVALUATED",
    }
    return {
        "dataset_status": "SYNTHETIC_CONTROL",
        "ocr_performed": False,
        "llm_extraction_performed": False,
        "receipts": [evaluate_document_intake(document)],
    }


def main() -> None:
    OUTPUT_PATH.write_text(
        json.dumps(build_receipts(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
