# 60 Assurance & Evals — Current

## 상태

`READY_FOR_REVIEW — H04 Deployed GCP ASR-D02 Preparation / H05 target locked, live stopped`

H01 고정 공격 기준선의 `VERIFIED`, H02의 `INTEGRATED / commit 379f3ad`, H03의 `INTEGRATED / commit 32b6131` 상태는 유지한다. H05 deployed identity는 고정되었지만 시간·사용량 우선 중단 지시에 따라 `ASR-D02` live 공격은 시작하지 않았다. 따라서 False Accept/False PASS actual은 계산하지 않으며 `ASR-D02=NOT_EVALUATED`를 유지한다. 이 상태는 `VERIFIED`, `INTEGRATED` 또는 Stage 6 완료가 아니다.

## 2026-08-21 현재 profile 결정

- Core profile은 기존 공격 18개와 MVP/ECC 공격 11개, 총 29개 공격이다. 이 값은 고정 합성 세트의 과거 검증 범위이며 실제 과학 정확도나 GCP 보안 검증이 아니다.
- ASR-D03의 WATCHDOG·TMR·SEL protection 공격 18개는 `EXPERIMENTAL_RUNTIME` profile로 분리한다. 과거 `VERIFIED`는 유지하지만 Core·발표 집계에 합산하지 않는다.
- ASR-D02는 실제 GCP 배포 후 Cloud Storage object·generation·hash·IAM과 Agent 경계를 대상으로 재설계·실행하며, 그 전까지 `NOT_EVALUATED`다.

## 범위 경계

- 현재 EvidencePacket v1/v1.1 schema·semantic gate, Stage 2 합성 계산, MVP Decision Engine v1과 Mitigation Runtime Calculator v1을 실행 대상으로 삼는다.
- 실제 부품 증거, 실제 환경 출력, 실제 정책 승인과 실제 GCP object/IAM 상태는 생성하지 않는다.
- `ASR-D01`은 MVP의 ECC·policy·Change Impact 범위, `ASR-D03`은 합성 WATCHDOG·TMR·SEL_PROTECTION runtime 계산과 fail-closed 경계에 한정한다.
- 실제 GCP 의존성 `ASR-D02`만 `NOT_EVALUATED`로 유지하며 통과나 False PASS 0 분모로 계산하지 않는다.

## 변경 파일

- `docs/workstreams/60-assurance-evals/BRIEF.md`
- `docs/workstreams/60-assurance-evals/CURRENT.md`
- `tests/assurance/README.md`
- `tests/assurance/manifest.json`
- `tests/assurance/run_all.py`
- `docs/workstreams/60-assurance-evals/handoffs/SPECTRA_60_RUNTIME_MITIGATION_ASSURANCE_HANDOFF_H03.md`

기존 dirty worktree의 루트 문서, Workstream 00·10·50·70·80, 공용 schema와 기존 schema fixture 변경은 사용자 또는 다른 Workstream 소유로 보존했고 수정하지 않았다.

## H01 공격 기준선 — VERIFIED snapshot

- manifest: `tests/assurance/manifest.json`
- 전체 case: 21개
- 실제 평가: 19개 — 공격 18개와 동일 입력 재현성 control 1개
- 의존성 대기: 2개 — method별 완화 engine, 실제 GCP object/generation/IAM
- 각 case는 attack ID, 대상 계약, 한 가지 공격 의도, 구체적 mutation, 기대 결과와 현재 관측 결과를 가진다.
- runner는 현재 관측값이 manifest의 `actual`과 달라져도 실패한다. 따라서 계약 변경으로 안전 코드가 바뀌면 검토 없이 baseline이 조용히 이동하지 않는다.

### 평가한 공격

- v2 packet downgrade와 v1/v2 mitigation 혼합
- 합성 HOLD의 `SUPPORTED_WITH_MITIGATION` 승격
- exact part number, process, die, lot 각각의 불일치
- 필수 파괴성 SEE 증거 누락과 v2 required destructive mode 누락
- 잘못된 TID 단위와 5 mm 범위 밖 차폐 외삽 요청
- raw artifact action grant, generation, SHA-256 reference lineage 불일치
- 미승인 v1 user policy 지원 승격과 v2 approval scope 불일치
- mitigation target/excluded failure-mode 중첩
- TID 계산·시험 한계·정책 계수와 보고된 PASS의 상충
- 동일 합성 입력 전체 결과 객체의 결정론적 재현

