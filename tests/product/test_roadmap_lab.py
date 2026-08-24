import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "roadmap-lab.html"

ROUTES = {
    "evidence-intake.html": "BLOCKED_EXTERNAL",
    "cots-candidate-library.html": "BLOCKED_EXTERNAL",
    "document-review.html": "IMPLEMENTED_BOUNDED",
    "ai-processing-readiness.html": "READINESS_ONLY",
    "change-impact.html": "IMPLEMENTED_BOUNDED",
    "cad-linkage-readiness.html": "READINESS_ONLY",
    "security-posture.html": "IMPLEMENTED_BOUNDED",
}

class RoadmapLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")

    def test_all_seven_routes_exist_and_are_relative_demo_links(self):
        links = re.findall(r'<a class="card" href="([^"]+)" data-route="([^"]+)" data-status="([^"]+)">', self.html)
        self.assertEqual(len(links), 7)
        self.assertEqual({href for href, route, status in links}, set(ROUTES))
        for href, route, status in links:
            self.assertEqual(href, route)
            self.assertEqual(status, ROUTES[href])
            self.assertTrue((HTML.parent / href).is_file(), href)
            self.assertFalse(href.startswith(("/", "http://", "https://")))

    def test_phase_route_grouping_is_exact(self):
        phases = re.findall(r'<article class="phase">([\s\S]*?)</article>', self.html)
        self.assertEqual(len(phases), 3)
        phase_routes = [re.findall(r'data-route="([^"]+)"', phase) for phase in phases]
        self.assertEqual(phase_routes, [
            ["evidence-intake.html", "cots-candidate-library.html"],
            ["document-review.html", "ai-processing-readiness.html"],
            ["change-impact.html", "cad-linkage-readiness.html", "security-posture.html"],
        ])

    def test_each_card_has_one_exact_status_and_all_status_classes_are_used(self):
        for route, expected in ROUTES.items():
            card = re.search(rf'<a class="card" href="{re.escape(route)}"[\s\S]*?</a>', self.html)
            self.assertIsNotNone(card, route)
            statuses = re.findall(r'>(IMPLEMENTED_BOUNDED|READINESS_ONLY|BLOCKED_EXTERNAL)<', card.group(0))
            self.assertEqual(statuses, [expected], route)
        self.assertEqual(set(ROUTES.values()), {"IMPLEMENTED_BOUNDED", "READINESS_ONLY", "BLOCKED_EXTERNAL"})

    def test_top_truth_boundary_and_assurance_hold_are_visible(self):
        for text in ["SYNTHETIC · LOCAL DEMO", "ASSURANCE HOLD", "실제 서비스 연결과 과학적 적합성을 뜻하지 않는다."]:
            self.assertIn(text, self.html)

    def test_external_systems_are_explicitly_not_complete(self):
        boundaries = [
            "실제 connector 미연동",
            "production library 아님",
            "AI 호출·승인 아님",
            "API call 0 · authenticated HITL 미구현",
            "CAD parser·3D shielding dose 계산 없음",
            "KMS 서명·침투시험 미완료",
        ]
        for boundary in boundaries:
            self.assertIn(boundary, self.html)
        for forbidden in ["LIVE_CONNECTED", "PRODUCTION_READY", "ASSURANCE PASS", "PENTEST_COMPLETE", "KMS_DEPLOYED", "AUTHENTICATED_HITL_COMPLETE"]:
            self.assertNotIn(forbidden, self.html)

    def test_actual_completion_conditions_are_present(self):
        for text in ["실제 완료 조건", "provider job reference", "승인 BOM", "mission applicability", "authenticated reviewer", "승인된 penetration test"]:
            self.assertIn(text, self.html)

    def test_no_remote_dependency_or_active_runtime(self):
        lowered = self.html.lower()
        self.assertNotRegex(lowered, r"https?://|//cdn|<script|fetch\s*\(|xmlhttprequest|websocket|sendbeacon")
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_fixed_viewport_layout_contract_is_present(self):
        self.assertIn("height:100vh", self.html)
        self.assertIn("overflow:hidden", self.html)
        self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))", self.html)
        self.assertIn("@media(max-height:760px)", self.html)

if __name__ == "__main__": unittest.main()
