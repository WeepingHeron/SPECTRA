# 20 Simulation Core Handoff

## Intended Session Owner

`20-simulation-core`

현재 파일은 잘못된 운영 안내로 채팅 10에서 먼저 생성됐다. 구현 내용은 보존하지만, 채팅 20이 파일과 검증 결과를 직접 인수·재확인하기 전에는 Workstream 20의 완료 후보로 인정하지 않는다.

## Status

`VERIFIED — H02 MVP Decision Engine synthetic baseline`

현재 작업 패키지: `20-mvp-decision-engine-v1` H02. H01에서 확인된 비유한 숫자 traceback 경로를 입력 경계와 하위 계산 경계에서 보완했다. `NaN`, `Infinity`, `-Infinity`는 direct engine과 CLI 모두 stable code를 가진 machine-readable `INVALID_INPUT / NOT_EVALUATED / HOLD`로 종료한다. Control Tower가 전체 schema·simulation·environment·assurance 회귀와 정상 canonical 결과를 독립 재현해 합성 MVP engine 기준선을 `VERIFIED`로 판정했다. 이전 Stage 2 합성 기준선의 `INTEGRATED` 판정 범위는 그대로 보존한다.

## H02 Control Tower 독립 재검증 — 2026-08-20

- schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- simulation 31개와 기존 비교 scenario 5개 통과
- `NaN`, `Infinity`, `-Infinity` direct engine·CLI 공격이 `NON_FINITE_NUMERIC_INPUT`, exit 2, traceback 없음, `INVALID_INPUT / NOT_EVALUATED / HOLD`로 종료
- 하위 TID·SEE `ValueError`가 stable `MvpDecisionError`로 변환됨
- 정상 canonical summary와 Change Impact ID `impact-ec33a03f8d94eca3` 유지
- environment 8개, assurance 21개 중 19 evaluated·2 `NOT_EVALUATED`, failure 0·False PASS 0 유지
- 판정 범위는 합성 Decision Engine이다. 실제 Stage 3·4 evidence 연결과 실제 지원 판정은 포함하지 않는다.

## H02 Handoff — 비유한 숫자 Fail-Closed 보완

### 수정 내용

- `validate_mvp_input()`이 schema gate보다 먼저 전체 정규화 입력을 결정론적 JSON pointer 순서로 순회한다.
- 모든 float 입력에서 `NaN`, 양의 `Infinity`, 음의 `Infinity`를 `NON_FINITE_NUMERIC_INPUT`으로 거부한다.
- TID·SEE 계산과 TID 시험 한계 변환에서 발생하는 예상 `ValueError`를 각각 `TID_CALCULATION_INPUT_INVALID`, `SEE_CALCULATION_INPUT_INVALID`의 `MvpDecisionError`로 변환한다.
- CLI 오류 JSON에 별도 `error_code` 필드를 추가했다. JSON 파싱 오류와 파일 오류도 각각 `INVALID_JSON_INPUT`, `INPUT_FILE_ERROR`로 구분한다.
- direct engine, CLI, 하위 TID·SEE 오류 변환 회귀를 추가해 Simulation 테스트를 28개에서 31개로 확장했다.

### H02 변경 파일

- `src/spectra_sim/mvp_engine.py`
- `simulation/run_mvp_decision.py`
- `tests/simulation/test_mvp_decision_engine.py`
- `docs/workstreams/20-simulation-core/CURRENT.md`

별도 handoff: `/Users/taehoon/Downloads/SPECTRA_20_MVP_DECISION_ENGINE_HANDOFF_H02.md`

Workstream 30 진행 파일, Workstream 40 문서, 루트 checklist, 공통 schema·계약은 수정하지 않았다. commit·push도 수행하지 않았다.

### H02 공격 실제 출력

세 입력 모두 CLI exit code `2`, stdout 없음, traceback 없음으로 동일하게 종료했다.

```text
NaN 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
Infinity 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
-Infinity 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
```

### H02 최종 검증

실행 명령:

```bash
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
python3 tests/assurance/run_all.py
python3 simulation/run_mvp_decision.py --summary
```

실제 출력 요약:

```text
SCHEMAS: 14 checked
VALID FIXTURES: 3 passed
INVALID FIXTURES: 83 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate

Ran 31 tests in 2.468s
OK

Assurance: cases 21, evaluated 19, NOT_EVALUATED 2, failures 0, false_passes 0
```

정상 canonical summary는 H01과 동일하다.

```json
{"baseline":{"assurance":"HOLD","ecc_enabled":false,"engineering":"NOT_EVALUATED","policy":"DRAFT","residual":0.063072},"case_id":"mvp-synthetic-ecc-policy-001","change_impact_id":"impact-ec33a03f8d94eca3","variant":{"assurance":"HOLD","ecc_enabled":true,"engineering":"NOT_EVALUATED","policy":"APPROVED","residual":0.013072}}
```

### H02 검토 경계

- 비유한 숫자 방어는 실제 환경·시험값을 추가하지 않으며 기존 합성 계산과 판정 규칙을 변경하지 않는다.
- 정상 baseline/variant의 hash 기반 ID와 canonical 결과는 유지된다.
- 합성 입력, 미승인 정책, 파괴성 SEE 공백은 계속 지원 판정으로 승격되지 않는다.
- 이 채팅은 `READY_FOR_REVIEW`까지만 선언한다. `VERIFIED`, `INTEGRATED`, checklist 변경과 commit·push는 Control Tower 소유다.

## H01 Control Tower 독립 검증 — 2026-08-20

- schema 14개, 정상 fixture 3개, 실패 fixture 83개를 다시 실행해 통과했다.
- simulation 28개, 합성 비교 5개와 CLI summary를 다시 실행해 통과했다.
- assurance 21개 중 19개 평가, 2개 `NOT_EVALUATED`, failure 0, False PASS 0을 유지했다.
- baseline·variant EvidencePacket export, canonical 재현성, ECC OFF/ON `0.063072 → 0.013072`, DRAFT/APPROVED 정책 비교와 최종 `NOT_EVALUATED/HOLD`를 재현했다.
- negative incident, approval scope tamper와 ECC→SEL 대체 공격은 안정된 `MvpDecisionError` 코드로 거부됐다.
- `particle_flux.value=NaN` 또는 `Infinity`는 `calculate_see()`의 일반 `ValueError("SEE inputs must be finite")`로 종료됐다. `run_mvp_decision.py`는 이 예외를 잡지 않아 구조화된 안전 실패 JSON 대신 traceback과 exit 1을 낸다.
- 지원 판정으로 승격되는 False PASS는 아니지만, MVP Exit Gate의 “모든 오염 입력이 설명 가능한 `HOLD/NOT_EVALUATED`로 종료”를 충족하지 못한다.

### H02 수정 요구

1. 입력 경계에서 모든 계산 숫자의 `NaN`·`Infinity`를 결정론적으로 거부하고 stable error code를 반환한다.
2. 하위 TID·SEE 계산의 예상 입력 오류를 `MvpDecisionError`로 변환해 CLI가 항상 machine-readable `INVALID_INPUT / NOT_EVALUATED / HOLD`로 종료하게 한다.
3. direct engine과 CLI 양쪽에 `NaN`, `Infinity`, `-Infinity` 회귀 테스트를 추가한다.
4. 정상 28개와 schema·assurance 전체 회귀를 유지하고 H02 handoff를 제출한다.

## H01 Handoff — MVP 결정론적 Decision Engine

### 구현 결과

