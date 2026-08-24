# 70 Platform & GCP — Current

## 상태

`VERIFIED — H05 Core Binding & Input Integrity Remediation`

이 상태는 H04에서 발견된 production Core 미결합, body-hash 결합 우회, runtime endpoint 교체 가능성과 production test control을 H05가 보완했고 Control Tower가 로컬 테스, 실제 revision·Workflow, 정상·공격 execution과 저장 result를 독립 재검증해 H05 패키지를 `VERIFIED`로 판정했다는 뜻이다. 실제 environment·BOM·시험 evidence와 Workstream 60 `ASR-D02`는 아직 완료되지 않았으므로 Stage 7은 `IN_PROGRESS`다.

## 2026-08-22 추가 body-hash 공격 execution 독립 확인

- execution `ad392071-1554-43e8-9447-5b92d4790a48`, Workflow `spectra-h04-e2e` revision `000005-32c`, state `SUCCEEDED`, duration `1.688795413s`를 gcloud API로 직접 확인했다.
- input object `inputs/20260821T054210Z-3b5b366e-assurance_fail.json`, generation `1787290933859867`은 expected·metadata SHA-256이 모두 all-zero인 합성 공격 입력이다.
- Mission revision `spectra-h04-mission-00006-4f5`가 실제 body SHA-256 `ec1f...b3b`와 불일치를 확인해 `INPUT_BODY_SHA256_MISMATCH`, `INVALID_INPUT / NOT_EVALUATED / HOLD`로 차단했다. Parts·Assurance는 호출되지 않았다.
- Storage result `results/ad392071-1554-43e8-9447-5b92d4790a48.json` generation `1787290937657357`의 본문이 Workflow result와 일치했다.
- 2026-08-21T05:42:16~17Z Cloud Logging에서 Workflows 시작·종료, Mission POST 200과 structured `spectra_h05_agent_result / INPUT_BODY_SHA256_MISMATCH`를 재확인했다.
- 판정: 추가 body-hash 공격 차단 실행 `VERIFIED`. 이는 오케스트레이션과 fail-closed 성공이며 세 Agent 정상 실행, 실제 environment·부품 evidence 또는 방사선 assurance 성공이 아니다.

## H04 Control Tower 독립 검토 — 2026-08-21

- 판정: `CHANGES_REQUESTED`
- H04 Agent contract unittest 7개, Cloud Run service·revision·IAM, Workflow revision과 제출된 3개 execution의 `SUCCEEDED`, Storage bucket·generation, structured log를 독립 재확인했다.
- Mission Agent가 `src/spectra_sim` production Decision Engine을 호출하지 않고 TID·SEU·ECC 계산을 서비스 내부에 다시 구현했다. Agent가 숫자를 만들지 않는다는 공식 계약과 다르고 production Product 값과 drift할 수 있다.
- Workflow는 GCS custom metadata의 SHA와 runtime argument SHA만 비교하고 다운로드한 JSON body의 SHA를 재계산하지 않았다. Control Tower가 변조 body와 all-zero metadata/argument SHA를 같이 제출한 execution `fc867d19-4a4a-4208-8733-3558f1428503`은 Workflow `SUCCEEDED`, Agent 3개 `VALID`로 수용됐다. 최종 판정은 `HOLD`였지만 provenance 검사는 False Accept다.
- Workflow 실행 인자의 `mission_url`, `parts_url`, `assurance_url`로 OIDC 호출 대상을 바꿀 수 있다. 배포 시 고정된 endpoint로 제한해야 한다.
- production Workflow의 `test_mode/failure_role`은 주 실행 경로에서 제거하고 malformed fixture 또는 테스트 전용 경로로 분리한다.
- 보완 지침: `instructions/SPECTRA_70_CORE_BINDING_INPUT_INTEGRITY_REMEDIATION_H05.md`
- 실제 GCP resource는 계속 배포 중이며 삭제하지 않았다. 합성 object에는 30일 lifecycle가 적용된다.

## 2026-08-21 활성 H04 결정

