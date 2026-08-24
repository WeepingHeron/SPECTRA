# Environment Contract Issuance Gate H03

## 상태와 목적

`PRE-RESULT PROTOCOL — READY_FOR_REVIEW 상한`

이 문서는 실제 SPENVIS bundle을 `RADIATION_ENVIRONMENT` TID-only contract와 제품 UI locator에 연결하기 전에 필요한 발행 조건을 고정한다. parser 성공이나 checksum 일치는 발행 승인이 아니다. 조건 하나라도 실제 승인 증거로 충족되지 않으면 결과는 `HOLD_NOT_ISSUED`이고 dose contract를 생성하지 않는다.

## H03 발행 대상과 action scope

H03는 내부 분석에만 머무는 좁은 연구 사본이 아니라 제품 contract, 제품 UI locator, Competition Demo Release의 cloud/automation/external-display 가능성까지 포함한 대상이다. 따라서 아래 9개 action을 모두 필수로 고정한다. 더 좁은 사용 목적은 별도 scope hash와 별도 권리 검토를 받아야 하며 이 H03 승인을 재사용할 수 없다.

| Action | H03에서 필요한 이유 | 승인 증거 최소 요건 |
|---|---|---|
| `FETCH` | provider 원본 취득·재취득 | 적용 주체와 대상 output이 명시된 grant |
| `PRIVATE_STORE` | private evidence 보관 | 보관 위치·기간·주체가 포함된 grant |
| `PROCESS_LOCAL` | parser·hash·구조 검증 | 로컬 처리 범위를 허용하는 grant |
| `DISPLAY_INTERNAL` | 내부 제품 UI locator와 검토 | 내부 audience와 표시 범위가 명시된 grant |
| `DISPLAY_EXTERNAL` | 심사·외부 시연 가능성 | 외부 audience와 파생값/locator 범위가 명시된 grant |
| `REDISTRIBUTE` | 결과·원문 또는 파생 산출물 전달 | 원문/파생물별 재배포 범위가 명시된 grant |
| `COMMERCIAL_USE` | 제품·사업 목적 사용 | 상업 주체와 목적이 명시된 승인 |
| `AUTOMATION` | 자동 ingest·재처리 | API/browser/job 자동화 범위가 명시된 승인 |
| `CLOUD_STORE` | GCP immutable storage와 generation | cloud provider·region·retention 범위가 명시된 승인 |

각 grant에는 source locator, 원문 위치, 적용 주체, scope hash, 승인자, 유효기간을 연결한다. 공개 접근, 개인 다운로드와 로컬 백업 관찰은 action approval이 아니다.

H03 scope의 canonical preimage는 다음 필드의 sorted compact JSON이다.

```json
{"actions":["AUTOMATION","CLOUD_STORE","COMMERCIAL_USE","DISPLAY_EXTERNAL","DISPLAY_INTERNAL","FETCH","PRIVATE_STORE","PROCESS_LOCAL","REDISTRIBUTE"],"consumer":"SPECTRA_PRODUCT_CONTRACT_AND_UI_LOCATOR_H03"}
```

계산된 scope hash는 `sha256:1983a85522d2f31eb74780a9d87be565470bd437c1cd1fba59e074734eae6e19`다. 이는 승인 hash가 아니라 검토 대상을 고정한 계산값이다.

## 발행 조건과 stable code

