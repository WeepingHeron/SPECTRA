# 70 Platform & GCP — Current

## 상태

`VERIFIED — H03 local raw manifest preflight`

이 상태는 `70-rights-raw-manifest-preflight-v1` H03의 로컬 fail-closed 구현이 Control Tower 독립 재검증을 통과했다는 뜻이다. 이전 `70-gcp-evidence-storage-rights-gate-v1` H01 문서 설계의 `VERIFIED` 판정도 유지한다. 실제 GCP 구현, 실제 권리 승인, raw manifest 발행, 비용 기준선 또는 Stage 7 완료를 뜻하지 않는다.

## 이번 패키지

- 세션: `70-platform-gcp`
- H01 소유 파일: `docs/workstreams/70-platform-gcp/BRIEF.md`, `RESEARCH.md`, `CURRENT.md`
- 기준선: 마지막 통합된 Workstream 30·40 조사와 현재 Workstream 50 계약 상태
- 루트 문서, 공통 schema, 다른 Workstream, checklist: 수정하지 않음
- commit/push: 수행하지 않음

### 새 패키지 H02

- 입력: Workstream 30 실제 SPENVIS bundle의 현재 gap, Workstream 40 TI locator의 현재 gap, raw manifest v2 schema
- 구현: read-only manifest issuance preflight, 합성 정상/공격 fixture, unittest
- 권리 문서: SPENVIS action별 권리와 provider run reference 문의 초안 (`DRAFT_NOT_SENT`)
- 실제 후보: SPENVIS/TI 모두 `HOLD_NOT_ISSUED`, manifest `null`
- 수정 범위: `docs/workstreams/70-platform-gcp/`만

### H03 변경 요청 반영

- candidate manifest schema-invalid 시 semantic traversal 전에 즉시 `RAW_MANIFEST_SCHEMA_INVALID`로 반환한다.
- request/context/receipt는 Workstream-local JSON Schema로 먼저 자료형을 검사한다.
- list action/artifact ID/receipt ID와 string malware scan의 예외 재현 입력을 모두 구조화된 HOLD로 전환했다.
- receipt에 `project_id`, `bucket_id`, `object_name`을 추가하고 generation과 함께 exact `storage_ref`에 결합했다.
- storage tuple mismatch는 `RAW_STORAGE_REF_MISMATCH`, generation mismatch는 `RAW_GENERATION_MISMATCH`도 함께 반환한다.
- missing, duplicate-key, manifest에 없는 extra receipt를 각각 별도 stable code로 차단한다.
- synthetic receipt는 실제 GCP 관찰 증거가 아니며 H03은 local contract verification에 한정한다.
- reference fixture의 declared gap은 외부 검증 결과가 아니라 Workstream 30/40에서 입력으로 전달된 gap임을 이름·문서·테스트에 고정했다.

## 설계한 계약

- 공개 raw, 제한 raw, 고객 raw, 파생값/manifest, synthetic, audit control의 구역을 분리했다.
- 고객 raw/derived는 tenant별 project를 기본안으로, tenant별 bucket을 조건부 pilot 대안으로 뒀다.
- 공개와 제한 원문은 별도 bucket·service account를 사용하며 prefix를 보안 경계로 인정하지 않는다.
- `RIGHTS_UNCONFIRMED`부터 `FORBIDDEN`까지 상태와 locator/download/store/Document AI/Vertex AI/internal/external display/redistribution 동작 행렬을 정의했다.
- 공개 URL만으로 다운로드하지 않고, 권리 미확인·충돌·만료·철회는 `HOLD`로 닫는다.
- 모든 raw bucket에 Public Access Prevention, uniform bucket-level access, 최소권한 IAM과 사람/서비스 역할 분리를 요구했다.
- Google 기본 암호화와 CMEK의 control, 비용, key lifecycle·가용성 trade-off를 분리했다.
- raw upload를 `ifGenerationMatch=0` create-only로 고정하고 exact generation + SHA-256을 manifest/EvidencePacket 연결 키로 정의했다.
- soft delete 7일 후보, Object Versioning 기본 off, retention/Bucket Lock 미사용 기본안을 제시하고 삭제 요구 충돌을 ingest 전 차단했다.
- 권리 판정 전 AI 처리 금지, MIME/malware/hash/tenant/duplicate/lineage와 deletion propagation의 fail-closed gate를 정의했다.
- Cloud Audit Logs Data Access 범위와 application-level rights/upload/process/display/delete audit를 분리했다.
- 필수 공격 8건에 탐지 조건, 오류 코드 후보, 차단 단계와 `HOLD` 결과를 명시했다.
- Workstream 10·30·40·50·60 전달 요구사항을 분리했다.