- 한 개 정규화 입력 `simulation/fixtures/mvp-ecc-policy-v2.json`을 자체 schema로 검증하고, 참조한 EvidencePacket v1.1과 MITIGATION/USER_POLICY v2를 Stage 1 schema·semantic gate로 먼저 검증한다.
- 같은 엔진에서 baseline `ECC OFF + DRAFT policy`와 variant `ECC ON + APPROVED 형식 policy`를 실행한다.
- ECC는 범용 `effectiveness_factor`를 사용하지 않고, 명시된 합성 multiplicity별 incident count와 outcome transition의 합으로만 계산한다.
- baseline raw/residual은 `0.063072 events/mission`, variant는 corrected `0.05`, detected-uncorrectable `0.01`, silent-uncorrected `0.003072`, residual `0.013072 events/mission`을 재현한다.
- threshold rule은 baseline `FAIL`, variant `PASS`; policy approval state는 baseline `FAIL`, variant `PASS`로 비교된다.
- 실제 Stage 3 환경과 Stage 4 exact-part 증거는 0건이므로 양쪽 모두 `engineering_gate=NOT_EVALUATED`, `assurance_decision=HOLD`이며 `STAGE3_INPUT_UNAVAILABLE`, `STAGE4_INPUT_UNAVAILABLE`, `SYNTHETIC_ONLY`를 차단 gap으로 남긴다.
- ECC가 `SEL/SEB/SEGR` 증거를 대체하지 못하도록 excluded mode와 required destructive mode를 분리하고, 누락 공격을 `DESTRUCTIVE_SEE_MODE_MISSING`으로 차단한다.
- Change Impact는 ECC·mitigation·policy 입력 변화, residual·corrected 출력 변화, threshold·approval 판정 변화, 무효화된 baseline mitigation/policy ID와 blocking gap을 machine-readable JSON으로 기록한다.
- CLI는 전체 canonical result, baseline/variant EvidencePacket 단독 export와 compact summary를 지원한다.

### H01 변경 파일

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

### 수정 전 기준선

```text
SCHEMAS: 14 checked
VALID FIXTURES: 3 passed
INVALID FIXTURES: 83 rejected with expected codes
Ran 19 tests in 0.813s
OK
```

### H01 최종 검증

실행 명령:

```bash
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
```

실제 출력 요약:

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

CLI 실제 출력:

```json
{"baseline":{"assurance":"HOLD","ecc_enabled":false,"engineering":"NOT_EVALUATED","policy":"DRAFT","residual":0.063072},"case_id":"mvp-synthetic-ecc-policy-001","change_impact_id":"impact-ec33a03f8d94eca3","variant":{"assurance":"HOLD","ecc_enabled":true,"engineering":"NOT_EVALUATED","policy":"APPROVED","residual":0.013072}}
```

### H01 공격·계약 검증

- 동일 입력 2회 실행의 전체 객체, canonical JSON, input/output hash가 동일하다.
- 생성된 baseline·variant EvidencePacket은 각각 JSON Schema와 semantic gate를 통과한다.
- Change Impact와 전체 MVP 결과는 전용 JSON Schema를 통과한다.
- 범용 `effectiveness_factor` 삽입은 입력 schema가 거부한다.
- ECC distribution 총량이 raw SEU와 다르면 `ECC_FAULT_DISTRIBUTION_MISMATCH`로 종료한다.
- required `SEB` 증거를 제거한 공격은 ECC 결과와 무관하게 `DESTRUCTIVE_SEE_MODE_MISSING`으로 종료한다.
- APPROVED 형식 policy도 `SYNTHETIC`이므로 지원 판정으로 승격되지 않는다.

### 알려진 한계와 검토 요청

- 합성 particle flux·cross section·ECC transition은 회귀 계산 fixture이며 실제 Stage 3·4 근거의 placeholder로 사용하지 않는다.
- MVP v1은 한 임무·한 부품·ECC 한 방법·baseline/variant 한 쌍만 지원한다.
- ECC transition distribution은 Simulation 입력 schema에서 명시적으로 고정하지만 공통 Workstream 10 schema에는 아직 참조 ID만 존재한다.
- 실제 policy 승인 권한, immutable history anchor와 실제 원문 권리는 검증하지 않았다.
- 독립 Assurance 승인 전에는 실제 입력이 들어와도 이 H01 경로가 `SUPPORTED_WITH_MITIGATION`을 만들지 않는다.
- Control Tower는 전체 명령, canonical 재현성, packet/change-impact 독립 검증과 공격 경계를 다시 확인해야 한다.
- `VERIFIED`, `INTEGRATED`, 체크리스트, commit·push는 Control Tower 소유다.

