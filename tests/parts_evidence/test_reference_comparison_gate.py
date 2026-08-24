import copy
import json
import math
import unittest
from pathlib import Path

from src.spectra_parts_adapter import assess_reference_comparison


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PATH = (
    ROOT
    / "docs/workstreams/40-parts-evidence/references/23lc1024-published-comparison.json"
)


class PublishedReferenceComparisonGateTest(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))

    def assess(self, record=None):
        return assess_reference_comparison(
            self.record if record is None else record
        )

    def test_current_reference_is_calculated_but_not_directly_comparable(self):
        result = self.assess()

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["comparison_status"], "NOT_COMPARABLE")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertFalse(result["direct_validation_allowed"])
        self.assertEqual(
            result["numeric_comparison"]["status"],
            "CALCULATED_REFERENCE_ONLY",
        )
        self.assertEqual(
            result["numeric_comparison"]["synthetic_divided_by_published"],
            243.90243902439022,
        )
        self.assertTrue(
            {
                "PART_IDENTITY_PARTIAL",
                "PACKAGE_MISMATCH",
                "LOT_DIE_UNRESOLVED",
                "SOURCE_ARTIFACT_MANIFEST_MISSING",
                "RIGHTS_SCOPE_UNRESOLVED",
                "PARTICLE_SPECTRUM_MISMATCH",
                "SYNTHETIC_PART_MISMATCH",
                "SYNTHETIC_EXPOSURE_SCALE",
                "MISSION_ENVIRONMENT_UNAVAILABLE",
                "DESTRUCTIVE_SEE_EVIDENCE_MISSING",
                "TID_EVIDENCE_MISSING",
            }.issubset(result["stable_codes"])
        )

    def test_receipt_is_deterministic(self):
        self.assertEqual(self.assess(), self.assess(copy.deepcopy(self.record)))

    def test_declared_blocking_codes_are_not_trusted(self):
        attacked = copy.deepcopy(self.record)
        attacked["blocking_codes"] = []

        self.assertEqual(
            self.assess()["stable_codes"], self.assess(attacked)["stable_codes"]
        )

    def test_recorded_ratio_tamper_is_invalid_and_hidden(self):
        attacked = copy.deepcopy(self.record)
        attacked["numeric_comparison"]["synthetic_divided_by_published"] = (
            math.nextafter(
                attacked["numeric_comparison"]["synthetic_divided_by_published"],
                math.inf,
            )
        )

        result = self.assess(attacked)

        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertIn("RECORDED_RATIO_MISMATCH", result["stable_codes"])
        self.assertEqual(result["numeric_comparison"]["status"], "NOT_COMPUTED")
        self.assertIsNone(
            result["numeric_comparison"]["synthetic_divided_by_published"]
        )

    def test_optimistic_decision_fields_are_rejected(self):
        attacks = (
            ("used_for_decision", True),
            ("comparison_status", "COMPARABLE"),
            ("assurance_decision", "PASS"),
            ("processing_status", "INVALID_INPUT"),
        )
        for field, value in attacks:
            with self.subTest(field=field):
                attacked = copy.deepcopy(self.record)
                attacked[field] = value
                result = self.assess(attacked)
                self.assertEqual(result["processing_status"], "INVALID_INPUT")
                expected_code = (
                    "DECLARED_PROCESSING_STATUS_INVALID"
                    if field == "processing_status"
                    else "OPTIMISTIC_COMPARISON_REJECTED"
                )
                self.assertIn(expected_code, result["stable_codes"])
                self.assertEqual(result["assurance_decision"], "HOLD")
                self.assertFalse(result["used_for_decision"])

    def test_direct_validation_and_tid_optimism_are_rejected(self):
        comparison_attack = copy.deepcopy(self.record)
        comparison_attack["numeric_comparison"]["direct_validation_allowed"] = True
        tid_attack = copy.deepcopy(self.record)
        tid_attack["published_observation"]["additional_screening_observation"][
            "direct_tid_comparison_allowed"
        ] = True

        comparison_result = self.assess(comparison_attack)
        tid_result = self.assess(tid_attack)

        self.assertIn(
            "OPTIMISTIC_COMPARISON_REJECTED",
            comparison_result["stable_codes"],
        )
        self.assertIn(
            "OPTIMISTIC_TID_COMPARISON_REJECTED", tid_result["stable_codes"]
        )
        self.assertEqual(comparison_result["processing_status"], "INVALID_INPUT")
        self.assertEqual(tid_result["processing_status"], "INVALID_INPUT")

    def test_invalid_cross_sections_fail_closed(self):
        for value in (True, 0, -1, math.nan, math.inf):
            with self.subTest(value=value):
                attacked = copy.deepcopy(self.record)
                attacked["spectra_synthetic_reference"]["cross_section"][
                    "value"
                ] = value
                result = self.assess(attacked)
                self.assertEqual(result["processing_status"], "INVALID_INPUT")
                self.assertIn("CROSS_SECTION_INVALID", result["stable_codes"])
                self.assertIsNone(
                    result["numeric_comparison"][
                        "synthetic_divided_by_published"
                    ]
                )

        exposure_attack = copy.deepcopy(self.record)
        exposure_attack["spectra_synthetic_reference"]["see_exposure_scale"] = True
        exposure_result = self.assess(exposure_attack)
        self.assertEqual(exposure_result["processing_status"], "INVALID_INPUT")
        self.assertIn(
            "SYNTHETIC_EXPOSURE_SCALE_INVALID",
            exposure_result["stable_codes"],
        )

        uncertainty_attack = copy.deepcopy(self.record)
        uncertainty_attack["published_observation"]["result"]["cross_section"][
            "uncertainty"
        ] = False
        uncertainty_result = self.assess(uncertainty_attack)
        self.assertEqual(uncertainty_result["processing_status"], "INVALID_INPUT")
        self.assertIn(
            "CROSS_SECTION_UNCERTAINTY_INVALID",
            uncertainty_result["stable_codes"],
        )

    def test_unit_mismatch_is_valid_record_but_not_calculable(self):
        attacked = copy.deepcopy(self.record)
        attacked["spectra_synthetic_reference"]["cross_section"]["unit"] = (
            "cm2/bit"
        )

        result = self.assess(attacked)

        self.assertEqual(result["processing_status"], "VALID")
        self.assertIn("CROSS_SECTION_UNIT_MISMATCH", result["stable_codes"])
        self.assertEqual(result["numeric_comparison"]["status"], "NOT_COMPUTED")
        self.assertIsNone(
            result["numeric_comparison"]["synthetic_divided_by_published"]
        )

    def test_exact_orderable_mismatch_is_not_collapsed_into_partial(self):
        attacked = copy.deepcopy(self.record)
        attacked["published_observation"]["tested_identity"][
            "orderable_part_number"
        ] = "23LC1024-I/P"

        result = self.assess(attacked)

        self.assertIn("PART_IDENTITY_MISMATCH", result["stable_codes"])
        self.assertNotIn("PART_IDENTITY_PARTIAL", result["stable_codes"])
        self.assertEqual(result["comparison_status"], "NOT_COMPARABLE")

    def test_invalid_source_hash_and_unknown_field_are_rejected(self):
        hash_attack = copy.deepcopy(self.record)
        hash_attack["published_observation"]["source"][
            "observed_artifact_sha256"
        ] = "not-a-hash"
        field_attack = copy.deepcopy(self.record)
        field_attack["numeric_comparison"]["direct_pass"] = True

        hash_result = self.assess(hash_attack)
        field_result = self.assess(field_attack)

        self.assertIn(
            "PUBLISHED_ARTIFACT_HASH_INVALID", hash_result["stable_codes"]
        )
        self.assertIn("INPUT_FIELD_FORBIDDEN", field_result["stable_codes"])
        self.assertEqual(hash_result["processing_status"], "INVALID_INPUT")
        self.assertEqual(field_result["processing_status"], "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
