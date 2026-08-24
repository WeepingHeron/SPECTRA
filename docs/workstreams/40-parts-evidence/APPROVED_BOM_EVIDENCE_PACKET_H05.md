# H05 Approved-BOM Exact-Part Evidence Packet Assessment

## 1. 상태와 발행 판정

- 패키지: `40-approved-bom-exact-part-evidence-packet-h05`
- 요청 기준 commit: `d287d62`
- 실제 검사 기준: `d730ded` (`main`, `origin/main`), 2026-08-24
- 기준 관계: `d287d62`는 현재 HEAD의 ancestor이며 시작 작업트리는 clean이었다.
- 상태 상한: `READY_FOR_REVIEW`
- packet 판정: `PARTIAL_UNRESOLVED / HOLD`
- primary blocker: `BOM_APPROVAL_MISSING`
- decision-usable packet 생성 수: `0`
- `PART_TEST_EVIDENCE v2` JSON 생성 수: `0`

승인자, 승인 시각, 승인 대상 hash/version 또는 동등한 immutable reference가 연결된 BOM item을 찾지 못했다. 따라서 TI `5962L1420901VXC`를 BOM item으로 채택하지 않았고, 기존 `SLLK019`·`SLLA381` 자료를 decision evidence로 승격하지 않았다.

## 2. 입력 존재성 검사와 승인 BOM gate

2026-08-24에 다음 경로를 read-only로 확인했다.

- repository tracked/untracked filename과 관련 식별자 검색
- `docs/`, `schemas/`, `tests/`의 approval/BOM reference 검색
- `/Users/taehoon/Downloads`의 depth 2 범위에서 `bom`, `approval`, `rights`, `manifest`, `evidence` 이름 검색
- 이번 요청의 pasted instruction attachment

발견된 `schemas/bom.schema.json`은 입력 형식 계약일 뿐 승인 BOM 인스턴스가 아니다. 합성 schema fixture의 approval/hash는 실제 BOM 승인이나 실제 rights snapshot이 아니다. Git 밖 private BOM·시험 evidence manifest는 이번 세션 입력으로 제공되지 않았다.

| Gate field | Required input | Observed | Status |
|---|---|---|---|
| BOM immutable identity | `bom_id`, version 또는 content hash | 없음 | `BOM_APPROVAL_MISSING` |
| component immutable identity | `component_id`와 승인 대상 pointer | 없음 | `BOM_COMPONENT_MISSING` |
| manufacturer | 승인 BOM claim | 없음 | `NOT_REPORTED` |
| exact orderable PN | suffix를 보존한 승인 BOM claim | 없음 | `NOT_REPORTED` |
| package/grade | 승인 BOM claim | 없음 | `NOT_REPORTED` |
| process/die/lot/date-code policy | required/optional/waivable 규칙과 owner | 없음 | `IDENTITY_POLICY_MISSING` |
| approval actor | 승인자 identity와 role | 없음 | `BOM_APPROVAL_MISSING` |
| approval time | timezone을 포함한 timestamp | 없음 | `BOM_APPROVAL_MISSING` |
| approval target | BOM content hash/version 또는 immutable object generation | 없음 | `BOM_APPROVAL_TARGET_MISSING` |
| approval history anchor | append-only history/object reference | 없음 | `BOM_APPROVAL_HISTORY_MISSING` |

재개에 필요한 최소 사용자 입력은 다음과 같다.

1. Git 밖 승인 BOM의 read-only locator 또는 승인된 작은 manifest.
2. BOM/component version, content hash 또는 immutable storage generation.
3. 승인자, 승인 시각, 승인 범위와 history anchor.
4. exact manufacturer/PN/package/grade와 process/die/lot/date-code 일치 정책.
5. 해당 입력을 `FETCH`, `PRIVATE_STORE`, `PROCESS_LOCAL/AI`, `DISPLAY_INTERNAL`할 수 있는 action별 승인.

## 3. discovery candidate 비교 — BOM 자동 채택 금지