## H02 구현 결과

- `RAW_MANIFEST_ISSUABLE / ISSUE_ALLOWED`와 `RAW_MANIFEST_HOLD_NOT_ISSUED / HOLD_NOT_ISSUED`를 machine-readable result로 고정했다.
- 실패 시 processing status, 정렬된 stable error code와 `manifest: null`을 반환한다.
- provider job reference, action별 rights, approval/history, tenant/zone, create-only receipt, generation, SHA-256, byte size, MIME, malware scan, validation/review와 bundle hash를 검사한다.
- 합성 정상 fixture만 발행 가능 후보이며 `data_class=SYNTHETIC`, assurance `HOLD`를 유지한다.
- overwrite, generation mismatch, rights missing/stale/action missing, cross-tenant, hash/MIME mismatch, scan/review 누락 공격은 모두 manifest 발행을 차단한다.
- SPENVIS/TI reference-only fixture는 실제 원문이나 수치를 포함하지 않으며 `HOLD_NOT_ISSUED`다.
- SPENVIS 문의 초안은 commercial, automation, private/cloud storage, Document AI/Vertex AI, internal/external display, raw/derived redistribution과 provider run reference를 한 번에 묻도록 작성했다. 발송하지 않았다.

## 현재 HOLD

| Gap | 현재 상태 | 재개 조건 |
|---|---|---|
| `GCP_RESOURCE_APPROVAL_MISSING` | project/bucket/SA/KMS/billing 0 | 사용자·Control Tower의 구조·비용·명령 승인 |
| `RIGHTS_APPROVAL_MISSING` | 실제 문서 action grant 0 | 문서별 저장·처리·표시·재배포 승인 |
| `TENANT_CONTRACT_MISSING` | 승인 BOM/고객 문서/tenant 0 | 고객 계약, region, retention, processor, deletion 승인 |
| `SCHEMA_VERIFIED_RUNTIME_PENDING` | Workstream 10 H05의 manifest generation/tenant/rights/lineage schema·validator 검증 완료; 실제 cloud 검증 없음 | 실제 GCP object/IAM·scanner·rights 상태 검증 |
| `MALWARE_GATE_UNSELECTED` | scan engine/policy 0 | 도구·signature·sandbox·오류 정책 승인 |
| `AUDIT_COST_UNAPPROVED` | Data Access log 범위/보존/비용 미정 | 예상량과 log sink/retention 승인 |
| `BUDGET_AND_QUOTA_UNSET` | region·quota·budget alert 미정 | 비용 모델과 hard ingest limits 승인 |
| `ASSURANCE_FIXTURES_PENDING` | H02 Workstream-local 합성 preflight fixture는 구현; 실제 IAM/GCP 공격은 없음 | Workstream 60 독립 구현·False PASS 검증 |
| `PROVIDER_JOB_REFERENCE_MISSING` | SPENVIS download에서 고유 provider job reference 미확인 | SPENVIS 회신 또는 provider-issued stable reference |
| `REAL_MANIFEST_HOLD_NOT_ISSUED` | SPENVIS/TI 실제 승인 manifest 0건 | active rights, tenant/zone, create-only generation, scan/review 전체 통과 |
| `LIVE_GCP_RECEIPT_NOT_OBSERVED` | H03 receipt는 synthetic fixture뿐 | 실제 승인 project에서 object identity/generation/audit를 독립 관찰 |

## H03 검증 결과

- Workstream 70 preflight: unittest 2개 통과
  - synthetic case 26개: 정상 `ISSUE_ALLOWED` 1개, invalid `HOLD_NOT_ISSUED` 25개
  - reference-only declared-gap case 2개: 모두 `RAW_MANIFEST_CANDIDATE_MISSING`, `HOLD_NOT_ISSUED`
