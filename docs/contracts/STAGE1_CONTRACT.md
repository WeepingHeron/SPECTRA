# SPECTRA Stage 1 공통 계약 v1

## 목적과 범위

이 계약은 Stage 2 합성 Vertical Slice와 이후 실제 방사선 증거가 같은 필드 구조를 사용하되, 데이터의 성격과 증거 적합성을 숨기지 않도록 한다. 이 계약은 비행 적합성 인증이나 실제 방사선 시험을 대체하지 않는다. 숫자 계산과 최종 게이트는 결정론적 코드가 수행하며 LLM 설명은 `decision`을 변경할 수 없다.

기계 계약의 기준 파일은 `schemas/*.schema.json`, 의미 규칙의 기준 구현은 `tests/schema/validate_contracts.py`다.

## 서로 섞지 않는 세 상태축

| 축 | 필드 | 값 | 의미 |
|---|---|---|---|
| 작업 검토 | `review_status` | `NOT_STARTED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `VERIFIED`, `INTEGRATED`, `CHANGES_REQUESTED`, `HOLD` | 산출물의 작업·독립 검토 단계 |
| 방사선 보증 | `decision.assurance_decision` | `SUPPORTED_WITH_MITIGATION`, `CONDITIONAL`, `HOLD`, `INSUFFICIENT_EVIDENCE` | 유효 증거와 정책에 따른 보증 결론 |
| 처리·범위 | `decision.processing_status` | `VALID`, `INVALID_INPUT`, `OUT_OF_MODEL_SCOPE`, `MODEL_FAILURE`, `STALE_EVIDENCE`, `PROVENANCE_FAILURE`, `CONFLICTING_EVIDENCE` | 입력·계산·증거 처리 가능 여부 |

`HOLD`라는 문자열이 작업 상태와 보증 판정 양쪽에 존재해도 필드와 의미가 다르다. 처리 상태에는 `HOLD`를 쓰지 않는다. `OUT_OF_MODEL_SCOPE`는 “지원 모델이 이 입력을 계산할 수 없음”이고, `INSUFFICIENT_EVIDENCE`는 “입력 처리는 가능했으나 보증에 필요한 증거가 부족함”이다. 전자는 처리 상태, 후자는 보증 판정이다.

처리 상태가 `VALID`가 아니면 보증 판정은 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`만 가능하다. 특히 `OUT_OF_MODEL_SCOPE`, `MODEL_FAILURE`, `STALE_EVIDENCE`는 지원 판정의 대체값이 아니며 `SUPPORTED_WITH_MITIGATION`으로 승격할 수 없다.

## 데이터 분류와 provenance

| `data_class` | 사용 조건 | 필수 origin |
|---|---|---|
| `PUBLISHED` | 외부 원문에서 확인한 값 | `source` |
| `CALCULATED` | 고정 입력·엔진으로 재현 가능한 값 | `calculation_run` |
| `ASSUMED` | 사용자·연구자가 명시한 가정 | `source`와 비어 있지 않은 `assumptions` |
| `SYNTHETIC` | 데모·fixture·시험 전용 값 | `calculation_run` |
| `CUSTOMER_VERIFIED` | 고객 자료와 승인 절차로 확인한 값 | `source` |

모든 record metadata는 `version`, `created_at`, `content_hash`, `review_status`를 가진다. `source`에는 원문 URI와 페이지·표·셀 등 `location`이 필요하다. 계산값은 엔진·버전·입출력 해시·실행시각을 가진 `calculation_run`으로 재현 경계를 고정한다. 한 metadata에서 `source`와 `calculation_run`을 동시에 origin으로 사용하지 않는다.

실제값과 합성값은 패킷 안에 함께 있을 수 있으나 각 값의 metadata에서 식별돼야 한다. `SYNTHETIC` 또는 `ASSUMED` 값을 최종 지원 판정의 결정 입력으로 쓰는 경우 검증기는 거부한다. fixture 원문을 `PUBLISHED`로 바꿔 표시하는 경우도 `SYNTHETIC_MISREPRESENTED`로 거부한다.