| Claim source | Manufacturer | Exact PN | Package/grade | Process/die/lot | Identity class | Decision eligibility |
|---|---|---|---|---|---|---|
| approved BOM item | `NOT_PROVIDED` | `NOT_PROVIDED` | `NOT_PROVIDED` | policy와 값 모두 `NOT_PROVIDED` | `PARTIAL_UNRESOLVED` | `false` |
| TI exact-part product page | Texas Instruments | `5962L1420901VXC` | CFP `HKX`, 8 pin; Space/QML-V/RHA | test lot claim 아님 | catalog-level discovery claim | `false` |
| TI `SLLK019–February 2018` | Texas Instruments | report에 `5962L1420901VXC` 직접 표기 | CFP, LBC3S; die lot `1634103DFB`; A/T lot/date code `7005041MTT/1736A`; die revision·actual test date 미보고 | source-side exact claim, 내부 TID 조건 충돌 존재 | `false` |
| TI `SLLA381–March 2018` | Texas Instruments | `5962L1420901VX` base SMD만 표기, suffix `C` 미표기 | 8-pin CFP, LBC3S; die/wafer/A/T lot·date code 미보고 | `PARTIAL_IDENTITY` | `false` |

제품 catalog의 exact PN 일치는 시험 sample exact suffix·lot 일치를 증명하지 않는다. `SLLK019`의 source-side exact identity도 승인 BOM과의 `EXACT_MATCH`가 아니며, `SLLA381`은 base SMD만 일치하므로 exact destructive SEE 근거가 아니다.

## 4. source·artifact·rights gate

| Source/artifact | Official locator | Document identity | Artifact/hash state | Rights state | Decision use |
|---|---|---|---|---|---|
| TI exact-part page | <https://www.ti.com/product/SN55HVD233-SP/part-details/5962L1420901VXC> | dynamic product page; current revision/date not fixed in an approved snapshot | approved snapshot/hash 없음 | public locator only; action approval 없음 | `false` |
| TI TID report | <https://www.ti.com/lit/rr/sllk019/sllk019.pdf> | `SLLK019`, February 2018; separate revision marker not reported | H03 historical observed SHA-256 `623b9d19e3b7aba3e55151c7f73f34f47a48f9b36fde46049d6c8d2c79884fa2`; 승인 artifact hash가 아니며 H05에서 재취득하지 않음 | locator conditional; other required actions `UNCONFIRMED` | `false` |
| TI SEE report | <https://www.ti.com/lit/pdf/slla381> | `SLLA381`, March 2018; separate revision marker not printed | approved artifact/hash/storage generation 없음 | public view observed in H04; required actions `RIGHTS_UNRESOLVED` | `false` |
| raw manifest v2 | repository schema only | actual manifest instance 없음 | storage generation, scan, parser, review 없음 | rights snapshot instance 없음 | `false` |

`observed download hash`와 `approved artifact hash`는 분리한다. H03의 hash는 당시 임시 관찰 bytes의 기록이며, 승인 storage generation·rights snapshot·validation/review history가 없으므로 H05 approval target이나 raw manifest reference로 재사용하지 않는다.

### 4.1 action별 rights 상태

| Action | Required for candidate packet | Approved evidence found | H05 status |
|---|---:|---|---|
| `LOCATOR` | yes | 조건부 public link 기록만 있음 | `CONDITIONAL_ONLY` |
| `FETCH` | yes | 없음 | `UNCONFIRMED` |
| `PRIVATE_STORE` | yes | 없음 | `UNCONFIRMED` |
| `PROCESS_LOCAL/AI` | yes | 없음 | `UNCONFIRMED` |
| `DISPLAY_INTERNAL` | yes | 없음 | `UNCONFIRMED` |
| `DISPLAY_EXTERNAL` | conditional | 없음 | `UNCONFIRMED` |
| `REDISTRIBUTE` | conditional | 없음 | `UNCONFIRMED` |
| `COMMERCIAL_USE` | conditional | 없음 | `UNCONFIRMED` |

필요 action 하나라도 미확인이면 decision-ineligible이다. 공개 열람 가능성은 위 action의 승인이 아니다. H05에서 PDF를 다운로드·저장·자동 추출하지 않았다.

## 5. 시험 조건·임무 적용성·사건 coverage

| Event | Evidence candidate | Identity/condition state | Mission requirement/applicability | Coverage decision |
|---|---|---|---|---|
| TID | `SLLK019` | source claim과 locator는 있으나 HDR dose rate, maximum irradiated dose, LDR bias coverage가 `CONFLICTING`; rights/manifest/BOM 없음 | Stage 3 environment와 Stage 5 criterion 미제공 | `EVIDENCE_PRESENT_BUT_DECISION_INELIGIBLE / HOLD` |
| SEU | 선택 exact-part 원문 없음 | `NOT_REPORTED_IN_SELECTED_BUNDLE` | required mode/policy 미제공 | `EVIDENCE_MISSING / HOLD` |
| SEL | `SLLA381` | `PARTIAL_IDENTITY`; `ZERO_EVENTS_WITH_TEST_LIMITS`; explicit detection threshold와 post-test latent-damage evidence 미확인 | required mode/policy와 mission LET envelope 미제공 | `REPORTED_IDENTITY_UNRESOLVED / HOLD` |
| SEB | exact-part result 없음 | `NOT_REPORTED_IN_SELECTED_BUNDLE` | `NOT_EVALUATED`; 단순 비적용 추론 금지 | `EVIDENCE_MISSING / HOLD` |
| SEGR | exact-part result 없음 | `NOT_REPORTED_IN_SELECTED_BUNDLE` | `NOT_EVALUATED`; 단순 비적용 추론 금지 | `EVIDENCE_MISSING / HOLD` |

