# 10 Contracts & Schema Handoff

## Status

`VERIFIED`

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
- `docs/contracts/STAGE1_CONTRACT.md`
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
- Stage 1 의미 검증은 TID 범위를 같은 단위끼리 비교한다. 실제 단위 정규화 엔진은 Workstream 20/30에서 구현해야 한다.
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
- 통합 범위: Stage 1 EvidencePacket·입력·판정 계약, 검증 스크립트와 최소 False PASS 세트
- Git 기준선: `303adb9` (`feat(contracts): establish verified Stage 0 baseline`), 비공개 `origin/main` push 완료. 커밋 메시지는 번호 정렬 이전의 역사적 명칭이다.
- 잔여 범위: 과학 모델 타당성, 실제 시험 원문, 단위 변환 엔진과 합성 Vertical Slice는 후속 Workstream에서 별도 검증

## Workstream 20의 첫 채팅 세션이 사용할 계약

- 입력 payload는 7개 독립 스키마 중 하나를 따라야 한다.
- 계산 결과는 `CALCULATED`와 재현 가능한 `calculation_run`을 사용하고, 데모값은 `SYNTHETIC`을 유지한다.
- 처리 실패·범위 밖·stale 상태는 `SUPPORTED_WITH_MITIGATION`으로 변환하지 않는다.
- 결정론적 판정 결과와 trace를 먼저 만들고 LLM 설명은 그 결과를 변경하지 않는다.

## 2026-08-20 계약 보완 패키지

패키지 ID: `10-tid-environment-provenance-contract-v1`

이 섹션의 `READY_FOR_REVIEW`는 기존 통합 baseline 이후 추가된 환경 provenance 계약 보완분에만 적용한다. 이전 Control Tower의 `INTEGRATED` 기록을 소급 변경하지 않으며, 이번 변경도 독립 재검증 전에는 `VERIFIED` 또는 `INTEGRATED`로 주장하지 않는다.

### 구현 계약과 호환성

- `RADIATION_ENVIRONMENT` v1.1에 `TID_ONLY` variant를 추가했다. `mission_dose`, `dose_scope`, silicon target, source completeness, shielding point, validity, model chain, raw manifest를 요구하며 `particle_flux`와 legacy `tid`를 금지한다.
- 기존 `environment_variant` 없는 `tid` + `particle_flux` payload는 그대로 허용한다. 기존 `synthetic-hold.json`을 수정하지 않고 정상 fixture로 재검증해 하위 호환성을 입증했다.
- trapped-only·solar 누락·partial 결과는 명시적으로 분류할 수 있으나 `dose_scope: MISSION`과 결합하면 `INCOMPLETE_MISSION_TID_SOURCE`로 차단한다.
- `model_chain`은 stage ID와 dependency로 ORBIT → trapped/solar → transport/dose 관계를 검증한다. exact model version/build와 configuration reference 또는 hash가 필요하다.
- raw manifest는 환경·calculation run의 `run_id`, bundle/parser/normalized output hash, artifact identity/hash, provider/parser 버전과 네 권리 축을 연결한다. 미확인·금지 권리를 사용 가능으로 주장하지 못한다.
- `HOLD`는 assurance decision에만 남겨 두었고 processing status enum은 변경하지 않았다.

### 변경 파일

- `schemas/radiation-environment.schema.json`
- `schemas/external-model-run.schema.json`
- `schemas/raw-artifact-manifest.schema.json`
- `tests/schema/validate_contracts.py`
- `tests/schema/fixtures/valid/synthetic-tid-only-hold.json`
- `tests/schema/fixtures/invalid/environment-provenance-cases.json`
- `docs/contracts/STAGE1_CONTRACT.md`
- `docs/workstreams/10-contracts-schema/BRIEF.md`
- `docs/workstreams/10-contracts-schema/CURRENT.md`

### 신규 오류 코드와 공격 fixture

