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

spec = importlib.util.spec_from_file_location("build_product_data", EXPORTER_PATH)
exporter = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(exporter)


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
        cls.payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        cls.wrapper = JAVASCRIPT_PATH.read_text(encoding="utf-8")
        cls.parser = ScriptParser()
        cls.parser.feed(cls.html)

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
        self.assertEqual(self.parser.sources, ["data/mvp-product-result.js"])
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
  return [method,{{ready:record.ready,processing:record.processing,engineering:record.engineering,assurance:record.assurance,dataClass:record.dataClass,resultId:record.resultId,equationId:record.equationId,inputHash:record.inputHash,outputHash:record.outputHash,projection:record.projection,policy:record.policy,codes:record.codes,metrics:api.runtimeDisplayMetrics(record)}}];
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

    def test_javascript_syntax_and_no_remote_runtime_dependencies(self) -> None:
        runtime = node_path()
        subprocess.run([runtime, "--check", str(JAVASCRIPT_PATH)], check=True, capture_output=True, text=True)
        with tempfile.TemporaryDirectory() as temp:
            for index, script in enumerate(self.parser.inline):
                script_path = Path(temp) / f"inline-{index}.js"
                script_path.write_text(script, encoding="utf-8")
                subprocess.run([runtime, "--check", str(script_path)], check=True, capture_output=True, text=True)
        combined = self.html + self.wrapper
        self.assertIsNone(re.search(r"https?://|//[^/]+\.(?:com|net|org)|\bfetch\s*\(|XMLHttpRequest|WebSocket", combined, re.I))
        self.assertNotIn("<link", self.html.lower())

    def test_presentation_note_has_scoped_desktop_width_override(self) -> None:
        presentation = (ROOT / "demo/index.html").read_text(encoding="utf-8")
        self.assertIn('class="lead slide4-note">합성 `SEL`은 정책 경로용 placeholder입니다.', presentation)
        self.assertIn('.slide2-note,.slide4-note{max-width:none;white-space:nowrap}', presentation)
        self.assertIn('.slide2-note,.slide4-note{white-space:normal}', presentation)
        digest = hashlib.sha256(presentation.encode("utf-8")).hexdigest()
        self.assertEqual(digest, "96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5")


if __name__ == "__main__":
    unittest.main(verbosity=2)
