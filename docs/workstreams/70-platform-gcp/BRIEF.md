# 70 Platform & GCP — Brief

## 책임

Workstream 70은 SPECTRA의 저장, 처리 경계, IAM, 암호화, 감사와 비용 상한 계약을 소유한다. 이번 패키지는 실제 GCP 리소스를 만드는 작업이 아니라, Workstream 30의 환경 모델 출력, Workstream 40의 부품 시험 원문, 고객 BOM을 권리와 tenant 경계 안에서 다루기 위한 최소 Cloud Storage 설계다.

## 이번 작업 패키지

- 세션: `70-platform-gcp`
- 패키지: `70-gcp-evidence-storage-rights-gate-v1`
- 소유 파일: `BRIEF.md`, `RESEARCH.md`, `CURRENT.md`
- 실제 GCP 프로젝트·bucket·service account·KMS key·billing resource 생성: 금지
- 실제 PDF·BOM·시험자료 다운로드 또는 Document AI·Vertex AI 전송: 금지
- 공통 schema, 루트 문서, 다른 Workstream, checklist, Git commit/push: 읽기 전용

## 작업 패키지 2 — Rights/Raw Manifest Preflight

- 패키지: `70-rights-raw-manifest-preflight-v1`
- 입력 계약: `schemas/raw-artifact-manifest-v2.schema.json` 읽기 전용
- 구현: `preflight/raw_manifest_preflight.py`, 합성 fixture와 unittest
- 권리 조치: `SPENVIS_RIGHTS_INQUIRY_DRAFT.md` 작성만 수행; 발송하지 않음
- 실제 SPENVIS bundle과 TI locator: reference-only 입력이며 `HOLD_NOT_ISSUED`
- 실제 GCP resource, object generation, scan/review 증거: 생성하지 않음
- 소유 범위: `docs/workstreams/70-platform-gcp/` 아래 파일만 수정

## 목표

1. 공개, 재배포·처리 제한, 고객 비공개 원문을 같은 접근 경계에 섞지 않는다.
2. 저장·처리·내부 표시·외부 표시·재배포 권리를 별도 동작으로 판정한다.
3. 권리 미확인·충돌·만료·철회 상태는 항상 `HOLD`로 닫는다.
4. raw object의 generation·SHA-256과 `RAW_ARTIFACT_MANIFEST`, 파생 사실, `EvidencePacket`의 lineage를 고정한다.
5. overwrite, hash mismatch, cross-tenant access, 과도한 signed URL, 무제한 보존과 불완전 삭제를 공격 계약으로 정의한다.

## 비목표

- Stage 7 완료 또는 End-to-End GCP 실행 증명
- Terraform, Cloud Run, Cloud SQL, Workflows/Pub/Sub 구현
- 법률 자문 또는 개별 문서 이용권한 승인
- 실제 비용 견적 확정
- 권리 미확인 공개 URL의 다운로드

## Exit Gate

- 데이터 구역, IAM/tenant 경계와 권리 동작 행렬이 정의돼 있다.
- raw object는 create-only generation과 SHA-256으로 manifest에 연결된다.
- 권리 gate 전 AI 처리와 표시가 차단된다.
- 보존·복구·삭제·암호화 선택의 비용과 책임이 드러난다.
- 필수 공격 8건이 오류 코드, 차단 단계와 `HOLD`로 종료된다.
- 실제 리소스 0개, 실제 원문 0건, 비용 발생 0원이라는 현재 진실을 유지한다.
- preflight 실패는 stable code와 `manifest: null`을 반환하고 실제 후보를 발행하지 않는다.