- TID variant: `TID_ONLY_PLACEHOLDER_FLUX`, `INCOMPLETE_MISSION_TID_SOURCE`, `INCOMPLETE_ENVIRONMENT_WITH_SUPPORT`
- chain: `MODEL_CHAIN_MISSING`, `MODEL_STAGE_VERSION_MISSING`, `MODEL_STAGE_CONFIG_MISSING`, `DUPLICATE_MODEL_STAGE_ID`, `BROKEN_MODEL_STAGE_LINK`, `MODEL_CHAIN_OUT_OF_APPROVED_SCOPE`
- manifest: `RAW_ARTIFACT_MANIFEST_MISSING`, `ARTIFACT_HASH_MISSING`, `ARTIFACT_HASH_INVALID`, `DUPLICATE_ARTIFACT_ID`
- run/parser 연결: `ENVIRONMENT_MANIFEST_RUN_MISMATCH`, `ENVIRONMENT_CALCULATION_RUN_MISMATCH`, `PARSER_BUNDLE_HASH_MISMATCH`, `PARSER_OUTPUT_HASH_MISMATCH`
- 권리·승격: `UNCONFIRMED_RIGHTS_CLAIM`, `CALCULATED_ENVIRONMENT_PROVENANCE_MISSING`, `SUPPORT_WITHOUT_ENVIRONMENT_PROVENANCE`
- 신규 실패 fixture 20개는 placeholder flux, 불완전 mission source와 trapped-only 지원 승격, model version/config 누락, 중복·깨진 stage, artifact hash 누락·오류·중복, run/parser hash 불일치, 미확인 권리의 자동화·재배포 주장, provenance 없는 계산·지원 승격, 승인 범위와 역할 dependency 위반을 각각 검증한다.

### 검증 결과

- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 스키마: 11개 Draft 2020-12 meta-schema 검사 대상
- 정상 fixture: 2개. 기존 flux 기반 1개와 dummy flux 없는 `TID_ONLY` 1개
- 실패 fixture: 기존 27개를 보존하고 신규 20개를 추가해 총 47개
- 전체 fixture: 49개
- 실제 출력:

