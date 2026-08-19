# SPECTRA Stage 0 공통 계약 v1

## 목적과 범위

이 계약은 Stage 1 합성 Vertical Slice와 이후 실제 방사선 증거가 같은 필드 구조를 사용하되, 데이터의 성격과 증거 적합성을 숨기지 않도록 한다. 이 계약은 비행 적합성 인증이나 실제 방사선 시험을 대체하지 않는다. 숫자 계산과 최종 게이트는 결정론적 코드가 수행하며 LLM 설명은 `decision`을 변경할 수 없다.

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
- `RADIATION_ENVIRONMENT`: 모델명·버전, 임무 연결, TID와 입자 플럭스
- `PART_TEST_EVIDENCE`: 시험 부품 식별자, TID·SEU·SEL·SEB·SEGR 유형, 조건과 범위
- `SHIELDING`: 재료, 등가 두께와 적용 부품
- `MITIGATION`: 완화 방법, 대상 고장 유형, 파라미터와 근거
- `USER_POLICY`: TID 설계 계수, 잔여 SEU 한도, 파괴성 SEE 요구와 승인

`trace[]`는 `input_pointer → origin_pointer → normalized_value → applicability → decision_rule_ids`를 연결한다. `decision.rule_results`는 trace ID와 동일한 rule ID를 역참조하고, `decision.evidence_gaps`는 누락 증거와 차단 여부를 기록한다. 깨진 JSON Pointer나 rule/trace 참조는 의미 검증에서 거부한다.

모든 `trace_id`와 모든 `decision.rule_results[].rule_id`는 각각 패킷 안에서 유일해야 한다. 중복 ID는 지원 판정 여부와 관계없이 EvidencePacket 전체 무결성 실패다.

각 `rule_result.trace_ids`에는 최소 하나의 trace ID가 있어야 한다. 참조한 모든 trace는 패킷에 실제로 존재하고, 각 trace의 `decision_rule_ids`가 해당 `rule_result.rule_id`를 직접 포함해야 한다. 패킷의 다른 trace에 같은 rule ID가 있다는 사실은 이 연결을 대신하지 못한다. `SUPPORTED_WITH_MITIGATION`에서는 각 `PASS` rule result가 직접 참조한 trace 중 최소 하나가 `used_for_decision: true`여야 하며, 무관한 decision trace로 이를 우회할 수 없다.

`SUPPORTED_WITH_MITIGATION`에서는 `used_for_decision: true`인 모든 trace와 지원 규칙이 참조한 모든 trace의 `applicability.status`가 `APPLICABLE`이어야 한다. `NOT_APPLICABLE`과 `UNRESOLVED`는 지원 근거가 아니며 `DECISION_TRACE_NOT_APPLICABLE`로 차단한다.

`origin_pointer`는 `input_pointer` 대상의 metadata 또는 그 대상의 조상 입력 레코드 metadata에 있는 실제 `source`/`calculation_run`만 가리킬 수 있다. provenance 객체의 내용이나 실행 ID가 같아도 형제 필드나 다른 입력 경로는 원본 연결로 인정하지 않는다. 깨진 pointer는 `BROKEN_TRACE_POINTER`, 존재하지만 허용된 조상 연결이 아닌 origin은 `UNRELATED_TRACE_ORIGIN`으로 거부한다.

## 단위와 변환

| 물리량 | 허용 단위 | 정규 단위 |
|---|---|---|
| TID | `rad(Si)`, `krad(Si)`, `Gy(Si)` | `rad(Si)` 또는 명시된 계산 단위 |
| 차폐 | `mm_Al_equivalent`, `g/cm2` | 모델 계약이 선택한 하나 |
| 기간 | `s`, `day`, `year` | `s` |
| 입자 플럭스 | `particles/cm2/s` | 동일 |
| 단면적 | `cm2/device`, `cm2/bit` | bit/device 기준을 보존 |

결정론적 변환 상수는 `1 krad(Si) = 1000 rad(Si)`, `1 Gy(Si) = 100 rad(Si)`, `1 day = 86400 s`다. `year`는 달력 기간과 고정 초 환산이 다르므로 계산 실행이 선택한 정의와 버전을 기록해야 한다. `mm_Al_equivalent ↔ g/cm2`는 재료 밀도와 형상 가정 없이는 자동 변환하지 않는다. `cm2/device ↔ cm2/bit`는 유효 bit 수 없이는 변환하지 않는다. 호환되지 않는 단위는 `INVALID_INPUT`; 지원하지 않는 물리 모델 입력은 `OUT_OF_MODEL_SCOPE`다.

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
