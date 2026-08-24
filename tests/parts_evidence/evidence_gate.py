"""Fail-closed Workstream 40 test gate.

This module is deliberately scoped to ``tests/parts_evidence``.  It is not the
production PART_TEST_EVIDENCE v2 contract and must not be imported by runtime
code.  It turns the H05 field map and attack specification into executable,
stable test behavior without modifying the common schemas.
"""

from __future__ import annotations

import copy
import hashlib
import json
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


EVENT_TYPES = ("TID", "SEU", "SEL", "SEB", "SEGR")
DESTRUCTIVE_EVENTS = {"SEL", "SEB", "SEGR"}
RIGHTS_ACTIONS = (
    "LOCATOR",
    "FETCH",
    "PRIVATE_STORE",
    "PROCESS_LOCAL_AI",
    "DISPLAY_INTERNAL",
    "DISPLAY_EXTERNAL",
    "REDISTRIBUTE",
    "COMMERCIAL_USE",
)
IDENTITY_FIELDS = (
    "manufacturer",
    "exact_part_number",
    "package",
    "grade",
    "process",
    "die",
    "lot",
    "generic_part_number",
    "family_relation",
)

STRUCTURAL_CODES = {
    "MALFORMED_JSON",
    "MALFORMED_RECORD_TYPE",
    "MALFORMED_FIELD_TYPE",
    "UNKNOWN_FIELD",
    "REQUIRED_FIELD_MISSING",
    "INVALID_ENUM_VALUE",
    "INVALID_CLAIM",
    "CONFLICTING_ALTERNATIVES_INSUFFICIENT",
    "CONFLICTING_ALTERNATIVE_DUPLICATE",
    "CONFLICTING_ALTERNATIVE_LOCATOR_MISSING",
}
PROVENANCE_CODES = {
    "SOURCE_LOCATOR_MISSING",
    "INVALID_SOURCE_LOCATOR",
    "ARTIFACT_HASH_MISSING",
    "ARTIFACT_HASH_MISMATCH",
    "ARTIFACT_PATH_INVALID",
    "ARTIFACT_ACCESS_ERROR",
    "BOM_APPROVAL_TARGET_MISMATCH",
    "BOM_APPROVAL_HISTORY_INVALID",
    "REVIEW_HISTORY_INVALID",
}


@dataclass(frozen=True)
class GateResult:
    processing_status: str
    identity_status: str
    applicability_status: str
    assurance_decision: str
    used_for_decision: bool
    recommendation: None
    codes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "processing_status": self.processing_status,
            "identity_status": self.identity_status,
            "applicability_status": self.applicability_status,
            "assurance_decision": self.assurance_decision,
            "used_for_decision": self.used_for_decision,
            "recommendation": self.recommendation,
            "codes": list(self.codes),
        }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _add(codes: list[str], *values: str) -> None:
    for value in values:
        if value not in codes:
            codes.append(value)