정규화 결과의 `data_class`는 원본 분류를 덮어쓰지 않는다. `used_for_decision: true` trace는 `input_pointer`를 실제 패킷에서 해석하고, 그 대상 자체 또는 가장 가까운 조상 입력 레코드의 metadata에서 원본 `data_class`를 확인한다. 원본이 `SYNTHETIC` 또는 `ASSUMED`이면 정규화 결과가 `CALCULATED`여도 `SUPPORTED_WITH_MITIGATION`에 사용할 수 없다.

## 입력과 EvidencePacket 연결

EvidencePacket은 다음 7개 입력을 최소 한 개씩 포함한다.

- `MISSION`: LEO 임무, 고도, 경사각, 시작시점, 기간
- `BOM`: 제조사·정확한 부품번호와 가능한 공정·다이·로트 식별자
- `RADIATION_ENVIRONMENT`: 기존 TID+flux payload 또는 provenance가 완비된 `TID_ONLY` payload
- `PART_TEST_EVIDENCE`: 시험 부품 식별자, TID·SEU·SEL·SEB·SEGR 유형, 조건과 범위
- `SHIELDING`: 재료, 등가 두께와 적용 부품
- `MITIGATION`: 완화 방법, 대상 고장 유형, 파라미터와 근거
- `USER_POLICY`: TID 설계 계수, 잔여 SEU 한도, 파괴성 SEE 요구와 승인

EvidencePacket v1에서는 위 7개 required kind를 각각 정확히 하나만 허용한다. JSON Schema는 각 `contains`에 `minContains: 1`, `maxContains: 1`을 적용하고 의미 gate도 중복 kind를 `DUPLICATE_REQUIRED_INPUT_KIND`로 거부한다. 이는 현재 계산기가 같은 kind의 첫 레코드를 암묵적으로 소비하는 동안 operand binding이 다른 중복 레코드를 가리키는 shadowing을 막는 v1 경계다. 향후 복수 evidence 또는 policy가 필요하면 별도 schema version에서 명시 ID로 계산 소비 레코드와 binding 대상이 동일함을 보장해야 하며 first-item 선택을 재사용하지 않는다.

`trace[]`는 `input_pointer → origin_pointer → normalized_value → applicability → decision_rule_ids`를 연결한다. `decision.rule_results`는 trace ID와 동일한 rule ID를 역참조하고, `decision.evidence_gaps`는 누락 증거와 차단 여부를 기록한다. 깨진 JSON Pointer나 rule/trace 참조는 의미 검증에서 거부한다.

모든 `trace_id`와 모든 `decision.rule_results[].rule_id`는 각각 패킷 안에서 유일해야 한다. 중복 ID는 지원 판정 여부와 관계없이 EvidencePacket 전체 무결성 실패다.

각 `rule_result.trace_ids`에는 최소 하나의 trace ID가 있어야 한다. 참조한 모든 trace는 패킷에 실제로 존재하고, 각 trace의 `decision_rule_ids`가 해당 `rule_result.rule_id`를 직접 포함해야 한다. 패킷의 다른 trace에 같은 rule ID가 있다는 사실은 이 연결을 대신하지 못한다. `SUPPORTED_WITH_MITIGATION`에서는 각 `PASS` rule result가 직접 참조한 trace 중 최소 하나가 `used_for_decision: true`여야 하며, 무관한 decision trace로 이를 우회할 수 없다.

`trace_ids`는 판정 결과의 주 trace를 연결하지만 규칙의 모든 계산 피연산자를 대신하지 않는다. optimistic `PASS` rule result는 `operand_bindings[]`에 `operand_role`, 실제 `input_pointer`, 해당 입력의 `origin_pointer`를 기록해야 한다. 알려지지 않은 규칙은 operand contract가 정의되기 전까지 지원 판정에 사용할 수 없다.

`TID_MARGIN_V1`의 필수 operand role은 다음 여섯 개다.