```text
SCHEMAS: 11 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 2 passed
INVALID FIXTURES: 47 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- 실제 exit code: `0`

### 데이터와 권리 경계

- 실제 환경 수치·실제 SPENVIS/OLTARIS 실행·실제 원문 파일은 추가하지 않았다.
- 신규 fixture의 수치, platform, provider job reference, parser commit, 파일 위치와 SHA-256은 전부 형식 검증용 `SYNTHETIC` 값이다.
- 권리 상태는 네 축 모두 `UNCONFIRMED`, 사용 주장은 모두 false인 정상 fixture를 사용한다. 이는 실제 이용 허가가 아니다.

### 알려진 한계와 다른 Workstream 영향

- 계약 검증은 chain·hash·identifier·rights claim의 구조 및 연결 무결성을 확인할 뿐 모델의 과학적 타당성, 원본 진위, 실제 권리 승인을 확인하지 않는다.
- checksum은 manifest에 선언된 문자열의 형식과 교차 필드 일치만 검증한다. 실제 외부 파일 byte stream 재해시는 Workstream 30/60의 실행 검증이 필요하다.
- Workstream 30은 실제 adapter를 구현할 때 `run_id`, four-role chain, raw manifest와 parser hash를 이 계약에 맞춰 제공해야 한다. 해당 Workstream 문서는 이번 작업에서 수정하지 않았다.
- Workstream 20은 기존 flux payload를 계속 사용할 수 있다. `TID_ONLY`를 소비할 때는 `mission_dose`를 읽고 provenance gate를 우회하지 않아야 한다.

### Control Tower 확인 요청

- 기존 27개 공격과 신규 20개 공격을 독립 환경에서 재실행하고 기대 오류 코드가 안정적으로 반환되는지 확인해 달라.
- 기존 flux payload와 새 TID-only payload의 동시 하위 호환성을 확인해 달라.
- 실제 외부 실행이나 권리 승인으로 오인될 값이 없는지 확인해 달라.
- 이번 패키지의 `VERIFIED`, `INTEGRATED`, checklist 반영과 Git commit·push는 Control Tower 판단으로 남긴다.

## Control Tower 독립 검증 — 2026-08-20

- 판정: `CHANGES_REQUESTED`
- 검토 범위: 기존 Stage 1 통합 기준선 이후 추가된 `10-tid-environment-provenance-contract-v1`만 검토했다. 기존 Stage 1 계약의 `INTEGRATED` 판정은 유지한다.
- 제공 명령 재실행: schema 11개, 상태 enum 축 4개, 정상 fixture 2개, 실패 fixture 47개가 기대 코드로 종료했고 exit code 0을 확인했다.
- 회귀 재실행: `tests/simulation/run_all.py`의 simulation test 19개가 모두 통과했다.
- 형식 검사: `git diff --check` 통과. 실제 외부 실행·원문·실제 환경 수치는 없고 신규 값은 `SYNTHETIC`이다.

### 독립 변형 공격 결과

다음 입력은 모두 JSON Schema 오류 없이 허용됐다.

1. 환경과 decision trace만 `CALCULATED`로 재분류하고 raw manifest는 `SYNTHETIC`, 네 권리 축은 `UNCONFIRMED`, `usage_claims`는 모두 false로 유지한 채 `SUPPORTED_WITH_MITIGATION`으로 변경한 패킷이 `semantic_codes=[]`로 통과했다.
2. `mission_dose=-1`인 TID-only 환경이 `schema_errors=[]`, `semantic_codes=[]`로 통과했다.
3. `valid_for.start_at > end_at`과 manifest의 `submitted_at > completed_at > downloaded_at`이 모두 오류 없이 통과했다.
4. top-level `model_name/model_version`을 model chain과 모순되게 바꿔도 오류 없이 통과했다.
5. `mission_dose.metadata.calculation_run.run_id`를 환경·manifest run과 다르게 바꾸고 trace origin을 해당 dose run으로 맞추면 오류 없이 통과했다.
6. mission dose의 calculation `output_hash`를 dose `content_hash`·parser output과 다르게 바꾸고 trace를 함께 맞춰도 오류 없이 통과했다.
7. manifest 자체 metadata의 calculation run ID가 환경 run과 달라도 오류 없이 통과했다.
8. manifest artifact를 `NORMALIZED_OUTPUT` 하나만 남겨 실제 `PROVIDER_OUTPUT` 원본이 전혀 없어도 provenance가 유효한 것으로 처리됐다.

### 수정 요구

- optimistic assurance에서는 environment, mission dose, manifest와 decision trace의 데이터 분류가 모두 증거 사용 가능 상태인지 검증하고, `SYNTHETIC`·`ASSUMED` manifest 또는 필요한 권리 축 `UNCONFIRMED/PROHIBITED`를 `HOLD`로 차단한다.
- `usage_claims=false`로 권리 gate를 우회하지 못하게 실제 수행 단계와 decision 사용이 요구하는 권리 축을 결정론적으로 도출한다.
- TID와 차폐값의 물리적 범위, validity와 실행 timestamp의 순서를 검증한다.
- TID-only에서 legacy `model_name/model_version`을 금지하거나 model chain의 대표 모델과 일치시키며 dual truth를 차단한다.
- environment `run_id`, top-level calculation run, mission dose calculation run, manifest run/metadata run과 parser input/output hash의 전체 연결을 검증한다.
- raw manifest에는 현재 경로가 요구하는 실제 provider raw artifact 역할과 0보다 큰 byte size를 최소 한 개 요구한다. normalized output만으로 provenance를 충족하지 못하게 한다.
- 위 공격을 각각 신규 실패 fixture와 고유한 기대 오류 코드로 추가한다.

### 재제출

- 기존 정상 2개와 실패 47개를 보존하고 위 공격 fixture를 추가한 뒤 단일 명령을 재실행한다.
- 다음 handoff는 기존 번호 없는 제출을 암묵적 `H01`로 보고 `/Users/taehoon/Downloads/SPECTRA_10_TID_ENVIRONMENT_PROVENANCE_HANDOFF_H02.md`로 작성한다.
- 다시 `READY_FOR_REVIEW`까지만 요청하며 다른 Workstream 파일, commit·push는 건드리지 않는다.

## H02 수정 반영 — 2026-08-20

대상 패키지는 계속 `10-tid-environment-provenance-contract-v1`이며 H02는 handoff 제출 회차다. 기존 Stage 1 기준선의 `INTEGRATED` 판정은 유지하고 이번 보완분만 `READY_FOR_REVIEW`로 재제출한다.

### 추가한 fail-closed gate

- optimistic assurance에서 environment, mission dose, raw manifest, decision trace의 provenance class를 각각 검사한다. `SYNTHETIC`·`ASSUMED`는 위치별 전용 코드로 지원 판정을 차단한다.
- `execution_mode`, `distribution_scope`, optimistic decision에서 research·automation·commercial·redistribution 필수 권리를 결정론적으로 도출한다. `usage_claims: false`는 권리 gate를 우회하지 못한다.
- TID는 0 이상, 차폐 두께는 0보다 크게 제한한다. mission validity와 provider timestamp는 각각 단조 증가 순서를 검사한다.
- `representative_stage_id`를 추가하고 top-level model name/version이 대표 stage와 일치하도록 했다.
- environment, environment metadata calculation, mission dose calculation, manifest와 manifest metadata calculation의 run identity를 하나로 연결했다.
- parser output, mission dose content hash, mission dose calculation output hash를 함께 비교한다. trace origin 변경과 독립적으로 검사한다.
- manifest에 양수 byte size·유효 hash·source location을 가진 `PROVIDER_OUTPUT`을 최소 하나 요구한다. normalized output만 있는 manifest는 provenance failure다.

안전한 소비자 종료 상태는 provenance·권리·raw artifact 실패 시 `processing_status: PROVENANCE_FAILURE`, `assurance_decision: HOLD`다. 검증기는 공격 packet의 optimistic decision을 자동 수정하지 않고 전용 오류 코드로 거부한다.

### H02 신규 오류 코드

- provenance class: `NON_EVIDENTIARY_ENVIRONMENT_WITH_SUPPORT`, `NON_EVIDENTIARY_DOSE_WITH_SUPPORT`, `NON_EVIDENTIARY_MANIFEST_WITH_SUPPORT`; decision trace는 기존 `NON_EVIDENTIARY_DECISION_INPUT`을 유지
- derived rights: `REQUIRED_RIGHT_NOT_ALLOWED`
- 물리·시간: `NEGATIVE_TID`, `NON_POSITIVE_SHIELDING_THICKNESS`, `INVALID_VALIDITY_INTERVAL`, `INVALID_PROVIDER_TIMESTAMP_ORDER`
- model truth: `REPRESENTATIVE_MODEL_STAGE_MISSING`, `TOP_LEVEL_MODEL_STAGE_MISMATCH`
- run/hash truth: `TID_RUN_PROVENANCE_MISSING`, `MISSION_DOSE_RUN_MISMATCH`, `MANIFEST_METADATA_RUN_MISMATCH`, `MISSION_DOSE_OUTPUT_HASH_MISMATCH`
- raw artifact: `PROVIDER_OUTPUT_ARTIFACT_MISSING`, `PROVIDER_OUTPUT_ARTIFACT_INVALID`

### H02 fixture와 검증 결과

- H02 공격 fixture: `tests/schema/fixtures/invalid/environment-provenance-h02-cases.json` 18개
- 기존 정상 fixture: 2개 유지
- 기존 실패 fixture: 47개가 기존 기대 코드를 유지
- 전체 실패 fixture: 65개
- 전체 schema fixture: 67개
- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 실제 출력:

```text
SCHEMAS: 11 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 2 passed
INVALID FIXTURES: 65 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- schema gate exit code: `0`
- simulation 회귀: `python3 tests/simulation/run_all.py`, 19개 통과, exit code `0`
- 형식 검사: `git diff --check -- schemas docs/contracts docs/workstreams/10-contracts-schema tests/schema`, exit code `0`