- schema: 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- simulation: 31개 통과
- environment: 23개 통과
- assurance: 21 cases, 20 evaluated, attack executions 29, failure 0, False PASS 0, live GCP 공격 1개 `NOT_EVALUATED`
- `git diff --check`: 통과

전체 회귀는 현재 혼합 작업트리 기준이며 다른 Workstream 변경의 승인 근거가 아니다. live GCP 공격 `NOT_EVALUATED`는 H03 synthetic receipt로 닫지 않는다.

### Control Tower H03 독립 재검증 — 2026-08-20

- 판정: `VERIFIED — H03 local raw manifest preflight`; H01 문서 설계의 `VERIFIED`도 유지한다.
- 제출 matrix와 별도 11개 공격에서 malformed action/artifact/malware/receipt 입력은 schema/input error로, project/bucket/object/generation 변조는 `RAW_STORAGE_REF_MISMATCH`로 안정 종료했다.
- receipt 누락·중복·extra는 각각 stable code로 `manifest: null`, assurance `HOLD`를 반환했다. 정상 synthetic candidate 1건만 `ISSUE_ALLOWED`이며 실제 GCP 관찰 증거가 아니다.
- schema 14개·fixture 3/83, simulation 31개, environment 23개, assurance 20 evaluated·1 `NOT_EVALUATED`, 공격 실행 29개, False PASS 0을 재현했다.
- 실제 GCP resource·creation receipt·rights approval·raw manifest·비용은 0이며 `ASR-D02`는 계속 `NOT_EVALUATED`다.

## 실제 상태

- GCP project 생성: 0
- Cloud Storage bucket 생성: 0
- service account/IAM binding 생성: 0
- Cloud KMS key 생성: 0
- Document AI/Vertex AI 호출: 0
- 승인 GCP raw/derived artifact와 raw manifest v2: 0
- Git에 포함한 실제 원문·BOM·시험 PDF·환경 output: 0
- 외부 private SPENVIS candidate bundle: 1세트 존재하나 Workstream 30 기준 `HOLD_NOT_ISSUED`
- TI locator candidate: 1건 존재하나 Workstream 40 기준 `HOLD_NOT_ISSUED`
- 발생 비용: 0원
- `gcloud auth` 또는 credential 조회: 수행하지 않음

## 검증된 계약과 남은 운영 결정

H03의 로컬 fail-closed 항목은 위 Control Tower 재검증을 통과했다. 다음 목록 중 실제 IAM·비용·운영 선택은 live GCP 작업 전에 별도 승인해야 한다.

1. 공개/제한/고객 경계가 실제 IAM과 tenant threat model에 충분한가.
2. 권리 행렬이 storage, processing, internal/external display와 redistribution을 별도 동작으로 차단하는가.
3. exact generation + SHA-256 + rights snapshot + tenant가 raw manifest와 EvidencePacket 연결에 충분한가.
4. soft delete 7일 후보와 versioning off가 삭제 SLA와 복구 목표에 맞는가.
5. 고객 tenant별 project 기본안의 운영비와 tenant별 bucket 대안의 residual risk를 수용할지.
6. CMEK 적용 대상, key owner, region, rotation/destroy와 비용을 누가 승인할지.
7. Data Access logs와 application audit가 signed URL recipient·rights approver·processor·deletion actor를 추적하는가.
8. 8개 필수 공격과 추가 MIME/malware/retention 공격을 Workstream 60 fixture로 넘길 수 있는가.
9. H03 preflight가 schema 오류와 semantic 오류를 안정적으로 구분하고 모든 실패에서 manifest를 `null`로 유지하는가.
10. synthetic creation receipt가 실제 Cloud Storage generation 증거로 오인되지 않도록 결과와 handoff가 경계를 유지하는가.
11. SPENVIS/TI reference-only 입력에 known gap을 적게 기입해도 `RAW_MANIFEST_CANDIDATE_MISSING`이 무조건 발행을 차단하는가.
12. SPENVIS 문의 초안의 action 범위와 provider run reference 질문이 회신 후 rights snapshot을 만들기에 충분한가.

