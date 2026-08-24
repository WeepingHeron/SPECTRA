import copy
import json
import pathlib
import re
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "demo" / "workspace.html"
SAMPLE = ROOT / "demo" / "data" / "review-workspace-synthetic.json"
ENVIRONMENT_RECEIPT = ROOT / "demo" / "data" / "readiness-environment-hold-v1.json"
PART_RECEIPT = ROOT / "demo" / "data" / "readiness-part-contract-not-implemented-v1.json"

def run_node(operation, value):
    program = r"""
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[1], "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw new Error("expected one inline application script");
vm.runInThisContext(scripts[0][1], { filename: "workspace-inline.js" });
const api = globalThis.SPECTRA_REVIEW_WORKSPACE;
const input = JSON.parse(fs.readFileSync(0, "utf8"));
let result;
if (process.argv[2] === "resolve") result = api.resolveReviewPayload(input);
else if (process.argv[2] === "parse") result = api.parseReviewText(input.text);
else if (process.argv[2] === "parse-workspace") result = api.parseWorkspaceText(input.text);
else if (process.argv[2] === "receipt") result = api.resolveReadinessReceipt(input);
else if (process.argv[2] === "export") result = JSON.parse(api.serializeAuditSummary(api.resolveReviewPayload(input)));
else if (process.argv[2] === "receipt-export") result = JSON.parse(api.serializeAuditSummary(api.resolveReadinessReceipt(input)));
else throw new Error("unknown operation");
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        ["node", "-e", program, str(WORKSPACE), operation],
        input=json.dumps(value),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


class EvidenceReviewWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = WORKSPACE.read_text(encoding="utf-8")
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
        cls.environment_receipt = json.loads(ENVIRONMENT_RECEIPT.read_text(encoding="utf-8"))
        cls.part_receipt = json.loads(PART_RECEIPT.read_text(encoding="utf-8"))

    def assert_fail_closed(self, model, reason=None):
        self.assertFalse(model["ready"])
        if reason:
            self.assertEqual(model["reason_code"], reason)
        self.assertEqual(model["decision"]["processing_status"], "DATA_UNAVAILABLE")
        self.assertEqual(model["decision"]["engineering_gate"], "NOT_EVALUATED")
        self.assertEqual(model["decision"]["assurance_decision"], "HOLD")
        self.assertNotIn("case", model)
        self.assertEqual(len(model["coverage"]), 8)
        self.assertTrue(all(item["status"] == "DATA_UNAVAILABLE" for item in model["coverage"]))

    def test_normal_synthetic_sample_resolves_to_hold(self):
        model = run_node("resolve", self.sample)
        self.assertTrue(model["ready"])
        self.assertEqual(model["case"]["data_class"], "SYNTHETIC")
        self.assertEqual(model["decision"], {
            "processing_status": "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
        })
        self.assertEqual([item["domain"] for item in model["coverage"]], [
            "ENVIRONMENT", "EXACT_PART", "TID", "SEL", "SEB", "SEGR", "RIGHTS", "SCIENTIFIC_CROSSCHECK"
        ])
        self.assertIn("AUTHENTICATED_ISSUANCE_ROOT_MISSING", [gap["stable_code"] for gap in model["blocking_gaps"]])

    def test_malformed_json_fails_closed_without_throwing(self):
        self.assert_fail_closed(run_node("parse", {"text": "{not-json"}), "MALFORMED_JSON")

    def test_wrong_nested_type_fails_closed(self):
        attack = copy.deepcopy(self.sample)
        attack["coverage"] = {"ENVIRONMENT": "MISSING"}
        self.assert_fail_closed(run_node("resolve", attack), "COVERAGE_SHAPE_INVALID")

    def test_duplicate_gap_id_fails_closed(self):
        attack = copy.deepcopy(self.sample)
        attack["blocking_gaps"][1]["gap_id"] = attack["blocking_gaps"][0]["gap_id"]
        self.assert_fail_closed(run_node("resolve", attack), "DUPLICATE_GAP_ID")

    def test_unknown_coverage_status_fails_closed(self):
        attack = copy.deepcopy(self.sample)
        attack["coverage"][0]["status"] = "PASS"
        self.assert_fail_closed(run_node("resolve", attack), "COVERAGE_STATUS_UNKNOWN")

    def test_actual_self_declaration_hides_identity_and_holds(self):
        attack = copy.deepcopy(self.sample)
        attack["case"]["data_class"] = "ACTUAL"
        attack["case"]["mission_ref"] = "mission-actual-secret"
        model = run_node("resolve", attack)
        self.assert_fail_closed(model, "UNAUTHENTICATED_ACTUAL_CLAIM")
        self.assertNotIn("mission-actual-secret", json.dumps(model))

    def test_unauthenticated_issuance_claim_fails_closed(self):
        attack = copy.deepcopy(self.sample)
        attack["issuance_authentication"] = {"status": "AUTHENTICATED", "issuance_root_ref": "self-claimed-root"}
        model = run_node("resolve", attack)
        self.assert_fail_closed(model, "UNAUTHENTICATED_ISSUANCE_CLAIM")
        self.assertNotIn("self-claimed-root", json.dumps(model))

    def test_optimistic_decision_and_actual_dose_are_rejected(self):
        optimistic = copy.deepcopy(self.sample)
        optimistic["decision"]["assurance_decision"] = "PASS"
        self.assert_fail_closed(run_node("resolve", optimistic), "OPTIMISTIC_DECISION_REJECTED")

        dose = copy.deepcopy(self.sample)
        dose["dose_krad"] = 8
        model = run_node("resolve", dose)
        self.assert_fail_closed(model, "WORKSPACE_SHAPE_INVALID")
        self.assertNotIn("dose_krad", json.dumps(model))

    def test_audit_export_is_allowlisted_and_non_sensitive(self):
        payload = copy.deepcopy(self.sample)
        payload["case"]["mission_ref"] = "secret-mission@example.com"
        payload["case"]["bom_ref"] = "/Users/reviewer/private-bom.json"
        payload["blocking_gaps"][0]["summary_ko"] = "PII Jane Doe, raw evidence, dose 8 krad"
        payload["blocking_gaps"][0]["required_evidence_ko"] = "local path /private/raw.pdf"
        exported = run_node("export", payload)
        serialized = json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["data_class"], "SYNTHETIC")
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")
        self.assertEqual(len(exported["coverage"]), 8)
        self.assertEqual(len(exported["blocking_gaps"]), 4)
        for forbidden in ["secret-mission", "/Users/", "Jane Doe", "raw evidence", "8 krad", "evidence_package_id", "gap_id", "summary_ko", "required_evidence_ko"]:
            self.assertNotIn(forbidden, serialized)

    def test_safe_export_remains_hold(self):
        exported = run_node("export", {"unexpected": True})
        self.assertEqual(exported["data_class"], "DATA_UNAVAILABLE")
        self.assertEqual(exported["coverage"], [])
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")

    def test_offline_runtime_and_static_fallback(self):
        lowered = self.html.lower()
        self.assertNotRegex(lowered, r"https?://|//cdn|<script[^>]+src=|fetch\s*\(|xmlhttprequest|websocket|sendbeacon")
        self.assertIn('type="file"', self.html)
        self.assertIn("JavaScript가 실행되지 않아 입력을 검토할 수 없다.", self.html)
        self.assertIn("DATA_UNAVAILABLE · NOT_EVALUATED · HOLD", self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_javascript_syntax(self):
        script = re.findall(r"<script>([\s\S]*?)</script>", self.html)
        self.assertEqual(len(script), 1)
        completed = subprocess.run(["node", "--check", "-"], input=script[0], text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_workspace_is_independent_from_existing_demos(self):
        self.assertNotIn("index.html", self.html)
        self.assertNotIn("product.html", self.html)
        for relative in ["demo/index.html", "demo/product.html"]:
            existing = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("SPECTRA_REVIEW_WORKSPACE", existing, relative)
            self.assertNotIn("review-workspace-synthetic.json", existing, relative)

    def test_current_v1_receipts_show_only_bounded_hold_readiness(self):
        environment = run_node("receipt", self.environment_receipt)
        self.assertTrue(environment["ready"])
        self.assertEqual(environment["receipt_kind"], "ENVIRONMENT")
        self.assertEqual(environment["source_label"], "SYNTHETIC_CONTROL")
        self.assertEqual(environment["readiness_status"], "HOLD_NOT_ISSUED")
        self.assertEqual(environment["decision"]["assurance_decision"], "HOLD")

        part = run_node("receipt", self.part_receipt)
        self.assertTrue(part["ready"])
        self.assertEqual(part["receipt_kind"], "PART")
        self.assertEqual(part["source_label"], "DEMO_ONLY")
        self.assertEqual(part["readiness_status"], "CONTRACT_NOT_IMPLEMENTED")
        self.assertEqual(part["identity_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(part["applicability_status"], "NOT_EVALUATED")
        self.assertEqual(part["decision"]["assurance_decision"], "HOLD")

        for model in (environment, part):
            serialized = json.dumps(model)
            for forbidden in ["receipt_id", "assessed_at", "source_record_id", "issued_contract_ref", "evidence_record_ref", "dose", "suitability", '"PASS"']:
                self.assertNotIn(forbidden, serialized)

    def test_receipt_dispatch_is_used_by_workspace_file_path(self):
        model = run_node("parse-workspace", {"text": json.dumps(self.environment_receipt)})
        self.assertTrue(model["ready"])
        self.assertEqual(model["input_type"], "READINESS_RECEIPT")
        self.assertEqual(model["readiness_status"], "HOLD_NOT_ISSUED")

    def test_receipt_blockers_map_to_bounded_owner_and_action(self):
        environment = run_node("receipt", self.environment_receipt)
        self.assertEqual(environment["blockers"], [{
            "stable_code": "ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED",
            "owner_role": "ENVIRONMENT_EVIDENCE_OWNER",
            "next_action_code": "CONFIGURE_DEPLOYMENT_AUTHENTICATOR",
            "next_action_ko": "배포 소유 인증기를 구성하고 발행 Gate를 다시 실행한다.",
        }])
        part = run_node("receipt", self.part_receipt)
        self.assertEqual(
            [(item["stable_code"], item["owner_role"], item["next_action_code"]) for item in part["blockers"]],
            [
                ("PART_TEST_EVIDENCE_V2_NOT_IMPLEMENTED", "CONTRACT_OWNER", "IMPLEMENT_PART_TEST_EVIDENCE_V2"),
                ("SYNTHETIC_DEMO_ONLY", "PARTS_EVIDENCE_OWNER", "SUPPLY_APPROVED_EVIDENCE_PACKET"),
            ],
        )

    def test_receipt_optimistic_statuses_fail_closed_and_hide_values(self):
        attacks = []

        candidate = copy.deepcopy(self.environment_receipt)
        candidate["issuance_status"] = "ISSUABLE_CANDIDATE"
        candidate["receipt_id"] = "secret-candidate-id"
        attacks.append(candidate)

        implemented = copy.deepcopy(self.part_receipt)
        implemented["target_contract"]["implementation_status"] = "IMPLEMENTED"
        implemented["receipt_id"] = "secret-implemented-id"
        attacks.append(implemented)

        decision_use = copy.deepcopy(self.part_receipt)
        decision_use["used_for_decision"] = True
        decision_use["receipt_id"] = "secret-decision-id"
        attacks.append(decision_use)

        assurance = copy.deepcopy(self.environment_receipt)
        assurance["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        assurance["receipt_id"] = "secret-assurance-id"
        attacks.append(assurance)

        for attack in attacks:
            model = run_node("receipt", attack)
            self.assert_fail_closed(model)
            serialized = json.dumps(model)
            self.assertNotIn(attack["receipt_id"], serialized)
            self.assertNotIn("ISSUABLE_CANDIDATE", serialized)
            self.assertNotIn("IMPLEMENTED", serialized)
            self.assertNotIn("SUPPORTED_WITH_MITIGATION", serialized)

    def test_receipt_unknown_version_cross_kind_and_output_refs_fail_closed(self):
        attacks = []
        unknown = copy.deepcopy(self.environment_receipt)
        unknown["contract_version"] = "2.0.0"
        attacks.append(unknown)

        cross_kind = copy.deepcopy(self.part_receipt)
        cross_kind["issuance_status"] = "HOLD_NOT_ISSUED"
        attacks.append(cross_kind)

        environment_output = copy.deepcopy(self.environment_receipt)
        environment_output["issued_contract_ref"] = {"secret": "environment-output"}
        attacks.append(environment_output)

        part_output = copy.deepcopy(self.part_receipt)
        part_output["evidence_record_ref"] = {"secret": "part-output"}
        attacks.append(part_output)

        for attack in attacks:
            model = run_node("receipt", attack)
            self.assert_fail_closed(model)
            serialized = json.dumps(model)
            self.assertNotIn("environment-output", serialized)
            self.assertNotIn("part-output", serialized)

    def test_receipt_malformed_nested_types_and_missing_blockers_fail_closed(self):
        nested = copy.deepcopy(self.environment_receipt)
        nested["source_result"] = []
        self.assert_fail_closed(run_node("receipt", nested), "ENVIRONMENT_SOURCE_SHAPE_INVALID")

        target = copy.deepcopy(self.part_receipt)
        target["target_contract"] = "NOT_IMPLEMENTED"
        self.assert_fail_closed(run_node("receipt", target), "PART_TARGET_INVALID")

        for receipt in (self.environment_receipt, self.part_receipt):
            missing = copy.deepcopy(receipt)
            missing["blocker_codes"] = []
            self.assert_fail_closed(run_node("receipt", missing), "READINESS_BLOCKERS_INVALID")

            false_pass = copy.deepcopy(receipt)
            false_pass["blocker_codes"] = ["PASS"]
            model = run_node("receipt", false_pass)
            self.assert_fail_closed(model, "READINESS_BLOCKERS_INVALID")
            self.assertNotIn('"PASS"', json.dumps(model))

    def test_receipt_export_is_allowlisted_and_never_carries_identity_or_values(self):
        payload = copy.deepcopy(self.part_receipt)
        payload["receipt_id"] = "private-receipt@example.com"
        payload["source_result"]["source_record_id"] = "/private/part-source"
        exported = run_node("receipt-export", payload)
        serialized = json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["data_class"], "READINESS_RECEIPT_V1")
        self.assertEqual(exported["readiness_status"], "CONTRACT_NOT_IMPLEMENTED")
        self.assertEqual(exported["decision"]["assurance_decision"], "HOLD")
        for forbidden in ["private-receipt", "/private/", "receipt_id", "source_record_id", "identity_status", "applicability_status", "dose", "suitability", '"PASS"']:
            self.assertNotIn(forbidden, serialized)

    def test_readiness_ui_copy_has_no_success_or_engineering_value_claims(self):
        self.assertNotIn("보증 PASS", self.html)
        self.assertNotIn("issued_contract_ref", self.html)
        self.assertNotIn("evidence_record_ref", self.html)
        self.assertNotIn("dose 값", self.html)
        self.assertNotIn("suitability", self.html.lower())


if __name__ == "__main__":
    unittest.main()
