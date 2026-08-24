import copy
import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "cad-linkage-readiness.html"
SAMPLE = ROOT / "demo" / "data" / "cad-linkage-readiness-synthetic.json"

def run_node(operation, value):
    program = r'''
const fs=require("fs"),vm=require("vm"),html=fs.readFileSync(process.argv[1],"utf8"),scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if(scripts.length!==1)throw new Error("one inline script required");vm.runInThisContext(scripts[0][1],{filename:"cad-linkage-inline.js"});const api=globalThis.SPECTRA_CAD_LINKAGE_READINESS,input=JSON.parse(fs.readFileSync(0,"utf8"));let result;
if(process.argv[2]==="resolve")result=api.resolve(input);else if(process.argv[2]==="parse")result=api.parse(input.text);else if(process.argv[2]==="demo")result={sample:api.SAMPLE,model:api.resolve(api.SAMPLE)};else if(process.argv[2]==="export")result=JSON.parse(api.serialize(api.resolve(input)));else throw new Error("unknown op");process.stdout.write(JSON.stringify(result));
'''
    done = subprocess.run(["node", "-e", program, str(HTML), operation], input=json.dumps(value), text=True, capture_output=True, check=True, cwd=ROOT)
    return json.loads(done.stdout)

class CadLinkageReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def assert_closed(self, model, reason=None):
        self.assertFalse(model["ready"])
        if reason: self.assertEqual(model["reason_code"], reason)
        self.assertEqual(model["gates"], [])
        self.assertEqual(model["output"], {"computed_dose_status": "NOT_COMPUTED", "scientific_evidence_status": "NOT_ESTABLISHED"})
        self.assertEqual(model["decision"]["engineering_gate"], "NOT_EVALUATED")
        self.assertEqual(model["decision"]["assurance_decision"], "HOLD")
        self.assertFalse(model["decision"]["used_for_decision"])

    def test_bundled_sample_matches_fixture_and_all_six_gates_are_not_ready(self):
        demo = run_node("demo", {})
        self.assertEqual(demo["sample"], self.sample)
        self.assertTrue(demo["model"]["ready"])
        self.assertEqual(len(demo["model"]["gates"]), 6)
        self.assertTrue(all(g["readiness_status"] == "NOT_READY" for g in demo["model"]["gates"]))
        self.assertEqual(demo["model"]["output"]["computed_dose_status"], "NOT_COMPUTED")
        self.assertEqual(demo["model"]["decision"]["assurance_decision"], "HOLD")

    def test_required_linkage_axes_and_owner_actions_are_visible(self):
        model = run_node("resolve", self.sample)
        self.assertEqual([g["gate_id"] for g in model["gates"]], [
            "GEOMETRY_SOURCE", "REVISION_HASH", "COORDINATE_UNIT", "COMPONENT_POSITION_BINDING", "MATERIAL_THICKNESS_MAPPING", "ENVIRONMENT_MODEL_REVISION_BINDING"
        ])
        self.assertTrue(all(g["blocker"]["owner_role"] for g in model["gates"]))
        self.assertTrue(all(g["blocker"]["next_action_code"] for g in model["gates"]))

    def test_malformed_and_missing_revision_or_hash_fail_closed(self):
        self.assert_closed(run_node("parse", {"text": "{bad"}), "MALFORMED_JSON")
        for field in ("approved_revision_status", "artifact_hash_status"):
            attack = copy.deepcopy(self.sample); del attack["geometry"][field]
            self.assert_closed(run_node("resolve", attack), "GEOMETRY_IDENTITY_SHAPE_INVALID")

    def test_actual_ready_and_pass_self_promotions_fail_closed(self):
        actual = copy.deepcopy(self.sample); actual["data_class"] = "ACTUAL"
        self.assert_closed(run_node("resolve", actual), "UNAUTHENTICATED_ACTUAL_PROMOTION")
        geometry = copy.deepcopy(self.sample); geometry["geometry"]["source_status"] = "READY"
        self.assert_closed(run_node("resolve", geometry), "OPTIMISTIC_GEOMETRY_PROMOTION_REJECTED")
        linkage = copy.deepcopy(self.sample); linkage["linkages"][0]["readiness_status"] = "READY"
        self.assert_closed(run_node("resolve", linkage), "OPTIMISTIC_LINKAGE_PROMOTION_REJECTED")
        decision = copy.deepcopy(self.sample); decision["decision"]["assurance_decision"] = "PASS"
        self.assert_closed(run_node("resolve", decision), "OPTIMISTIC_DECISION_REJECTED")

    def test_unit_or_coordinate_match_without_evidence_is_rejected(self):
        for field in ("coordinate_system_status", "unit_status"):
            attack = copy.deepcopy(self.sample); attack["coordinate_binding"][field] = "MATCH"
            self.assert_closed(run_node("resolve", attack), "COORDINATE_UNIT_PROMOTION_REJECTED")

    def test_geometry_cannot_be_promoted_to_shielding_scientific_evidence(self):
        attack = copy.deepcopy(self.sample)
        attack["output"]["scientific_evidence_status"] = "ESTABLISHED_FROM_GEOMETRY"
        self.assert_closed(run_node("resolve", attack), "OUTPUT_PROMOTION_REJECTED")

    def test_dose_value_insertion_is_hidden_and_fails_closed(self):
        for location in ("root", "output"):
            attack = copy.deepcopy(self.sample)
            if location == "root": attack["dose_krad"] = 8
            else: attack["output"]["computed_dose"] = {"value": 8, "unit": "krad"}
            model = run_node("resolve", attack)
            self.assert_closed(model)
            self.assertNotIn("dose_krad", json.dumps(model))
            self.assertNotIn('"value": 8', json.dumps(model))

    def test_duplicate_or_missing_linkage_gate_fails_closed(self):
        duplicate = copy.deepcopy(self.sample); duplicate["linkages"][1]["gate_id"] = duplicate["linkages"][0]["gate_id"]
        self.assert_closed(run_node("resolve", duplicate), "LINKAGE_GATE_INVALID")
        missing = copy.deepcopy(self.sample); missing["linkages"].pop()
        self.assert_closed(run_node("resolve", missing), "LINKAGES_SHAPE_INVALID")

    def test_allowlist_export_contains_no_geometry_values_or_dose(self):
        exported = run_node("export", self.sample); serialized = json.dumps(exported, ensure_ascii=False).lower()
        self.assertEqual(exported["output"]["computed_dose_status"], "NOT_COMPUTED")
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")
        for forbidden in ["artifact_hash", "revision_id", "coordinate_value", "thickness_value", "environment_value", "dose_krad", '"value"']:
            self.assertNotIn(forbidden, serialized)

    def test_failed_export_redacts_attacker_values(self):
        exported = run_node("export", {"geometry_path": "/Users/private/cad.step", "dose": 8})
        serialized = json.dumps(exported)
        self.assertEqual(exported["gates"], [])
        self.assertNotIn("/Users/", serialized)
        self.assertNotIn('"dose": 8', serialized)

    def test_offline_runtime_static_boundary_and_javascript_syntax(self):
        lowered = self.html.lower()
        self.assertNotRegex(lowered, r"https?://|//cdn|<script[^>]+src=|fetch\s*\(|xmlhttprequest|websocket|sendbeacon")
        self.assertIn('type="file"', self.html)
        self.assertIn("CAD parser·3D shielding 계산·과학 검증이 아니라", self.html)
        self.assertNotIn("localStorage", self.html)
        scripts = re.findall(r"<script>([\s\S]*?)</script>", self.html)
        done = subprocess.run(["node", "--check", "-"], input=scripts[0], text=True, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stderr)

if __name__ == "__main__": unittest.main()
