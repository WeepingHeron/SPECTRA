"""Synthetic vertical-slice orchestration and EvidencePacket construction."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass

from .contracts import packet_contract_errors
from .policy import evaluate_policy
from .see import calculate_see
from .tid import OutOfModelScope, calculate_tid
from .units import UnitError, tid_krad_si


@dataclass(frozen=True)
class SimulationOptions:
    shielding_mm: float | None = None
    duration_value: float | None = None
    duration_unit: str | None = None
    ecc_enabled: bool = True
    maximum_residual_seu: float | None = None
    tid_design_factor: float | None = None
    analysis_device_count: int = 2


def canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(value) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def by_kind(packet: dict, kind: str) -> dict:
    matches = [item for item in packet["inputs"] if item.get("kind") == kind]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {kind} input")
    return matches[0]


def indexed_by_kind(packet: dict, kind: str) -> tuple[int, dict]:
    matches = [(index, item) for index, item in enumerate(packet["inputs"]) if item.get("kind") == kind]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {kind} input")
    return matches[0]


def model_errors(model: dict) -> list[str]:
    if not isinstance(model, dict):
        return ["synthetic model configuration must be an object"]
    errors = []
    if model.get("model_name") != "SPECTRA_SYNTHETIC_BASELINE_NOT_PHYSICAL":
        errors.append("unexpected synthetic model name")
    if model.get("data_class") != "SYNTHETIC":
        errors.append("synthetic model data_class must be SYNTHETIC")
    if not isinstance(model.get("model_version"), str) or not model.get("model_version"):
        errors.append("synthetic model version is required")
    numeric_fields = ("reference_duration_years", "see_exposure_scale")
    for field in numeric_fields:
        value = model.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            errors.append(f"{field} must be finite and greater than zero")
    factors = model.get("shielding_factors_by_mm")
    if not isinstance(factors, dict) or set(factors) != {"1", "2", "3", "4"}:
        errors.append("shielding lookup must contain exactly 1, 2, 3, and 4 mm")
    elif any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 < value <= 1
        for value in factors.values()
    ):
        errors.append("shielding factors must be finite, greater than zero, and at most one")
    elif [factors[key] for key in ("1", "2", "3", "4")] != sorted(factors.values(), reverse=True):
        errors.append("shielding factors must decrease monotonically with thickness")
    limitations = model.get("limitations")
    if not isinstance(limitations, list) or not limitations or any(
        not isinstance(item, str) or not item.strip() for item in limitations
    ):
        errors.append("synthetic model limitations must be a non-empty string list")
    return errors


def options_errors(options: SimulationOptions) -> list[str]:
    if not isinstance(options, SimulationOptions):
        return ["options must be a SimulationOptions instance"]
    if not isinstance(options.ecc_enabled, bool):
        return ["ecc_enabled must be boolean"]
    if (
        isinstance(options.analysis_device_count, bool)
        or not isinstance(options.analysis_device_count, int)
        or options.analysis_device_count < 1
    ):
        return ["analysis_device_count must be a positive integer"]
    errors = []
    for field in ("shielding_mm", "duration_value", "maximum_residual_seu", "tid_design_factor"):
        value = getattr(options, field)
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            errors.append(f"{field} must be a finite number")
    if options.duration_unit is not None and not isinstance(options.duration_unit, str):
        errors.append("duration_unit must be a string")
    return errors


def _refresh_metadata(record: dict, base_input_hash: str, created_at: str) -> None:
    payload = {key: value for key, value in record.items() if key != "metadata"}
    payload_hash = sha256(payload)
    record["metadata"] = {
        "data_class": "SYNTHETIC",
        "version": "scenario-override-v1",
        "created_at": created_at,
        "content_hash": payload_hash,
        "review_status": "READY_FOR_REVIEW",
        "calculation_run": {
            "run_id": "synthetic-scenario-override",
            "engine": "spectra-synthetic-scenario-builder",
            "engine_version": "1.0.0",
            "input_hash": base_input_hash,
            "output_hash": payload_hash,
            "executed_at": created_at,
        },
    }


def _apply_options(packet: dict, options: SimulationOptions) -> dict:
    scenario = copy.deepcopy(packet)
    base_input_hash = sha256(packet)
    created_at = scenario["created_at"]
    mission = by_kind(scenario, "MISSION")
    shielding = by_kind(scenario, "SHIELDING")
    policy = by_kind(scenario, "USER_POLICY")

    if options.shielding_mm is not None:
        shielding["equivalent_thickness"]["value"] = options.shielding_mm
        _refresh_metadata(shielding["equivalent_thickness"], base_input_hash, created_at)
        _refresh_metadata(shielding, base_input_hash, created_at)
    if options.duration_value is not None:
        mission["duration"]["value"] = options.duration_value
        if options.duration_unit is not None:
            mission["duration"]["unit"] = options.duration_unit
        _refresh_metadata(mission["duration"], base_input_hash, created_at)
        _refresh_metadata(mission, base_input_hash, created_at)
    elif options.duration_unit is not None:
        mission["duration"]["unit"] = options.duration_unit
        _refresh_metadata(mission["duration"], base_input_hash, created_at)
        _refresh_metadata(mission, base_input_hash, created_at)
    if options.maximum_residual_seu is not None:
        policy["maximum_residual_seu"]["value"] = options.maximum_residual_seu
        _refresh_metadata(policy["maximum_residual_seu"], base_input_hash, created_at)
        _refresh_metadata(policy, base_input_hash, created_at)
    if options.tid_design_factor is not None:
        policy["tid_design_factor"] = options.tid_design_factor
        _refresh_metadata(policy, base_input_hash, created_at)
    return scenario


def _metadata(run_id: str, input_hash: str, output_hash: str, created_at: str, model: dict) -> dict:
    return {
        "data_class": "SYNTHETIC",
        "version": model["model_version"],
        "created_at": created_at,
        "content_hash": output_hash,
        "review_status": "READY_FOR_REVIEW",
        "calculation_run": {
            "run_id": run_id,
            "engine": model["model_name"],
            "engine_version": model["model_version"],
            "input_hash": input_hash,
            "output_hash": output_hash,
            "executed_at": created_at,
        },
    }


def _quantity(value: float, kind: str, unit: str, metadata: dict) -> dict:
    return {
        "value": value,
        "quantity_kind": kind,
        "unit": unit,
        "metadata": copy.deepcopy(metadata),
    }


def _safe_result(packet: dict, model: dict, input_hash: str, run_id: str, status: str, message: str) -> dict:
    safe_packet = None
    if (
        status != "INVALID_INPUT"
        and isinstance(packet, dict)
        and isinstance(packet.get("trace"), list)
        and packet["trace"]
    ):
        safe_packet = copy.deepcopy(packet)
        safe_packet["packet_id"] = f"packet-{run_id}"
        safe_packet["trace"] = copy.deepcopy(packet["trace"])
        safe_packet["decision"] = {
            "processing_status": status,
            "assurance_decision": "HOLD",
            "rule_results": [
                {"rule_id": "SIMULATION_SCOPE_V1", "outcome": "NOT_EVALUATED", "trace_ids": [safe_packet["trace"][0]["trace_id"]]}
            ],
            "evidence_gaps": [{"gap_code": status, "description": message, "blocking": True}],
        }
        safe_packet["trace"][0]["decision_rule_ids"] = ["SIMULATION_SCOPE_V1"]
    return {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "data_class": "SYNTHETIC",
        "model": {
            "name": "SPECTRA_SYNTHETIC_BASELINE_NOT_PHYSICAL",
            "version": (
                model["model_version"]
                if isinstance(model, dict) and isinstance(model.get("model_version"), str) and model["model_version"]
                else "invalid-config"
            ),
        },
        "input_hash": input_hash,
        "processing_status": status,
        "assurance_decision": "HOLD",
        "engineering_gate": "NOT_EVALUATED",
        "metrics": {"shielded_tid": None, "required_tid": None, "raw_seu": None, "residual_seu": None},
        "rule_results": [{"rule_id": "SIMULATION_SCOPE_V1", "outcome": "NOT_EVALUATED"}],
        "evidence_gaps": [{"gap_code": status, "description": message, "blocking": True}],
        "evidence_packet": safe_packet,
    }


def run_simulation(packet: dict, model: dict, options: SimulationOptions = SimulationOptions()) -> dict:
    invalid_options = options_errors(options)
    options_payload = options.__dict__ if isinstance(options, SimulationOptions) else {
        "invalid_type": type(options).__name__
    }
    try:
        original_input_hash = sha256({"packet": packet, "options": options_payload, "model": model})
    except (TypeError, ValueError) as exc:
        original_input_hash = sha256({
            "serialization_error": type(exc).__name__,
            "packet_type": type(packet).__name__,
            "model_type": type(model).__name__,
        })
        original_run_id = "sim-" + original_input_hash.removeprefix("sha256:")[:16]
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "INVALID_INPUT",
            "simulation inputs must be JSON-serializable",
        )
    original_run_id = "sim-" + original_input_hash.removeprefix("sha256:")[:16]
    invalid_model = model_errors(model)
    if invalid_model:
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "MODEL_FAILURE", invalid_model[0]
        )
    if invalid_options:
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "INVALID_INPUT", invalid_options[0]
        )
    original_errors = packet_contract_errors(packet)
    if original_errors:
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "INVALID_INPUT", original_errors[0]
        )
    required_kinds = {
        "MISSION", "BOM", "RADIATION_ENVIRONMENT", "PART_TEST_EVIDENCE",
        "SHIELDING", "MITIGATION", "USER_POLICY",
    }
    if any(sum(item.get("kind") == kind for item in packet["inputs"]) != 1 for kind in required_kinds):
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "INVALID_INPUT",
            "Stage 2 baseline requires exactly one input of each required kind",
        )
    try:
        scenario = _apply_options(packet, options)
    except (KeyError, TypeError, ValueError, UnitError) as exc:
        return _safe_result(
            packet, model, original_input_hash, original_run_id, "INVALID_INPUT", str(exc)
        )
    input_hash = sha256({"packet": scenario, "options": options.__dict__, "model": model})
    run_id = "sim-" + input_hash.removeprefix("sha256:")[:16]
    validation_errors = packet_contract_errors(scenario)
    if validation_errors:
        return _safe_result(
            scenario, model, input_hash, run_id, "INVALID_INPUT", validation_errors[0]
        )
    try:
        mission_index, mission = indexed_by_kind(scenario, "MISSION")
        environment_index, environment = indexed_by_kind(scenario, "RADIATION_ENVIRONMENT")
        bom_index, bom = indexed_by_kind(scenario, "BOM")
        evidence_index, evidence = indexed_by_kind(scenario, "PART_TEST_EVIDENCE")
        shielding_index, shielding = indexed_by_kind(scenario, "SHIELDING")
        mitigation_index, mitigation = indexed_by_kind(scenario, "MITIGATION")
        policy_index, policy = indexed_by_kind(scenario, "USER_POLICY")
        component = bom["components"][0]
        if evidence["component_id"] != component["component_id"]:
            raise ValueError("part evidence does not reference the simulated component")
        if shielding["applies_to"] != [component["component_id"]]:
            raise ValueError("Stage 2 baseline requires shielding for exactly the simulated component")
        if mitigation["component_id"] != component["component_id"]:
            raise ValueError("mitigation does not reference the simulated component")
        if mitigation["method"] != "ECC" or "SEU" not in mitigation["failure_modes"]:
            raise OutOfModelScope("Stage 2 baseline supports an SEU-targeted ECC mitigation only")
        maximum_residual_seu = float(policy["maximum_residual_seu"]["value"])
        if not math.isfinite(maximum_residual_seu) or maximum_residual_seu < 0:
            raise ValueError("maximum residual SEU must be finite and non-negative")
        tid = calculate_tid(
            environment["tid"], mission["duration"], shielding["equivalent_thickness"],
            policy["tid_design_factor"], model,
        )
        mitigation_factor = float(mitigation.get("effectiveness_factor", 1.0)) if options.ecc_enabled else 1.0
        see = calculate_see(
            environment["particle_flux"], evidence["cross_section"],
            options.analysis_device_count, mission["duration"], mitigation_factor,
            model["see_exposure_scale"],
        )
        tested_limit = tid_krad_si(evidence["tid_test_limit"]["value"], evidence["tid_test_limit"]["unit"])
    except OutOfModelScope as exc:
        return _safe_result(scenario, model, input_hash, run_id, "OUT_OF_MODEL_SCOPE", str(exc))
    except (KeyError, TypeError, ValueError, UnitError) as exc:
        return _safe_result(scenario, model, input_hash, run_id, "INVALID_INPUT", str(exc))

    rules = evaluate_policy(
        tid["required_tid_krad_si"], tested_limit, see["residual_events_per_mission"],
        maximum_residual_seu, evidence["evidence_types"],
        policy["require_destructive_see_evidence"], policy["approval_status"] == "APPROVED",
    )
    engineering_gate = "PASS" if all(rule["outcome"] == "PASS" for rule in rules) else "FAIL"
    metric_values = {
        "shielded_tid": tid["shielded_tid_krad_si"],
        "required_tid": tid["required_tid_krad_si"],
        "raw_seu": see["raw_events_per_mission"],
        "residual_seu": see["residual_events_per_mission"],
    }
    output_hash = sha256(metric_values)
    metadata = _metadata(run_id, input_hash, output_hash, scenario["created_at"], model)
    metrics = {
        "shielded_tid": _quantity(metric_values["shielded_tid"], "TID", "krad(Si)", metadata),
        "required_tid": _quantity(metric_values["required_tid"], "TID", "krad(Si)", metadata),
        "raw_seu": _quantity(metric_values["raw_seu"], "RATE", "events/mission", metadata),
        "residual_seu": _quantity(metric_values["residual_seu"], "RATE", "events/mission", metadata),
    }
    trace_specs = [
        ("trace-tid-required", f"/inputs/{environment_index}/tid", f"/inputs/{environment_index}/tid/metadata/calculation_run", metrics["required_tid"], ["TID_MARGIN_V1"]),
        ("trace-tid-limit", f"/inputs/{evidence_index}/tid_test_limit", f"/inputs/{evidence_index}/tid_test_limit/metadata/calculation_run", _quantity(tested_limit, "TID", "krad(Si)", metadata), ["TID_MARGIN_V1"]),
        ("trace-shielding", f"/inputs/{shielding_index}/equivalent_thickness", f"/inputs/{shielding_index}/equivalent_thickness/metadata/calculation_run", _quantity(shielding["equivalent_thickness"]["value"], "SHIELDING", "mm_Al_equivalent", metadata), ["TID_MARGIN_V1"]),
        ("trace-duration", f"/inputs/{mission_index}/duration", f"/inputs/{mission_index}/duration/metadata/calculation_run", _quantity(tid["duration_years"], "DURATION", "year", metadata), ["TID_MARGIN_V1", "SEU_POLICY_V1"]),
        ("trace-seu-residual", f"/inputs/{evidence_index}/cross_section", f"/inputs/{evidence_index}/cross_section/metadata/calculation_run", metrics["residual_seu"], ["SEU_POLICY_V1"]),
        ("trace-seu-limit", f"/inputs/{policy_index}/maximum_residual_seu", f"/inputs/{policy_index}/maximum_residual_seu/metadata/calculation_run", _quantity(policy["maximum_residual_seu"]["value"], "RATE", "events/mission", metadata), ["SEU_POLICY_V1"]),
        ("trace-destructive-see", f"/inputs/{evidence_index}", f"/inputs/{evidence_index}/metadata/calculation_run", _quantity(1 if {"SEL", "SEB", "SEGR"}.intersection(evidence["evidence_types"]) else 0, "COUNT", "count", metadata), ["DESTRUCTIVE_SEE_V1"]),
        ("trace-policy-approval", f"/inputs/{policy_index}", f"/inputs/{policy_index}/metadata/calculation_run", _quantity(1 if policy["approval_status"] == "APPROVED" else 0, "COUNT", "count", metadata), ["POLICY_APPROVAL_V1"]),
    ]
    traces = [
        {
            "trace_id": trace_id,
            "input_pointer": input_pointer,
            "origin_pointer": origin_pointer,
            "normalized_value": value,
            "applicability": {"status": "APPLICABLE", "conditions": ["synthetic Stage 2 baseline only"]},
            "decision_rule_ids": rule_ids,
            "used_for_decision": True,
        }
        for trace_id, input_pointer, origin_pointer, value, rule_ids in trace_specs
    ]
    trace_ids_by_rule = {
        rule["rule_id"]: [trace["trace_id"] for trace in traces if rule["rule_id"] in trace["decision_rule_ids"]]
        for rule in rules
    }
    packet_result = copy.deepcopy(scenario)
    packet_result["packet_id"] = f"packet-{run_id}"
    packet_result["trace"] = traces
    packet_result["decision"] = {
        "processing_status": "VALID",
        "assurance_decision": "HOLD",
        "rule_results": [
            {**rule, "trace_ids": trace_ids_by_rule[rule["rule_id"]]} for rule in rules
        ],
        "evidence_gaps": [{
            "gap_code": "SYNTHETIC_ONLY",
            "description": "Synthetic calculations are not radiation assurance evidence.",
            "blocking": True,
        }],
    }
    packet_result["review_status"] = "READY_FOR_REVIEW"
    output_contract_errors = packet_contract_errors(packet_result)
    if output_contract_errors:
        return _safe_result(
            scenario, model, input_hash, run_id, "MODEL_FAILURE", output_contract_errors[0]
        )
    return {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "data_class": "SYNTHETIC",
        "model": {"name": model["model_name"], "version": model["model_version"]},
        "input_hash": input_hash,
        "processing_status": "VALID",
        "assurance_decision": "HOLD",
        "engineering_gate": engineering_gate,
        "metrics": metrics,
        "rule_results": rules,
        "evidence_gaps": packet_result["decision"]["evidence_gaps"],
        "evidence_packet": packet_result,
    }
