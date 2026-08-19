#!/usr/bin/env python3
"""Validate SPECTRA schemas, composed fixtures, and fail-closed semantic rules."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
VALID_DIR = ROOT / "tests/schema/fixtures/valid"
CASES_FILE = ROOT / "tests/schema/fixtures/invalid/cases.json"
PACKET_SCHEMA = SCHEMA_DIR / "evidence-packet.schema.json"

DATA_CLASSES = {"PUBLISHED", "CALCULATED", "ASSUMED", "SYNTHETIC", "CUSTOMER_VERIFIED"}
REVIEW_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "READY_FOR_REVIEW", "VERIFIED", "INTEGRATED", "CHANGES_REQUESTED", "HOLD"}
ASSURANCE_DECISIONS = {"SUPPORTED_WITH_MITIGATION", "CONDITIONAL", "HOLD", "INSUFFICIENT_EVIDENCE"}
PROCESSING_STATUSES = {"VALID", "INVALID_INPUT", "OUT_OF_MODEL_SCOPE", "MODEL_FAILURE", "STALE_EVIDENCE", "PROVENANCE_FAILURE", "CONFLICTING_EVIDENCE"}
OPTIMISTIC = {"SUPPORTED_WITH_MITIGATION"}
SAFE_FAILURE_DECISIONS = {"HOLD", "INSUFFICIENT_EVIDENCE"}
UNIT_MAP = {
    "TID": {"rad(Si)", "krad(Si)", "Gy(Si)"},
    "SHIELDING": {"mm_Al_equivalent", "g/cm2"},
    "DURATION": {"s", "day", "year"},
    "PARTICLE_FLUX": {"particles/cm2/s"},
    "CROSS_SECTION": {"cm2/device", "cm2/bit"},
    "ALTITUDE": {"km", "m"},
    "ANGLE": {"deg"},
    "COUNT": {"count"},
    "RATE": {"events/day", "events/mission"},
}
REQUIRED_INPUT_KINDS = {
    "MISSION", "BOM", "RADIATION_ENVIRONMENT", "PART_TEST_EVIDENCE",
    "SHIELDING", "MITIGATION", "USER_POLICY",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def preflight_codes(packet: dict) -> set[str]:
    codes: set[str] = set()
    for node in walk(packet):
        if "quantity_kind" in node:
            if "unit" not in node:
                codes.add("MISSING_UNIT")
            elif node["unit"] not in UNIT_MAP.get(node["quantity_kind"], set()):
                codes.add("INCOMPATIBLE_UNIT")
        if "data_class" in node:
            data_class = node.get("data_class")
            if data_class not in DATA_CLASSES:
                codes.add("INVALID_DATA_CLASS")
            if "content_hash" not in node:
                codes.add("MISSING_CONTENT_HASH")
            if data_class in {"PUBLISHED", "CUSTOMER_VERIFIED", "ASSUMED"} and "source" not in node:
                codes.add("MISSING_SOURCE")
            if data_class in {"CALCULATED", "SYNTHETIC"} and "calculation_run" not in node:
                codes.add("MISSING_CALCULATION_RUN")
            source = node.get("source")
            if isinstance(source, dict) and not source.get("location"):
                codes.add("MISSING_SOURCE_LOCATION")
            if data_class != "SYNTHETIC" and isinstance(source, dict) and source.get("source_type") == "FIXTURE_SPEC":
                codes.add("SYNTHETIC_MISREPRESENTED")
    return codes


def semantic_codes(packet: dict) -> set[str]:
    codes = preflight_codes(packet)
    inputs = packet.get("inputs", [])
    by_kind = {}
    for item in inputs:
        by_kind.setdefault(item.get("kind"), []).append(item)
    if not REQUIRED_INPUT_KINDS.issubset(by_kind):
        codes.add("REQUIRED_INPUT_KIND_MISSING")
    decision = packet.get("decision", {})
    processing = decision.get("processing_status")
    assurance = decision.get("assurance_decision")

    if processing and processing != "VALID" and assurance not in SAFE_FAILURE_DECISIONS:
        codes.add("PROCESSING_DECISION_CONFLICT")

    def pointer_tokens(pointer: str) -> list[str]:
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            return []
        return [token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:]]

    def resolve_tokens(tokens: list[str]):
        current = packet
        try:
            for token in tokens:
                current = current[int(token)] if isinstance(current, list) else current[token]
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def resolve_pointer(pointer: str):
        return resolve_tokens(pointer_tokens(pointer))

    def encode_pointer(tokens: list[str]) -> str:
        return "/" + "/".join(token.replace("~", "~0").replace("/", "~1") for token in tokens)

    def input_metadata(tokens: list[str]):
        if len(tokens) < 2 or tokens[0] != "inputs":
            return None
        for depth in range(len(tokens), 1, -1):
            prefix = tokens[:depth]
            node = resolve_tokens(prefix)
            if not isinstance(node, dict):
                continue
            if "data_class" in node:
                return node
            metadata = node.get("metadata")
            if isinstance(metadata, dict) and "data_class" in metadata:
                return metadata
        return None

    def allowed_origin_pointers(tokens: list[str], metadata: dict) -> set[str]:
        data_class = metadata.get("data_class")
        origin_key = "source" if data_class in {"PUBLISHED", "CUSTOMER_VERIFIED", "ASSUMED"} else "calculation_run"
        expected_origin = metadata.get(origin_key)
        if expected_origin is None:
            return set()
        allowed = set()
        for depth in range(len(tokens), 1, -1):
            prefix = tokens[:depth]
            node = resolve_tokens(prefix)
            if not isinstance(node, dict):
                continue
            if node.get(origin_key) == expected_origin:
                allowed.add(encode_pointer(prefix + [origin_key]))
            candidate_metadata = node.get("metadata")
            if isinstance(candidate_metadata, dict) and candidate_metadata.get(origin_key) == expected_origin:
                allowed.add(encode_pointer(prefix + ["metadata", origin_key]))
        return allowed

    traces = packet.get("trace", [])
    trace_ids = [trace.get("trace_id") for trace in traces]
    if len(trace_ids) != len(set(trace_ids)):
        codes.add("DUPLICATE_TRACE_ID")
    traces_by_id = {}
    source_class_by_trace = {}
    for trace in traces:
        traces_by_id.setdefault(trace.get("trace_id"), []).append(trace)
        input_pointer = trace.get("input_pointer", "")
        origin_pointer = trace.get("origin_pointer", "")
        input_tokens = pointer_tokens(input_pointer)
        input_value = resolve_pointer(input_pointer)
        origin_value = resolve_pointer(origin_pointer)
        if input_value is None or origin_value is None:
            codes.add("BROKEN_TRACE_POINTER")
            continue
        metadata = input_metadata(input_tokens)
        if metadata is None:
            codes.add("TRACE_INPUT_METADATA_MISSING")
            continue
        source_class_by_trace[id(trace)] = metadata.get("data_class")
        if origin_pointer not in allowed_origin_pointers(input_tokens, metadata):
            codes.add("UNRELATED_TRACE_ORIGIN")
    has_decision_trace = any(trace.get("used_for_decision") for trace in traces)
    rule_results = decision.get("rule_results", [])
    rule_ids = [result.get("rule_id") for result in rule_results]
    if len(rule_ids) != len(set(rule_ids)):
        codes.add("DUPLICATE_RULE_ID")
    for result in rule_results:
        rule_id = result.get("rule_id")
        referenced_ids = result.get("trace_ids", [])
        if not referenced_ids:
            codes.add("RULE_WITHOUT_TRACE")
            continue

        referenced_traces = []
        missing_reference = False
        for trace_id in referenced_ids:
            matches = traces_by_id.get(trace_id, [])
            if not matches:
                missing_reference = True
                codes.add("BROKEN_DECISION_TRACE")
            referenced_traces.extend(matches)
        if missing_reference:
            continue

        if any(rule_id not in trace.get("decision_rule_ids", []) for trace in referenced_traces):
            codes.add("RULE_TRACE_MISMATCH")
            continue

        if assurance in OPTIMISTIC and any(
            trace.get("applicability", {}).get("status") != "APPLICABLE" for trace in referenced_traces
        ):
            codes.add("DECISION_TRACE_NOT_APPLICABLE")

        if assurance in OPTIMISTIC and result.get("outcome") == "PASS" and has_decision_trace and not any(
            trace.get("used_for_decision") for trace in referenced_traces
        ):
            codes.add("SUPPORT_RULE_WITHOUT_DECISION_TRACE")

    policies = by_kind.get("USER_POLICY", [])
    if assurance in OPTIMISTIC and (not policies or any(p.get("approval_status") != "APPROVED" for p in policies)):
        codes.add("UNAPPROVED_POLICY_SUPPORT")

    if assurance in OPTIMISTIC:
        decision_traces = [trace for trace in traces if trace.get("used_for_decision")]
        if not decision_traces:
            codes.add("SUPPORT_WITHOUT_DECISION_TRACE")
        if any(result.get("outcome") != "PASS" for result in decision.get("rule_results", [])):
            codes.add("NON_PASS_RULE_WITH_SUPPORT")
        for trace in decision_traces:
            if trace.get("applicability", {}).get("status") != "APPLICABLE":
                codes.add("DECISION_TRACE_NOT_APPLICABLE")
            metadata = trace.get("normalized_value", {}).get("metadata", {})
            if metadata.get("data_class") in {"SYNTHETIC", "ASSUMED"}:
                codes.add("NON_EVIDENTIARY_DECISION_INPUT")
            if source_class_by_trace.get(id(trace)) in {"SYNTHETIC", "ASSUMED"}:
                codes.add("NON_EVIDENTIARY_SOURCE_INPUT")
        if any(gap.get("blocking") for gap in decision.get("evidence_gaps", [])):
            codes.add("BLOCKING_GAP_WITH_SUPPORT")

    component_by_id = {}
    for bom in by_kind.get("BOM", []):
        for component in bom.get("components", []):
            component_by_id[component.get("component_id")] = component
    identity_fields = ("manufacturer", "part_number", "process_id", "die_revision", "lot_id", "date_code")
    for evidence in by_kind.get("PART_TEST_EVIDENCE", []):
        component = component_by_id.get(evidence.get("component_id"))
        if not component:
            codes.add("EVIDENCE_COMPONENT_NOT_FOUND")
            continue
        expected = component.get("identity", {})
        tested = evidence.get("tested_identity", {})
        if any(expected.get(field) != tested.get(field) for field in identity_fields if expected.get(field) or tested.get(field)):
            codes.add("PART_IDENTITY_MISMATCH")

    require_destructive = any(p.get("require_destructive_see_evidence") for p in policies)
    if require_destructive:
        destructive = {"SEL", "SEB", "SEGR"}
        for evidence in by_kind.get("PART_TEST_EVIDENCE", []):
            if not destructive.intersection(evidence.get("evidence_types", [])):
                codes.add("DESTRUCTIVE_SEE_EVIDENCE_MISSING")

    environments = by_kind.get("RADIATION_ENVIRONMENT", [])
    evidences = by_kind.get("PART_TEST_EVIDENCE", [])
    if environments and evidences and policies:
        tid = environments[0].get("tid", {})
        limit = evidences[0].get("tid_test_limit", {})
        factor = policies[0].get("tid_design_factor")
        if tid.get("unit") == limit.get("unit") and isinstance(factor, (int, float)):
            if tid.get("value", 0) * factor > limit.get("value", float("-inf")):
                codes.add("TEST_RANGE_EXCEEDED")
    return codes


def build_registry(schemas: list[dict]) -> Registry:
    resources = [(schema["$id"], Resource.from_contents(schema)) for schema in schemas]
    return Registry().with_resources(resources)


def schema_errors(packet: dict, schema: dict, registry: Registry) -> list[str]:
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    return [f"/{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in validator.iter_errors(packet)]


def apply_operations(base: dict, operations: list[dict]) -> dict:
    value = copy.deepcopy(base)
    for operation in operations:
        parts = [part.replace("~1", "/").replace("~0", "~") for part in operation["path"].split("/")[1:]]
        parent = value
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        key = parts[-1]
        if isinstance(parent, list) and key != "-":
            key = int(key)
        if operation["op"] == "set":
            parent[key] = operation["value"]
        elif operation["op"] == "delete":
            del parent[key]
        elif operation["op"] == "copy":
            source = value
            for source_part in operation["from"].split("/")[1:]:
                source_part = source_part.replace("~1", "/").replace("~0", "~")
                source = source[int(source_part)] if isinstance(source, list) else source[source_part]
            if isinstance(parent, list) and key == "-":
                parent.append(copy.deepcopy(source))
            else:
                parent[key] = copy.deepcopy(source)
        else:
            raise ValueError(f"Unsupported fixture operation: {operation['op']}")
    return value


def main() -> int:
    failures: list[str] = []
    schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
    loaded_schemas = []
    for path in schemas:
        try:
            schema = load(path)
            Draft202012Validator.check_schema(schema)
            loaded_schemas.append(schema)
        except Exception as exc:
            failures.append(f"schema {path.name}: {exc}")
    print(f"SCHEMAS: {len(schemas)} checked")

    common_schema = load(SCHEMA_DIR / "common.schema.json")
    enum_contracts = {
        "dataClass": DATA_CLASSES,
        "reviewStatus": REVIEW_STATUSES,
        "assuranceDecision": ASSURANCE_DECISIONS,
        "processingStatus": PROCESSING_STATUSES,
    }
    for definition, expected in enum_contracts.items():
        actual = set(common_schema["$defs"][definition]["enum"])
        if actual != expected:
            failures.append(f"enum {definition}: expected {sorted(expected)}, got {sorted(actual)}")
    print("ENUM CONTRACTS: 4 axes checked")

    packet_schema = load(PACKET_SCHEMA)
    registry = build_registry(loaded_schemas)
    valid_files = sorted(VALID_DIR.glob("*.json"))
    for path in valid_files:
        packet = load(path)
        errors = schema_errors(packet, packet_schema, registry)
        codes = semantic_codes(packet)
        if errors or codes:
            failures.append(f"valid {path.name}: schema={errors} semantic={sorted(codes)}")
    print(f"VALID FIXTURES: {len(valid_files)} passed")

    case_doc = load(CASES_FILE)
    base = load((CASES_FILE.parent / case_doc["base"]).resolve())
    for case in case_doc["cases"]:
        packet = apply_operations(base, case["operations"])
        errors = schema_errors(packet, packet_schema, registry)
        codes = semantic_codes(packet)
        if not errors and not codes:
            failures.append(f"invalid {case['name']}: unexpectedly passed")
        if case["expected"] not in codes:
            failures.append(f"invalid {case['name']}: expected {case['expected']}, got schema={errors} semantic={sorted(codes)}")
    print(f"INVALID FIXTURES: {len(case_doc['cases'])} rejected with expected codes")

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("RESULT: READY_FOR_REVIEW candidate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
