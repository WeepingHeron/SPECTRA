#!/usr/bin/env python3
"""Validate SPECTRA schemas, composed fixtures, and fail-closed semantic rules."""

from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
VALID_DIR = ROOT / "tests/schema/fixtures/valid"
INVALID_DIR = ROOT / "tests/schema/fixtures/invalid"
PACKET_SCHEMA = SCHEMA_DIR / "evidence-packet.schema.json"

DATA_CLASSES = {"PUBLISHED", "CALCULATED", "ASSUMED", "SYNTHETIC", "CUSTOMER_VERIFIED"}
REVIEW_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "READY_FOR_REVIEW", "VERIFIED", "INTEGRATED", "CHANGES_REQUESTED", "HOLD"}
ASSURANCE_DECISIONS = {"SUPPORTED_WITH_MITIGATION", "CONDITIONAL", "HOLD", "INSUFFICIENT_EVIDENCE"}
PROCESSING_STATUSES = {"VALID", "INVALID_INPUT", "OUT_OF_MODEL_SCOPE", "MODEL_FAILURE", "STALE_EVIDENCE", "PROVENANCE_FAILURE", "CONFLICTING_EVIDENCE"}
OPTIMISTIC = {"SUPPORTED_WITH_MITIGATION"}
SAFE_FAILURE_DECISIONS = {"HOLD", "INSUFFICIENT_EVIDENCE"}
EVIDENTIARY_CLASSES = {"PUBLISHED", "CALCULATED", "CUSTOMER_VERIFIED"}
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
RULE_OPERAND_REQUIREMENTS = {
    "TID_MARGIN_V1": {
        "MISSION_DOSE", "PART_TID_LIMIT", "TID_DESIGN_FACTOR",
        "POLICY_APPROVAL", "SHIELDING_THICKNESS", "MISSION_DURATION",
    },
}
RULE_OPERAND_TARGETS = {
    "MISSION_DOSE": ("RADIATION_ENVIRONMENT", ("mission_dose",)),
    "PART_TID_LIMIT": ("PART_TEST_EVIDENCE", ("tid_test_limit",)),
    "TID_DESIGN_FACTOR": ("USER_POLICY", ("tid_design_factor",)),
    "POLICY_APPROVAL": ("USER_POLICY", ("approval_status",)),
    "SHIELDING_THICKNESS": ("SHIELDING", ("equivalent_thickness",)),
    "MISSION_DURATION": ("MISSION", ("duration",)),
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
            quantity_value = node.get("value")
            if isinstance(quantity_value, (int, float)) and not isinstance(quantity_value, bool):
                if node.get("quantity_kind") == "TID" and quantity_value < 0:
                    codes.add("NEGATIVE_TID")
                if node.get("quantity_kind") == "SHIELDING" and quantity_value <= 0:
                    codes.add("NON_POSITIVE_SHIELDING_THICKNESS")
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
    if any(len(by_kind.get(kind, [])) > 1 for kind in REQUIRED_INPUT_KINDS):
        codes.add("DUPLICATE_REQUIRED_INPUT_KIND")
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

        if assurance in OPTIMISTIC and result.get("outcome") == "PASS":
            required_operands = RULE_OPERAND_REQUIREMENTS.get(rule_id)
            bindings = result.get("operand_bindings", [])
            binding_roles = [binding.get("operand_role") for binding in bindings]
            if required_operands is None:
                codes.add("RULE_OPERAND_CONTRACT_UNKNOWN")
            elif not required_operands.issubset(set(binding_roles)):
                codes.add("RULE_OPERAND_TRACE_MISSING")
            if len(binding_roles) != len(set(binding_roles)):
                codes.add("DUPLICATE_RULE_OPERAND_ROLE")

            for binding in bindings:
                operand_role = binding.get("operand_role")
                input_pointer = binding.get("input_pointer", "")
                origin_pointer = binding.get("origin_pointer", "")
                input_tokens = pointer_tokens(input_pointer)
                operand_value = resolve_pointer(input_pointer)
                operand_origin = resolve_pointer(origin_pointer)
                if operand_value is None or operand_origin is None:
                    codes.add("BROKEN_RULE_OPERAND_POINTER")
                    continue
                metadata = input_metadata(input_tokens)
                if metadata is None:
                    codes.add("RULE_OPERAND_METADATA_MISSING")
                    continue
                if origin_pointer not in allowed_origin_pointers(input_tokens, metadata):
                    codes.add("UNRELATED_RULE_OPERAND_ORIGIN")

                expected_target = RULE_OPERAND_TARGETS.get(operand_role)
                try:
                    input_index = int(input_tokens[1])
                    input_kind = inputs[input_index].get("kind")
                    input_record_metadata = inputs[input_index].get("metadata", {})
                    relative_path = tuple(input_tokens[2:])
                except (IndexError, TypeError, ValueError):
                    input_kind = None
                    input_record_metadata = {}
                    relative_path = ()
                if expected_target is None or (input_kind, relative_path) != expected_target:
                    codes.add("RULE_OPERAND_ROLE_MISMATCH")

                operand_classes = {metadata.get("data_class"), input_record_metadata.get("data_class")}
                if operand_classes.intersection({"SYNTHETIC", "ASSUMED"}):
                    codes.add("NON_EVIDENTIARY_RULE_OPERAND")
                if operand_role in {"TID_DESIGN_FACTOR", "POLICY_APPROVAL"} and "SYNTHETIC" in operand_classes:
                    codes.add("SYNTHETIC_POLICY_WITH_SUPPORT")

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
    required_chain_roles = {"ORBIT", "TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT", "TRANSPORT_DOSE"}

    def parse_timestamp(value):
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    for environment in environments:
        variant = environment.get("environment_variant")
        chain = environment.get("model_chain")
        manifest = environment.get("raw_artifact_manifest")
        environment_class = environment.get("metadata", {}).get("data_class")
        dose = environment.get("mission_dose", environment.get("tid", {}))
        dose_metadata = dose.get("metadata", {}) if isinstance(dose, dict) else {}

        dose_value = dose.get("value") if isinstance(dose, dict) else None
        if isinstance(dose_value, (int, float)) and not isinstance(dose_value, bool) and dose_value < 0:
            codes.add("NEGATIVE_TID")
        thickness_value = environment.get("shielding_point", {}).get("thickness", {}).get("value")
        if isinstance(thickness_value, (int, float)) and not isinstance(thickness_value, bool) and thickness_value <= 0:
            codes.add("NON_POSITIVE_SHIELDING_THICKNESS")

        validity = environment.get("valid_for", {})
        validity_start = parse_timestamp(validity.get("start_at"))
        validity_end = parse_timestamp(validity.get("end_at"))
        if validity_start and validity_end and validity_start > validity_end:
            codes.add("INVALID_VALIDITY_INTERVAL")

        if variant == "TID_ONLY" and "particle_flux" in environment:
            codes.add("TID_ONLY_PLACEHOLDER_FLUX")
        if variant == "TID_ONLY" and environment.get("dose_scope") == "MISSION" and environment.get("source_completeness") != "COMPLETE_MISSION":
            codes.add("INCOMPLETE_MISSION_TID_SOURCE")

        if environment_class == "CALCULATED" and (not chain or not manifest):
            codes.add("CALCULATED_ENVIRONMENT_PROVENANCE_MISSING")
        if assurance in OPTIMISTIC and (not chain or not manifest):
            codes.add("SUPPORT_WITHOUT_ENVIRONMENT_PROVENANCE")

        if variant == "TID_ONLY" and not chain:
            codes.add("MODEL_CHAIN_MISSING")
        if variant == "TID_ONLY" and not manifest:
            codes.add("RAW_ARTIFACT_MANIFEST_MISSING")

        if isinstance(chain, dict):
            stages = chain.get("stages", [])
            stage_ids = [stage.get("stage_id") for stage in stages]
            if len(stage_ids) != len(set(stage_ids)):
                codes.add("DUPLICATE_MODEL_STAGE_ID")
            known_stage_ids = set(stage_ids)
            roles = {stage.get("role") for stage in stages}
            role_by_id = {stage.get("stage_id"): stage.get("role") for stage in stages}
            stages_by_id = {stage.get("stage_id"): stage for stage in stages}
            representative_stage = stages_by_id.get(chain.get("representative_stage_id"))
            if not representative_stage:
                codes.add("REPRESENTATIVE_MODEL_STAGE_MISSING")
            elif variant == "TID_ONLY" and (
                environment.get("model_name") != representative_stage.get("model_name")
                or environment.get("model_version") != representative_stage.get("model_version")
            ):
                codes.add("TOP_LEVEL_MODEL_STAGE_MISMATCH")
            dependencies = {}
            for stage in stages:
                stage_id = stage.get("stage_id")
                if not stage.get("model_version") or not stage.get("model_build"):
                    codes.add("MODEL_STAGE_VERSION_MISSING")
                has_reference = bool(stage.get("configuration_reference"))
                has_hash = bool(stage.get("configuration_hash"))
                if has_reference == has_hash:
                    codes.add("MODEL_STAGE_CONFIG_MISSING")
                depends_on = stage.get("depends_on", [])
                dependencies[stage_id] = depends_on
                if any(parent not in known_stage_ids or parent == stage_id for parent in depends_on):
                    codes.add("BROKEN_MODEL_STAGE_LINK")
                dependency_roles = {role_by_id.get(parent) for parent in depends_on}
                if stage.get("role") == "ORBIT" and depends_on:
                    codes.add("BROKEN_MODEL_STAGE_LINK")
                if stage.get("role") in {"TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT"} and "ORBIT" not in dependency_roles:
                    codes.add("BROKEN_MODEL_STAGE_LINK")

            visiting: set[str] = set()
            visited: set[str] = set()

            def has_cycle(stage_id: str) -> bool:
                if stage_id in visiting:
                    return True
                if stage_id in visited:
                    return False
                visiting.add(stage_id)
                cycle = any(parent in dependencies and has_cycle(parent) for parent in dependencies.get(stage_id, []))
                visiting.remove(stage_id)
                visited.add(stage_id)
                return cycle

            if any(has_cycle(stage_id) for stage_id in dependencies):
                codes.add("BROKEN_MODEL_STAGE_LINK")

            approved_scope = chain.get("approved_scope")
            if approved_scope not in {"MISSION_TID_COMPLETE", "TRAPPED_ONLY_RESEARCH", "PARTIAL_RESEARCH"}:
                codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")
            if variant == "TID_ONLY" and environment.get("dose_scope") == "MISSION":
                if approved_scope != "MISSION_TID_COMPLETE" or not required_chain_roles.issubset(roles):
                    codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")
                transport_stages = [stage for stage in stages if stage.get("role") == "TRANSPORT_DOSE"]
                if not transport_stages or any(
                    {role_by_id.get(parent) for parent in stage.get("depends_on", [])}
                    < {"TRAPPED_ENVIRONMENT", "SOLAR_ENVIRONMENT"}
                    for stage in transport_stages
                ):
                    codes.add("MODEL_CHAIN_OUT_OF_APPROVED_SCOPE")

        if variant == "TID_ONLY" and assurance in OPTIMISTIC and (
            environment.get("dose_scope") != "MISSION"
            or environment.get("source_completeness") != "COMPLETE_MISSION"
        ):
            codes.add("INCOMPLETE_ENVIRONMENT_WITH_SUPPORT")

        if isinstance(manifest, dict):
            if environment.get("run_id") != manifest.get("run_id"):
                codes.add("ENVIRONMENT_MANIFEST_RUN_MISMATCH")
            calculation_run = environment.get("metadata", {}).get("calculation_run", {})
            if calculation_run and environment.get("run_id") != calculation_run.get("run_id"):
                codes.add("ENVIRONMENT_CALCULATION_RUN_MISMATCH")
            dose_calculation_run = dose_metadata.get("calculation_run", {})
            if dose_calculation_run and environment.get("run_id") != dose_calculation_run.get("run_id"):
                codes.add("MISSION_DOSE_RUN_MISMATCH")
            manifest_calculation_run = manifest.get("metadata", {}).get("calculation_run", {})
            if manifest_calculation_run and environment.get("run_id") != manifest_calculation_run.get("run_id"):
                codes.add("MANIFEST_METADATA_RUN_MISMATCH")
            if variant == "TID_ONLY" and any(
                not run for run in (calculation_run, dose_calculation_run, manifest_calculation_run)
            ):
                codes.add("TID_RUN_PROVENANCE_MISSING")
            bundle_hash = manifest.get("bundle_hash")
            parser = manifest.get("parser", {})
            if parser.get("input_bundle_hash") != bundle_hash:
                codes.add("PARSER_BUNDLE_HASH_MISMATCH")
            dose_hash = environment.get("mission_dose", {}).get("metadata", {}).get("content_hash")
            if dose_hash and parser.get("output_hash") != dose_hash:
                codes.add("PARSER_OUTPUT_HASH_MISMATCH")
            dose_output_hash = dose_calculation_run.get("output_hash")
            if dose_hash and dose_output_hash and dose_output_hash != dose_hash:
                codes.add("MISSION_DOSE_OUTPUT_HASH_MISMATCH")
            timestamps = manifest.get("timestamps", {})
            submitted_at = parse_timestamp(timestamps.get("submitted_at"))
            completed_at = parse_timestamp(timestamps.get("completed_at"))
            downloaded_at = parse_timestamp(timestamps.get("downloaded_at"))
            if submitted_at and completed_at and downloaded_at and not (submitted_at <= completed_at <= downloaded_at):
                codes.add("INVALID_PROVIDER_TIMESTAMP_ORDER")
            artifacts = manifest.get("artifacts", [])
            artifact_ids = [artifact.get("artifact_id") for artifact in artifacts]
            if len(artifact_ids) != len(set(artifact_ids)):
                codes.add("DUPLICATE_ARTIFACT_ID")
            for artifact in artifacts:
                content_hash = artifact.get("content_hash")
                if not content_hash:
                    codes.add("ARTIFACT_HASH_MISSING")
                elif not isinstance(content_hash, str) or re.fullmatch(r"sha256:[a-f0-9]{64}", content_hash) is None:
                    codes.add("ARTIFACT_HASH_INVALID")
            provider_outputs = [artifact for artifact in artifacts if artifact.get("role") == "PROVIDER_OUTPUT"]
            if not provider_outputs:
                codes.add("PROVIDER_OUTPUT_ARTIFACT_MISSING")
            elif any(
                not isinstance(artifact.get("byte_size"), int)
                or isinstance(artifact.get("byte_size"), bool)
                or artifact.get("byte_size") <= 0
                or re.fullmatch(r"sha256:[a-f0-9]{64}", artifact.get("content_hash", "")) is None
                or not artifact.get("source_location")
                for artifact in provider_outputs
            ):
                codes.add("PROVIDER_OUTPUT_ARTIFACT_INVALID")
            rights = manifest.get("rights", {})
            claims = manifest.get("usage_claims", {})
            for use in ("research", "commercial", "automation", "redistribution"):
                if claims.get(use) is True and rights.get(use) != "ALLOWED":
                    codes.add("UNCONFIRMED_RIGHTS_CLAIM")

            if assurance in OPTIMISTIC and variant == "TID_ONLY":
                if environment_class not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_ENVIRONMENT_WITH_SUPPORT")
                if dose_metadata.get("data_class") not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_DOSE_WITH_SUPPORT")
                manifest_class = manifest.get("metadata", {}).get("data_class")
                if manifest_class not in EVIDENTIARY_CLASSES:
                    codes.add("NON_EVIDENTIARY_MANIFEST_WITH_SUPPORT")

                required_rights = {"research"}
                if manifest.get("execution_mode") == "AUTOMATED":
                    required_rights.add("automation")
                distribution_scope = manifest.get("distribution_scope")
                if distribution_scope in {"EXTERNAL_RESEARCH", "COMMERCIAL_PRODUCT"}:
                    required_rights.add("redistribution")
                if distribution_scope == "COMMERCIAL_PRODUCT":
                    required_rights.add("commercial")
                if any(rights.get(required) != "ALLOWED" for required in required_rights):
                    codes.add("REQUIRED_RIGHT_NOT_ALLOWED")

    evidences = by_kind.get("PART_TEST_EVIDENCE", [])
    if environments and evidences and policies:
        tid = environments[0].get("tid", environments[0].get("mission_dose", {}))
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


def load_fixture(path: Path) -> dict:
    document = load(path)
    if "base" in document and "operations" in document:
        base = load_fixture((path.parent / document["base"]).resolve())
        return apply_operations(base, document["operations"])
    return document


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
    cardinality_rules = packet_schema["properties"]["inputs"]["allOf"]
    exact_one_kinds = {
        rule["contains"]["properties"]["kind"]["const"]
        for rule in cardinality_rules
        if rule.get("minContains") == 1 and rule.get("maxContains") == 1
    }
    if exact_one_kinds != REQUIRED_INPUT_KINDS:
        failures.append(
            f"input cardinality: expected exact-one {sorted(REQUIRED_INPUT_KINDS)}, got {sorted(exact_one_kinds)}"
        )
    print("INPUT CARDINALITY: 7 required kinds exact-one")
    registry = build_registry(loaded_schemas)
    valid_files = sorted(VALID_DIR.glob("*.json"))
    for path in valid_files:
        packet = load_fixture(path)
        errors = schema_errors(packet, packet_schema, registry)
        codes = semantic_codes(packet)
        if errors or codes:
            failures.append(f"valid {path.name}: schema={errors} semantic={sorted(codes)}")
    print(f"VALID FIXTURES: {len(valid_files)} passed")

    invalid_count = 0
    for case_path in sorted(INVALID_DIR.glob("*.json")):
        case_doc = load(case_path)
        base = load_fixture((case_path.parent / case_doc["base"]).resolve())
        for case in case_doc["cases"]:
            invalid_count += 1
            packet = apply_operations(base, case["operations"])
            errors = schema_errors(packet, packet_schema, registry)
            codes = semantic_codes(packet)
            if not errors and not codes:
                failures.append(f"invalid {case['name']}: unexpectedly passed")
            if case["expected"] not in codes:
                failures.append(f"invalid {case['name']}: expected {case['expected']}, got schema={errors} semantic={sorted(codes)}")
    print(f"INVALID FIXTURES: {invalid_count} rejected with expected codes")

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("RESULT: READY_FOR_REVIEW candidate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
