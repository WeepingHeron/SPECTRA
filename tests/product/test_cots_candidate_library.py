import copy
import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "cots-candidate-library.html"
SAMPLE = ROOT / "demo" / "data" / "cots-candidate-registry-synthetic.json"

def run_node(operation, value):
    program = r'''
const fs=require("fs"),vm=require("vm"),html=fs.readFileSync(process.argv[1],"utf8"),scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if(scripts.length!==1)throw new Error("one inline script required");vm.runInThisContext(scripts[0][1],{filename:"cots-candidate-inline.js"});
const api=globalThis.SPECTRA_COTS_CANDIDATE_LIBRARY,input=JSON.parse(fs.readFileSync(0,"utf8"));let result;
if(process.argv[2]==="resolve")result=api.resolve(input);else if(process.argv[2]==="parse")result=api.parse(input.text);else if(process.argv[2]==="demo")result={sample:api.SAMPLE,model:api.resolve(api.SAMPLE)};else if(process.argv[2]==="export")result=JSON.parse(api.serialize(api.resolve(input)));else throw new Error("unknown op");process.stdout.write(JSON.stringify(result));
'''
    done = subprocess.run(["node", "-e", program, str(HTML), operation], input=json.dumps(value), text=True, capture_output=True, check=True, cwd=ROOT)
    return json.loads(done.stdout)

class CotsCandidateLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def assert_closed(self, model, reason=None):
        self.assertFalse(model["ready"])
        if reason: self.assertEqual(model["reason_code"], reason)
        self.assertEqual(model["records"], [])
        self.assertEqual(model["decision"]["assurance_decision"], "HOLD")
        self.assertEqual(model["decision"]["engineering_gate"], "NOT_EVALUATED")

    def test_demo_matches_fixture_and_all_records_are_decision_ineligible(self):
        demo = run_node("demo", {})
        self.assertEqual(demo["sample"], self.sample)
        self.assertTrue(demo["model"]["ready"])
        for record in demo["model"]["records"]:
            self.assertEqual(record["record_purpose"], "DISCOVERY_CANDIDATE")
            self.assertEqual(record["identity_status"], "PARTIAL_UNRESOLVED")
            self.assertFalse(record["used_for_decision"])
            self.assertEqual(record["applicability_status"], "NOT_EVALUATED")
            self.assertEqual(record["assurance_decision"], "HOLD")

    def test_exact_catalog_candidate_is_not_bom_exact_match(self):
        catalog = run_node("resolve", self.sample)["records"][0]
        self.assertEqual(catalog["part_number"], "5962L1420901VXC")
        self.assertEqual(catalog["identity_status"], "PARTIAL_UNRESOLVED")
        self.assertIn("BOM_APPROVAL_MISSING", [b["stable_code"] for b in catalog["blockers"]])

    def test_tid_conflict_and_sel_test_limits_are_kept_separate(self):
        records = {r["source_identity"]: r for r in run_node("resolve", self.sample)["records"]}
        tid = {e["event_type"]: e["status"] for e in records["SLLK019"]["coverage"]}
        sel = {e["event_type"]: e["status"] for e in records["SLLA381"]["coverage"]}
        self.assertEqual(tid["TID"], "REPORTED_WITH_CONFLICTS")
        self.assertEqual(sel["SEL"], "ZERO_EVENTS_WITH_TEST_LIMITS")
        self.assertEqual(sel["SEB"], "EVIDENCE_MISSING")
        self.assertEqual(sel["SEGR"], "EVIDENCE_MISSING")

    def test_malformed_and_nested_shape_attacks_fail_closed(self):
        self.assert_closed(run_node("parse", {"text": "{bad"}), "MALFORMED_JSON")
        attack = copy.deepcopy(self.sample); attack["records"][0]["coverage"] = {}
        self.assert_closed(run_node("resolve", attack), "COVERAGE_SHAPE_INVALID")

    def test_actual_approved_exact_match_and_pass_promotions_fail_closed(self):
        for field, value in [("data_class", "ACTUAL")]:
            attack = copy.deepcopy(self.sample); attack[field] = value
            self.assert_closed(run_node("resolve", attack), "UNAUTHENTICATED_PROMOTION")
        mutations = [("record_purpose", "APPROVED"), ("identity_status", "EXACT_MATCH"), ("assurance_decision", "PASS"), ("used_for_decision", True)]
        for field, value in mutations:
            attack = copy.deepcopy(self.sample); attack["records"][0][field] = value
            self.assert_closed(run_node("resolve", attack), "OPTIMISTIC_RECORD_REJECTED")

    def test_suitability_and_approval_identity_injection_is_redacted(self):
        attack = copy.deepcopy(self.sample)
        attack["records"][0]["suitability"] = "FLIGHT_APPROVED"
        attack["records"][0]["approver"] = "Jane Doe"
        model = run_node("resolve", attack)
        self.assert_closed(model, "RECORD_SHAPE_INVALID")
        serialized = json.dumps(model)
        self.assertNotIn("FLIGHT_APPROVED", serialized)
        self.assertNotIn("Jane Doe", serialized)

    def test_family_only_substitution_fails_closed(self):
        attack = copy.deepcopy(self.sample)
        attack["records"][0]["identity_status"] = "FAMILY_ONLY"
        attack["records"][0]["part_number"] = "SN55HVD233-family"
        self.assert_closed(run_node("resolve", attack), "OPTIMISTIC_RECORD_REJECTED")

    def test_seu_cannot_substitute_for_sel_or_other_destructive_see(self):
        for target in ("SEL", "SEB", "SEGR"):
            attack = copy.deepcopy(self.sample)
            event = next(e for e in attack["records"][2]["coverage"] if e["event_type"] == target)
            event["status"] = "ZERO_EVENTS_WITH_TEST_LIMITS"
            event["source_event_type"] = "SEU"
            self.assert_closed(run_node("resolve", attack), "EVIDENCE_TYPE_SUBSTITUTION")

    def test_duplicate_record_and_incomplete_event_coverage_fail_closed(self):
        duplicate = copy.deepcopy(self.sample); duplicate["records"][1]["record_id"] = duplicate["records"][0]["record_id"]
        self.assert_closed(run_node("resolve", duplicate), "RECORD_ID_INVALID")
        missing = copy.deepcopy(self.sample); missing["records"][0]["coverage"].pop()
        self.assert_closed(run_node("resolve", missing), "COVERAGE_SHAPE_INVALID")

    def test_allowlist_export_has_no_pdf_locator_numbers_or_decision_claim(self):
        exported = run_node("export", self.sample); serialized = json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")
        self.assertTrue(all(record["used_for_decision"] is False for record in exported["records"]))
        for forbidden in ["record_id", "manufacturer", "part_number", "source_identity", "next_action_ko", "http", ".pdf", "lot", "date_code", "approver", "suitability", "5962l1420901vxc", "sllk019", "slla381"]:
            self.assertNotIn(forbidden, serialized.lower())

    def test_failed_export_redacts_attacker_values(self):
        exported = run_node("export", {"suitability": "secret-flight-pass"})
        self.assertEqual(exported["records"], [])
        self.assertNotIn("secret-flight-pass", json.dumps(exported))

    def test_offline_runtime_filter_controls_and_javascript_syntax(self):
        lowered = self.html.lower()
        self.assertNotRegex(lowered, r"https?://|//cdn|<script[^>]+src=|fetch\s*\(|xmlhttprequest|websocket|sendbeacon")
        self.assertEqual(len(re.findall(r'<button class="filter(?: active)?"', self.html)), 3)
        self.assertIn('type="file"', self.html)
        self.assertNotIn("localStorage", self.html)
        scripts = re.findall(r"<script>([\s\S]*?)</script>", self.html)
        done = subprocess.run(["node", "--check", "-"], input=scripts[0], text=True, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stderr)

if __name__ == "__main__": unittest.main()
