#!/usr/bin/env python3
"""Export deterministic engine results consumed by the offline Product UI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import (  # noqa: E402
    SimulationOptions,
    canonical_runtime_json,
    evaluate_runtime_mitigation,
    run_mvp_decision,
    run_simulation,
)
from spectra_sim.contracts import load_contract_fixture  # noqa: E402

DEFAULT_JSON = ROOT / "demo/data/mvp-product-result.json"
DEFAULT_JAVASCRIPT = ROOT / "demo/data/mvp-product-result.js"
JAVASCRIPT_PREFIX = "globalThis.SPECTRA_MVP_PRODUCT_RESULT="


def runtime_output_preimage(result: dict) -> str:
    """Return the production-canonical output-hash preimage for one result."""
    return canonical_runtime_json({
        key: value for key, value in result.items() if key != "output_hash"
    })


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(root: Path = ROOT) -> dict:
    """Build one read model exclusively from existing deterministic engines."""
    case_path = root / "simulation/fixtures/mvp-ecc-policy-v2.json"
    model_path = root / "simulation/config/synthetic-model.json"
    scope_fixture_path = root / "tests/schema/fixtures/valid/synthetic-hold.json"
    case = load_json(case_path)
    model = load_json(model_path)
    scope_fixture = load_json(scope_fixture_path)

    mvp_decision = run_mvp_decision(case, model)
    scope_specs = (
        ("1-on", "shield-1mm-ecc", SimulationOptions(shielding_mm=1, ecc_enabled=True)),
        ("4-on", "shield-4mm-ecc", SimulationOptions(shielding_mm=4, ecc_enabled=True)),
        ("5-on", "out-of-scope-5mm", SimulationOptions(shielding_mm=5, ecc_enabled=True)),
    )
    scope_results = {
        binding: {
            "scenario_id": scenario_id,
            "shielding_mm": options.shielding_mm,
            "ecc_enabled": options.ecc_enabled,
            "result": run_simulation(scope_fixture, model, options),
        }
        for binding, scenario_id, options in scope_specs
    }
    runtime_specs = (
        ("WATCHDOG", "tests/schema/fixtures/valid/synthetic-v2-hold.json"),
        ("TMR", "tests/schema/fixtures/valid/synthetic-tmr-runtime-hold.json"),
        ("SEL_PROTECTION", "tests/schema/fixtures/valid/synthetic-sel-runtime-hold.json"),
    )
    runtime_results = {}
    for method, fixture_ref in runtime_specs:
        packet = load_contract_fixture((root / fixture_ref).resolve())
        mitigation = next(item for item in packet["inputs"] if item["kind"] == "MITIGATION")
        control_inputs = {}
        if method == "TMR":
            control_inputs["replica_failure_probability"] = mitigation["design_parameters"][
                "replica_failure_probability"
            ]
        runtime_result = evaluate_runtime_mitigation(packet)
        runtime_results[method] = {
            "fixture": fixture_ref,
            "control_inputs": control_inputs,
            "integrity": {
                "result_id": runtime_result["result_id"],
                "input_hash": runtime_result["input_hash"],
                "output_hash": runtime_result["output_hash"],
                "output_hash_preimage": runtime_output_preimage(runtime_result),
            },
            "result": runtime_result,
        }

    return {
        "schema_version": "1.0.0",
        "data_class": "SYNTHETIC",
        "provenance": {
            "mvp_runner": "simulation/run_mvp_decision.py",
            "mvp_case_fixture": "simulation/fixtures/mvp-ecc-policy-v2.json",
            "synthetic_model": "simulation/config/synthetic-model.json",
            "scope_runner": "simulation/run_demo.py",
            "scope_fixture": "tests/schema/fixtures/valid/synthetic-hold.json",
            "runtime_runner": "simulation/run_mitigation_runtime.py",
            "runtime_api": "spectra_sim.evaluate_runtime_mitigation",
        },
        "selection_bindings": {
            "1-on": "scope_results.1-on.result",
            "2-off": "mvp_decision.baseline",
            "2-on": "mvp_decision.variant",
            "4-on": "scope_results.4-on.result",
            "5-on": "scope_results.5-on.result",
        },
        "mvp_decision": mvp_decision,
        "scope_results": scope_results,
        "runtime_mitigation_results": runtime_results,
    }


def canonical_json_bytes(payload: dict) -> bytes:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def javascript_bytes(payload: dict) -> bytes:
    json_text = canonical_json_bytes(payload).decode("utf-8").rstrip("\n")
    return f"{JAVASCRIPT_PREFIX}{json_text};\n".encode("utf-8")


def write_outputs(payload: dict, json_path: Path, javascript_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    javascript_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_bytes(canonical_json_bytes(payload))
    javascript_path.write_bytes(javascript_bytes(payload))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--javascript", type=Path, default=DEFAULT_JAVASCRIPT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    write_outputs(payload, args.json, args.javascript)
    print(f"wrote {args.json}")
    print(f"wrote {args.javascript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
