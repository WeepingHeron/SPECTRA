import copy
import json
import pathlib
import re
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "evidence-intake.html"
SAMPLE = ROOT / "demo" / "data" / "evidence-source-readiness-synthetic.json"


def run_node(operation, value):
    program = r'''
const fs=require("fs"),vm=require("vm");
const html=fs.readFileSync(process.argv[1],"utf8");
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if(scripts.length!==1)throw new Error("expected one inline script");
vm.runInThisContext(scripts[0][1],{filename:"evidence-intake-inline.js"});
const api=globalThis.SPECTRA_EVIDENCE_SOURCE_INTAKE;
const input=JSON.parse(fs.readFileSync(0,"utf8")); let result;
if(process.argv[2]==="resolve")result=api.resolve(input);
else if(process.argv[2]==="parse")result=api.parse(input.text);
else if(process.argv[2]==="demo")result={sample:api.DEMO_SAMPLE,model:api.resolve(api.DEMO_SAMPLE)};
else if(process.argv[2]==="export")result=JSON.parse(api.serialize(api.resolve(input)));
else throw new Error("unknown operation");
process.stdout.write(JSON.stringify(result));
'''
    completed = subprocess.run(
        ["node", "-e", program, str(HTML), operation],
        input=json.dumps(value), text=True, capture_output=True, check=True, cwd=ROOT,
    )
    return json.loads(completed.stdout)


class EvidenceSourceIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def assert_fail_closed(self, model, reason=None):
        self.assertFalse(model["ready"])
        if reason:
            self.assertEqual(model["reason_code"], reason)
        self.assertEqual(model["sources"], [])
        self.assertEqual(model["decision"], {
            "processing_status": "DATA_UNAVAILABLE",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
        })

    def test_bundled_sample_exactly_matches_fixture_and_holds(self):
        demo = run_node("demo", {})
        self.assertEqual(demo["sample"], self.sample)
        self.assertTrue(demo["model"]["ready"])
        self.assertEqual([s["source_id"] for s in demo["model"]["sources"]], ["SPENVIS", "NASA_PUBLIC_DB", "COTS_EVIDENCE_LIBRARY"])
        self.assertTrue(all(s["connector_status"] == "CONNECTOR_NOT_READY" for s in demo["model"]["sources"]))
        self.assertEqual(demo["model"]["decision"]["assurance_decision"], "HOLD")

    def test_spenvis_requires_job_reference_rights_manifest_and_provenance(self):
        spenvis = run_node("resolve", self.sample)["sources"][0]
        self.assertEqual(spenvis["requirements"], {
            "provider_job_reference": "MISSING", "rights": "UNRESOLVED", "raw_manifest": "MISSING", "provenance": "NOT_VERIFIED"
        })
        self.assertEqual(spenvis["blockers"][0]["owner_role"], "ENVIRONMENT_EVIDENCE_OWNER")

    def test_nasa_and_cots_require_exact_locator_rights_and_provenance(self):
        sources = {s["source_id"]: s for s in run_node("resolve", self.sample)["sources"]}
        for source_id in ("NASA_PUBLIC_DB", "COTS_EVIDENCE_LIBRARY"):
            self.assertEqual(sources[source_id]["requirements"], {"exact_locator": "MISSING", "rights": "UNRESOLVED", "provenance": "NOT_VERIFIED"})

    def test_malformed_json_and_nested_shapes_fail_closed(self):
        self.assert_fail_closed(run_node("parse", {"text": "{broken"}), "MALFORMED_JSON")
        attack = copy.deepcopy(self.sample)
        attack["sources"][0]["requirements"] = []
        self.assert_fail_closed(run_node("resolve", attack), "REQUIREMENTS_INVALID")

    def test_actual_promotion_and_live_connector_claim_fail_closed(self):
        actual = copy.deepcopy(self.sample)
        actual["data_class"] = "ACTUAL"
        model = run_node("resolve", actual)
        self.assert_fail_closed(model, "UNAUTHENTICATED_ACTUAL_PROMOTION")

        live = copy.deepcopy(self.sample)
        live["sources"][0]["connector_status"] = "READY"
        model = run_node("resolve", live)
        self.assert_fail_closed(model, "OPTIMISTIC_CONNECTOR_STATUS_REJECTED")

        injected = copy.deepcopy(self.sample)
        injected["secret_locator"] = "https://private.example/record"
        injected["sources"][0]["provider_token"] = "secret-token"
        model = run_node("resolve", injected)
        self.assert_fail_closed(model, "INTAKE_SHAPE_INVALID")
        self.assertNotIn("private.example", json.dumps(model))
        self.assertNotIn("secret-token", json.dumps(model))

    def test_optimistic_decision_and_pass_blocker_fail_closed(self):
        optimistic = copy.deepcopy(self.sample)
        optimistic["decision"]["assurance_decision"] = "PASS"
        self.assert_fail_closed(run_node("resolve", optimistic), "OPTIMISTIC_DECISION_REJECTED")

        blocker = copy.deepcopy(self.sample)
        blocker["sources"][0]["blockers"][0]["stable_code"] = "PASS"
        self.assert_fail_closed(run_node("resolve", blocker), "BLOCKER_INVALID")

    def test_unknown_duplicate_or_missing_sources_fail_closed(self):
        duplicate = copy.deepcopy(self.sample)
        duplicate["sources"][1]["source_id"] = "SPENVIS"
        self.assert_fail_closed(run_node("resolve", duplicate), "SOURCE_ID_INVALID")
        missing = copy.deepcopy(self.sample)
        missing["sources"].pop()
        self.assert_fail_closed(run_node("resolve", missing), "SOURCES_SHAPE_INVALID")

    def test_export_is_allowlisted_and_non_sensitive(self):
        payload = copy.deepcopy(self.sample)
        payload["sources"][0]["blockers"][0]["next_action_ko"] = "Jane Doe /Users/private raw evidence 8 krad"
        exported = run_node("export", payload)
        serialized = json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["data_class"], "SYNTHETIC")
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")
        for forbidden in ["Jane Doe", "/Users/", "raw evidence", "8 krad", "next_action_ko", "https://", "source_record_id"]:
            self.assertNotIn(forbidden, serialized)

    def test_failed_export_contains_no_source_identity(self):
        exported = run_node("export", {"unexpected": "private-source"})
        self.assertEqual(exported["data_class"], "DATA_UNAVAILABLE")
        self.assertEqual(exported["sources"], [])
        self.assertNotIn("private-source", json.dumps(exported))

    def test_offline_single_file_runtime_and_static_fallback(self):
        lowered = self.html.lower()
        self.assertNotRegex(lowered, r"https?://|//cdn|<script[^>]+src=|fetch\s*\(|xmlhttprequest|websocket|sendbeacon")
        self.assertIn('type="file"', self.html)
        self.assertIn("DATA_UNAVAILABLE · NOT_EVALUATED · HOLD", self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_javascript_syntax_and_no_success_claims(self):
        script = re.findall(r"<script>([\s\S]*?)</script>", self.html)
        self.assertEqual(len(script), 1)
        completed = subprocess.run(["node", "--check", "-"], input=script[0], text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("LIVE_CONNECTED", self.html)
        self.assertNotIn("보증 PASS", self.html)


if __name__ == "__main__":
    unittest.main()
