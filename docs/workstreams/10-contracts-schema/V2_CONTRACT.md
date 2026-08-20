# Mitigation/Policy & Raw Artifact v2 Contract

## 목적과 버전 경계

이 계약은 Workstream 50 H02와 Workstream 70 H01의 검증된 설계를 공통 교환 형식에 반영한다. 실제 완화 효과 계산, 실제 정책 승인, 실제 cloud object 또는 권리 허가는 생성하지 않는다.

| EvidencePacket | MITIGATION | USER_POLICY | Raw manifest | 규칙 |
|---|---|---|---|---|
| `1.0.0` | v1 | v1 | v1 | 기존 fixture와 소비자를 그대로 지원한다. `raw_manifest_refs`는 금지한다. |
| `1.1.0` | `2.0.0` | `2.0.0` | `2.0.0` | 세 v2 계약을 함께 사용하고 `raw_manifest_refs`로 exact artifact revision을 연결한다. |

한 packet에서 v1/v2 mitigation·policy·manifest를 섞거나 같은 input kind를 shadowing하는 것은 허용하지 않는다. 자동 승격이나 암묵적 migration도 없다.

## MITIGATION v2

`method`는 discriminant이고 `design_parameters`는 method별 닫힌 typed object다. 공통 envelope는 component와 architecture scope, target/excluded failure mode, applicability, provenance를 요구한다.

- Watchdog와 SEL protection은 true activation과 false activation을 별도 model로 기록한다. 각 model은 count 또는 rate, denominator, action path와 검증 evidence를 가지며 공통 evaluation window에 묶인다. 누락값을 0으로 간주하지 않는다.
- TMR의 제한 출력은 같은 evaluation window의 `system_failure_probability`다. voter susceptibility, common-mode probability, independence와 window 내 repair 조건이 모두 명시돼야 한다. 이를 availability/reliability/success로 재표시할 수 없다.
- `SEL`, `SEB`, `SEGR`은 서로 다른 destructive mode다. policy가 요구한 각 mode는 part-test evidence에 직접 존재해야 하며 ECC, scrub, TMR 또는 recovery method로 대체하지 않는다.
- v1의 자유형 `parameters`와 `effectiveness_factor`는 v2로 자동 변환되지 않으며 v2 packet의 지원 근거로 사용할 수 없다.

## USER_POLICY v2

Policy는 immutable `policy_id + policy_version + policy_content_hash`로 식별한다. scope는 tenant, mission, component와 `scope_hash`를 고정하며 approval은 정확한 content hash와 scope hash를 가리킨다. 승인 상태, 유효 기간, 철회·대체 상태와 immutable history anchor는 서로 분리한다.

`APPROVED` 문자열만으로 synthetic/assumed policy가 증거성 정책이 되지 않는다. 낙관 판정에는 승인 target/scope 일치, 유효 기간, 미철회 상태와 evidentiary provenance가 모두 필요하다.

## RAW_ARTIFACT_MANIFEST v2

Manifest는 tenant/zone과 create-only precondition을 고정하고 artifact revision마다 다음을 요구한다.

- `project_id + bucket_id + object_name + generation`
- bytes에서 계산한 SHA-256, 양수 byte size, declared/detected MIME
- source locator와 retrieval time
- rights snapshot ID
- quarantine, malware, MIME, hash 검증 상태
- derived record lineage와 deletion state

Rights의 넓은 상태 문자열은 개별 action 허가가 아니다. `LOCATOR`, `FETCH`, `PRIVATE_STORE`, `PROCESS_DOCUMENT_AI`, `PROCESS_VERTEX_AI`, `DISPLAY_INTERNAL`, `DISPLAY_EXTERNAL`, `REDISTRIBUTE`는 각각 독립 grant이며 EvidencePacket이 요구한 action이 정확히 `ALLOWED`여야 한다. 미확인·금지·철회·만료 snapshot은 지원 판정에 사용할 수 없다.

EvidencePacket `raw_manifest_refs`는 manifest/artifact revision, tenant, zone, exact generation, SHA-256, rights snapshot, source locator와 claim locator를 복제해 고정한다. validator는 복제 필드가 실제 nested manifest와 모두 일치하는지 결정론적으로 확인한다.

## 실패 정책

구조 누락은 JSON Schema와 semantic target code 양쪽에서 가능한 범위까지 거부한다. 주요 코드는 다음과 같다.

- 버전/필수 필드: `CONTRACT_VERSION_MIXED`, `V2_REQUIRED_FIELD_MISSING`
- TMR/watchdog: `TMR_OUTPUT_SEMANTIC_MISMATCH`, `TMR_*_MISSING`, `WATCHDOG_FALSE_POSITIVE_MODEL_MISSING`
- raw identity: `RAW_OVERWRITE_PRECONDITION_MISSING`, `RAW_GENERATION_MISSING`, `RAW_GENERATION_MISMATCH`, `RAW_ARTIFACT_HASH_MISMATCH`, `RAW_MANIFEST_TENANT_MISMATCH`, `RAW_MANIFEST_ZONE_MISMATCH`
- rights/reference: `RAW_RIGHTS_SNAPSHOT_MISMATCH`, `RIGHTS_ACTION_GRANT_MISSING`, `RIGHTS_SNAPSHOT_NOT_ACTIVE`, `RAW_MANIFEST_REFERENCE_MISSING`

이 오류는 처리 결과를 support로 바꾸지 않는다. 실제 근거가 없는 정상 v2 fixture도 `processing_status=VALID`, `assurance_decision=HOLD`, blocking evidence gap을 유지한다.

## 소비 Workstream migration

- Workstream 20은 기존 v1 합성 시뮬레이션을 계속 사용할 수 있다. v1.1을 소비할 때는 method별 typed operand와 packet에 고정된 exact raw reference만 읽고, 배열 순서나 v1 필드 fallback으로 계산하지 않는다.
- Workstream 60은 Workstream 50이 정의한 29개 계산/공격 fixture와 Workstream 70 IAM 공격을 소유한다. 특히 watchdog true/false path 합산, TMR 경계 계산, destructive mode 대체 공격, 권리 철회·tenant isolation·generation race를 같은 target code로 검증해야 한다.
- Workstream 70은 manifest에 기록된 값을 실제 storage/IAM 상태에서 생성·검증해야 한다. 이 schema 검증만으로 object 존재, malware scanner 신뢰성, 승인자 권한 또는 실제 권리를 증명할 수 없다.

## 알려진 한계

- 이 패키지는 계산 엔진과 GCP resource/IAM을 구현하지 않는다.
- immutable history와 cloud generation은 참조 구조와 일치만 검사한다. 외부 저장소의 실제 불변성·존재 여부는 소비 시스템 검증이 필요하다.
- v1.1도 required input kind는 각각 정확히 하나다. 복수 evidence/policy 집계는 향후 별도 schema version과 명시 record selection이 필요하다.