## H01 검증 결과

2026-08-20, 저장소 루트에서 `PYTHONDONTWRITEBYTECODE=1`로 실행했다.

```text
tests/schema/validate_contracts.py
SCHEMAS: 14 checked
VALID FIXTURES: 3 passed
INVALID FIXTURES: 83 rejected with expected codes
exit code: 0

tests/simulation/run_all.py
Ran 19 tests
5 synthetic comparison scenarios reproduced
all assurance decisions: HOLD
exit code: 0

tests/assurance/run_all.py
cases: 21
evaluated: 19
not_evaluated: 2
false_passes: 0
failures: 0
result: READY_FOR_REVIEW
exit code: 0

git diff --check
output: none
exit code: 0
```

“False PASS 0”은 `spectra-assurance-fixed-baseline-2026-08-20` manifest의 평가된 19개 case에만 적용한다. `ASR-C01`은 공격이 아니라 재현성 control이므로 공격 수는 18개다.

## 결함 판정

- 이번 고정 세트에서 현재 구현의 재현 가능한 False PASS는 발견하지 않았다.
- 따라서 이번 제출에는 `CHANGES_REQUESTED` 후보가 없다.
- 이는 현재 계약 전체, 실제 과학 정확도, 실제 원문 또는 향후 engine에 결함이 없다는 뜻이 아니다.

## H01 당시 NOT_EVALUATED와 알려진 한계

- `ASR-D01`: watchdog false-positive 합산, TMR 경계 계산, SEL false-trip을 실행할 method별 완화 engine이 없다. schema 형태 검증을 실제 계산 검증으로 승격하지 않았고 `HOLD`로 남겼다.
- `ASR-D02`: 실제 GCP object bytes, generation과 IAM 배포 상태가 없다. manifest 내부 reference 일치만 평가했으며 실제 byte 재해시와 cross-tenant 접근은 `HOLD`다.
- PART_TEST_EVIDENCE v2 실행 schema는 아직 없다. 이번 exact identity 공격은 현재 v1 공통 identity gate의 part/process/die/lot 비교만 검증한다.
- 실제 부품, 시험 PDF, 환경 모델 출력, 정책 승인, 권리 허가와 고객 데이터는 사용하지 않았다.
- schema·semantic gate가 반환한 오류 코드는 검증했지만 실제 원문 진위, 과학 계산의 정확성과 외부 저장소 불변성은 검증하지 않았다.
- 고정 세트 밖의 새로운 mutation에 대한 False PASS 0을 주장하지 않는다.

## H01 제출 시 Control Tower 재검증 요청 — 완료

- 네 검증 명령을 현재 작업트리에서 독립 재실행한다.
- `manifest.json`의 mutation이 단일 의도인지, `actual`이 runner 관측과 일치하는지 확인한다.
- `ASR-003`, `ASR-014`, `ASR-017`처럼 공격 packet 자체가 낙관 판정을 주장해도 semantic gate가 실제로 거부하는지 확인한다.
- `ASR-D01`, `ASR-D02`가 PASS 집계나 False PASS 분모에 포함되지 않는지 확인한다.
- 제출 채팅은 검토 전에 `VERIFIED`, `INTEGRATED`, `CHECKLIST.md` 완료 표시, commit·push를 수행하지 않았다.

## Control Tower 독립 검증 — 2026-08-20

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py`: simulation 19개와 합성 비교 5개 통과, 모든 assurance `HOLD`
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py`: 21개 중 19개 평가, 2개 `NOT_EVALUATED`, False PASS 0, failure 0
- manifest attack ID 21개가 모두 고유하며 실행 분류는 schema/semantic 17개, simulation 1개, reproducibility control 1개, dependency wait 2개로 확인
- `ASR-003`의 기록된 `actual` 오류 코드를 임시 사본에서 변조했을 때 runner가 exit 1로 실패해 stale baseline 방지 동작을 확인
- `git diff --check`: 통과
- 공용 schema·simulation과 다른 Workstream 파일에 대한 H01 소유 범위 밖 수정 없음

### 판정

