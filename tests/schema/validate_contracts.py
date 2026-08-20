#!/usr/bin/env python3
"""Validate SPECTRA schemas, composed fixtures, and fail-closed semantic rules."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
VALID_DIR = ROOT / "tests/schema/fixtures/valid"
INVALID_DIR = ROOT / "tests/schema/fixtures/invalid"
PACKET_SCHEMA = SCHEMA_DIR / "evidence-packet.schema.json"

DATA_CLASSES = {"PUBLISHED", "CALCULATED", "ASSUMED", "SYNTHETIC", "CUSTOMER_VERIFIED"}
REVIEW_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "READY_FOR_REVIEW", "VERIFIED", "INTEGRATED", "CHANGES_REQUESTED", "HOLD"}
ASSURANCE_DECISIONS = {"SUPPORTED_WITH_MITIGATION", "CONDITIONAL", "HOLD", "INSUFFICIENT_EVIDENCE"}
PROCESSING_STATUSES = {"VALID", "INVALID_INPUT", "OUT_OF_MODEL_SCOPE", "MODEL_FAILURE", "STALE_EVIDENCE", "PROVENANCE_FAILURE", "CONFLICTING_EVIDENCE"}
OPTIMISTIC = {"SUPPORTED_WITH_MITIGATION"}
SAFE_FAILURE_DECISIONS = {"HOLD", "INSUFFICIENT_EVIDENCE"}
EVIDENTIARY_CLASSES = {"PUBLISHED", "CALCULATED", "CUSTOMER_VERIFIED"}
UNIT_MAP = {
    "TID": {"rad(Si)", "krad(Si)", "Gy(Si)"},
    "SHIELDING": {"mm_Al_equivalent", "g/cm2"},
    "DURATION": {"s", "day", "year"},
    "PARTICLE_FLUX": {"particles/cm2/s"},
    "CROSS_SECTION": {"cm2/device", "cm2/bit"},
    "ALTITUDE": {"km", "m"},
    "ANGLE": {"deg"},
    "COUNT": {"count"},
    "RATE": {"events/day", "events/mission"},
}
REQUIRED_INPUT_KINDS = {
    "MISSION", "BOM", "RADIATION_ENVIRONMENT", "PART_TEST_EVIDENCE",
    "SHIELDING", "MITIGATION", "USER_POLICY",
}
RULE_OPERAND_REQUIREMENTS = {
    "TID_MARGIN_V1": {
        "MISSION_DOSE", "PART_TID_LIMIT", "TID_DESIGN_FACTOR",
        "POLICY_APPROVAL", "SHIELDING_THICKNESS", "MISSION_DURATION",
    },
}
RULE_OPERAND_TARGETS = {
    "MISSION_DOSE": ("RADIATION_ENVIRONMENT", ("mission_dose",)),
    "PART_TID_LIMIT": ("PART_TEST_EVIDENCE", ("tid_test_limit",)),
    "TID_DESIGN_FACTOR": ("USER_POLICY", ("tid_design_factor",)),
    "POLICY_APPROVAL": ("USER_POLICY", ("approval_status",)),
    "SHIELDING_THICKNESS": ("SHIELDING", ("equivalent_thickness",)),
    "MISSION_DURATION": ("MISSION", ("duration",)),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def policy_scope_projection(policy: dict) -> dict:
    scope = policy.get("scope", {})
    if not isinstance(scope, dict):
        scope = {}
    component_ids = scope.get("component_ids", [])
    mission_ids = scope.get("mission_ids", [])
    if not isinstance(component_ids, list):
        component_ids = []
    if not isinstance(mission_ids, list):
        mission_ids = []
    component_ids = [value for value in component_ids if isinstance(value, str)]
    mission_ids = [value for value in mission_ids if isinstance(value, str)]
    return {
        "component_ids": sorted(component_ids),
        "mission_ids": sorted(mission_ids),
        "tenant_id": scope.get("tenant_id"),
    }


def policy_content_projection(policy: dict, scope_hash: str) -> dict:
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


def tmr_limited_failure_probability(replica_failure_probability: float) -> float:
    return 3 * replica_failure_probability**2 - 2 * replica_failure_probability**3


def close_number(actual, expected) -> bool:
    return (
        isinstance(actual, (int, float))
        and not isinstance(actual, bool)
        and math.isfinite(actual)
        and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
    )


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def preflight_codes(packet: dict) -> set[str]:
    codes: set[str] = set()
    for node in walk(packet):
        if "quantity_kind" in node:
            if "unit" not in node:
                codes.add("MISSING_UNIT")
            elif node["unit"] not in UNIT_MAP.get(node["quantity_kind"], set()):
                codes.add("INCOMPATIBLE_UNIT")
            quantity_value = node.get("value")
            if isinstance(quantity_value, (int, float)) and not isinstance(quantity_value, bool):
                if node.get("quantity_kind") == "TID" and quantity_value < 0:
                    codes.add("NEGATIVE_TID")
                if node.get("quantity_kind") == "SHIELDING" and quantity_value <= 0:
                    codes.add("NON_POSITIVE_SHIELDING_THICKNESS")
        if "data_class" in node:
            data_class = node.get("data_class")
            if data_class not in DATA_CLASSES:
                codes.add("INVALID_DATA_CLASS")
            if "content_hash" not in node:
                codes.add("MISSING_CONTENT_HASH")
            if data_class in {"PUBLISHED", "CUSTOMER_VERIFIED", "ASSUMED"} and "source" not in node:
                codes.add("MISSING_SOURCE")
            if data_class in {"CALCULATED", "SYNTHETIC"} and "calculation_run" not in node:
                codes.add("MISSING_CALCULATION_RUN")
            source = node.get("source")
            if isinstance(source, dict) and not source.get("location"):
                codes.add("MISSING_SOURCE_LOCATION")
            if data_class != "SYNTHETIC" and isinstance(source, dict) and source.get("source_type") == "FIXTURE_SPEC":
                codes.add("SYNTHETIC_MISREPRESENTED")
    return codes


def semantic_codes(packet: dict) -> set[str]:
    codes = preflight_codes(packet)
    inputs = packet.get("inputs", [])
    if not isinstance(inputs, list):
        inputs = []
    by_kind = {}
    for item in inputs:
        if not isinstance(item, dict):
            codes.add("MALFORMED_INPUT_RECORD")
            continue
        by_kind.setdefault(item.get("kind"), []).append(item)
    if not REQUIRED_INPUT_KINDS.issubset(by_kind):
        codes.add("REQUIRED_INPUT_KIND_MISSING")
    if any(len(by_kind.get(kind, [])) > 1 for kind in REQUIRED_INPUT_KINDS):
        codes.add("DUPLICATE_REQUIRED_INPUT_KIND")
    decision = packet.get("decision", {})
    processing = decision.get("processing_status")
    assurance = decision.get("assurance_decision")
    packet_version = packet.get("schema_version")

    def parse_timestamp(value):
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    mitigations = by_kind.get("MITIGATION", [])
    policies = by_kind.get("USER_POLICY", [])
    has_v2_inputs = any(item.get("contract_version") == "2.0.0" for item in mitigations + policies)
    if packet_version == "1.0.0" and (has_v2_inputs or "raw_manifest_refs" in packet):
        codes.add("CONTRACT_VERSION_MIXED")
    if packet_version == "1.1.0" and (
        not mitigations or not policies
        or any(item.get("contract_version") != "2.0.0" for item in mitigations + policies)
    ):
        codes.add("CONTRACT_VERSION_MIXED")

    for mitigation in mitigations:
        if mitigation.get("contract_version") != "2.0.0":
            continue
        required_v2 = {"component_ids", "architecture_scope", "target_failure_modes", "excluded_failure_modes", "design_parameters", "applicability"}
        if not required_v2.issubset(mitigation):
            codes.add("V2_REQUIRED_FIELD_MISSING")
        raw_targets = mitigation.get("target_failure_modes", [])
        raw_excluded = mitigation.get("excluded_failure_modes", [])
        targets = set(raw_targets) if isinstance(raw_targets, list) else set()
        excluded = set(raw_excluded) if isinstance(raw_excluded, list) else set()
        if targets.intersection(excluded):
            codes.add("MITIGATION_MODE_OVERLAP")
        parameters = mitigation.get("design_parameters", {})
        if not isinstance(parameters, dict):
            codes.add("MALFORMED_MITIGATION_PARAMETERS")
            parameters = {}
        method = mitigation.get("method")
        allowed_runtime_modes = {
            "TMR": {"SEU", "SEFI", "SET", "FUNCTIONAL_INTERRUPT", "SILENT_DATA_CORRUPTION"},
            "WATCHDOG": {"SEFI", "FUNCTIONAL_INTERRUPT"},
            "SEL_PROTECTION": {"SEL"},
        }
        if method in allowed_runtime_modes and not targets.issubset(allowed_runtime_modes[method]):
            codes.add("MITIGATION_METHOD_MODE_MISMATCH")
        runtime_method = method in {"TMR", "WATCHDOG", "SEL_PROTECTION"}
        if runtime_method and mitigation.get("runtime_contract_version") != "1.0.0":
            codes.add("MITIGATION_RUNTIME_CONTRACT_MISSING")
        effect_model = mitigation.get("effect_model")
        if runtime_method and not isinstance(effect_model, dict):
            codes.add("MITIGATION_EFFECT_MODEL_MISSING")
        elif runtime_method and not effect_model.get("equation_id"):
            codes.add("MITIGATION_EQUATION_ID_MISSING")
        expected_equations = {
            "TMR": "TMR_3P2_MINUS_2P3_V1",
            "WATCHDOG": "WATCHDOG_TRUE_FALSE_PATH_V1",
            "SEL_PROTECTION": "SEL_TRUE_FALSE_PATH_V1",
        }
        if runtime_method and isinstance(effect_model, dict) and effect_model.get("equation_id") and effect_model.get("equation_id") != expected_equations[method]:
            codes.add("MITIGATION_EQUATION_ID_MISMATCH")
        if runtime_method and not mitigation.get("verification_evidence_ids"):
            codes.add("MITIGATION_EFFECT_EVIDENCE_MISSING")
        projection = mitigation.get("runtime_projection")
        if runtime_method and not isinstance(projection, dict):
            codes.add("MITIGATION_RUNTIME_PROJECTION_MISSING")

        def normalized_count(model: dict, count_key: str, rate_key: str, window: dict):
            if not isinstance(model, dict):
                return None
            has_count = count_key in model
            has_rate = rate_key in model
            if has_count == has_rate:
                codes.add("ACTIVATION_COUNT_RATE_CONFLICT")
                return None
            if has_count:
                return model.get(count_key)
            denominator = model.get("denominator", {})
            if not isinstance(denominator, dict):
                codes.add("MALFORMED_MITIGATION_PARAMETERS")
                return None
            denominator_count = denominator.get("count")
            duration = window.get("duration_seconds") if isinstance(window, dict) else None
            rate = model.get(rate_key)
            if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (rate, denominator_count, duration)):
                return rate * denominator_count * duration
            return None

        def action_paths(model: dict) -> list[dict]:
            if not isinstance(model, dict):
                return []
            paths = model.get("action_paths", [])
            if not isinstance(paths, list):
                codes.add("MALFORMED_ACTION_PATH")
                return []
            valid_paths = []
            for path in paths:
                if not isinstance(path, dict):
                    codes.add("MALFORMED_ACTION_PATH")
                    continue
                valid_paths.append(path)
            return valid_paths

        def paths_are_complete(paths: list[dict]) -> bool:
            fractions = [path.get("fraction") for path in paths]
            if any(
                not isinstance(fraction, (int, float)) or isinstance(fraction, bool)
                for fraction in fractions
            ):
                codes.add("MALFORMED_ACTION_PATH")
                return False
            total = sum(fractions)
            if not paths or not close_number(total, 1.0):
                codes.add("ACTION_PATH_FRACTION_INVALID")
                return False
            return True

        def denominator_matches(model: dict, window: dict):
            if isinstance(model, dict) and isinstance(window, dict):
                denominator = model.get("denominator", {})
                if not isinstance(denominator, dict):
                    codes.add("MALFORMED_MITIGATION_PARAMETERS")
                elif denominator.get("scope") != window.get("denominator_scope"):
                    codes.add("RECOVERY_DENOMINATOR_WINDOW_MISMATCH")

        if method == "TMR":
            voter_model = parameters.get("voter_model")
            common_mode_model = parameters.get("common_mode_model")
            repair_model = parameters.get("repair_model")
            if not isinstance(voter_model, dict):
                codes.add("TMR_VOTER_MODEL_MISSING")
            elif voter_model.get("susceptible") is not False:
                codes.add("TMR_VOTER_SUSCEPTIBLE")
            if not isinstance(common_mode_model, dict):
                codes.add("TMR_COMMON_MODE_MODEL_MISSING")
            elif common_mode_model.get("probability") != 0:
                codes.add("TMR_COMMON_MODE_NONZERO")
            if not isinstance(parameters.get("evaluation_window"), dict) or not isinstance(repair_model, dict):
                codes.add("TMR_REPAIR_WINDOW_MISSING")
            elif repair_model.get("repair_within_window") is not False:
                codes.add("TMR_REPAIR_WINDOW_MISMATCH")
            if parameters.get("independence_verified") is not True:
                codes.add("TMR_INDEPENDENCE_UNVERIFIED")
            if parameters.get("output_semantic") != "system_failure_probability":
                codes.add("TMR_OUTPUT_SEMANTIC_MISMATCH")
            eligible = (
                isinstance(voter_model, dict) and voter_model.get("susceptible") is False
                and isinstance(common_mode_model, dict) and common_mode_model.get("probability") == 0
                and parameters.get("independence_verified") is True
                and isinstance(repair_model, dict) and repair_model.get("repair_within_window") is False
                and isinstance(parameters.get("evaluation_window"), dict)
                and parameters.get("output_semantic") == "system_failure_probability"
            )
            p = parameters.get("replica_failure_probability")
            if eligible and isinstance(p, (int, float)) and not isinstance(p, bool) and isinstance(projection, dict):
                expected = tmr_limited_failure_probability(p)
                if not close_number(projection.get("system_failure_probability"), expected):
                    codes.add("TMR_RUNTIME_PROJECTION_MISMATCH")

        if method == "WATCHDOG":
            window = parameters.get("evaluation_window", {})
            target_model = parameters.get("target_event_model")
            false_model = parameters.get("false_positive_model")
            if parameters.get("true_positive_coverage") is None:
                codes.add("WATCHDOG_TRUE_POSITIVE_COVERAGE_MISSING")
            if not false_model:
                codes.add("WATCHDOG_FALSE_POSITIVE_MODEL_MISSING")
            denominator_matches(target_model, window)
            denominator_matches(false_model, window)
            target_paths = action_paths(target_model)
            false_paths = action_paths(false_model)
            target_paths_valid = paths_are_complete(target_paths)
            false_paths_valid = paths_are_complete(false_paths)
            target_count = normalized_count(target_model, "event_count", "event_rate_per_second", window)
            false_count = normalized_count(false_model, "activation_count", "activation_rate_per_second", window)
            coverage = parameters.get("true_positive_coverage")
            if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (target_count, false_count, coverage)) and target_paths_valid and false_paths_valid and isinstance(projection, dict):
                true_count = target_count * coverage
                durations_valid = all(
                    isinstance(path.get("duration_seconds"), (int, float))
                    and not isinstance(path.get("duration_seconds"), bool)
                    for path in target_paths + false_paths
                )
                if not durations_valid:
                    codes.add("MALFORMED_ACTION_PATH")
                    continue
                true_reboots = sum(true_count * path["fraction"] for path in target_paths if path.get("action") == "REBOOT")
                false_reboots = sum(false_count * path["fraction"] for path in false_paths if path.get("action") == "REBOOT")
                latency = parameters.get("detection_latency_seconds", 0)
                if not isinstance(latency, (int, float)) or isinstance(latency, bool):
                    codes.add("MALFORMED_MITIGATION_PARAMETERS")
                    continue
                true_downtime = sum(true_count * path["fraction"] * (latency + path["duration_seconds"]) for path in target_paths)
                false_downtime = sum(false_count * path["fraction"] * path["duration_seconds"] for path in false_paths)
                expected_reboots = true_reboots + false_reboots
                expected_downtime = true_downtime + false_downtime
                if not close_number(projection.get("true_target_event_count"), target_count) or not close_number(projection.get("true_positive_activation_count"), true_count):
                    codes.add("WATCHDOG_RUNTIME_PROJECTION_MISMATCH")
                if not close_number(projection.get("false_positive_activation_count"), false_count) or (
                    false_count > 0 and (
                        not close_number(projection.get("reboot_count_total"), expected_reboots)
                        or not close_number(projection.get("downtime_total_seconds"), expected_downtime)
                    )
                ):
                    codes.add("WATCHDOG_FALSE_POSITIVE_IGNORED")
                double_latency = expected_downtime + true_count * latency
                if true_count * latency > 0 and close_number(projection.get("downtime_total_seconds"), double_latency):
                    codes.add("WATCHDOG_DETECTION_LATENCY_DOUBLE_COUNTED")
                elif not close_number(projection.get("reboot_count_total"), expected_reboots) or not close_number(projection.get("downtime_total_seconds"), expected_downtime):
                    codes.add("WATCHDOG_RUNTIME_PROJECTION_MISMATCH")

        if method == "SEL_PROTECTION":
            window = parameters.get("evaluation_window", {})
            true_model = parameters.get("true_sel_model")
            false_model = parameters.get("false_trip_model")
            if not false_model:
                codes.add("SEL_FALSE_TRIP_MODEL_MISSING")
            required_sel_evidence = {
                "prompt_failure_evidence_id", "latent_damage_evidence_id", "post_test_electrical_evidence_id"
            }
            if any(not parameters.get(field) for field in required_sel_evidence):
                codes.add("SEL_PROTECTION_NOT_VALIDATED")
            sel_paths = []
            for model in (true_model, false_model):
                denominator_matches(model, window)
                paths = action_paths(model)
                sel_paths.append(paths)
                paths_are_complete(paths)
                if any("duration_seconds" in path for path in paths):
                    codes.add("SEL_DURATION_SEMANTIC_CONFLICT")
            true_count = normalized_count(true_model, "activation_count", "activation_rate_per_second", window)
            false_count = normalized_count(false_model, "activation_count", "activation_rate_per_second", window)
            if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (true_count, false_count)) and isinstance(projection, dict):
                true_cycles = sum(true_count * path["fraction"] for path in sel_paths[0] if path.get("action") == "POWER_CYCLE")
                false_cycles = sum(false_count * path["fraction"] for path in sel_paths[1] if path.get("action") == "POWER_CYCLE")
                phase_values = [
                    parameters.get(field, 0)
                    for field in ("trip_delay_seconds", "off_time_seconds", "restart_time_seconds")
                ]
                if any(
                    not isinstance(value, (int, float)) or isinstance(value, bool)
                    for value in phase_values
                ):
                    codes.add("MALFORMED_MITIGATION_PARAMETERS")
                    continue
                phase_duration = sum(phase_values)
                expected_cycles = true_cycles + false_cycles
                expected_downtime = expected_cycles * phase_duration
                if not close_number(projection.get("true_sel_activation_count"), true_count) or not close_number(projection.get("false_trip_activation_count"), false_count) or not close_number(projection.get("power_cycle_count_total"), expected_cycles):
                    codes.add("SEL_RUNTIME_PROJECTION_MISMATCH")
                if close_number(projection.get("downtime_total_seconds"), expected_downtime * 2) and expected_downtime > 0:
                    codes.add("SEL_DURATION_DOUBLE_COUNTED")
                elif not close_number(projection.get("downtime_total_seconds"), expected_downtime):
                    codes.add("SEL_RUNTIME_PROJECTION_MISMATCH")
        if runtime_method:
            raw_declared_evidence = mitigation.get("verification_evidence_ids", [])
            declared_evidence = set(raw_declared_evidence) if isinstance(raw_declared_evidence, list) else set()
            parameter_evidence = {
                value for key, value in parameters.items()
                if key.endswith("_evidence_id") and isinstance(value, str)
            }
            for model_name in ("target_event_model", "false_positive_model", "true_sel_model", "false_trip_model", "voter_model", "common_mode_model"):
                model = parameters.get(model_name)
                if isinstance(model, dict):
                    evidence_id = model.get("verification_evidence_id", model.get("evidence_id"))
                    if evidence_id:
                        parameter_evidence.add(evidence_id)
            if not parameter_evidence.issubset(declared_evidence):
                codes.add("MITIGATION_EVIDENCE_LINK_MISMATCH")
        mitigation_metadata = mitigation.get("metadata", {})
        if not isinstance(mitigation_metadata, dict):
            mitigation_metadata = {}
        if assurance in OPTIMISTIC and mitigation_metadata.get("data_class") in {"SYNTHETIC", "ASSUMED"}:
            codes.add("NON_EVIDENTIARY_MITIGATION_OPERAND")

    for policy in policies:
        if policy.get("contract_version") != "2.0.0":
            continue
        required_v2 = {"policy_version", "policy_content_hash", "scope", "rules", "approval", "immutable_history_ref"}
        if not required_v2.issubset(policy):
            codes.add("V2_REQUIRED_FIELD_MISSING")
        approval = policy.get("approval", {})
        if not isinstance(approval, dict):
            codes.add("MALFORMED_POLICY_APPROVAL")
            approval = {}
        scope = policy.get("scope", {})
        if not isinstance(scope, dict):
            codes.add("MALFORMED_POLICY_SCOPE")
            scope = {}
        rules = policy.get("rules", {})
        if not isinstance(rules, dict):
            codes.add("MALFORMED_POLICY_RULES")
            rules = {}
        history = policy.get("immutable_history_ref", {})
        if not isinstance(history, dict):
            codes.add("MALFORMED_POLICY_HISTORY")
            history = {}
        mission_ids = scope.get("mission_ids", [])
        component_ids = scope.get("component_ids", [])
        if (
            not isinstance(mission_ids, list)
            or not isinstance(component_ids, list)
            or (isinstance(mission_ids, list) and any(not isinstance(value, str) for value in mission_ids))
            or (isinstance(component_ids, list) and any(not isinstance(value, str) for value in component_ids))
        ):
            codes.add("MALFORMED_POLICY_SCOPE")
            mission_ids = [value for value in mission_ids if isinstance(value, str)] if isinstance(mission_ids, list) else []
            component_ids = [value for value in component_ids if isinstance(value, str)] if isinstance(component_ids, list) else []
        destructive_modes = rules.get("required_destructive_modes", [])
        if not isinstance(destructive_modes, list):
            codes.add("MALFORMED_DESTRUCTIVE_MODES")
            destructive_modes = []
        hash_contract = policy.get("hash_contract_version") == "1.0.0"
        if hash_contract:
            computed_scope_hash = canonical_sha256(policy_scope_projection(policy))
            computed_content_hash = canonical_sha256(policy_content_projection(policy, computed_scope_hash))
            if scope.get("scope_hash") != computed_scope_hash:
                codes.add("POLICY_SCOPE_HASH_MISMATCH")
            if policy.get("policy_content_hash") != computed_content_hash:
                codes.add("POLICY_CONTENT_HASH_MISMATCH")
            if approval.get("approval_target_hash") != computed_content_hash:
                codes.add("POLICY_APPROVAL_TARGET_MISMATCH")
            if approval.get("approval_scope_hash") != computed_scope_hash:
                codes.add("POLICY_SCOPE_HASH_MISMATCH")
                codes.add("POLICY_APPROVAL_TARGET_MISMATCH")
            if approval.get("history_head_hash") != history.get("head_hash"):
                codes.add("POLICY_HISTORY_MISMATCH")
            packet_mission_ids = {
                mission.get("mission_id") for mission in by_kind.get("MISSION", []) if mission.get("mission_id")
            }
            packet_component_ids = {
                component.get("component_id")
                for bom in by_kind.get("BOM", [])
                for component in bom.get("components", [])
                if component.get("component_id")
            }
            if not packet_mission_ids.issubset(set(mission_ids)) or not {
                component_id for mitigation in mitigations for component_id in mitigation.get("component_ids", [])
            }.issubset(set(component_ids)) or not set(component_ids).issubset(packet_component_ids):
                codes.add("POLICY_SCOPE_REUSE_MISMATCH")
        elif approval.get("approval_target_hash") != policy.get("policy_content_hash") or approval.get("approval_scope_hash") != scope.get("scope_hash"):
            codes.add("POLICY_APPROVAL_TARGET_MISMATCH")
        created_at = parse_timestamp(packet.get("created_at"))
        valid_from = parse_timestamp(approval.get("valid_from"))
        valid_until = parse_timestamp(approval.get("valid_until"))
        revoked = approval.get("status") == "REVOKED" or bool(approval.get("revoked_at"))
        expired = bool(created_at and valid_until and created_at > valid_until)
        if valid_from and valid_until and valid_from > valid_until:
            codes.add("POLICY_VALIDITY_INVALID")
        if revoked:
            codes.add("POLICY_REVOKED")
        if expired:
            codes.add("POLICY_EXPIRED")
        if assurance in OPTIMISTIC:
            if approval.get("status") != "APPROVED" or revoked:
                codes.add("POLICY_PACK_NOT_APPROVED")
            if approval.get("status") == "APPROVED" and not hash_contract:
                codes.add("POLICY_HASH_CONTRACT_MISSING")
            if created_at and ((valid_from and created_at < valid_from) or expired):
                codes.add("POLICY_PACK_NOT_APPROVED")
            policy_metadata = policy.get("metadata", {})
            if not isinstance(policy_metadata, dict):
                policy_metadata = {}
            if policy_metadata.get("data_class") in {"SYNTHETIC", "ASSUMED"}:
                codes.add("SYNTHETIC_POLICY_WITH_SUPPORT")

    if processing and processing != "VALID" and assurance not in SAFE_FAILURE_DECISIONS:
        codes.add("PROCESSING_DECISION_CONFLICT")

    def pointer_tokens(pointer: str) -> list[str]:
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            return []
        return [token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:]]

    def resolve_tokens(tokens: list[str]):
        current = packet
        try:
            for token in tokens:
                current = current[int(token)] if isinstance(current, list) else current[token]
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def resolve_pointer(pointer: str):
        return resolve_tokens(pointer_tokens(pointer))

    def encode_pointer(tokens: list[str]) -> str:
        return "/" + "/".join(token.replace("~", "~0").replace("/", "~1") for token in tokens)

    def input_metadata(tokens: list[str]):
        if len(tokens) < 2 or tokens[0] != "inputs":
            return None
        for depth in range(len(tokens), 1, -1):
            prefix = tokens[:depth]
            node = resolve_tokens(prefix)
            if not isinstance(node, dict):
                continue
            if "data_class" in node:
                return node
            metadata = node.get("metadata")
            if isinstance(metadata, dict) and "data_class" in metadata:
                return metadata
        return None

    def allowed_origin_pointers(tokens: list[str], metadata: dict) -> set[str]:
        data_class = metadata.get("data_class")
        origin_key = "source" if data_class in {"PUBLISHED", "CUSTOMER_VERIFIED", "ASSUMED"} else "calculation_run"
        expected_origin = metadata.get(origin_key)
        if expected_origin is None:
            return set()
        allowed = set()
        for depth in range(len(tokens), 1, -1):
            prefix = tokens[:depth]
            node = resolve_tokens(prefix)
            if not isinstance(node, dict):
                continue
            if node.get(origin_key) == expected_origin:
                allowed.add(encode_pointer(prefix + [origin_key]))
            candidate_metadata = node.get("metadata")
            if isinstance(candidate_metadata, dict) and candidate_metadata.get(origin_key) == expected_origin:
                allowed.add(encode_pointer(prefix + ["metadata", origin_key]))
        return allowed

    traces = packet.get("trace", [])
    trace_ids = [trace.get("trace_id") for trace in traces]
    if len(trace_ids) != len(set(trace_ids)):
        codes.add("DUPLICATE_TRACE_ID")
    traces_by_id = {}
    source_class_by_trace = {}
    for trace in traces:
        traces_by_id.setdefault(trace.get("trace_id"), []).append(trace)
        input_pointer = trace.get("input_pointer", "")
        origin_pointer = trace.get("origin_pointer", "")
        input_tokens = pointer_tokens(input_pointer)
        input_value = resolve_pointer(input_pointer)
        origin_value = resolve_pointer(origin_pointer)
        if input_value is None or origin_value is None:
            codes.add("BROKEN_TRACE_POINTER")
            continue
        metadata = input_metadata(input_tokens)
        if metadata is None:
            codes.add("TRACE_INPUT_METADATA_MISSING")
            continue
        source_class_by_trace[id(trace)] = metadata.get("data_class")
        if origin_pointer not in allowed_origin_pointers(input_tokens, metadata):
            codes.add("UNRELATED_TRACE_ORIGIN")
    has_decision_trace = any(trace.get("used_for_decision") for trace in traces)
    rule_results = decision.get("rule_results", [])
    rule_ids = [result.get("rule_id") for result in rule_results]
    if len(rule_ids) != len(set(rule_ids)):
        codes.add("DUPLICATE_RULE_ID")
    for result in rule_results:
        rule_id = result.get("rule_id")
        referenced_ids = result.get("trace_ids", [])
        if not referenced_ids:
            codes.add("RULE_WITHOUT_TRACE")
            continue

        referenced_traces = []
        missing_reference = False
        for trace_id in referenced_ids:
            matches = traces_by_id.get(trace_id, [])
            if not matches:
                missing_reference = True
                codes.add("BROKEN_DECISION_TRACE")
            referenced_traces.extend(matches)
        if missing_reference:
            continue

        if any(rule_id not in trace.get("decision_rule_ids", []) for trace in referenced_traces):
            codes.add("RULE_TRACE_MISMATCH")
            continue

        if assurance in OPTIMISTIC and any(
            trace.get("applicability", {}).get("status") != "APPLICABLE" for trace in referenced_traces
        ):
            codes.add("DECISION_TRACE_NOT_APPLICABLE")

        if assurance in OPTIMISTIC and result.get("outcome") == "PASS" and has_decision_trace and not any(
            trace.get("used_for_decision") for trace in referenced_traces
        ):
            codes.add("SUPPORT_RULE_WITHOUT_DECISION_TRACE")

        if assurance in OPTIMISTIC and result.get("outcome") == "PASS":
            required_operands = RULE_OPERAND_REQUIREMENTS.get(rule_id)
            bindings = result.get("operand_bindings", [])
            binding_roles = [binding.get("operand_role") for binding in bindings]
            if required_operands is None:
                codes.add("RULE_OPERAND_CONTRACT_UNKNOWN")
            elif not required_operands.issubset(set(binding_roles)):
                codes.add("RULE_OPERAND_TRACE_MISSING")
            if len(binding_roles) != len(set(binding_roles)):
                codes.add("DUPLICATE_RULE_OPERAND_ROLE")

            for binding in bindings:
                operand_role = binding.get("operand_role")
                input_pointer = binding.get("input_pointer", "")
                origin_pointer = binding.get("origin_pointer", "")
                input_tokens = pointer_tokens(input_pointer)
                operand_value = resolve_pointer(input_pointer)
                operand_origin = resolve_pointer(origin_pointer)
                if operand_value is None or operand_origin is None:
                    codes.add("BROKEN_RULE_OPERAND_POINTER")
                    continue
                metadata = input_metadata(input_tokens)
                if metadata is None:
                    codes.add("RULE_OPERAND_METADATA_MISSING")
                    continue
                if origin_pointer not in allowed_origin_pointers(input_tokens, metadata):
                    codes.add("UNRELATED_RULE_OPERAND_ORIGIN")

                expected_target = RULE_OPERAND_TARGETS.get(operand_role)
                try:
                    input_index = int(input_tokens[1])
                    input_kind = inputs[input_index].get("kind")
                    input_record_metadata = inputs[input_index].get("metadata", {})
                    relative_path = tuple(input_tokens[2:])
                except (IndexError, TypeError, ValueError):
                    input_kind = None
                    input_record_metadata = {}
                    relative_path = ()
                if expected_target is None or (input_kind, relative_path) != expected_target:
                    codes.add("RULE_OPERAND_ROLE_MISMATCH")

                operand_classes = {metadata.get("data_class"), input_record_metadata.get("data_class")}
                if operand_classes.intersection({"SYNTHETIC", "ASSUMED"}):
                    codes.add("NON_EVIDENTIARY_RULE_OPERAND")
                if operand_role in {"TID_DESIGN_FACTOR", "POLICY_APPROVAL"} and "SYNTHETIC" in operand_classes:
                    codes.add("SYNTHETIC_POLICY_WITH_SUPPORT")

    if assurance in OPTIMISTIC and (not policies or any(p.get("approval_status") != "APPROVED" for p in policies)):
        if any(p.get("contract_version") != "2.0.0" for p in policies):
            codes.add("UNAPPROVED_POLICY_SUPPORT")

    if assurance in OPTIMISTIC:
        decision_traces = [trace for trace in traces if trace.get("used_for_decision")]
        if not decision_traces:
            codes.add("SUPPORT_WITHOUT_DECISION_TRACE")
        if any(result.get("outcome") != "PASS" for result in decision.get("rule_results", [])):
            codes.add("NON_PASS_RULE_WITH_SUPPORT")
        for trace in decision_traces:
            if trace.get("applicability", {}).get("status") != "APPLICABLE":
                codes.add("DECISION_TRACE_NOT_APPLICABLE")
            metadata = trace.get("normalized_value", {}).get("metadata", {})
            if metadata.get("data_class") in {"SYNTHETIC", "ASSUMED"}:
                codes.add("NON_EVIDENTIARY_DECISION_INPUT")
            if source_class_by_trace.get(id(trace)) in {"SYNTHETIC", "ASSUMED"}:
                codes.add("NON_EVIDENTIARY_SOURCE_INPUT")
        if any(gap.get("blocking") for gap in decision.get("evidence_gaps", [])):
            codes.add("BLOCKING_GAP_WITH_SUPPORT")

    component_by_id = {}
    for bom in by_kind.get("BOM", []):
        for component in bom.get("components", []):
            component_by_id[component.get("component_id")] = component
    identity_fields = ("manufacturer", "part_number", "process_id", "die_revision", "lot_id", "date_code")
    for evidence in by_kind.get("PART_TEST_EVIDENCE", []):
        component = component_by_id.get(evidence.get("component_id"))
        if not component:
            codes.add("EVIDENCE_COMPONENT_NOT_FOUND")
            continue
        expected = component.get("identity", {})
        tested = evidence.get("tested_identity", {})
        if any(expected.get(field) != tested.get(field) for field in identity_fields if expected.get(field) or tested.get(field)):
            codes.add("PART_IDENTITY_MISMATCH")

    require_destructive = any(p.get("require_destructive_see_evidence") for p in policies)
    if require_destructive:
        destructive = {"SEL", "SEB", "SEGR"}
        for evidence in by_kind.get("PART_TEST_EVIDENCE", []):
            if not destructive.intersection(evidence.get("evidence_types", [])):
                codes.add("DESTRUCTIVE_SEE_EVIDENCE_MISSING")
    required_destructive_modes = set()
    for policy in policies:
        if policy.get("contract_version") != "2.0.0":
            continue
        rules = policy.get("rules", {})
        if not isinstance(rules, dict):
            continue
        modes = rules.get("required_destructive_modes", [])
        if isinstance(modes, list):
            required_destructive_modes.update(modes)
    if required_destructive_modes:
        available_modes = set().union(*(
            set(evidence.get("evidence_types", [])) for evidence in by_kind.get("PART_TEST_EVIDENCE", [])
        )) if by_kind.get("PART_TEST_EVIDENCE") else set()
        if not required_destructive_modes.issubset(available_modes):
            codes.add("DESTRUCTIVE_SEE_MODE_MISSING")

    environments = by_kind.get("RADIATION_ENVIRONMENT", [])
    required_chain_roles = {"ORBIT", "TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT", "TRANSPORT_DOSE"}

    for environment in environments:
        variant = environment.get("environment_variant")
        chain = environment.get("model_chain")
        manifest = environment.get("raw_artifact_manifest")
        environment_class = environment.get("metadata", {}).get("data_class")
        dose = environment.get("mission_dose", environment.get("tid", {}))
        dose_metadata = dose.get("metadata", {}) if isinstance(dose, dict) else {}

        dose_value = dose.get("value") if isinstance(dose, dict) else None
        if isinstance(dose_value, (int, float)) and not isinstance(dose_value, bool) and dose_value < 0:
            codes.add("NEGATIVE_TID")
        thickness_value = environment.get("shielding_point", {}).get("thickness", {}).get("value")
        if isinstance(thickness_value, (int, float)) and not isinstance(thickness_value, bool) and thickness_value <= 0:
            codes.add("NON_POSITIVE_SHIELDING_THICKNESS")

        validity = environment.get("valid_for", {})
        validity_start = parse_timestamp(validity.get("start_at"))
        validity_end = parse_timestamp(validity.get("end_at"))
        if validity_start and validity_end and validity_start > validity_end:
            codes.add("INVALID_VALIDITY_INTERVAL")

        if variant == "TID_ONLY" and "particle_flux" in environment:
            codes.add("TID_ONLY_PLACEHOLDER_FLUX")
        if variant == "TID_ONLY" and environment.get("dose_scope") == "MISSION" and environment.get("source_completeness") != "COMPLETE_MISSION":
            codes.add("INCOMPLETE_MISSION_TID_SOURCE")

        if environment_class == "CALCULATED" and (not chain or not manifest):
            codes.add("CALCULATED_ENVIRONMENT_PROVENANCE_MISSING")
        if assurance in OPTIMISTIC and (not chain or not manifest):
            codes.add("SUPPORT_WITHOUT_ENVIRONMENT_PROVENANCE")

        if variant == "TID_ONLY" and not chain:
            codes.add("MODEL_CHAIN_MISSING")
        if variant == "TID_ONLY" and not manifest:
            codes.add("RAW_ARTIFACT_MANIFEST_MISSING")

        if isinstance(chain, dict):
            stages = chain.get("stages", [])
            stage_ids = [stage.get("stage_id") for stage in stages]
            if len(stage_ids) != len(set(stage_ids)):
                codes.add("DUPLICATE_MODEL_STAGE_ID")
            known_stage_ids = set(stage_ids)
            roles = {stage.get("role") for stage in stages}
            role_by_id = {stage.get("stage_id"): stage.get("role") for stage in stages}
            stages_by_id = {stage.get("stage_id"): stage for stage in stages}
            representative_stage = stages_by_id.get(chain.get("representative_stage_id"))
            if not representative_stage:
                codes.add("REPRESENTATIVE_MODEL_STAGE_MISSING")
            elif variant == "TID_ONLY" and (
                environment.get("model_name") != representative_stage.get("model_name")
                or environment.get("model_version") != representative_stage.get("model_version")
            ):
                codes.add("TOP_LEVEL_MODEL_STAGE_MISMATCH")
            dependencies = {}
            for stage in stages:
                stage_id = stage.get("stage_id")
                if not stage.get("model_version") or not stage.get("model_build"):
                    codes.add("MODEL_STAGE_VERSION_MISSING")
                has_reference = bool(stage.get("configuration_reference"))
                has_hash = bool(stage.get("configuration_hash"))
                if has_reference == has_hash:
                    codes.add("MODEL_STAGE_CONFIG_MISSING")
                depends_on = stage.get("depends_on", [])
                dependencies[stage_id] = depends_on
                if any(parent not in known_stage_ids or parent == stage_id for parent in depends_on):
                    codes.add("BROKEN_MODEL_STAGE_LINK")
                dependency_roles = {role_by_id.get(parent) for parent in depends_on}
                if stage.get("role") == "ORBIT" and depends_on:
                    codes.add("BROKEN_MODEL_STAGE_LINK")
                if stage.get("role") in {"TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT"} and "ORBIT" not in dependency_roles:
                    codes.add("BROKEN_MODEL_STAGE_LINK")

            visiting: set[str] = set()
            visited: set[str] = set()

            def has_cycle(stage_id: str) -> bool:
                if stage_id in visiting:
                    return True
                if stage_id in visited:
                    return False
                visiting.add(stage_id)
                cycle = any(parent in dependencies and has_cycle(parent) for parent in dependencies.get(stage_id, []))
                visiting.remove(stage_id)
                visited.add(stage_id)
                return cycle

            if any(has_cycle(stage_id) for stage_id in dependencies):
                codes.add("BROKEN_MODEL_STAGE_LINK")

            approved_scope = chain.get("approved_scope")
            if approved_scope not in {"MISSION_TID_COMPLETE", "TRAPPED_ONLY_RESEARCH", "PARTIAL_RESEARCH"}:
                codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")
            if variant == "TID_ONLY" and environment.get("dose_scope") == "MISSION":
                if approved_scope != "MISSION_TID_COMPLETE" or not required_chain_roles.issubset(roles):
                    codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")
                transport_stages = [stage for stage in stages if stage.get("role") == "TRANSPORT_DOSE"]
                if not transport_stages or any(
                    {role_by_id.get(parent) for parent in stage.get("depends_on", [])}
                    < {"TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT"}
                    for stage in transport_stages
                ):
                    codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")

        if variant == "TID_ONLY" and assurance in OPTIMISTIC and (
            environment.get("dose_scope") != "MISSION"
            or environment.get("source_completeness") != "COMPLETE_MISSION"
        ):
            codes.add("INCOMPLETE_ENVIRONMENT_WITH_SUPPORT")

        if isinstance(manifest, dict):
            manifest_version = manifest.get("contract_version")
            if (packet_version == "1.0.0" and manifest_version == "2.0.0") or (
                packet_version == "1.1.0" and manifest_version != "2.0.0"
            ):
                codes.add("CONTRACT_VERSION_MIXED")
            if environment.get("run_id") != manifest.get("run_id"):
                codes.add("ENVIRONMENT_MANIFEST_RUN_MISMATCH")
            calculation_run = environment.get("metadata", {}).get("calculation_run", {})
            if calculation_run and environment.get("run_id") != calculation_run.get("run_id"):
                codes.add("ENVIRONMENT_CALCULATION_RUN_MISMATCH")
            dose_calculation_run = dose_metadata.get("calculation_run", {})
            if dose_calculation_run and environment.get("run_id") != dose_calculation_run.get("run_id"):
                codes.add("MISSION_DOSE_RUN_MISMATCH")
            manifest_calculation_run = manifest.get("metadata", {}).get("calculation_run", {})
            if manifest_calculation_run and environment.get("run_id") != manifest_calculation_run.get("run_id"):
                codes.add("MANIFEST_METADATA_RUN_MISMATCH")
            if variant == "TID_ONLY" and any(
                not run for run in (calculation_run, dose_calculation_run, manifest_calculation_run)
            ):
                codes.add("TID_RUN_PROVENANCE_MISSING")
            bundle_hash = manifest.get("bundle_hash")
            parser = manifest.get("parser", {})
            if parser.get("input_bundle_hash") != bundle_hash:
                codes.add("PARSER_BUNDLE_HASH_MISMATCH")
            dose_hash = environment.get("mission_dose", {}).get("metadata", {}).get("content_hash")
            if dose_hash and parser.get("output_hash") != dose_hash:
                codes.add("PARSER_OUTPUT_HASH_MISMATCH")
            dose_output_hash = dose_calculation_run.get("output_hash")
            if dose_hash and dose_output_hash and dose_output_hash != dose_hash:
                codes.add("MISSION_DOSE_OUTPUT_HASH_MISMATCH")
            timestamps = manifest.get("timestamps", {})
            submitted_at = parse_timestamp(timestamps.get("submitted_at"))
            completed_at = parse_timestamp(timestamps.get("completed_at"))
            downloaded_at = parse_timestamp(timestamps.get("downloaded_at"))
            if submitted_at and completed_at and downloaded_at and not (submitted_at <= completed_at <= downloaded_at):
                codes.add("INVALID_PROVIDER_TIMESTAMP_ORDER")
            artifacts = manifest.get("artifacts", [])
            if manifest_version == "2.0.0":
                if manifest.get("create_precondition") != "IF_GENERATION_MATCH_0":
                    codes.add("RAW_OVERWRITE_PRECONDITION_MISSING")
                rights_snapshot = manifest.get("rights_snapshot", {})
                if rights_snapshot.get("tenant_id") != manifest.get("tenant_id"):
                    codes.add("RAW_MANIFEST_TENANT_MISMATCH")
                action_grants = rights_snapshot.get("action_grants", [])
                action_names = [grant.get("action") for grant in action_grants]
                if len(action_names) != len(set(action_names)):
                    codes.add("DUPLICATE_RIGHTS_ACTION_GRANT")
                rights_valid_from = parse_timestamp(rights_snapshot.get("valid_from"))
                rights_valid_until = parse_timestamp(rights_snapshot.get("valid_until"))
                packet_created_at = parse_timestamp(packet.get("created_at"))
                if assurance in OPTIMISTIC and (
                    rights_snapshot.get("status") in {"RIGHTS_UNCONFIRMED", "FORBIDDEN", "SYNTHETIC_TEST_ONLY"}
                    or rights_snapshot.get("revoked_at")
                    or (packet_created_at and rights_valid_from and packet_created_at < rights_valid_from)
                    or (packet_created_at and rights_valid_until and packet_created_at > rights_valid_until)
                ):
                    codes.add("RIGHTS_SNAPSHOT_NOT_ACTIVE")
                artifact_keys = [(artifact.get("artifact_id"), artifact.get("artifact_revision_id")) for artifact in artifacts]
                if len(artifact_keys) != len(set(artifact_keys)):
                    codes.add("DUPLICATE_ARTIFACT_ID")
                for artifact in artifacts:
                    if not artifact.get("storage_ref", {}).get("generation"):
                        codes.add("RAW_GENERATION_MISSING")
                    if artifact.get("tenant_id") != manifest.get("tenant_id") or artifact.get("zone") != manifest.get("zone"):
                        codes.add("RAW_MANIFEST_TENANT_MISMATCH")
                    if artifact.get("rights_snapshot_id") != rights_snapshot.get("rights_snapshot_id"):
                        codes.add("RAW_RIGHTS_SNAPSHOT_MISMATCH")
                    content_hash = artifact.get("integrity", {}).get("sha256")
                    if not content_hash:
                        codes.add("ARTIFACT_HASH_MISSING")
                    elif re.fullmatch(r"sha256:[a-f0-9]{64}", content_hash) is None:
                        codes.add("ARTIFACT_HASH_INVALID")
                    validation = artifact.get("validation", {})
                    if assurance in OPTIMISTIC and (
                        validation.get("quarantine_status") != "VALIDATED"
                        or validation.get("malware_scan", {}).get("status") != "PASS"
                        or validation.get("mime_check") != "MATCH"
                        or validation.get("hash_check") != "MATCH"
                    ):
                        codes.add("RAW_ARTIFACT_NOT_VALIDATED")
                    if assurance in OPTIMISTIC and artifact.get("lineage", {}).get("deletion_state") != "ACTIVE":
                        codes.add("RAW_ARTIFACT_DELETION_STATE_INVALID")
            else:
                artifact_ids = [artifact.get("artifact_id") for artifact in artifacts]
                if len(artifact_ids) != len(set(artifact_ids)):
                    codes.add("DUPLICATE_ARTIFACT_ID")
                for artifact in artifacts:
                    content_hash = artifact.get("content_hash")
                    if not content_hash:
                        codes.add("ARTIFACT_HASH_MISSING")
                    elif not isinstance(content_hash, str) or re.fullmatch(r"sha256:[a-f0-9]{64}", content_hash) is None:
                        codes.add("ARTIFACT_HASH_INVALID")
                provider_outputs = [artifact for artifact in artifacts if artifact.get("role") == "PROVIDER_OUTPUT"]
                if not provider_outputs:
                    codes.add("PROVIDER_OUTPUT_ARTIFACT_MISSING")
                elif any(
                    not isinstance(artifact.get("byte_size"), int)
                    or isinstance(artifact.get("byte_size"), bool)
                    or artifact.get("byte_size") <= 0
                    or re.fullmatch(r"sha256:[a-f0-9]{64}", artifact.get("content_hash", "")) is None
                    or not artifact.get("source_location")
                    for artifact in provider_outputs
                ):
                    codes.add("PROVIDER_OUTPUT_ARTIFACT_INVALID")
                rights = manifest.get("rights", {})
                claims = manifest.get("usage_claims", {})
                for use in ("research", "commercial", "automation", "redistribution"):
                    if claims.get(use) is True and rights.get(use) != "ALLOWED":
                        codes.add("UNCONFIRMED_RIGHTS_CLAIM")

            if assurance in OPTIMISTIC and variant == "TID_ONLY":
                if environment_class not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_ENVIRONMENT_WITH_SUPPORT")
                if dose_metadata.get("data_class") not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_DOSE_WITH_SUPPORT")
                manifest_class = manifest.get("metadata", {}).get("data_class")
                if manifest_class not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_MANIFEST_WITH_SUPPORT")

                if manifest_version != "2.0.0":
                    required_rights = {"research"}
                    if manifest.get("execution_mode") == "AUTOMATED":
                        required_rights.add("automation")
                    distribution_scope = manifest.get("distribution_scope")
                    if distribution_scope in {"EXTERNAL_RESEARCH", "COMMERCIAL_PRODUCT"}:
                        required_rights.add("redistribution")
                    if distribution_scope == "COMMERCIAL_PRODUCT":
                        required_rights.add("commercial")
                    if any(rights.get(required) != "ALLOWED" for required in required_rights):
                        codes.add("REQUIRED_RIGHT_NOT_ALLOWED")

    v2_manifests = {
        manifest.get("manifest_id"): manifest
        for environment in environments
        for manifest in [environment.get("raw_artifact_manifest")]
        if isinstance(manifest, dict) and manifest.get("contract_version") == "2.0.0"
    }
    for reference in packet.get("raw_manifest_refs", []):
        manifest = v2_manifests.get(reference.get("manifest_id"))
        if manifest is None:
            codes.add("RAW_MANIFEST_REFERENCE_MISSING")
            continue
        artifacts = [
            artifact for artifact in manifest.get("artifacts", [])
            if artifact.get("artifact_id") == reference.get("artifact_id")
            and artifact.get("artifact_revision_id") == reference.get("artifact_revision_id")
        ]
        if len(artifacts) != 1:
            codes.add("RAW_MANIFEST_REFERENCE_MISSING")
            continue
        artifact = artifacts[0]
        rights_snapshot = manifest.get("rights_snapshot", {})
        if reference.get("tenant_id") != manifest.get("tenant_id") or reference.get("tenant_id") != artifact.get("tenant_id"):
            codes.add("RAW_MANIFEST_TENANT_MISMATCH")
        if reference.get("zone") != manifest.get("zone") or reference.get("zone") != artifact.get("zone"):
            codes.add("RAW_MANIFEST_ZONE_MISMATCH")
        if reference.get("storage_generation") != artifact.get("storage_ref", {}).get("generation"):
            codes.add("RAW_GENERATION_MISMATCH")
        if reference.get("artifact_sha256") != artifact.get("integrity", {}).get("sha256"):
            codes.add("RAW_ARTIFACT_HASH_MISMATCH")
        if (
            reference.get("rights_snapshot_id") != rights_snapshot.get("rights_snapshot_id")
            or reference.get("rights_snapshot_id") != artifact.get("rights_snapshot_id")
        ):
            codes.add("RAW_RIGHTS_SNAPSHOT_MISMATCH")
        if reference.get("source_locator") != artifact.get("source", {}).get("locator"):
            codes.add("RAW_SOURCE_LOCATOR_MISMATCH")
        grants = {
            grant.get("action"): grant.get("grant_status")
            for grant in rights_snapshot.get("action_grants", [])
        }
        if any(grants.get(action) != "ALLOWED" for action in reference.get("required_actions", [])):
            codes.add("RIGHTS_ACTION_GRANT_MISSING")

    evidences = by_kind.get("PART_TEST_EVIDENCE", [])
    if environments and evidences and policies:
        tid = environments[0].get("tid", environments[0].get("mission_dose", {}))
        limit = evidences[0].get("tid_test_limit", {})
        rules = policies[0].get("rules", {})
        if not isinstance(rules, dict):
            rules = {}
        factor = policies[0].get("tid_design_factor", rules.get("tid_design_factor"))
        if tid.get("unit") == limit.get("unit") and isinstance(factor, (int, float)):
            if tid.get("value", 0) * factor > limit.get("value", float("-inf")):
                codes.add("TEST_RANGE_EXCEEDED")
    return codes


def build_registry(schemas: list[dict]) -> Registry:
    resources = [(schema["$id"], Resource.from_contents(schema)) for schema in schemas]
    return Registry().with_resources(resources)


def schema_errors(packet: dict, schema: dict, registry: Registry) -> list[str]:
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    return [f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in validator.iter_errors(packet)]


def apply_operations(base: dict, operations: list[dict]) -> dict:
    value = copy.deepcopy(base)
    for operation in operations:
        parts = [part.replace("~1", "/").replace("~0", "~") for part in operation["path"].split("/")[1:]]
        parent = value
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        key = parts[-1]
        if isinstance(parent, list) and key != "-":
            key = int(key)
        if operation["op"] == "set":
            parent[key] = operation["value"]
        elif operation["op"] == "delete":
            del parent[key]
        elif operation["op"] == "copy":
            source = value
            for source_part in operation["from"].split("/")[1:]:
                source_part = source_part.replace("~1", "/").replace("~0", "~")
                source = source[int(source_part)] if isinstance(source, list) else source[source_part]
            if isinstance(parent, list) and key == "-":
                parent.append(copy.deepcopy(source))
            else:
                parent[key] = copy.deepcopy(source)
        else:
            raise ValueError(f"Unsupported fixture operation: {operation['op']}")
    return value


def load_fixture(path: Path) -> dict:
    document = load(path)
    if "base" in document and "operations" in document:
        base = load_fixture((path.parent / document["base"]).resolve())
        return apply_operations(base, document["operations"])
    return document


def main() -> int:
    failures: list[str] = []
    schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
    loaded_schemas = []
    for path in schemas:
        try:
            schema = load(path)
            Draft202012Validator.check_schema(schema)
            loaded_schemas.append(schema)
        except Exception as exc:
            failures.append(f"schema {path.name}: {exc}")
    print(f"SCHEMAS: {len(schemas)} checked")

    common_schema = load(SCHEMA_DIR / "common.schema.json")
    enum_contracts = {
        "dataClass": DATA_CLASSES,
        "reviewStatus": REVIEW_STATUSES,
        "assuranceDecision": ASSURANCE_DECISIONS,
        "processingStatus": PROCESSING_STATUSES,
    }
    for definition, expected in enum_contracts.items():
        actual = set(common_schema["$defs"][definition]["enum"])
        if actual != expected:
            failures.append(f"enum {definition}: expected {sorted(expected)}, got {sorted(actual)}")
    print("ENUM CONTRACTS: 4 axes checked")

    packet_schema = load(PACKET_SCHEMA)
    cardinality_rules = packet_schema["properties"]["inputs"]["allOf"]
    exact_one_kinds = {
        rule["contains"]["properties"]["kind"]["const"]
        for rule in cardinality_rules
        if rule.get("minContains") == 1 and rule.get("maxContains") == 1
    }
    if exact_one_kinds != REQUIRED_INPUT_KINDS:
        failures.append(
            f"input cardinality: expected exact-one {sorted(REQUIRED_INPUT_KINDS)}, got {sorted(exact_one_kinds)}"
        )
    print("INPUT CARDINALITY: 7 required kinds exact-one")

    packet_versions = set(packet_schema["properties"]["schema_version"]["enum"])
    if packet_versions != {"1.0.0", "1.1.0"}:
        failures.append(f"packet versions: expected ['1.0.0', '1.1.0'], got {sorted(packet_versions)}")
    for schema_name in ("mitigation-v2.schema.json", "user-policy-v2.schema.json", "raw-artifact-manifest-v2.schema.json"):
        version = load(SCHEMA_DIR / schema_name)["properties"]["contract_version"].get("const")
        if version != "2.0.0":
            failures.append(f"{schema_name}: expected contract_version 2.0.0, got {version}")
    print("VERSION CONTRACTS: EvidencePacket 1.0.0/1.1.0 and v2 contracts checked")
    expected_tmr_boundaries = {0.0: 0.0, 0.1: 0.028, 1.0: 1.0}
    for p, expected in expected_tmr_boundaries.items():
        if not close_number(tmr_limited_failure_probability(p), expected):
            failures.append(f"TMR boundary p={p}: expected {expected}")
    mitigation_v2 = load(SCHEMA_DIR / "mitigation-v2.schema.json")
    policy_v2 = load(SCHEMA_DIR / "user-policy-v2.schema.json")
    if mitigation_v2["properties"].get("runtime_contract_version", {}).get("const") != "1.0.0":
        failures.append("mitigation runtime contract version 1.0.0 missing")
    if policy_v2["properties"].get("hash_contract_version", {}).get("const") != "1.0.0":
        failures.append("policy hash contract version 1.0.0 missing")
    print("RUNTIME CONTRACTS: mitigation 1.0.0, policy hash 1.0.0, TMR boundaries checked")
    registry = build_registry(loaded_schemas)
    valid_files = sorted(VALID_DIR.glob("*.json"))
    for path in valid_files:
        packet = load_fixture(path)
        errors = schema_errors(packet, packet_schema, registry)
        codes = semantic_codes(packet)
        if errors or codes:
            failures.append(f"valid {path.name}: schema={errors} semantic={sorted(codes)}")
    print(f"VALID FIXTURES: {len(valid_files)} passed")

    invalid_count = 0
    for case_path in sorted(INVALID_DIR.glob("*.json")):
        case_doc = load(case_path)
        base = load_fixture((case_path.parent / case_doc["base"]).resolve())
        for case in case_doc["cases"]:
            invalid_count += 1
            packet = apply_operations(base, case["operations"])
            errors = schema_errors(packet, packet_schema, registry)
            codes = semantic_codes(packet)
            if case.get("require_schema_error") and not errors:
                failures.append(f"invalid {case['name']}: expected schema error, got none")
            if not errors and not codes:
                failures.append(f"invalid {case['name']}: unexpectedly passed")
            if case["expected"] not in codes:
                failures.append(f"invalid {case['name']}: expected {case['expected']}, got schema={errors} semantic={sorted(codes)}")
    print(f"INVALID FIXTURES: {invalid_count} rejected with expected codes")

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("RESULT: READY_FOR_REVIEW candidate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