- Competition Demo Release에서 Multi-Agent·GCP는 필수다.
- 교육용 project `iceu-686`, 기본 region `asia-northeast3`, active account `edu_686@iceu.kr`, project lifecycle `ACTIVE`와 billing enabled를 확인했다. credential/token 원문은 출력하거나 문서화하지 않았다.
- H04는 합성 fixture만 사용해 Orchestrator와 세 Agent, Cloud Run·Cloud Storage·Workflows 또는 Pub/Sub·Cloud Logging·IAM의 최소 E2E를 구현한다.
- 실제 environment·BOM·시험 PDF는 업로드하지 않으며, 합성 실행도 실제 방사선 보증으로 승격하지 않는다.
- 사용자가 비용 제한을 두지 않았으므로 비용 상한은 blocker가 아니다. 실제 resource·호출·로그·IAM은 H04에서 관측했지만 독립 공격 검증과 Control Tower 통합 전 Stage 7은 계속 `IN_PROGRESS`다.

## H04 실제 구현·배포 결과 — 2026-08-21

### 배포 아키텍처

- private Cloud Storage `spectra-h04-iceu-686`의 합성 input을 Workflows `spectra-h04-e2e`가 exact generation과 SHA-256 metadata로 확인한다.
- Workflows revision `000003-f39`가 Mission → Parts → Assurance 순서로 인증된 Cloud Run을 호출하고 결과를 `ifGenerationMatch=0`으로 create-only 저장한다.
- Cloud Run revision은 Mission `00004-dzn`, Parts `00004-qv5`, Assurance `00004-vq9`이며 모두 `asia-northeast3`, min instance 0, max instance 1이다.
- 세 Agent service account에는 project role을 부여하지 않았다. Workflow service account만 각 service의 `roles/run.invoker`, bucket의 `roles/storage.objectViewer/objectCreator`, project의 `roles/logging.logWriter`를 가진다.
- Cloud Run IAM에 `allUsers`/`allAuthenticatedUsers`는 없고 비인증 `/healthz`는 세 서비스 모두 HTTP 404로 응답해 application handler에 도달하지 않았다.
- bucket은 Public Access Prevention `enforced`, uniform bucket-level access `true`, versioning off, soft delete 7일, 합성 object 30일 Delete lifecycle이다.
- image digest는 `sha256:926ecc64ca419753a302a82e1a4ec0cf2a79a4b98aeac8bda19394a1f79ed1da`다.

### 최종 실제 Workflow 세 실행

| 사례 | execution ID | Agent 상태 | 최종 결과 | 차단 code |
|---|---|---|---|---|
| 정상 합성 | `1a513bb1-2780-4a7f-a907-a5aa59a8cbc1` | Mission/Parts/Assurance 모두 `VALID` | `NOT_EVALUATED/HOLD` | `SYNTHETIC_ONLY` |
| evidence hash 오염 | `8b9215e5-65d8-42d2-abb6-7ce41ef46749` | Parts/Assurance `INVALID_INPUT` | `NOT_EVALUATED/HOLD` | `PART_EVIDENCE_HASH_MISMATCH`, `PARTS_AGENT_NOT_VALID` |
| Parts Agent 구조화 실패 | `8677c107-84c7-4f09-9f94-2ac061db798f` | Parts/Assurance `INVALID_INPUT` | `NOT_EVALUATED/HOLD` | `AGENT_TEST_FAILURE`, `PARTS_AGENT_NOT_VALID` |

세 execution은 모두 Workflow 상태 `SUCCEEDED`이며, 이는 orchestration과 안전한 결과 저장이 성공했다는 뜻이다. 오염·Agent failure를 분석 성공이나 방사선 PASS로 해석하지 않는다. 각 실행에서 세 Agent의 structured Cloud Run log 9건을 correlation ID로 확인했다.

### 실제 Storage 관찰

- 최종 정상 input: generation `1787241287203919`, SHA-256 `a7359dcaadec22c56f70e2937333a22bfdf95138742f706d30cf70e3a22a060a`
- 최종 정상 result: generation `1787241292513530`, SHA-256 `376f06e48cdd5c00470c51c434d48a37ae656d895ea84776bf6e6b0d3f4d7bcd`
- 최종 오염 result: generation `1787241303412096`, SHA-256 `19b1d35cd40c7211acbe9d25f773729f33bc960312f25e97e8b4959cbb6cc849`
- 최종 Agent failure result: generation `1787241313811707`, SHA-256 `244a10130ef6b76fa2f48d60d941dbd21532b4a23a931db3f5aacd8a2dc6bc1c`
- 개발·진단 실행을 포함해 현재 합성 input 16개, result 13개, 총 56,110 bytes다. 실제 원문은 0건이다.
- durable evidence: `evidence/h04-e2e-runs.json`, `evidence/h04-gcp-inventory-and-logs.json`.

