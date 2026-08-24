"""Compose source-artifact and numerical-reference receipts safely."""

from __future__ import annotations

from typing import Any, Mapping

from .published_artifact_gate import evaluate_published_artifact
from .reference_comparison import assess_reference_comparison


CONTRACT_VERSION = "PUBLISHED_REFERENCE_PACKAGE_1.0.0"
SOURCE_BLOCKERS = frozenset(
    {"SOURCE_ARTIFACT_MANIFEST_MISSING", "RIGHTS_SCOPE_UNRESOLVED"}
)


def _comparison_source_hash(record: Any) -> str | None:
    if not isinstance(record, Mapping):
        return None
    published = record.get("published_observation")
    if not isinstance(published, Mapping):
        return None
    source = published.get("source")
    if not isinstance(source, Mapping):
        return None
    value = source.get("observed_artifact_sha256")
    return value if isinstance(value, str) else None


def assess_published_reference_package(
    comparison_record: Any,
    source_candidate: Any,
    content_bytes: Any,
    *,
    trusted_anchors: Any = None,
) -> dict[str, Any]:
    """Bind a published source to a comparison without promoting suitability."""

    source_receipt = evaluate_published_artifact(
        source_candidate,
        content_bytes,
        trusted_anchors=trusted_anchors,
    )
    comparison_receipt = assess_reference_comparison(comparison_record)
    binding = source_receipt.get("artifact_binding")
    source_ready = (
        source_receipt.get("processing_status") == "VALID"
        and source_receipt.get("issuance_status")
        == "READY_FOR_REFERENCE_REVIEW"
        and isinstance(binding, Mapping)
        and binding.get("content_sha256")
        == _comparison_source_hash(comparison_record)
    )

    comparison_codes = set(comparison_receipt.get("stable_codes", []))
    resolved_codes = sorted(SOURCE_BLOCKERS & comparison_codes) if source_ready else []
    remaining_codes = comparison_codes - set(resolved_codes)
    package_codes: set[str] = set()
    if not source_ready:
        package_codes.add("SOURCE_PACKAGE_BINDING_FAILED")
        package_codes.update(source_receipt.get("stable_codes", []))
    if comparison_receipt.get("processing_status") != "VALID":
        package_codes.add("COMPARISON_RECEIPT_INVALID")
    package_codes.update(remaining_codes)

    return {
        "contract_version": CONTRACT_VERSION,
        "processing_status": (
            "VALID"
            if source_ready
            and comparison_receipt.get("processing_status") == "VALID"
            else "INVALID_INPUT"
        ),
        "package_status": (
            "SOURCE_READY_COMPARISON_BLOCKED"
            if source_ready
            and comparison_receipt.get("processing_status") == "VALID"
            else "PACKAGE_NOT_READY"
        ),
        "comparison_status": "NOT_COMPARABLE",
        "assurance_decision": "HOLD",
        "used_for_decision": False,
        "source_receipt": source_receipt,
        "comparison_receipt": comparison_receipt,
        "resolved_source_codes": resolved_codes,
        "remaining_blocking_codes": sorted(remaining_codes),
        "stable_codes": sorted(package_codes),
    }
