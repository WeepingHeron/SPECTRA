# SPECTRA 채팅 20 H02 Handoff — MVP Decision Engine 비유한 숫자 보완

## 작업 식별

- 세션: `20-simulation-core`
- 작업 패키지: `20-mvp-decision-engine-v1`
- 회차: `H02`
- 상태: `READY_FOR_REVIEW`
- 기준 판정: `CHANGES_REQUESTED — H01`

## 결과

H01에서 확인된 `NaN`·`Infinity` traceback 결함을 보완했다. 정규화 입력의 모든 float 숫자를 schema 검증 전에 순회하며 비유한 값을 stable code `NON_FINITE_NUMERIC_INPUT`으로 거부한다. 하위 TID·SEE 계산이 예상 입력 `ValueError`를 내더라도 `MvpDecisionError`로 변환되므로 CLI가 일반 traceback으로 이탈하지 않는다.

세 공격 모두 다음 안전 상태를 유지한다.

```json
{
  "processing_status": "INVALID_INPUT",
  "engineering_gate": "NOT_EVALUATED",
  "assurance_decision": "HOLD",
  "error_code": "NON_FINITE_NUMERIC_INPUT"
}
```

## 구현 변경

- `validate_mvp_input()` 앞단에 결정론적 비유한 숫자 탐지기를 추가했다.
- 오류 메시지는 오염 위치를 JSON pointer로 제공한다: `/particle_flux/value`.
- TID 계산과 TID 시험 한계 변환의 `ValueError`는 `TID_CALCULATION_INPUT_INVALID`로 변환한다.
- SEE 계산의 `ValueError`는 `SEE_CALCULATION_INPUT_INVALID`로 변환한다.
- CLI 오류 응답에 machine-readable `error_code`를 추가했다.
- direct engine과 CLI에 `NaN`, `Infinity`, `-Infinity` 회귀를 추가했다.
- 하위 TID·SEE `ValueError` 변환 회귀를 추가했다.

## 변경 파일

- `src/spectra_sim/mvp_engine.py`
- `simulation/run_mvp_decision.py`
- `tests/simulation/test_mvp_decision_engine.py`
- `docs/workstreams/20-simulation-core/CURRENT.md`

Workstream 30 진행 파일, Workstream 40 문서, 루트 checklist, 공통 schema·계약은 수정하지 않았다. commit·push도 수행하지 않았다.

## 공격 실제 출력

세 입력 모두 exit code `2`, stdout 없음, traceback 없음으로 종료했다.

```text
NaN 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
Infinity 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
-Infinity 2 {"assurance_decision": "HOLD", "engineering_gate": "NOT_EVALUATED", "error": "numeric input at /particle_flux/value must be finite", "error_code": "NON_FINITE_NUMERIC_INPUT", "processing_status": "INVALID_INPUT"}
```

## 최종 검증

실행 명령:

```bash
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
python3 tests/assurance/run_all.py
python3 simulation/run_mvp_decision.py --summary
```

실제 결과:

```text
SCHEMAS: 14 checked
ENUM CONTRACTS: 4 axes checked
INPUT CARDINALITY: 7 required kinds exact-one
VERSION CONTRACTS: EvidencePacket 1.0.0/1.1.0 and v2 contracts checked
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

## 검토 요청과 한계

- 합성 입력, 미승인 정책과 파괴성 SEE 공백은 계속 지원 판정으로 승격되지 않는다.
- 실제 Stage 3 환경 또는 Stage 4 시험값을 추가하거나 만들어 내지 않았다.
- H02는 입력 안전 실패와 오류 표현만 보완했으며 수치 계산·판정 규칙·정상 canonical 결과를 바꾸지 않았다.
- Control Tower는 세 비유한 숫자 공격, 전체 회귀와 정상 canonical summary를 독립 재실행해 확인해 달라.
- 이 handoff는 `READY_FOR_REVIEW` 선언이다. `VERIFIED`, `INTEGRATED`, checklist 변경과 commit·push는 Control Tower가 담당한다.
