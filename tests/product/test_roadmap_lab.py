#!/usr/bin/env python3
"""Direct tests for the functional three-step Evidence Review demo."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "roadmap-lab.html"
DATA = ROOT / "demo" / "data"


class RoadmapLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>([\s\S]*?)</script>", cls.html)
        assert len(scripts) == 1
        cls.script = scripts[0]

    def evaluate(self, function: str, fixture: str, mutate: str = "") -> dict:
        payload = json.loads((DATA / fixture).read_text(encoding="utf-8"))
        command = (
            "eval(" + json.dumps(self.script) + ");"
            "const payload=" + json.dumps(payload) + ";"
            + mutate
            + f"process.stdout.write(JSON.stringify(globalThis.SPECTRA_REVIEW_DEMO.{function}(payload)));"
        )
        completed = subprocess.run(
            ["node", "-e", command], check=True, capture_output=True, text=True
        )
        return json.loads(completed.stdout)

    def test_main_ui_is_three_actions_not_a_second_slide_deck(self) -> None:
        self.assertEqual(len(re.findall(r'<button class="stage(?: active)?"', self.html)), 3)
        for label in (
            "테스트 예시 3개",
            "실제 후보 receipt 3개",
            "검사 시작 →",
            "변경 적용 · 다시 검사 →",
            "검사 통과 ≠ 실제 승인",
            "선택한 자료를 6개 관문으로 확인합니다.",
            'href="evidence-console.html"',
            "RAW CONSOLE ↗",
        ):
            self.assertIn(label, self.html)
        self.assertNotIn("선택한 자료를 다섯 관문", self.html)
        for presentation_artifact in ('class="card"', "Q&amp;A", "7 routes", "권장 시연"):
            self.assertNotIn(presentation_artifact, self.html)

    def test_bundled_data_files_are_bound_to_runtime_fetches(self) -> None:
        expected = {
            "demo-case-clean-control.json",
            "demo-case-tampered.json",
            "demo-case-wrong-part.json",
            "actual-environment-bundle-receipt.json",
            "actual-part-bundle-receipt.json",
            "local-document-extraction-receipt.json",
            "local-bundle-binding-receipt.json",
        }
        for name in expected:
            self.assertTrue((DATA / name).is_file(), name)
            self.assertIn(name, self.script)
        self.assertIn("fetch(path,{cache:\"no-store\"})", self.script)

    def test_actual_pdf_extraction_is_review_only_and_tamper_rejected(self) -> None:
        result = self.evaluate("inspectJson", "local-document-extraction-receipt.json")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["kind"], "LOCAL DOCUMENT EXTRACTION")
        self.assertEqual(result["status"], "3 CANDIDATES · HOLD")
        tampered = self.evaluate(
            "inspectJson",
            "local-document-extraction-receipt.json",
            'payload.assurance_decision="PASS";',
        )
        self.assertFalse(tampered["recognized"])
        self.assertEqual(tampered["status"], "INVALID · HOLD")

    def test_actual_pdf_candidate_never_becomes_exact_target_without_approved_bom(self) -> None:
        result = self.evaluate(
            "resolveDocumentCandidate", "local-document-extraction-receipt.json"
        )
        self.assertTrue(result["candidateFound"])
        self.assertEqual(result["partNumber"], "5962L1420901VXC")
        self.assertEqual(result["targetMatch"], "NOT_EVALUATED")
        self.assertEqual(result["stop"], 3)
        self.assertEqual(result["blocker"], "APPROVED_BOM_TARGET_MISSING")
        self.assertIn("승인 BOM target", result["why"])
        self.assertIn("시험 조건·임무 적용성", result["why"])

    def test_evidence_intake_accepts_exact_fixture_but_never_passes(self) -> None:
        result = self.evaluate(
            "validateEvidence", "evidence-source-readiness-synthetic.json"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")
        self.assertEqual(
            result["states"],
            {
                "environment": "PROVIDER REF MISSING",
                "parts": "APPROVED BOM MISSING",
            },
        )

    def test_nasa_local_gate_receipt_is_control_only(self) -> None:
        result = self.evaluate(
            "validateNasaReceipt", "nasa-snapshot-gate-receipt.json"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")
        self.assertEqual(result["state"], "CONTROL VALID · NO DECISION")
        tampered = self.evaluate(
            "validateNasaReceipt",
            "nasa-snapshot-gate-receipt.json",
            'payload.use_status="FOR_DECISION";',
        )
        self.assertFalse(tampered["ok"])
        self.assertEqual(tampered["assurance"], "HOLD")

    def test_evidence_intake_rejects_optimistic_decision(self) -> None:
        result = self.evaluate(
            "validateEvidence",
            "evidence-source-readiness-synthetic.json",
            'payload.decision.assurance_decision="PASS";',
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")
        malformed = self.evaluate(
            "validateEvidence",
            "evidence-source-readiness-synthetic.json",
            "payload.sources[0]=null;",
        )
        self.assertFalse(malformed["ok"])
        self.assertEqual(malformed["assurance"], "HOLD")

    def test_candidate_is_review_only_and_exactly_bound(self) -> None:
        result = self.evaluate(
            "validateCandidate", "document-extraction-candidate-synthetic.json"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")
        self.assertEqual(result["partNumber"], "EX-100-SRAM-64M")
        self.assertEqual(result["process"], "28 nm CMOS")
        self.assertEqual(result["lot"], "LOT-SYN-001")
        self.assertEqual(result["value"], "25 krad(Si)")

    def test_candidate_rejects_fabricated_approval_and_rights(self) -> None:
        result = self.evaluate(
            "validateCandidate",
            "document-extraction-candidate-synthetic.json",
            "payload.review_policy.authenticated_approval=true;"
            'payload.source.rights.scope="COMMERCIAL_REUSE";',
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")

    def test_change_impact_reads_generated_values_and_retains_gaps(self) -> None:
        result = self.evaluate("validateImpact", "mvp-product-result.json")
        self.assertTrue(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")
        self.assertEqual(result["before"], 0.063072)
        self.assertEqual(result["after"], 0.013072)
        self.assertTrue(result["environmentGap"])
        self.assertTrue(result["partGap"])

    def test_change_impact_rejects_false_pass_and_value_rebinding(self) -> None:
        result = self.evaluate(
            "validateImpact",
            "mvp-product-result.json",
            'payload.mvp_decision.assurance_decision="PASS";'
            "payload.mvp_decision.change_impact.output_changes[0].after=0;",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["assurance"], "HOLD")

    def test_no_remote_dependency_or_browser_storage(self) -> None:
        lowered = self.html.lower()
        self.assertNotRegex(
            lowered,
            r"https?://|//cdn|xmlhttprequest|websocket|sendbeacon",
        )
        self.assertIn('<script src="data/embedded-review-data.js"></script>', self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_large_minimal_fixed_viewport_and_javascript_syntax(self) -> None:
        for token in (
            "height:100vh",
            "overflow:hidden",
            "font-size:34px",
            "grid-template-columns:repeat(6,minmax(0,1fr))",
            "grid-template-columns:minmax(0,1fr) 330px",
        ):
            self.assertIn(token, self.html)
        completed = subprocess.run(
            ["node", "--check", "-"], input=self.script, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('textContent="DATA_UNAVAILABLE · HOLD"', self.script)


if __name__ == "__main__":
    unittest.main()