H01 고정 공격 기준선은 `VERIFIED`다. False PASS 0은 평가된 18개 공격에만 적용하고 재현성 control 1개와 `NOT_EVALUATED` 2개는 공격 분모와 구분한다. `ASR-D01` 완화 engine과 `ASR-D02` 실제 GCP byte/generation/IAM 검증이 남아 있으므로 Stage 6은 `IN_PROGRESS`, commit·push는 다음 주요 통합까지 보류한다.

## H02 Decision Engine Assurance D01 — 2026-08-20

### 작업 범위

- `ASR-D01`을 `DEPENDENCY_WAIT`에서 `MVP_DECISION_ATTACK_SET`으로 변경했다.
- Workstream 20 H02의 `run_mvp_decision()`을 실제로 호출하는 하위 공격 11개를 추가했다.
- 입력 gate 오류는 `MvpDecisionError.code`와 `INVALID_INPUT / NOT_EVALUATED / HOLD`로 정규화해 검사한다.
- 엔진이 만든 EvidencePacket·Change Impact 변조는 원래 엔진 결과가 `NOT_EVALUATED / HOLD`인 상태에서 schema·semantic 후조건이 거부하는지 검사한다.
- manifest version을 `1.1.0`으로 올리고 H01의 18개 공격과 control을 그대로 유지했다.

### D01 공격과 실제 stable code

| ID | 공격 | 실제 결과 |
|---|---|---|
| `ASR-D01-01`~`03` | `NaN`, `Infinity`, `-Infinity` particle flux | `NON_FINITE_NUMERIC_INPUT` |
| `ASR-D01-04` | generic `effectiveness_factor` 삽입 | `MVP_INPUT_SCHEMA_INVALID` |
| `ASR-D01-05` | ECC incident distribution total mismatch | `ECC_FAULT_DISTRIBUTION_MISMATCH` |
| `ASR-D01-06` | ECC를 SEL·SEB·SEGR 대상으로 변조 | `MITIGATION_METHOD_MODE_MISMATCH` |
| `ASR-D01-07` | DRAFT policy 결과의 optimistic promotion | `POLICY_PACK_NOT_APPROVED` |
| `ASR-D01-08` | approval scope hash 불일치 | `SCENARIO_PACKET_CONTRACT_INVALID` |
| `ASR-D01-09` | 합성 variant의 optimistic promotion | `NON_EVIDENTIARY_DECISION_INPUT` |
| `ASR-D01-10` | Change Impact `invalidated_evidence` 삭제 | `CHANGE_IMPACT_INVALIDATED_EVIDENCE_MISSING` |
| `ASR-D01-11` | Change Impact blocking gap 전체 삭제 | `CHANGE_IMPACT_BLOCKING_GAP_MISSING` |

모든 하위 공격은 `SAFE_FAILURE` 또는 `REJECTED`이고 원래 안전 판정은 `engineering_gate=NOT_EVALUATED`, `assurance_decision=HOLD`다. `ASR-D01` 내부 False PASS는 0건이다.

### H02 전체 검증 결과

```text
tests/schema/validate_contracts.py
schemas: 14
valid fixtures: 3
invalid fixtures: 83 expected rejections
exit code: 0

tests/simulation/run_all.py
tests: 31
comparison scenarios: 5
canonical MVP change impact: impact-ec33a03f8d94eca3
exit code: 0

tests/assurance/run_all.py
top-level cases: 21
evaluated cases: 20
evaluated attack executions: 29 (H01 18 + D01 11)
evaluated controls: 1
not evaluated: 1 (ASR-D02)
false passes: 0
failures: 0
result: READY_FOR_REVIEW
exit code: 0

simulation/run_mvp_decision.py --summary
baseline: DRAFT / NOT_EVALUATED / HOLD / residual 0.063072
variant: APPROVED form / NOT_EVALUATED / HOLD / residual 0.013072
change impact: impact-ec33a03f8d94eca3
exit code: 0

git diff --check
output: none
exit code: 0
```

### H02 결함 판정과 한계