- `MISSION_DOSE`: TID-only environment의 `mission_dose`
- `PART_TID_LIMIT`: part-test evidence의 `tid_test_limit`
- `TID_DESIGN_FACTOR`: user policy의 `tid_design_factor`
- `POLICY_APPROVAL`: 동일 user policy의 `approval_status`
- `SHIELDING_THICKNESS`: shielding 입력의 `equivalent_thickness`
- `MISSION_DURATION`: mission 입력의 `duration`

역할 이름만 맞추고 무관한 입력을 가리키는 것을 막기 위해 각 role은 입력 kind와 상대 경로까지 결정론적으로 검증한다. pointer 존재 여부, 허용된 조상 provenance origin, leaf metadata와 소유 input record metadata의 데이터 분류를 모두 확인한다. 필수 role 누락은 `RULE_OPERAND_TRACE_MISSING`, 합성·가정 operand는 `NON_EVIDENTIARY_RULE_OPERAND`, 합성 policy를 `APPROVED` 문자열만으로 승격하는 경우는 `SYNTHETIC_POLICY_WITH_SUPPORT`로 거부한다.

`SUPPORTED_WITH_MITIGATION`에서는 `used_for_decision: true`인 모든 trace와 지원 규칙이 참조한 모든 trace의 `applicability.status`가 `APPLICABLE`이어야 한다. `NOT_APPLICABLE`과 `UNRESOLVED`는 지원 근거가 아니며 `DECISION_TRACE_NOT_APPLICABLE`로 차단한다.

`origin_pointer`는 `input_pointer` 대상의 metadata 또는 그 대상의 조상 입력 레코드 metadata에 있는 실제 `source`/`calculation_run`만 가리킬 수 있다. provenance 객체의 내용이나 실행 ID가 같아도 형제 필드나 다른 입력 경로는 원본 연결로 인정하지 않는다. 깨진 pointer는 `BROKEN_TRACE_POINTER`, 존재하지만 허용된 조상 연결이 아닌 origin은 `UNRELATED_TRACE_ORIGIN`으로 거부한다.

## TID-only 환경과 외부 실행 provenance

`RADIATION_ENVIRONMENT` v1.1은 기존 payload를 깨지 않는 additive extension이다. `environment_variant`가 없고 `tid`와 `particle_flux`가 있는 기존 v1 payload는 계속 검증된다. 새 경로는 `environment_variant: TID_ONLY`를 명시하고 `particle_flux`와 legacy `tid`를 금지한다. 따라서 의미 없는 0 flux나 placeholder flux로 필수 계약을 채우지 않는다.