채팅 20은 2026-08-19에 미추적 후보 파일 전부를 직접 읽고 수정 전 검증을 재실행한 뒤 소유권을 인수했다. 초기 구현의 구조를 보존하면서 발견한 계약·False PASS 위험을 수정하고 전체 검증을 완료했다.

2026-08-19 Stage 번호 정렬 요청에 따라 공통 계약을 Stage 1, Simulation Core 합성 Vertical Slice를 Stage 2로 통일했다. 코드 식별자·docstring·오류 메시지·README·결과 schema 설명·인수인계 명칭만 변경했으며 계산과 판정 의미는 변경하지 않았다.

## Stage 번호 정렬 변경 파일

- `src/spectra_sim/contracts.py`
- `src/spectra_sim/engine.py`
- `src/spectra_sim/see.py`
- `src/spectra_sim/units.py`
- `simulation/run_demo.py`
- `simulation/README.md`
- `simulation/schemas/simulation-result.schema.json`
- `tests/simulation/run_all.py`
- `docs/workstreams/20-simulation-core/BRIEF.md`
- `docs/workstreams/20-simulation-core/CURRENT.md`

## 인수 과정과 수정 전 기준선

- Git 기준선: `main...origin/main`, Workstream 20 후보 전체는 미추적, 별도 사용자 변경 `.obsidian/`도 미추적
- 소유 범위 밖 `.obsidian/`, 루트 문서, `schemas/`, `docs/contracts/`, Workstream 10·00 파일은 수정하지 않음
- 후보 파일 전부와 필수 계약 문서를 직접 읽고 완결성·계약 호환성을 검토함
- 수정 전 `python3 tests/schema/validate_contracts.py`: 정상 1개와 실패 27개, exit code 0
- 수정 전 `python3 tests/simulation/run_all.py`: Simulation 13개, 데모 5개 시나리오, exit code 0
- 인수 시 발견 위험: Stage 1 의미 검증 미호출, 입력 배열 index 하드코딩, 음수·비유한 계산값, 중복 입력 종류, 합성 모델 설정 변조 방어 누락

## 구현한 Vertical Slice

- Stage 1 EvidencePacket을 입력으로 받는 결정론적 합성 엔진
- 분리된 TID, SEE, 단위 변환, 정책, 입력 계약 모듈
- 1·2·3·4 mm 합성 차폐 lookup과 기간 변화 TID 비교
- ECC 사용·미사용의 raw/residual SEU 비교
- TID margin, residual SEU 한도, 파괴성 SEE, 정책 승인 rule
- Stage 2 결과 JSON Schema와 결과 EvidencePacket
- 합성 계산이 수치 조건을 만족해도 `HOLD`를 유지하는 보증 gate
- 실행 전·후 Stage 1 JSON Schema와 semantic gate 검증
- 입력 종류의 동적 index trace와 종류별 정확히 1개 제한
- 음수·비유한 값, 잘못된 component 연결과 비지원 완화의 fail-closed 처리
- 합성 모델 분류·계수·이산 lookup 무결성 검증
- 파일을 쓰지 않는 CLI 비교와 전체 단일 검증 명령

## 변경 파일

- `src/spectra_sim/__init__.py`
- `src/spectra_sim/contracts.py`
- `src/spectra_sim/engine.py`
- `src/spectra_sim/policy.py`
- `src/spectra_sim/see.py`
- `src/spectra_sim/tid.py`
- `src/spectra_sim/units.py`
- `simulation/config/synthetic-model.json`
- `simulation/schemas/simulation-result.schema.json`
- `simulation/run_demo.py`
- `simulation/README.md`
- `tests/simulation/test_vertical_slice.py`
- `tests/simulation/run_all.py`
- `docs/workstreams/20-simulation-core/BRIEF.md`
- `docs/workstreams/20-simulation-core/CURRENT.md`

## 계산과 판정 경계

