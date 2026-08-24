import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PATH = (
    ROOT
    / "docs/workstreams/40-parts-evidence/references/23lc1024-published-comparison.json"
)
CASE_PATH = ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json"
MODEL_PATH = ROOT / "simulation/config/synthetic-model.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ReferenceComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load_json(REFERENCE_PATH)
        cls.case = load_json(CASE_PATH)
        cls.model = load_json(MODEL_PATH)
        packet_path = ROOT / cls.case["base_packet_fixture"]
        cls.packet_overlays = []
        while True:
            packet = load_json(packet_path)
            if "inputs" in packet:
                cls.packet = packet
                break
            cls.packet_overlays.append(packet)
            packet_path = packet_path.parent / packet["base"]

    def test_comparison_remains_fail_closed(self):
        self.assertEqual(self.reference["comparison_status"], "NOT_COMPARABLE")
        self.assertEqual(self.reference["assurance_decision"], "HOLD")
        self.assertFalse(self.reference["used_for_decision"])
        self.assertFalse(
            self.reference["numeric_comparison"]["direct_validation_allowed"]
        )

    def test_published_article_is_not_claimed_as_exact_target(self):
        target = self.reference["approved_catalog_target"]
        tested = self.reference["published_observation"]["tested_identity"]
        self.assertEqual(target["orderable_part_number"], "23LC1024-I/SN")
        self.assertEqual(target["package"], "8-lead SOIC")
        self.assertIsNone(tested["orderable_part_number"])
        self.assertEqual(tested["package"], "8-lead PDIP")
        self.assertEqual(tested["identity_status"], "PARTIAL_UNRESOLVED")

    def test_ratio_is_bound_to_current_synthetic_fixture(self):
        self.assertFalse(
            any(
                operation["path"] == "/inputs/3/cross_section"
                for overlay in self.packet_overlays
                for operation in overlay["operations"]
            )
        )
        evidence = next(item for item in self.packet["inputs"] if item["kind"] == "PART_TEST_EVIDENCE")
        synthetic = evidence["cross_section"]["value"]
        published = self.reference["published_observation"]["result"]["cross_section"]["value"]
        recorded = self.reference["numeric_comparison"]["synthetic_divided_by_published"]
        self.assertEqual(
            synthetic,
            self.reference["spectra_synthetic_reference"]["cross_section"]["value"],
        )
        self.assertAlmostEqual(recorded, synthetic / published, places=12)
        self.assertEqual(
            self.model["see_exposure_scale"],
            self.reference["spectra_synthetic_reference"]["see_exposure_scale"],
        )

    def test_known_non_comparability_codes_are_explicit(self):
        codes = set(self.reference["blocking_codes"])
        self.assertTrue(
            {
                "PART_IDENTITY_PARTIAL",
                "PACKAGE_MISMATCH",
                "PARTICLE_SPECTRUM_MISMATCH",
                "SYNTHETIC_EXPOSURE_SCALE",
            }.issubset(codes)
        )

    def test_xray_observation_is_not_used_as_tid_assurance(self):
        observation = self.reference["published_observation"][
            "additional_screening_observation"
        ]
        self.assertEqual(observation["reported_dose"]["unit"], "kGy")
        self.assertFalse(observation["direct_tid_comparison_allowed"])


if __name__ == "__main__":
    unittest.main()