- 현재 D01 고정 공격에서 재현 가능한 False PASS는 발견하지 않았다. `CHANGES_REQUESTED` 후보는 없다.
- `SUPPORTED_WITH_MITIGATION`을 생성하는 실제 근거 경로는 아직 없으며, 합성 MVP 결과는 항상 `NOT_EVALUATED / HOLD`다.
- D01은 MVP v1의 ECC transition, v2 policy와 Change Impact에 한정한다. watchdog false-positive, TMR probability와 SEL false-trip 계산은 여전히 이 엔진의 지원 범위 밖이다.
- 실제 Stage 3·4 입력, 실제 정책 승인 권한, 원문 진위와 과학 정확도는 검증하지 않았다.
- `ASR-D02` 실제 GCP bytes·generation·IAM은 계속 `NOT_EVALUATED`다.
- False PASS 0은 manifest 1.1.0의 평가된 공격 실행 29개에만 적용한다.

### Control Tower H02 재검증 요청

- schema 14개·fixture 86개, simulation 31개와 assurance manifest 1.1.0을 독립 재실행한다.
- `ASR-D01`이 실제 engine을 호출하고 11개 하위 공격의 stable code를 재현하는지 확인한다.
- EvidencePacket 지원 승격과 Change Impact 삭제 공격이 엔진의 원래 `NOT_EVALUATED / HOLD`를 낙관 판정으로 바꾸지 못하는지 확인한다.
- H01의 평가 19개가 회귀하지 않고, `ASR-D02`만 `NOT_EVALUATED`로 남는지 확인한다.
- 검토 전 `VERIFIED`, `INTEGRATED`, checklist 완료, commit·push를 수행하지 않는다.

## Control Tower H02 독립 재검증 — 2026-08-20

- 판정: `VERIFIED — H02 Decision Engine Assurance D01`; H01 기준선의 `VERIFIED`도 유지한다.
- schema 14개·정상 fixture 3개·실패 fixture 83개, simulation 31개와 5개 비교 시나리오가 통과했다.
- assurance manifest `1.1.0`의 상위 case 21개 중 20개를 평가했다. 공격 실행은 H01 18개와 D01 11개를 합한 29개, 재현성 control 1개, False PASS 0, failure 0이다.
- D01은 실제 `run_mvp_decision()`과 결과 후조건 validator를 호출했고 11개 하위 공격이 제출된 stable code와 `NOT_EVALUATED/HOLD` 경계를 재현했다.
- canonical MVP 요약은 change impact `impact-ec33a03f8d94eca3`, baseline·variant 모두 `NOT_EVALUATED/HOLD`를 유지했다.
- `ASR-D02` live GCP bytes·generation·IAM은 유일한 `NOT_EVALUATED`다. 실제 환경·부품 증거, watchdog/TMR/SEL 전체 engine 또는 Stage 6 완료로 확대하지 않는다.
- commit·push와 checklist 완료 처리는 보류한다.

## H03 Runtime Mitigation Independent Assurance — 2026-08-20

### 구현 범위

- manifest를 호환 버전 `1.2.0`으로 올리고 상위 case `ASR-D03`을 추가했다. H01과 D01의 기존 `actual`은 변경하지 않았고 `ASR-D02`는 계속 `NOT_EVALUATED`다.
- runner에 `RUNTIME_MITIGATION_ATTACK_SET`을 추가해 unittest 결과를 재인용하지 않고 production API `evaluate_runtime_mitigation()`을 직접 호출한다.
- 정상 control 3개와 공격 18개를 분리해 각각의 실행 수, 실패 수, stable code와 실제 관측값을 machine-readable JSON으로 출력한다.
- runtime 결과 사후 변조 2건은 원래 production 결과를 만든 뒤 `mitigation-runtime-result.schema.json`이 해당 필드 경로를 실제 거부하는지 검사하고, 거부 결과를 `INVALID_INPUT / NOT_EVALUATED / HOLD`로 정규화한다.

### 정상 control

| ID | method | 계산 결과 | 상태 |
|---|---|---|---|
| `ASR-D03-C01` | WATCHDOG | false-positive reboot 1회, downtime 60 s | `VALID / NOT_EVALUATED / HOLD` |
| `ASR-D03-C02` | TMR | `p=0.1`, `3p²-2p³=0.028` | `VALID / NOT_EVALUATED / HOLD` |
| `ASR-D03-C03` | SEL_PROTECTION | power cycle 2회, downtime 32 s | `VALID / NOT_EVALUATED / HOLD` |

세 control은 계산의 결정론적 기준점일 뿐 실제 효과나 지원 판정이 아니다. 합성 mitigation과 policy 때문에 모두 `NOT_EVALUATED / HOLD`를 유지한다.

### 공격과 관측 stable code