### H02 알려진 한계와 영향

- 실제 provider raw file byte stream의 hash 재계산, 모델 과학 검증, 실제 권리 승인은 수행하지 않는다.
- 현재 공통 policy는 `PROVIDER_OUTPUT`만 필수다. provider input·configuration·run log의 추가 필수 여부는 실제 adapter별 계약에서 좁혀야 한다.
- Workstream 30은 `representative_stage_id`, `execution_mode`, `distribution_scope`와 통합 run/hash identity를 제공해야 한다. 해당 Workstream 파일은 이번 수정에서 건드리지 않았다.
- 실제 수치·실행·원문·권리·임의 confidence는 추가하지 않았다. 모든 신규 fixture는 기존 `SYNTHETIC` base를 변형한다.

### Control Tower H02 재검증 요청

- 기존 정상 2개와 실패 47개가 회귀 없이 유지되는지 확인해 달라.
- H02 공격 18개가 각 target code로 거부되고 optimistic provenance/rights 실패가 안전 상태로만 매핑되는지 확인해 달라.
- trace origin을 공격 dose run으로 맞춰도 run/hash dual truth가 차단되는지 독립 변형으로 확인해 달라.
- normalized output만 남긴 manifest와 0-byte provider output을 각각 거부하는지 확인해 달라.
- `VERIFIED`, `INTEGRATED`, checklist, commit·push는 Control Tower 판단으로 남긴다.


