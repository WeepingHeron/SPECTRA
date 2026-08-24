#!/usr/bin/env python3
"""Structural and execution tests for the Workstream 80 Product result binding."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT / "demo/product.html"
JSON_PATH = ROOT / "demo/data/mvp-product-result.json"
JAVASCRIPT_PATH = ROOT / "demo/data/mvp-product-result.js"
EXPORTER_PATH = ROOT / "demo/build_product_data.py"
GCP_JSON_PATH = ROOT / "demo/data/h05-gcp-snapshot.json"
GCP_JAVASCRIPT_PATH = ROOT / "demo/data/h05-gcp-snapshot.js"
GCP_EXPORTER_PATH = ROOT / "demo/build_gcp_snapshot.py"

spec = importlib.util.spec_from_file_location("build_product_data", EXPORTER_PATH)
exporter = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(exporter)

gcp_spec = importlib.util.spec_from_file_location("build_gcp_snapshot", GCP_EXPORTER_PATH)
gcp_exporter = importlib.util.module_from_spec(gcp_spec)
assert gcp_spec.loader is not None
gcp_spec.loader.exec_module(gcp_exporter)


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []
        self.inline: list[str] = []
        self._capture = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        src = dict(attrs).get("src")
        if src:
            self.sources.append(src)
        else:
            self._capture = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capture:
            self.inline.append("".join(self._buffer))
            self._capture = False


def node_path() -> str:
    found = shutil.which("node")
    if found:
        return found
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    if bundled.is_file():
        return str(bundled)
    raise unittest.SkipTest("Node.js runtime unavailable")


def parse_wrapper(text: str) -> dict:
    prefix = exporter.JAVASCRIPT_PREFIX
    if not text.startswith(prefix) or not text.endswith(";\n"):
        raise AssertionError("unexpected JavaScript wrapper shape")
    return json.loads(text[len(prefix):-2])


def build_tmr_runtime_record(probability: float, declared_projection: float) -> dict:
    from spectra_sim import evaluate_runtime_mitigation
    from spectra_sim.contracts import load_contract_fixture

    packet = load_contract_fixture(
        (ROOT / "tests/schema/fixtures/valid/synthetic-tmr-runtime-hold.json").resolve()
    )
    mitigation = next(item for item in packet["inputs"] if item["kind"] == "MITIGATION")
    mitigation["design_parameters"]["replica_failure_probability"] = probability
    mitigation["runtime_projection"]["system_failure_probability"] = declared_projection
    result = evaluate_runtime_mitigation(packet)
    return {
        "fixture": "numeric-parity-control",
        "control_inputs": {"replica_failure_probability": probability},
        "integrity": {
            "result_id": result["result_id"],
            "input_hash": result["input_hash"],
            "output_hash": result["output_hash"],
            "output_hash_preimage": exporter.runtime_output_preimage(result),
        },
        "result": result,
    }


class ProductDataBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.json_bytes = JSON_PATH.read_bytes()
        cls.javascript_bytes = JAVASCRIPT_PATH.read_bytes()
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.wrapper = JAVASCRIPT_PATH.read_text(encoding="utf-8")
        cls.parser = ScriptParser()
        cls.parser.feed(cls.html)
        cls.gcp_payload = json.loads(GCP_JSON_PATH.read_text(encoding="utf-8"))
        cls.gcp_wrapper = GCP_JAVASCRIPT_PATH.read_text(encoding="utf-8")

    def test_exporter_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            first_json = temp_path / "first.json"
            first_js = temp_path / "first.js"
            second_json = temp_path / "second.json"
            second_js = temp_path / "second.js"
            for json_path, js_path in ((first_json, first_js), (second_json, second_js)):
                subprocess.run(
                    ["python3", str(EXPORTER_PATH), "--json", str(json_path), "--javascript", str(js_path)],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_js.read_bytes(), second_js.read_bytes())
            self.assertEqual(first_json.read_bytes(), JSON_PATH.read_bytes())
            self.assertEqual(first_js.read_bytes(), JAVASCRIPT_PATH.read_bytes())

    def test_json_and_wrapper_are_the_same_payload(self) -> None:
        self.assertEqual(parse_wrapper(self.wrapper), self.payload)
        self.assertEqual(JSON_PATH.read_bytes(), exporter.canonical_json_bytes(self.payload))
        self.assertEqual(JAVASCRIPT_PATH.read_bytes(), exporter.javascript_bytes(self.payload))

    def test_gcp_snapshot_is_deterministic_source_bound_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            outputs = []
            for suffix in ("first", "second"):
                json_path = temp_path / f"{suffix}.json"
                js_path = temp_path / f"{suffix}.js"
                subprocess.run(
                    ["python3", str(GCP_EXPORTER_PATH), "--json", str(json_path), "--javascript", str(js_path)],
                    cwd=ROOT, check=True, capture_output=True, text=True,
                )
                outputs.append((json_path.read_bytes(), js_path.read_bytes()))
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[0][0], GCP_JSON_PATH.read_bytes())
            self.assertEqual(outputs[0][1], GCP_JAVASCRIPT_PATH.read_bytes())

        prefix = gcp_exporter.JS_PREFIX
        self.assertTrue(self.gcp_wrapper.startswith(prefix))
        self.assertEqual(json.loads(self.gcp_wrapper[len(prefix):-2]), self.gcp_payload)
        self.assertEqual(
            self.gcp_payload["snapshot_sha256"],
            "sha256:" + hashlib.sha256(self.gcp_payload["snapshot_hash_preimage"].encode()).hexdigest(),
        )
        self.assertEqual(json.loads(self.gcp_payload["snapshot_hash_preimage"]), {
            key: value for key, value in self.gcp_payload.items()
            if key not in {"snapshot_hash_preimage", "snapshot_sha256"}
        })

        runs = json.loads((ROOT / "docs/workstreams/70-platform-gcp/evidence/h05-e2e-runs.json").read_text())
        inventory = json.loads((ROOT / "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json").read_text())
        cases = {item["case"]: item for item in runs["cases"]}
        self.assertEqual(self.gcp_payload["workflow"]["revision"], inventory["workflow"]["revision_id"])
        self.assertEqual(
            self.gcp_payload["executions"]["normal"]["id"],
            cases["normal-production-core"]["workflow_execution"].rsplit("/", 1)[-1],
        )
        self.assertEqual(self.gcp_payload["final_assurance"], "HOLD")
        self.assertEqual(self.gcp_payload["executions"]["endpoint_override"]["agent_call_count"], 0)

        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(self.gcp_wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING;
const source=globalThis.SPECTRA_GCP_H05_SNAPSHOT;
const valid=api.resolveGcpSnapshot(source);
const optimistic=JSON.parse(JSON.stringify(source)); optimistic.final_assurance='PASS';
const changed=JSON.parse(JSON.stringify(source)); changed.workflow.revision='999999-bad';
const results=[api.resolveGcpSnapshot(undefined),api.resolveGcpSnapshot(optimistic),api.resolveGcpSnapshot(changed)];
process.stdout.write(JSON.stringify({{valid,closed:results.map(x=>({{ready:x.ready,assurance:x.assurance}}))}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        self.assertTrue(observed["valid"]["ready"])
        self.assertEqual(observed["valid"]["assurance"], "HOLD")
        self.assertTrue(all(item == {"ready": False, "assurance": "HOLD"} for item in observed["closed"]))

    def test_embedded_contracts_and_semantic_gates(self) -> None:
        from spectra_sim.contracts import packet_contract_errors
        from spectra_sim.mvp_engine import _schema_errors

        mvp = self.payload["mvp_decision"]
        self.assertEqual(_schema_errors(mvp, "mvp-decision-result.schema.json"), [])
        for scenario_name in ("baseline", "variant"):
            self.assertEqual(packet_contract_errors(mvp[scenario_name]["evidence_packet"]), [])
            self.assertEqual(mvp[scenario_name]["assurance_decision"], "HOLD")
        for item in self.payload["scope_results"].values():
            result = item["result"]
            self.assertEqual(_schema_errors(result, "simulation-result.schema.json"), [])
            if result["evidence_packet"] is not None:
                self.assertEqual(packet_contract_errors(result["evidence_packet"]), [])
            self.assertEqual(result["assurance_decision"], "HOLD")
        outside = self.payload["scope_results"]["5-on"]["result"]
        self.assertEqual(outside["processing_status"], "OUT_OF_MODEL_SCOPE")
        self.assertEqual(outside["engineering_gate"], "NOT_EVALUATED")
        self.assertTrue(all(value is None for value in outside["metrics"].values()))

    def test_runtime_results_match_production_api_and_schema(self) -> None:
        from spectra_sim import evaluate_runtime_mitigation
        from spectra_sim.contracts import load_contract_fixture
        from spectra_sim.mvp_engine import _schema_errors

        runtime = self.payload["runtime_mitigation_results"]
        self.assertEqual(set(runtime), {"WATCHDOG", "TMR", "SEL_PROTECTION"})
        for method, record in runtime.items():
            expected = evaluate_runtime_mitigation(
                load_contract_fixture((ROOT / record["fixture"]).resolve())
            )
            result = record["result"]
            self.assertEqual(result, expected)
            self.assertEqual(_schema_errors(result, "mitigation-runtime-result.schema.json"), [])
            self.assertEqual(result["method"], method)
            self.assertEqual(result["processing_status"], "VALID")
            self.assertEqual(result["engineering_gate"], "NOT_EVALUATED")
            self.assertEqual(result["assurance_decision"], "HOLD")
            self.assertEqual(result["data_class"], "SYNTHETIC")
            self.assertTrue(result["result_id"].startswith("runtime-"))
            self.assertTrue(result["input_hash"].startswith("sha256:"))
            self.assertTrue(result["output_hash"].startswith("sha256:"))
            self.assertEqual(result["computed_projection"]["method"], method)
            self.assertTrue(result["stable_error_codes"])
            self.assertEqual(record["integrity"], {
                "result_id": result["result_id"],
                "input_hash": result["input_hash"],
                "output_hash": result["output_hash"],
                "output_hash_preimage": exporter.runtime_output_preimage(result),
            })

        watchdog = runtime["WATCHDOG"]["result"]["computed_projection"]
        self.assertEqual(watchdog["false_positive_activation_count"], 1.0)
        self.assertEqual(watchdog["reboot_count_total"], 1.0)
        self.assertEqual(watchdog["downtime_total_seconds"], 60.0)
        self.assertIn('"downtime_total_seconds":60.0', runtime["WATCHDOG"]["integrity"]["output_hash_preimage"])
        self.assertIn('"true_target_event_count":0.0', runtime["WATCHDOG"]["integrity"]["output_hash_preimage"])
        tmr_record = runtime["TMR"]
        self.assertEqual(tmr_record["control_inputs"]["replica_failure_probability"], 0.1)
        self.assertEqual(tmr_record["result"]["computed_projection"]["system_failure_probability"], 0.028)
        sel = runtime["SEL_PROTECTION"]["result"]["computed_projection"]
        self.assertEqual(sel["true_sel_activation_count"], 1.0)
        self.assertEqual(sel["false_trip_activation_count"], 1.0)
        self.assertEqual(sel["power_cycle_count_total"], 2.0)
        self.assertEqual(sel["downtime_total_seconds"], 32.0)

    def test_ui_uses_local_wrapper_without_authoritative_duplicates(self) -> None:
        self.assertEqual(self.parser.sources, ["data/mvp-product-result.js", "data/h05-gcp-snapshot.js"])
        forbidden_ids = set()
        forbidden_numbers = set()

        def visit(value, key=""):
            if isinstance(value, dict):
                for child_key, child in value.items():
                    visit(child, child_key)
            elif isinstance(value, list):
                for child in value:
                    visit(child, key)
            elif isinstance(value, str) and (key.endswith("run_id") or key.endswith("result_id") or key in {"impact_id", "packet_id"}):
                forbidden_ids.add(value)
            elif isinstance(value, (int, float)) and key == "value":
                return

        visit(self.payload)
        mvp = self.payload["mvp_decision"]
        for scenario_name in ("baseline", "variant"):
            forbidden_numbers.update(str(metric["value"]) for metric in mvp[scenario_name]["metrics"].values())
        for entry in self.payload["scope_results"].values():
            forbidden_numbers.update(
                str(metric["value"])
                for metric in entry["result"]["metrics"].values()
                if metric is not None
            )
        for identifier in forbidden_ids:
            self.assertNotIn(identifier, self.html)
        for number in forbidden_numbers:
            self.assertIsNone(re.search(rf"(?<![\d.]){re.escape(number)}(?![\d.])", self.html))
        self.assertNotIn("const runs", self.html)

        visible_markup = re.sub(r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>", "", self.html, flags=re.I | re.S)
        for record in self.payload["runtime_mitigation_results"].values():
            result = record["result"]
            for authoritative in (result["result_id"], result["equation_id"], result["input_hash"], result["output_hash"]):
                self.assertNotIn(authoritative, self.html)
        for authoritative_number in ("0.028", "0.1", "60.0", "32.0"):
            self.assertNotIn(authoritative_number, visible_markup)
        for value in (
            self.gcp_payload["workflow"]["revision"],
            *(item["revision"] for item in self.gcp_payload["agents"]),
            *(item["id"] for item in self.gcp_payload["executions"].values()),
        ):
            self.assertNotIn(str(value), self.html)

    def test_ui_consumer_and_safe_fallback_execute(self) -> None:
        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING;
const valid=api.resolveProductData(globalThis.SPECTRA_MVP_PRODUCT_RESULT);
const missing=api.resolveProductData(undefined);
const corrupt=JSON.parse(JSON.stringify(globalThis.SPECTRA_MVP_PRODUCT_RESULT));
corrupt.mvp_decision.variant.assurance_decision='PASS';
const rejected=api.resolveProductData(corrupt);
process.stdout.write(JSON.stringify({{
  validReady:valid.ready,
  caseId:valid.caseId,
  runId:valid.runId,
  baselineResidual:valid.selections['2-off'].residualSeu,
  variantResidual:valid.selections['2-on'].residualSeu,
  outside:valid.selections['5-on'],
  packetId:valid.selections['2-on'].packetId,
  impactId:valid.impact.id,
  invalidationCount:valid.impact.invalidations.length,
  gapCodes:valid.gaps.map(g=>g.gap_code),
  missing:{{ready:missing.ready,assurance:missing.assurance,engineering:missing.engineering,selectionCount:Object.keys(missing.selections).length}},
  rejected:{{ready:rejected.ready,assurance:rejected.assurance,engineering:rejected.engineering,selectionCount:Object.keys(rejected.selections).length}}
}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        mvp = self.payload["mvp_decision"]
        self.assertTrue(observed["validReady"])
        self.assertEqual(observed["caseId"], mvp["case_id"])
        self.assertEqual(observed["runId"], mvp["run_id"])
        self.assertEqual(observed["baselineResidual"], mvp["baseline"]["metrics"]["residual_logical_errors"]["value"])
        self.assertEqual(observed["variantResidual"], mvp["variant"]["metrics"]["residual_logical_errors"]["value"])
        self.assertEqual(observed["outside"]["processing"], "OUT_OF_MODEL_SCOPE")
        self.assertIsNone(observed["outside"]["tid"])
        self.assertEqual(observed["packetId"], mvp["variant"]["evidence_packet"]["packet_id"])
        self.assertEqual(observed["impactId"], mvp["change_impact"]["impact_id"])
        self.assertEqual(observed["invalidationCount"], len(mvp["change_impact"]["invalidated_evidence"]))
        self.assertEqual(observed["gapCodes"], [gap["gap_code"] for gap in mvp["variant"]["evidence_gaps"]])
        for key in ("missing", "rejected"):
            self.assertEqual(observed[key], {"ready": False, "assurance": "HOLD", "engineering": "NOT_EVALUATED", "selectionCount": 0})

    def test_runtime_ui_consumer_selection_and_attacks_execute(self) -> None:
        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING;
const source=globalThis.SPECTRA_MVP_PRODUCT_RESULT;
const valid=api.resolveProductData(source);
const snapshot=model=>Object.fromEntries(['WATCHDOG','TMR','SEL_PROTECTION'].map(method=>{{
  const record=api.getRuntimeRecord(model,method);
  return [method,{{ready:record.ready,reason:record.reason,processing:record.processing,engineering:record.engineering,assurance:record.assurance,dataClass:record.dataClass,resultId:record.resultId,equationId:record.equationId,inputHash:record.inputHash,outputHash:record.outputHash,projection:record.projection,policy:record.policy,codes:record.codes,metrics:api.runtimeDisplayMetrics(record)}}];
}}));
const clone=value=>JSON.parse(JSON.stringify(value));
const reverseKeys=value=>Array.isArray(value)?value.map(reverseKeys):(value&&typeof value==='object'?Object.fromEntries(Object.keys(value).reverse().map(key=>[key,reverseKeys(value[key])])):value);
const missingCollection=JSON.parse(JSON.stringify(source)); delete missingCollection.runtime_mitigation_results;
const brokenRecord=JSON.parse(JSON.stringify(source)); delete brokenRecord.runtime_mitigation_results.WATCHDOG.result.computed_projection;
const unknownMethod=JSON.parse(JSON.stringify(source)); unknownMethod.runtime_mitigation_results.UNKNOWN={{}};
const badHash=JSON.parse(JSON.stringify(source)); badHash.runtime_mitigation_results.TMR.result.output_hash='sha256:'+'0'.repeat(64);
const optimistic=JSON.parse(JSON.stringify(source)); optimistic.runtime_mitigation_results.SEL_PROTECTION.result.assurance_decision='PASS';
const schemaDrift=JSON.parse(JSON.stringify(source)); schemaDrift.runtime_mitigation_results.WATCHDOG.result.schema_version='2.0.0';
const staleProjection=clone(source); staleProjection.runtime_mitigation_results.WATCHDOG.result.computed_projection.downtime_total_seconds=999;
const positiveToNegativeZero=clone(source); positiveToNegativeZero.runtime_mitigation_results.WATCHDOG.result.computed_projection.true_target_event_count=-0;
const stalePolicy=clone(source); stalePolicy.runtime_mitigation_results.TMR.result.policy_evaluation.status='MUTATED_DRAFT';
const staleCode=clone(source); staleCode.runtime_mitigation_results.SEL_PROTECTION.result.stable_error_codes[0]='MUTATED_CODE';
const projectionAndAnchor=clone(source); projectionAndAnchor.runtime_mitigation_results.WATCHDOG.result.computed_projection.downtime_total_seconds=999; projectionAndAnchor.runtime_mitigation_results.WATCHDOG.integrity.output_hash='sha256:'+'1'.repeat(64);
const preimageOnly=clone(source); const preimageOnlyBody=JSON.parse(preimageOnly.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage); preimageOnlyBody.computed_projection.downtime_total_seconds=999; preimageOnly.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage=JSON.stringify(preimageOnlyBody);
const resultAndPreimage=clone(source); resultAndPreimage.runtime_mitigation_results.WATCHDOG.result.computed_projection.downtime_total_seconds=999; const resultAndPreimageBody=JSON.parse(resultAndPreimage.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage); resultAndPreimageBody.computed_projection.downtime_total_seconds=999; resultAndPreimage.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage=JSON.stringify(resultAndPreimageBody);
const allHashesSame=clone(resultAndPreimage); allHashesSame.runtime_mitigation_results.WATCHDOG.result.output_hash='sha256:'+'2'.repeat(64); allHashesSame.runtime_mitigation_results.WATCHDOG.integrity.output_hash='sha256:'+'2'.repeat(64);
const negativeZeroControl=clone(source); negativeZeroControl.runtime_mitigation_results.WATCHDOG.result.computed_projection.true_target_event_count=-0; negativeZeroControl.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage=negativeZeroControl.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage.replace('"true_target_event_count":0.0','"true_target_event_count":-0.0'); negativeZeroControl.runtime_mitigation_results.WATCHDOG.result.output_hash=api.runtimePreimageHash(negativeZeroControl.runtime_mitigation_results.WATCHDOG.integrity.output_hash_preimage); negativeZeroControl.runtime_mitigation_results.WATCHDOG.integrity.output_hash=negativeZeroControl.runtime_mitigation_results.WATCHDOG.result.output_hash;
const negativeToPositiveZero=clone(negativeZeroControl); negativeToPositiveZero.runtime_mitigation_results.WATCHDOG.result.computed_projection.true_target_event_count=0;
const reordered=clone(source); reordered.runtime_mitigation_results.WATCHDOG.result=reverseKeys(reordered.runtime_mitigation_results.WATCHDOG.result);
const summarize=value=>{{const m=api.resolveProductData(value);return {{productReady:m.ready,collectionReady:m.runtime.ready,radiationResidual:m.selections['2-on']&&m.selections['2-on'].residualSeu,records:snapshot(m)}};}};
const negativeControlModel=api.resolveProductData(negativeZeroControl); const negativeControlRecord=api.getRuntimeRecord(negativeControlModel,'WATCHDOG');
process.stdout.write(JSON.stringify({{valid:{{productReady:valid.ready,collectionReady:valid.runtime.ready,records:snapshot(valid),preimageHashes:Object.fromEntries(Object.entries(source.runtime_mitigation_results).map(([method,record])=>[method,api.runtimePreimageHash(record.integrity.output_hash_preimage)]))}},missingCollection:summarize(missingCollection),brokenRecord:summarize(brokenRecord),unknownMethod:summarize(unknownMethod),badHash:summarize(badHash),optimistic:summarize(optimistic),schemaDrift:summarize(schemaDrift),staleProjection:summarize(staleProjection),positiveToNegativeZero:summarize(positiveToNegativeZero),stalePolicy:summarize(stalePolicy),staleCode:summarize(staleCode),projectionAndAnchor:summarize(projectionAndAnchor),preimageOnly:summarize(preimageOnly),resultAndPreimage:summarize(resultAndPreimage),allHashesSame:summarize(allHashesSame),negativeZeroControl:{{summary:summarize(negativeZeroControl),isNegativeZero:Object.is(negativeControlRecord.projection.true_target_event_count,-0)}},negativeToPositiveZero:summarize(negativeToPositiveZero),reordered:summarize(reordered)}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        self.assertTrue(observed["valid"]["productReady"])
        self.assertTrue(observed["valid"]["collectionReady"])
        for method, source_record in self.payload["runtime_mitigation_results"].items():
            actual = observed["valid"]["records"][method]
            expected = source_record["result"]
            self.assertTrue(actual["ready"])
            self.assertEqual(actual["processing"], expected["processing_status"])
            self.assertEqual(actual["engineering"], expected["engineering_gate"])
            self.assertEqual(actual["assurance"], expected["assurance_decision"])
            self.assertEqual(actual["dataClass"], expected["data_class"])
            self.assertEqual(actual["resultId"], expected["result_id"])
            self.assertEqual(actual["equationId"], expected["equation_id"])
            self.assertEqual(actual["inputHash"], expected["input_hash"])
            self.assertEqual(actual["outputHash"], expected["output_hash"])
            self.assertEqual(actual["projection"], expected["computed_projection"])
            self.assertEqual(actual["policy"], expected["policy_evaluation"])
            self.assertEqual(actual["codes"], expected["stable_error_codes"])
            self.assertTrue(actual["metrics"])
            self.assertEqual(observed["valid"]["preimageHashes"][method], expected["output_hash"])

        self.assertFalse(observed["missingCollection"]["collectionReady"])
        self.assertTrue(all(not record["ready"] and record["assurance"] == "HOLD" for record in observed["missingCollection"]["records"].values()))
        self.assertFalse(observed["unknownMethod"]["collectionReady"])
        self.assertTrue(all(not record["ready"] for record in observed["unknownMethod"]["records"].values()))
        self.assertFalse(observed["brokenRecord"]["records"]["WATCHDOG"]["ready"])
        self.assertTrue(observed["brokenRecord"]["records"]["TMR"]["ready"])
        self.assertFalse(observed["badHash"]["records"]["TMR"]["ready"])
        self.assertFalse(observed["optimistic"]["records"]["SEL_PROTECTION"]["ready"])
        self.assertFalse(observed["schemaDrift"]["records"]["WATCHDOG"]["ready"])
        self.assertTrue(observed["reordered"]["records"]["WATCHDOG"]["ready"])
        self.assertTrue(observed["negativeZeroControl"]["summary"]["records"]["WATCHDOG"]["ready"])
        self.assertTrue(observed["negativeZeroControl"]["isNegativeZero"])
        self.assertEqual(observed["staleProjection"]["records"]["WATCHDOG"]["reason"], "RUNTIME_PREIMAGE_VALUE_MISMATCH")
        for attack in (
            "brokenRecord", "badHash", "optimistic", "schemaDrift",
            "staleProjection", "positiveToNegativeZero", "negativeToPositiveZero",
            "stalePolicy", "staleCode",
            "projectionAndAnchor", "preimageOnly", "resultAndPreimage",
            "allHashesSame",
        ):
            self.assertTrue(observed[attack]["productReady"])
            self.assertEqual(
                observed[attack]["radiationResidual"],
                self.payload["mvp_decision"]["variant"]["metrics"]["residual_logical_errors"]["value"],
            )
            for record in observed[attack]["records"].values():
                if not record["ready"]:
                    self.assertEqual(record["processing"], "DATA_UNAVAILABLE")
                    self.assertEqual(record["engineering"], "NOT_EVALUATED")
                    self.assertEqual(record["assurance"], "HOLD")
                    self.assertIsNone(record["projection"])
                    self.assertEqual(record["resultId"], "—")
                    self.assertEqual(record["inputHash"], "—")
                    self.assertEqual(record["outputHash"], "—")

    def test_assurance_attack_demo_controller_and_reset(self) -> None:
        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING;
const source=globalThis.SPECTRA_MVP_PRODUCT_RESULT;
const sourceBefore=JSON.stringify(source);
const original=source.runtime_mitigation_results.WATCHDOG;
const attack=api.buildWatchdogAttackPayload(source);
const attacked=attack.runtime_mitigation_results.WATCHDOG;
const controller=api.createAttackDemoController(source);
const record=(model,method)=>api.getRuntimeRecord(model,method);
const summarize=snapshot=>{{
  const watchdog=record(snapshot.model,'WATCHDOG');
  return {{
    phase:snapshot.phase,
    preview:snapshot.preview,
    watchdog:{{ready:watchdog.ready,reason:watchdog.reason,processing:watchdog.processing,engineering:watchdog.engineering,assurance:watchdog.assurance,projection:watchdog.projection,resultId:watchdog.resultId,inputHash:watchdog.inputHash,outputHash:watchdog.outputHash}},
    tmrReady:record(snapshot.model,'TMR').ready,
    selReady:record(snapshot.model,'SEL_PROTECTION').ready,
    radiationResidual:snapshot.model.selections['2-on']&&snapshot.model.selections['2-on'].residualSeu
  }};
}};
const normal=summarize(controller.current());
const preview=summarize(controller.preview());
const blocked=summarize(controller.verify());
const reset=summarize(controller.reset());
const normalizedAttack=JSON.parse(JSON.stringify(attack));
normalizedAttack.runtime_mitigation_results.WATCHDOG.result.computed_projection.downtime_total_seconds=original.result.computed_projection.downtime_total_seconds;
process.stdout.write(JSON.stringify({{
  sourceUnchanged:sourceBefore===JSON.stringify(source),
  cloneIsDistinct:attack!==source&&attacked!==original,
  attackOnlyChangesDowntime:JSON.stringify(normalizedAttack)===sourceBefore,
  attackDowntime:attacked.result.computed_projection.downtime_total_seconds,
  stalePreimage:attacked.integrity.output_hash_preimage===original.integrity.output_hash_preimage,
  staleResultHash:attacked.result.output_hash===original.result.output_hash,
  staleAnchor:attacked.integrity.output_hash===original.integrity.output_hash,
  normal,preview,blocked,reset
}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        source_watchdog = self.payload["runtime_mitigation_results"]["WATCHDOG"]["result"]
        residual = self.payload["mvp_decision"]["variant"]["metrics"]["residual_logical_errors"]["value"]

        self.assertTrue(observed["sourceUnchanged"])
        self.assertTrue(observed["cloneIsDistinct"])
        self.assertTrue(observed["attackOnlyChangesDowntime"])
        self.assertEqual(observed["attackDowntime"], 999)
        self.assertTrue(observed["stalePreimage"])
        self.assertTrue(observed["staleResultHash"])
        self.assertTrue(observed["staleAnchor"])

        normal = observed["normal"]
        self.assertEqual(normal["phase"], "normal")
        self.assertEqual(normal["watchdog"]["projection"]["false_positive_activation_count"], 1)
        self.assertEqual(normal["watchdog"]["projection"]["reboot_count_total"], 1)
        self.assertEqual(normal["watchdog"]["projection"]["downtime_total_seconds"], 60)
        self.assertEqual(normal["watchdog"]["processing"], "VALID")
        self.assertEqual(normal["watchdog"]["engineering"], "NOT_EVALUATED")
        self.assertEqual(normal["watchdog"]["assurance"], "HOLD")
        self.assertEqual(normal["watchdog"]["resultId"], source_watchdog["result_id"])
        self.assertEqual(normal["watchdog"]["inputHash"], source_watchdog["input_hash"])
        self.assertEqual(normal["watchdog"]["outputHash"], source_watchdog["output_hash"])

        self.assertEqual(observed["preview"]["phase"], "preview")
        self.assertEqual(observed["preview"]["preview"], {"before": 60, "after": 999})
        self.assertTrue(observed["preview"]["watchdog"]["ready"])

        blocked = observed["blocked"]
        self.assertEqual(blocked["phase"], "blocked")
        self.assertFalse(blocked["watchdog"]["ready"])
        self.assertEqual(blocked["watchdog"]["reason"], "RUNTIME_PREIMAGE_VALUE_MISMATCH")
        self.assertEqual(blocked["watchdog"]["processing"], "DATA_UNAVAILABLE")
        self.assertEqual(blocked["watchdog"]["engineering"], "NOT_EVALUATED")
        self.assertEqual(blocked["watchdog"]["assurance"], "HOLD")
        self.assertIsNone(blocked["watchdog"]["projection"])
        for key in ("resultId", "inputHash", "outputHash"):
            self.assertEqual(blocked["watchdog"][key], "—")
        self.assertTrue(blocked["tmrReady"])
        self.assertTrue(blocked["selReady"])
        self.assertEqual(blocked["radiationResidual"], residual)

        reset = observed["reset"]
        self.assertEqual(reset["phase"], "normal")
        self.assertEqual(reset["watchdog"], normal["watchdog"])
        self.assertEqual(reset["radiationResidual"], residual)
        self.assertEqual(JSON_PATH.read_bytes(), self.json_bytes)
        self.assertEqual(JAVASCRIPT_PATH.read_bytes(), self.javascript_bytes)

        visible_markup = re.sub(r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>", "", self.html, flags=re.I | re.S)
        self.assertNotIn('data-analysis-mode="attack"', visible_markup)
        self.assertNotIn('data-analysis-panel="attack"', visible_markup)
        self.assertNotIn("Assurance 공격", visible_markup)
        self.assertIn('data-step="4"', visible_markup)
        self.assertIn('data-view="4"', visible_markup)
        self.assertIn('04 · GCP 실행', visible_markup)
        self.assertIn('05 · 결과 전달 무결성', visible_markup)
        self.assertIn('id="attack-action"', visible_markup)
        self.assertIn('테스트용 숫자 바꾸기', visible_markup)
        self.assertIn('Core 결과가 전달 중 바뀌면 어떻게 할까요?', visible_markup)
        number_change = re.search(r'<section class="view" data-view="4".*?</section>', visible_markup, re.S)
        self.assertIsNotNone(number_change)
        beginner_surface = re.sub(r'<details class="attack-tech">.*?</details>', '', number_change.group(0), flags=re.S)
        for internal_term in ("결과 검증", "assurance attack", "consumer", "preimage", "sibling", "reason"):
            self.assertNotIn(internal_term, beginner_surface)
        self.assertNotIn("999", visible_markup)
        self.assertNotIn("WATCHDOG", visible_markup)
        self.assertNotIn("60초", visible_markup)
        self.assertNotIn("신뢰성 안전장치 4/4", visible_markup)
        for exact_copy in (
            "01 · Core 계산 결과", "02 · Product 도착 사본", "03 · 대조 결과",
            "Production MVP Core의 Residual SEU 기록과 도착 값을 대조한다.",
            "결과 전달 무결성 합성 시연 · 하드웨어 완화 구현 아님",
            "Core 기록과 대조", "정상 상태로 되돌리기",
        ):
            self.assertIn(exact_copy, self.html)
        for removed_runtime_control in ('data-analysis-mode="runtime"', 'data-runtime-method="WATCHDOG"', 'data-runtime-method="TMR"', 'data-runtime-method="SEL_PROTECTION"'):
            self.assertNotIn(removed_runtime_control, visible_markup)
        self.assertEqual(visible_markup.count("합성 데모 · 실제 보증 아님"), 1)
        self.assertEqual(visible_markup.count("현재 결론 HOLD"), 1)
        self.assertEqual(visible_markup.count("현재 연결된 실제 근거: 0건"), 1)
        self.assertEqual(visible_markup.count("승인 BOM 0건"), 1)
        self.assertNotIn("실제 추천 아님", visible_markup)
        self.assertNotIn("backend/network 없음", visible_markup)
        for h15_copy in (
            "합성 데모 · 실제 보증 아님", "현재 결론 HOLD", "현재 연결된 실제 근거: 0건",
            "방사선으로 메모리 정보가 뒤집힐 수 있음", "ECC는 SEU 사건 자체나 SEL·SEB·SEGR 같은 파괴성 SEE를 해결하지 않는다.",
            "확인된 것", "아직 필요한 것", "그래서 내린 결정", "실패나 불합격 아님",
        ):
            self.assertIn(h15_copy, self.html)
        self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))", self.html)
        self.assertIn(".causal-flow,.gap-action-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px", self.html)
        for exact_copy in ("다음", "실제 근거를 연결한 뒤 재검토", "환경 출력, 승인 BOM·시험 원문, 독립 검토를 채우면 같은 규칙으로 다시 판정한다."):
            self.assertIn(exact_copy, self.html)
        self.assertIn("font-variant-numeric:tabular-nums", self.html)

    def test_core_result_integrity_controller_uses_generated_variant_and_resets(self) -> None:
        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING,source=globalThis.SPECTRA_MVP_PRODUCT_RESULT;
const before=JSON.stringify(source),test=api.buildCoreIntegrityTestPayload(source);
const original=source.mvp_decision.variant.metrics.residual_logical_errors.value;
const changed=test.mvp_decision.variant.metrics.residual_logical_errors.value;
const normalized=JSON.parse(JSON.stringify(test)); normalized.mvp_decision.variant.metrics.residual_logical_errors.value=original;
const controller=api.createCoreIntegrityDemoController(source);
const normal=controller.current(),preview=controller.preview(),blocked=controller.verify(),reset=controller.reset();
process.stdout.write(JSON.stringify({{
  sourceUnchanged:before===JSON.stringify(source),onlyResidualChanged:JSON.stringify(normalized)===before,
  original,changed,hashesPreserved:test.mvp_decision.input_hash===source.mvp_decision.input_hash&&test.mvp_decision.output_hash===source.mvp_decision.output_hash,
  normal:{{phase:normal.phase,ready:normal.model.ready}},preview:{{phase:preview.phase,preview:preview.preview}},
  blocked:{{phase:blocked.phase,ready:blocked.model.ready,reason:blocked.model.reason,assurance:blocked.model.assurance}},
  reset:{{phase:reset.phase,ready:reset.model.ready,value:reset.model.selections['2-on'].residualSeu}}
}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        expected = self.payload["mvp_decision"]["variant"]["metrics"]["residual_logical_errors"]["value"]
        self.assertEqual(observed["original"], expected)
        self.assertNotEqual(observed["changed"], expected)
        self.assertTrue(observed["sourceUnchanged"])
        self.assertTrue(observed["onlyResidualChanged"])
        self.assertTrue(observed["hashesPreserved"])
        self.assertEqual(observed["normal"], {"phase": "normal", "ready": True})
        self.assertEqual(observed["preview"]["phase"], "preview")
        self.assertEqual(observed["preview"]["preview"]["before"], expected)
        self.assertEqual(observed["blocked"], {"phase": "blocked", "ready": False, "reason": "CORE_RESULT_VALUE_MISMATCH", "assurance": "HOLD"})
        self.assertEqual(observed["reset"], {"phase": "normal", "ready": True, "value": expected})

    def test_cross_runtime_canonical_number_parity(self) -> None:
        from spectra_sim.mvp_engine import _schema_errors

        controls = {
            "p_0_001": build_tmr_runtime_record(0.001, 2.998e-6),
            "below_1e_6": build_tmr_runtime_record(0.0005, 7.4975e-7),
            "above_1e_6": build_tmr_runtime_record(0.0006, 1.079568e-6),
            "one_e_7_family": build_tmr_runtime_record(0.0002, 1.19984e-7),
            "negative_zero": build_tmr_runtime_record(-0.0, 0.0),
        }
        for record in controls.values():
            result = record["result"]
            self.assertEqual(result["processing_status"], "VALID")
            self.assertEqual(_schema_errors(result, "mitigation-runtime-result.schema.json"), [])

        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const api=globalThis.SPECTRA_PRODUCT_BINDING;
const source=globalThis.SPECTRA_MVP_PRODUCT_RESULT;
const controls={json.dumps(controls, ensure_ascii=False, separators=(',', ':'))};
const observed={{}};
for (const [name,entry] of Object.entries(controls)) {{
  const payload=JSON.parse(JSON.stringify(source));
  payload.runtime_mitigation_results.TMR=entry;
  const model=api.resolveProductData(payload);
  const record=api.getRuntimeRecord(model,'TMR');
  observed[name]={{ready:record.ready,projection:record.projection,productionHash:entry.result.output_hash,browserHash:api.runtimePreimageHash(entry.integrity.output_hash_preimage),assurance:record.assurance}};
}}
process.stdout.write(JSON.stringify(observed));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        for name, source_record in controls.items():
            actual = observed[name]
            expected = source_record["result"]
            self.assertTrue(actual["ready"])
            self.assertEqual(actual["projection"], expected["computed_projection"])
            self.assertEqual(actual["productionHash"], expected["output_hash"])
            self.assertEqual(actual["browserHash"], expected["output_hash"])
            self.assertEqual(actual["assurance"], "HOLD")

        self.assertEqual(observed["p_0_001"]["projection"]["system_failure_probability"], 2.998e-6)
        self.assertLess(observed["below_1e_6"]["projection"]["system_failure_probability"], 1e-6)
        self.assertGreater(observed["above_1e_6"]["projection"]["system_failure_probability"], 1e-6)
        self.assertEqual(observed["one_e_7_family"]["projection"]["system_failure_probability"], 1.19984e-7)
        self.assertEqual(observed["negative_zero"]["projection"]["system_failure_probability"], 0.0)

    def test_product_five_step_gcp_and_integrity_navigation_executes(self) -> None:
        app_script = self.parser.inline[-1]
        harness = f"""
