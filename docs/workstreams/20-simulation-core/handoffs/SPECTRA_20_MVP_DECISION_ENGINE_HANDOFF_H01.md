# SPECTRA 채팅 20 H01 Handoff — MVP 결정론적 Decision Engine

## 작업 패키지

- 세션: `20-simulation-core`
- 패키지: `20-mvp-decision-engine-v1`
- 회차: `H01`
- 상태: `READY_FOR_REVIEW`
- 프로젝트: `/Users/taehoon/Desktop/IAA/SPECTRA`

이 상태는 Workstream 50의 검증된 완화·정책 설계와 Workstream 10의 v2 계약을 소비하는 합성 MVP Decision Engine 구현이 작업 채팅 검증을 통과했다는 뜻이다. `VERIFIED`, `INTEGRATED`, 실제 방사선 보증 완료 또는 Git 반영을 뜻하지 않는다.

## 구현 결과

- 정규화 입력 `simulation/fixtures/mvp-ecc-policy-v2.json`을 자체 schema로 검증한다.
- 참조한 EvidencePacket v1.1과 MITIGATION/USER_POLICY v2를 Stage 1 schema·semantic gate로 먼저 검증한다.
- 같은 엔진에서 baseline `ECC OFF + DRAFT policy`와 variant `ECC ON + APPROVED 형식 policy`를 실행한다.
- ECC는 범용 `effectiveness_factor`를 사용하지 않고 합성 multiplicity별 incident count와 outcome transition의 합으로 계산한다.
- baseline raw/residual은 `0.063072 events/mission`이다.
- variant는 corrected `0.05`, detected-uncorrectable `0.01`, silent-uncorrected `0.003072`, residual `0.013072 events/mission`이다.
- residual threshold는 baseline `FAIL`, variant `PASS`다.
- policy approval state는 baseline `FAIL`, variant `PASS`다.
- 실제 Stage 3 환경과 Stage 4 exact-part 증거가 없으므로 두 시나리오 모두 `engineering_gate=NOT_EVALUATED`, `assurance_decision=HOLD`다.
- `STAGE3_INPUT_UNAVAILABLE`, `STAGE4_INPUT_UNAVAILABLE`, `SYNTHETIC_ONLY`, `INDEPENDENT_ASSURANCE_PENDING`을 blocking gap으로 보존한다.
- ECC가 `SEL/SEB/SEGR` 증거를 대체하지 못하도록 failure-mode 경계를 적용한다.
- Change Impact에 입력·출력·판정 변화와 무효화된 baseline mitigation/policy ID를 machine-readable JSON으로 기록한다.
- CLI는 전체 canonical result, baseline/variant EvidencePacket 단독 export와 compact summary를 지원한다.

## 변경 파일

- `src/spectra_sim/__init__.py`
- `src/spectra_sim/contracts.py`
- `src/spectra_sim/mvp_engine.py`
- `simulation/fixtures/mvp-ecc-policy-v2.json`
- `simulation/run_mvp_decision.py`
- `simulation/schemas/mvp-decision-input.schema.json`
- `simulation/schemas/mvp-decision-result.schema.json`
- `simulation/schemas/change-impact.schema.json`
- `simulation/README.md`
- `tests/simulation/test_mvp_decision_engine.py`
- `tests/simulation/run_all.py`
- `docs/workstreams/20-simulation-core/BRIEF.md`
- `docs/workstreams/20-simulation-core/CURRENT.md`

## 실행 명령

```bash
cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
python3 simulation/run_mvp_decision.py --summary
python3 simulation/run_mvp_decision.py --evidence-packet variant
```

## 실제 검증 출력

```text
SCHEMAS: 14 checked
ENUM CONTRACTS: 4 axes checked
INPUT CARDINALITY: 7 required kinds exact-one
VERSION CONTRACTS: EvidencePacket 1.0.0/1.1.0 and v2 contracts checked
VALID FIXTURES: 3 passed
INVALID FIXTURES: 83 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate

Ran 28 tests in 2.073s
OK
```

CLI 요약:

```json
{"baseline":{"assurance":"HOLD","ecc_enabled":false,"engineering":"NOT_EVALUATED","policy":"DRAFT","residual":0.063072},"case_id":"mvp-synthetic-ecc-policy-001","change_impact_id":"impact-ec33a03f8d94eca3","variant":{"assurance":"HOLD","ecc_enabled":true,"engineering":"NOT_EVALUATED","policy":"APPROVED","residual":0.013072}}
```

## 공격·계약 검증

- 동일 입력 2회 실행의 전체 객체, canonical JSON과 input/output hash가 동일하다.
- 생성된 baseline·variant EvidencePacket은 각각 JSON Schema와 semantic gate를 통과한다.
- Change Impact와 전체 MVP 결과는 전용 JSON Schema를 통과한다.
- 범용 `effectiveness_factor` 삽입은 입력 schema가 거부한다.
- ECC distribution 총량이 raw SEU와 다르면 `ECC_FAULT_DISTRIBUTION_MISMATCH`로 종료한다.
- required `SEB` 증거 누락 공격은 ECC 결과와 무관하게 `DESTRUCTIVE_SEE_MODE_MISSING`으로 종료한다.
- APPROVED 형식 policy도 `SYNTHETIC`이므로 지원 판정으로 승격되지 않는다.

## 알려진 한계

- 합성 particle flux·cross section·ECC transition은 회귀 fixture이며 실제 Stage 3·4 근거를 대신하지 않는다.
- MVP v1은 한 임무·한 부품·ECC 한 방법·baseline/variant 한 쌍만 지원한다.
- ECC transition distribution은 Simulation 입력 schema에서 고정하지만 공통 Workstream 10 schema에는 아직 참조 ID만 존재한다.
- 실제 policy 승인 권한, immutable history anchor와 실제 원문 권리는 검증하지 않았다.
- 독립 Assurance 승인 전에는 실제 입력이 들어와도 이 H01 경로가 `SUPPORTED_WITH_MITIGATION`을 만들지 않는다.

## Control Tower 검토 요청

1. `python3 tests/schema/validate_contracts.py`와 `python3 tests/simulation/run_all.py`를 독립 재실행한다.
2. 동일 입력 반복 실행의 canonical 결과와 hash를 비교한다.
3. baseline·variant EvidencePacket의 schema·semantic gate를 독립 검증한다.
4. Change Impact의 입력·출력·판정 변화와 invalidated evidence를 확인한다.
5. ECC destructive-mode 대체, generic factor와 distribution mismatch 공격을 재실행한다.
6. 검증 후에만 `VERIFIED`, `INTEGRATED`, 체크리스트와 Git 반영을 결정한다.

## 소유권 경계

- 채팅 20은 `READY_FOR_REVIEW`까지만 선언했다.
- 루트 문서, 공통 schema와 다른 Workstream 변경은 수정하지 않았다.
- commit·push와 체크리스트 변경은 수행하지 않았다.