`TID_ONLY`는 `run_id`, `mission_dose`, `dose_scope`, `target_material: SILICON`, `source_completeness`, `shielding_point`, `valid_for`, `model_chain`, `raw_artifact_manifest`, record metadata를 요구한다. `dose_scope: MISSION`은 `source_completeness: COMPLETE_MISSION`과 `model_chain.approved_scope: MISSION_TID_COMPLETE`일 때만 완전한 mission TID로 취급한다. trapped-only·solar 누락·partial 결과 자체는 research scope의 chain과 `dose_scope`·completeness로 표현할 수 있지만 mission dose로 허위 표시하면 `INCOMPLETE_MISSION_TID_SOURCE`, 지원 판정으로 승격하면 `INCOMPLETE_ENVIRONMENT_WITH_SUPPORT`로 거부한다. 이 경우 보증 판정은 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`를 유지하며 processing status에 `HOLD`를 추가하지 않는다.

`model_chain.stages[]`는 배열 위치가 아니라 `stage_id`, `role`, `depends_on`으로 연결된다. 역할은 `ORBIT`, `TRAPPED_ENVIRONMENT`, `SOLAR_ENVIRONMENT`, `TRANSPORT_DOSE`이고 각 단계는 model name, exact version, build, configuration reference 또는 SHA-256 중 정확히 하나를 가진다. `representative_stage_id`가 top-level `model_name`·`model_version`의 유일한 대표 stage를 정하고 두 값은 반드시 일치해야 한다. stage ID 중복, 없는 단계·자기 자신 참조, cycle, 역할별 dependency 위반, mission TID에 필요한 역할·승인 범위 누락은 fail-closed 오류다.

`raw_artifact_manifest`는 환경 결과와 동일한 `run_id`를 사용한다. environment metadata, mission dose metadata, manifest metadata의 calculation run ID도 모두 이 ID와 같아야 한다. 원본 파일마다 artifact ID, filename, media type, 양수 byte size, SHA-256, 역할, source location을 기록하며 실제 파일 자체는 이 계약 fixture에 포함하지 않는다. 현재 TID-only 외부 실행 경로는 `PROVIDER_OUTPUT` artifact를 최소 하나 요구하고, `NORMALIZED_OUTPUT`만으로 raw provenance를 충족할 수 없다. provider input·configuration·run log는 현재 v1.1에서는 선택적이며 후속 provider adapter가 더 엄격한 completeness policy를 추가할 수 있다. bundle SHA-256과 parser input SHA-256이 일치하고, parser output·mission dose content hash·mission dose calculation output hash도 모두 일치해야 한다. provider platform version/build와 job reference, 제출·완료·다운로드 시각, parser name/version/commit을 서로 다른 필드로 보존한다.

권리는 `research`, `commercial`, `automation`, `redistribution` 네 축에서 각각 `ALLOWED`, `PROHIBITED`, `UNCONFIRMED`, `NOT_APPLICABLE`로 기록한다. `usage_claims`가 true인 축뿐 아니라 시스템이 `execution_mode`와 `distribution_scope` 및 optimistic decision에서 도출한 필수 축도 명시적으로 `ALLOWED`여야 한다. 지원 판정은 항상 research 권리를 요구하고, 자동 실행은 automation, 외부 전달은 redistribution, 상용 제품은 commercial과 redistribution 권리를 추가로 요구한다. 따라서 `usage_claims: false`로 gate를 우회할 수 없다. 필요한 축의 `UNCONFIRMED`, `PROHIBITED`, 부적절한 `NOT_APPLICABLE`은 `REQUIRED_RIGHT_NOT_ALLOWED`이며, 안전한 종료는 `processing_status: PROVENANCE_FAILURE`와 assurance `HOLD`다. 제공 fixture의 플랫폼·job·파일·hash·수치는 모두 명백한 `SYNTHETIC` 형식 예시이며 실제 SPENVIS·OLTARIS 실행이나 권리 승인을 뜻하지 않는다.

optimistic assurance에서는 environment, mission dose, raw manifest와 decision trace의 provenance class를 각각 검증한다. 어느 하나라도 `SYNTHETIC` 또는 `ASSUMED`이면 지원 근거가 아니며 위치별 오류 코드로 거부한다. trace origin을 mission dose의 calculation run으로 바꿔도 상위 run identity와 output hash 검증은 독립적으로 수행되므로 모순을 숨길 수 없다.

## 단위와 변환

| 물리량 | 허용 단위 | 정규 단위 |
|---|---|---|
| TID | `rad(Si)`, `krad(Si)`, `Gy(Si)` | `rad(Si)` 또는 명시된 계산 단위 |
| 차폐 | `mm_Al_equivalent`, `g/cm2` | 모델 계약이 선택한 하나 |
| 기간 | `s`, `day`, `year` | `s` |
| 입자 플럭스 | `particles/cm2/s` | 동일 |
| 단면적 | `cm2/device`, `cm2/bit` | bit/device 기준을 보존 |

결정론적 변환 상수는 `1 krad(Si) = 1000 rad(Si)`, `1 Gy(Si) = 100 rad(Si)`, `1 day = 86400 s`다. `year`는 달력 기간과 고정 초 환산이 다르므로 계산 실행이 선택한 정의와 버전을 기록해야 한다. `mm_Al_equivalent ↔ g/cm2`는 재료 밀도와 형상 가정 없이는 자동 변환하지 않는다. `cm2/device ↔ cm2/bit`는 유효 bit 수 없이는 변환하지 않는다. 호환되지 않는 단위는 `INVALID_INPUT`; 지원하지 않는 물리 모델 입력은 `OUT_OF_MODEL_SCOPE`다.

TID와 particle flux는 0 이상이어야 하고 차폐 두께는 현재 지원 범위에서 0보다 커야 한다. `valid_for.start_at <= end_at`이며 외부 실행 시각은 `submitted_at <= completed_at <= downloaded_at` 순서를 만족해야 한다. 범위·순서 위반은 schema와 결정론적 의미 gate에서 낙관 판정 전에 차단한다.

## 판정과 실패 우선순위

다음 조건에서는 `SUPPORTED_WITH_MITIGATION`을 허용하지 않는다.

1. 처리 상태가 `VALID`가 아니다.
2. 핵심 결정값에 출처 또는 계산 실행, 버전, 해시가 없다.
3. 합성값 또는 가정값이 최종 결정 입력이다.
4. BOM과 시험 증거의 제조사·부품번호·공정·다이·로트·Date Code가 불일치한다.
5. TID 요구량이 확인된 시험 범위를 넘는다. 시험 범위 밖 외삽은 금지한다.
6. 정책이 요구하는 SEL·SEB·SEGR 중 파괴성 SEE 증거가 없다. SEU 또는 ECC 결과로 대체하지 않는다.
7. 사용자 정책이 `APPROVED`가 아니다.
8. 차단형 evidence gap, stale evidence, provenance failure 또는 상충 증거가 있다.
9. `used_for_decision: true`인 trace가 하나도 없다.
10. `decision.rule_results` 중 하나라도 `FAIL` 또는 `NOT_EVALUATED`다. 지원 판정의 모든 규칙 결과는 `PASS`여야 한다.
11. rule result의 `trace_ids`가 비어 있거나 존재하지 않는 trace를 가리킨다.
12. rule result의 rule ID와 직접 참조한 trace의 `decision_rule_ids`가 일치하지 않는다.
13. 지원 판정의 `PASS` rule result가 직접 연결된 decision trace를 하나도 갖지 않는다.
14. decision trace가 가리키는 원본 입력이 `SYNTHETIC` 또는 `ASSUMED`인데 정규화 결과만 `CALCULATED`로 재분류됐다.
15. `input_pointer` 또는 `origin_pointer`가 깨졌거나, origin이 해당 입력의 metadata·조상 metadata와 직접 연결되지 않는다.
16. 결정 trace 또는 지원 규칙이 참조한 trace의 적용성이 `NOT_APPLICABLE` 또는 `UNRESOLVED`다.
17. 패킷 안에서 `trace_id` 또는 rule result의 `rule_id`가 중복된다.
18. TID-only environment, mission dose, manifest 또는 decision trace가 합성·가정 provenance인데 지원 판정을 시도한다.
19. decision·execution·distribution scope가 요구하는 권리가 명시적으로 `ALLOWED`가 아니다.
20. TID·차폐 범위 또는 mission/provider timestamp 순서가 유효하지 않다.
21. top-level model과 대표 stage, run identity 또는 parser/dose output hash가 서로 모순된다.
22. 유효한 `PROVIDER_OUTPUT` raw artifact가 없다.
23. rule result가 필수 계산 operand를 모두 연결하지 않았거나 operand role과 실제 입력 경로가 다르다.
24. rule operand의 leaf 또는 소유 입력 record가 `SYNTHETIC`·`ASSUMED`다.
25. 합성 user policy의 `approval_status`만 `APPROVED`로 바꿔 지원 근거로 사용한다.
26. required input kind가 중복되어 실제 계산 레코드와 operand binding 레코드가 달라질 수 있다.

판정 우선순위는 처리 실패 차단 → provenance·식별자 검증 → 적용 범위 검증 → 파괴성 SEE gate → 승인 정책 평가 → 보증 판정 순서다. 실패 원인을 낙관 판정으로 치환하지 않는다.

## 검증 재현

현재 환경과 동일한 의존성은 다음처럼 설치할 수 있다.

```bash
python3 -m pip install -r tests/schema/requirements.txt
```

전체 계약은 한 명령으로 검증한다.

```bash
python3 tests/schema/validate_contracts.py
```

정상 fixture는 의도적으로 전부 `SYNTHETIC`이며 보증 판정은 `HOLD`다. 이 fixture의 숫자는 실제 환경값이나 부품 시험 결과가 아니다.
