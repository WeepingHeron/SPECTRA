from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_env_adapter import DoseParseError, normalize_tid_candidates, parse_shieldose2_text  # noqa: E402


# SYNTHETIC parser fixture. Values below are deliberately not copied from a model run.
SYNTHETIC = """'*', 25, 6
'SPENVIS 4.6.14.3582          - 20-Aug-2026 00:00:00'
'PRJ_DEF', -1, 'SYNTHETIC_PROJECT'
'PRJ_HDR', -1, 'SYNTHETIC PARSER FIXTURE'
'MIS_DUR', 1, 3.650000E+02, 'days'
'PLT_HDR', -1, '4pi Dose at Centre of Al Spheres'
'Mission start: 01/01/2027 00:00:00'
'Mission end: 01/01/2028 00:00:00'
'Thick', 'mm', 1, 'Aluminium Absorber Thickness'
'Dose', 'rad', 5, 'Dose in Si'
1.0, 10, 1, 2, 3, 4
2.0, 20, 2, 3, 4, 5
3.0, 30, 3, 4, 5, 6
4.0, 40, 4, 5, 6, 7
'End of File'
"""


class Shieldose2ParserTests(unittest.TestCase):
    def test_parses_reviewed_signature_and_creates_hold_candidates(self):
        parsed = parse_shieldose2_text(SYNTHETIC)
        candidates = normalize_tid_candidates(parsed)
        self.assertEqual(parsed["provider"]["platform_build"], "4.6.14.3582")
        self.assertEqual(parsed["dose_unit"], "rad(Si)")
        self.assertEqual(len(candidates), 4)
        self.assertTrue(all(item["contract_status"].startswith("HOLD_") for item in candidates))

    def test_rejects_unreviewed_units(self):
        with self.assertRaises(DoseParseError) as caught:
            parse_shieldose2_text(SYNTHETIC.replace("'Dose', 'rad', 5", "'Dose', 'Gy', 5"))
        self.assertEqual(caught.exception.code, "UNSUPPORTED_UNITS")

    def test_rejects_missing_required_shielding_point(self):
        parsed = parse_shieldose2_text(SYNTHETIC.replace("4.0, 40, 4, 5, 6, 7\n", ""))
        with self.assertRaises(DoseParseError) as caught:
            normalize_tid_candidates(parsed)
        self.assertEqual(caught.exception.code, "SHIELDING_POINTS_MISMATCH")


if __name__ == "__main__":
    unittest.main()