- 합성 TID: 기준 TID × 기간 비율 × 이산 차폐 계수
- 합성 SEE: flux × cross section × 수량 × 기간 × 합성 exposure scale
- 잔여 SEE: raw SEE × ECC 완화 계수
- `engineering_gate`: 합성 조건 비교용 `PASS/FAIL/NOT_EVALUATED`
- `assurance_decision`: 모든 합성 실행에서 `HOLD`
- `OUT_OF_MODEL_SCOPE`: 1~4 mm 이외 차폐나 지원하지 않는 차폐 단위
- `INVALID_INPUT`: EvidencePacket 스키마·의미 오류, 호환되지 않는 단위, 중복 종류, 음수·비유한 입력
- `MODEL_FAILURE`: 합성 모델 설정 또는 생성 EvidencePacket 계약 실패

## 검증 결과

- 실행 명령: `python3 tests/schema/validate_contracts.py` — exit code 0
- 실행 명령: `python3 tests/simulation/run_all.py` — exit code 0
- Stage 1: 스키마 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 검증
- Stage 2: 테스트 19개 통과
- 비교 CLI: 차폐 1·2·4 mm, ECC on/off, 5 mm 범위 밖 시나리오 재현

최종 Stage 1 실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 27 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

최종 Simulation 실제 요약:

```text
Ran 19 tests in 0.766s
OK
```

실제 비교 출력:

```text
scenario                 status               shielded_tid_krad  residual_seu  engineering    assurance
shield-1mm-ecc           VALID                8                  0.0063072      PASS           HOLD
shield-2mm-ecc           VALID                6                  0.0063072      PASS           HOLD
shield-4mm-ecc           VALID                3.5                0.0063072      PASS           HOLD
shield-2mm-no-ecc        VALID                6                  0.063072       PASS           HOLD
out-of-scope-5mm         OUT_OF_MODEL_SCOPE   -                  -              NOT_EVALUATED  HOLD
```

## 검증한 실패·경계

- TID 시험 한계 부족
- SEE 단면적 누락
- 파괴성 SEE 증거 누락
- 사용자 residual SEU 한도 초과
- 미승인 정책
- 5 mm 차폐 외삽 요청
- 호환되지 않는 기간 단위
- 필수 입력·trace가 없는 심각하게 손상된 packet
- 합성 데이터 표시 누락·지원 판정 승격 방지
- 합성 `engineering_gate=PASS` 결과를 `SUPPORTED_WITH_MITIGATION`으로 변조하는 공격
- Stage 1 semantic 오염과 중복 trace ID
- 입력 7종 배열 재정렬과 동적 provenance pointer
- 중복 필수 입력 종류
- 음수 duration·flux와 무한대 정책 한도
- 합성 모델의 `data_class` 변조
- 동일 입력의 byte-equivalent 결과 재현

## 수동 교차검산

fixture의 합성 입력 `TID=10 krad(Si)`, 설계계수 2, 차폐계수 `0.8/0.6/0.45/0.35`를 독립 산술로 계산했다.

```text
manual_tid_1_2_3_4mm=[8.0, 6.0, 4.5, 3.5]
manual_required_tid_factor2=[16.0, 12.0, 9.0, 7.0]
manual_raw_seu=0.063072
manual_residual_ecc_0.1=0.0063072
```

기간 0.5년과 2년은 기준 1년 대비 각각 0.5배와 2배이며, 테스트에서 required TID `6.0/24.0`, raw SEU `0.031536/0.126144`로 교차검산했다.

## 데이터 분류와 출처

- 실제 데이터: 없음
- 합성 데이터: 모델 설정, 입력 fixture, 모든 계산 결과가 `SYNTHETIC`
- `CALCULATED` 실제 근거: 없음
- 합성 계수: 차폐 lookup과 SEE exposure scale은 `simulation/config/synthetic-model.json`에 명시
- 최종 EvidencePacket: `SYNTHETIC_ONLY` 차단 gap과 `HOLD` 유지

## 알려진 한계

