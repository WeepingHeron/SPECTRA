# 50 Mitigation & Policy — Current

## 상태

`INTEGRATED — H02 contract design / commit 379f3ad`

이 상태는 완화·정책 엔진의 **계약 조사와 결정론적 설계 패키지 H02**가 Control Tower 독립 검증 후 Git에 통합됐다는 뜻이다. Stage 5 전체 구현, 실제 효과 계산 또는 실제 policy 승인을 뜻하지 않는다.

## 이번 패키지

- 세션: `50-mitigation-policy`
- 패키지: `50-mitigation-policy-contract-design-v1`
- 수정 제출: `H02` — watchdog false-positive와 TMR probability semantics 보정
- 변경 범위: Workstream 50의 `BRIEF.md`, `RESEARCH.md`, `CURRENT.md`
- 공통 schema, tests, 루트 문서, 다른 Workstream 파일: 읽기 전용
- commit/push/checklist 변경: 수행하지 않음

## 완료한 설계

- 차폐, 부품 대체, ECC, scrubbing, TMR, watchdog/reboot, checkpoint/retry, SEL current limiting/power cycling, spare switching을 failure mode별로 분리했다.
- incident event, logical error, recovery, downtime, irreparable event를 서로 다른 계산 축으로 정의했다.
- method별 typed input, unit, output, 결정론적 식 또는 계산 불가 조건을 정의했다.
- 현행 범용 `effectiveness_factor`를 실제 지원 근거로 쓰지 않고 equation/evidence 없는 경우 `ARBITRARY_MITIGATION_FACTOR + HOLD`로 종료하도록 요구했다.
- `PUBLISHED`, `CUSTOMER_VERIFIED`, `CALCULATED`의 조건부 사용과 `ASSUMED`, `SYNTHETIC`의 최종 판정 사용 금지를 정의했다.
- 조직 기본 policy pack, custom exception, scope·유효기간·승인 target/hash·immutable history 계약을 정의했다.
- SEL·SEB·SEGR을 개별 required mode로 평가하고 ECC/scrubbing/TMR로 대체하지 못하게 했다.
- 정상·누락·오염·정책 우회·failure-mode substitution을 포함한 최소 공격 fixture 20건을 명세했다.
- H02에서 기존 20개를 보존하고 watchdog false-positive attack/control, TMR 경계·의미·voter/common-mode, SEL false-trip 누락 fixture 9개를 추가해 총 29개 ID를 명세했다.
- watchdog true/false activation을 별도 path로 계산하고 reboot count와 downtime에 합산하며, 오탐 모델 누락 시 `NOT_EVALUATED + HOLD`로 고정했다.
- TMR 제한식 출력을 `system_failure_probability`로 고정하고 `p=0 → 0`, `p=0.1 → 0.028`, `p=1 → 1` 경계와 의미를 명시했다.
- Workstream 10·20·40·60의 schema/engine/evidence/eval 전달 요구사항을 정리했다.

## 조사 출처와 데이터 상태

공식 NASA NESC RHA 보고서, NASA NESC Technical Bulletin 19-01-1, NASA SEE Criticality Analysis, NASA/TM-2019-220269, NASA radiation reliability tutorial, ESCIES 공식 radiation standards index를 확인했다.

이 출처들은 방법별 적용 범위와 검증 필요성을 뒷받침한다. 특정 부품·SPECTRA 설계의 수치 완화율은 제공하지 않으므로 임의 계수를 만들지 않았다.

- 실제 Stage 3 환경·차폐 run: 0건
- 실제 Stage 4 승인 BOM·시험 원문·수치: 0건
- 실제 조직 policy pack/custom exception: 0건
- `PUBLISHED` 또는 `CUSTOMER_VERIFIED` decision operand: 0건
- 실제 `CALCULATED` 완화 효과: 0건
- fixture 구현: 0건; 문서 명세만 존재

## 현재 HOLD

| Gap | 상태 | 재개 조건 |
|---|---|---|
| `STAGE3_INPUT_UNAVAILABLE` | 실제 TID/SEE environment와 shielding transport 없음 | Workstream 30의 provenance-complete 실제 출력 |
| `STAGE4_INPUT_UNAVAILABLE` | 실제 BOM과 event별 evidence 없음 | Workstream 40 계약을 만족한 승인 evidence |
| `SCHEMA_VERIFIED_ENGINE_PENDING` | Workstream 10 H05의 MITIGATION/POLICY v2 schema·validator 검증 완료; 계산 미구현 | Workstream 20 method별 engine과 Workstream 60 공격 fixture |
| `ENGINE_IMPLEMENTATION_PENDING` | method별 calculator/policy evaluator 미구현 | Workstream 20 구현과 재현 테스트 |
| `ADVERSARIAL_FIXTURES_PENDING` | 공격 fixture 미구현 | Workstream 60 paired fixture와 target-code 실행 |
| `POLICY_OWNER_UNASSIGNED` | 조직 policy owner/approver 역할 미지정 | 역할 분리와 승인 권한 결정 |
| `AUDIT_ANCHOR_UNAVAILABLE` | immutable approval history anchor 미지정 | Workstream 70/Control Tower 저장·감사 계약 |