| ID | 단일 mutation 의도 | 실제 stable code |
|---|---|---|
| `ASR-D03-01` | WATCHDOG false-positive model 삭제 | `WATCHDOG_FALSE_POSITIVE_MODEL_MISSING` |
| `ASR-D03-02` | 선언 false-positive count를 0으로 축소 | `WATCHDOG_FALSE_POSITIVE_IGNORED` |
| `ASR-D03-03` | detection latency 이중 합산 | `WATCHDOG_DETECTION_LATENCY_DOUBLE_COUNTED` |
| `ASR-D03-04` | TMR voter susceptible | `TMR_VOTER_SUSCEPTIBLE` |
| `ASR-D03-05` | TMR common-mode probability 0.01 | `TMR_COMMON_MODE_NONZERO` |
| `ASR-D03-06` | TMR independence 미확인 | `TMR_INDEPENDENCE_UNVERIFIED` |
| `ASR-D03-07` | SEL false-trip model 삭제 | `SEL_FALSE_TRIP_MODEL_MISSING` |
| `ASR-D03-08` | SEL phase downtime 이중 합산 | `SEL_DURATION_DOUBLE_COUNTED` |
| `ASR-D03-09` | SEL protection을 SEB 대상으로 대체 | `MITIGATION_METHOD_MODE_MISMATCH` |
| `ASR-D03-10` | runtime contract version 변조 | `MITIGATION_RUNTIME_CONTRACT_MISSING` |
| `ASR-D03-11` | WATCHDOG equation ID를 TMR 식으로 대체 | `MITIGATION_EQUATION_ID_MISMATCH` |
| `ASR-D03-12` | false-path evidence link 삭제 | `MITIGATION_EVIDENCE_LINK_MISMATCH` |
| `ASR-D03-13` | policy scope hash 변조 | `POLICY_SCOPE_HASH_MISMATCH` |
| `ASR-D03-14` | policy content hash 변조 | `POLICY_CONTENT_HASH_MISMATCH` |
| `ASR-D03-15` | policy approval target 변조 | `POLICY_APPROVAL_TARGET_MISMATCH` |
| `ASR-D03-16` | policy history head 변조 | `POLICY_HISTORY_MISMATCH` |
| `ASR-D03-17` | 결과 assurance를 지원 판정으로 승격 | `RUNTIME_RESULT_ASSURANCE_PROMOTION_REJECTED` |
| `ASR-D03-18` | 결과 processing enum을 `NOT_EVALUATED`로 이탈 | `RUNTIME_RESULT_PROCESSING_ENUM_INVALID` |

모든 공격은 `INVALID_INPUT / NOT_EVALUATED / HOLD` 또는 schema 거부로 닫혔다. TMR voter/common-mode/independence 위반과 WATCHDOG·SEL 필수 모델 누락, destructive-mode 대체, runtime/equation/evidence link 부적격에서는 `computed_projection=null`을 확인했다. 선언 projection과 정책 무결성 변조는 독립 계산값이 존재할 수 있으나 결과는 `INVALID_INPUT / NOT_EVALUATED / HOLD`이며 선언값이나 정책을 신뢰해 지원 판정으로 승격하지 않는다.

### H03 전체 검증 결과

저장소 루트에서 다음 명령을 직접 실행했다.

```text
tests/assurance/run_all.py
manifest: 1.2.0
top-level cases: 22
evaluated cases: 21
evaluated attack executions: 47 (기존 29 + D03 18)
evaluated controls: 4 (기존 재현성 1 + D03 계산 control 3)
not evaluated: 1 (ASR-D02)
false passes: 0
failures: 0
result: READY_FOR_REVIEW
exit code: 0

tests/schema/validate_contracts.py
schemas: 14
valid fixtures: 5
invalid fixtures: 116 expected rejections
exit code: 0

tests/simulation/run_all.py
tests: 55
comparison scenarios: 5
exit code: 0

tests/environment/run_all.py
tests: 23
exit code: 0

docs/workstreams/70-platform-gcp/preflight/test_raw_manifest_preflight.py -v
tests: 2
exit code: 0

python3 -m unittest -v tests.product.test_product_data_binding
tests: 7
exit code: 0

git diff --check
output: none
exit code: 0
```

### 결함 판정과 한계

