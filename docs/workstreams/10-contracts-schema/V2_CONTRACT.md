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

### Runtime contract `1.0.0`

TMR, watchdog, SEL protection은 `contract_version: 2.0.0`에 더해 `runtime_contract_version: 1.0.0`을 요구한다. 이 세 method는 `effect_model`, `verification_evidence_ids`, method별 `runtime_projection`이 모두 있어야 계산 가능한 입력이다. `effect_model.equation_id`는 각각 다음 값으로 고정한다.

| Method | Equation ID | Projection semantic |
|---|---|---|
| `WATCHDOG` | `WATCHDOG_TRUE_FALSE_PATH_V1` | true target/activation, false activation, reboot와 downtime |
| `TMR` | `TMR_3P2_MINUS_2P3_V1` | `system_failure_probability` |
| `SEL_PROTECTION` | `SEL_TRUE_FALSE_PATH_V1` | true SEL/false trip, power cycle와 downtime |

runtime contract가 없는 기존 ECC v2 payload는 계속 허용한다. 하지만 TMR/watchdog/SEL protection은 H06 runtime field 없이 구조-valid 또는 계산 가능하다고 간주하지 않는다. equation이나 evidence가 없으면 임의 효과율로 대체하지 않고 `NOT_EVALUATED/HOLD`다.

#### Watchdog exact projection

- `target_event_model.event_count`는 평가 window 안의 검출 전 target event 수다. 이미 검출된 activation 수가 아니다.
- count 입력은 `event_count`, rate 입력은 `event_rate_per_second` 중 정확히 하나다. rate는 `rate × denominator.count × evaluation_window.duration_seconds`로 count에 정규화한다.
- `true_positive_activation_count = true_target_event_count × true_positive_coverage`다.
- false path는 `false_positive_model.activation_count` 또는 `activation_rate_per_second` 중 정확히 하나를 독립적으로 사용한다. 검증된 명시적 0만 0으로 인정한다.
- 두 model의 denominator scope는 `evaluation_window.denominator_scope`와 같아야 한다.
- true와 false의 각 `action_paths[].fraction` 합은 각각 정확히 1이다.
- `action_paths[].duration_seconds`는 reset/boot/self-test/restore를 포함한 **검출 후 action downtime**이며 detection latency를 포함하지 않는다. `action_duration_semantic`은 `POST_DETECTION_ACTION_ONLY`다.
- true path downtime은 `activation × fraction × (detection_latency_seconds + duration_seconds)`, false path downtime은 target detection latency 없이 `activation × fraction × duration_seconds`다.
- reboot와 downtime total은 true/false path를 모두 합한다. 따라서 `N_target=0`, `N_false=1`, false path `REBOOT`, duration `60 s`는 유일하게 `reboot_count_total=1`, `downtime_total_seconds=60`을 만든다.

#### TMR limited formula

제한식은 다음 조건이 모두 참일 때만 실행한다.

- replica count가 3이고 `p`가 같은 evaluation window의 repair 전 단일 replica failure probability다.
- `independence_verified=true`다.
- voter model이 존재하고 `susceptible=false`다.
- common-mode model이 존재하고 `probability=0`이다.
- evaluation window와 repair model이 존재하고 `repair_within_window=false`다.
- output semantic이 정확히 `system_failure_probability`다.

이때만 `3p²-2p³`을 사용한다. 기준 경계는 `p=0 → 0`, `p=0.1 → 0.028`, `p=1 → 1`이다. voter susceptibility 또는 nonzero common mode가 있으면 더 일반적인 state model이 필요하므로 제한식을 실행하지 않는다. 출력값을 success probability, reliability 또는 availability로 바꾸지 않는다.

#### SEL protection exact projection

- `true_sel_model`과 `false_trip_model`은 count/rate, denominator와 action fraction을 독립적으로 가진다. false trip 누락을 0으로 간주하지 않는다.
- SEL action path에는 duration field를 두지 않는다. `duration_semantic`은 `TRIP_OFF_RESTART_FIELDS_ONLY`이며 power-cycle 1회의 downtime은 `trip_delay_seconds + off_time_seconds + restart_time_seconds`다.
- `power_cycle_count_total`과 `downtime_total_seconds`는 true SEL과 false trip의 power-cycle path를 모두 합한다. phase time을 action path에 다시 더하면 이중 계산이다.
- prompt failure, latent damage, post-test electrical evidence가 모두 있어야 protection effect를 평가할 수 있다.
- SEL protection의 허용 target은 `SEL`뿐이다. `SEB` 또는 `SEGR` evidence gap을 닫지 않는다.

## USER_POLICY v2

Policy는 immutable `policy_id + policy_version + policy_content_hash`로 식별한다. scope는 tenant, mission, component와 `scope_hash`를 고정하며 approval은 정확한 content hash와 scope hash를 가리킨다. 승인 상태, 유효 기간, 철회·대체 상태와 immutable history anchor는 서로 분리한다.

`APPROVED` 문자열만으로 synthetic/assumed policy가 증거성 정책이 되지 않는다. 낙관 판정에는 승인 target/scope 일치, 유효 기간, 미철회 상태와 evidentiary provenance가 모두 필요하다.

### Canonical policy hash contract `1.0.0`

Runtime 소비 policy는 `hash_contract_version: 1.0.0`을 사용한다. canonical JSON은 UTF-8, key lexicographic sort, insignificant whitespace 없음, separator `,`/`:`, UTF-8 문자를 ASCII escape하지 않는 JSON으로 직렬화한다. 숫자는 JSON finite number만 허용하고 hash는 직렬화 bytes의 SHA-256을 `sha256:<64 lowercase hex>`로 기록한다. Python 기준 표현은 `json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))`다.