## 검증 범위

이번 채팅에서 실행하는 검증은 Markdown 구조, 링크/식별자 존재, `git diff --check`, 기존 schema/simulation 회귀에 한정한다. 기존 회귀가 통과해도 새 v2 schema·engine·fixture가 존재하지 않으므로 Stage 5 검증 완료로 승격하지 않는다.

## False PASS 위험

가장 큰 위험은 다음과 같다.

- Stage 2 합성 ECC `effectiveness_factor`를 실제 완화 효과로 재사용
- SEL 하나 또는 SEU/ECC 결과로 SEL·SEB·SEGR 전체 gate를 통과
- watchdog/reboot/spare switching을 incident-rate 감소로 계산
- watchdog/SEL protection의 false-positive·false-trip을 0으로 간주해 reboot/power-cycle/downtime 정책을 통과
- TMR `3p²-2p³`를 success probability, reliability 또는 availability로 잘못 표시
- TID shielding factor를 SEE spectrum에 그대로 복사
- 대체 부품에 이전 부품 evidence/approval을 재사용
- policy status 문자열만 `APPROVED`로 바꾸거나 만료·범위 밖 exception 재사용
- `ASSUMED` 입력으로 만든 `CALCULATED` 결과를 evidence laundering에 사용

이 위험들은 모두 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`로 종료해야 한다.

## 다음 의존 작업

1. Workstream 10이 v2 schema/semantic contract와 migration을 검토한다.
2. Workstream 20이 generic factor 없이 method별 결정론적 calculator와 policy evaluator를 구현한다.
3. Workstream 40이 event·설계별 effect evidence 입력을 제공한다.
4. Workstream 30이 provenance-complete 실제 환경/차폐 입력을 제공한다.
5. Workstream 60이 명세 fixture를 구현하고 False PASS 0을 독립 검증한다.

H02 문서 계약은 Control Tower 독립 검토에서 `VERIFIED`됐다. `INTEGRATED`, Stage 5 완료, checklist 완료 또는 Git 반영은 Control Tower의 별도 판단 전까지 선언하지 않는다.


## Control Tower H01 독립 검증 — 2026-08-20

- 판정: `CHANGES_REQUESTED` — `50-mitigation-policy-contract-design-v1` 문서 계약 패키지에 한정한다. Stage 5 구현은 아직 0건이다.
- 회귀 재실행: schema 11개, required input kind 7종 exact-one, 정상 fixture 2개, 실패 fixture 71개와 simulation test 19개가 통과했다. 이는 기존 v1/합성 경로 회귀이며 이 문서의 v2 구현 검증이 아니다.
- 구조 검사: 공격 fixture 명세 20개가 고유했고 `git diff --check`가 통과했다.
- 원문 대조: NASA 자료는 recoverable/irreparable SEE를 availability/reliability로 분리하고, watchdog·redundancy·SEL protection을 mission/device-specific 설계와 시험 조건으로 평가해야 한다는 문서 방향을 뒷받침한다. 특정 SPECTRA 완화율을 제공하지 않는다는 한계도 올바르게 유지했다.

### 수정이 필요한 계산 계약

1. watchdog/reboot 입력에는 `false-positive rate`가 있지만 식 `N_reboot = N_target × coverage`와 downtime 합산에는 false-positive activation이 없다. 실제 target event가 0이고 오탐 재부팅이 1회/mission, 복구 경로가 60초인 독립 spot check에서 현재 식은 `0회, 0초`를 만들지만 실제 정책 operand는 `1회, 60초`여야 한다. 이 누락은 reboot/downtime 한도를 잘못 통과시키는 False PASS가 될 수 있다.
2. TMR 식 `3p²-2p³`은 독립 3-replica 중 2개 이상이 실패할 확률인데 출력명이 `P_system`으로만 적혀 성공확률/가용성과 혼동될 수 있다. `p=0.1`일 때 식은 `0.028`의 system failure probability이고 availability 후보는 `0.972`다. 출력 의미와 단위를 명시적으로 고정해야 한다.

### H02 수정 요구와 Exit Gate

- watchdog의 true-positive recovery와 false-positive activation을 별도 count/path로 계산하고 reboot count·downtime에 모두 합산한다.
- false-positive 입력의 denominator와 time window를 명시한다. 값 또는 검증 모델이 없으면 `RECOVERY_MODEL_INPUT_MISSING` 또는 별도 안정 코드로 `NOT_EVALUATED + HOLD`를 반환한다.
- `mitigation-v2-watchdog-false-positive-ignored` 공격과 최소 차이 paired control을 fixture 명세에 추가한다.
- SEL current protection도 false-trip output을 주장하려면 오탐 모델/검증 입력을 요구하고, 없으면 해당 output을 `NOT_EVALUATED`로 둔다.
- TMR 제한식의 출력명을 `system_failure_probability` 또는 동등한 명확한 이름으로 고정하고 success/availability와 서로 대체하지 못하게 한다.
- `p=0`, `p=0.1`, `p=1` 경계 paired fixture와 voter/common-mode 누락 공격을 명세한다.
- 다음 handoff는 `docs/workstreams/50-mitigation-policy/handoffs/SPECTRA_50_MITIGATION_POLICY_HANDOFF_H02.md`로 제출하고 `READY_FOR_REVIEW`까지만 요청한다.

## H02 변경 요청 반영 — 2026-08-20

- watchdog 계약: true-positive activation과 false-positive activation을 별도 count/path로 정규화하고 `reboot_count_total`과 `downtime_total`에 모두 합산한다. false-positive rate는 denominator scope와 evaluation window를 요구하며, 누락 시 `WATCHDOG_FALSE_POSITIVE_MODEL_MISSING + NOT_EVALUATED + HOLD`다.
- watchdog spot check: `N_target=0`, `N_false=1/mission`, false reboot path `60 s`에서 결과를 `1 reboot`, `60 s downtime`으로 고정했다.
- SEL protection: false-trip count/rate·denominator·window와 path가 없으면 0으로 간주하지 않고 total power-cycle/downtime을 `NOT_EVALUATED + HOLD`로 둔다.
- TMR 의미: `p`를 같은 evaluation window에서 repair 전 단일 replica 실패확률로 정의하고 제한식 출력을 `system_failure_probability`로 고정했다. success probability는 조건부 complement일 뿐 reliability/availability가 아니다.
- TMR 경계: 동일 operand/window에서 `p=0 → 0`, `p=0.1 → 0.028`, `p=1 → 1`을 명세했다. voter, common-mode, independence, repair/window 입력이 없으면 제한식을 실행하지 않는다.
- fixture: H01 20개 ID를 유지하고 H02 9개를 추가해 총 29개 고유 fixture ID를 명세했다. 실제 fixture 파일은 만들지 않았다.
- 회귀 재실행: schema 11개, 정상 fixture 2개, 실패 fixture 71개와 simulation test 19개가 통과했다. 문서 fixture는 29개/unique 29개이고 H01 구간은 20개다.
- 독립 산술 확인: 제한식은 `p=0 → 0`, `p=0.1 → 0.028000000000000004`(문서 표기 `0.028`), `p=1 → 1`을 반환했다.
- 상태: `READY_FOR_REVIEW`; 공통 schema, tests, 다른 Workstream, checklist, commit, push는 수정하지 않았다.

## Control Tower H02 독립 검증 — 2026-08-20

- 판정: `VERIFIED` — `50-mitigation-policy-contract-design-v1` H02 문서 계약 패키지에 한정한다. Stage 5 구현 또는 실제 완화 효과 검증을 뜻하지 않는다.
- watchdog 교차검산: `N_target=0`, `N_false=1/mission`, false reboot path `60 s`에서 `reboot_count_total=1`, `downtime_total=60 s`가 되며 false-positive 모델 누락은 0으로 대체하지 않고 `NOT_EVALUATED + HOLD`로 종료하도록 계약했다.
- TMR 교차검산: `3p²-2p³`은 `p=0 → 0`, `p=0.1 → 0.028`, `p=1 → 1`을 재현했고 출력 의미를 evaluation-window 단위 `system_failure_probability`로 고정했다. voter, common-mode, independence 또는 repair/window 근거가 없으면 제한식을 실행하지 않는다.
- fixture 구조: H01 20개와 H02 9개, 총 29개 ID가 고유하며 공격과 paired control의 기대 차이가 명시됐다. 실제 fixture 파일은 아직 0개다.
- 회귀 재실행: `python3 tests/schema/validate_contracts.py`에서 schema 11개, 정상 fixture 2개, 실패 fixture 71개가 통과했고 `python3 tests/simulation/run_all.py`에서 19개 테스트와 비교 CLI가 통과했다. 이는 기존 계약·합성 기준선 회귀이며 H02 구현 증거로 승격하지 않는다.
- 데이터 상태: 실제 Stage 3·4 입력, 실제 false-positive/false-trip 데이터, 실제 policy pack과 decision-eligible operand는 모두 0건이다. 최종 assurance는 `HOLD`다.

## 계약 패키지 종료와 대기

- `50-mitigation-policy-contract-design-v1` H02 문서 계약 패키지는 `VERIFIED` 상태로 종료하고 대기한다.
- 채팅 50은 공통 schema, Simulation Core calculator, Assurance fixture 또는 GCP 저장·감사 경로를 직접 구현하지 않는다.
- Workstream 10은 `MITIGATION/POLICY v2` schema와 validator를 소유한다.
- Workstream 20은 method별 calculator와 policy evaluator를 소유한다.
- Workstream 60은 29개 공격·control fixture와 False PASS 검증을 소유한다.
- Workstream 70은 immutable policy approval/audit anchor와 저장 계약을 소유한다.
- 후속 구현에서 계약 모순이 발견될 때만 채팅 50에서 H03 보완을 재개한다. 제출이 필요하면 `docs/workstreams/50-mitigation-policy/handoffs/SPECTRA_50_MITIGATION_POLICY_HANDOFF_H03.md`를 사용한다.
- `INTEGRATED`, Stage 5 완료, checklist 완료와 Git 반영은 Control Tower가 별도로 판단한다.
