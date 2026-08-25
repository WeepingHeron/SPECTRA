#!/usr/bin/env python3
"""Serve the SPECTRA Evidence Console without triggering GCP mutations.

POST /api/intake streams JSONL events from the real local PDF/TXT intake path.
GET /api/gcp-snapshot-logs returns the stored H05 Cloud Logging evidence only.
GET /api/mission-case-demo runs the deterministic multi-document Mission Case Core.
GET /api/review-impact-demo runs the deterministic change-impact classifier.
The default bind is loopback. Cloud Run may set HOST=0.0.0.0 and PORT.
Uploaded bytes are processed in a temporary directory and are not persisted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator


def _add_bundled_pdf_packages() -> None:
    """Expose the bundled pure-Python PDF package without replacing this runtime."""
    try:
        import pypdf  # noqa: F401

        return
    except ModuleNotFoundError:
        pass
    site_packages = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages"
    )
    if site_packages.is_dir():
        sys.path.append(str(site_packages))


_add_bundled_pdf_packages()

from intake_local_document_candidate import MAX_BYTES, intake_document
from spectra_sim import synthesize_mission_case
from spectra_value_proof import classify_review_impact, source_sha256


REPO_ROOT = Path(__file__).resolve().parents[1]
GCP_LOG_EVIDENCE = (
    REPO_ROOT
    / "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json"
)
GCP_SNAPSHOT = REPO_ROOT / "demo/data/h05-gcp-snapshot.json"
ALLOWED_SUFFIXES = frozenset({".pdf", ".txt"})
SYNTHETIC_MODEL = REPO_ROOT / "simulation/config/synthetic-model.json"
MISSION_EVENTS = ("TID", "SEU", "SEL", "SEB", "SEGR")
MISSION_IDENTITY_FIELDS = (
    "manufacturer",
    "orderable_part_number",
    "package",
    "process",
    "die",
    "lot",
)
STAGE_AGENT = {
    "INGEST": "INTAKE_GATEWAY",
    "DOCUMENT_PARSER": "LOCAL_DOCUMENT_GATE",
    "ENVIRONMENT_REVIEW": "MISSION_AGENT",
    "PARTS_REVIEW": "PARTS_AGENT",
    "ASSURANCE": "ASSURANCE_AGENT",
    "DECISION": "DETERMINISTIC_CORE",
}


def _json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _event(
    sequence: int,
    run_id: str,
    stage: str,
    event: str,
    status: str,
    message: str,
    **evidence: Any,
) -> dict[str, Any]:
    return {
        "event_version": "1.0.0",
        "sequence": sequence,
        "run_id": run_id,
        "stage": stage,
        "agent_role": STAGE_AGENT.get(stage, "SYSTEM"),
        "event": event,
        "status": status,
        "message": message,
        "evidence": evidence,
    }


def local_intake_events(
    filename: str,
    content: bytes,
    *,
    expected_part: str,
    manufacturer: str | None,
    local_review_rights_confirmed: bool,
) -> Iterator[dict[str, Any]]:
    """Run the real local intake and emit its unedited event payloads in order."""
    safe_name = Path(filename).name
    suffix = Path(safe_name).suffix.lower()
    digest = hashlib.sha256(content).hexdigest()
    run_id = f"local-{digest[:16]}"
    sequence = 1
    yield _event(
        sequence,
        run_id,
        "INGEST",
        "run.started",
        "RUNNING",
        "문서 검사를 시작했습니다.",
        filename=safe_name,
        byte_count=len(content),
        content_sha256=f"sha256:{digest}",
        decision_use=False,
    )
    sequence += 1

    if suffix not in ALLOWED_SUFFIXES:
        yield _event(
            sequence,
            run_id,
            "INGEST",
            "run.blocked",
            "DATA_UNAVAILABLE",
            "지원하지 않는 파일 형식입니다.",
            stable_code="DOCUMENT_TYPE_UNSUPPORTED",
            assurance_decision="HOLD",
        )
        return
    if not content or len(content) > MAX_BYTES:
        yield _event(
            sequence,
            run_id,
            "INGEST",
            "run.blocked",
            "DATA_UNAVAILABLE",
            "파일 크기가 허용 범위를 벗어났습니다.",
            stable_code="DOCUMENT_SIZE_OUT_OF_RANGE",
            assurance_decision="HOLD",
        )
        return

    yield _event(
        sequence,
        run_id,
        "DOCUMENT_PARSER",
        "parser.started",
        "RUNNING",
        "PDF/TXT 텍스트와 원문 지문을 추출합니다.",
        suffix=suffix,
        raw_path_exposed=False,
        raw_text_exposed=False,
    )
    sequence += 1

    with tempfile.TemporaryDirectory(prefix="spectra-console-") as directory:
        document = Path(directory) / ("document" + suffix)
        document.write_bytes(content)
        receipt = intake_document(
            document,
            expected_part=expected_part,
            manufacturer=manufacturer,
            local_review_rights_confirmed=local_review_rights_confirmed,
        )

    source = receipt.get("source", {})
    yield _event(
        sequence,
        run_id,
        "DOCUMENT_PARSER",
        "parser.completed",
        receipt["processing_status"],
        "파서가 판단에 바로 사용할 수 없는 추출 후보 기록을 생성했습니다.",
        extraction_status=receipt["extraction_status"],
        extraction_engine=source.get("extraction_engine"),
        page_count=source.get("page_count"),
        candidate_count=receipt["candidate_count"],
        blocker_codes=receipt["blocker_codes"],
        assurance_decision=receipt["assurance_decision"],
        used_for_decision=receipt["used_for_decision"],
    )
    sequence += 1

    for candidate in receipt.get("candidates", []):
        yield _event(
            sequence,
            run_id,
            "DOCUMENT_PARSER",
            "candidate.found",
            candidate["candidate_status"],
            "원문 위치에 결속된 미승인 후보를 찾았습니다.",
            candidate_id=candidate["candidate_id"],
            field=candidate["field"],
            value=candidate["value"],
            unit=candidate["unit"],
            source_span=candidate["source_span"],
        )
        sequence += 1

    summary = receipt["review_summary"]
    ledger = receipt["partial_evaluation"]
    if receipt["processing_status"] == "VALID":
        for agent_role, stage in (
            ("MISSION_AGENT", "ENVIRONMENT_REVIEW"),
            ("PARTS_AGENT", "PARTS_REVIEW"),
        ):
            validated = [
                item for item in ledger["validated_checks"]
                if item["agent_role"] == agent_role
            ]
            failed = [
                item for item in ledger["failed_checks"]
                if item["agent_role"] == agent_role
            ]
            if not validated and not failed:
                continue
            yield _event(
                sequence,
                run_id,
                stage,
                "partial_checks.completed",
                "FAILED" if failed else "VALID",
                (
                    f"누락된 다른 입력과 무관하게 확인 가능한 {len(validated) + len(failed)}개 "
                    f"항목을 검사했습니다. {len(validated)}개 확인, {len(failed)}개 불일치입니다."
                ),
                agent_role=agent_role,
                validated_checks=validated,
                failed_checks=failed,
                claim_boundary="BOUNDED_CHECKS_NOT_MISSION_SUITABILITY",
            )
            sequence += 1
    if receipt["processing_status"] == "VALID":
        fields = set(receipt.get("candidate_fields", []))
        mission_fields = {
            "MISSION_NAME",
            "ORBIT_REGIME",
            "ORBIT_ALTITUDE",
            "ORBIT_INCLINATION",
            "MISSION_DURATION",
            "SHIELDING_THICKNESS",
        }
        radiation_fields = {
            "TID_DOSE",
            "DOSE_RATE",
            "SEE_LET",
            "SEE_CROSS_SECTION",
            "PARTICLE_FLUENCE",
            "PARTICLE_ENERGY",
            "EVIDENCE_EVENT_MENTION",
        }
        if fields & mission_fields and not fields & radiation_fields:
            review_stage = "ENVIRONMENT_REVIEW"
            review_event = "environment_link.blocked"
            review_code = "RADIATION_ENVIRONMENT_MISSING"
        elif fields & {"ORDERABLE_PART_NUMBER", "MANUFACTURER", "SUPPLY_VOLTAGE"} and not fields & radiation_fields:
            review_stage = "PARTS_REVIEW"
            review_event = "evidence_link.blocked"
            review_code = "RADIATION_TEST_EVIDENCE_MISSING"
        else:
            review_stage = "PARTS_REVIEW"
            review_event = "approved_target.blocked"
            review_code = "APPROVED_BOM_TARGET_MISSING"
        if ledger["failed_checks"]:
            review_code = ledger["failed_checks"][0]["stable_codes"][-1]
        yield _event(
            sequence,
            run_id,
            review_stage,
            review_event,
            "NOT_EVALUATED",
            summary["blocking_reason"],
            stable_code=review_code,
            problem_location=summary["problem_location"],
            confirmed_facts=summary["confirmed_facts"],
            assurance_decision="HOLD",
        )
        sequence += 1
    else:
        yield _event(
            sequence,
            run_id,
            "PARTS_REVIEW",
            "review.not_called",
            "NOT_CALLED",
            "문서 입력 단계가 닫혀 부품 검토를 호출하지 않았습니다.",
            blocker_codes=receipt["blocker_codes"],
            assurance_decision="HOLD",
        )
        sequence += 1

    yield _event(
        sequence,
        run_id,
        "ASSURANCE",
        "assurance.partial_review.completed",
        "HOLD",
        "확인·불일치·추가 입력 필요 결과를 대조하고 최종 보류를 확인했습니다.",
        upstream_status=receipt["processing_status"],
        validated_check_count=len(ledger["validated_checks"]),
        failed_check_count=len(ledger["failed_checks"]),
        not_evaluated_check_count=len(ledger["not_evaluated_checks"]),
        hold_agent=ledger["hold_agent"],
        assurance_decision="HOLD",
    )
    sequence += 1
    yield _event(
        sequence,
        run_id,
        "DECISION",
        "decision.completed",
        "HOLD",
        summary["headline"],
        processing_status=receipt["processing_status"],
        problem_location=summary["problem_location"],
        confirmed_facts=summary["confirmed_facts"],
        blocking_reason=summary["blocking_reason"],
        next_action=summary["next_action"],
        validation_results=summary["validation_results"],
        validated_check_count=summary["validated_check_count"],
        failed_check_count=summary["failed_check_count"],
        not_evaluated_check_count=summary["not_evaluated_check_count"],
        hold_agent=summary["hold_agent"],
        approval_status="NOT_EVALUATED",
        use_status="NOT_FOR_DECISION",
        assurance_decision="HOLD",
    )


def _artifact_sha256(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _synthetic_identity() -> dict[str, str]:
    return {
        "manufacturer": "Example Semiconductor",
        "orderable_part_number": "EX-100-A",
        "package": "QFP-64",
        "process": "CMOS-65NM",
        "die": "DIE-A",
        "lot": "LOT-A",
    }


def _mission_source(
    source_id: str,
    document_id: str,
    claim_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    artifact_sha256 = _artifact_sha256(document_id)
    return {
        "source_id": source_id,
        "document_id": document_id,
        "mission_case_id": "console-mission-case",
        "data_class": "SYNTHETIC",
        "artifact_sha256": artifact_sha256,
        "observed_artifact_sha256": artifact_sha256,
        "locator": f"synthetic://mission-case/{document_id}",
        "claims": [
            {
                "claim_id": claim_id,
                "component_id": "component-001",
                "tested_identity": _synthetic_identity(),
                "test_conditions": {},
                "event_evidence": events,
            }
        ],
    }


def _mission_event(event_type: str, locator: str, **values: Any) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "source_event_type": event_type,
        "locator": locator,
        **values,
    }


def build_mission_case_demo_input() -> dict[str, Any]:
    """Return the fixed synthetic console input, never an actual evidence claim."""

    return {
        "contract_version": "MISSION_CASE_1.0.0",
        "mission_case_id": "console-mission-case",
        "data_class": "SYNTHETIC",
        "mission_conditions": {
            "mission_id": "synthetic-leo-001",
            "duration": {"value": 1, "unit": "year"},
            "environment_tid": {"value": 10, "unit": "krad(Si)"},
            "particle_flux": {"value": 1000, "unit": "particles/cm2/s"},
            "shielding": {"value": 2, "unit": "mm_Al_equivalent"},
            "tid_design_factor": 2,
            "analysis_device_count": 2,
        },
        "approved_bom_targets": [
            {
                "component_id": "component-001",
                "approval_status": "APPROVED",
                "identity": _synthetic_identity(),
            }
        ],
        "sources": [
            _mission_source(
                "source-tid",
                "synthetic-tid-report",
                "claim-tid",
                [
                    _mission_event(
                        "TID",
                        "synthetic://mission-case/tid#page=3",
                        tid_test_limit={"value": 25, "unit": "krad(Si)"},
                    )
                ],
            ),
            _mission_source(
                "source-seu",
                "synthetic-seu-report",
                "claim-seu",
                [
                    _mission_event(
                        "SEU",
                        "synthetic://mission-case/seu#table=2",
                        cross_section={"value": 1e-6, "unit": "cm2/device"},
                    )
                ],
            ),
            _mission_source(
                "source-destructive",
                "synthetic-destructive-see-report",
                "claim-destructive",
                [
                    _mission_event("SEL", "synthetic://mission-case/see#sel"),
                    _mission_event("SEB", "synthetic://mission-case/see#seb"),
                    _mission_event("SEGR", "synthetic://mission-case/see#segr"),
                ],
            ),
        ],
    }


def load_mission_case_demo() -> dict[str, Any]:
    model = json.loads(SYNTHETIC_MODEL.read_text(encoding="utf-8"))
    result = synthesize_mission_case(build_mission_case_demo_input(), model)
    identity = result["questions"]["exact_part_identity"]
    applicability = result["questions"]["mission_test_applicability"]
    coverage = result["questions"]["event_coverage"]
    calculations = {item["event_type"]: item for item in result["applicability_calculations"]}
    events = [
        _event(1, "mission-case-demo", "INPUT", "mission_case.started", "VALID", "임무 조건·승인 BOM·합성 시험 문서 3개를 한 Mission Case로 결속했습니다.", detail="문서 3개 · source hash/locator 유지 · 실제 증거 아님"),
        _event(2, "mission-case-demo", "EXACT IDENTITY", "identity.completed", identity["status"], "승인 부품과 각 시험품의 정확한 식별 정보를 비교했습니다.", detail="manufacturer · orderable PN · package · process · die · lot 모두 일치"),
        _event(3, "mission-case-demo", "TID / SEU", "bounded_calculation.completed", "VALID", "기존 결정론적 Core로 TID 시험 범위와 SEU 예상 사건 수를 계산했습니다.", detail=f"TID {calculations['TID']['status']} · SEU {calculations['SEU']['raw_events_per_mission']:.6f} events/mission (SYNTHETIC)"),
        _event(4, "mission-case-demo", "EVENT COVERAGE", "coverage.completed", coverage["status"], "사건별 근거 위치를 서로 합치거나 대체하지 않고 확인했습니다.", detail="TID · SEU · SEL · SEB · SEGR 5/5 source-local coverage"),
        _event(5, "mission-case-demo", "APPLICABILITY", "applicability.blocked", applicability["status"], "현재 모델로 비교할 수 없는 시험 조건과 파괴성 SEE 적용성을 추정하지 않았습니다.", blocker_codes=applicability["blocker_codes"]),
        _event(6, "mission-case-demo", "DECISION", "decision.completed", "HOLD", "근거 연결은 완료됐지만 현재 임무에 쓸 수 있다는 판단은 보류했습니다.", stable_code="MISSION_TEST_APPLICABILITY_NOT_EVALUATED"),
    ]
    return {
        "boundary": {
            "data_class": "SYNTHETIC",
            "actual_evidence": 0,
            "assurance_decision": "HOLD",
            "parser_wired": False,
        },
        "events": events,
        "summary": {
            "headline": "부품과 사건별 근거는 연결됐지만, 시험 조건 적용성은 판단 보류",
            "decision": "VALID · NOT_EVALUATED · HOLD",
            "problem_location": "Mission Case · 시험 조건 적용성",
            "confirmed_facts": [
                "승인 부품과 시험품의 정확한 식별 6개 필드가 일치합니다.",
                "TID·SEU는 기존 결정론적 Core 계산을 재사용했습니다.",
                "TID·SEU·SEL·SEB·SEGR 근거 위치를 5/5로 연결했습니다.",
            ],
            "blocking_reason": "입자종·에너지·LET·fluence·온도·bias와 파괴성 SEE 적용성을 현재 모델이 비교하지 못합니다.",
            "next_action": "시험 조건과 파괴성 SEE 적용성을 독립 검토하고, 지원 모델이 없으면 HOLD를 유지합니다.",
        },
        "result": result,
    }


def _review_leaf(value: Any, locator: str) -> dict[str, Any]:
    return {
        "value": value,
        "source_locator": locator,
        "source_sha256": source_sha256(value, locator),
    }


def _review_snapshot(side: str) -> dict[str, Any]:
    prefix = f"synthetic://review-impact/{side}"
    identity = _synthetic_identity()
    return {
        "mission_orbit_context": {
            "orbit_regime": _review_leaf("LEO", f"{prefix}#/mission/orbit/regime"),
            "altitude_km": _review_leaf(550.0, f"{prefix}#/mission/orbit/altitude_km"),
            "inclination_deg": _review_leaf(97.6, f"{prefix}#/mission/orbit/inclination_deg"),
        },
        "duration_days": _review_leaf(365.0, f"{prefix}#/mission/duration_days"),
        "shielding_mm_al_equivalent": _review_leaf(2.0, f"{prefix}#/shielding/mm_al_equivalent"),
        "approved_component_identity": {
            field: _review_leaf(value, f"{prefix}#/approved_bom/identity/{field}")
            for field, value in identity.items()
        },
        "event_coverage": {
            event: _review_leaf(True, f"{prefix}#/evidence/event_coverage/{event}")
            for event in MISSION_EVENTS
        },
    }


def build_review_impact_demo_input() -> dict[str, Any]:
    baseline = _review_snapshot("baseline")
    candidate = _review_snapshot("candidate")
    candidate["duration_days"] = _review_leaf(
        730.0, "synthetic://review-impact/candidate#/mission/duration_days"
    )
    candidate["shielding_mm_al_equivalent"] = _review_leaf(
        3.0, "synthetic://review-impact/candidate#/shielding/mm_al_equivalent"
    )
    candidate["approved_component_identity"]["orderable_part_number"] = _review_leaf(
        "EX-100-B",
        "synthetic://review-impact/candidate#/approved_bom/identity/orderable_part_number",
    )
    return {
        "contract_version": "REVIEW_IMPACT_1.0.0",
        "data_class": "SYNTHETIC",
        "baseline": baseline,
        "candidate": candidate,
        "requested_outcome": {
            "engineering_gate": "NOT_EVALUATED",
            "evaluation_status": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
            "used_for_decision": False,
        },
    }


def load_review_impact_demo() -> dict[str, Any]:
    result = classify_review_impact(build_review_impact_demo_input())
    changes = {item["field_pointer"]: item for item in result["changed_fields"]}
    events = [
        _event(1, "review-impact-demo", "CHANGE INPUT", "change.detected", "VALID", "기준안과 변경안을 출처 hash에 결속해 비교했습니다.", detail="임무 기간 · 차폐 · 주문형 부품번호 3개 변경"),
        _event(2, "review-impact-demo", "DURATION", "duration.impact", "NOT_EVALUATED", "임무 기간 변경이 TID와 SEU 재계산을 요구합니다.", detail=f"{changes['duration_days']['baseline']['value']:.0f}일 → {changes['duration_days']['candidate']['value']:.0f}일 · TID + SEU"),
        _event(3, "review-impact-demo", "SHIELDING", "shielding.impact", "NOT_EVALUATED", "차폐 변경은 현재 Core에서 TID 계산만 다시 열어야 합니다.", detail=f"{changes['shielding_mm_al_equivalent']['baseline']['value']:.0f} mm → {changes['shielding_mm_al_equivalent']['candidate']['value']:.0f} mm · TID only"),
        _event(4, "review-impact-demo", "EXACT IDENTITY", "identity.impact", "NOT_EVALUATED", "주문형 부품번호 변경으로 기존 사건별 시험 근거 결속을 무효화했습니다.", detail=f"{changes['approved_component_identity.orderable_part_number']['baseline']['value']} → {changes['approved_component_identity.orderable_part_number']['candidate']['value']} · TID/SEU/SEL/SEB/SEGR 재검토"),
        _event(5, "review-impact-demo", "NEXT ACTION", "actions.completed", "HOLD", "재계산과 exact-part 근거 재결속을 다음 행동으로 반환했습니다.", blocker_codes=result["blocker_codes"]),
    ]
    return {
        "boundary": {
            "data_class": "SYNTHETIC",
            "physics_recalculated": False,
            "assurance_decision": "HOLD",
            "used_for_decision": False,
        },
        "events": events,
        "summary": {
            "headline": "무엇이 바뀌었고 어디부터 다시 검토할지 확인했습니다",
            "decision": "REVIEW_REQUIRED · NOT_EVALUATED · HOLD",
            "problem_location": "기간 · 차폐 · 정확한 부품 식별",
            "confirmed_facts": [
                "기간 변경은 TID·SEU 재계산 대상으로 분류했습니다.",
                "차폐 변경은 TID만 재계산하며 SEU 영향으로 과장하지 않았습니다.",
                "부품번호 변경은 TID·SEU·SEL·SEB·SEGR 근거를 모두 재검토 대상으로 만들었습니다.",
            ],
            "blocking_reason": "변경된 입력으로 계산을 다시 실행하고 새 exact-part 근거를 결속하기 전에는 기존 판단을 재사용할 수 없습니다.",
            "next_action": "TID·SEU 기존 Core를 다시 실행하고, 변경된 부품번호의 사건별 시험 근거를 다시 연결합니다.",
        },
        "result": result,
    }


def load_gcp_snapshot_logs() -> dict[str, Any]:
    payload = json.loads(GCP_LOG_EVIDENCE.read_text(encoding="utf-8"))
    snapshot = json.loads(GCP_SNAPSHOT.read_text(encoding="utf-8"))
    logs = payload.get("cloud_run_structured_logs")
    executions = snapshot.get("executions")
    logging = snapshot.get("logging")
    if (
        payload.get("schema_version") != "1.0.0"
        or payload.get("project_id") != "iceu-686"
        or payload.get("region") != "asia-northeast3"
        or snapshot.get("schema_version") != "1.0.0"
        or snapshot.get("project_id") != payload.get("project_id")
        or snapshot.get("region") != payload.get("region")
        or not isinstance(executions, dict)
        or not isinstance(logging, dict)
        or not isinstance(logs, list)
        or not logs
        or any(not isinstance(item, dict) for item in logs)
    ):
        raise ValueError("GCP_SNAPSHOT_LOG_EVIDENCE_INVALID")
    return {
        "boundary": {
            "source_classification": "CONTROL_TOWER_VERIFIED_H05_SNAPSHOT",
            "live": False,
            "project_id": payload["project_id"],
            "region": payload["region"],
            "log_count": len(logs),
            "assurance_decision": "HOLD",
        },
        "scenarios": {
            "normal": {
                **executions["normal"],
                "correlation_id": logging.get("normal_correlation_id"),
            },
            "body_hash_forgery": executions["body_hash_forgery"],
            "endpoint_override": executions["endpoint_override"],
        },
        "logs": logs,
    }


class EvidenceConsoleHandler(SimpleHTTPRequestHandler):
    server_version = "SPECTRAEvidenceConsole/1.0"

    def end_headers(self) -> None:
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def _send_json(self, status: int, value: Any) -> None:
        body = _json(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/api/health":
            self._send_json(
                200,
                {
                    "status": "READY",
                    "deployment_mode": os.environ.get("SPECTRA_DEPLOYMENT_MODE", "LOCAL"),
                    "gcp_agent_live": False,
                },
            )
            return
        if parsed.path == "/api/gcp-snapshot-logs":
            try:
                self._send_json(200, load_gcp_snapshot_logs())
            except (OSError, ValueError, json.JSONDecodeError):
                self._send_json(
                    500,
                    {
                        "status": "DATA_UNAVAILABLE",
                        "stable_code": "GCP_SNAPSHOT_LOG_EVIDENCE_INVALID",
                        "assurance_decision": "HOLD",
                    },
                )
            return
        if parsed.path == "/api/mission-case-demo":
            try:
                self._send_json(200, load_mission_case_demo())
            except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
                self._send_json(
                    500,
                    {
                        "status": "DATA_UNAVAILABLE",
                        "stable_code": "MISSION_CASE_DEMO_UNAVAILABLE",
                        "assurance_decision": "HOLD",
                    },
                )
            return
        if parsed.path == "/api/review-impact-demo":
            try:
                self._send_json(200, load_review_impact_demo())
            except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
                self._send_json(
                    500,
                    {
                        "status": "DATA_UNAVAILABLE",
                        "stable_code": "REVIEW_IMPACT_DEMO_UNAVAILABLE",
                        "assurance_decision": "HOLD",
                    },
                )
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/intake":
            self._send_json(404, {"status": "NOT_FOUND"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BYTES:
            self._send_json(
                413,
                {
                    "status": "DATA_UNAVAILABLE",
                    "stable_code": "DOCUMENT_SIZE_OUT_OF_RANGE",
                    "assurance_decision": "HOLD",
                },
            )
            return
        params = urllib.parse.parse_qs(parsed.query)
        expected_part = params.get("expected_part", [""])[0].strip()
        manufacturer = params.get("manufacturer", [""])[0].strip() or None
        rights = params.get("confirm_local_review_rights", ["false"])[0] == "true"
        encoded_filename = self.headers.get("X-Spectra-Filename", "document.bin")
        filename = Path(urllib.parse.unquote(encoded_filename)).name
        if len(expected_part) > 120 or len(filename) > 180:
            self._send_json(
                400,
                {
                    "status": "INVALID_INPUT",
                    "stable_code": "CONSOLE_INPUT_INVALID",
                    "assurance_decision": "HOLD",
                },
            )
            return
        content = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        for event in local_intake_events(
            filename,
            content,
            expected_part=expected_part,
            manufacturer=manufacturer,
            local_review_rights_confirmed=rights,
        ):
            self.wfile.write(_json(event) + b"\n")
            self.wfile.flush()

    def log_message(self, format: str, *args: Any) -> None:
        print("[evidence-console] " + (format % args))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    args = parser.parse_args()
    handler = partial(EvidenceConsoleHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"SPECTRA Evidence Console: http://{args.host}:{args.port}/demo/evidence-console.html")
    print("Document parser enabled · GCP agent logs are stored H05 snapshot only · no GCP mutation")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
