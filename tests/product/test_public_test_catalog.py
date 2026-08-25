#!/usr/bin/env python3
"""Validate public test catalog classification, paths, and audit hash chain."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_public_test_catalog import build_catalog, canonical  # noqa: E402


class PublicTestCatalogTests(unittest.TestCase):
    def test_catalog_has_three_input_roles_and_no_false_approval(self) -> None:
        catalog, audit = build_catalog("2026-08-25T08:00:00Z")
        roles = {item["document_role"] for item in catalog["documents"]}
        self.assertTrue({"MISSION_PLAN", "PART_SPEC", "RADIATION_TEST"} <= roles)
        self.assertEqual(catalog["summary"]["assurance_approved_count"], 0)
        self.assertTrue(
            all(item["assurance_decision"] == "HOLD" for item in catalog["documents"])
        )
        synthetic = next(
            item for item in catalog["bundles"] if item["bundle_id"] == "BUNDLE-SYNTHETIC-CORE"
        )
        self.assertEqual(synthetic["pipeline_result"], "PIPELINE_COMPLETE")
        self.assertEqual(synthetic["assurance_decision"], "HOLD")
        actual = next(
            item
            for item in catalog["bundles"]
            if item["bundle_id"] == "BUNDLE-LANDSAT-MICROCHIP-NASA-MICRON"
        )
        self.assertEqual(actual["first_blocker"], "EXACT_PART_IDENTITY_MISMATCH")
        self.assertEqual(actual["hold_agent"], "PARTS_AGENT")
        landsat = next(
            item for item in catalog["documents"] if item["document_id"] == "DOC-013"
        )
        self.assertEqual(landsat["partial_evaluation"]["hold_agent"], "MISSION_AGENT")
        self.assertGreater(
            landsat["partial_evaluation"]["validated_check_count"], 0
        )
        self.assertEqual(landsat["partial_evaluation"]["failed_check_count"], 0)
        self.assertEqual(audit["events"][-1]["event_type"], "CATALOG_SUBMITTED")

    def test_audit_chain_is_exact_and_catalog_bound(self) -> None:
        catalog, audit = build_catalog("2026-08-25T08:00:00Z")
        expected_catalog_hash = "sha256:" + hashlib.sha256(canonical(catalog)).hexdigest()
        self.assertEqual(audit["catalog_sha256"], expected_catalog_hash)
        previous = "sha256:" + "0" * 64
        for event in audit["events"]:
            self.assertEqual(event["previous_event_hash"], previous)
            core = {key: value for key, value in event.items() if key != "event_hash"}
            expected = "sha256:" + hashlib.sha256(canonical(core)).hexdigest()
            self.assertEqual(event["event_hash"], expected)
            previous = expected
        self.assertEqual(audit["chain_head"], previous)


if __name__ == "__main__":
    unittest.main()
