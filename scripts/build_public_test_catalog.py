#!/usr/bin/env python3
"""Build the sanitized public test catalog and its deterministic audit chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_evidence_console import _add_bundled_pdf_packages  # noqa: E402

_add_bundled_pdf_packages()

from intake_local_document_candidate import intake_document  # noqa: E402


DEFAULT_GENERATED_AT = "2026-08-25T08:00:00Z"
STAGES = ("INGEST", "PARSE", "ROLE_LINK", "CONDITION_LINK", "FINAL_GATE")
BLOCKER_PRIORITY = (
    "PROMPT_INJECTION_PATTERN_DETECTED",
    "RIGHTS_PROCESS_LOCAL_UNRESOLVED",
    "RIGHTS_READ_LOCAL_UNRESOLVED",
    "PDF_TEXT_EXTRACTION_FAILED",
    "PDF_EXTRACTOR_UNAVAILABLE",
    "DOCUMENT_TYPE_UNSUPPORTED",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def source_urls(path: Path) -> list[str]:
    if path.suffix.lower() not in {".txt", ".json"}:
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return [item.rstrip(".,)") for item in re.findall(r"https://\S+", text)]


def inferred_role(filename: str) -> str:
    if "임무계획" in filename:
        return "MISSION_PLAN"
    if "부품명세" in filename:
        return "PART_SPEC"
    if "실제공개값" in filename:
        return "RADIATION_TEST"
    return "SYNTHETIC_CONTROL"


def specific_blocker(codes: list[str], fallback: str) -> str:
    for code in BLOCKER_PRIORITY:
        if code in codes:
            return code
    for code in codes:
        if code not in {"ACTUAL_CANDIDATE_NOT_ISSUED", "NOT_FOR_DECISION"}:
            return code
    return fallback


def stage_result(
    role: str, processing_status: str, candidate_fields: list[str], filename: str
) -> tuple[dict[str, str], str, str]:
    stages = {stage: "NOT_REACHED" for stage in STAGES}
    stages["INGEST"] = "PASS" if processing_status == "VALID" else processing_status
    if processing_status != "VALID":
        return stages, "INGEST", processing_status

    stages["PARSE"] = "PASS" if candidate_fields else "NO_CANDIDATE"
    if not candidate_fields:
        return stages, "PARSE", "NO_REVIEWABLE_CANDIDATE"

    stages["ROLE_LINK"] = "PASS"
    if role == "MISSION_PLAN":
        stages["CONDITION_LINK"] = "PASS"
        return stages, "ENVIRONMENT_LINK", "RADIATION_ENVIRONMENT_MISSING"
    if role == "PART_SPEC":
        stages["CONDITION_LINK"] = "NOT_REACHED"
        return stages, "EVIDENCE_LINK", "RADIATION_TEST_EVIDENCE_MISSING"
    if role == "RADIATION_TEST":
        stages["CONDITION_LINK"] = "CANDIDATE_ONLY"
        return stages, "EXACT_IDENTITY", "APPROVED_BOM_TARGET_MISSING"

    stages["CONDITION_LINK"] = "CANDIDATE_ONLY"
    stages["FINAL_GATE"] = "HOLD"
    if filename.startswith("05_"):
        return stages, "INGEST", "PROMPT_INJECTION_PATTERN_DETECTED"
    return stages, "FINAL_GATE", "SYNTHETIC_OR_INCOMPLETE_EVIDENCE"


def build_catalog(generated_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture_root = ROOT / "demo" / "test-data"
    manifest = json.loads((fixture_root / "manifest.json").read_text(encoding="utf-8"))
    documents: list[dict[str, Any]] = []
    audit_events: list[dict[str, Any]] = []
    previous_hash = "sha256:" + "0" * 64

    for index, case in enumerate(manifest["cases"], start=1):
        path = fixture_root / case["file"]
        role = case.get("document_role", inferred_role(case["file"]))
        manufacturer = case.get("manufacturer")
        if "manufacturer" not in case and role != "MISSION_PLAN":
            manufacturer = manifest.get("manufacturer")
        receipt = intake_document(
            path,
            expected_part=case.get("expected_part", manifest["expected_part"]),
            manufacturer=manufacturer,
            local_review_rights_confirmed=case["rights"],
        )
        source_class = case.get(
            "source_classification",
            "SYNTHETIC_TEST_FIXTURE",
        )
        stages, stopped_at, first_blocker = stage_result(
            role,
            receipt["processing_status"],
            receipt["candidate_fields"],
            case["file"],
        )
        if receipt["processing_status"] != "VALID" and receipt["blocker_codes"]:
            first_blocker = specific_blocker(receipt["blocker_codes"], first_blocker)
        document_id = f"DOC-{index:03d}"
        content_sha256 = sha256_bytes(path.read_bytes())
        row = {
            "document_id": document_id,
            "title": path.stem,
            "filename": path.name,
            "document_role": role,
            "source_classification": source_class,
            "source_urls": source_urls(path),
            "content_sha256": content_sha256,
            "processing_status": receipt["processing_status"],
            "candidate_count": receipt["candidate_count"],
            "candidate_fields": receipt["candidate_fields"],
            "partial_evaluation": {
                "validated_check_count": len(
                    receipt["partial_evaluation"]["validated_checks"]
                ),
                "failed_check_count": len(
                    receipt["partial_evaluation"]["failed_checks"]
                ),
                "not_evaluated_check_count": len(
                    receipt["partial_evaluation"]["not_evaluated_checks"]
                ),
                "hold_agent": receipt["partial_evaluation"]["hold_agent"],
                "validation_results": receipt["review_summary"]["validation_results"],
            },
            "stages": stages,
            "stopped_at": stopped_at,
            "first_blocker": first_blocker,
            "pipeline_result": "COMPLETED_WITH_HOLD"
            if stages["FINAL_GATE"] == "HOLD"
            else "STOPPED_FAIL_CLOSED",
            "assurance_decision": "HOLD",
        }
        documents.append(row)
        event_core = {
            "sequence": index,
            "event_type": "DOCUMENT_EVALUATED",
            "document_id": document_id,
            "content_sha256": content_sha256,
            "processing_status": receipt["processing_status"],
            "first_blocker": first_blocker,
            "hold_agent": receipt["partial_evaluation"]["hold_agent"],
            "validated_check_count": len(
                receipt["partial_evaluation"]["validated_checks"]
            ),
            "assurance_decision": "HOLD",
            "previous_event_hash": previous_hash,
        }
        event_hash = sha256_bytes(canonical(event_core))
        audit_events.append({**event_core, "event_hash": event_hash})
        previous_hash = event_hash

    bundles = [
        {
            "bundle_id": "BUNDLE-SYNTHETIC-CORE",
            "label": "합성 임무·부품·시험 3축 Core 회귀",
            "data_class": "SYNTHETIC",
            "documents": ["demo/data/mvp-product-result.json"],
            "reached_stage": "FINAL_GATE",
            "pipeline_result": "PIPELINE_COMPLETE",
            "first_blocker": "SYNTHETIC_ONLY",
            "hold_agent": "ASSURANCE_AGENT",
            "assurance_decision": "HOLD",
        },
        {
            "bundle_id": "BUNDLE-LANDSAT-MICROCHIP-NASA-MICRON",
            "label": "Landsat 9 + 23LC1024 명세 + NASA Micron TID",
            "data_class": "PUBLISHED_SOURCE_SUMMARY",
            "documents": ["DOC-013", "DOC-015", "DOC-010"],
            "reached_stage": "EXACT_IDENTITY",
            "pipeline_result": "STOPPED_FAIL_CLOSED",
            "first_blocker": "EXACT_PART_IDENTITY_MISMATCH",
            "hold_agent": "PARTS_AGENT",
            "assurance_decision": "HOLD",
        },
        {
            "bundle_id": "BUNDLE-LANDSAT-MICROCHIP",
            "label": "Landsat 9 + 23LC1024 명세",
            "data_class": "PUBLISHED_SOURCE_SUMMARY",
            "documents": ["DOC-013", "DOC-015"],
            "reached_stage": "EVIDENCE_LINK",
            "pipeline_result": "STOPPED_FAIL_CLOSED",
            "first_blocker": "RADIATION_TEST_EVIDENCE_MISSING",
            "hold_agent": "PARTS_AGENT",
            "assurance_decision": "HOLD",
        },
        {
            "bundle_id": "BUNDLE-SENTINEL-ESA-MICRON",
            "label": "Sentinel-2 + ESA Micron TID/SEE",
            "data_class": "PUBLISHED_SOURCE_SUMMARY",
            "documents": ["DOC-014", "DOC-012"],
            "reached_stage": "PART_SPEC_LINK",
            "pipeline_result": "STOPPED_FAIL_CLOSED",
            "first_blocker": "PART_SPECIFICATION_MISSING",
            "hold_agent": "PARTS_AGENT",
            "assurance_decision": "HOLD",
        },
    ]

    catalog = {
        "contract_version": "SPECTRA_PUBLIC_TEST_CATALOG_1.0.0",
        "generated_at": generated_at,
        "data_boundary": (
            "Public-source summaries and synthetic controls only. No raw proprietary "
            "document, mission approval, or radiation assurance is published."
        ),
        "stage_order": list(STAGES),
        "documents": documents,
        "bundles": bundles,
        "summary": {
            "document_count": len(documents),
            "published_summary_count": sum(
                item["source_classification"] == "PUBLISHED_SOURCE_SUMMARY"
                for item in documents
            ),
            "pipeline_complete_count": sum(
                item["pipeline_result"] == "COMPLETED_WITH_HOLD" for item in documents
            ),
            "assurance_approved_count": 0,
        },
    }
    catalog_hash = sha256_bytes(canonical(catalog))
    submission_core = {
        "sequence": len(audit_events) + 1,
        "event_type": "CATALOG_SUBMITTED",
        "catalog_sha256": catalog_hash,
        "document_count": len(documents),
        "bundle_count": len(bundles),
        "assurance_approved_count": 0,
        "previous_event_hash": previous_hash,
    }
    submission_hash = sha256_bytes(canonical(submission_core))
    audit_events.append({**submission_core, "event_hash": submission_hash})
    audit = {
        "contract_version": "SPECTRA_PUBLIC_TEST_AUDIT_1.0.0",
        "generated_at": generated_at,
        "hash_algorithm": "SHA-256",
        "canonicalization": "UTF-8 JSON; sorted keys; compact separators",
        "catalog_sha256": catalog_hash,
        "chain_head": submission_hash,
        "events": audit_events,
    }
    return catalog, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "demo" / "data" / "test-catalog"
    )
    args = parser.parse_args()
    catalog, audit = build_catalog(args.generated_at)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "audit-log.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