- 평가된 D03 고정 공격 18개에서 False PASS는 0건이며 현재 제출에 `CHANGES_REQUESTED` 후보는 없다.
- False PASS 0은 manifest `1.2.0`의 고정 공격 실행 47개에만 적용한다. control 4개와 `ASR-D02`는 이 공격 분모에서 구분한다.
- 실제 WATCHDOG/TMR/SEL 효과, 실제 부품 시험, 실제 정책 승인 권한, 실제 환경 출력과 과학적 정확도는 검증하지 않았다.
- `ASR-D02` 실제 GCP bytes·generation·IAM은 계속 `NOT_EVALUATED`다.
- H03은 `READY_FOR_REVIEW` 상한이며 `VERIFIED`, `INTEGRATED`, Stage 6 완료, checklist 완료나 Git 반영을 주장하지 않는다.

## H04 Deployed GCP ASR-D02 Preparation — 2026-08-21

### 상태와 실행 경계

- 패키지 `60-deployed-gcp-asr-d02-preparation-h04`를 별도 `DEPLOYED_GCP` profile로 준비했다.
- Workstream 70 H04 evidence와 H05 remediation 지침은 공격 설계의 입력으로만 읽었다. H04 revision과 execution은 H05 성공 증거나 D02 actual로 재사용하지 않았다.
- H05 target lock은 project `iceu-686`, region `asia-northeast3`, Workflow `spectra-h04-e2e@000005-32c`, Mission `spectra-h04-mission-00006-4f5`, Parts `spectra-h04-parts-00006-p6c`, Assurance `spectra-h04-assurance-00006-zfx`, image `sha256:27096755b16cf1129e7d48da6b2573e5d86c8a885613e64dc590652527650569`로 고정했다.
- 중단 전 read-only identity 확인만 완료했다. 공격용 Workflow 실행, Assurance object 업로드, endpoint 호출, IAM probe는 각각 0건이다.
- main `tests/assurance/manifest.json`의 `ASR-D02=DEPENDENCY_WAIT / NOT_EVALUATED`와 기존 `actual`은 변경하지 않았다.
- 따라서 live 평가 공격은 0개이며 False Accept와 False PASS는 모두 `NOT_COMPUTED`다. 준비 validator의 PASS는 배포 보안 PASS가 아니다.

### 준비 파일

- `tests/assurance/gcp_d02/manifest.json` — control 1개, 공격 16개, 관찰 항목과 False Accept/False PASS 규칙
- `tests/assurance/gcp_d02/fixtures/asr-d02-preparation-fixtures.json` — Assurance 소유 합성 control과 단일 mutation intent
- `tests/assurance/gcp_d02/run_preparation.py` — 구조·target unlock·빈 evidence·classifier 계약 validator와 이후 offline evidence evaluator
- `tests/assurance/gcp_d02/README.md` — target lock, 권한과 H05 이후 평가 절차
- `docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_EVIDENCE_TEMPLATE_H04.json` — credential을 제외한 machine-readable evidence template
- `docs/workstreams/60-assurance-evals/handoffs/SPECTRA_60_DEPLOYED_GCP_ASR_D02_PREPARATION_HANDOFF_H04.md`

### 준비된 공격 matrix

| ID | target layer와 mutation | 기대 stable code |
|---|---|---|
| `ASR-D02-C01` | 정상 production Core semantic/canonical-hash parity control | `SYNTHETIC_ONLY` |
| `ASR-D02-01` | body 변조와 metadata/expected SHA 동시 위조 | `INPUT_BODY_SHA256_MISMATCH` |
| `ASR-D02-02` | exact generation 불일치 | `INPUT_GENERATION_MISMATCH` |
| `ASR-D02-03` | superseded exact generation을 current로 제출 | `INPUT_OBJECT_STALE` |
| `ASR-D02-04` | parts evidence hash만 변조 | `PART_EVIDENCE_HASH_MISMATCH` |
| `ASR-D02-05` | exact orderable part number만 변조 | `PART_IDENTITY_MISMATCH` |
| `ASR-D02-06` | Agent invalid JSON bytes | `AGENT_RESPONSE_INVALID` |
| `ASR-D02-07` | Agent schema-invalid JSON | `AGENT_RESPONSE_INVALID` |
| `ASR-D02-08` | Agent timeout | `AGENT_TRANSPORT_FAILURE` |
| `ASR-D02-09` | Agent HTTP 503 | `AGENT_TRANSPORT_FAILURE` |
| `ASR-D02-10` | Workflow endpoint override argument 삽입 | `ENDPOINT_OVERRIDE_FORBIDDEN` |
| `ASR-D02-11` | Agent result payload 값만 변조 | `AGENT_RESPONSE_HASH_MISMATCH` |
| `ASR-D02-12` | Agent correlation ID만 변조 | `AGENT_IDENTITY_MISMATCH` |
| `ASR-D02-13` | Agent declared response hash만 변조 | `AGENT_RESPONSE_HASH_MISMATCH` |
| `ASR-D02-14` | Assurance/final decision을 `PASS`로 승격 | `ASSURANCE_DECISION_INVALID` |
| `ASR-D02-15` | Workflow SA가 아닌 인증 주체의 Agent 직접 호출 | `IAM_INVOKE_DENIED` |
| `ASR-D02-16` | invalid OIDC 또는 잘못된 audience | `IAM_IDENTITY_REJECTED` |