### H04 구현 중 관찰한 결함과 보완

- Workflow call logging에 필요한 `roles/logging.logWriter` 누락은 첫 실행에서 IAM fail로 드러나 최소 project binding으로 보완했다.
- Storage connector의 slash 포함 object+generation 조회 404는 encoded Storage JSON API metadata 조회로 교체했다.
- runner가 실패 execution의 `result`를 바로 읽던 `KeyError`를 state/error context가 있는 fail-closed `RuntimeError`로 바꿨다.
- Workflows가 JSON `12.0`을 `12`로 정규화해 response hash가 달라진 오탐은 의미 보존형 numeric canonicalization으로 보완했다.
- 실패 응답에도 input SHA-256을 보존해 어느 input generation에 대한 실패인지 Assurance lineage를 유지했다.

### H04 최종 로컬·전체 회귀

- H04 Agent contract unittest: 7개 통과
- schema: 14개 schema, valid fixture 5개, invalid fixture 116개 통과
- simulation: 55개 통과
- environment: 23개 통과
- assurance: 22 cases, 21 evaluated, attack executions 47, controls 4, failure 0, False PASS 0, live independent GCP attack 1개 `NOT_EVALUATED`
- `git diff --check`: 통과

기존 assurance `ASR-D02`의 `NOT_EVALUATED`는 H04 자체 실행으로 임의 승격하지 않았다. Workstream 60이 deployed identity와 endpoint를 독립 공격한 뒤 별도 판정해야 한다.

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
| `GCP_SYNTHETIC_E2E_REVIEW_PENDING` | H04 최소 resource와 세 실행 존재, 현재 상한 `READY_FOR_REVIEW` | Control Tower와 Workstream 60의 독립 IAM·endpoint·failure 검증 |
| `RIGHTS_APPROVAL_MISSING` | 실제 문서 action grant 0 | 문서별 저장·처리·표시·재배포 승인 |
| `TENANT_CONTRACT_MISSING` | 승인 BOM/고객 문서/tenant 0 | 고객 계약, region, retention, processor, deletion 승인 |
| `SCHEMA_VERIFIED_RUNTIME_PENDING` | Workstream 10 H05의 manifest generation/tenant/rights/lineage schema·validator 검증 완료; 실제 cloud 검증 없음 | 실제 GCP object/IAM·scanner·rights 상태 검증 |
| `MALWARE_GATE_UNSELECTED` | scan engine/policy 0 | 도구·signature·sandbox·오류 정책 승인 |
| `AUDIT_COST_UNAPPROVED` | Data Access log 범위/보존/비용 미정 | 예상량과 log sink/retention 승인 |
| `BUDGET_AND_QUOTA_UNSET` | 사용자는 H04 비용 상한을 두지 않았고 budget alert는 미설정 | 계속 운영할 경우 owner·alert·quota와 cleanup 시점 결정 |
| `ASSURANCE_FIXTURES_PENDING` | H04 정상/오염/Agent failure 실제 실행 완료; 외부 attacker profile 미검증 | Workstream 60 독립 구현·False PASS 검증 |
| `PROVIDER_JOB_REFERENCE_MISSING` | SPENVIS download에서 고유 provider job reference 미확인 | SPENVIS 회신 또는 provider-issued stable reference |
| `REAL_MANIFEST_HOLD_NOT_ISSUED` | SPENVIS/TI 실제 승인 manifest 0건 | active rights, tenant/zone, create-only generation, scan/review 전체 통과 |
| `LIVE_RAW_RECEIPT_NOT_OBSERVED` | H04 합성 object generation/hash는 관찰; 실제 raw evidence receipt는 0 | 승인된 실제 원문과 rights snapshot으로 별도 검증 |

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

## 실제 상태 — H04 이후

