# 10 Contracts & Schema Handoff

## Status

`INTEGRATED`

## 구현한 계약

- JSON Schema Draft 2020-12 기반 공통 metadata, 단위, 상태 enum
- 7종 핵심 입력의 독립 스키마
- 입력에서 origin·정규화·적용 조건·판정 규칙·보증 판정·증거 공백·검토 상태까지 연결하는 EvidencePacket v1
- JSON Schema와 결정론적 의미 검증을 결합한 fail-closed gate
- 정상 합성 HOLD fixture와 누락·오염·충돌 실패 fixture

## 변경 파일

- `schemas/common.schema.json`
- `schemas/mission.schema.json`
- `schemas/bom.schema.json`
- `schemas/radiation-environment.schema.json`
- `schemas/part-test-evidence.schema.json`
- `schemas/shielding.schema.json`
- `schemas/mitigation.schema.json`
- `schemas/user-policy.schema.json`
- `schemas/evidence-packet.schema.json`
- `docs/contracts/STAGE0_CONTRACT.md`
- `docs/workstreams/10-contracts-schema/BRIEF.md`
- `docs/workstreams/10-contracts-schema/CURRENT.md`
- `tests/schema/validate_contracts.py`
- `tests/schema/requirements.txt`
- `tests/schema/fixtures/valid/synthetic-hold.json`
- `tests/schema/fixtures/invalid/cases.json`

## 상태 체계

