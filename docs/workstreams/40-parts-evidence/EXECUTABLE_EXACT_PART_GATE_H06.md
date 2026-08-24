# H06 Executable Exact-Part Evidence Gate

## 1. 상태와 범위

- 패키지: `40-executable-exact-part-evidence-gate-h06`
- 기준 HEAD: `d730ded`, branch `main`
- 실행일: 2026-08-24
- 상태: `READY_FOR_REVIEW`
- 실제 packet: `0`
- production `PART_TEST_EVIDENCE v2`: `NOT_IMPLEMENTED`
- H05 discovery decision: `PARTIAL_UNRESOLVED / HOLD`

H05 field map과 공격 명세를 `tests/parts_evidence/**`의 격리된 test contract, validator, fixture와 unittest로 전환했다. 공통 schema·validator·engine을 수정하지 않았으며 이 구현은 production contract가 아니다.

## 2. test contract 경계

test contract version은 `W40_TEST_CONTRACT_1.0.0`이다. 모든 입력은 `PART_TEST_EVIDENCE_TEST_GATE`, `record_purpose=DISCOVERY_CANDIDATE`, `usage=DEMO_ONLY`이며 결과는 항상 `assurance_decision=HOLD`, `used_for_decision=false`, `recommendation=null`로 닫힌다.

분리된 축:

- BOM approval: version, component pointer, approval target hash, history anchor
- exact identity claim: `VERIFIED`, `NOT_REPORTED`, `CONFLICTING alternatives[]`
- source document와 locator
- artifact identity와 synthetic fixture bytes hash
- action별 rights 8종
- review history와 entry/head hash
- TID·SEU·SEL·SEB·SEGR 독립 coverage
- structured applicability
- requested outcome과 decision-use

synthetic control의 BOM approval target, review entry/head와 작은 text artifact hash는 실제 fixture bytes/projection에서 테스트 실행 시 계산한다. digest literal을 실제 hash처럼 작성하지 않았다. fixture identity, actor와 URI는 모두 `SYNTHETIC_CONTROL / DEMO_ONLY`다.

## 3. 결정론적 상태 전이

| 조건 | processing | identity | applicability | decision use |
|---|---|---|---|---|
| unknown field, malformed nested type, invalid claim/alternatives | `INVALID_INPUT` | safe unresolved/contradicted state | `NOT_EVALUATED` 또는 safe state | `false` |
| hash/locator/approval target/review chain failure | `PROVENANCE_FAILURE` | safe unresolved/contradicted state | safe state | `false` |
| verified identity conflict | `VALID` 또는 structural/provenance 우선 | `CONTRADICTED` | independent | `false` |
| exact PN `NOT_REPORTED` + verified family relation | `VALID` | `FAMILY_ONLY` | independent | `false` |
| exact PN/BOM approval 불완전 | safe processing | `PARTIAL_UNRESOLVED` | independent | `false` |
| approved real BOM and all identity fields match | test contract에 상태 규칙만 존재 | `EXACT_MATCH` 가능 | independent | 이 suite에서는 production decision 금지 |
| out-of-range comparison | `VALID` | independent | `NOT_APPLICABLE` | `false` |
| mission environment 없음 | `VALID` 또는 선행 failure | independent | `NOT_EVALUATED` | `false` |

`EXACT_MATCH`는 `approval.status=APPROVED`와 모든 required identity의 verified match일 때만 의미상 도달한다. 현재 fixture에는 실제 `APPROVED` BOM이 없으며 synthetic control은 구조가 일치해도 `PARTIAL_UNRESOLVED`다.

## 4. event coverage gate

- event array는 TID·SEU·SEL·SEB·SEGR exact-one coverage를 요구한다.
- `source_event_type != event_type`이면 `EVIDENCE_TYPE_SUBSTITUTION`; target이 destructive mode이면 `DESTRUCTIVE_SEE_MODE_MISSING`을 추가한다.
- zero-event immunity claim은 fluence, sample size, detection limit, confidence/upper-bound presence flag가 모두 true여도 이 test gate에서는 `IMMUNITY_CLAIM_UNSUPPORTED`로 decision 사용을 막는다. 하나라도 빠지면 `ZERO_EVENT_BOUND_MISSING`도 반환한다.
- `EVIDENCE_MISSING`은 event별 stable gap code로 유지한다.
- destructive event가 `REPORTED_IDENTITY_UNRESOLVED`이면 `EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED`다.

실제 시험 수치, 실제 lot/date code, 실제 confidence 또는 upper bound를 synthetic fixture에 넣지 않았다. zero-event와 시험 범위 공격은 값 존재 여부 boolean만 사용한다.

## 5. fixture와 direct tests

| File | Purpose |
|---|---|
| `tests/parts_evidence/evidence_gate.py` | strict test validator, hash materializer, mutation helper |
| `fixtures/synthetic-control.json` | structure-valid `SYNTHETIC_CONTROL / DEMO_ONLY` |
| `fixtures/artifacts/synthetic-source.txt` | hash/locator 검사용 작은 synthetic bytes |
| `fixtures/h05-discovery-candidate.json` | H05 TI locator/observed status만 보존한 decision-ineligible candidate |
| `fixtures/attack-cases.json` | 15 required axes를 21 executable cases로 분해 |
| `test_evidence_gate.py` | unittest 5 methods, 26 scenario checks |