- 실제 환경 모델·시험 원문·과학적 정확도를 검증하지 않았다.
- 단일 부품, `cm2/device`, 365일 합성 연도만 지원한다.
- 차폐 lookup은 물리 모델이 아니며 보간·외삽하지 않는다.
- 기본 입력은 Workstream 10의 합성 fixture다. 문서에 언급된 외부 합성 데모는 위치가 없어 이관하지 않았다.
- CLI 비교만 구현했으며 제품 대시보드와 변경 영향 UI는 후속 작업이다.
- 잘못된 입력은 유효 EvidencePacket을 만들 수 없으므로 결과 envelope의 `evidence_packet`을 `null`로 두고 `INVALID_INPUT/HOLD`를 반환한다.
- Stage 1 semantic gate의 기준 구현이 현재 `tests/schema/validate_contracts.py`에 있으므로 분리 패키징 전에 공통 검증 모듈 승격이 필요하다. 현재 저장소에서 파일이 없거나 로드되지 않으면 fail-closed한다.
- 공통 계약 문서는 `docs/contracts/STAGE1_CONTRACT.md`, 본 합성 Vertical Slice는 Stage 2로 정렬했다. 번호 변경은 명칭과 식별자에만 적용했으며 수치 계산·판정 규칙·테스트 의미는 바꾸지 않았다.

## Control Tower 확인 요청

- 독립 환경에서 `python3 tests/simulation/run_all.py`를 재실행해 달라.
- 출력 JSON Schema와 내장 EvidencePacket을 각각 독립 검증해 달라.
- 합성 `engineering_gate=PASS`가 어떤 경로에서도 보증 지원 판정으로 승격되지 않는지 공격 테스트해 달라.
- 차폐·기간·ECC 변화와 고정 입력 재현성을 수동 교차검산해 달라.
- 독립 검증 전 루트 체크리스트를 완료 처리하지 말아 달라.
- `VERIFIED`, `INTEGRATED`, commit·push는 Control Tower 판단으로 남긴다.

## Control Tower 독립 검증 — 2026-08-19

- 판정: `INTEGRATED` — Stage 2의 **합성 기준선 패키지**만 통합했다. 실제 환경·부품 시험 근거 또는 방사선 보증의 통합을 뜻하지 않는다.
- 재실행: `python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개가 기대대로 종료됨.
- 재실행: `python3 tests/simulation/run_all.py` — Stage 2 테스트 19개, 비교 CLI 5개 시나리오가 통과함.
- 수동 공격: `engineering_gate=PASS` 결과를 `SUPPORTED_WITH_MITIGATION`으로 변조했을 때 결과 schema와 Stage 1 semantic gate가 모두 거부했다. 4.1 mm 차폐는 `OUT_OF_MODEL_SCOPE/HOLD`, JSON 직렬화 불가 입력은 `INVALID_INPUT/HOLD`로 종료했다.
- 데이터 분류: 모델 설정·fixture·계산값은 모두 `SYNTHETIC`; 생성 결과의 `assurance_decision`은 모든 경로에서 `HOLD`다. 실제 물리값이나 시험값은 없다.
- 남은 범위: 외부 합성 데모/CSV/대시보드 이관은 원본 위치가 확인되지 않아 수행하지 않았고, 제품 UI도 후속 Stage 범위다.

## Git 통합

- 브랜치: `main`
- 검증된 통합 commit: `35f36a2` — `feat(sim): integrate verified synthetic Stage 2 baseline`
- 원격: `origin` (`https://github.com/WeepingHeron/SPECTRA.git`), push 완료
- 제외: 사용자 소유의 미추적 `.obsidian/`

## 다음 작업이 사용할 계약

- Workstream 30은 `RADIATION_ENVIRONMENT`와 shielding output을 실제 모델 provenance로 교체한다.
- Workstream 40은 `PART_TEST_EVIDENCE`를 정확한 부품·공정·로트와 원문 위치로 교체한다.
- 실제 provenance가 검증되기 전에는 `SUPPORTED_WITH_MITIGATION`을 만들지 않는다.