- 작업 검토 상태: `NOT_STARTED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `VERIFIED`, `INTEGRATED`, `CHANGES_REQUESTED`, `HOLD`
- 방사선 보증 판정: `SUPPORTED_WITH_MITIGATION`, `CONDITIONAL`, `HOLD`, `INSUFFICIENT_EVIDENCE`
- 처리·범위 상태: `VALID`, `INVALID_INPUT`, `OUT_OF_MODEL_SCOPE`, `MODEL_FAILURE`, `STALE_EVIDENCE`, `PROVENANCE_FAILURE`, `CONFLICTING_EVIDENCE`

## 검증 결과

- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 정상 fixture: 1개 통과 (`SYNTHETIC`, 보증 판정 `HOLD`)
- 실패 fixture: 기존 23개와 4차 적용성·중복 ID 공격 fixture 4개, 총 27개가 각 기대 오류 코드로 거부
- 결과: 스키마 9개가 Draft 2020-12 meta-schema 검사를 통과했고 전체 검증 명령이 exit code 0으로 종료

실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 27 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- 전체 fixture: 28개(정상 1개, 실패 27개)
- 실제 exit code: `0`

## Control Tower 독립 검증

- 검증일: 2026-08-19
- 제공 명령 재실행: `python3 tests/schema/validate_contracts.py` 성공
- 재현 환경: Python 3.12.2, `jsonschema 4.21.1`
- 판정: `CHANGES_REQUESTED`

다음 False PASS가 스키마 오류와 의미 오류 없이 허용됐다.

1. `SUPPORTED_WITH_MITIGATION`이면서 `decision.rule_results[].outcome`이 `FAIL`인 패킷
2. `SUPPORTED_WITH_MITIGATION`이면서 `used_for_decision: true`인 trace가 하나도 없는 패킷

두 공격 사례 모두 `schema_errors=[]`, `semantic_codes=[]`로 종료됐다. 낙관 판정에는 최소 한 개 이상의 실제 결정 trace가 필요하고, 연결된 필수 규칙에 `FAIL` 또는 `NOT_EVALUATED`가 있으면 지원 판정을 차단해야 한다. 두 사례를 실패 fixture에 추가하고 기대 오류 코드를 검증한 뒤 다시 `READY_FOR_REVIEW`를 요청해야 한다.

## 수정 요청 반영

- 추가 오류 코드 `NON_PASS_RULE_WITH_SUPPORT`: `SUPPORTED_WITH_MITIGATION`에서 `FAIL` 또는 `NOT_EVALUATED` rule result가 하나라도 있으면 거부
- 추가 오류 코드 `SUPPORT_WITHOUT_DECISION_TRACE`: `SUPPORTED_WITH_MITIGATION`에서 `used_for_decision: true` trace가 하나도 없으면 거부
- 추가 공격 fixture `support-with-failed-rule`: 지원 판정과 `FAIL` 규칙 조합을 `NON_PASS_RULE_WITH_SUPPORT`로 거부
- 추가 공격 fixture `support-without-decision-trace`: 모든 trace가 결정 미사용인 지원 판정을 `SUPPORT_WITHOUT_DECISION_TRACE`로 거부
- 두 fixture는 기존 지정 오류 코드를 계속 반환한다. 3차 provenance gate 이후 합성 원본을 사용하는 지원 공격에는 `NON_EVIDENTIARY_SOURCE_INPUT`이 함께 반환될 수 있다.

## Control Tower 재검증

- 검증일: 2026-08-19
- 제공 명령 재실행: 스키마 9개, 정상 fixture 1개, 실패 fixture 14개 검증 성공
- 이전 False PASS 재검증: `NON_PASS_RULE_WITH_SUPPORT`, `SUPPORT_WITHOUT_DECISION_TRACE`로 정상 차단
- 판정: `CHANGES_REQUESTED`

다음 trace–rule 무결성 위반이 스키마 오류와 의미 오류 없이 허용됐다.

1. `SUPPORTED_WITH_MITIGATION`의 `PASS` rule result가 빈 `trace_ids` 배열을 가진 경우
2. rule result의 `rule_id`가 해당 `trace_ids`로 참조한 trace의 `decision_rule_ids`와 일치하지 않는 경우

두 공격 사례 모두 `schema_errors=[]`, `semantic_codes=[]`로 종료됐다. `trace_ids`에는 최소 한 개를 요구하고, 각 rule result의 모든 trace 참조가 동일한 `rule_id`를 선언하는 실제 trace로 연결되는지 검증해야 한다. 지원 판정에서는 그 연결된 trace 중 최소 하나가 `used_for_decision: true`여야 한다. 공격 fixture와 구체적인 기대 오류 코드를 추가한 뒤 다시 `READY_FOR_REVIEW`를 요청해야 한다.

## 2차 수정 요청 반영

- 추가 오류 코드 `RULE_WITHOUT_TRACE`: rule result의 `trace_ids`가 비어 있으면 거부
- 추가 오류 코드 `RULE_TRACE_MISMATCH`: rule result가 직접 참조한 trace의 `decision_rule_ids`에 동일한 rule ID가 없으면 거부
- 추가 오류 코드 `SUPPORT_RULE_WITHOUT_DECISION_TRACE`: 지원 판정의 rule result가 직접 참조한 trace 중 `used_for_decision: true`가 하나도 없으면 거부
- 기존 오류 코드 `BROKEN_DECISION_TRACE`: rule result가 존재하지 않는 trace ID를 참조하면 거부
- `support-pass-rule-without-trace`: 빈 `trace_ids`를 JSON Schema `minItems: 1`과 `RULE_WITHOUT_TRACE`로 거부
- `rule-trace-mismatch-with-rule-elsewhere`: 다른 무관한 trace에 rule ID가 있어도 직접 참조가 불일치하면 `RULE_TRACE_MISMATCH`로 거부
- `support-rule-only-linked-to-nondecision-trace`: 무관한 decision trace가 별도로 존재해도 `SUPPORT_RULE_WITHOUT_DECISION_TRACE`로 거부
- `rule-references-missing-trace`: 존재하지 않는 trace 참조를 `BROKEN_DECISION_TRACE`로 거부
- 이전 공격 fixture `support-with-failed-rule`, `support-without-decision-trace`도 기존 기대 코드로 계속 거부됨

2차 수정 후 실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 18 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 전체 fixture: 19개(정상 1개, 실패 18개)
- 실제 exit code: `0`

## Control Tower 3차 검증

- 검증일: 2026-08-19
- 제공 명령 재실행: 스키마 9개, 정상 fixture 1개, 실패 fixture 18개 검증 성공
- 이전 trace–rule 공격 재검증: 빈 `trace_ids`와 rule–trace 불일치는 정상 차단
- 판정: `CHANGES_REQUESTED`

합성 원본을 계산값으로 재표시하는 provenance 우회가 지원 판정을 통과했다.

1. 패킷의 실제 입력과 `trace.input_pointer` 대상은 `SYNTHETIC`
2. `trace.normalized_value.metadata.data_class`만 `CALCULATED`로 변경
3. 규칙 결과를 `PASS`, evidence gap을 빈 배열, 보증 판정을 `SUPPORTED_WITH_MITIGATION`으로 설정

이 공격은 `schema_errors=[]`, `semantic_codes=[]`로 종료됐다. 최종 판정 trace의 `input_pointer`와 `origin_pointer`를 실제로 해석해 원본 데이터 분류를 확인하고, `SYNTHETIC` 또는 `ASSUMED` 원본에서 파생된 계산값을 실제 보증 근거로 승격하지 못하게 해야 한다. 공격 fixture와 명확한 기대 오류 코드를 추가한 뒤 다시 `READY_FOR_REVIEW`를 요청해야 한다.

## 3차 수정 요청 반영

- 추가 오류 코드 `NON_EVIDENTIARY_SOURCE_INPUT`: decision trace의 원본 입력 metadata가 `SYNTHETIC` 또는 `ASSUMED`이면 정규화 결과가 `CALCULATED`여도 지원 판정을 거부
- 추가 오류 코드 `UNRELATED_TRACE_ORIGIN`: `origin_pointer`가 입력 대상 또는 그 조상 입력 레코드의 동일 provenance 객체를 직접 가리키지 않으면 거부
- 기존 오류 코드 `BROKEN_TRACE_POINTER`: `input_pointer` 또는 `origin_pointer`가 실제 패킷에서 해석되지 않으면 거부
- `support-reclassified-synthetic-source`: 합성 원본을 계산값으로 재표시한 지원 판정을 `NON_EVIDENTIARY_SOURCE_INPUT`으로 거부
- `support-reclassified-assumed-source`: 가정 원본을 계산값으로 재표시한 지원 판정을 `NON_EVIDENTIARY_SOURCE_INPUT`으로 거부
- `trace-uses-unrelated-sibling-origin`: 동일 계산 실행 내용을 가진 형제 필드 provenance도 허용된 조상 경로가 아니면 `UNRELATED_TRACE_ORIGIN`으로 거부
- `broken-trace-input-pointer`, `broken-trace-origin-pointer`: 깨진 포인터를 각각 `BROKEN_TRACE_POINTER`로 거부
- 각 신규 fixture는 `schema_errors=[]`이며 지정된 semantic 오류 코드 하나만 반환하는 것을 별도로 확인함

3차 수정 후 실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 23 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 전체 fixture: 24개(정상 1개, 실패 23개)
- 실제 exit code: `0`

## Control Tower 4차 검증

- 검증일: 2026-08-19
- 제공 명령 재실행: 스키마 9개, 정상 fixture 1개, 실패 fixture 23개 검증 성공
- 이전 provenance 공격 재검증: `NON_EVIDENTIARY_SOURCE_INPUT`으로 정상 차단
- 판정: `CHANGES_REQUESTED`

다음 EvidencePacket 무결성 위반이 모두 `schema_errors=[]`, `semantic_codes=[]`로 지원 판정을 통과했다.

1. `used_for_decision: true` trace의 `applicability.status`가 `NOT_APPLICABLE`
2. `used_for_decision: true` trace의 `applicability.status`가 `UNRESOLVED`
3. 동일한 `trace_id`가 두 번 존재
4. 동일한 `decision.rule_results[].rule_id`가 두 번 존재

`SUPPORTED_WITH_MITIGATION`에서는 결정에 사용되거나 지원 규칙에 연결된 모든 trace가 `APPLICABLE`이어야 한다. `trace_id`와 rule result의 `rule_id`도 패킷 안에서 유일해야 한다. 네 공격 fixture와 구체적인 기대 오류 코드를 추가한 뒤 다시 `READY_FOR_REVIEW`를 요청해야 한다.

## 4차 수정 요청 반영

- 추가 오류 코드 `DECISION_TRACE_NOT_APPLICABLE`: 지원 판정의 decision trace 또는 지원 규칙이 참조한 trace가 `APPLICABLE`이 아니면 거부
- 추가 오류 코드 `DUPLICATE_TRACE_ID`: 판정 종류와 무관하게 패킷 내 중복 `trace_id`를 거부
- 추가 오류 코드 `DUPLICATE_RULE_ID`: 판정 종류와 무관하게 중복 rule result ID를 거부
- `support-with-not-applicable-decision-trace`: `NOT_APPLICABLE` 결정 trace를 `DECISION_TRACE_NOT_APPLICABLE`로 거부
- `support-with-unresolved-decision-trace`: `UNRESOLVED` 결정 trace를 `DECISION_TRACE_NOT_APPLICABLE`로 거부
- `duplicate-trace-id`: 서로 다른 배열 항목의 동일 `trace_id`를 `DUPLICATE_TRACE_ID`로 거부
- `duplicate-rule-id`: 동일한 `decision.rule_results[].rule_id` 반복을 `DUPLICATE_RULE_ID`로 거부
- 각 신규 fixture는 `schema_errors=[]`이며 지정된 semantic 오류 코드 하나만 반환하는 것을 별도로 확인함

4차 수정 후 실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 27 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 전체 fixture: 28개(정상 1개, 실패 27개)
- 실제 exit code: `0`

## 데이터 분류와 출처

- 실제 데이터: 이번 세션에서 추가하지 않음
- 합성 데이터: 모든 샘플 수치는 `SYNTHETIC`, fixture 계산 실행 ID와 해시를 포함
- 가정: 실제 보증 계산에 사용할 가정값 없음; 계약상 `ASSUMED`는 명시적 assumptions와 source가 필수
- 출처 없는 값: `PUBLISHED` 또는 `CUSTOMER_VERIFIED`로 허용하지 않음

## 알려진 한계

- 실제 환경 모델 출력과 실제 시험 보고서에 대한 과학적·원문 검증은 수행하지 않았다.
- Stage 0 의미 검증은 TID 범위를 같은 단위끼리 비교한다. 실제 단위 정규화 엔진은 Workstream 20/30에서 구현해야 한다.
- `year` 환산 정의, 차폐 질량두께 변환, device/bit 단면적 변환은 모델별 추가 입력 없이는 자동 수행하지 않는다.
- 현재 검증 명령은 Python 3.12.2, `jsonschema 4.21.1`, `referencing 0.34.0`에서 실행했다.
- 빈 `trace_ids`는 JSON Schema와 의미 gate 양쪽에서 차단한다. trace 존재 여부, 직접 rule ID 연결, rule별 decision trace 연결은 `validate_contracts.py`의 결정론적 의미 gate에서 강제되므로 소비자는 JSON Schema 검사만 실행하지 말고 제공된 전체 검증 경로를 사용해야 한다.
- provenance 연결은 JSON Pointer 경로와 metadata 객체의 구조적 동일성을 검증한다. 계산 실행의 과학적 타당성이나 원문 진위는 이후 Workstream의 독립 검증 대상이다.
- `trace_id`·`rule_id` 유일성과 지원 trace 적용성은 JSON Schema 단독 검사가 아니라 결정론적 의미 gate에서 강제된다.

## Control Tower 확인 요청

- 4차 공격 fixture 4개와 기존 실패 fixture 23개를 포함해 독립 환경에서 단일 명령과 기대 실패 코드를 재실행해 달라.
- 루트 `docs/workstreams/README.md` 상태표에 `CHANGES_REQUESTED`가 빠져 있으나 Control Tower BRIEF에는 존재한다. 루트 소유 문서의 일관성 수정 여부를 결정해 달라.
- 루트 체크리스트는 본 세션에서 완료 표시하지 않았다. 독립 검증 뒤 해당 항목만 갱신해 달라.
- `VERIFIED`, `INTEGRATED`, Git commit·push는 Control Tower 판단으로 남긴다.

## Control Tower 최종 재검증

- 검증일: 2026-08-19
- 제공 명령 재실행: `python3 tests/schema/validate_contracts.py`
- 제공 검증 결과: 스키마 9개, 상태 enum 축 4개, 정상 fixture 1개 통과, 실패 fixture 27개가 기대 코드로 거부, exit code 0
- 독립 혼합 공격: 적용 불가·미해결 trace, 중복 trace/rule ID, 혼합 적용성, 합성 원본 재분류, 무관한 decision trace 우회를 포함한 7개 공격이 모두 의도한 fail-closed 코드로 거부됨
- 데이터 확인: 실제·고객 데이터 없음. 정상 fixture와 모든 샘플 값은 `SYNTHETIC`이며 실제 방사선 보증 근거로 승격되지 않음
- 판정: `INTEGRATED`
- 통합 범위: Stage 0 EvidencePacket·입력·판정 계약, 검증 스크립트와 최소 False PASS 세트
- Git 기준선: `303adb9` (`feat(contracts): establish verified Stage 0 baseline`), 비공개 `origin/main` push 완료
- 잔여 범위: 과학 모델 타당성, 실제 시험 원문, 단위 변환 엔진과 합성 Vertical Slice는 후속 Workstream에서 별도 검증

## Workstream 20의 첫 채팅 세션이 사용할 계약

- 입력 payload는 7개 독립 스키마 중 하나를 따라야 한다.
- 계산 결과는 `CALCULATED`와 재현 가능한 `calculation_run`을 사용하고, 데모값은 `SYNTHETIC`을 유지한다.
- 처리 실패·범위 밖·stale 상태는 `SUPPORTED_WITH_MITIGATION`으로 변환하지 않는다.
- 결정론적 판정 결과와 trace를 먼저 만들고 LLM 설명은 그 결과를 변경하지 않는다.
