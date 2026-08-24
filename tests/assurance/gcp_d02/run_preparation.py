#!/usr/bin/env python3
"""Validate the offline ASR-D02 preparation contract; never calls GCP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_DIR = ROOT / "tests/assurance/gcp_d02"
MANIFEST_PATH = PACKAGE_DIR / "manifest.json"
FIXTURE_PATH = PACKAGE_DIR / "fixtures/asr-d02-preparation-fixtures.json"
TEMPLATE_PATH = (
    ROOT
    / "docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_EVIDENCE_TEMPLATE_H04.json"
)
OPTIMISTIC_DECISIONS = {"PASS", "SUPPORTED_WITH_MITIGATION", "CONDITIONAL", "RECOMMENDED"}
REQUIRED_CASE_FIELDS = {
    "attack_id",
    "case_type",
    "target_layer",
    "precondition",
    "mutation",
    "fixture_ref",
    "expected_stable_code",
    "expected_status",
    "expected_engineering_gate",
    "expected_decision",
    "required_gcp_observations",
    "false_pass_rule",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def all_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [manifest["control"], *manifest["attacks"]]


def classify(case: dict[str, Any], observation: dict[str, Any]) -> str:
    if (
        observation.get("observed_decision") in OPTIMISTIC_DECISIONS
        or observation.get("observed_engineering_gate") == "PASS"
        or observation.get("recommendation_present") is True
    ):
        return "FALSE_PASS" if case["case_type"] == "ATTACK" else "CONTROL_FAIL"
    if case["case_type"] == "ATTACK" and observation.get("downstream_payload_accepted") is True:
        return "FALSE_ACCEPT"
    codes = observation.get("observed_stable_codes")
    expected_matches = (
        isinstance(codes, list)
        and case["expected_stable_code"] in codes
        and observation.get("observed_status") == case["expected_status"]
        and observation.get("observed_engineering_gate") == case["expected_engineering_gate"]
        and observation.get("observed_decision") == case["expected_decision"]
    )
    if not expected_matches:
        return "UNEXPECTED_RESULT" if case["case_type"] == "ATTACK" else "CONTROL_FAIL"
    if case["case_type"] == "CONTROL":
        return "CONTROL_PASS" if observation.get("core_semantic_parity") is True else "CONTROL_FAIL"
    return "SAFE_FAILURE"


def validate_structure(
    manifest: dict[str, Any], fixture: dict[str, Any], template: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    cases = all_cases(manifest)
    ids = [case.get("attack_id") for case in cases]
    if len(ids) != len(set(ids)):
        failures.append("attack IDs are not unique")
    status = manifest.get("preparation_status")
    target = manifest.get("target_lock", {})
    if status not in {"PREPARED_NOT_EXECUTED", "TARGET_LOCKED", "TARGET_LOCKED_PARTIAL_LIVE"}:
        failures.append("manifest preparation_status is invalid")
    if status == "PREPARED_NOT_EXECUTED":
        if target.get("state") != "WAITING_FOR_H05_REVISION":
            failures.append("unexecuted preparation must have an unlocked target")
        if any(value is not None for key, value in target.items() if key != "state"):
            failures.append("unexecuted preparation contains a deployed target identity")
    else:
        if target.get("state") != "LOCKED":
            failures.append("target-locked preparation must have target_lock.state=LOCKED")
        missing_target = [key for key, value in target.items() if key != "state" and not value]
        if missing_target:
            failures.append(f"locked manifest target identity is incomplete: {missing_target}")

    for case in cases:
        missing = sorted(REQUIRED_CASE_FIELDS - set(case))
        if missing:
            failures.append(f"{case.get('attack_id')}: missing fields {missing}")
        if not isinstance(case.get("required_gcp_observations"), list) or not case.get(
            "required_gcp_observations"
        ):
            failures.append(f"{case.get('attack_id')}: required observations are empty")
        code = case.get("expected_stable_code")
        if not isinstance(code, str) or not code or code != code.upper():
            failures.append(f"{case.get('attack_id')}: expected stable code is invalid")
        expected_ref = (
            "tests/assurance/gcp_d02/fixtures/asr-d02-preparation-fixtures.json#/control_input"
            if case.get("case_type") == "CONTROL"
            else "tests/assurance/gcp_d02/fixtures/asr-d02-preparation-fixtures.json"
            f"#/mutations/{case.get('attack_id')}"
        )
        if case.get("fixture_ref") != expected_ref:
            failures.append(f"{case.get('attack_id')}: fixture_ref does not resolve to its owned fixture")
        if case.get("case_type") == "ATTACK" and (
            case.get("expected_status") != "INVALID_INPUT"
            or case.get("expected_engineering_gate") != "NOT_EVALUATED"
            or case.get("expected_decision") != "HOLD"
        ):
            failures.append(f"{case.get('attack_id')}: attack does not fail closed")

    mutation_ids = set(fixture.get("mutations", {}))
    expected_mutation_ids = {case["attack_id"] for case in manifest["attacks"]}
    if mutation_ids != expected_mutation_ids:
        failures.append(
            f"fixture mutation IDs differ: {sorted(mutation_ids ^ expected_mutation_ids)}"
        )
    for attack_id, mutation in fixture.get("mutations", {}).items():
        if not isinstance(mutation, dict) or not isinstance(mutation.get("intent"), str):
            failures.append(f"{attack_id}: fixture mutation intent is missing")
    if fixture.get("fixture_status") != "PREPARATION_ONLY_NOT_LIVE_EVIDENCE":
        failures.append("fixture is not marked preparation-only")
    if fixture.get("control_input", {}).get("data_class") != "SYNTHETIC":
        failures.append("control fixture must be SYNTHETIC")

    observations = template.get("case_observations", [])
    if template.get("package_id") != manifest.get("package_id"):
        failures.append("evidence template package_id differs from manifest")
    observation_ids = [item.get("attack_id") for item in observations]
    if observation_ids != ids:
        failures.append("evidence template case order/IDs do not match manifest")
    if template.get("evidence_status") != "TEMPLATE_NOT_EXECUTED":
        failures.append("evidence template is not marked unexecuted")
    if template.get("target_lock", {}).get("state") != "WAITING_FOR_H05_REVISION":
        failures.append("evidence template target must remain unlocked")
    for item in observations:
        if item.get("execution_attempted") is not False or item.get("classification") != "NOT_EVALUATED":
            failures.append(f"{item.get('attack_id')}: preparation template contains a live result")
        observed_fields = (
            "observed_status",
            "observed_engineering_gate",
            "observed_decision",
            "observed_stable_codes",
            "downstream_payload_accepted",
            "recommendation_present",
            "core_semantic_parity",
            "gcp_observations",
        )
        if any(item.get(field) is not None for field in observed_fields):
            failures.append(f"{item.get('attack_id')}: observed fields must remain null")
    aggregate = template.get("aggregate", {})
    if (
        aggregate.get("live_executions") != 0
        or aggregate.get("evaluated_attacks") != 0
        or aggregate.get("result") != "NOT_EVALUATED"
    ):
        failures.append("evidence template aggregate incorrectly claims execution")
    return failures


def classifier_contract_checks(manifest: dict[str, Any]) -> tuple[int, list[str]]:
    failures: list[str] = []
    checks = 0
    control = manifest["control"]
    control_observation = {
        "observed_status": control["expected_status"],
        "observed_engineering_gate": control["expected_engineering_gate"],
        "observed_decision": control["expected_decision"],
        "observed_stable_codes": [control["expected_stable_code"]],
        "downstream_payload_accepted": True,
        "recommendation_present": False,
        "core_semantic_parity": True,
        "workflow_state": "SUCCEEDED",
    }
    checks += 1
    if classify(control, control_observation) != "CONTROL_PASS":
        failures.append("control classifier did not recognize the safe synthetic parity control")

    for case in manifest["attacks"]:
        safe = {
            "observed_status": case["expected_status"],
            "observed_engineering_gate": case["expected_engineering_gate"],
            "observed_decision": case["expected_decision"],
            "observed_stable_codes": [case["expected_stable_code"]],
            "downstream_payload_accepted": False,
            "recommendation_present": False,
            "core_semantic_parity": None,
            "workflow_state": "SUCCEEDED",
        }
        false_accept = {**safe, "downstream_payload_accepted": True}
        false_pass = {**safe, "observed_decision": "PASS"}
        recommendation = {**safe, "recommendation_present": True}
        for name, observation, expected in (
            ("safe", safe, "SAFE_FAILURE"),
            ("false_accept", false_accept, "FALSE_ACCEPT"),
            ("false_pass", false_pass, "FALSE_PASS"),
            ("recommendation", recommendation, "FALSE_PASS"),
        ):
            checks += 1
            actual = classify(case, observation)
            if actual != expected:
                failures.append(
                    f"{case['attack_id']} {name}: expected {expected}, classifier returned {actual}"
                )
    return checks, failures


def evaluate_filled_evidence(
    manifest: dict[str, Any], evidence: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    target = evidence.get("target_lock", {})
    if target.get("state") != "LOCKED":
        return [], ["filled evidence target_lock.state must be LOCKED"]
    required_target = [key for key in manifest["target_lock"] if key != "state"]
    missing_target = [key for key in required_target if not target.get(key)]
    if missing_target:
        failures.append(f"locked target identity is incomplete: {missing_target}")
    by_id = {item.get("attack_id"): item for item in evidence.get("case_observations", [])}
    results = []
    common_required = manifest["common_required_gcp_observations"]
    for case in all_cases(manifest):
        observation = by_id.get(case["attack_id"])
        if not isinstance(observation, dict):
            failures.append(f"{case['attack_id']}: observation record is missing")
            continue
        if observation.get("execution_attempted") is not True:
            reason = observation.get("not_evaluated_reason")
            if not isinstance(reason, str) or not reason:
                failures.append(f"{case['attack_id']}: NOT_EVALUATED reason is missing")
            results.append({"attack_id": case["attack_id"], "classification": "NOT_EVALUATED"})
            continue
        gcp = observation.get("gcp_observations")
        required = [*common_required, *case["required_gcp_observations"]]
        missing = [field for field in required if not isinstance(gcp, dict) or gcp.get(field) is None]
        if missing:
            failures.append(f"{case['attack_id']}: missing GCP observations {missing}")
        classification = classify(case, observation)
        results.append({"attack_id": case["attack_id"], "classification": classification})
    return results, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluate-evidence",
        type=Path,
        help="Evaluate a separately filled, target-locked evidence JSON. This command still makes no GCP calls.",
    )
    args = parser.parse_args()
    manifest = load(MANIFEST_PATH)
    fixture = load(FIXTURE_PATH)
    template = load(TEMPLATE_PATH)

    if args.evaluate_evidence:
        evidence = load(args.evaluate_evidence.resolve())
        results, failures = evaluate_filled_evidence(manifest, evidence)
        false_accepts = sum(item["classification"] == "FALSE_ACCEPT" for item in results)
        false_passes = sum(item["classification"] == "FALSE_PASS" for item in results)
        not_evaluated = sum(item["classification"] == "NOT_EVALUATED" for item in results)
        unexpected = sum(
            item["classification"] in {"UNEXPECTED_RESULT", "CONTROL_FAIL"} for item in results
        )
        output = {
            "package_id": manifest["package_id"],
            "mode": "OFFLINE_EVIDENCE_EVALUATION",
            "result": "READY_FOR_REVIEW" if not failures and false_accepts == 0 and false_passes == 0 and unexpected == 0 else "FAIL",
            "summary": {
                "observations": len(results),
                "false_accepts": false_accepts,
                "false_passes": false_passes,
                "not_evaluated": not_evaluated,
                "unexpected_results": unexpected,
                "failures": len(failures),
            },
            "results": results,
            "failures": failures,
        }
    else:
        failures = validate_structure(manifest, fixture, template)
        checks, classifier_failures = classifier_contract_checks(manifest)
        failures.extend(classifier_failures)
        output = {
            "package_id": manifest["package_id"],
            "mode": "PREPARATION_VALIDATION_ONLY",
            "result": "READY_FOR_REVIEW" if not failures else "FAIL",
            "asr_d02_status": "NOT_EVALUATED",
            "summary": {
                "prepared_controls": 1,
                "prepared_attacks": len(manifest["attacks"]),
                "classifier_contract_checks": checks,
                "live_executions": 0,
                "evaluated_attacks": 0,
                "false_passes": "NOT_COMPUTED",
                "failures": len(failures),
            },
            "failures": failures,
        }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["result"] == "READY_FOR_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