## Control Tower H02 독립 재검증 — 2026-08-20

- 판정: `CHANGES_REQUESTED` — 기존 Stage 1 통합 기준선은 유지하고 `10-tid-environment-provenance-contract-v1` 보완분만 재검토했다.
- 제공 명령 재실행: schema 11개, enum 축 4개, 정상 fixture 2개, 실패 fixture 65개가 기대 코드로 종료했고 exit code 0을 확인했다.
- 회귀 재실행: `python3 tests/simulation/run_all.py`의 simulation test 19개가 모두 통과했다.
- 형식 검사: `git diff --check` 통과.
- H01에서 지적한 합성 manifest·권리, 음수 dose, 시간 역전, 대표 모델, run/hash 연결, provider raw artifact 공격은 H02 전용 오류 코드로 차단됐다.

### 남은 False PASS

정상 `synthetic-tid-only-hold.json`을 기반으로 환경·mission dose·manifest·decision trace의 표면 metadata만 `CALCULATED`로 바꾸고 manifest research 권리를 `ALLOWED`로 만든 뒤, 다음 실제 규칙 피연산자는 그대로 `SYNTHETIC`으로 유지했다.

- `PART_TEST_EVIDENCE`의 TID limit와 해당 provenance
- `USER_POLICY`의 design factor·approval 근거와 해당 provenance

그 상태에서 TID margin rule을 `PASS`, evidence gap을 빈 배열, assurance를 `SUPPORTED_WITH_MITIGATION`으로 바꿔도 `schema_errors=[]`, `semantic_codes=[]`로 통과했다. 현재 rule result가 환경 trace 하나만 참조해도 되므로, 계산에 실제 사용한 부품 시험 한계와 정책 피연산자의 trace·데이터 분류를 검증하지 않는다.

### H03 수정 요구와 Exit Gate

- 각 rule result가 실제 사용한 모든 피연산자를 명시적인 trace 또는 동등한 구조로 연결하도록 한다.
- TID margin rule은 최소한 mission dose, part-test TID limit, user design factor/승인 정책과 실제 계산에 사용한 차폐·임무 입력을 추적한다.
- optimistic assurance에 사용된 피연산자 중 하나라도 `SYNTHETIC` 또는 `ASSUMED` 원본이면 지원 판정을 거부한다. policy의 `approval_status: APPROVED`만으로 합성 정책을 증거로 승격하지 않는다.
- `support-with-synthetic-part-evidence-and-policy` 공격 fixture를 추가한다. 원인 분리를 위해 합성 part evidence와 합성 policy 공격을 별도 fixture로 나누는 것을 권장한다.
- 누락 operand trace, 비증거성 rule operand, 합성 정책 지원 승격을 구분하는 안정적인 오류 코드를 정의하고 기존 실패 fixture 65개를 모두 유지한다.
- 다음 handoff는 `/Users/taehoon/Downloads/SPECTRA_10_TID_ENVIRONMENT_PROVENANCE_HANDOFF_H03.md`로 제출하고 다시 `READY_FOR_REVIEW`까지만 요청한다.

## H03 수정 반영 — 2026-08-20

대상 패키지는 계속 `10-tid-environment-provenance-contract-v1`이다. 기존 Stage 1 기준선의 `INTEGRATED` 판정과 H01/H02 회귀 결과를 유지하며 H03 보완분만 `READY_FOR_REVIEW`로 재제출한다.

### Rule operand 계약

