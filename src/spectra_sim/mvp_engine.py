"""Deterministic MVP baseline/variant decision path for v2 ECC and policy inputs."""

from __future__ import annotations

import copy
import json
import math
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .contracts import load_contract_fixture, packet_contract_errors
from .engine import by_kind, canonical_bytes, model_errors, sha256
from .see import calculate_see
from .tid import calculate_tid
from .units import tid_krad_si

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
SIMULATION_SCHEMA_DIR = ROOT / "simulation" / "schemas"
VALID_FIXTURE_DIR = (ROOT / "tests" / "schema" / "fixtures" / "valid").resolve()
ENGINE_NAME = "SPECTRA_MVP_DECISION_ENGINE_SYNTHETIC"
ENGINE_VERSION = "1.0.0"
DESTRUCTIVE_MODES = {"SEL", "SEB", "SEGR"}


class MvpDecisionError(ValueError):
    """Fail-closed error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=3)
def _validator(schema_name: str) -> Draft202012Validator:
    root_schemas = [_load(path) for path in sorted(SCHEMA_DIR.glob("*.schema.json"))]
    simulation_schemas = [
        _load(path) for path in sorted(SIMULATION_SCHEMA_DIR.glob("*.schema.json"))
    ]
    registry = Registry().with_resources([
        (schema["$id"], Resource.from_contents(schema))
        for schema in root_schemas + simulation_schemas
    ])
    schema = _load(SIMULATION_SCHEMA_DIR / schema_name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def _schema_errors(value: dict, schema_name: str) -> list[str]:
    return [
        f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in _validator(schema_name).iter_errors(value)
    ]


def _first_non_finite_path(value, path: str = "") -> str | None:
    """Return the first deterministic JSON pointer containing NaN or infinity."""
    if isinstance(value, float) and not math.isfinite(value):
        return path or "/<root>"
    if isinstance(value, dict):
        for key in sorted(value):
            found = _first_non_finite_path(value[key], f"{path}/{key}")
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _first_non_finite_path(item, f"{path}/{index}")
            if found is not None:
                return found
    return None


def validate_mvp_input(case: dict) -> None:
    non_finite_path = _first_non_finite_path(case)
    if non_finite_path is not None:
        raise MvpDecisionError(
            "NON_FINITE_NUMERIC_INPUT",
            f"numeric input at {non_finite_path} must be finite",
        )
    errors = _schema_errors(case, "mvp-decision-input.schema.json")
    if errors:
        raise MvpDecisionError("MVP_INPUT_SCHEMA_INVALID", errors[0])
    distribution = case["ecc_fault_distribution"]
    if distribution["metadata"]["data_class"] != "SYNTHETIC":
        raise MvpDecisionError(
            "NON_EVIDENTIARY_MITIGATION_OPERAND",
            "MVP regression distribution must remain explicitly SYNTHETIC",
        )
    for pattern in distribution["patterns"]:
        total = sum(pattern["transition"].values())
        if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-12):
            raise MvpDecisionError(
                "ECC_TRANSITION_INVALID",
                f"transition fractions for multiplicity {pattern['multiplicity_bits']} must sum to one",
            )
    for scenario_name in ("baseline", "variant"):
        scenario = case[scenario_name]
        mitigation = scenario["mitigation"]
        if mitigation["method"] != "ECC" or mitigation["target_failure_modes"] != ["SEU"]:
            raise MvpDecisionError(
                "MITIGATION_METHOD_MODE_MISMATCH", "MVP v1 supports SEU-targeted ECC only"
            )
        if not DESTRUCTIVE_MODES.issubset(set(mitigation["excluded_failure_modes"])):
            raise MvpDecisionError(
                "EVIDENCE_TYPE_SUBSTITUTION",
                "ECC must explicitly exclude SEL, SEB, and SEGR",
            )
        if mitigation["design_parameters"]["fault_multiplicity_ref"] != distribution["distribution_id"]:
            raise MvpDecisionError(
                "ECC_FAULT_DISTRIBUTION_MISSING", "fault multiplicity reference is unresolved"
            )
        model = mitigation.get("effect_model", {})
        if model.get("equation_id") != "ECC_TRANSITION_MATRIX_V1":
            raise MvpDecisionError(
                "ARBITRARY_MITIGATION_FACTOR", "ECC transition equation is not explicitly bound"
            )
        applicability = mitigation["applicability"]["status"]
        expected = "APPLICABLE" if scenario["ecc_enabled"] else "NOT_APPLICABLE"
        if applicability != expected:
            raise MvpDecisionError(
                "MITIGATION_APPLICABILITY_MISMATCH",
                f"{scenario_name} ECC applicability must be {expected}",
            )


def _base_packet(case: dict) -> dict:
    fixture_path = (ROOT / case["base_packet_fixture"]).resolve()
    try:
        fixture_path.relative_to(VALID_FIXTURE_DIR)
    except ValueError as exc:
        raise MvpDecisionError(
            "MVP_BASE_PACKET_OUT_OF_SCOPE", "base packet must be a verified valid fixture"
        ) from exc
    packet = load_contract_fixture(fixture_path)
    errors = packet_contract_errors(packet)
    if errors:
        raise MvpDecisionError("BASE_PACKET_CONTRACT_INVALID", errors[0])
    return packet


def _scenario_packet(base: dict, case: dict, scenario_name: str) -> dict:
    packet = copy.deepcopy(base)
    scenario = case[scenario_name]
    packet["created_at"] = case["created_at"]
    packet["packet_id"] = f"mvp-{case['case_id']}-{scenario_name}-input"
    environment = by_kind(packet, "RADIATION_ENVIRONMENT")
    environment["environment_variant"] = "FLUX_AND_TID"
    environment["tid"] = copy.deepcopy(environment["mission_dose"])
    environment["particle_flux"] = copy.deepcopy(case["particle_flux"])
    mitigation_index = next(
        index for index, item in enumerate(packet["inputs"]) if item["kind"] == "MITIGATION"
    )
    policy_index = next(
        index for index, item in enumerate(packet["inputs"]) if item["kind"] == "USER_POLICY"
    )
    packet["inputs"][mitigation_index] = copy.deepcopy(scenario["mitigation"])
    packet["inputs"][policy_index] = copy.deepcopy(scenario["policy"])
    errors = packet_contract_errors(packet)
    if errors:
        raise MvpDecisionError("SCENARIO_PACKET_CONTRACT_INVALID", errors[0])
    return packet


def _metadata(run_id: str, input_hash: str, output_hash: str, created_at: str) -> dict:
    return {
        "data_class": "SYNTHETIC",
        "version": ENGINE_VERSION,
        "created_at": created_at,
        "content_hash": output_hash,
        "review_status": "READY_FOR_REVIEW",
        "calculation_run": {
            "run_id": run_id,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "executed_at": created_at,
        },
    }


def _quantity(value: float, quantity_kind: str, unit: str, metadata: dict) -> dict:
    return {
        "value": value,
        "quantity_kind": quantity_kind,
        "unit": unit,
        "metadata": copy.deepcopy(metadata),
    }


def _ecc_outcomes(case: dict, enabled: bool, raw_events: float) -> dict[str, float]:
    if not enabled:
        return {
            "corrected": 0.0,
            "detected_uncorrectable": 0.0,
            "silent_uncorrected": 0.0,
            "residual_logical_errors": raw_events,
        }
    patterns = case["ecc_fault_distribution"]["patterns"]
    incident_total = sum(pattern["incident_events"] for pattern in patterns)
    if not math.isclose(incident_total, raw_events, rel_tol=0, abs_tol=1e-12):
        raise MvpDecisionError(
            "ECC_FAULT_DISTRIBUTION_MISMATCH",
            f"pattern total {incident_total} does not match raw SEU {raw_events}",
        )
    outcomes = {"corrected": 0.0, "detected_uncorrectable": 0.0, "silent_uncorrected": 0.0}
    for pattern in patterns:
        for outcome, fraction in pattern["transition"].items():
            outcomes[outcome] += pattern["incident_events"] * fraction
    outcomes["residual_logical_errors"] = (
        outcomes["detected_uncorrectable"] + outcomes["silent_uncorrected"]
    )
    return outcomes


def _gaps() -> list[dict]:
    return [
        {
            "gap_code": "STAGE3_INPUT_UNAVAILABLE",
            "description": "No decision-eligible real Stage 3 environment input is present.",
            "blocking": True,
        },
        {
            "gap_code": "STAGE4_INPUT_UNAVAILABLE",
            "description": "No decision-eligible exact-part Stage 4 evidence is present.",
            "blocking": True,
        },
        {
            "gap_code": "SYNTHETIC_ONLY",
            "description": "All MVP regression operands are synthetic and cannot support assurance.",
            "blocking": True,
        },
        {
            "gap_code": "INDEPENDENT_ASSURANCE_PENDING",
            "description": "Independent assurance has not authorized an optimistic decision.",
            "blocking": True,
        },
    ]


def _scenario_result(packet: dict, case: dict, model: dict, scenario_name: str) -> dict:
    scenario = case[scenario_name]
    mission = by_kind(packet, "MISSION")
    environment = by_kind(packet, "RADIATION_ENVIRONMENT")
    bom = by_kind(packet, "BOM")
    evidence = by_kind(packet, "PART_TEST_EVIDENCE")
    shielding = by_kind(packet, "SHIELDING")
    mitigation = by_kind(packet, "MITIGATION")
    policy = by_kind(packet, "USER_POLICY")
    component = bom["components"][0]
    try:
        tid = calculate_tid(
            environment["tid"], mission["duration"], shielding["equivalent_thickness"],
            policy["rules"]["tid_design_factor"], model,
        )
    except ValueError as exc:
        raise MvpDecisionError(
            "TID_CALCULATION_INPUT_INVALID",
            f"{scenario_name} TID calculation rejected its inputs: {exc}",
        ) from exc
    try:
        see = calculate_see(
            environment["particle_flux"], evidence["cross_section"], component["quantity"],
            mission["duration"], 1.0, model["see_exposure_scale"],
        )
    except ValueError as exc:
        raise MvpDecisionError(
            "SEE_CALCULATION_INPUT_INVALID",
            f"{scenario_name} SEE calculation rejected its inputs: {exc}",
        ) from exc
    outcomes = _ecc_outcomes(case, scenario["ecc_enabled"], see["raw_events_per_mission"])
    try:
        tested_limit = tid_krad_si(
            evidence["tid_test_limit"]["value"], evidence["tid_test_limit"]["unit"]
        )
    except ValueError as exc:
        raise MvpDecisionError(
            "TID_CALCULATION_INPUT_INVALID",
            f"{scenario_name} TID test limit conversion rejected its inputs: {exc}",
        ) from exc
    required_modes = set(policy["rules"]["required_destructive_modes"])
    available_modes = set(evidence["evidence_types"])
    if not required_modes.issubset(available_modes):
        raise MvpDecisionError(
            "DESTRUCTIVE_SEE_MODE_MISSING",
            f"missing required destructive modes: {sorted(required_modes - available_modes)}",
        )
    rules = [
        {"rule_id": "TID_MARGIN_V2", "outcome": "PASS" if tested_limit >= tid["required_tid_krad_si"] else "FAIL"},
        {"rule_id": "ECC_TRANSITION_V2", "outcome": "PASS" if scenario["ecc_enabled"] else "NOT_EVALUATED"},
        {"rule_id": "RESIDUAL_SEU_THRESHOLD_V2", "outcome": "PASS" if outcomes["residual_logical_errors"] <= policy["rules"]["maximum_residual_seu"]["value"] else "FAIL"},
        {"rule_id": "POLICY_APPROVAL_STATE_V2", "outcome": "PASS" if policy["approval"]["status"] == "APPROVED" else "FAIL"},
        {"rule_id": "DESTRUCTIVE_MODE_COVERAGE_V2", "outcome": "PASS"},
        {"rule_id": "EVIDENCE_ELIGIBILITY_V2", "outcome": "NOT_EVALUATED"},
    ]
    numeric = {
        "shielded_tid": tid["shielded_tid_krad_si"],
        "required_tid": tid["required_tid_krad_si"],
        "raw_seu": see["raw_events_per_mission"],
        **outcomes,
    }
    scenario_input_hash = sha256({"packet": packet, "distribution": case["ecc_fault_distribution"]})
    scenario_output_hash = sha256({"numeric": numeric, "rules": rules})
    result_id = "result-" + scenario_output_hash.removeprefix("sha256:")[:16]
    metadata = _metadata(result_id, scenario_input_hash, scenario_output_hash, case["created_at"])
    metrics = {
        "shielded_tid": _quantity(numeric["shielded_tid"], "TID", "krad(Si)", metadata),
        "required_tid": _quantity(numeric["required_tid"], "TID", "krad(Si)", metadata),
        "raw_seu": _quantity(numeric["raw_seu"], "RATE", "events/mission", metadata),
        "residual_logical_errors": _quantity(numeric["residual_logical_errors"], "RATE", "events/mission", metadata),
        "corrected": _quantity(numeric["corrected"], "RATE", "events/mission", metadata),
        "detected_uncorrectable": _quantity(numeric["detected_uncorrectable"], "RATE", "events/mission", metadata),
        "silent_uncorrected": _quantity(numeric["silent_uncorrected"], "RATE", "events/mission", metadata),
    }
    indices = {item["kind"]: index for index, item in enumerate(packet["inputs"])}
    trace_specs = [
        ("trace-tid", f"/inputs/{indices['RADIATION_ENVIRONMENT']}/tid", f"/inputs/{indices['RADIATION_ENVIRONMENT']}/tid/metadata/calculation_run", metrics["required_tid"], ["TID_MARGIN_V2"]),
        ("trace-tid-limit", f"/inputs/{indices['PART_TEST_EVIDENCE']}/tid_test_limit", f"/inputs/{indices['PART_TEST_EVIDENCE']}/tid_test_limit/metadata/calculation_run", _quantity(tested_limit, "TID", "krad(Si)", metadata), ["TID_MARGIN_V2"]),
        ("trace-raw-seu", f"/inputs/{indices['RADIATION_ENVIRONMENT']}/particle_flux", f"/inputs/{indices['RADIATION_ENVIRONMENT']}/particle_flux/metadata/calculation_run", metrics["raw_seu"], ["ECC_TRANSITION_V2"]),
        ("trace-ecc", f"/inputs/{indices['MITIGATION']}/design_parameters", f"/inputs/{indices['MITIGATION']}/metadata/calculation_run", metrics["residual_logical_errors"], ["ECC_TRANSITION_V2", "RESIDUAL_SEU_THRESHOLD_V2"]),
        ("trace-policy-limit", f"/inputs/{indices['USER_POLICY']}/rules/maximum_residual_seu", f"/inputs/{indices['USER_POLICY']}/rules/maximum_residual_seu/metadata/calculation_run", _quantity(policy["rules"]["maximum_residual_seu"]["value"], "RATE", "events/mission", metadata), ["RESIDUAL_SEU_THRESHOLD_V2"]),
        ("trace-policy-approval", f"/inputs/{indices['USER_POLICY']}", f"/inputs/{indices['USER_POLICY']}/metadata/calculation_run", _quantity(1 if policy["approval"]["status"] == "APPROVED" else 0, "COUNT", "count", metadata), ["POLICY_APPROVAL_STATE_V2", "EVIDENCE_ELIGIBILITY_V2"]),
        ("trace-destructive", f"/inputs/{indices['PART_TEST_EVIDENCE']}", f"/inputs/{indices['PART_TEST_EVIDENCE']}/metadata/calculation_run", _quantity(len(required_modes), "COUNT", "count", metadata), ["DESTRUCTIVE_MODE_COVERAGE_V2", "EVIDENCE_ELIGIBILITY_V2"]),
    ]
    traces = [
        {
            "trace_id": f"{trace_id}-{scenario_name}",
            "input_pointer": input_pointer,
            "origin_pointer": origin_pointer,
            "normalized_value": copy.deepcopy(value),
            "applicability": {"status": "APPLICABLE", "conditions": ["Synthetic MVP comparison only"]},
            "decision_rule_ids": rule_ids,
            "used_for_decision": True,
        }
        for trace_id, input_pointer, origin_pointer, value, rule_ids in trace_specs
    ]
    trace_ids_by_rule = {
        rule["rule_id"]: [
            trace["trace_id"] for trace in traces
            if rule["rule_id"] in trace["decision_rule_ids"]
        ]
        for rule in rules
    }
    result_packet = copy.deepcopy(packet)
    result_packet["packet_id"] = f"packet-{result_id}"
    result_packet["trace"] = traces
    result_packet["decision"] = {
        "processing_status": "VALID",
        "assurance_decision": "HOLD",
        "rule_results": [
            {**rule, "trace_ids": trace_ids_by_rule[rule["rule_id"]]} for rule in rules
        ],
        "evidence_gaps": _gaps(),
    }
    result_packet["review_status"] = "READY_FOR_REVIEW"
    errors = packet_contract_errors(result_packet)
    if errors:
        raise MvpDecisionError("OUTPUT_EVIDENCE_PACKET_INVALID", errors[0])
    return {
        "scenario_id": scenario["scenario_id"],
        "result_id": result_id,
        "ecc_enabled": scenario["ecc_enabled"],
        "policy_approval_status": policy["approval"]["status"],
        "calculation_status": "CALCULATED_SYNTHETIC",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "metrics": metrics,
        "rule_results": rules,
        "evidence_gaps": _gaps(),
        "evidence_packet": result_packet,
    }


def _rule_outcome(result: dict, rule_id: str) -> str:
    return next(rule["outcome"] for rule in result["rule_results"] if rule["rule_id"] == rule_id)


def _change_impact(case: dict, baseline: dict, variant: dict) -> dict:
    baseline_hash = sha256(baseline)
    variant_hash = sha256(variant)
    impact_seed = sha256({"baseline": baseline_hash, "variant": variant_hash})
    return {
        "schema_version": "1.0.0",
        "impact_id": "impact-" + impact_seed.removeprefix("sha256:")[:16],
        "data_class": "SYNTHETIC",
        "baseline_result_id": baseline["result_id"],
        "variant_result_id": variant["result_id"],
        "baseline_hash": baseline_hash,
        "variant_hash": variant_hash,
        "input_changes": [
            {"field": "ecc_enabled", "before": False, "after": True},
            {"field": "mitigation_id", "before": case["baseline"]["mitigation"]["mitigation_id"], "after": case["variant"]["mitigation"]["mitigation_id"]},
            {"field": "policy.approval.status", "before": case["baseline"]["policy"]["approval"]["status"], "after": case["variant"]["policy"]["approval"]["status"]},
        ],
        "output_changes": [
            {"field": "residual_logical_errors", "before": baseline["metrics"]["residual_logical_errors"]["value"], "after": variant["metrics"]["residual_logical_errors"]["value"], "delta": variant["metrics"]["residual_logical_errors"]["value"] - baseline["metrics"]["residual_logical_errors"]["value"]},
            {"field": "corrected", "before": baseline["metrics"]["corrected"]["value"], "after": variant["metrics"]["corrected"]["value"], "delta": variant["metrics"]["corrected"]["value"] - baseline["metrics"]["corrected"]["value"]},
        ],
        "decision_changes": [
            {"field": "RESIDUAL_SEU_THRESHOLD_V2", "before": _rule_outcome(baseline, "RESIDUAL_SEU_THRESHOLD_V2"), "after": _rule_outcome(variant, "RESIDUAL_SEU_THRESHOLD_V2")},
            {"field": "POLICY_APPROVAL_STATE_V2", "before": _rule_outcome(baseline, "POLICY_APPROVAL_STATE_V2"), "after": _rule_outcome(variant, "POLICY_APPROVAL_STATE_V2")},
            {"field": "assurance_decision", "before": "HOLD", "after": "HOLD"},
        ],
        "invalidated_evidence": [
            {"evidence_id": case["baseline"]["mitigation"]["mitigation_id"], "reason_code": "MITIGATION_INPUT_CHANGED", "invalidated_for": ["ECC_TRANSITION_V2", "RESIDUAL_SEU_THRESHOLD_V2"]},
            {"evidence_id": case["baseline"]["policy"]["policy_id"], "reason_code": "POLICY_VERSION_CHANGED", "invalidated_for": ["POLICY_APPROVAL_STATE_V2", "RESIDUAL_SEU_THRESHOLD_V2"]},
        ],
        "evidence_gaps": _gaps(),
    }


def run_mvp_decision(case: dict, model: dict) -> dict:
    """Run one canonical baseline/variant comparison and return byte-stable JSON data."""
    validate_mvp_input(case)
    invalid_model = model_errors(model)
    if invalid_model:
        raise MvpDecisionError("MODEL_FAILURE", invalid_model[0])
    base = _base_packet(case)
    baseline_packet = _scenario_packet(base, case, "baseline")
    variant_packet = _scenario_packet(base, case, "variant")
    baseline = _scenario_result(baseline_packet, case, model, "baseline")
    variant = _scenario_result(variant_packet, case, model, "variant")
    impact = _change_impact(case, baseline, variant)
    impact_errors = _schema_errors(impact, "change-impact.schema.json")
    if impact_errors:
        raise MvpDecisionError("CHANGE_IMPACT_SCHEMA_INVALID", impact_errors[0])
    input_hash = sha256({"case": case, "model": model})
    run_id = "mvp-" + input_hash.removeprefix("sha256:")[:16]
    result = {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "case_id": case["case_id"],
        "data_class": "SYNTHETIC",
        "input_hash": input_hash,
        "output_hash": "",
        "processing_status": "VALID",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "baseline": baseline,
        "variant": variant,
        "change_impact": impact,
    }
    result["output_hash"] = sha256({key: value for key, value in result.items() if key != "output_hash"})
    result_errors = _schema_errors(result, "mvp-decision-result.schema.json")
    if result_errors:
        raise MvpDecisionError("MVP_RESULT_SCHEMA_INVALID", result_errors[0])
    return result


def canonical_result_json(result: dict) -> str:
    return canonical_bytes(result).decode("utf-8")