| Gate | 충족 조건 | 실패 code |
|---|---|---|
| Provider | provider가 발행한 고유 job reference와 source location/hash | `PROVIDER_JOB_REFERENCE_MISSING`, `PROVIDER_JOB_REFERENCE_UNVERIFIED` |
| Rights | 9개 action exact-one, `ALLOWED`, 동일 subject/scope/approver, 유효기간 활성 | `RIGHTS_APPROVAL_MISSING`, `RIGHTS_ACTION_GRANT_MISSING`, `RIGHTS_ACTION_SCOPE_MISMATCH`, `RIGHTS_ACTION_GRANT_STALE` |
| Storage | 승인 immutable storage identity와 exact generation | `APPROVED_STORAGE_UNAVAILABLE`, `RAW_GENERATION_MISMATCH` |
| Raw manifest | 승인 v2, bundle/parser/hash/rights/history/validation binding | `RAW_ARTIFACT_MANIFEST_V2_MISSING`, `RAW_BUNDLE_HASH_MISMATCH`, `RAW_RIGHTS_SNAPSHOT_MISMATCH`, `RAW_ARTIFACT_VALIDATION_INCOMPLETE` |
| Artifact identity | 9/9 checksum, 필수 7 role exact-one, identity/path 재사용 없음 | 기존 `SOURCE_ROLE_*`, `ARTIFACT_ID_REUSED_ACROSS_ROLES`, `RESOLVED_PATH_REUSED_ACROSS_ROLES` |
| Model | mission·source·unit·target·geometry·depth·model/version/config 일치 | `MODEL_CONFIGURATION_MISMATCH`, `MODEL_VERSION_DRIFT`, `MODEL_VERSION_NOT_VERIFIED` |
| Crosscheck | 결과 확인 전에 승인된 protocol/criteria와 독립 reviewer, 결과 hash | `SCIENTIFIC_CROSSCHECK_NOT_EVALUATED`, `SCIENTIFIC_CROSSCHECK_FAILED` |
| Emission | 승인 manifest hash에 결합된 발행 승인과 history anchor | `CONTRACT_EMISSION_NOT_APPROVED`, `EMISSION_AUTHORIZATION_TARGET_MISMATCH` |

## H04 out-of-band trust boundary

`ACTUAL_REVIEW`의 분류와 승인 상태는 review payload 자체만으로 발행 후보가 될 수 없다. `assess_issuance`는 별도 함수 인자 또는 CLI의 별도 `--trusted-anchor` 파일로 전달된 out-of-band anchor를 요구하며, payload 내부의 `trusted_anchor` 복제본은 신뢰하지 않는다.

anchor는 `evidence_class`를 포함한 전체 review payload의 canonical SHA-256와 함께 provider record hash/job reference, rights snapshot ID/scope hash, raw manifest hash/bundle hash/storage generation, scientific crosscheck result hash, emission authorization target hash를 exact match로 결속한다. 누락은 `ISSUANCE_TRUST_ANCHOR_MISSING`, anchor 메타데이터 결함은 `ISSUANCE_TRUST_ANCHOR_INVALID`, payload 내부 복제는 `ISSUANCE_TRUST_ANCHOR_IN_PAYLOAD`, 일반 target 불일치는 `ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH`, rights 불일치는 `ISSUANCE_TRUST_ANCHOR_RIGHTS_MISMATCH`로 `HOLD_NOT_ISSUED` 처리한다.

별도 anchor가 있다는 사실만으로 contract를 발행하지 않는다. 기존 provider·rights·storage·manifest·artifact·model·crosscheck·emission gate도 모두 통과해야 하며 결과는 여전히 발행 전 `ISSUABLE_CANDIDATE`일 뿐이다.

## H05 authenticated issuance root fail-closed

H04의 별도 JSON anchor는 binding 설명일 뿐 인증된 trust root가 아니다. 공격자가 review와 anchor를 함께 만들면 모든 identity/hash, anchor ID, approver와 history를 자기 일관되게 구성할 수 있다. 따라서 현재 production path는 exact-match JSON anchor에도 `ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED`를 추가하고 모든 `ACTUAL_REVIEW`를 `HOLD_NOT_ISSUED`로 닫는다.

향후 성공 경로에는 deployment가 소유한 KMS signature/public-key 검증 또는 immutable trust store 조회가 필요하다. verifier는 신뢰한 key/version 또는 trust-store identity, 검증된 signature/record identity, 검증 대상 canonical review hash를 반환해야 하며 plain payload나 anchor의 `APPROVED` 자기 선언을 인증 결과로 사용해서는 안 된다. 현재 production 함수에는 그러한 authenticator가 구현·주입되지 않았고 mock verifier 성공 경로도 없다.