def _object(
    value: Any,
    codes: list[str],
    field: str,
    allowed: Iterable[str],
    required: Iterable[str] = (),
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _add(codes, "MALFORMED_FIELD_TYPE")
        return None
    allowed_set = set(allowed)
    if any(key not in allowed_set for key in value):
        _add(codes, "UNKNOWN_FIELD")
    if any(key not in value for key in required):
        _add(codes, "REQUIRED_FIELD_MISSING")
    return value


def _claim_value(claim: Any) -> str | None:
    if not isinstance(claim, dict) or claim.get("status") != "VERIFIED":
        return None
    value = claim.get("value")
    if not isinstance(value, dict):
        return None
    canonical = value.get("canonical")
    return canonical if isinstance(canonical, str) else None


def _claim_raw(claim: Any) -> str | None:
    if not isinstance(claim, dict) or claim.get("status") != "VERIFIED":
        return None
    value = claim.get("value")
    if not isinstance(value, dict):
        return None
    raw = value.get("raw")
    return raw if isinstance(raw, str) else None


def _validate_claim(
    claim: Any, codes: list[str], locator_ids: set[str]
) -> None:
    obj = _object(
        claim,
        codes,
        "claim",
        ("status", "value", "locator_ids", "alternatives"),
        ("status",),
    )
    if obj is None:
        return
    status = obj.get("status")
    if status not in {"VERIFIED", "NOT_REPORTED", "CONFLICTING"}:
        _add(codes, "INVALID_CLAIM")
        return
    if status == "VERIFIED":
        value = _object(
            obj.get("value"), codes, "claim.value", ("raw", "canonical"), ("raw", "canonical")
        )
        if value is not None and not all(
            isinstance(value.get(key), str) and value.get(key) for key in ("raw", "canonical")
        ):
            _add(codes, "INVALID_CLAIM")
        refs = obj.get("locator_ids")
        if not isinstance(refs, list) or not refs:
            _add(codes, "SOURCE_LOCATOR_MISSING")
        elif any(not isinstance(ref, str) or ref not in locator_ids for ref in refs):
            _add(codes, "INVALID_SOURCE_LOCATOR")
    elif status == "NOT_REPORTED":
        if "value" in obj or "alternatives" in obj:
            _add(codes, "INVALID_CLAIM")
    else:
        alternatives = obj.get("alternatives")
        if not isinstance(alternatives, list) or len(alternatives) < 2:
            _add(codes, "CONFLICTING_ALTERNATIVES_INSUFFICIENT")
            return
        values: set[str] = set()
        for alternative in alternatives:
            alt = _object(
                alternative,
                codes,
                "claim.alternative",
                ("alternative_id", "value", "source_claim_id", "locator_ids"),
                ("alternative_id", "value", "source_claim_id", "locator_ids"),
            )
            if alt is None:
                continue
            value = alt.get("value")
            if not isinstance(value, str) or not value:
                _add(codes, "INVALID_CLAIM")
            elif value in values:
                _add(codes, "CONFLICTING_ALTERNATIVE_DUPLICATE")
            else:
                values.add(value)
            refs = alt.get("locator_ids")
            if not isinstance(refs, list) or not refs:
                _add(codes, "CONFLICTING_ALTERNATIVE_LOCATOR_MISSING")
            elif any(not isinstance(ref, str) or ref not in locator_ids for ref in refs):
                _add(codes, "INVALID_SOURCE_LOCATOR")


def _bom_projection(record: dict[str, Any]) -> dict[str, Any]:
    bom = record.get("bom") if isinstance(record.get("bom"), dict) else {}
    approval = bom.get("approval") if isinstance(bom.get("approval"), dict) else {}
    return {
        "version": approval.get("version"),
        "component_pointer": approval.get("component_pointer"),
        "identity": bom.get("identity"),
    }


def materialize_synthetic_record(
    record: dict[str, Any], fixture_root: Path
) -> dict[str, Any]:
    """Compute hashes only for explicit synthetic controls and fixture bytes."""

    result = copy.deepcopy(record)
    if result.get("data_class") != "SYNTHETIC_CONTROL":
        return result
    bom = result.get("bom")
    if isinstance(bom, dict) and isinstance(bom.get("approval"), dict):
        approval = bom["approval"]
        if approval.get("target_hash") == "AUTO_COMPUTE_SYNTHETIC":
            approval["target_hash"] = _sha256(_canonical_bytes(_bom_projection(result)))
    artifacts = result.get("artifacts")
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            if artifact.get("sha256") == "AUTO_COMPUTE_SYNTHETIC":
                path = fixture_root / str(artifact.get("relative_path", ""))
                artifact["sha256"] = _sha256(path.read_bytes())
    review = result.get("review")
    if isinstance(review, dict) and isinstance(review.get("history"), list):
        previous = None
        for sequence, entry in enumerate(review["history"]):
            if not isinstance(entry, dict):
                continue
            entry["sequence"] = sequence
            entry["previous_entry_hash"] = previous
            projection = {key: value for key, value in entry.items() if key != "entry_hash"}
            entry["entry_hash"] = _sha256(_canonical_bytes(projection))
            previous = entry["entry_hash"]
        review["history_head_hash"] = previous
    return result


def validate_json_text(text: str, fixture_root: Path) -> GateResult:
    try:
        record = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return _result(["MALFORMED_JSON"], "PARTIAL_UNRESOLVED", "NOT_EVALUATED")
    return validate_record(record, fixture_root)


def validate_record(record: Any, fixture_root: Path) -> GateResult:
    codes: list[str] = []
    if not isinstance(record, dict):
        return _result(["MALFORMED_RECORD_TYPE"], "PARTIAL_UNRESOLVED", "NOT_EVALUATED")

    top = _object(
        record,
        codes,
        "record",
        (
            "contract_version",
            "kind",
            "data_class",
            "usage",
            "record_purpose",
            "component_id",
            "bom",
            "tested_identity",
            "sources",
            "artifacts",
            "rights",
            "review",
            "event_coverage",
            "applicability",
            "decision",
        ),
        (
            "contract_version",
            "kind",
            "data_class",
            "usage",
            "record_purpose",
            "component_id",
            "bom",
            "tested_identity",
            "sources",
            "artifacts",
            "rights",
            "review",
            "event_coverage",
            "applicability",
            "decision",
        ),
    )
    assert top is not None
    if record.get("contract_version") != "W40_TEST_CONTRACT_1.0.0" or record.get("kind") != "PART_TEST_EVIDENCE_TEST_GATE":
        _add(codes, "INVALID_ENUM_VALUE")
    if record.get("data_class") not in {"SYNTHETIC_CONTROL", "DISCOVERY_CANDIDATE"}:
        _add(codes, "INVALID_ENUM_VALUE")
    if record.get("usage") != "DEMO_ONLY" or record.get("record_purpose") != "DISCOVERY_CANDIDATE":
        _add(codes, "DECISION_USE_FORBIDDEN")
    if record.get("data_class") == "SYNTHETIC_CONTROL":
        _add(codes, "SYNTHETIC_DEMO_ONLY")

    sources = record.get("sources")
    locator_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        _add(codes, "MALFORMED_FIELD_TYPE")
        sources = []
    for source in sources:
        src = _object(
            source,
            codes,
            "source",
            ("source_id", "document_id", "issuer", "revision", "uri", "locators"),
            ("source_id", "document_id", "issuer", "revision", "uri", "locators"),
        )
        if src is None:
            continue
        locators = src.get("locators")
        if not isinstance(locators, list):
            _add(codes, "MALFORMED_FIELD_TYPE")
            continue
        for locator in locators:
            loc = _object(
                locator,
                codes,
                "locator",
                ("locator_id", "media_type", "target", "artifact_id"),
                ("locator_id", "media_type", "target"),
            )
            if loc is None:
                continue
            locator_id = loc.get("locator_id")
            if not isinstance(locator_id, str) or not locator_id or locator_id in locator_ids:
                _add(codes, "INVALID_SOURCE_LOCATOR")
            else:
                locator_ids.add(locator_id)

    bom = _object(
        record.get("bom"), codes, "bom", ("approval", "identity"), ("approval", "identity")
    )
    tested_identity = _object(
        record.get("tested_identity"),
        codes,
        "tested_identity",
        IDENTITY_FIELDS,
        IDENTITY_FIELDS,
    )
    bom_identity: dict[str, Any] = {}
    approval: dict[str, Any] = {}
    if bom is not None:
        approval = _object(
            bom.get("approval"),
            codes,
            "bom.approval",
            ("status", "version", "component_pointer", "target_hash", "history_anchor"),
            ("status",),
        ) or {}
        bom_identity = _object(
            bom.get("identity"), codes, "bom.identity", IDENTITY_FIELDS, IDENTITY_FIELDS
        ) or {}
    for identity in (bom_identity, tested_identity or {}):
        for field in IDENTITY_FIELDS:
            if field in identity:
                _validate_claim(identity[field], codes, locator_ids)

    approval_status = approval.get("status")
    if approval_status == "NOT_PROVIDED" or not approval_status:
        _add(
            codes,
            "BOM_APPROVAL_MISSING",
            "BOM_APPROVAL_TARGET_MISSING",
            "BOM_APPROVAL_HISTORY_INVALID",
        )
    elif approval_status not in {"SYNTHETIC_CONTROL", "APPROVED"}:
        _add(codes, "INVALID_ENUM_VALUE")
    else:
        for field in ("version", "component_pointer", "target_hash", "history_anchor"):
            if not isinstance(approval.get(field), str) or not approval.get(field):
                _add(codes, "BOM_APPROVAL_MISSING")
        expected_target = _sha256(_canonical_bytes(_bom_projection(record)))
        if approval.get("target_hash") != expected_target:
            _add(codes, "BOM_APPROVAL_TARGET_MISMATCH")

    artifacts = record.get("artifacts")
    artifact_ids: set[str] = set()
    if not isinstance(artifacts, list):
        _add(codes, "MALFORMED_FIELD_TYPE")
        artifacts = []
    for artifact in artifacts:
        art = _object(
            artifact,
            codes,
            "artifact",
            ("artifact_id", "status", "relative_path", "sha256", "source_id"),
            ("artifact_id", "status", "source_id"),
        )
        if art is None:
            continue
        artifact_id = art.get("artifact_id")
        if isinstance(artifact_id, str):
            artifact_ids.add(artifact_id)
        status = art.get("status")
        if status == "NOT_PROVIDED":
            _add(codes, "RAW_MANIFEST_REFERENCE_MISSING")
            continue
        if status != "PRESENT_SYNTHETIC":
            _add(codes, "INVALID_ENUM_VALUE")
            continue
        relative_path = art.get("relative_path")
        if not isinstance(relative_path, str) or not relative_path:
            _add(codes, "ARTIFACT_PATH_INVALID")
            continue
        try:
            root = fixture_root.resolve()
            path = (fixture_root / relative_path).resolve()
            path.relative_to(root)
        except ValueError:
            _add(codes, "ARTIFACT_PATH_INVALID")
            continue
        except OSError:
            _add(codes, "ARTIFACT_ACCESS_ERROR")
            continue
        if not isinstance(art.get("sha256"), str) or not art.get("sha256"):
            _add(codes, "ARTIFACT_HASH_MISSING")
            continue
        try:
            file_stat = path.stat()
        except FileNotFoundError:
            _add(codes, "ARTIFACT_HASH_MISMATCH")
            continue
        except OSError:
            _add(codes, "ARTIFACT_ACCESS_ERROR")
            continue
        if not stat.S_ISREG(file_stat.st_mode):
            _add(codes, "ARTIFACT_HASH_MISMATCH")
            continue
        try:
            artifact_bytes = path.read_bytes()
        except FileNotFoundError:
            _add(codes, "ARTIFACT_HASH_MISMATCH")
            continue
        except OSError:
            _add(codes, "ARTIFACT_ACCESS_ERROR")
            continue
        if art.get("sha256") != _sha256(artifact_bytes):
            _add(codes, "ARTIFACT_HASH_MISMATCH")

    rights = _object(
        record.get("rights"),
        codes,
        "rights",
        ("status", "scope", "actions"),
        ("status", "scope", "actions"),
    )
    if rights is not None:
        actions = rights.get("actions")
        if not isinstance(actions, dict):
            _add(codes, "MALFORMED_FIELD_TYPE")
        else:
            if any(key not in RIGHTS_ACTIONS for key in actions):
                _add(codes, "UNKNOWN_FIELD")
            for action in RIGHTS_ACTIONS:
                if action not in actions:
                    _add(codes, "RIGHTS_ACTION_MISSING", "RIGHTS_UNRESOLVED")
                elif actions[action] not in {"SYNTHETIC_ONLY", "ALLOWED", "UNCONFIRMED", "DENIED"}:
                    _add(codes, "INVALID_ENUM_VALUE")
                elif actions[action] in {"UNCONFIRMED", "DENIED"}:
                    _add(codes, "RIGHTS_UNRESOLVED")
        if record.get("data_class") == "SYNTHETIC_CONTROL":
            if rights.get("status") != "SYNTHETIC_TEST_ONLY" or rights.get("scope") != "DEMO_ONLY":
                _add(codes, "RIGHTS_SCOPE_VIOLATION")
        elif rights.get("status") != "UNRESOLVED":
            _add(codes, "RIGHTS_SCOPE_VIOLATION")

    review = _object(
        record.get("review"),
        codes,
        "review",
        ("status", "history", "history_head_hash"),
        ("status", "history", "history_head_hash"),
    )
    if review is not None:
        history = review.get("history")
        if not isinstance(history, list) or not history:
            _add(codes, "REVIEW_HISTORY_INVALID")
        else:
            previous = None
            for sequence, entry in enumerate(history):
                ent = _object(
                    entry,
                    codes,
                    "review.history.entry",
                    ("sequence", "previous_entry_hash", "action", "actor", "entry_hash"),
                    ("sequence", "previous_entry_hash", "action", "actor", "entry_hash"),
                )
                if ent is None:
                    continue
                projection = {key: value for key, value in ent.items() if key != "entry_hash"}
                expected = _sha256(_canonical_bytes(projection))
                if ent.get("sequence") != sequence or ent.get("previous_entry_hash") != previous or ent.get("entry_hash") != expected:
                    _add(codes, "REVIEW_HISTORY_INVALID")
                previous = ent.get("entry_hash")
            if review.get("history_head_hash") != previous:
                _add(codes, "REVIEW_HISTORY_INVALID")

    event_coverage = record.get("event_coverage")
    seen_events: set[str] = set()
    if not isinstance(event_coverage, list):
        _add(codes, "MALFORMED_FIELD_TYPE")
        event_coverage = []
    for event in event_coverage:
        ev = _object(
            event,
            codes,
            "event",
            ("event_type", "status", "source_event_type", "source_id", "locator_ids", "observation"),
            ("event_type", "status"),
        )
        if ev is None:
            continue
        event_type = ev.get("event_type")
        if event_type not in EVENT_TYPES or event_type in seen_events:
            _add(codes, "INVALID_ENUM_VALUE")
            continue
        seen_events.add(event_type)
        if ev.get("status") == "EVIDENCE_MISSING":
            _add(codes, f"{event_type}_EVIDENCE_MISSING")
        elif ev.get("status") == "REPORTED_IDENTITY_UNRESOLVED" and event_type in DESTRUCTIVE_EVENTS:
            _add(codes, "EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED")
        source_event_type = ev.get("source_event_type")
        if source_event_type is not None and source_event_type != event_type:
            _add(codes, "EVIDENCE_TYPE_SUBSTITUTION")
            if event_type in DESTRUCTIVE_EVENTS:
                _add(codes, "DESTRUCTIVE_SEE_MODE_MISSING")
        refs = ev.get("locator_ids")
        if ev.get("status") in {"REPORTED", "REPORTED_IDENTITY_UNRESOLVED"}:
            if not isinstance(refs, list) or not refs:
                _add(codes, "SOURCE_LOCATOR_MISSING")
            elif any(not isinstance(ref, str) or ref not in locator_ids for ref in refs):
                _add(codes, "INVALID_SOURCE_LOCATOR")
        observation = ev.get("observation")
        if observation is not None:
            obs = _object(
                observation,
                codes,
                "event.observation",
                (
                    "zero_events_claimed",
                    "fluence_reported",
                    "sample_size_reported",
                    "detection_limit_reported",
                    "confidence_or_upper_bound_reported",
                    "immunity_claimed",
                ),
            )
            if obs is not None and obs.get("immunity_claimed") is True:
                required_flags = (
                    "fluence_reported",
                    "sample_size_reported",
                    "detection_limit_reported",
                    "confidence_or_upper_bound_reported",
                )
                if not all(obs.get(flag) is True for flag in required_flags):
                    _add(codes, "ZERO_EVENT_BOUND_MISSING")
                _add(codes, "IMMUNITY_CLAIM_UNSUPPORTED")
    if seen_events != set(EVENT_TYPES):
        _add(codes, "EVENT_COVERAGE_MISSING")

    applicability = _object(
        record.get("applicability"),
        codes,
        "applicability",
        ("status", "mission_environment_ref", "comparisons"),
        ("status", "mission_environment_ref", "comparisons"),
    )
    applicability_status = "NOT_EVALUATED"
    if applicability is not None:
        applicability_status = applicability.get("status")
        if applicability_status not in {"APPLICABLE", "NOT_APPLICABLE", "NOT_EVALUATED"}:
            _add(codes, "INVALID_ENUM_VALUE")
            applicability_status = "NOT_EVALUATED"
        if applicability_status == "NOT_EVALUATED":
            _add(codes, "MISSION_APPLICABILITY_NOT_EVALUATED")
        comparisons = applicability.get("comparisons")
        if not isinstance(comparisons, list):
            _add(codes, "MALFORMED_FIELD_TYPE")
        elif applicability_status == "APPLICABLE" and any(
            isinstance(item, dict) and item.get("within_test_range") is False
            for item in comparisons
        ):
            _add(codes, "OUT_OF_TEST_SCOPE", "DECISION_TRACE_NOT_APPLICABLE")
            applicability_status = "NOT_APPLICABLE"

    decision = _object(
        record.get("decision"),
        codes,
        "decision",
        ("requested_outcome", "used_for_decision", "recommendation"),
        ("requested_outcome", "used_for_decision", "recommendation"),
    )
    if decision is not None:
        if decision.get("used_for_decision") is not False or decision.get("recommendation") is not None:
            _add(codes, "DECISION_USE_FORBIDDEN")
        if decision.get("requested_outcome") != "HOLD":
            _add(codes, "DECISION_USE_FORBIDDEN")
            if applicability_status == "NOT_EVALUATED":
                _add(codes, "MISSION_APPLICABILITY_NOT_EVALUATED")

    identity_status = _identity_status(
        bom_identity, tested_identity or {}, approval_status, codes
    )
    if record.get("data_class") == "DISCOVERY_CANDIDATE":
        _add(codes, "DISCOVERY_ONLY_INPUT")
    return _result(codes, identity_status, applicability_status)


def _identity_status(
    bom_identity: dict[str, Any],
    tested_identity: dict[str, Any],
    approval_status: Any,
    codes: list[str],
) -> str:
    contradicted = False
    unresolved = False
    for field in ("manufacturer", "exact_part_number", "package", "grade", "process", "die", "lot"):
        bom_claim = bom_identity.get(field)
        tested_claim = tested_identity.get(field)
        if isinstance(bom_claim, dict) and bom_claim.get("status") == "CONFLICTING":
            contradicted = True
        if isinstance(tested_claim, dict) and tested_claim.get("status") == "CONFLICTING":
            contradicted = True
        left, right = _claim_value(bom_claim), _claim_value(tested_claim)
        if left is None or right is None:
            unresolved = True
            continue
        if left != right:
            contradicted = True
            mapping = {
                "manufacturer": "MANUFACTURER_CONFLICT",
                "exact_part_number": "PART_NUMBER_CONFLICT",
                "package": "PACKAGE_CONFLICT",
                "grade": "QUALITY_GRADE_CONFLICT",
                "process": "PROCESS_CONFLICT",
                "die": "DIE_CONFLICT",
                "lot": "LOT_CONFLICT",
            }
            _add(codes, mapping[field])
        elif field == "manufacturer" and _claim_raw(bom_claim) != _claim_raw(tested_claim):
            _add(codes, "MANUFACTURER_ALIAS_UNAPPROVED")
            unresolved = True
        elif field == "exact_part_number" and _claim_raw(bom_claim) != _claim_raw(tested_claim):
            _add(codes, "IDENTITY_NORMALIZATION_LOSSY", "PART_NUMBER_CONFLICT")
            contradicted = True
    if contradicted:
        return "CONTRADICTED"
    exact_claim = tested_identity.get("exact_part_number")
    family = tested_identity.get("family_relation")
    if isinstance(exact_claim, dict) and exact_claim.get("status") == "NOT_REPORTED":
        if isinstance(family, dict) and family.get("status") == "VERIFIED":
            return "FAMILY_ONLY"
        return "PARTIAL_UNRESOLVED"
    if approval_status == "APPROVED" and not unresolved:
        return "EXACT_MATCH"
    return "PARTIAL_UNRESOLVED"


def _result(codes: list[str], identity: str, applicability: str) -> GateResult:
    if any(code in STRUCTURAL_CODES for code in codes):
        processing = "INVALID_INPUT"
    elif any(code in PROVENANCE_CODES for code in codes):
        processing = "PROVENANCE_FAILURE"
    else:
        processing = "VALID"
    return GateResult(
        processing_status=processing,
        identity_status=identity,
        applicability_status=applicability,
        assurance_decision="HOLD",
        used_for_decision=False,
        recommendation=None,
        codes=tuple(codes),
    )


def apply_operations(record: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    result = copy.deepcopy(record)
    for operation in operations:
        op = operation.get("op")
        pointer = operation.get("path")
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            raise ValueError("fixture operation path must be a JSON pointer")
        tokens = [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]
        parent: Any = result
        for token in tokens[:-1]:
            parent = parent[int(token)] if isinstance(parent, list) else parent[token]
        last = tokens[-1]
        if op == "set":
            if isinstance(parent, list):
                parent[int(last)] = copy.deepcopy(operation.get("value"))
            else:
                parent[last] = copy.deepcopy(operation.get("value"))
        elif op == "remove":
            if isinstance(parent, list):
                del parent[int(last)]
            else:
                parent.pop(last, None)
        else:
            raise ValueError(f"unsupported fixture operation: {op}")
    return result


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