H03 로컬 구현은 `VERIFIED`지만 `INTEGRATED`, Stage 7 완료, checklist 완료 또는 Git 반영은 선언하지 않는다.

## Control Tower H02 독립 재검증 기록 — 2026-08-20

아래 `CHANGES_REQUESTED`와 두 결함은 H02 제출물에 대한 당시 판정 기록이다. H03 수정본에서는 schema-first 중단과 exact storage receipt binding으로 보완했으며, 현재 재제출 상태는 위의 `H03 변경 요청 반영` 및 `H03 검증 결과`를 따른다.

- 판정: `CHANGES_REQUESTED — 70-rights-raw-manifest-preflight-v1`; H01 문서 설계의 `VERIFIED` 판정은 유지한다.
- 제출 회귀: preflight unittest 2개·합성 case 11개·real reference HOLD 2개, schema 14·fixture 3/83, simulation 31, environment 20, assurance 20 evaluated·1 `NOT_EVALUATED`가 통과했다.
- 제출된 정상·공격 fixture에서는 모든 실패가 `manifest: null/HOLD`였고 실제 GCP resource·권리 승인·raw manifest 발행은 0이다.
- H02 당시 오염 입력 결함: schema-invalid `action_grants[].action` list, `artifact_id` list, `malware_scan` string, creation receipt의 list ID가 각각 `TypeError` 또는 `AttributeError`를 발생시켰다. H03에서는 unsafe semantic traversal 전에 구조 검증 실패로 종료한다.
- H02 당시 provenance 결함: candidate manifest의 `storage_ref.project_id`, `bucket_id` 또는 `object_name`만 다른 값으로 바꿔도 기존 creation receipt가 그 object identity를 담지 않아 `ISSUE_ALLOWED`가 반환됐다. H03에서는 receipt를 exact project/bucket/object/generation에 결합한다.
- 실제 후보 fixture의 선언 gap은 입력에서 복사된 주장일 뿐 외부 권리·provider 상태의 독립 검증이 아니다. `RAW_MANIFEST_CANDIDATE_MISSING`에 의한 HOLD 증거로만 해석한다.
- 후속 제출: `/Users/taehoon/Downloads/SPECTRA_70_RIGHTS_RAW_MANIFEST_PREFLIGHT_HANDOFF_H03.md`; malformed-input safe failure와 exact storage receipt binding을 반영해 재검토를 요청한다.

## Control Tower H01 독립 검증 — 2026-08-20

- 판정: `VERIFIED` — GCP Evidence Storage & Rights Gate 문서 설계 패키지에 한정한다. 실제 GCP resource, IAM, 권리 승인, 비용 또는 배포 검증을 뜻하지 않는다.
- 공식 문서 대조: Public Access Prevention, uniform bucket-level access, generation precondition, soft delete, Object Versioning, Bucket Lock, CMEK, signed URL과 Data Access audit log의 동작·한계를 Google Cloud 공식 문서와 재확인했다.
- 권리 계약: 8개 상태와 독립 action grant가 함께 필요하며 공개 URL, 넓은 상태 문자열 또는 processor 하나의 허가가 다른 동작을 자동 허용하지 않는다.
- 무결성 계약: `ifGenerationMatch=0`, exact generation, SHA-256, rights snapshot과 tenant 연결이 overwrite·provenance laundering을 fail-closed로 막는다.
- 위협 구조: 필수 공격 8개와 오류 코드가 모두 존재하고 MIME/malware/duplicate/retention conflict도 `HOLD`로 종료한다.
- 회귀 재실행: schema 11개, 정상 fixture 2개, 실패 fixture 71개와 simulation test 19개가 통과했다. 이는 기존 계약 회귀이며 GCP 실행 증거가 아니다.
- 실제 상태: project, bucket, service account/IAM binding, KMS key, AI 호출, raw artifact와 비용은 모두 0이다.
- 남은 결정: project/region/billing owner, tenant 격리 수준, retention/deletion SLA, CMEK, malware gate, audit 범위·비용과 quota는 실제 생성 전에 사용자·Control Tower 승인이 필요하다.
- Git: 이번 검증에서 commit·push하지 않았다.