## H06 deployment-owned issuance trust store

H06는 H04 anchor를 request와 분리된 deployment configuration의 allowlist entry에 exact binding한다. 기본 `assess_issuance(evidence, trusted_anchor=...)`와 `--trusted-anchor` 단독 경로는 H05와 동일하게 `ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED/HOLD_NOT_ISSUED`다. 후보 경로에는 다음 두 단계가 모두 필요하다.

1. deployment loader가 JSON document를 canonical string으로 복사한 frozen `DeploymentTrustStoreSnapshot`을 만든다. request payload의 `trusted_anchor`, trust-store object/path와 allowlist는 `ISSUANCE_TRUST_STORE_IN_PAYLOAD`로 거부하며 raw mutable dict를 deployment snapshot으로 받지 않는다.
2. gate가 store schema·snapshot ID·self hash·audience·scope·immutable flag와 모든 entry를 검증하고, 선택된 anchor의 exact ID·canonical digest·approver·evidence class·활성 기간·revocation을 확인한다.

store snapshot hash는 `snapshot_hash` 필드를 제외한 전체 document의 canonical JSON SHA-256다. anchor digest는 허용된 H04 anchor 필드 전체의 canonical JSON SHA-256이며 unknown field를 허용하지 않는다. 중복 anchor ID·digest, 알 수 없는 anchor, digest·approver·scope·classification 불일치, stale/not-yet-active·revoked entry, snapshot 변경과 과거 anchor replay는 각각 stable trust-store code로 `HOLD_NOT_ISSUED` 처리한다.

exact-match test fixture만 `ISSUABLE_CANDIDATE`에 도달한다. 이 결과도 `assurance_decision=HOLD`, `normalized_environment=null`이며 contract·dose를 발행하지 않는다. 이 allowlist는 cryptographic signature, KMS/IAM 배포나 과학적 교차검산을 대신하지 않으며 실제 private review에는 deployment trust store를 구성하지 않는다.

## Candidate와 approved manifest 분리

- `local-evidence-manifest.json`: 실제 local tracking v1, consumer eligibility `NOT_ELIGIBLE`.
- 향후 `raw-manifest-v2-candidate.json`: schema-valid 후보일 수 있으나 승인 전 consumer eligibility `NOT_ELIGIBLE`.
- 승인 `RAW_ARTIFACT_MANIFEST v2`: immutable storage generation, active rights snapshot, validation/reviewer와 history anchor가 모두 실제로 존재하고 승인된 경우만 consumer eligibility `ELIGIBLE_CANDIDATE`.

현재 local filesystem의 path, mtime 또는 파일명은 cloud/object generation이나 승인 storage identity를 대신하지 않는다. placeholder generation, provider reference, approver 또는 hash를 만들지 않는다.

## 과학적 교차검산 사전 프로토콜

### 목적

SPENVIS chain의 수치가 다른 도구와 같음을 증명하는 것이 아니라, 동일하게 맞출 수 있는 입력과 모델·transport·geometry 차이로 달라질 입력을 구분하고 예상 밖 차이를 독립 검토하는 것이다.

### 비교 후보

1. **Trapped environment component:** AP-8/AE-8 또는 별도 승인된 trapped model run과 AE9/AP9 결과의 범위·형태 비교.
2. **Mission shielding/dose chain:** OLTARIS 또는 독립 승인 transport 계산과 SPENVIS SHIELDOSE-2의 범위·경향 비교.

비교 도구의 계정·사용권·입출력 provenance가 승인되지 않으면 실행하지 않는다.

### 가능한 한 동일하게 고정할 입력

- Earth circular LEO, altitude, inclination, start/end와 duration
- target material
- Al material과 1/2/3/4 mm discrete shielding points
- trapped/solar component 포함 범위
- 출력 단위와 mission/component dose scope

