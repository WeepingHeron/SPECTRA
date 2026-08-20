# SPECTRA 채팅 20 — MVP Decision Engine Change Request H02

기존 채팅 `20-simulation-core`에서 H02 보완을 계속 진행해 주세요.

## 판정

`CHANGES_REQUESTED — H01`

정상 경로와 명세된 공격은 통과했지만 `NaN`·`Infinity` 입력이 machine-readable 안전 실패가 아닌 일반 `ValueError` traceback으로 종료됩니다. 지원 판정 False PASS는 아니지만 MVP fail-closed 계약을 충족하지 못합니다.

## 재현

`simulation/fixtures/mvp-ecc-policy-v2.json`의 다음 값을 Python이 허용하는 비유한 숫자로 변경하면 재현됩니다.

- `particle_flux.value = NaN`
- `particle_flux.value = Infinity`
- `particle_flux.value = -Infinity`

현재 관찰:

```text
ValueError: SEE inputs must be finite
```

CLI는 `MvpDecisionError`만 처리하므로 구조화된 `INVALID_INPUT / NOT_EVALUATED / HOLD` 대신 traceback과 exit 1을 냅니다.

## 수정 요구

1. `validate_mvp_input()` 또는 동등한 입력 경계에서 모든 계산 대상 숫자가 finite인지 검증합니다.
2. stable code를 사용합니다. 예: `NON_FINITE_NUMERIC_INPUT` 또는 기존 계약과 일치하는 명시적 코드.
3. 하위 TID·SEE 계산이 예상 입력 `ValueError`를 내는 경우 `MvpDecisionError`로 변환합니다.
4. CLI는 세 공격 모두 stderr에 machine-readable JSON을 출력하고 다음을 유지해야 합니다.

```json
{
  "processing_status": "INVALID_INPUT",
  "engineering_gate": "NOT_EVALUATED",
  "assurance_decision": "HOLD"
}
```

5. direct engine과 CLI 회귀 테스트에 `NaN`, `Infinity`, `-Infinity`를 추가합니다.
6. 기존 schema 14개, 정상 3개, 실패 83개, simulation 28개 이상, assurance 전체 회귀와 canonical 결과가 유지돼야 합니다.

## 범위 경계

- Workstream 20 소유 파일만 수정합니다.
- Workstream 30 진행 파일과 Workstream 40 문서는 수정하지 않습니다.
- 실제 환경·시험값을 만들지 않습니다.
- 루트 checklist, commit, push는 수행하지 않습니다.
- `CURRENT.md`를 갱신하고 회차가 붙은 `SPECTRA_20_MVP_DECISION_ENGINE_HANDOFF_H02.md`를 제출합니다.
