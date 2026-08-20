#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime
from pathlib import Path

from raw_manifest_preflight import assess_preflight


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURES = HERE / "fixtures"
SCHEMAS = ROOT / "schemas"


def load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def resolve(document, pointer: str):
    current = document
    tokens = pointer.split("/")[1:]
    for token in tokens[:-1]:
        current = current[int(token)] if isinstance(current, list) else current[token]
    final = tokens[-1]
    return current, int(final) if isinstance(current, list) else final


def read_pointer(document, pointer: str):
    current = document
    for token in pointer.split("/")[1:]:
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def apply_operations(base: dict, operations: list[dict]) -> dict:
    result = copy.deepcopy(base)
    for operation in operations:
        parent, key = resolve(result, operation["path"])
        if operation["op"] == "set":
            parent[key] = operation["value"]
        elif operation["op"] == "delete":
            del parent[key]
        elif operation["op"] == "copy_append":
            target = read_pointer(result, operation["path"])
            target.append(copy.deepcopy(read_pointer(result, operation["from"])))
        else:
            raise AssertionError(f"unsupported fixture operation: {operation['op']}")
    return result


class RawManifestPreflightTests(unittest.TestCase):
    def test_synthetic_attack_matrix(self):
        fixture = load("synthetic-preflight-cases.json")
        now = datetime.fromisoformat(fixture["evaluation_time"].replace("Z", "+00:00"))
        allowed_count = 0
        for case in fixture["cases"]:
            with self.subTest(case=case["name"]):
                request = apply_operations(fixture["base"], case["operations"])
                result = assess_preflight(request, schema_root=SCHEMAS, now=now)
                self.assertEqual(result["decision"], case["decision"])
                self.assertTrue(set(case["expected_codes"]).issubset(result["error_codes"]))
                if case["decision"] == "ISSUE_ALLOWED":
                    allowed_count += 1
                    self.assertEqual(result["result_code"], "RAW_MANIFEST_ISSUABLE")
                    self.assertIsNotNone(result["manifest"])
                    self.assertEqual(result["manifest"]["metadata"]["data_class"], "SYNTHETIC")
                    self.assertEqual(result["assurance_decision"], "HOLD")
                else:
                    self.assertEqual(result["result_code"], "RAW_MANIFEST_HOLD_NOT_ISSUED")
                    self.assertIsNone(result["manifest"])
                    self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertEqual(allowed_count, 1)

    def test_declared_gap_reference_fixtures_are_not_external_verification(self):
        fixture = load("real-candidate-holds.json")
        now = datetime.fromisoformat(fixture["evaluation_time"].replace("Z", "+00:00"))
        for case in fixture["cases"]:
            with self.subTest(case=case["name"]):
                result = assess_preflight(case["request"], schema_root=SCHEMAS, now=now)
                self.assertEqual(result["decision"], case["decision"])
                self.assertEqual(result["result_code"], "RAW_MANIFEST_HOLD_NOT_ISSUED")
                self.assertIn("RAW_MANIFEST_CANDIDATE_MISSING", result["error_codes"])
                self.assertTrue(
                    set(case["request"].get("declared_preflight_gaps", [])).issubset(result["error_codes"])
                )
                self.assertIsNone(result["manifest"])


if __name__ == "__main__":
    unittest.main()