- `decision.rule_results[].operand_bindings[]`를 기계 계약에 추가했다. 각 binding은 `operand_role`, 실제 `input_pointer`, 연결된 `origin_pointer`를 가진다.
- optimistic `TID_MARGIN_V1`은 `MISSION_DOSE`, `PART_TID_LIMIT`, `TID_DESIGN_FACTOR`, `POLICY_APPROVAL`, `SHIELDING_THICKNESS`, `MISSION_DURATION` 여섯 role을 모두 요구한다.
- 각 role은 단순 문자열 존재가 아니라 기대 input kind와 상대 경로까지 일치해야 한다.
- operand pointer와 origin을 실제 packet에서 해석하고 기존 provenance 조상 규칙으로 직접 연결을 확인한다.
- leaf metadata와 소유 input record metadata를 함께 검사한다. 어느 한쪽이라도 `SYNTHETIC` 또는 `ASSUMED`면 optimistic support를 거부한다.
- user policy의 `approval_status: APPROVED`는 policy metadata가 합성인 경우 증거성 승인이 아니다.
- operand contract가 정의되지 않은 rule은 optimistic support에 사용할 수 없다.

### H03 오류 코드

- `RULE_OPERAND_TRACE_MISSING`: 알려진 rule의 필수 operand role 누락
- `NON_EVIDENTIARY_RULE_OPERAND`: leaf 또는 소유 input record가 합성·가정 operand
- `SYNTHETIC_POLICY_WITH_SUPPORT`: 합성 user policy의 factor·approval을 지원 근거로 승격
- 인접 무결성 코드: `RULE_OPERAND_CONTRACT_UNKNOWN`, `DUPLICATE_RULE_OPERAND_ROLE`, `BROKEN_RULE_OPERAND_POINTER`, `RULE_OPERAND_METADATA_MISSING`, `UNRELATED_RULE_OPERAND_ORIGIN`, `RULE_OPERAND_ROLE_MISMATCH`

### H03 공격 fixture

- `support-with-environment-trace-only` → `RULE_OPERAND_TRACE_MISSING`
- `support-with-synthetic-part-evidence-and-policy` → `NON_EVIDENTIARY_RULE_OPERAND`과 `SYNTHETIC_POLICY_WITH_SUPPORT`
- `support-with-synthetic-part-evidence` → `NON_EVIDENTIARY_RULE_OPERAND`
- `support-with-synthetic-user-policy` → `SYNTHETIC_POLICY_WITH_SUPPORT`과 `NON_EVIDENTIARY_RULE_OPERAND`
- 네 fixture 모두 `schema_errors=[]` 상태에서 semantic gate의 지정 코드로 거부되는 것을 별도로 확인했다.

### H03 fixture 및 검증 결과

- 기존 정상 fixture: 2개 유지
- 기존 실패 fixture: 65개가 기존 기대 코드를 유지
- H03 신규 공격 fixture: 4개
- 전체 실패 fixture: 69개
- 전체 schema fixture: 71개
- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 실제 출력:

```text
SCHEMAS: 11 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 2 passed
INVALID FIXTURES: 69 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- schema gate exit code: `0`
- simulation 회귀: `python3 tests/simulation/run_all.py`, 19개 통과, exit code `0`
- 형식 검사: `git diff --check -- schemas docs/contracts docs/workstreams/10-contracts-schema tests/schema`, exit code `0`

### H03 알려진 한계와 영향

- 이번 operand contract는 Stage 1의 `TID_MARGIN_V1`에 한정한다. 새 deterministic rule은 optimistic 판정 전에 자체 필수 operand role map을 계약에 추가해야 한다.
- operand provenance의 구조와 분류를 검증하지만 실제 시험 보고서 진위, 정책 승인자의 권한, 과학 계산 정확도는 검증하지 않는다.
- 실제 데이터·실제 권리 승인·외부 모델 실행·임의 confidence는 추가하지 않았다. H03 fixture는 기존 synthetic base의 분류와 판정만 변형한다.
- Workstream 00·20·30·40 파일은 이번 H03 수정 범위에서 변경하지 않았다.

### Control Tower H03 재검증 요청

- 기존 정상 2개와 실패 65개의 기대 결과를 독립 환경에서 유지하는지 확인해 달라.
- 환경 trace 하나만 연결한 TID margin support가 `RULE_OPERAND_TRACE_MISSING`으로 거부되는지 확인해 달라.
- 모든 operand binding을 제공해도 합성 part evidence 또는 합성 policy가 위치별 코드로 차단되는지 확인해 달라.
- operand role을 무관한 evidentiary pointer로 바꾸는 변형이 `RULE_OPERAND_ROLE_MISMATCH`로 거부되는지 확인해 달라.
- `VERIFIED`, `INTEGRATED`, checklist, stage·commit·push는 Control Tower 판단으로 남긴다.


## Control Tower H03 독립 재검증 — 2026-08-20

- 판정: `CHANGES_REQUESTED` — 기존 Stage 1 통합 기준선은 유지하고 `10-tid-environment-provenance-contract-v1` H03 보완분만 검토했다.
- 제공 명령 재실행: schema 11개, 정상 fixture 2개, 실패 fixture 69개가 기대 코드로 종료했고 exit code 0을 확인했다.
- simulation 회귀: 19개 test 통과, 모든 합성 scenario의 assurance가 `HOLD`를 유지했다.
- 형식 검사: `git diff --check` 통과.
- H03 제출 공격: 환경 trace만 있는 support, 합성 part evidence, 합성 user policy가 각각 지정된 operand 오류 코드로 거부됐다.

### 남은 duplicate-input shadowing False PASS

EvidencePacket v1은 각 required input kind에 `minContains: 1`만 요구하고 중복을 허용한다. 반면 현재 TID margin 의미 계산은 `environments[0]`, `evidences[0]`, `policies[0]`을 사용하고, H03 operand binding은 임의의 같은-kind 입력 index를 가리킬 수 있다.

다음 두 독립 공격이 모두 `schema_errors=[]`, `semantic_codes=[]`로 통과했다.

1. 첫 번째 `PART_TEST_EVIDENCE`는 `SYNTHETIC`으로 두고 같은 identity의 두 번째 계산 evidence를 추가한 뒤 `PART_TID_LIMIT` binding만 두 번째 입력으로 연결했다. 실제 margin 계산은 첫 번째 합성 limit를 사용했다.
2. 첫 번째 `USER_POLICY`는 `SYNTHETIC`으로 두고 두 번째 계산 policy를 추가한 뒤 `TID_DESIGN_FACTOR`와 `POLICY_APPROVAL` binding만 두 번째 입력으로 연결했다. 실제 margin 계산은 첫 번째 합성 policy를 사용했다.

즉, binding의 provenance와 실제 계산 소비 레코드가 동일하다는 보장이 없다.

### H04 수정 요구와 Exit Gate

- EvidencePacket v1에서 7개 required input kind를 각각 정확히 하나만 허용하는 것을 우선 권고한다. JSON Schema의 각 `contains`에 `maxContains: 1`을 추가하고 의미 gate도 중복 kind를 안정적인 코드(예: `DUPLICATE_REQUIRED_INPUT_KIND`)로 거부한다.
- 장래에 같은 kind의 복수 입력을 지원하려면 첫 항목을 암묵적으로 선택하지 말고, rule 계산 자체가 operand binding 또는 명시 ID로 선택한 동일 레코드를 소비·재계산하도록 별도 버전 계약을 설계한다.
- duplicate part evidence와 duplicate user policy shadowing 공격 fixture를 추가하고 기존 실패 fixture 69개를 모두 유지한다.
- 다음 handoff는 `/Users/taehoon/Downloads/SPECTRA_10_TID_ENVIRONMENT_PROVENANCE_HANDOFF_H04.md`로 제출하고 다시 `READY_FOR_REVIEW`까지만 요청한다.

## H04 수정 반영 — 2026-08-20

대상 패키지는 계속 `10-tid-environment-provenance-contract-v1`이다. 기존 Stage 1 기준선의 `INTEGRATED` 판정과 H01~H03 회귀 결과는 유지하며 H04 보완분만 `READY_FOR_REVIEW`로 재제출한다.

### Required input 단일성 계약

- EvidencePacket v1의 `MISSION`, `BOM`, `RADIATION_ENVIRONMENT`, `PART_TEST_EVIDENCE`, `SHIELDING`, `MITIGATION`, `USER_POLICY`를 각각 정확히 하나로 제한했다.
- JSON Schema의 각 required-kind `contains`에 `minContains: 1`과 `maxContains: 1`을 함께 적용했다.
- 의미 gate는 7종 중 어느 kind든 두 개 이상이면 `DUPLICATE_REQUIRED_INPUT_KIND`를 반환한다.
- 검증 명령은 packet schema에서 exact-one rule이 7종 전체에 존재하는지 별도로 검사하고 `INPUT CARDINALITY: 7 required kinds exact-one`을 출력한다.
- 향후 복수 evidence·policy가 필요하면 first-item 계산을 유지하지 않는다. 별도 schema version에서 명시 record ID 또는 operand binding이 선택한 동일 레코드를 계산기가 직접 소비하도록 설계해야 한다.

### H04 공격 fixture

- `duplicate-part-evidence-shadow-binding`: 첫 번째 synthetic part evidence는 실제 계산 위치에 유지하고, 두 번째 calculated evidence로 `PART_TID_LIMIT` binding만 옮긴다.
- `duplicate-user-policy-shadow-binding`: 첫 번째 synthetic policy는 실제 계산 위치에 유지하고, 두 번째 calculated policy로 factor·approval binding만 옮긴다.
- 두 공격 모두 JSON Schema에서 `maxContains` 위반 1건, 의미 gate에서 `DUPLICATE_REQUIRED_INPUT_KIND`를 반환한다.

### H04 fixture 및 검증 결과

- 기존 정상 fixture: 2개 유지
- 기존 실패 fixture: 69개가 기존 기대 코드를 유지
- H04 신규 공격 fixture: 2개
- 전체 실패 fixture: 71개
- 전체 schema fixture: 73개
- 실행 명령: `python3 tests/schema/validate_contracts.py`
- 실제 출력:

```text
SCHEMAS: 11 checked
ENUM CONTRACTS: 4 axes checked
INPUT CARDINALITY: 7 required kinds exact-one
VALID FIXTURES: 2 passed
INVALID FIXTURES: 71 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