`SLLK019`의 충돌 대안과 각 locator는 기존 H03 record를 유지한다. 해결 전에는 report-wide dose rate, 최대 조사량 또는 LDR bias coverage를 decision operand로 선택하지 않는다. `SLLA381`의 zero-event SEL은 제한 조건·fluence·sample·upper bound·identity 한계와 함께만 보존하며 immunity로 표현하지 않는다. SEL은 SEB·SEGR을, SEU/ECC는 destructive SEE를 대체하지 않는다.

Stage 3의 실제 mission environment와 Stage 5의 event별 승인 policy가 이번 입력에 없으므로 모든 applicability는 `NOT_EVALUATED`다. 임의 궤도, dose, LET, bias, temperature, design factor 또는 failure-mode requirement를 만들지 않았다.

## 6. Workstream 40 packet candidate 결정

실행 JSON fixture를 만들지 않았다. 현재 v1 `schemas/part-test-evidence.schema.json`에 맞추려면 미보고 `test_date`, 숫자 `temperature_c`, 단일 `facility`를 만들어야 하고, approval·claim locator·action rights·conflict alternatives·독립 event coverage를 표현할 수 없다. 이는 evidence loss 또는 false precision을 만든다.

대신 다음 field map만 발행한다.

| Candidate field | H05 value/status | Decision rule |
|---|---|---|
| `record_purpose` | `DISCOVERY_CANDIDATE` | decision candidate로 승격 금지 |
| `component_ref` | `NOT_REPORTED` | `BOM_APPROVAL_MISSING` |
| `bom_approval` | `NOT_PROVIDED` | `used_for_decision=false` |
| `tested_identity` | source별 claim을 분리; merged exact identity 금지 | catalog/report/BOM claim 혼합 금지 |
| `artifact_refs` | 없음 | `RAW_MANIFEST_REFERENCE_MISSING` |
| `rights_snapshot` | 없음 | `RIGHTS_SNAPSHOT_NOT_ACTIVE` |
| `events.TID` | discovery claim; conflict 유지 | decision operand 금지 |
| `events.SEU` | `EVIDENCE_MISSING` | independent gap |
| `events.SEL` | `REPORTED_IDENTITY_UNRESOLVED` | independent gap/claim |
| `events.SEB` | `EVIDENCE_MISSING` | independent gap |
| `events.SEGR` | `EVIDENCE_MISSING` | independent gap |
| `applicability` | `NOT_EVALUATED` | PASS 금지 |
| `used_for_decision` | `false` | immutable H05 outcome |
| `termination` | `PARTIAL_UNRESOLVED / HOLD` | packet not issuable |

## 7. direct test와 공격 fixture 상태

Workstream 40 전용 실행 구조를 추가하지 않았으므로 H05 direct tests는 `0`개다. 승인 BOM·권리 manifest·v2 contract 없이 synthetic local validator를 새 사실 계약처럼 만드는 것은 안전하지 않다. 아래 expected code는 통합된 `RESEARCH.md` 명세의 구현 요구이며 actual은 모두 `NOT_EXECUTED — V2_VALIDATOR_NOT_AVAILABLE`이다.

