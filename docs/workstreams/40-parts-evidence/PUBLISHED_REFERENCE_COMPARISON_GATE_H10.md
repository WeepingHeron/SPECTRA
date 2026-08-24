# H10 Published Reference Comparison Gate

## 결론

`23LC1024` 공개 시험값과 SPECTRA 합성 입력의 숫자 비율은 재현할 수 있지만, 현재 자료로는 승인 대상 `23LC1024-I/SN`을 직접 검증할 수 없다. production adapter는 이 경계를 코드로 고정해 정상 reference도 `VALID / NOT_COMPARABLE / HOLD`로 반환한다.

## 구현 범위

- 입력 계약: `SPECTRA_REFERENCE_COMPARISON_1.0.0`
- 출력 계약: `PUBLISHED_REFERENCE_GATE_RESULT_1.0.0`
- 구현: `src/spectra_parts_adapter/reference_comparison.py`
- 입력 reference: `references/23lc1024-published-comparison.json`
- 직접 테스트: `tests/parts_evidence/test_reference_comparison_gate.py`

게이트는 공개 cross section과 현재 합성 cross section의 단위가 모두 `cm2/device`이고 양의 유한수일 때만 `synthetic / published` 비율을 다시 계산한다. 저장된 비율과 bit-exact하게 다르면 입력 무결성 실패로 `INVALID_INPUT` 처리하고 비율을 숨긴다.

## 비교 차단 조건

현재 reference에서 다음 조건을 선언값이 아니라 입력 내용으로 재계산한다.

- 승인 SOIC exact orderable과 공개 PDIP family-level test article 불일치
- 공개 시험의 exact suffix, lot, die revision 부재
- raw artifact의 승인 manifest binding 부재
- Am-Be 시험과 합성 mission exposure의 particle/environment 불일치
- 합성 part와 승인 part 불일치 및 합성 exposure scale
- destructive SEE coverage 부재

따라서 약 `243.9×`는 `CALCULATED_REFERENCE_ONLY`다. 모델 정확도, 오차율, flight suitability 또는 승인 근거가 아니다.

## Fail-closed 공격 범위

- 저장된 blocker 목록 삭제
- 마지막 부동소수점 자리의 비율 변조
- `COMPARABLE`, `PASS`, `used_for_decision=true` 승격
- direct validation 또는 X-ray/TID direct comparison 승격
- boolean, 0, 음수, NaN, Infinity cross section
- cross-section 단위 변조
- exact orderable mismatch
- artifact hash 훼손과 금지 필드 추가

게이트는 blocker 선언을 신뢰하지 않고 stable code를 정렬해 출력한다. optimistic 또는 구조·무결성 공격은 `INVALID_INPUT / NOT_COMPARABLE / HOLD`, 유효하지만 조건이 맞지 않는 자료는 `VALID / NOT_COMPARABLE / HOLD`다.

## 검증과 남은 한계

- H10 gate 10개와 기존 reference binding 5개, 총 15개 직접 테스트 통과
- 첫 실행에서 reference의 저장 비율이 재계산값과 마지막 부동소수점 자리에서 달라 정상 입력이 거부되는 문제를 발견했다. 저장 파생값을 Python 재계산값 `243.90243902439022`로 바로잡은 뒤 재통과했다.
- 이 기능은 EvidencePacket을 발행하지 않고 part suitability를 결정하지 않는다.
- exact suffix/package/lot/die, 승인 raw manifest와 rights, mission applicability, TID 및 필요한 SEE coverage가 확보되기 전에는 실제 packet 0건과 `HOLD`를 유지한다.
