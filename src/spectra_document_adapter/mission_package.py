"""Strict document-to-Mission-Case adapter for bounded evidence linking.

The adapter accepts three UTF-8 key/value documents plus a hash manifest.  It
does not infer missing fields.  Every accepted value is bound to a source line
and every document must match its manifest hash before a Mission Case contract
is emitted.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping


ADAPTER_VERSION = "MISSION_PACKAGE_ADAPTER_2.0.0"
ROLES = ("MISSION_CONDITIONS", "APPROVED_BOM", "RADIATION_TEST")
IDENTITY_KEYS = (
    "MANUFACTURER",
    "ORDERABLE_PART_NUMBER",
    "PACKAGE",
    "PROCESS",
    "DIE",
    "LOT",
)
MISSION_KEYS = frozenset(
    {
        "MISSION_ID",
        "DURATION",
        "ENVIRONMENT_TID",
        "PARTICLE_FLUX",
        "SHIELDING",
        "TID_DESIGN_FACTOR",
        "ANALYSIS_DEVICE_COUNT",
    }
)
BOM_KEYS = frozenset({"COMPONENT_ID", "APPROVAL_STATUS", *IDENTITY_KEYS})
TEST_KEYS = frozenset(
    {
        "COMPONENT_ID",
        *IDENTITY_KEYS,
        "SPECIES",
        "ENERGY",
        "LET",
        "FLUENCE",
        "TEMPERATURE",
        "BIAS",
        "EVENTS",
        "TID_TEST_LIMIT",
        "SEU_CROSS_SECTION",
        "SEL_FLUENCE",
        "SEL_SAMPLE_SIZE",
        "SEL_OBSERVED_EVENTS",
        "SEB_FLUENCE",
        "SEB_SAMPLE_SIZE",
        "SEB_OBSERVED_EVENTS",
        "SEGR_FLUENCE",
        "SEGR_SAMPLE_SIZE",
        "SEGR_OBSERVED_EVENTS",
    }
)
ROLE_KEYS = {
    "MISSION_CONDITIONS": MISSION_KEYS,
    "APPROVED_BOM": BOM_KEYS,
    "RADIATION_TEST": TEST_KEYS,
}
_QUANTITY = re.compile(
    r"^(?P<value>[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)\s+(?P<unit>\S+)$"
)


class MissionPackageError(ValueError):
    """Stable fail-closed adapter error."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _canonical_sha256(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MissionPackageError("TRUST_CONTRACT_INVALID") from exc
    return _sha256(encoded)


def _policy_scope_projection(policy: Mapping[str, Any]) -> dict[str, Any]:
    scope = policy.get("scope")
    if not isinstance(scope, Mapping):
        raise MissionPackageError("POLICY_SCOPE_INVALID")
    mission_ids = scope.get("mission_ids")
    component_ids = scope.get("component_ids")
    if not isinstance(mission_ids, list) or not isinstance(component_ids, list):
        raise MissionPackageError("POLICY_SCOPE_INVALID")
    return {
        "component_ids": sorted(component_ids),
        "mission_ids": sorted(mission_ids),
        "tenant_id": scope.get("tenant_id"),
    }


def _policy_content_projection(policy: Mapping[str, Any], scope_hash: str) -> dict[str, Any]:
    rules = policy.get("rules")
    if not isinstance(rules, Mapping):
        raise MissionPackageError("POLICY_RULES_INVALID")
    normalized_rules = dict(rules)
    destructive_modes = normalized_rules.get("required_destructive_modes")
    if isinstance(destructive_modes, list):
        normalized_rules["required_destructive_modes"] = sorted(destructive_modes)
    return {
        "contract_version": policy.get("contract_version"),
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "rules": normalized_rules,
        "scope_hash": scope_hash,
    }