검증 순서는 다음과 같다.

1. Scope projection을 `{component_ids: sorted, mission_ids: sorted, tenant_id}`로 만들고 SHA-256을 계산한다.
2. 계산 scope hash를 `scope.scope_hash`와 비교한다.
3. Content projection을 `{contract_version, policy_id, policy_version, rules, scope_hash}`로 만든다. `required_destructive_modes`는 정렬하고 approval, metadata, 저장 hash 자체와 history reference는 self-reference를 피하기 위해 제외한다.
4. content projection SHA-256을 `policy_content_hash`와 비교한다.
5. `approval.approval_scope_hash`를 계산 scope hash와, `approval.approval_target_hash`를 계산 content hash와 비교한다.
6. `approval.history_head_hash`를 `immutable_history_ref.head_hash`와 비교한다.
7. packet mission과 mitigation component가 scope 안에 있는지 확인한 뒤 status, validity, expiry, revocation을 검사한다.
8. 마지막으로 policy provenance를 검사한다. 따라서 canonical hash와 `APPROVED` 형식이 맞아도 synthetic policy는 `HOLD`다.

기존 H05/Workstream 20의 DRAFT 비교 policy는 hash contract가 없어도 legacy 구조로 읽을 수 있다. 그러나 `APPROVED` policy를 optimistic assurance에 사용할 때 hash contract가 없으면 `POLICY_HASH_CONTRACT_MISSING`으로 거부한다.

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
- runtime projection: `ACTIVATION_COUNT_RATE_CONFLICT`, `RECOVERY_DENOMINATOR_WINDOW_MISMATCH`, `ACTION_PATH_FRACTION_INVALID`, `WATCHDOG_FALSE_POSITIVE_IGNORED`, `WATCHDOG_DETECTION_LATENCY_DOUBLE_COUNTED`, `SEL_DURATION_DOUBLE_COUNTED`
- TMR eligibility: `TMR_VOTER_SUSCEPTIBLE`, `TMR_COMMON_MODE_NONZERO`, `TMR_REPAIR_WINDOW_MISMATCH`, `TMR_RUNTIME_PROJECTION_MISMATCH`
- effect/policy: `MITIGATION_EFFECT_MODEL_MISSING`, `MITIGATION_EQUATION_ID_MISSING`, `MITIGATION_EFFECT_EVIDENCE_MISSING`, `POLICY_CONTENT_HASH_MISMATCH`, `POLICY_SCOPE_HASH_MISMATCH`, `POLICY_EXPIRED`, `POLICY_REVOKED`
- malformed runtime/policy: `MALFORMED_MITIGATION_PARAMETERS`, `MALFORMED_ACTION_PATH`, `MALFORMED_POLICY_SCOPE`, `MALFORMED_POLICY_RULES`, `MALFORMED_POLICY_APPROVAL`, `MALFORMED_POLICY_HISTORY`, `MALFORMED_DESTRUCTIVE_MODES`
- raw identity: `RAW_OVERWRITE_PRECONDITION_MISSING`, `RAW_GENERATION_MISSING`, `RAW_GENERATION_MISMATCH`, `RAW_ARTIFACT_HASH_MISMATCH`, `RAW_MANIFEST_TENANT_MISMATCH`, `RAW_MANIFEST_ZONE_MISMATCH`
- rights/reference: `RAW_RIGHTS_SNAPSHOT_MISMATCH`, `RIGHTS_ACTION_GRANT_MISSING`, `RIGHTS_SNAPSHOT_NOT_ACTIVE`, `RAW_MANIFEST_REFERENCE_MISSING`

이 오류는 처리 결과를 support로 바꾸지 않는다. 실제 근거가 없는 정상 v2 fixture도 `processing_status=VALID`, `assurance_decision=HOLD`, blocking evidence gap을 유지한다.

JSON Schema 오류가 먼저 발견되더라도 semantic gate는 같은 packet에서 계속 오류 코드를 수집한다. 따라서 runtime `design_parameters`, policy `scope`/`rules`/`approval`/`immutable_history_ref`, action path item과 policy ID/mode 배열은 사용 전에 컨테이너 타입을 확인한다. malformed 값을 산술, `.get()`, `sorted()` 또는 `set()`에 넘기지 않으며 broad exception fallback도 사용하지 않는다.

## 소비 Workstream migration

- Workstream 20은 기존 v1 합성 시뮬레이션을 계속 사용할 수 있다. v1.1을 소비할 때는 method별 typed operand와 packet에 고정된 exact raw reference만 읽고, 배열 순서나 v1 필드 fallback으로 계산하지 않는다.
- Workstream 60은 Workstream 50이 정의한 29개 계산/공격 fixture와 Workstream 70 IAM 공격을 소유한다. 특히 watchdog true/false path 합산, TMR 경계 계산, destructive mode 대체 공격, 권리 철회·tenant isolation·generation race를 같은 target code로 검증해야 한다.
- Workstream 70은 manifest에 기록된 값을 실제 storage/IAM 상태에서 생성·검증해야 한다. 이 schema 검증만으로 object 존재, malware scanner 신뢰성, 승인자 권한 또는 실제 권리를 증명할 수 없다.

## 알려진 한계

- 이 패키지는 계산 엔진과 GCP resource/IAM을 구현하지 않는다.
- immutable history와 cloud generation은 참조 구조와 일치만 검사한다. 외부 저장소의 실제 불변성·존재 여부는 소비 시스템 검증이 필요하다.
- v1.1도 required input kind는 각각 정확히 하나다. 복수 evidence/policy 집계는 향후 별도 schema version과 명시 record selection이 필요하다.