### 동일하지 않을 수 있어 반드시 기록할 항목

- trapped/solar model family와 solar-cycle/confidence 정의
- transport engine, nuclear/particle interaction treatment
- spherical/slab 또는 ray-distribution geometry
- material composition과 thickness conversion
- energy grid, cut-off, interpolation과 numerical defaults

### 비교 산출물

- source component coverage와 누락 여부
- 네 shielding point의 순서와 차폐 증가에 따른 방향성
- 단위·target·mission scope 일치 여부
- 모델별 결과 차이의 부호와 패턴

실제 dose 값과 차이는 private 검토 기록에만 둔다.

### 판정 규칙

- 단위·target·mission scope·source coverage·shielding sequence가 다르면 즉시 `SCIENTIFIC_CROSSCHECK_FAILED`다.
- 차폐가 증가했는데 같은 조건의 dose가 증가하는 등 사전 물리 기대와 반대인 결과는 전문 검토 전 실패다.
- 모델·transport·geometry가 다른 도구 사이에 임의의 숫자 일치 tolerance를 만들지 않는다.
- 허용 오차는 비교 도구의 공식 validation 자료 또는 자격 있는 독립 reviewer가 H03 결과를 보기 전에 승인해야 한다.
- 승인된 tolerance와 reviewer가 없으면 결과를 실행했더라도 `SCIENTIFIC_CROSSCHECK_NOT_EVALUATED`다.

현재 이 protocol은 `DRAFT_BEFORE_RESULTS`다. 승인된 비교 기준, 독립 reviewer와 허용 오차가 없으므로 실제 crosscheck를 실행하거나 PASS를 선언하지 않는다.

## CONTRACT_CHANGE_REQUEST

공용 schema는 이번 Workstream에서 수정하지 않는다. Control Tower와 Workstream 10에 다음 변경을 요청한다.

### CCR-ENV-H03-01 — action vocabulary

`raw-artifact-manifest-v2.schema.json`의 action enum에는 `PROCESS_LOCAL`, `COMMERCIAL_USE`, `AUTOMATION`, `CLOUD_STORE`가 없다. 기존 `PROCESS_DOCUMENT_AI`·`PROCESS_VERTEX_AI`는 로컬 처리나 일반 자동화 권리를 대신하지 않는다.

요청:

- 위 4개 action을 공용 vocabulary에 추가하거나, versioned rights-action registry reference를 도입한다.
- action별 subject, approver, source locator/location, scope hash, valid_from/until을 강제한다.
- 기존 v2 consumer는 새 action을 모르는 경우 PASS가 아니라 `REQUIRED_ACTION_SET_INCOMPLETE/HOLD`로 닫는다.

### CCR-ENV-H03-02 — issuance evidence binding

현재 `RADIATION_ENVIRONMENT`와 raw manifest v2만으로는 provider reference의 검증 상태, scientific crosscheck protocol/result와 최종 emission authorization을 명시적으로 결합하기 어렵다.

요청 필드 또는 별도 versioned issuance envelope:

- `provider_reference_verification {status, source_locator, source_location, record_hash}`
- `scientific_crosscheck {status, protocol_hash, criteria_source, reviewer, result_hash}`
- `emission_authorization {status, approval_target_hash, approver, history_anchor_ref}`
- `consumer_eligibility: NOT_ELIGIBLE | ELIGIBLE_CANDIDATE`

필수 공격 fixture:

- missing/forged provider reference
- missing/expired/wrong-scope rights grant
- generation, bundle hash와 rights binding mismatch
- model/version drift
- crosscheck missing/failed/post-result protocol
- emission status 또는 approval target 변조

호환 영향:

- 기존 v1/v2 packet은 소급 변경하지 않는다.
- 새 envelope가 없으면 실제 external evidence contract는 fail-closed `HOLD_NOT_ISSUED`다.
- 합성 fixture는 `SYNTHETIC_CONTROL_ONLY`로 분리하고 실제 consumer eligibility를 얻지 못한다.