def _validate_trust(
    *,
    parsed: Mapping[str, Mapping[str, Any]],
    mission_case_id: str,
    raw_manifest: Mapping[str, Any],
    approval_policy: Mapping[str, Any],
    trust_store: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate rights and approval against a deployment-owned trust snapshot."""

    if raw_manifest.get("contract_version") != "2.0.0":
        raise MissionPackageError("RAW_MANIFEST_VERSION_UNSUPPORTED")
    if raw_manifest.get("mission_case_id") != mission_case_id:
        raise MissionPackageError("RAW_MANIFEST_MISSION_MISMATCH")
    document_index = raw_manifest.get("documents")
    if not isinstance(document_index, list) or len(document_index) != len(ROLES):
        raise MissionPackageError("RAW_MANIFEST_DOCUMENT_SET_INVALID")
    expected_documents = [
        {
            "role": role,
            "document_id": parsed[role]["document_id"],
            "sha256": parsed[role]["sha256"],
        }
        for role in ROLES
    ]
    indexed_documents = [
        {key: item.get(key) for key in ("role", "document_id", "sha256")}
        for item in document_index
        if isinstance(item, Mapping)
    ]
    if indexed_documents != expected_documents:
        raise MissionPackageError("RAW_MANIFEST_DOCUMENT_HASH_MISMATCH")
    bundle_hash = _canonical_sha256(
        {
            "manifest_id": raw_manifest.get("manifest_id"),
            "mission_case_id": mission_case_id,
            "documents": expected_documents,
        }
    )
    if raw_manifest.get("bundle_hash") != bundle_hash:
        raise MissionPackageError("RAW_MANIFEST_BUNDLE_HASH_MISMATCH")

    rights = raw_manifest.get("rights_snapshot")
    if not isinstance(rights, Mapping):
        raise MissionPackageError("RIGHTS_SNAPSHOT_MISSING")
    if rights.get("status") != "SYNTHETIC_TEST_ONLY":
        raise MissionPackageError("RIGHTS_STATUS_INVALID")
    if rights.get("approval_target_hash") != bundle_hash:
        raise MissionPackageError("RIGHTS_APPROVAL_TARGET_MISMATCH")
    grants = {
        item.get("action"): item
        for item in rights.get("action_grants", [])
        if isinstance(item, Mapping)
    }
    for action in ("PRIVATE_STORE", "DISPLAY_INTERNAL"):
        grant = grants.get(action)
        if not isinstance(grant, Mapping) or grant.get("grant_status") != "ALLOWED":
            raise MissionPackageError("RIGHTS_ACTION_GRANT_MISSING")
        if grant.get("scope_hash") != bundle_hash:
            raise MissionPackageError("RIGHTS_SCOPE_HASH_MISMATCH")

    if approval_policy.get("kind") != "USER_POLICY" or approval_policy.get("contract_version") != "2.0.0":
        raise MissionPackageError("POLICY_VERSION_UNSUPPORTED")
    if approval_policy.get("hash_contract_version") != "1.0.0":
        raise MissionPackageError("POLICY_HASH_CONTRACT_MISSING")
    scope_hash = _canonical_sha256(_policy_scope_projection(approval_policy))
    content_hash = _canonical_sha256(_policy_content_projection(approval_policy, scope_hash))
    scope = approval_policy.get("scope")
    approval = approval_policy.get("approval")
    history = approval_policy.get("immutable_history_ref")
    metadata = approval_policy.get("metadata")
    if not all(isinstance(item, Mapping) for item in (scope, approval, history, metadata)):
        raise MissionPackageError("POLICY_CONTRACT_INVALID")
    if scope.get("scope_hash") != scope_hash:
        raise MissionPackageError("POLICY_SCOPE_HASH_MISMATCH")
    if approval_policy.get("policy_content_hash") != content_hash or metadata.get("content_hash") != content_hash:
        raise MissionPackageError("POLICY_CONTENT_HASH_MISMATCH")
    if approval.get("approval_target_hash") != content_hash or approval.get("approval_scope_hash") != scope_hash:
        raise MissionPackageError("POLICY_APPROVAL_TARGET_MISMATCH")
    if approval.get("status") != "APPROVED":
        raise MissionPackageError("POLICY_NOT_APPROVED")
    if approval.get("history_head_hash") != history.get("head_hash"):
        raise MissionPackageError("POLICY_HISTORY_MISMATCH")

    mission_id = parsed["MISSION_CONDITIONS"]["values"]["MISSION_ID"]
    component_id = parsed["APPROVED_BOM"]["values"]["COMPONENT_ID"]
    if mission_id not in scope.get("mission_ids", []) or component_id not in scope.get("component_ids", []):
        raise MissionPackageError("POLICY_SCOPE_TARGET_MISMATCH")
    if parsed["APPROVED_BOM"]["values"]["APPROVAL_STATUS"] != approval.get("status"):
        raise MissionPackageError("BOM_APPROVAL_CLAIM_MISMATCH")

    if trust_store.get("contract_version") != "MISSION_PACKAGE_TRUST_STORE_1.0.0":
        raise MissionPackageError("TRUST_STORE_VERSION_UNSUPPORTED")
    policy_anchor = trust_store.get("approval_policy")
    rights_anchor = trust_store.get("rights_snapshot")
    if not isinstance(policy_anchor, Mapping) or not isinstance(rights_anchor, Mapping):
        raise MissionPackageError("TRUST_ANCHOR_MISSING")
    expected_policy_anchor = {
        "policy_id": approval_policy.get("policy_id"),
        "policy_content_hash": content_hash,
        "scope_hash": scope_hash,
        "history_head_hash": history.get("head_hash"),
        "approved_bom_sha256": parsed["APPROVED_BOM"]["sha256"],
    }
    if any(policy_anchor.get(key) != value for key, value in expected_policy_anchor.items()):
        raise MissionPackageError("APPROVAL_TRUST_ANCHOR_MISMATCH")
    expected_rights_anchor = {
        "rights_snapshot_id": rights.get("rights_snapshot_id"),
        "bundle_hash": bundle_hash,
        "history_anchor_ref": rights.get("history_anchor_ref"),
    }
    if any(rights_anchor.get(key) != value for key, value in expected_rights_anchor.items()):
        raise MissionPackageError("RIGHTS_TRUST_ANCHOR_MISMATCH")

    return {
        "contract_version": "MISSION_CASE_EVIDENCE_BINDING_1.0.0",
        "manifest_id": raw_manifest.get("manifest_id"),
        "bundle_hash": bundle_hash,
        "document_hashes": expected_documents,
        "rights_snapshot_id": rights.get("rights_snapshot_id"),
        "rights_history_anchor_ref": rights.get("history_anchor_ref"),
        "approval_policy_id": approval_policy.get("policy_id"),
        "approval_policy_content_hash": content_hash,
        "approval_scope_hash": scope_hash,
        "approval_history_head_hash": history.get("head_hash"),
        "trust_store_id": trust_store.get("trust_store_id"),
        "trust_store_hash": _canonical_sha256(trust_store),
    }


def _decode(document: Mapping[str, Any]) -> tuple[str, str, str, str]:
    role = document.get("role")
    document_id = document.get("document_id")
    content = document.get("content")
    declared_hash = document.get("declared_sha256")
    if role not in ROLES or not isinstance(document_id, str) or not document_id:
        raise MissionPackageError("DOCUMENT_IDENTITY_INVALID")
    if not isinstance(content, bytes) or not content:
        raise MissionPackageError("DOCUMENT_CONTENT_INVALID")
    observed_hash = _sha256(content)
    if declared_hash != observed_hash:
        raise MissionPackageError("DOCUMENT_HASH_MISMATCH")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MissionPackageError("DOCUMENT_NOT_UTF8") from exc
    return role, document_id, text, observed_hash


def _fields(role: str, document_id: str, text: str) -> tuple[dict[str, str], dict[str, str]]:
    values: dict[str, str] = {}
    locators: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise MissionPackageError("DOCUMENT_LINE_INVALID")
        key, value = (item.strip() for item in line.split(":", 1))
        if key not in ROLE_KEYS[role]:
            raise MissionPackageError("DOCUMENT_FIELD_FORBIDDEN")
        if key in values:
            raise MissionPackageError("DOCUMENT_FIELD_DUPLICATE")
        if not value:
            raise MissionPackageError("DOCUMENT_VALUE_MISSING")
        values[key] = value
        locators[key] = f"synthetic://mission-package/{document_id}#line={line_number}"
    missing = ROLE_KEYS[role] - values.keys()
    if missing:
        raise MissionPackageError("DOCUMENT_REQUIRED_FIELD_MISSING")
    return values, locators


def _quantity(value: str) -> dict[str, Any]:
    match = _QUANTITY.fullmatch(value)
    if match is None:
        raise MissionPackageError("QUANTITY_FORMAT_INVALID")
    number = float(match.group("value"))
    if not math.isfinite(number):
        raise MissionPackageError("QUANTITY_VALUE_INVALID")
    return {"value": number, "unit": match.group("unit")}


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise MissionPackageError("NUMBER_FORMAT_INVALID") from exc
    if not math.isfinite(number) or number <= 0:
        raise MissionPackageError("NUMBER_VALUE_INVALID")
    return number


def _positive_int(value: str) -> int:
    if not value.isdigit() or int(value) <= 0:
        raise MissionPackageError("INTEGER_VALUE_INVALID")
    return int(value)


def _identity(values: Mapping[str, str]) -> dict[str, str]:
    return {key.lower(): values[key] for key in IDENTITY_KEYS}


def adapt_mission_package(
    documents: list[Mapping[str, Any]], *, mission_case_id: str,
    raw_manifest: Mapping[str, Any], approval_policy: Mapping[str, Any],
    trust_store: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and bind three source documents into one synthetic Mission Case."""

    if not isinstance(mission_case_id, str) or not mission_case_id:
        raise MissionPackageError("MISSION_CASE_ID_MISSING")
    if len(documents) != len(ROLES):
        raise MissionPackageError("DOCUMENT_SET_INCOMPLETE")

    parsed: dict[str, dict[str, Any]] = {}
    receipts: list[dict[str, Any]] = []
    for document in documents:
        role, document_id, text, observed_hash = _decode(document)
        if role in parsed:
            raise MissionPackageError("DOCUMENT_ROLE_DUPLICATE")
        values, locators = _fields(role, document_id, text)
        parsed[role] = {
            "document_id": document_id,
            "sha256": observed_hash,
            "values": values,
            "locators": locators,
        }
        receipts.append(
            {
                "role": role,
                "document_id": document_id,
                "observed_sha256": observed_hash,
                "declared_sha256": document["declared_sha256"],
                "hash_status": "MATCH",
                "field_count": len(values),
                "field_bindings": [
                    {"field": key, "source_locator": locators[key]}
                    for key in sorted(values)
                ],
            }
        )
    if set(parsed) != set(ROLES):
        raise MissionPackageError("DOCUMENT_SET_INCOMPLETE")

    evidence_binding = _validate_trust(
        parsed=parsed,
        mission_case_id=mission_case_id,
        raw_manifest=raw_manifest,
        approval_policy=approval_policy,
        trust_store=trust_store,
    )

    mission = parsed["MISSION_CONDITIONS"]
    bom = parsed["APPROVED_BOM"]
    test = parsed["RADIATION_TEST"]
    mission_values = mission["values"]
    bom_values = bom["values"]
    test_values = test["values"]
    event_types = [item.strip().upper() for item in test_values["EVENTS"].split(",")]
    if len(event_types) != len(set(event_types)) or any(
        item not in {"TID", "SEU", "SEL", "SEB", "SEGR"} for item in event_types
    ):
        raise MissionPackageError("EVENT_LIST_INVALID")

    events: list[dict[str, Any]] = []
    for event_type in event_types:
        event: dict[str, Any] = {
            "event_type": event_type,
            "source_event_type": event_type,
            "locator": test["locators"]["EVENTS"] + f"&event={event_type}",
        }
        if event_type == "TID":
            event["tid_test_limit"] = _quantity(test_values["TID_TEST_LIMIT"])
            event["locator"] = test["locators"]["TID_TEST_LIMIT"]
        elif event_type == "SEU":
            event["cross_section"] = _quantity(test_values["SEU_CROSS_SECTION"])
            event["locator"] = test["locators"]["SEU_CROSS_SECTION"]
        elif event_type in {"SEL", "SEB", "SEGR"}:
            event["fluence"] = _quantity(test_values[f"{event_type}_FLUENCE"])
            event["sample_size"] = _positive_int(test_values[f"{event_type}_SAMPLE_SIZE"])
            observed = test_values[f"{event_type}_OBSERVED_EVENTS"]
            if not observed.isdigit():
                raise MissionPackageError("OBSERVED_EVENT_COUNT_INVALID")
            event["observed_events"] = int(observed)
            event["locator"] = test["locators"][f"{event_type}_OBSERVED_EVENTS"]
        events.append(event)

    component_id = bom_values["COMPONENT_ID"]
    if test_values["COMPONENT_ID"] != component_id:
        raise MissionPackageError("TEST_COMPONENT_NOT_IN_BOM")

    case = {
        "contract_version": "MISSION_CASE_1.1.0",
        "mission_case_id": mission_case_id,
        "data_class": "SYNTHETIC",
        "evidence_binding": evidence_binding,
        "mission_conditions": {
            "mission_id": mission_values["MISSION_ID"],
            "duration": _quantity(mission_values["DURATION"]),
            "environment_tid": _quantity(mission_values["ENVIRONMENT_TID"]),
            "particle_flux": _quantity(mission_values["PARTICLE_FLUX"]),
            "shielding": _quantity(mission_values["SHIELDING"]),
            "tid_design_factor": _positive_float(mission_values["TID_DESIGN_FACTOR"]),
            "analysis_device_count": _positive_int(mission_values["ANALYSIS_DEVICE_COUNT"]),
        },
        "approved_bom_targets": [
            {
                "component_id": component_id,
                "approval_status": approval_policy["approval"]["status"],
                "approval_policy_id": approval_policy["policy_id"],
                "approval_target_hash": approval_policy["approval"]["approval_target_hash"],
                "identity": _identity(bom_values),
            }
        ],
        "sources": [
            {
                "source_id": "source-" + test["document_id"],
                "document_id": test["document_id"],
                "mission_case_id": mission_case_id,
                "data_class": "SYNTHETIC",
                "artifact_sha256": test["sha256"],
                "observed_artifact_sha256": test["sha256"],
                "locator": f"synthetic://mission-package/{test['document_id']}",
                "claims": [
                    {
                        "claim_id": "claim-" + test["document_id"],
                        "component_id": component_id,
                        "tested_identity": _identity(test_values),
                        "test_conditions": {
                            key.lower(): test_values[key]
                            for key in ("SPECIES", "ENERGY", "LET", "FLUENCE", "TEMPERATURE", "BIAS")
                        },
                        "event_evidence": events,
                    }
                ],
            }
        ],
    }
    return {
        "adapter_version": ADAPTER_VERSION,
        "status": "SOURCE_BOUND",
        "mission_case_id": mission_case_id,
        "document_count": len(receipts),
        "document_receipts": sorted(receipts, key=lambda item: ROLES.index(item["role"])),
        "mission_source_locator": mission["locators"]["MISSION_ID"],
        "bom_source_locator": bom["locators"]["COMPONENT_ID"],
        "mission_case": case,
    }