const vm=require('vm');
const makeClassList=()=>{{const values=new Set();return {{toggle(name,on){{if(on)values.add(name);else values.delete(name);}},contains(name){{return values.has(name);}}}};}};
const makeElement=(dataset={{}})=>({{dataset,listeners:{{}},children:[],classList:makeClassList(),textContent:'',disabled:false,style:{{}},tagName:'DIV',firstChild:{{textContent:''}},setAttribute(){{}},append(...nodes){{this.children.push(...nodes);}},appendChild(node){{this.children.push(node);}},replaceChildren(...nodes){{this.children=[...nodes];}},addEventListener(type,listener){{this.listeners[type]=listener;}}}});
const views=Array.from({{length:5}},(_,index)=>makeElement({{view:String(index)}}));
const steps=Array.from({{length:5}},(_,index)=>makeElement({{step:String(index)}}));
const nextButtons=Array.from({{length:4}},()=>makeElement());
const prevButtons=Array.from({{length:4}},()=>makeElement());
const analysisModes=[];
const analysisPanels=[makeElement({{analysisPanel:'radiation'}})];
const runtimeMethods=[];
const shieldButtons=['1','2','4','5'].map(shield=>makeElement({{shield}}));
const eccButtons=['off','on'].map(ecc=>makeElement({{ecc}}));
const selectors=new Map([
  ['[data-view]',views],['[data-step]',steps],['[data-next]',nextButtons],['[data-prev]',prevButtons],
  ['[data-analysis-mode]',analysisModes],['[data-analysis-panel]',analysisPanels],['[data-runtime-method]',runtimeMethods],
  ['[data-shield]',shieldButtons],['[data-ecc]',eccButtons]
]);
const singletons=new Map();
const one=selector=>{{if(!singletons.has(selector))singletons.set(selector,makeElement());return singletons.get(selector);}};
const documentListeners={{}},windowListeners={{}};
globalThis.document={{querySelectorAll(selector){{return selectors.get(selector)||[one(selector)];}},querySelector(selector){{const values=selectors.get(selector);return values?values[0]:one(selector);}},createElement(){{return makeElement();}},createTextNode(text){{const node=makeElement();node.textContent=text;return node;}},addEventListener(type,listener){{documentListeners[type]=listener;}}}};
globalThis.window={{addEventListener(type,listener){{windowListeners[type]=listener;}}}};
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(self.gcp_wrapper)});
vm.runInThisContext({json.dumps(app_script)});
const activeView=()=>views.findIndex(view=>view.classList.contains('active'));
const key=(key,extra={{}})=>documentListeners.keydown({{key,target:{{tagName:'DIV'}},preventDefault(){{}},...extra}});
const observed={{initial:activeView(),assuranceCardCount:one('[data-gap-actions]').children.length}};
shieldButtons[0].listeners.click();
observed.shield1={{
  tid:one('[data-tid]').textContent,
  residual:one('[data-residual]').textContent,
  eccFoot:one('[data-ecc-foot]').textContent,
  eccOffDisabled:eccButtons[0].disabled,
}};
shieldButtons[2].listeners.click();
observed.shield4={{
  tid:one('[data-tid]').textContent,
  residual:one('[data-residual]').textContent,
  eccFoot:one('[data-ecc-foot]').textContent,
  eccOffDisabled:eccButtons[0].disabled,
}};
shieldButtons[1].listeners.click();
eccButtons[0].listeners.click();
observed.shield2Off={{tid:one('[data-tid]').textContent,residual:one('[data-residual]').textContent,eccFoot:one('[data-ecc-foot]').textContent}};
eccButtons[1].listeners.click();
observed.shield2On={{tid:one('[data-tid]').textContent,residual:one('[data-residual]').textContent,eccFoot:one('[data-ecc-foot]').textContent}};
shieldButtons[3].listeners.click();
observed.shield5={{
  tid:one('[data-tid]').textContent,
  tidUnit:one('[data-tid-unit]').textContent,
  residual:one('[data-residual]').textContent,
  eccFoot:one('[data-ecc-foot]').textContent,
  processing:one('[data-processing]').textContent,
  engineering:one('[data-engineering]').textContent,
  assurance:one('[data-assurance]').textContent,
  eccOffDisabled:eccButtons[0].disabled,
}};
nextButtons[0].listeners.click();observed.afterNext1=activeView();
nextButtons[1].listeners.click();observed.afterNext2=activeView();
nextButtons[2].listeners.click();observed.afterNext3=activeView();
nextButtons[3].listeners.click();observed.afterNext4=activeView();
prevButtons[3].listeners.click();observed.afterPrev=activeView();
key('Home');observed.afterHome=activeView();
key('4');observed.afterFour=activeView();
key('5');observed.afterFive=activeView();
key('ArrowLeft',{{altKey:true}});observed.afterAltLeft=activeView();
key('End');observed.afterEnd=activeView();
const action=one('#attack-action');
observed.initialAction=action.textContent;
action.listeners.click();observed.previewAction=action.textContent;observed.previewValue=one('[data-attack-preview-value]').textContent;
action.listeners.click();observed.blockedAction=action.textContent;observed.blockedLabel=one('[data-attack-result-label]').textContent;observed.blockedValue=one('[data-attack-result-value]').textContent;observed.blockedState=one('[data-attack-result-state]').textContent;observed.reason=one('[data-attack-reason]').textContent;observed.hiddenIds=one('[data-attack-hidden-ids]').textContent;
action.listeners.click();observed.resetAction=action.textContent;observed.resetValue=one('[data-attack-normal-value]').textContent;
one('#reset').listeners.click();observed.afterReset=activeView();
process.stdout.write(JSON.stringify(observed));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        self.assertEqual(
            {key: observed[key] for key in ("initial", "afterNext1", "afterNext2", "afterNext3", "afterNext4", "afterPrev", "afterHome", "afterFour", "afterFive", "afterAltLeft", "afterEnd", "afterReset")},
            {"initial": 0, "afterNext1": 1, "afterNext2": 2, "afterNext3": 3, "afterNext4": 4, "afterPrev": 3, "afterHome": 0, "afterFour": 3, "afterFive": 4, "afterAltLeft": 3, "afterEnd": 4, "afterReset": 0},
        )
        self.assertEqual(observed["assuranceCardCount"], 4)
        self.assertEqual(observed["shield1"], {
            "tid": "8.0",
            "residual": "—",
            "eccFoot": "비교 가능한 ECC 정책 결과 없음 · 2 mm에서만 비교",
            "eccOffDisabled": True,
        })
        self.assertEqual(observed["shield4"], {
            "tid": "3.5",
            "residual": "—",
            "eccFoot": "비교 가능한 ECC 정책 결과 없음 · 2 mm에서만 비교",
            "eccOffDisabled": True,
        })
        self.assertEqual(observed["shield2Off"], {
            "tid": "6.0",
            "residual": "0.063072",
            "eccFoot": "BASELINE 결정 엔진 결과 · 실제 완화 성능 아님",
        })
        self.assertEqual(observed["shield2On"], {
            "tid": "6.0",
            "residual": "0.013072",
            "eccFoot": "VARIANT 결정 엔진 결과 · 실제 완화 성능 아님",
        })
        self.assertEqual(observed["shield5"], {
            "tid": "—",
            "tidUnit": "",
            "residual": "—",
            "eccFoot": "평가하지 않음 (NOT_EVALUATED) · 값 생성 안 함",
            "processing": "OUT_OF_MODEL_SCOPE",
            "engineering": "NOT_EVALUATED · 보증 아님",
            "assurance": "근거 부족으로 판단 보류 (HOLD)",
            "eccOffDisabled": True,
        })
        self.assertEqual(observed["initialAction"], "테스트용 숫자 바꾸기")
        self.assertEqual(observed["previewAction"], "Core 기록과 대조")
        self.assertEqual(observed["previewValue"], "0.013073")
        self.assertEqual(observed["blockedAction"], "정상 상태로 되돌리기")
        self.assertEqual(observed["blockedLabel"], "서로 다름")
        self.assertEqual(observed["blockedValue"], "불일치 → 숫자 비노출 → 판단 보류(HOLD)")
        self.assertIn("결과 사용 불가(DATA_UNAVAILABLE)", observed["blockedState"])
        self.assertIn("평가하지 않음(NOT_EVALUATED)", observed["blockedState"])
        self.assertEqual(observed["reason"], "CORE_RESULT_VALUE_MISMATCH")
        self.assertEqual(observed["hiddenIds"], "— / — / —")
        self.assertEqual(observed["resetAction"], "테스트용 숫자 바꾸기")
        self.assertEqual(observed["resetValue"], "0.013072")

    def test_javascript_syntax_and_no_remote_runtime_dependencies(self) -> None:
        runtime = node_path()
        subprocess.run([runtime, "--check", str(JAVASCRIPT_PATH)], check=True, capture_output=True, text=True)
        subprocess.run([runtime, "--check", str(GCP_JAVASCRIPT_PATH)], check=True, capture_output=True, text=True)
        with tempfile.TemporaryDirectory() as temp:
            for index, script in enumerate(self.parser.inline):
                script_path = Path(temp) / f"inline-{index}.js"
                script_path.write_text(script, encoding="utf-8")
                subprocess.run([runtime, "--check", str(script_path)], check=True, capture_output=True, text=True)
        combined = self.html + self.wrapper
        self.assertIsNone(re.search(r"https?://|//[^/]+\.(?:com|net|org)|\bfetch\s*\(|XMLHttpRequest|WebSocket", combined, re.I))
        self.assertNotIn("<link", self.html.lower())

    def test_gcp_beginner_surface_and_tone_contract(self) -> None:
        presentation = (ROOT / "demo/index.html").read_text(encoding="utf-8")
        combined = presentation + self.html
        for stale in ("GCP resource 0개", "GCP 리소스 0개", "GCP cost 0", "비용 0원", "멀티에이전트 미구현"):
            self.assertNotIn(stale, combined)
        for term in ("WORKFLOWS", "MISSION", "PARTS", "ASSURANCE", "STORAGE", "HOLD"):
            self.assertIn(term, presentation)
        self.assertNotIn("평가 비중 35점", presentation)
        for term in ("Mission Agent", "Parts Agent", "Assurance Agent", "최소권한"):
            self.assertIn(term, combined)
        gcp_slide = re.search(r'<section class="slide" data-title="GCP Multi-Agent".*?</section>', presentation, re.S).group(0)
        for exact_copy in (
            "세 Agent가 서로 다른 증거를 검증하고",
            "4. Parts 차단 예시",
            "5. Assurance 차단 예시",
            "1–3은 독립 확인된 저장 기록, 4–5는 역할을 설명하는 동작 예시입니다.",
            "검증된 고정 GCP 실행 기록 · SNAPSHOT / NOT LIVE",
        ):
            self.assertIn(exact_copy, gcp_slide)
        for hidden_value in (self.gcp_payload["workflow"]["revision"], *(item["id"] for item in self.gcp_payload["executions"].values())):
            self.assertNotIn(str(hidden_value), gcp_slide)
        self.assertEqual(len(re.findall(r'class="gcp-node state-valid"', gcp_slide)), 6)
        self.assertEqual(gcp_slide.count('class="demo-btn'), 5)
        self.assertIn('class="demo-pipeline-view simplified"', gcp_slide)
        self.assertNotRegex(presentation, r"\bfetch\s*\(")
        product_flow = re.search(r'<div class="gcp-workflow".*?</div>', self.html, re.S)
        self.assertIsNotNone(product_flow)
        self.assertEqual(product_flow.group(0).count("<article"), 6)
        self.assertEqual(len(re.findall(r'class="step(?: active)?"', self.html)), 5)
        self.assertEqual(len(re.findall(r'<section class="view(?: active)?"', self.html)), 5)
        self.assertIn("독립 확인된 저장 기록 · live 조회 아님", combined)
        self.assertIn("독립 확인된 합성 snapshot", self.html)
        self.assertIn("비용 ${costCopy}", self.html)
        self.assertNotIn("GCP REAL-TIME VERIFIED", presentation)

    def test_presentation_h05_scenarios_match_authoritative_snapshot(self) -> None:
        presentation = (ROOT / "demo/index.html").read_text(encoding="utf-8")
        embedded_match = re.search(
            r"globalThis\.SPECTRA_GCP_H05_SNAPSHOT\s*=\s*(\{.*?\n\s*\});",
            presentation,
            re.S,
        )
        self.assertIsNotNone(embedded_match)
        embedded = json.loads(embedded_match.group(1))
        self.assertEqual(
            embedded["executions"],
            self.gcp_payload["executions"],
        )
        self.assertEqual(
            re.findall(r'data-scenario="([^"]+)"', presentation),
            ["normal", "body_hash_forgery", "endpoint_override"],
        )
        self.assertEqual(
            re.findall(r'data-design-scenario="([^"]+)"', presentation),
            ["parts_block", "assurance_block"],
        )
        for exact_copy in (
            "INPUT_BODY_SHA256_MISMATCH",
            "Core / Parts / Assurance 미호출",
            "ENDPOINT_OVERRIDE_FORBIDDEN",
            "Agent 호출 0회",
            "1–3은 독립 확인된 저장 기록, 4–5는 역할을 설명하는 동작 예시입니다.",
            "모든 버튼은 새 Workflow를 시작하지 않습니다.",
        ):
            self.assertIn(exact_copy, presentation)
        for stale_copy in (
            "8677c107-84c7-4f09-9f94-2ac061db798f",
            "mission_fail",
            "parts_fail",
            "assurance_fail",
            "VERIFIED GCP EXECUTION",
            "HOLD → PASS 강제 위조 시도",
        ):
            self.assertNotIn(stale_copy, presentation)

        audience_html = presentation + self.html
        audience_html = re.sub(r"<(?:script|style)\b.*?</(?:script|style)>", " ", audience_html, flags=re.S | re.I)
        audience_text = re.sub(r"<[^>]+>", " ", audience_html)
        self.assertNotRegex(audience_text, r"\bH\d{1,2}\b")
        for internal_label in ("Control Tower", "READY_FOR_REVIEW", "Workstream"):
            self.assertNotIn(internal_label, audience_text)

    def test_presentation_feedback_structure_and_scope_contract(self) -> None:
        presentation = (ROOT / "demo/index.html").read_text(encoding="utf-8")
        for inserted_copy in (
            '03 · COTS ADOPTION &amp; RADIATION UNCERTAINTY',
            '우주급 부품 (Rad-Hard)',
            '상용 기성 부품 (COTS · EX-100)',
            'Commercial availability',
            'Evidence gap',
            'Mission-specific verification',
            '정성적 검토 구조 · 외부 가격·납기·성능 수치를 사용하지 않음',
            'NOT_EVALUATED / HOLD',
            '04 · WHY SHIELDING MATTERS',
            '왜 방사선을 차폐하고,<br><span class="accent">1·4·5 mm는 무엇을 의미하는가.',
            '05 · TARGET MISSION &amp; COMPONENT EVIDENCE',
            'LEO SSO 550 km 궤도 조건과 COTS SRAM 부품을 정의하고',
        ):
            self.assertIn(inserted_copy, presentation)
        cots_at = presentation.index('03 · COTS ADOPTION')
        primer_at = presentation.index('04 · WHY SHIELDING')
        mission_at = presentation.index('05 · TARGET MISSION')
        self.assertLess(cots_at, primer_at)
        self.assertLess(primer_at, mission_at)
        self.assertIn('class="evidence-ring"', presentation)
        self.assertIn('class="glossary-bar"', presentation)
        self.assertIn('기계 검증형 데이터 규칙', presentation)
        self.assertIn('SEU MITIGATION MODEL · 2 mm Al FIXED', presentation)
        self.assertNotIn('시뮬레이션의 계산된 낙관주의보다', presentation)
        self.assertNotIn('시험 성적서로 검증된 확실한 판단', presentation)
        self.assertNotIn('비행 승인', presentation)
        self.assertNotIn('SPECTRA IS', presentation)
        for immutable in (
            "sim-d5a72077d684f459", "sim-3cc00f2c824db56d", "sim-ddf29f8ab807196d",
            "sim-27e031f2388ab6fc",
            "OUT_OF_MODEL_SCOPE", "SYNTHETIC", "HOLD",
        ):
            self.assertIn(immutable, presentation)
        self.assertNotIn("0.0063072", presentation + self.html)
        self.assertEqual(re.findall(r'<script src="([^"]+)"', presentation), [])
        self.assertIn("globalThis.SPECTRA_MVP_PRODUCT_RESULT", presentation)
        self.assertIn("globalThis.SPECTRA_GCP_H05_SNAPSHOT", presentation)
        for cover_copy in (
            "SPECTRA", "Space", "Parts", "Evidence", "Component", "Traceability", "Radiation", "Assurance",
            "우주 부품 증거 · 소자 추적성 · 방사선 보증", "데이터 무결성으로 방사선 판단 근거를",
            "SYNTHETIC DEMO · ACTUAL EVIDENCE 0 · FINAL HOLD",
        ):
            self.assertIn(cover_copy, presentation)
        self.assertNotIn("궤도 방사선 신뢰성을", presentation)
        cots_slide = re.search(r'<section class="slide" data-title="COTS 비교".*?</section>', presentation, re.S).group(0)
        for unsupported_comparison in (
            "수억 원", "12~24개월", "98% 절감", "수십 배 고성능", "100% 면역",
            "100 krad", "5~25 krad", "$1,000", "$1k",
        ):
            self.assertNotIn(unsupported_comparison, cots_slide)
        self.assertEqual(len(re.findall(r'<section class="slide(?: [^"]*)?"', presentation)), 13)
        self.assertIn('href="roadmap-lab.html"', presentation)
        self.assertIn('40초 제품 흐름 열기 ↗', presentation)
        self.assertIn("String(slides.length - 2).padStart(2,'0')", presentation)
        self.assertIn("@keyframes slide-enter", presentation)
        self.assertIn("animation:slide-enter", presentation)
        self.assertIn("@media(prefers-reduced-motion:reduce)", presentation)

    def test_presentation_fixed_wheel_intent_and_navigation_execute(self) -> None:
        presentation = (ROOT / "demo/index.html").read_text(encoding="utf-8")
        self.assertNotIn("scroll-snap", presentation)
        self.assertIn(".js .slide{display:none}", presentation)
        self.assertIn(".js .slide.active{display:grid;animation:slide-enter", presentation)
        self.assertIn("createWheelIntentController", presentation)
        self.assertNotIn("setTimeout", presentation)
        self.assertNotIn("clearTimeout", presentation)
        self.assertNotRegex(presentation, r"addEventListener\(['\"]pointermove['\"]")
        parser = ScriptParser()
        parser.feed(presentation)
        deck_script = parser.inline[-1]
        harness = f"""
const vm=require('vm');
const makeClassList=()=>{{const values=new Set();return {{toggle(name,on){{if(on)values.add(name);else values.delete(name);}},add(name){{values.add(name);}},remove(name){{values.delete(name);}}}};}};
const makeElement=(id='')=>({{id,dataset:{{}},children:[],listeners:{{}},className:'',textContent:'',innerHTML:'',href:'',disabled:false,style:{{}},classList:makeClassList(),setAttribute(){{}},appendChild(child){{this.children.push(child);}},addEventListener(type,listener){{this.listeners[type]=listener;}},querySelector(){{return makeElement();}}}});
const requiredIds=['progress','count','prev','next','shield-controls','tid-card','tid-value','tid-unit','tid-note','scope-status','scope-detail','ecc-controls','raw-value','residual-value','residual-bar','ecc-run','gcp-console-btn','scenario-buttons-group','demo-input-view','badge-mission','badge-parts','badge-assurance','demo-status-text','demo-decision-badge','demo-reason-text','demo-failclosed-alert','live-status-pill','live-exec-id','live-time-text','node-01','node-02','node-03','node-04','node-05','node-06'];
const ids=Object.fromEntries(requiredIds.map(id=>[id,makeElement(id)]));
const mockSlides=Array.from({{length:13}},(_,index)=>{{const slide=makeElement(`slide-${{index}}`);slide.dataset.title=index===0?'시작':index===12?'질의응답':`slide-${{index}}`;return slide;}});
const documentListeners={{}};
globalThis.document={{body:makeElement('body'),querySelectorAll(selector){{return selector==='.slide'?mockSlides:[];}},querySelector(selector){{return selector==='.count'?ids.count:null;}},getElementById(id){{return ids[id];}},createElement(){{return makeElement();}},addEventListener(type,listener){{documentListeners[type]=listener;}}}};
globalThis.window={{scrollTo(){{}}}};
vm.runInThisContext({json.dumps(self.wrapper)});
vm.runInThisContext({json.dumps(deck_script)});
const observedSnapshots=vm.runInThisContext('snapshots');
const observedCore=vm.runInThisContext('coreEcc');
const current=()=>vm.runInThisContext('index');
const key=key=>documentListeners.keydown({{key,preventDefault(){{}}}});
let prevented=0;
const wheel=(deltaY,timeStamp,deltaMode=0)=>documentListeners.wheel({{deltaY,deltaMode,timeStamp,clientX:640,clientY:360,preventDefault(){{prevented+=1;}}}});
key('Home');let at=0;const forward=[];for(let step=0;step<7;step+=1){{at+=200;wheel(3,at,1);forward.push(current());}}
const reverse=[];for(let step=0;step<7;step+=1){{at+=200;wheel(-3,at,1);reverse.push(current());}}
key('Home');at+=200;wheel(48,at);for(const tail of [42,35,28,22,16,11,8,5,3,2,-2]){{at+=90;wheel(tail,at);}}
const afterLongInertia=current();
at+=100;wheel(60,at);const afterNextIntent=current();
ids.next.listeners.click();
const afterNext=current();
ids.prev.listeners.click();
const afterPrev=current();
key('ArrowRight');const afterArrowRight=current();
key('PageDown');const afterPageDown=current();
key(' ');const afterSpace=current();
key('ArrowLeft');const afterArrowLeft=current();
key('PageUp');const afterPageUp=current();
key('Home');key('ArrowLeft');const firstClamp=current();
key('End');key('PageDown');const lastClamp=current();
process.stdout.write(JSON.stringify({{forward,reverse,afterLongInertia,afterNextIntent,afterNext,afterPrev,afterArrowRight,afterPageDown,afterSpace,afterArrowLeft,afterPageUp,firstClamp,lastClamp,prevented,hasWheelListener:Object.hasOwn(documentListeners,'wheel'),hasPointerListener:Object.hasOwn(documentListeners,'pointermove'),snapshots:observedSnapshots,core:observedCore,rendered:{{raw:ids['raw-value'].textContent,residual:ids['residual-value'].textContent}}}}));
"""
        completed = subprocess.run([node_path(), "-e", harness], check=True, capture_output=True, text=True)
        observed = json.loads(completed.stdout)
        self.assertEqual(
            observed.pop("snapshots"),
            {
                "shield": {
                    "1": {"tid": "8.0", "required": "16.0", "status": "VALID", "run": "sim-d5a72077d684f459"},
                    "2": {"tid": "6.0", "required": "12.0", "status": "VALID", "run": "sim-3cc00f2c824db56d"},
                    "4": {"tid": "3.5", "required": "7.0", "status": "VALID", "run": "sim-ddf29f8ab807196d"},
                    "5": {"tid": None, "required": None, "status": "OUT_OF_MODEL_SCOPE", "run": "sim-27e031f2388ab6fc"},
                },
            },
        )
        core = observed.pop("core")
        rendered = observed.pop("rendered")
        mvp = self.payload["mvp_decision"]
        self.assertEqual(core["raw"], mvp["variant"]["metrics"]["raw_seu"]["value"])
        self.assertEqual(float(core["on"]["residual"]), mvp["variant"]["metrics"]["residual_logical_errors"]["value"])
        self.assertEqual(float(core["off"]["residual"]), mvp["baseline"]["metrics"]["residual_logical_errors"]["value"])
        self.assertEqual(rendered, {"raw": "0.063072", "residual": "0.063072"})
        self.assertEqual(
            observed,
            {
                "forward": [1, 2, 3, 4, 5, 6, 7],
                "reverse": [6, 5, 4, 3, 2, 1, 0],
                "afterLongInertia": 1,
                "afterNextIntent": 2,
                "afterNext": 3,
                "afterPrev": 2,
                "afterArrowRight": 3,
                "afterPageDown": 4,
                "afterSpace": 5,
                "afterArrowLeft": 4,
                "afterPageUp": 3,
                "firstClamp": 0,
                "lastClamp": 12,
                "prevented": 27,
                "hasWheelListener": True,
                "hasPointerListener": False,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