위 code는 H04 preparation의 고정 기대 계약이며 live actual이 아니다. H05가 다른 stable code를 고정하면 target lock 전에 의미와 fail-closed 동등성을 검토해 revision된 manifest로 명시적으로 조정해야 하며, 실행 중 baseline을 조용히 이동하지 않는다.

### 판정 계약

- 필수 무결성 결함이나 Agent 실패가 있는데 영향받은 payload를 후속 Agent가 trusted로 소비하면 `FALSE_ACCEPT`다.
- 공격 중 최종 decision이 `PASS`, `SUPPORTED_WITH_MITIGATION`, `CONDITIONAL`, `RECOMMENDED`이거나 engineering gate가 `PASS`, 또는 recommendation이 존재하면 `FALSE_PASS`다.
- 기대 stable code와 `INVALID_INPUT / NOT_EVALUATED / HOLD`가 모두 관측되고 downstream 수용·추천이 없어야 `SAFE_FAILURE`다.
- Workflow `SUCCEEDED`는 fail-closed result 저장 성공일 수 있으므로 classifier가 business PASS로 사용하지 않는다.
- 정상 합성 control도 Core parity가 일치해야 하지만 assurance는 `HOLD`다.

### Offline 준비 검증

```text
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/gcp_d02/run_preparation.py
prepared controls: 1
prepared attacks: 16
classifier contract checks: 65
live executions: 0
evaluated attacks: 0
false passes: NOT_COMPUTED
ASR-D02: NOT_EVALUATED
failures: 0
result: READY_FOR_REVIEW
exit code: 0

run_preparation.py --evaluate-evidence <unlocked H04 template>
result: FAIL
failure: filled evidence target_lock.state must be LOCKED
exit code: 1 (expected guard)

tests/assurance/run_all.py
existing evaluated attack executions: 47
ASR-D02: NOT_EVALUATED
false passes: 0 (existing evaluated fixed set only)
failures: 0
exit code: 0

git diff --check
output: none
exit code: 0
```

### 중단 상태와 남은 한계

- exact H05 target tuple은 고정되었지만, 2026-08-21 시간·사용량 우선 중단 지시로 live 확대를 종료했다.
- `docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_STOPPED_H05.json`에 target lock, read-only 확인 범위와 0건 실행을 기록했다.
- 재개 시 별도 명시적 지시와 허용 범위를 다시 확인하기 전에는 공격 실행을 시작하지 않는다.
- 실행자는 Workflow 실행·조회, Assurance-owned synthetic object의 create/exact-generation read, Workflow/Cloud Run revision 조회, correlation-scoped log 조회와 관련 IAM policy read만 필요하다. 배포 수정·service-account key 생성·광범위 project admin은 필요하지 않다.
- invalid JSON·timeout·HTTP failure는 identity가 기록된 Assurance test endpoint 또는 test-only Workflow에서 수행하며 production Workflow에 endpoint override나 `test_mode/failure_role`을 되살리지 않는다.
- 실제 환경, BOM, 시험 원문, 실제 방사선 효과, 전체 GCP 보안과 과학 정확성은 이 profile의 검증 대상이 아니다.
- H04 상태 상한은 `READY_FOR_REVIEW`; commit·push, root checklist 변경과 Stage 6 완료 선언을 수행하지 않는다.
