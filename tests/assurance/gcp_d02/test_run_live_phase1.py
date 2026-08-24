from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tests.assurance.gcp_d02.run_live_phase1 import PHASE1_IDS, canonical_bytes, mutate


ROOT = Path(__file__).resolve().parents[3]


class Phase1MutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(
            (ROOT / "tests/assurance/gcp_d02/fixtures/asr-d02-preparation-fixtures.json").read_text()
        )
        cls.control = payload["control_input"]

    def test_scope_is_exactly_approved_subset(self) -> None:
        self.assertEqual(PHASE1_IDS, ("ASR-D02-02", "ASR-D02-04", "ASR-D02-05", "ASR-D02-10"))

    def test_hash_attack_changes_only_declared_evidence_hash(self) -> None:
        attacked = mutate(self.control, "ASR-D02-04")
        expected = copy.deepcopy(self.control)
        expected["part_evidence"]["evidence_hash"] = "sha256:" + "a" * 64
        self.assertEqual(attacked, expected)

    def test_identity_attack_changes_only_exact_part_number(self) -> None:
        attacked = mutate(self.control, "ASR-D02-05")
        expected = copy.deepcopy(self.control)
        expected["part_evidence"]["exact_orderable_part_number"] = "SYNTHETIC-PART-999"
        self.assertEqual(attacked, expected)

    def test_mutation_does_not_change_control(self) -> None:
        original = canonical_bytes(self.control)
        for attack_id in PHASE1_IDS:
            mutate(self.control, attack_id)
        self.assertEqual(canonical_bytes(self.control), original)

    def test_canonical_bytes_normalize_workflows_integer_floats(self) -> None:
        self.assertEqual(canonical_bytes({"value": 10.0}), b'{"value":10}')


if __name__ == "__main__":
    unittest.main()
