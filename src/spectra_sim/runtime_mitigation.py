"""Deterministic runtime calculator for H06 mitigation and policy contracts."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal

from .contracts import packet_schema_errors, packet_semantic_errors

ENGINE_NAME = "SPECTRA_RUNTIME_MITIGATION_CALCULATOR"
ENGINE_VERSION = "1.0.0"
RESULT_SCHEMA_VERSION = "1.0.0"
RUNTIME_CONTRACT_VERSION = "1.0.0"
METHOD_EQUATIONS = {
    "WATCHDOG": "WATCHDOG_TRUE_FALSE_PATH_V1",
    "TMR": "TMR_3P2_MINUS_2P3_V1",
    "SEL_PROTECTION": "SEL_TRUE_FALSE_PATH_V1",
}
POST_CALCULATION_CONTRACT_CODES = {
    "POLICY_APPROVAL_TARGET_MISMATCH",
    "POLICY_CONTENT_HASH_MISMATCH",
    "POLICY_EXPIRED",
    "POLICY_HISTORY_MISMATCH",
    "POLICY_PACK_NOT_APPROVED",
    "POLICY_REVOKED",
    "POLICY_SCOPE_HASH_MISMATCH",
    "POLICY_SCOPE_REUSE_MISMATCH",
    "POLICY_VALIDITY_INVALID",
    "SEL_DURATION_DOUBLE_COUNTED",
    "SEL_RUNTIME_PROJECTION_MISMATCH",
    "TMR_RUNTIME_PROJECTION_MISMATCH",
    "WATCHDOG_DETECTION_LATENCY_DOUBLE_COUNTED",
    "WATCHDOG_FALSE_POSITIVE_IGNORED",
    "WATCHDOG_RUNTIME_PROJECTION_MISMATCH",
}
TMR_INELIGIBLE_CODES = {
    "TMR_COMMON_MODE_MODEL_MISSING",
    "TMR_COMMON_MODE_NONZERO",
    "TMR_INDEPENDENCE_UNVERIFIED",
    "TMR_OUTPUT_SEMANTIC_MISMATCH",
    "TMR_REPAIR_WINDOW_MISMATCH",
    "TMR_REPAIR_WINDOW_MISSING",
    "TMR_REPLICA_COUNT_MISMATCH",
    "TMR_VOTER_MODEL_MISSING",
    "TMR_VOTER_SUSCEPTIBLE",
}
EVIDENCE_INELIGIBLE_CODES = {
    "DESTRUCTIVE_SEE_MODE_MISSING",
    "MITIGATION_EFFECT_EVIDENCE_MISSING",
    "MITIGATION_EVIDENCE_LINK_MISMATCH",
    "SEL_EVIDENCE_MISSING",
    "SEL_FALSE_TRIP_MODEL_MISSING",
    "SEL_PROTECTION_NOT_VALIDATED",
}


def _sanitize_for_hash(value):
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return "<NON_FINITE:NaN>"
        return "<NON_FINITE:+Infinity>" if value > 0 else "<NON_FINITE:-Infinity>"
    if isinstance(value, dict):
        return {str(key): _sanitize_for_hash(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_for_hash(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return f"<NON_JSON:{type(value).__name__}>"


def _canonical_bytes(value) -> bytes:
    return json.dumps(
        _sanitize_for_hash(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def canonical_runtime_json(result: dict) -> str:
    """Serialize a runtime result using the project canonical JSON rules."""
    return _canonical_bytes(result).decode("utf-8")


def _non_finite_paths(value, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, float) and not math.isfinite(value):
        return [path or "/<root>"]
    if isinstance(value, dict):
        for key in sorted(value, key=str):
            paths.extend(_non_finite_paths(value[key], f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(_non_finite_paths(item, f"{path}/{index}"))
    return paths


def _is_number(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _close(actual, expected) -> bool:
    return _is_number(actual) and math.isclose(
        actual, expected, rel_tol=1e-12, abs_tol=1e-12
    )


def _parse_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _records_by_kind(packet: dict, kind: str) -> list[dict]:
    inputs = packet.get("inputs", []) if isinstance(packet, dict) else []
    if not isinstance(inputs, list):
        return []
    return [item for item in inputs if isinstance(item, dict) and item.get("kind") == kind]


def _identifiers(packet, mitigation=None, policy=None) -> dict:
    def text_or_none(value):
        return value if isinstance(value, str) else None

    return {
        "packet_id": text_or_none(packet.get("packet_id")) if isinstance(packet, dict) else None,
        "mitigation_id": text_or_none(mitigation.get("mitigation_id")) if isinstance(mitigation, dict) else None,
        "policy_id": text_or_none(policy.get("policy_id")) if isinstance(policy, dict) else None,
        "policy_version": text_or_none(policy.get("policy_version")) if isinstance(policy, dict) else None,
    }


def _empty_policy_summary() -> dict:
    return {
        "status": None,
        "hash_contract_version": None,
        "computed_scope_hash": None,
        "computed_content_hash": None,
        "scope_matches": False,
        "content_matches": False,
        "approval_target_matches": False,
        "history_matches": False,
        "valid_at_packet_time": False,
        "approval_eligible": False,
        "evidence_eligible": False,
        "rule_results": [],
    }


def _finalize(
    packet,
    *,
    mitigation=None,
    policy=None,
    method=None,
    equation_id=None,
    processing_status="INVALID_INPUT",
    engineering_gate="NOT_EVALUATED",
    normalized_counts=None,
    computed_projection=None,
    declared_projection=None,
    mismatched_fields=None,
    policy_summary=None,
    codes=(),
) -> dict:
    input_hash = _sha256(packet)
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "engine": {
            "name": ENGINE_NAME,
            "version": ENGINE_VERSION,
        },
        "result_id": "runtime-" + _sha256({
            "input_hash": input_hash,
            "engine_version": ENGINE_VERSION,
        }).removeprefix("sha256:")[:16],
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "identifiers": _identifiers(packet, mitigation, policy),
        "method": method if isinstance(method, str) else None,
        "equation_id": equation_id if isinstance(equation_id, str) else None,
        "processing_status": processing_status,
        "engineering_gate": engineering_gate,
        "assurance_decision": "HOLD",
        "data_class": "SYNTHETIC",
        "normalized_counts": normalized_counts or {},
        "computed_projection": copy.deepcopy(computed_projection),
        "declared_projection_comparison": {
            "declared_projection": copy.deepcopy(declared_projection)
            if isinstance(declared_projection, dict) else None,
            "matches": computed_projection is not None and not (mismatched_fields or []),
            "mismatched_fields": sorted(set(mismatched_fields or [])),
        },
        "policy_evaluation": policy_summary or _empty_policy_summary(),
        "stable_error_codes": sorted(set(codes)),
        "input_hash": input_hash,
        "output_hash": "",
    }
    result["output_hash"] = _sha256({
        key: value for key, value in result.items() if key != "output_hash"
    })
    return result


def _normalized_count(model, count_key, rate_key, window, codes) -> float | None:
    if not isinstance(model, dict) or not isinstance(window, dict):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return None
    has_count = count_key in model
    has_rate = rate_key in model
    if has_count == has_rate:
        codes.add("ACTIVATION_COUNT_RATE_CONFLICT")
        return None
    denominator = model.get("denominator")
    if not isinstance(denominator, dict):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return None
    if denominator.get("scope") != window.get("denominator_scope"):
        codes.add("RECOVERY_DENOMINATOR_WINDOW_MISMATCH")
    denominator_count = denominator.get("count")
    duration = window.get("duration_seconds")
    if (
        not isinstance(denominator_count, int)
        or isinstance(denominator_count, bool)
        or denominator_count < 1
        or not _is_number(duration)
        or duration <= 0
    ):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return None
    value = model.get(count_key if has_count else rate_key)
    if not _is_number(value) or value < 0:
        codes.add("INVALID_RUNTIME_NUMERIC_INPUT")
        return None
    return float(value) if has_count else float(value * denominator_count * duration)


def _action_paths(model, *, allow_duration, codes) -> list[dict] | None:
    if not isinstance(model, dict) or not isinstance(model.get("action_paths"), list):
        codes.add("MALFORMED_ACTION_PATH")
        return None
    paths = model["action_paths"]
    if not paths or any(not isinstance(path, dict) for path in paths):
        codes.add("MALFORMED_ACTION_PATH")
        return None
    total = 0.0
    for path in paths:
        fraction = path.get("fraction")
        if not _is_number(fraction) or not 0 <= fraction <= 1:
            codes.add("MALFORMED_ACTION_PATH")
            return None
        total += fraction
        if allow_duration:
            duration = path.get("duration_seconds")
            if not _is_number(duration) or duration < 0:
                codes.add("MALFORMED_ACTION_PATH")
                return None
        elif "duration_seconds" in path:
            codes.add("SEL_DURATION_SEMANTIC_CONFLICT")
            return None
    if not _close(total, 1.0):
        codes.add("ACTION_PATH_FRACTION_INVALID")
        return None
    return paths


def _evidence_links(parameters, mitigation, model_names, direct_names, codes) -> bool:
    declared_raw = mitigation.get("verification_evidence_ids")
    if not isinstance(declared_raw, list) or not declared_raw or any(
        not isinstance(item, str) or not item for item in declared_raw
    ):
        codes.add("MITIGATION_EFFECT_EVIDENCE_MISSING")
        return False
    declared = set(declared_raw)
    required: set[str] = set()
    for name in model_names:
        model = parameters.get(name)
        if not isinstance(model, dict):
            continue
        evidence_id = model.get("verification_evidence_id", model.get("evidence_id"))
        if isinstance(evidence_id, str) and evidence_id:
            required.add(evidence_id)
        else:
            codes.add("MITIGATION_EFFECT_EVIDENCE_MISSING")
    for name in direct_names:
        evidence_id = parameters.get(name)
        if isinstance(evidence_id, str) and evidence_id:
            required.add(evidence_id)
        else:
            codes.add("MITIGATION_EFFECT_EVIDENCE_MISSING")
    if not required.issubset(declared):
        codes.add("MITIGATION_EVIDENCE_LINK_MISMATCH")
    return required.issubset(declared) and not codes.intersection(EVIDENCE_INELIGIBLE_CODES)


def _watchdog_projection(mitigation, codes):
    parameters = mitigation.get("design_parameters")
    if not isinstance(parameters, dict):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return {}, None
    window = parameters.get("evaluation_window")
    target_model = parameters.get("target_event_model")
    false_model = parameters.get("false_positive_model")
    if not isinstance(false_model, dict):
        codes.add("WATCHDOG_FALSE_POSITIVE_MODEL_MISSING")
    target_count = _normalized_count(
        target_model, "event_count", "event_rate_per_second", window, codes
    )
    false_count = _normalized_count(
        false_model, "activation_count", "activation_rate_per_second", window, codes
    )
    target_paths = _action_paths(target_model, allow_duration=True, codes=codes)
    false_paths = _action_paths(false_model, allow_duration=True, codes=codes)
    coverage = parameters.get("true_positive_coverage")
    latency = parameters.get("detection_latency_seconds")
    if not _is_number(coverage) or not 0 <= coverage <= 1:
        codes.add("WATCHDOG_TRUE_POSITIVE_COVERAGE_MISSING")
    if not _is_number(latency) or latency < 0:
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
    if parameters.get("action_duration_semantic") != "POST_DETECTION_ACTION_ONLY":
        codes.add("WATCHDOG_ACTION_DURATION_SEMANTIC_MISMATCH")
    _evidence_links(
        parameters,
        mitigation,
        ("target_event_model", "false_positive_model"),
        (),
        codes,
    )
    if (
        target_count is None
        or false_count is None
        or target_paths is None
        or false_paths is None
        or not _is_number(coverage)
        or not _is_number(latency)
        or codes.intersection(EVIDENCE_INELIGIBLE_CODES)
    ):
        return {}, None
    true_count = target_count * coverage
    true_reboots = sum(
        true_count * path["fraction"]
        for path in target_paths
        if path.get("action") == "REBOOT"
    )
    false_reboots = sum(
        false_count * path["fraction"]
        for path in false_paths
        if path.get("action") == "REBOOT"
    )
    true_downtime = sum(
        true_count * path["fraction"] * (latency + path["duration_seconds"])
        for path in target_paths
    )
    false_downtime = sum(
        false_count * path["fraction"] * path["duration_seconds"]
        for path in false_paths
    )
    counts = {
        "true_target_event_count": target_count,
        "true_positive_activation_count": true_count,
        "false_positive_activation_count": false_count,
    }
    projection = {
        "method": "WATCHDOG",
        **counts,
        "reboot_count_total": true_reboots + false_reboots,
        "downtime_total_seconds": true_downtime + false_downtime,
    }
    return counts, projection


def _tmr_projection(mitigation, codes):
    parameters = mitigation.get("design_parameters")
    if not isinstance(parameters, dict):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return {}, None
    voter = parameters.get("voter_model")
    common = parameters.get("common_mode_model")
    repair = parameters.get("repair_model")
    window = parameters.get("evaluation_window")
    p = parameters.get("replica_failure_probability")
    if parameters.get("replica_count") != 3:
        codes.add("TMR_REPLICA_COUNT_MISMATCH")
    if not _is_number(p) or not 0 <= p <= 1:
        codes.add("INVALID_RUNTIME_NUMERIC_INPUT")
    if not isinstance(voter, dict):
        codes.add("TMR_VOTER_MODEL_MISSING")
    elif voter.get("susceptible") is not False:
        codes.add("TMR_VOTER_SUSCEPTIBLE")
    if not isinstance(common, dict):
        codes.add("TMR_COMMON_MODE_MODEL_MISSING")
    elif common.get("probability") != 0:
        codes.add("TMR_COMMON_MODE_NONZERO")
    if not isinstance(window, dict) or not isinstance(repair, dict):
        codes.add("TMR_REPAIR_WINDOW_MISSING")
    elif repair.get("repair_within_window") is not False:
        codes.add("TMR_REPAIR_WINDOW_MISMATCH")
    if parameters.get("independence_verified") is not True:
        codes.add("TMR_INDEPENDENCE_UNVERIFIED")
    if parameters.get("output_semantic") != "system_failure_probability":
        codes.add("TMR_OUTPUT_SEMANTIC_MISMATCH")
    _evidence_links(
        parameters,
        mitigation,
        ("voter_model", "common_mode_model"),
        (),
        codes,
    )
    if codes.intersection(TMR_INELIGIBLE_CODES | EVIDENCE_INELIGIBLE_CODES) or not _is_number(p):
        return {}, None
    decimal_p = Decimal(str(p))
    failure_probability = float(3 * decimal_p**2 - 2 * decimal_p**3)
    return {}, {
        "method": "TMR",
        "system_failure_probability": failure_probability,
    }


def _sel_projection(packet, mitigation, policy, codes):
    parameters = mitigation.get("design_parameters")
    if not isinstance(parameters, dict):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
        return {}, None
    if mitigation.get("target_failure_modes") != ["SEL"]:
        codes.add("MITIGATION_METHOD_MODE_MISMATCH")
    window = parameters.get("evaluation_window")
    true_model = parameters.get("true_sel_model")
    false_model = parameters.get("false_trip_model")
    if not isinstance(false_model, dict):
        codes.add("SEL_FALSE_TRIP_MODEL_MISSING")
    true_count = _normalized_count(
        true_model, "activation_count", "activation_rate_per_second", window, codes
    )
    false_count = _normalized_count(
        false_model, "activation_count", "activation_rate_per_second", window, codes
    )
    true_paths = _action_paths(true_model, allow_duration=False, codes=codes)
    false_paths = _action_paths(false_model, allow_duration=False, codes=codes)
    phase_names = ("trip_delay_seconds", "off_time_seconds", "restart_time_seconds")
    phases = [parameters.get(name) for name in phase_names]
    if any(not _is_number(value) or value < 0 for value in phases):
        codes.add("MALFORMED_MITIGATION_PARAMETERS")
    if parameters.get("duration_semantic") != "TRIP_OFF_RESTART_FIELDS_ONLY":
        codes.add("SEL_DURATION_SEMANTIC_CONFLICT")
    _evidence_links(
        parameters,
        mitigation,
        ("true_sel_model", "false_trip_model"),
        (
            "prompt_failure_evidence_id",
            "latent_damage_evidence_id",
            "post_test_electrical_evidence_id",
        ),
        codes,
    )
    evidence_records = _records_by_kind(packet, "PART_TEST_EVIDENCE")
    evidence_types = evidence_records[0].get("evidence_types", []) if len(evidence_records) == 1 else []
    if not isinstance(evidence_types, list) or "SEL" not in evidence_types:
        codes.add("SEL_EVIDENCE_MISSING")
    rules = policy.get("rules", {}) if isinstance(policy, dict) else {}
    required_modes = rules.get("required_destructive_modes", []) if isinstance(rules, dict) else []
    if isinstance(required_modes, list) and not set(required_modes).issubset(set(evidence_types)):
        codes.add("DESTRUCTIVE_SEE_MODE_MISSING")
    if (
        true_count is None
        or false_count is None
        or true_paths is None
        or false_paths is None
        or any(not _is_number(value) for value in phases)
        or codes.intersection(EVIDENCE_INELIGIBLE_CODES)
    ):
        return {}, None
    true_cycles = sum(
        true_count * path["fraction"]
        for path in true_paths
        if path.get("action") == "POWER_CYCLE"
    )
    false_cycles = sum(
        false_count * path["fraction"]
        for path in false_paths
        if path.get("action") == "POWER_CYCLE"
    )
    cycles = true_cycles + false_cycles
    counts = {
        "true_sel_activation_count": true_count,
        "false_trip_activation_count": false_count,
    }
    return counts, {
        "method": "SEL_PROTECTION",
        **counts,
        "power_cycle_count_total": cycles,
        "downtime_total_seconds": cycles * sum(phases),
    }


def _projection_mismatches(computed, declared) -> list[str]:
    if not isinstance(computed, dict) or not isinstance(declared, dict):
        return ["<projection>"]
    fields = sorted(set(computed) | set(declared))
    mismatches = []
    for field in fields:
        expected = computed.get(field)
        actual = declared.get(field)
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if not _close(actual, expected):
                mismatches.append(field)
        elif actual != expected:
            mismatches.append(field)
    return mismatches


def _policy_scope_projection(policy: dict) -> dict:
    scope = policy.get("scope", {})
    if not isinstance(scope, dict):
        scope = {}
    mission_ids = scope.get("mission_ids", [])
    component_ids = scope.get("component_ids", [])
    return {
        "component_ids": sorted(item for item in component_ids if isinstance(item, str))
        if isinstance(component_ids, list) else [],
        "mission_ids": sorted(item for item in mission_ids if isinstance(item, str))
        if isinstance(mission_ids, list) else [],
        "tenant_id": scope.get("tenant_id"),
    }


def _policy_content_projection(policy: dict, scope_hash: str) -> dict:
    rules = copy.deepcopy(policy.get("rules", {}))
    if not isinstance(rules, dict):
        rules = {}
    if isinstance(rules.get("required_destructive_modes"), list):
        rules["required_destructive_modes"] = sorted(rules["required_destructive_modes"])
    return {
        "contract_version": policy.get("contract_version"),
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "rules": rules,
        "scope_hash": scope_hash,
    }


def _policy_evaluation(packet, mitigation, policy, projection, codes):
    summary = _empty_policy_summary()
    if not isinstance(policy, dict):
        codes.add("MALFORMED_POLICY")
        return summary, False
    scope = policy.get("scope")
    rules = policy.get("rules")
    approval = policy.get("approval")
    history = policy.get("immutable_history_ref")
    if not all(isinstance(value, dict) for value in (scope, rules, approval, history)):
        codes.add("MALFORMED_POLICY")
        return summary, False
    try:
        scope_hash = _sha256(_policy_scope_projection(policy))
        content_hash = _sha256(_policy_content_projection(policy, scope_hash))
    except (TypeError, ValueError):
        codes.add("MALFORMED_POLICY")
        return summary, False
    scope_matches = scope.get("scope_hash") == scope_hash
    content_matches = policy.get("policy_content_hash") == content_hash
    approval_target_matches = (
        approval.get("approval_scope_hash") == scope_hash
        and approval.get("approval_target_hash") == content_hash
    )
    history_matches = approval.get("history_head_hash") == history.get("head_hash")
    if policy.get("hash_contract_version") != "1.0.0":
        codes.add("POLICY_HASH_CONTRACT_MISSING")
    if not scope_matches:
        codes.add("POLICY_SCOPE_HASH_MISMATCH")
    if not content_matches:
        codes.add("POLICY_CONTENT_HASH_MISMATCH")
    if not approval_target_matches:
        codes.add("POLICY_APPROVAL_TARGET_MISMATCH")
    if not history_matches:
        codes.add("POLICY_HISTORY_MISMATCH")
    metadata = policy.get("metadata", {})
    if not isinstance(metadata, dict) or metadata.get("content_hash") != content_hash:
        codes.add("POLICY_METADATA_HASH_MISMATCH")
    mission_ids = set(_policy_scope_projection(policy)["mission_ids"])
    component_ids = set(_policy_scope_projection(policy)["component_ids"])
    packet_mission_ids = {
        record.get("mission_id")
        for record in _records_by_kind(packet, "MISSION")
        if record.get("mission_id")
    }
    packet_component_ids = {
        component.get("component_id")
        for bom in _records_by_kind(packet, "BOM")
        for component in bom.get("components", [])
        if isinstance(component, dict) and component.get("component_id")
    }
    mitigation_component_ids = set(mitigation.get("component_ids", []))
    if (
        not packet_mission_ids.issubset(mission_ids)
        or not mitigation_component_ids.issubset(component_ids)
        or not component_ids.issubset(packet_component_ids)
    ):
        codes.add("POLICY_SCOPE_REUSE_MISMATCH")
    packet_time = _parse_timestamp(packet.get("created_at"))
    valid_from = _parse_timestamp(approval.get("valid_from"))
    valid_until = _parse_timestamp(approval.get("valid_until"))
    valid_at_packet_time = bool(
        packet_time
        and valid_from
        and packet_time >= valid_from
        and (valid_until is None or packet_time <= valid_until)
    )
    if valid_from and valid_until and valid_from > valid_until:
        codes.add("POLICY_VALIDITY_INVALID")
    if packet_time and valid_until and packet_time > valid_until:
        codes.add("POLICY_EXPIRED")
    revoked = approval.get("status") == "REVOKED" or bool(approval.get("revoked_at"))
    if revoked:
        codes.add("POLICY_REVOKED")
    if approval.get("status") == "SUPERSEDED" or approval.get("superseded_by"):
        codes.add("POLICY_SUPERSEDED")
    status_approved = approval.get("status") == "APPROVED"
    policy_class = metadata.get("data_class") if isinstance(metadata, dict) else None
    evidence_eligible = policy_class not in {"SYNTHETIC", "ASSUMED", None}
    approval_eligible = bool(
        status_approved
        and scope_matches
        and content_matches
        and approval_target_matches
        and history_matches
        and valid_at_packet_time
        and not revoked
        and not approval.get("superseded_by")
    )
    if not status_approved:
        codes.add("POLICY_NOT_APPROVED")
    if not evidence_eligible:
        codes.add("NON_EVIDENTIARY_POLICY")
    rule_results = []
    for rule_id, key, projection_key in (
        ("MAXIMUM_REBOOTS", "maximum_reboots", "reboot_count_total"),
        ("MAXIMUM_DOWNTIME_SECONDS", "maximum_downtime_seconds", "downtime_total_seconds"),
    ):
        threshold_present = key in rules
        threshold = rules.get(key) if threshold_present else None
        actual = projection.get(projection_key) if isinstance(projection, dict) else None
        if threshold_present and _is_number(threshold) and _is_number(actual):
            outcome = "PASS" if actual <= threshold else "FAIL"
        else:
            outcome = "NOT_EVALUATED"
        rule_results.append({
            "rule_id": rule_id,
            "threshold_present": threshold_present,
            "threshold": threshold,
            "actual": actual,
            "outcome": outcome,
        })
    summary.update({
        "status": approval.get("status"),
        "hash_contract_version": policy.get("hash_contract_version"),
        "computed_scope_hash": scope_hash,
        "computed_content_hash": content_hash,
        "scope_matches": scope_matches,
        "content_matches": content_matches,
        "approval_target_matches": approval_target_matches,
        "history_matches": history_matches,
        "valid_at_packet_time": valid_at_packet_time,
        "approval_eligible": approval_eligible,
        "evidence_eligible": evidence_eligible,
        "rule_results": rule_results,
    })
    policy_valid = not codes.intersection({
        "MALFORMED_POLICY",
        "POLICY_APPROVAL_TARGET_MISMATCH",
        "POLICY_CONTENT_HASH_MISMATCH",
        "POLICY_EXPIRED",
        "POLICY_HASH_CONTRACT_MISSING",
        "POLICY_HISTORY_MISMATCH",
        "POLICY_METADATA_HASH_MISMATCH",
        "POLICY_REVOKED",
        "POLICY_SCOPE_HASH_MISMATCH",
        "POLICY_SUPERSEDED",
        "POLICY_VALIDITY_INVALID",
    })
    return summary, policy_valid


def evaluate_runtime_mitigation(packet: dict) -> dict:
    """Validate and independently calculate one WATCHDOG, TMR, or SEL control."""
    codes: set[str] = set()
    if not isinstance(packet, dict):
        codes.add("MALFORMED_EVIDENCE_PACKET")
        return _finalize(packet, codes=codes)
    non_finite = _non_finite_paths(packet)
    if non_finite:
        codes.add("NON_FINITE_NUMERIC_INPUT")
    try:
        schema_errors = packet_schema_errors(packet)
    except Exception:
        schema_errors = ["validator failure"]
        codes.add("PACKET_SCHEMA_VALIDATOR_FAILURE")
    try:
        codes.update(packet_semantic_errors(packet))
    except Exception:
        codes.add("PACKET_SEMANTIC_VALIDATOR_FAILURE")
    if schema_errors:
        codes.add("PACKET_SCHEMA_INVALID")
    mitigations = _records_by_kind(packet, "MITIGATION")
    policies = _records_by_kind(packet, "USER_POLICY")
    if len(mitigations) != 1:
        codes.add("MITIGATION_EXACT_ONE_REQUIRED")
    if len(policies) != 1:
        codes.add("USER_POLICY_EXACT_ONE_REQUIRED")
    mitigation = mitigations[0] if len(mitigations) == 1 else None
    policy = policies[0] if len(policies) == 1 else None
    method = mitigation.get("method") if mitigation else None
    effect_model = mitigation.get("effect_model") if mitigation else None
    equation_id = effect_model.get("equation_id") if isinstance(effect_model, dict) else None
    if mitigation is None or policy is None or non_finite:
        return _finalize(
            packet,
            mitigation=mitigation,
            policy=policy,
            method=method,
            equation_id=equation_id,
            codes=codes,
        )
    if mitigation.get("contract_version") != "2.0.0" or policy.get("contract_version") != "2.0.0":
        codes.add("CONTRACT_VERSION_MISMATCH")
    if mitigation.get("runtime_contract_version") != RUNTIME_CONTRACT_VERSION:
        codes.add("MITIGATION_RUNTIME_CONTRACT_MISSING")
    expected_equation = METHOD_EQUATIONS.get(method)
    if expected_equation is None:
        codes.add("UNSUPPORTED_RUNTIME_METHOD")
    elif equation_id != expected_equation:
        codes.add("MITIGATION_EQUATION_ID_MISMATCH")
    contract_blockers = codes - POST_CALCULATION_CONTRACT_CODES
    if schema_errors or contract_blockers.intersection({
        "CONTRACT_VERSION_MISMATCH",
        "MITIGATION_EXACT_ONE_REQUIRED",
        "MITIGATION_RUNTIME_CONTRACT_MISSING",
        "MITIGATION_EQUATION_ID_MISMATCH",
        "PACKET_SCHEMA_INVALID",
        "UNSUPPORTED_RUNTIME_METHOD",
        "USER_POLICY_EXACT_ONE_REQUIRED",
    }):
        return _finalize(
            packet,
            mitigation=mitigation,
            policy=policy,
            method=method,
            equation_id=equation_id,
            processing_status="INVALID_INPUT",
            declared_projection=mitigation.get("runtime_projection"),
            codes=codes,
        )
    if contract_blockers:
        return _finalize(
            packet,
            mitigation=mitigation,
            policy=policy,
            method=method,
            equation_id=equation_id,
            processing_status="INVALID_INPUT",
            declared_projection=mitigation.get("runtime_projection"),
            codes=codes,
        )
    if method == "WATCHDOG":
        counts, projection = _watchdog_projection(mitigation, codes)
    elif method == "TMR":
        counts, projection = _tmr_projection(mitigation, codes)
    else:
        counts, projection = _sel_projection(packet, mitigation, policy, codes)
    declared = mitigation.get("runtime_projection")
    if projection is None:
        return _finalize(
            packet,
            mitigation=mitigation,
            policy=policy,
            method=method,
            equation_id=equation_id,
            processing_status="INVALID_INPUT",
            normalized_counts=counts,
            declared_projection=declared,
            codes=codes,
        )
    mismatches = _projection_mismatches(projection, declared)
    if mismatches:
        projection_code = {
            "WATCHDOG": "WATCHDOG_RUNTIME_PROJECTION_MISMATCH",
            "TMR": "TMR_RUNTIME_PROJECTION_MISMATCH",
            "SEL_PROTECTION": "SEL_RUNTIME_PROJECTION_MISMATCH",
        }[method]
        codes.add(projection_code)
    policy_summary, policy_valid = _policy_evaluation(
        packet, mitigation, policy, projection, codes
    )
    mitigation_metadata = mitigation.get("metadata", {})
    if not isinstance(mitigation_metadata, dict) or mitigation_metadata.get("data_class") in {
        "SYNTHETIC", "ASSUMED", None,
    }:
        codes.add("NON_EVIDENTIARY_MITIGATION")
    applicability = mitigation.get("applicability", {})
    applicable = isinstance(applicability, dict) and applicability.get("status") == "APPLICABLE"
    if not applicable:
        codes.add("MITIGATION_APPLICABILITY_UNRESOLVED")
    packet_gaps = packet.get("decision", {}).get("evidence_gaps", [])
    if isinstance(packet_gaps, list) and any(
        isinstance(gap, dict) and gap.get("blocking") for gap in packet_gaps
    ):
        codes.add("BLOCKING_EVIDENCE_GAP")
    invalid = bool(mismatches) or not policy_valid or bool(
        (codes - POST_CALCULATION_CONTRACT_CODES).intersection({
            "INVALID_RUNTIME_NUMERIC_INPUT",
            "MALFORMED_ACTION_PATH",
            "MALFORMED_MITIGATION_PARAMETERS",
            "MITIGATION_EVIDENCE_LINK_MISMATCH",
        })
    )
    processing_status = "INVALID_INPUT" if invalid else "VALID"
    rule_outcomes = [item["outcome"] for item in policy_summary["rule_results"]]
    if processing_status != "VALID":
        engineering_gate = "NOT_EVALUATED"
    elif "FAIL" in rule_outcomes:
        engineering_gate = "FAIL"
    elif (
        "PASS" in rule_outcomes
        and policy_summary["approval_eligible"]
        and policy_summary["evidence_eligible"]
        and applicable
        and "BLOCKING_EVIDENCE_GAP" not in codes
    ):
        engineering_gate = "PASS"
    else:
        engineering_gate = "NOT_EVALUATED"
    return _finalize(
        packet,
        mitigation=mitigation,
        policy=policy,
        method=method,
        equation_id=equation_id,
        processing_status=processing_status,
        engineering_gate=engineering_gate,
        normalized_counts=counts,
        computed_projection=projection,
        declared_projection=declared,
        mismatched_fields=mismatches,
        policy_summary=policy_summary,
        codes=codes,
    )