| Attack | Expected primary code(s) | Expected safe end | Actual |
|---|---|---|---|
| suffix 제거 false exact | `IDENTITY_NORMALIZATION_LOSSY`, `PART_NUMBER_CONFLICT` | `HOLD`, decision false | `NOT_EXECUTED` |
| manufacturer alias 오매핑 | `MANUFACTURER_ALIAS_UNAPPROVED` | `PARTIAL_UNRESOLVED/HOLD` | `NOT_EXECUTED` |
| package/grade mismatch | `PACKAGE_CONFLICT` 또는 `QUALITY_GRADE_CONFLICT` | `CONTRADICTED/HOLD` | `NOT_EXECUTED` |
| process/die/lot mismatch | `PROCESS_CONFLICT`, `DIE_CONFLICT`, `LOT_CONFLICT` | `CONTRADICTED/HOLD` | `NOT_EXECUTED` |
| BOM approval 누락 | `BOM_APPROVAL_MISSING` | `PARTIAL_UNRESOLVED/HOLD` | input inspection으로 gap 확인; validator `NOT_EXECUTED` |
| BOM approval 위조/stale target | `BOM_APPROVAL_TARGET_MISMATCH` 또는 `BOM_APPROVAL_HISTORY_INVALID` | `PROVENANCE_FAILURE/HOLD` | `NOT_EXECUTED` |
| locator 누락/불일치 | `SOURCE_LOCATOR_MISSING` 또는 `INVALID_SOURCE_LOCATOR` | `PROVENANCE_FAILURE/HOLD` | `NOT_EXECUTED` |
| artifact hash 누락/불일치 | `ARTIFACT_HASH_MISSING` 또는 `ARTIFACT_HASH_MISMATCH` | `PROVENANCE_FAILURE/HOLD` | `NOT_EXECUTED` |
| rights action 누락/불일치 | `RIGHTS_UNRESOLVED` 또는 `RIGHTS_SCOPE_VIOLATION` | `HOLD` | input inspection으로 gap 확인; validator `NOT_EXECUTED` |
| conflict alternative 소실 | `CONFLICTING_ALTERNATIVES_INSUFFICIENT` | `INVALID_INPUT/HOLD` | `NOT_EXECUTED` |
| SEU→SEL 대체 | `EVIDENCE_TYPE_SUBSTITUTION`, `DESTRUCTIVE_SEE_MODE_MISSING` | `HOLD` | `NOT_EXECUTED` |
| zero-event immunity 승격 | `ZERO_EVENT_BOUND_MISSING`, `IMMUNITY_CLAIM_UNSUPPORTED` | `HOLD` | `NOT_EXECUTED` |
| SEL→SEB/SEGR 대체 | `EVIDENCE_TYPE_SUBSTITUTION`, `DESTRUCTIVE_SEE_MODE_MISSING` | `HOLD` | `NOT_EXECUTED` |
| 시험 범위 외삽 | `OUT_OF_TEST_SCOPE`, `DECISION_TRACE_NOT_APPLICABLE` | `HOLD` | `NOT_EXECUTED` |
| applicability 미확인 PASS | `MISSION_APPLICABILITY_NOT_EVALUATED` 또는 `DECISION_TRACE_NOT_APPLICABLE` | `HOLD` | `NOT_EXECUTED` |

위 표의 새 BOM approval·package/grade·mission applicability 코드 이름은 v2 구현 전 변경 요청 대상이며 현재 validator가 이미 구현했다고 주장하지 않는다.

## 8. CONTRACT_CHANGE_REQUEST

### 요청 대상

- Workstream 10 / Control Tower

### 요청 내용

1. `PART_TEST_EVIDENCE v2`를 v1과 분리된 discriminated record로 구현하고 packet/input version dispatch를 추가한다.
2. claim wrapper가 `VERIFIED`, `NOT_REPORTED`, `CONFLICTING alternatives[]`, 필요한 경우 `NOT_APPLICABLE`을 lossless하게 표현하도록 한다.
3. `CONFLICTING alternatives[]`는 서로 다른 canonical value 2개 이상, source/claim identity와 실제 locator를 각 대안에 요구한다.
4. HDR/LDR 또는 facility별 다중 `test_campaign.subruns[]`와 event별 override를 지원한다.
5. 모든 decision-used claim에 typed field locator를 연결하고 raw artifact revision/generation과 resolve한다.
6. `LOCATOR`, `FETCH`, `PRIVATE_STORE`, `PROCESS_LOCAL`, `PROCESS_DOCUMENT_AI`, `PROCESS_VERTEX_AI`, `DISPLAY_INTERNAL`, `DISPLAY_EXTERNAL`, `REDISTRIBUTE`, `COMMERCIAL_USE`를 action별 grant/scope/processor/audience/기간/approver로 표현한다.
7. `artifact_sha256`, `evidence_content_sha256`, `approval_target_sha256`, `review.history[].entry_sha256`를 self-reference 없는 projection으로 분리하고 외부 immutable history anchor를 요구한다.
8. BOM approval에도 BOM content/version target, component pointer, actor/time/scope와 append-only history anchor를 구조화한다.
9. TID·SEU·SEL·SEB·SEGR을 독립 result/gap record로 만들고 event substitution을 금지한다.
10. structured applicability가 mission environment/policy pointer, compared boundaries, status `APPLICABLE/NOT_APPLICABLE/NOT_EVALUATED`, reason codes를 보존하도록 한다.

