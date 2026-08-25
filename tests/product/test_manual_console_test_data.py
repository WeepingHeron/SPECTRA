#!/usr/bin/env python3
"""Keep the user-facing manual upload fixtures honest and reproducible."""

from __future__ import annotations

import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import run_evidence_console  # noqa: E402,F401
from intake_local_document_candidate import intake_document  # noqa: E402


class ManualConsoleTestDataTests(unittest.TestCase):
    def test_manifest_cases_match_actual_local_parser_results(self) -> None:
        fixture_root = ROOT / "demo" / "test-data"
        manifest = json.loads((fixture_root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["source_classification"],
            "MIXED_SYNTHETIC_AND_PUBLISHED_SUMMARIES",
        )
        self.assertGreaterEqual(len(manifest["cases"]), 15)

        receipts = {}
        for case in manifest["cases"]:
            with self.subTest(file=case["file"]):
                path = fixture_root / case["file"]
                self.assertTrue(path.is_file())
                receipt = intake_document(
                    path,
                    expected_part=case.get("expected_part", manifest["expected_part"]),
                    manufacturer=case.get("manufacturer", manifest["manufacturer"]),
                    local_review_rights_confirmed=case["rights"],
                )
                self.assertEqual(receipt["processing_status"], case["processing_status"])
                self.assertEqual(receipt["candidate_count"], case["candidate_count"])
                self.assertEqual(receipt["assurance_decision"], "HOLD")
                self.assertFalse(receipt["used_for_decision"])
                receipts[case["file"]] = receipt
                if blocker := case.get("blocker"):
                    self.assertIn(blocker, receipt["blocker_codes"])

        nasa_tid = receipts[
            "10_실제공개값_NASA_Micron_MT29F4T08CTHBBM5_TID.txt"
        ]["candidates"]
        self.assertIn(
            ("TID_DOSE", "39 krad(Si)", "krad(Si)"),
            {(item["field"], item["value"], item["unit"]) for item in nasa_tid},
        )
        nasa_see = receipts[
            "11_실제공개값_NASA_Hynix_H25QFT8F4A9R-BDF_SEE.txt"
        ]["candidates"]
        nasa_see_values = {
            (item["field"], item["value"], item["unit"]) for item in nasa_see
        }
        self.assertIn(
            ("SEE_LET", "58.8 MeV-cm2/mg", "MeV-cm2/mg"), nasa_see_values
        )
        self.assertIn(
            ("SEE_CROSS_SECTION", "< 1x10-12 cm2/byte", "cm2/byte"),
            nasa_see_values,
        )
        esa = receipts[
            "12_실제공개값_ESA_Micron_MT29F32G08CBACA_TID_SEE.txt"
        ]["candidates"]
        esa_values = {(item["field"], item["value"], item["unit"]) for item in esa}
        self.assertIn(("TID_DOSE", "~20 krad", "krad"), esa_values)
        self.assertIn(("LOT_DATE_CODE", "Unknown", None), esa_values)

        landsat = receipts[
            "13_실제임무계획_NASA_Landsat9_궤도수명.txt"
        ]["candidates"]
        landsat_values = {
            (item["field"], item["value"], item["unit"]) for item in landsat
        }
        self.assertIn(("ORBIT_ALTITUDE", "705 km", "km"), landsat_values)
        self.assertIn(("ORBIT_INCLINATION", "98.2 deg", "deg"), landsat_values)
        self.assertIn(("MISSION_DURATION", "5 years", "years"), landsat_values)

        part_spec = receipts[
            "15_실제부품명세_Microchip_23LC1024.txt"
        ]["candidates"]
        part_values = {
            (item["field"], item["value"], item["unit"]) for item in part_spec
        }
        self.assertIn(("SUPPLY_VOLTAGE", "2.5V-5.5V", "V"), part_values)
        self.assertIn(
            ("TEST_TEMPERATURE", "-40°C to +85°C", "degC"), part_values
        )


if __name__ == "__main__":
    unittest.main()
