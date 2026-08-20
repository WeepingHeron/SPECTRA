#!/usr/bin/env python3
"""Run the fixed SPECTRA assurance attack baseline and emit JSON results."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests/schema"))

import validate_contracts as contracts  # noqa: E402
from spectra_sim import (  # noqa: E402
    MvpDecisionError,
    SimulationOptions,
    evaluate_runtime_mitigation,
    run_mvp_decision,
    run_simulation,
)

MANIFEST_PATH = ROOT / "tests/assurance/manifest.json"
MODEL_PATH = ROOT / "simulation/config/synthetic-model.json"
OPTIMISTIC = {"SUPPORTED_WITH_MITIGATION", "CONDITIONAL"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_schema_attack(case: dict, packet_schema: dict, registry) -> dict:
    base = contracts.load_fixture((ROOT / case["fixture"]).resolve())
    packet = contracts.apply_operations(base, case["operations"])
    schema_errors = contracts.schema_errors(packet, packet_schema, registry)
    semantic_codes = sorted(contracts.semantic_codes(packet))
    target = case["expected"]["detected_code"]
    return {
        "outcome": "REJECTED" if schema_errors or semantic_codes else "ACCEPTED",
        "detected_code": target if target in semantic_codes else None,
        "safe_decision": packet.get("decision", {}).get("assurance_decision"),
        "schema_error_count": len(schema_errors),
        "semantic_codes": semantic_codes,
    }


def evaluate_simulation_attack(case: dict) -> dict:
    base = contracts.load_fixture((ROOT / case["fixture"]).resolve())
    packet = contracts.apply_operations(base, case.get("operations", []))
    options = SimulationOptions(**case.get("simulation_options", {}))
    result = run_simulation(packet, load(MODEL_PATH), options)
    return {
        "outcome": "SAFE_FAILURE" if result["assurance_decision"] not in OPTIMISTIC else "FALSE_PASS",
        "processing_status": result["processing_status"],
        "assurance_decision": result["assurance_decision"],
        "engineering_gate": result["engineering_gate"],
    }


def evaluate_reproducibility(case: dict) -> dict:
    packet = contracts.load_fixture((ROOT / case["fixture"]).resolve())
    model = load(MODEL_PATH)
    first = run_simulation(packet, model)
    second = run_simulation(packet, model)
    return {
        "outcome": "REPRODUCIBLE" if first == second else "NON_REPRODUCIBLE",
        "processing_status": first["processing_status"],
        "assurance_decision": first["assurance_decision"],
        "engineering_gate": first["engineering_gate"],
    }


def _mvp_safe_failure(code: str | None, outcome: str = "SAFE_FAILURE") -> dict:
    return {
        "outcome": outcome,
        "detected_code": code,
        "processing_status": "INVALID_INPUT" if outcome == "SAFE_FAILURE" else "VALID",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
    }


def _mvp_case(case: dict, attack: dict, model: dict, result_validator) -> dict:
    attacked = contracts.apply_operations(case, attack.get("operations", []))
    if "non_finite_value" in attack:
        values = {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf}
        attacked["particle_flux"]["value"] = values[attack["non_finite_value"]]
    kind = attack["attack_kind"]

    if kind == "ENGINE_INPUT":
        try:
            result = run_mvp_decision(attacked, model)
        except MvpDecisionError as exc:
            return _mvp_safe_failure(exc.code)
        return {
            "outcome": "FALSE_PASS" if result.get("assurance_decision") in OPTIMISTIC else "UNEXPECTED_ACCEPT",
            "detected_code": None,
            "processing_status": result.get("processing_status"),
            "engineering_gate": result.get("engineering_gate"),
            "assurance_decision": result.get("assurance_decision"),
        }

    result = run_mvp_decision(attacked, model)
    if kind == "EVIDENCE_PACKET_TAMPER":
        packet = result[attack["scenario"]]["evidence_packet"]
        packet = contracts.apply_operations(packet, attack["result_operations"])
        codes = contracts.semantic_codes(packet)
        target = attack["expected_code"]
        return _mvp_safe_failure(
            target if target in codes else None,
            "REJECTED" if codes else "FALSE_PASS",
        )
    if kind == "CHANGE_IMPACT_TAMPER":
        tampered = contracts.apply_operations(result, attack["result_operations"])
        errors = list(result_validator.iter_errors(tampered))
        marker = attack["schema_error_marker"]
        matched = any(marker in error.message for error in errors)
        return _mvp_safe_failure(
            attack["expected_code"] if matched else None,
            "REJECTED" if matched else "FALSE_PASS",
        )
    raise ValueError(f"unknown MVP attack kind: {kind}")


def evaluate_mvp_attack_set(case: dict):
    fixture = load((ROOT / case["fixture"]).resolve())
    model = load(MODEL_PATH)
    schema_docs = [load(path) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
    simulation_docs = [
        load(path) for path in sorted((ROOT / "simulation/schemas").glob("*.schema.json"))
    ]
    registry = Registry().with_resources([
        (schema["$id"], Resource.from_contents(schema))
        for schema in schema_docs + simulation_docs
    ])
    result_schema = load(ROOT / "simulation/schemas/mvp-decision-result.schema.json")
    result_validator = Draft202012Validator(
        result_schema, registry=registry, format_checker=FormatChecker()
    )
    subresults = []
    false_passes = 0
    for attack in case["attacks"]:
        try:
            observed = _mvp_case(fixture, attack, model, result_validator)
        except Exception as exc:  # an unexplained exception is never a safe failure
            observed = {
                "outcome": "UNEXPLAINED_EXCEPTION",
                "detected_code": type(exc).__name__,
                "processing_status": None,
                "engineering_gate": None,
                "assurance_decision": None,
            }
        expected_code = attack["expected_code"]
        safety_passed = (
            observed["outcome"] in {"SAFE_FAILURE", "REJECTED"}
            and observed["detected_code"] == expected_code
            and observed["engineering_gate"] == "NOT_EVALUATED"
            and observed["assurance_decision"] == "HOLD"
        )
        expected = attack.get("expected", {})
        recorded = attack.get("actual", {})
        passed = (
            safety_passed
            and projection(observed, expected) == expected
            and projection(observed, recorded) == recorded
        )
        if not passed:
            false_passes += 1
        subresults.append({
            "attack_id": attack["attack_id"],
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
        })
    return {
        "outcome": "SAFE_FAILURE_SET" if false_passes == 0 else "FALSE_PASS",
        "evaluated_attacks": len(subresults),
        "false_passes": false_passes,
        "safe_decision": "HOLD",
        "engineering_gate": "NOT_EVALUATED",
        "subresults": subresults,
    }


def _runtime_result_validator():
    schema_docs = [load(path) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
    simulation_docs = [
        load(path) for path in sorted((ROOT / "simulation/schemas").glob("*.schema.json"))
    ]
    registry = Registry().with_resources([
        (schema["$id"], Resource.from_contents(schema))
        for schema in schema_docs + simulation_docs
    ])
    result_schema = load(ROOT / "simulation/schemas/mitigation-runtime-result.schema.json")
    return Draft202012Validator(
        result_schema, registry=registry, format_checker=FormatChecker()
    )


def _runtime_control(control: dict, result_validator) -> dict:
    packet = contracts.load_fixture((ROOT / control["fixture"]).resolve())
    result = evaluate_runtime_mitigation(packet)
    schema_valid = not list(result_validator.iter_errors(result))
    return {
        "outcome": "CONTROL_PASS" if (
            schema_valid
            and result.get("processing_status") == "VALID"
            and result.get("engineering_gate") == "NOT_EVALUATED"
            and result.get("assurance_decision") == "HOLD"
        ) else "CONTROL_FAIL",
        "processing_status": result.get("processing_status"),
        "engineering_gate": result.get("engineering_gate"),
        "assurance_decision": result.get("assurance_decision"),
        "computed_projection": result.get("computed_projection"),
    }


def _runtime_attack(attack: dict, result_validator) -> dict:
    packet = contracts.load_fixture((ROOT / attack["fixture"]).resolve())
    attacked = contracts.apply_operations(packet, attack.get("operations", []))
    result = evaluate_runtime_mitigation(attacked)
    target = attack["expected_code"]

    if attack["attack_kind"] == "ENGINE_INPUT":
        codes = result.get("stable_error_codes", [])
        schema_valid = not list(result_validator.iter_errors(result))
        return {
            "outcome": "SAFE_FAILURE" if (
                schema_valid
                and result.get("processing_status") == "INVALID_INPUT"
                and result.get("engineering_gate") == "NOT_EVALUATED"
                and result.get("assurance_decision") == "HOLD"
                and target in codes
            ) else "FALSE_PASS",
            "detected_code": target if target in codes else None,
            "processing_status": result.get("processing_status"),
            "engineering_gate": result.get("engineering_gate"),
            "assurance_decision": result.get("assurance_decision"),
            "computed_projection": result.get("computed_projection"),
        }

    if attack["attack_kind"] == "RESULT_TAMPER":
        base_errors = list(result_validator.iter_errors(result))
        tampered = contracts.apply_operations(result, attack["result_operations"])
        target_path = attack["schema_error_path"]
        errors = list(result_validator.iter_errors(tampered))
        matched = not base_errors and any(
            list(error.absolute_path) == target_path for error in errors
        )
        return {
            "outcome": "REJECTED" if matched else "FALSE_PASS",
            "detected_code": target if matched else None,
            "processing_status": "INVALID_INPUT" if matched else tampered.get("processing_status"),
            "engineering_gate": "NOT_EVALUATED" if matched else tampered.get("engineering_gate"),
            "assurance_decision": "HOLD" if matched else tampered.get("assurance_decision"),
            "computed_projection": tampered.get("computed_projection"),
        }
    raise ValueError(f"unknown runtime attack kind: {attack['attack_kind']}")


def evaluate_runtime_attack_set(case: dict) -> dict:
    result_validator = _runtime_result_validator()
    control_results = []
    control_failures = 0
    for control in case["controls"]:
        try:
            observed = _runtime_control(control, result_validator)
        except Exception as exc:
            observed = {
                "outcome": "UNEXPLAINED_EXCEPTION",
                "processing_status": None,
                "engineering_gate": None,
                "assurance_decision": None,
                "computed_projection": None,
                "exception_type": type(exc).__name__,
            }
        expected = control["expected"]
        recorded = control["actual"]
        passed = (
            projection(observed, expected) == expected
            and projection(observed, recorded) == recorded
        )
        if not passed:
            control_failures += 1
        control_results.append({
            "control_id": control["control_id"],
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
        })

    attack_results = []
    false_passes = 0
    for attack in case["attacks"]:
        try:
            observed = _runtime_attack(attack, result_validator)
        except Exception as exc:
            observed = {
                "outcome": "UNEXPLAINED_EXCEPTION",
                "detected_code": type(exc).__name__,
                "processing_status": None,
                "engineering_gate": None,
                "assurance_decision": None,
                "computed_projection": None,
            }
        expected = attack["expected"]
        recorded = attack["actual"]
        passed = (
            projection(observed, expected) == expected
            and projection(observed, recorded) == recorded
        )
        if not passed:
            false_passes += 1
        attack_results.append({
            "attack_id": attack["attack_id"],
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
        })

    clean = control_failures == 0 and false_passes == 0
    return {
        "outcome": "SAFE_FAILURE_SET" if clean else "FALSE_PASS",
        "evaluated_attacks": len(attack_results),
        "evaluated_controls": len(control_results),
        "not_evaluated": 0,
        "false_passes": false_passes,
        "control_failures": control_failures,
        "safe_decision": "HOLD",
        "engineering_gate": "NOT_EVALUATED",
        "control_results": control_results,
        "attack_results": attack_results,
    }


def projection(value: dict, keys) -> dict:
    return {key: value.get(key) for key in keys}


def main() -> int:
    manifest = load(MANIFEST_PATH)
    schema_docs = [load(path) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
    packet_schema = load(ROOT / "schemas/evidence-packet.schema.json")
    registry = contracts.build_registry(schema_docs)
    results = []
    failures = []
    false_passes = 0

    for case in manifest["cases"]:
        kind = case["execution"]
        if kind == "SCHEMA_SEMANTIC_GATE":
            observed = evaluate_schema_attack(case, packet_schema, registry)
        elif kind == "SYNTHETIC_SIMULATION":
            observed = evaluate_simulation_attack(case)
        elif kind == "REPRODUCIBILITY_CONTROL":
            observed = evaluate_reproducibility(case)
        elif kind == "MVP_DECISION_ATTACK_SET":
            observed = evaluate_mvp_attack_set(case)
        elif kind == "RUNTIME_MITIGATION_ATTACK_SET":
            observed = evaluate_runtime_attack_set(case)
        elif kind == "DEPENDENCY_WAIT":
            observed = case["actual"]
        else:
            failures.append(f"{case['attack_id']}: unknown execution kind {kind}")
            continue

        expected = case["expected"]
        recorded = case["actual"]
        observed_projection = projection(observed, expected)
        if observed_projection != expected:
            failures.append(
                f"{case['attack_id']}: expected {expected}, observed {observed_projection}"
            )
        if projection(observed, recorded) != recorded:
            failures.append(
                f"{case['attack_id']}: recorded actual is stale: {recorded} vs {projection(observed, recorded)}"
            )
        if observed.get("outcome") in {"ACCEPTED", "FALSE_PASS", "NON_REPRODUCIBLE"}:
            false_passes += max(1, observed.get("false_passes", 0))
        results.append({
            "attack_id": case["attack_id"],
            "status": "NOT_EVALUATED" if kind == "DEPENDENCY_WAIT" else (
                "PASS" if observed_projection == expected else "FAIL"
            ),
            "observed": observed,
        })

    evaluated = sum(result["status"] != "NOT_EVALUATED" for result in results)
    deferred = sum(result["status"] == "NOT_EVALUATED" for result in results)
    evaluated_attack_executions = 0
    evaluated_controls = 0
    for case, result in zip(manifest["cases"], results):
        if result["status"] == "NOT_EVALUATED":
            continue
        if case["execution"] == "REPRODUCIBILITY_CONTROL":
            evaluated_controls += 1
        elif case["execution"] in {"MVP_DECISION_ATTACK_SET", "RUNTIME_MITIGATION_ATTACK_SET"}:
            evaluated_attack_executions += result["observed"]["evaluated_attacks"]
            evaluated_controls += result["observed"].get("evaluated_controls", 0)
        else:
            evaluated_attack_executions += 1
    output = {
        "suite_id": manifest["suite_id"],
        "manifest_version": manifest["manifest_version"],
        "result": "READY_FOR_REVIEW" if not failures and false_passes == 0 else "FAIL",
        "summary": {
            "cases": len(results),
            "evaluated": evaluated,
            "evaluated_attack_executions": evaluated_attack_executions,
            "evaluated_controls": evaluated_controls,
            "not_evaluated": deferred,
            "false_passes": false_passes,
            "failures": len(failures),
        },
        "results": results,
        "failures": failures,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if output["result"] == "READY_FOR_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