- GCP project: 기존 교육용 `iceu-686` 사용; H04가 project를 생성하지 않음
- Cloud Storage bucket 생성: H04 합성 전용 1개
- Cloud Run service 생성: 역할별 3개
- Workflows 생성: 1개
- Artifact Registry repository 생성: 1개, build iteration image version 5개
- service account 생성: 4개; H04 IAM binding은 Run invoker 3개, bucket role 2개, project log writer 1개
- Cloud KMS key 생성: 0
- Document AI/Vertex AI 호출: 0
- 승인 GCP raw/derived artifact와 raw manifest v2: 0
- 실제 environment/BOM/시험 원문 업로드: 0
- 합성 Storage object: input 16개, result 13개, 총 56,110 bytes
- Git에 포함한 실제 원문·BOM·시험 PDF·환경 output: 0
- 외부 private SPENVIS candidate bundle: 1세트 존재하나 Workstream 30 기준 `HOLD_NOT_ISSUED`
- TI locator candidate: 1건 존재하나 Workstream 40 기준 `HOLD_NOT_ISSUED`
- 비용 발생 가능 resource: Cloud Build 5회, Artifact Registry image 5개, Cloud Run/Workflows 호출, Storage 56,110 bytes와 Logging. billing export 또는 실시간 청구액은 아직 관측하지 못해 0원으로 주장하지 않는다.
- `gcloud auth`: active account의 브라우저 callback 재인증 수행; password/token/credential 원문은 출력·보관하지 않음

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

H03 로컬 구현의 현재 기준선은 commit `379f3ad`에 `INTEGRATED`다. 이 이력으로 H04의 `VERIFIED/INTEGRATED`, Stage 7 완료 또는 checklist 완료를 대신 선언하지 않는다.

## H05 현재 상태 — Core binding/input integrity remediation

### Control Tower 독립 판정 — 2026-08-21

- 판정: `VERIFIED — H05 package only`
- H05 unittest 12개를 독립 재실행해 전부 통과했다.
- Cloud Run 최종 revision Mission `00006-4f5`, Parts `00006-p6c`, Assurance `00006-zfx`와 image digest `sha256:27096755b16cf1129e7d48da6b2573e5d86c8a885613e64dc590652527650569`, Workflow `000005-32c`·deployment-bound URL을 실제 GCP에서 재확인했다.
- 제출된 6개 execution이 모두 Workflow `SUCCEEDED`임을 재확인했고, 정상·body 동시 위조·endpoint override result object를 직접 읽어 production Core parity, `INPUT_BODY_SHA256_MISMATCH`, `ENDPOINT_OVERRIDE_FORBIDDEN`, 모든 `HOLD`를 대조했다.
- H05의 `VERIFIED`는 수정 범위의 실행·무결성 계약에 한정한다. GCP 전체 보안, 실제 방사선 근거, Stage 7 `COMPLETE`, Git 통합을 뜻하지 않는다.

상태 상한은 `READY_FOR_REVIEW`다. H04의 실제 리소스를 유지한 채 Cloud Run 세 서비스와 Workflow만 새 revision으로 갱신했다.

- Mission `spectra-h04-mission-00006-4f5`, Parts `spectra-h04-parts-00006-p6c`, Assurance `spectra-h04-assurance-00006-zfx`
- Workflow `spectra-h04-e2e` revision `000005-32c`
- final image `agents@sha256:27096755b16cf1129e7d48da6b2573e5d86c8a885613e64dc590652527650569`
- 새 project/bucket/repository/service account/KMS key: 0
- 실제 SPENVIS/TI/BOM/시험 원문, rights approval, raw manifest v2: 0
- Document AI/Vertex AI 호출: 0

Mission의 H04 중복 TID·SEU 계산은 제거했다. 제한된 image build context에 production `src/spectra_sim`, 필요한 schema, 고정 `mvp-ecc-policy-v2.json`과 합성 model/base fixture만 포함하고 `run_mvp_decision(case, model)` 결과를 그대로 반환한다. 저장된 정상 result generation을 재다운로드해 로컬 Core와 비교한 결과 전체 semantic object, 지정 payload, canonical SHA-256이 모두 일치했다. 양쪽 hash는 `sha256:a7e7de0d71e9ec5f94574ae5bd2244a94ef70169304b190c2126b1698d701a27`이다.

uploader와 Agent는 `shared/integrity.py`의 하나의 canonical JSON byte 계약을 사용한다. Mission은 body를 다시 해시해 object metadata SHA와 expected SHA에 모두 결합한다. body mismatch는 `INPUT_BODY_SHA256_MISMATCH`로 Core 및 downstream 호출 전에 종료한다. Workflow Agent URL은 deployment `userEnvVars`에 고정하고 execution arg의 URL은 `ENDPOINT_OVERRIDE_FORBIDDEN`으로 Agent 호출 전에 차단한다. production `test_mode/failure_role` 실행 경로는 Agent와 Workflow에서 제거했다.

최종 실제 실행:

| case | execution | 결과 | stable code/경계 |
|---|---|---|---|
| production Core 정상 | `ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34` | `VALID / NOT_EVALUATED / HOLD` | `PRODUCTION_CORE_BOUND`, 최종 `SYNTHETIC_ONLY` |
| body+metadata+expected SHA 동시 위조 | `3f5d9221-7b7a-4023-be3c-f933fdbaf070` | `INVALID_INPUT / NOT_EVALUATED / HOLD` | `INPUT_BODY_SHA256_MISMATCH`; Mission만 호출, Core/Parts/Assurance 미호출 |
| parts evidence hash 오염 | `bbf7d6c7-bcfb-4dd7-87a5-38303e861738` | `INVALID_INPUT / NOT_EVALUATED / HOLD` | `PART_EVIDENCE_HASH_MISMATCH` |
| malformed part input | `270332c4-232c-4dda-84d5-12ef92e36efa` | `INVALID_INPUT / NOT_EVALUATED / HOLD` | `EXACT_PART_IDENTITY_INVALID` |
| endpoint override | `df49b5c1-3883-468e-bf1e-67e87ee0b6a7` | `INVALID_INPUT / NOT_EVALUATED / HOLD` | `ENDPOINT_OVERRIDE_FORBIDDEN`; Agent 호출 0 |
| legacy test-control key 제출 | `e51de87e-3b84-4c57-8eb1-89f0ce755782` | `VALID / NOT_EVALUATED / HOLD` | key가 실행 경로에 없고 `AGENT_TEST_FAILURE` 미발생 |

모든 execution은 안전한 result object까지 기록돼 Workflow state가 `SUCCEEDED`지만, 이는 과학·assurance PASS가 아니다. 정상 포함 모든 fixture는 `SYNTHETIC`, assurance `HOLD`다. PAP enforced, uniform access, soft delete 7일, versioning off, age 30 delete lifecycle, create-only result와 기존 최소권한 IAM을 유지했다. H05는 기존 비용 발생 리소스를 보존했고 Cloud Build 2회, image version 2개, Workflow/Run/Storage/Logging 사용량을 추가했으므로 비용 0원을 주장하지 않는다. cleanup은 수행하지 않았다.

## Control Tower H02 독립 재검증 기록 — 2026-08-20

아래 `CHANGES_REQUESTED`와 두 결함은 H02 제출물에 대한 당시 판정 기록이다. H03 수정본에서는 schema-first 중단과 exact storage receipt binding으로 보완했으며, 현재 재제출 상태는 위의 `H03 변경 요청 반영` 및 `H03 검증 결과`를 따른다.

- 판정: `CHANGES_REQUESTED — 70-rights-raw-manifest-preflight-v1`; H01 문서 설계의 `VERIFIED` 판정은 유지한다.
- 제출 회귀: preflight unittest 2개·합성 case 11개·real reference HOLD 2개, schema 14·fixture 3/83, simulation 31, environment 20, assurance 20 evaluated·1 `NOT_EVALUATED`가 통과했다.
- 제출된 정상·공격 fixture에서는 모든 실패가 `manifest: null/HOLD`였고 실제 GCP resource·권리 승인·raw manifest 발행은 0이다.
- H02 당시 오염 입력 결함: schema-invalid `action_grants[].action` list, `artifact_id` list, `malware_scan` string, creation receipt의 list ID가 각각 `TypeError` 또는 `AttributeError`를 발생시켰다. H03에서는 unsafe semantic traversal 전에 구조 검증 실패로 종료한다.
- H02 당시 provenance 결함: candidate manifest의 `storage_ref.project_id`, `bucket_id` 또는 `object_name`만 다른 값으로 바꿔도 기존 creation receipt가 그 object identity를 담지 않아 `ISSUE_ALLOWED`가 반환됐다. H03에서는 receipt를 exact project/bucket/object/generation에 결합한다.
- 실제 후보 fixture의 선언 gap은 입력에서 복사된 주장일 뿐 외부 권리·provider 상태의 독립 검증이 아니다. `RAW_MANIFEST_CANDIDATE_MISSING`에 의한 HOLD 증거로만 해석한다.
- 후속 제출: `docs/workstreams/70-platform-gcp/handoffs/SPECTRA_70_RIGHTS_RAW_MANIFEST_PREFLIGHT_HANDOFF_H03.md`; malformed-input safe failure와 exact storage receipt binding을 반영해 재검토를 요청한다.

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
