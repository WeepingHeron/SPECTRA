# 70 Platform & GCP — Brief

## 책임

Workstream 70은 SPECTRA의 Multi-Agent 실행, GCP 저장·처리 경계, IAM, 감사와 배포 증거를 소유한다. H01~H03의 로컬 권리·raw-manifest preflight 기준선을 보존하고, 현재 활성 패키지에서는 Core Evidence-to-Decision 경로를 교육용 GCP에 최소 E2E로 연결한다.

## 과거 패키지 H01~H03

- 세션: `70-platform-gcp`
- 패키지: `70-gcp-evidence-storage-rights-gate-v1`
- 소유 파일: `BRIEF.md`, `RESEARCH.md`, `CURRENT.md`
- 당시 실제 GCP 프로젝트·bucket·service account·KMS key·billing resource 생성: 금지
- 실제 PDF·BOM·시험자료 다운로드 또는 Document AI·Vertex AI 전송: 계속 금지
- 공통 schema, 루트 문서, 다른 Workstream, checklist, Git commit/push: 읽기 전용

## 작업 패키지 2 — Rights/Raw Manifest Preflight

- 패키지: `70-rights-raw-manifest-preflight-v1`
- 입력 계약: `schemas/raw-artifact-manifest-v2.schema.json` 읽기 전용
- 구현: `preflight/raw_manifest_preflight.py`, 합성 fixture와 unittest
- 권리 조치: `SPENVIS_RIGHTS_INQUIRY_DRAFT.md` 작성만 수행; 발송하지 않음
- 실제 SPENVIS bundle과 TI locator: reference-only 입력이며 `HOLD_NOT_ISSUED`
- 실제 GCP resource, object generation, scan/review 증거: 생성하지 않음
- 소유 범위: `docs/workstreams/70-platform-gcp/` 아래 파일만 수정

## 현재 활성 패키지 H04 — Competition Multi-Agent GCP Minimum E2E

- 대상 project: `iceu-686`
- 기본 region: `asia-northeast3`
- 데이터: 저장소의 `SYNTHETIC` fixture만 사용하며 실제 SPENVIS·BOM·시험 PDF는 업로드하지 않는다.
- 필수 서비스: Cloud Run, Cloud Storage, Workflows 또는 Pub/Sub, Cloud Logging, Agent별 service account/IAM
- 필수 역할: Orchestrator, Mission Environment Agent, Parts Evidence Agent, Independent Assurance Agent
- 필수 결과: 정상 합성 1건과 Agent 실패·오염 입력의 fail-closed 실행, correlation ID, resource 목록, 요청·응답, 로그와 재현 명령
- 비용은 사용자 승인으로 차단 조건이 아니다. 실제 resource 생성·IAM 변경·API enablement는 project와 active account 확인 뒤 수행한다.
- Document AI·Vertex AI·Cloud SQL·BigQuery·KMS는 최소 E2E가 통과한 뒤에만 추가한다.

## 목표

1. 공개, 재배포·처리 제한, 고객 비공개 원문을 같은 접근 경계에 섞지 않는다.
2. 저장·처리·내부 표시·외부 표시·재배포 권리를 별도 동작으로 판정한다.
3. 권리 미확인·충돌·만료·철회 상태는 항상 `HOLD`로 닫는다.
4. raw object의 generation·SHA-256과 `RAW_ARTIFACT_MANIFEST`, 파생 사실, `EvidencePacket`의 lineage를 고정한다.
5. overwrite, hash mismatch, cross-tenant access, 과도한 signed URL, 무제한 보존과 불완전 삭제를 공격 계약으로 정의한다.

## 비목표

- 실제 방사선 assurance 또는 실제 고객 데이터 운영 완료 주장
- 모든 후보 GCP 서비스를 한 번에 배치하는 과도한 인프라
- 법률 자문 또는 개별 문서 이용권한 승인
- 실제 비용 견적 확정
- 권리 미확인 공개 URL의 다운로드

## Exit Gate

- 데이터 구역, IAM/tenant 경계와 권리 동작 행렬이 정의돼 있다.
- raw object는 create-only generation과 SHA-256으로 manifest에 연결된다.
- 권리 gate 전 AI 처리와 표시가 차단된다.
- 보존·복구·삭제·암호화 선택의 비용과 책임이 드러난다.
- 필수 공격 8건이 오류 코드, 차단 단계와 `HOLD`로 종료된다.
- 실제 원문 0건을 유지하고 합성 데이터가 실제 evidence로 승격되지 않게 한다.
- preflight 실패는 stable code와 `manifest: null`을 반환하고 실제 후보를 발행하지 않는다.
- 실제 GCP E2E에서 Agent 실패가 낙관 판정으로 전파되지 않고 로그·응답에 `HOLD/NOT_EVALUATED`로 남는다.