### v1→v2 non-filling adapter

- 없는 exact PN, test date, temperature, facility, lot, locator, rights, approval과 event condition을 생성하지 않는다.
- v1 value에 원문 locator가 없으면 discovery context에 격리하고 v2 claim은 `NOT_REPORTED`로 둔다.
- v1 `cross_section`을 SEL·SEB·SEGR에 복사하지 않는다.
- v1 hash를 artifact/content/approval/history hash로 복사하지 않는다.
- adapter output은 재추출·재검토·실제 artifact 검증 전 `DISCOVERY`, `used_for_decision=false`, `MIGRATION_REVIEW_REQUIRED / HOLD`다.

### 필요한 정상·공격 fixture와 stable error code

- 정상: exact approved-BOM match, missing-but-valid discovery, family-only discovery, complete conflicting alternatives, 실제 synthetic bytes에서 계산한 hash/history chain, event별 complete control.
- 공격: 7절의 15개 축과 content/history tamper, stale approval target, legacy dual truth.
- validator는 target code와 함께 `used_for_decision=false`, assurance `HOLD`를 assert하고 `SUPPORTED_WITH_MITIGATION`을 금지해야 한다.
- 누락과 확인된 모순은 각각 `PARTIAL_UNRESOLVED`와 `CONTRADICTED`로 분리한다.

### v1 consumer 호환·migration·rollback 경계

- v1 schema/fixtures와 합성 consumer는 동결하고 기존 version dispatch를 유지한다.
- v2 record를 v1 flat record로 자동 down-convert하지 않는다. event, conflict, rights와 locator가 손실되기 때문이다.
- 동일 packet에서 v1/v2를 함께 허용하면 exact input pointer와 schema version을 rule result에 기록하고 v1 trace는 실제 support decision에 사용할 수 없게 한다.
- rollout은 v2 validator와 fixtures가 독립 통과한 뒤 opt-in으로 시작한다.
- rollback은 v2 decision 경로를 비활성화하되 v2 records를 삭제·v1로 변환하지 않고 discovery archive로 보존한다.

공통 schema·validator·consumer는 이 요청 승인 전 수정하지 않았다.

## 9. data-quality finding과 재개 조건

| Finding | Severity | Decision risk | Resume condition |
|---|---|---|---|
| approved BOM/approval target 없음 | Critical | discovery part를 고객 BOM으로 오인 | BOM owner의 immutable approval record |
| rights snapshot/raw manifest 없음 | Critical | 무단 처리 및 artifact 바꿔치기 | rights owner와 Workstream 70의 승인 manifest |
| v1 표현력 부족 | Critical | 누락값 생성, conflict/event loss | Workstream 10의 v2 schema/semantic gate |
| TID source 내부 충돌 | High | 임의 dose/rate/bias operand 선택 | 정정본/raw log 또는 승인 reviewer resolution |
| SEL exact test identity 불완전 | High | base SMD를 exact suffix·lot로 승격 | exact test article/lot 원문과 승인 review |
| SEB·SEGR evidence 없음 | High | SEL/SEU로 destructive gap 대체 | event별 exact evidence 또는 승인된 applicability policy |
| mission applicability/policy 없음 | Critical | 시험 범위 밖 PASS | Stage 3 environment와 Stage 5 approved policy |

## 10. 최종 HOLD와 다음 행동

현재 packet은 발행할 수 없다. 종료 상태는 다음과 같다.

- `BOM_APPROVAL_MISSING`
- `BOM_APPROVAL_TARGET_MISSING`
- `IDENTITY_POLICY_MISSING`
- `RIGHTS_SNAPSHOT_NOT_ACTIVE`
- `RAW_MANIFEST_REFERENCE_MISSING`
- `DOCUMENT_INTERNAL_CONFLICT`
- `EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED`
- `SEU_EVIDENCE_MISSING`
- `SEB_EVIDENCE_MISSING`
- `SEGR_EVIDENCE_MISSING`
- `MISSION_APPLICABILITY_NOT_EVALUATED`
- `V2_CONTRACT_REQUIRED`
- `REVIEW_APPROVAL_MISSING`

다음 행동 순서는 승인 BOM 입력 → action rights/storage manifest → v2 contract/validator → exact identity review → event별 applicability/coverage → 공격 fixture → independent approval이다. 그 전에는 `PACKET_ISSUABLE_CANDIDATE`, Stage 4 완료, 지원 판정 또는 비행 적합성을 주장하지 않는다.