실행 명령:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.parts_evidence.test_evidence_gate
```

결과:

```text
Ran 5 tests in 0.006s
OK
```

첫 실행에서는 out-of-range attack이 `OUT_OF_TEST_SCOPE`와 `HOLD`를 만들면서도 display status가 `APPLICABLE`로 남는 실패 1건을 검출했다. validator를 수정해 해당 상태를 `NOT_APPLICABLE`로 강등한 뒤 전체 suite가 통과했다.

## 6. 공격 expected/actual

| Required attack axis | Executable cases | Expected | Actual |
|---|---:|---|---|
| suffix 제거 false exact | 1 | `IDENTITY_NORMALIZATION_LOSSY`, `PART_NUMBER_CONFLICT` | exact codes; `CONTRADICTED/HOLD/false` |
| manufacturer alias 오매핑 | 1 | `MANUFACTURER_ALIAS_UNAPPROVED` | exact code; `PARTIAL_UNRESOLVED/HOLD/false` |
| package/grade mismatch | 1 | `PACKAGE_CONFLICT`, `QUALITY_GRADE_CONFLICT` | exact codes; `CONTRADICTED/HOLD/false` |
| process/die/lot mismatch | 1 | `PROCESS_CONFLICT`, `DIE_CONFLICT`, `LOT_CONFLICT` | exact codes; `CONTRADICTED/HOLD/false` |
| BOM approval 누락 | 1 | `BOM_APPROVAL_MISSING`, target/history gap | exact codes; `PROVENANCE_FAILURE/HOLD/false` |
| BOM approval stale target | 1 | `BOM_APPROVAL_TARGET_MISMATCH` | exact code; `PROVENANCE_FAILURE/HOLD/false` |
| locator 누락·불일치 | 2 | `SOURCE_LOCATOR_MISSING`, `INVALID_SOURCE_LOCATOR` | 각 exact code; `PROVENANCE_FAILURE/HOLD/false` |
| artifact hash 누락·불일치 | 2 | `ARTIFACT_HASH_MISSING`, `ARTIFACT_HASH_MISMATCH` | 각 exact code; `PROVENANCE_FAILURE/HOLD/false` |
| rights 누락·scope mismatch | 2 | `RIGHTS_ACTION_MISSING/RIGHTS_UNRESOLVED`, `RIGHTS_SCOPE_VIOLATION` | 각 exact code; `HOLD/false` |
| conflict alternative 소실·중복 | 2 | insufficient/duplicate codes | 각 exact code; `INVALID_INPUT/CONTRADICTED/HOLD/false` |
| SEU→SEL 대체 | 1 | substitution + destructive gap | exact codes; `HOLD/false` |
| zero-event immunity 승격 | 1 | bound missing + immunity unsupported | exact codes; `HOLD/false` |
| SEL→SEB/SEGR 대체 | 1 | substitution + destructive gap | exact codes; `HOLD/false` |
| 시험 범위 외삽 | 1 | out-of-scope + trace not applicable | exact codes; `NOT_APPLICABLE/HOLD/false` |
| applicability 미확인 PASS | 1 | mission not evaluated + decision forbidden | exact codes; `NOT_EVALUATED/HOLD/false` |
| additional parser hardening | 2 | unknown field / malformed nested type | exact codes; `INVALID_INPUT/HOLD/false` |

추가 direct checks는 malformed JSON, non-object root, valid family-only transition과 H05 discovery candidate 재평가다.

## 7. H05 discovery candidate 재평가

```text
processing_status: PROVENANCE_FAILURE
identity_status: PARTIAL_UNRESOLVED
applicability_status: NOT_EVALUATED
assurance_decision: HOLD
used_for_decision: false
recommendation: null
```

stable codes:

- `BOM_APPROVAL_MISSING`
- `BOM_APPROVAL_TARGET_MISSING`
- `BOM_APPROVAL_HISTORY_INVALID`
- `RAW_MANIFEST_REFERENCE_MISSING`
- `RIGHTS_UNRESOLVED`
- `REVIEW_HISTORY_INVALID`
- `SEU_EVIDENCE_MISSING`
- `EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED`
- `SEB_EVIDENCE_MISSING`
- `SEGR_EVIDENCE_MISSING`
- `MISSION_APPLICABILITY_NOT_EVALUATED`
- `DISCOVERY_ONLY_INPUT`

TI product page와 `SLLK019`의 source-side exact claim은 승인 BOM exact match로 승격되지 않았다. `SLLA381`의 SEL은 identity unresolved이며 SEB·SEGR gap을 닫지 않는다.

## 8. 알려진 경계와 CONTRACT_CHANGE_REQUEST

이 gate는 test-only reference implementation이다. production 발행에는 Workstream 10/Control Tower가 다음을 공통 계약으로 승인·구현해야 한다.

- versioned `PART_TEST_EVIDENCE v2` schema와 semantic dispatch
- BOM approval content/scope/history contract와 canonical projection
- typed source locator와 raw manifest resolution
- action rights scope/processor/audience/validity/approval
- self-reference 없는 artifact/content/approval/history hashes
- event별 수치·단위·condition discriminated records
- structured mission applicability와 policy pointers
- v1 non-filling adapter, production fixtures, migration/rollback

Workstream 40 test contract를 production code로 import하거나 공통 schema 대신 사용하면 안 된다. 승인 BOM, rights snapshot, raw manifest, mission environment/policy, exact destructive SEE evidence가 들어오기 전 실제 packet은 계속 0건이다.

## 9. Exit Gate

- 21 executable attack cases가 target code와 `HOLD`, `used_for_decision=false`를 확인했다.
- 승인 BOM이 없는 H05 candidate에서 `EXACT_MATCH`, `APPLICABLE`, PASS, recommendation이 생성되지 않았다.
- event substitution, zero-event immunity와 범위 외삽이 차단됐다.
- actual PDF, customer BOM, rights-unresolved artifact를 추가하지 않았다.
- production v2 또는 Stage 4 완료를 주장하지 않는다.
- 제출 상태는 `READY_FOR_REVIEW`다.