- schema gate exit code: `0`
- simulation 회귀: `python3 tests/simulation/run_all.py`, 19개 통과, exit code `0`
- 형식 검사: `git diff --check -- schemas docs/contracts docs/workstreams/10-contracts-schema tests/schema`, exit code `0`

### H04 알려진 한계와 영향

- v1은 복수 part evidence·policy의 합성이나 우선순위 선택을 지원하지 않는다. 이는 모호한 first-item 선택보다 fail-closed 단일성을 우선한 의도적 제약이다.
- 실제 데이터·외부 실행·원문·권리 승인·임의 confidence는 추가하지 않았다. 공격 fixture는 synthetic base를 복제·재분류한 invalid packet이다.
- Workstream 00·20·30·40 및 루트 문서는 이번 H04 수정에서 변경하지 않았다.

### Control Tower H04 재검증 요청

- 기존 정상 2개와 실패 69개의 기대 결과가 유지되는지 확인해 달라.
- 두 shadow-binding 공격이 schema `maxContains`와 `DUPLICATE_REQUIRED_INPUT_KIND` 양쪽에서 거부되는지 확인해 달라.
- 7개 required kind 각각에 exact-one 구조가 적용됐는지 검증 출력과 schema를 독립 확인해 달라.
- `VERIFIED`, `INTEGRATED`, checklist, stage·commit·push는 Control Tower 판단으로 남긴다.


## Control Tower H04 독립 재검증 — 2026-08-20

- 판정: `VERIFIED` — 기존 Stage 1 통합 기준선 이후의 `10-tid-environment-provenance-contract-v1` H01~H04 누적 보완분에 적용한다. Git 통합 전 상태다.
- contract gate: schema 11개, enum 축 4개, required input kind 7종 exact-one, 정상 fixture 2개, 실패 fixture 71개가 통과했다.
- simulation 회귀: 19개 test가 통과했고 합성 scenario의 assurance는 모두 `HOLD`를 유지했다.
- H04 shadow-binding 공격: duplicate part evidence와 duplicate user policy가 schema `maxContains`와 `DUPLICATE_REQUIRED_INPUT_KIND` 양쪽에서 거부됐다.
- 독립 확장 공격: 7개 required input kind를 각각 복제하고 배열 선두로 이동한 모든 경우가 schema와 의미 gate 양쪽에서 거부됐다.
- 데이터 경계: 실제 환경 모델 실행·실제 원문·실제 권리 승인·실제 assurance 수치는 추가되지 않았다. 신규 fixture는 모두 `SYNTHETIC`이다.
- 잔여 한계: EvidencePacket v1은 복수 same-kind input aggregation을 지원하지 않는다. 장래 복수 입력은 명시 record ID와 계산 소비 ID를 갖는 별도 version 계약이 필요하다.
