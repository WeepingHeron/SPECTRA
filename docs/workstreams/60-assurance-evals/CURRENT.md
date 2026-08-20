# 60 Assurance & Evals — Current

## 상태

`INTEGRATED — H02 Decision Engine Assurance D01 / commit 379f3ad`

H01 고정 공격 기준선의 `VERIFIED` 판정은 유지한다. H02 패키지는 Workstream 20 H02 MVP Decision Engine을 독립 공격하고 `ASR-D01`을 실제 평가로 승격한 뒤 commit `379f3ad`로 통합했다. 이는 Stage 6 완료를 뜻하지 않는다.

## 범위 경계

- 현재 EvidencePacket v1/v1.1 schema·semantic gate, Stage 2 합성 계산과 MVP Decision Engine v1을 실행 대상으로 삼는다.
- 실제 부품 증거, 실제 환경 출력, 실제 정책 승인, method별 완화 engine과 실제 GCP object/IAM 상태는 생성하지 않는다.
- `ASR-D01`은 MVP의 ECC·policy·Change Impact 범위에서 평가한다. watchdog·TMR·SEL protection 전체 method engine을 검증했다는 뜻은 아니다.
- 실제 GCP 의존성 `ASR-D02`만 `NOT_EVALUATED`로 유지하며 통과나 False PASS 0 분모로 계산하지 않는다.

## 변경 파일

- `docs/workstreams/60-assurance-evals/BRIEF.md`
- `docs/workstreams/60-assurance-evals/CURRENT.md`
- `tests/assurance/README.md`
- `tests/assurance/manifest.json`
- `tests/assurance/run_all.py`

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
