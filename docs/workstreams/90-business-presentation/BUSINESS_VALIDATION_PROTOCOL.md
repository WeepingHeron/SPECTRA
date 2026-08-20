# SPECTRA Business Validation Protocol

> Package: `90-business-validation-instrument-v1`
> Submission: `H03`
> Baseline: `main` / `4920b6e`
> Status ceiling: `READY_FOR_REVIEW`
> Current result state: all business hypotheses `UNVALIDATED`; price and pilot values `UNSET`

## 1. 목적과 사용 경계

이 문서는 SPECTRA의 사용자 문제, 현재 업무 기준선, 제품 가치, 구매 단위와 pilot 성공 조건을 실제 증거로 검증하기 위한 실행 도구다. 인터뷰 결과나 사업성을 미리 주장하는 문서가 아니다.

이 문서만으로 다음을 수행할 수 있어야 한다.

1. 실무 사용자·기술 승인자·구매자·데이터 권리 승인자를 구분한다.
2. 30분 이내에 최근 실제 사례 중심의 인터뷰를 진행한다.
3. 시간·비용·재작업을 단위·기간·분모·산정 방법·출처와 함께 기록한다.
4. 문제·가치·구매·pilot 가설과 실제 답변을 분리한다.
5. 증거가 없거나 사용할 수 없으면 결론을 `UNVALIDATED` 또는 `INSUFFICIENT_EVIDENCE`로 유지한다.

### 이 패키지가 증명하지 않는 것

- 실제 인터뷰 수행 또는 사용자 반응
- 방사선 적합성·부품 인증·과학 정확도
- 시간·비용 절감률, 가격, 구매 의사, 시장 규모
- 실제 고객 데이터, live GCP 또는 Multi-Agent E2E
- Stage 9 완료, MVP 완료 또는 checklist 완료

합성 Product UI는 인터뷰에서 workflow concept를 설명하는 보조 자료로만 쓸 수 있다. 프로토타입 조작 또는 내부 검증을 실제 사용자 가치 검증으로 승격하지 않는다.

## 2. 핵심 상태 체계

### 2.1 가설 상태

가설에는 다음 상태만 사용한다.

| 상태 | 사용 조건 |
|---|---|
| `UNVALIDATED` | 아직 유효한 외부 증거를 수집하지 않음. 현재 모든 가설의 기본값 |
| `PARTIALLY_SUPPORTED` | 관련 증거가 있으나 역할·상황·표본 범위 또는 corroboration 한계가 큼 |
| `SUPPORTED_WITH_LIMITS` | 직접적인 관련 증거가 둘 이상의 독립 출처 또는 역할에서 corroborate되고 적용 한계가 명시됨 |
| `CONTRADICTED` | 유효한 최근 사례나 구매·승인 증거가 가설의 핵심 예측과 반대됨 |
| `INSUFFICIENT_EVIDENCE` | 자료 누락, 출처 불명, 회상 불가, 단위·분모 결함, 권리 문제 또는 중대한 충돌로 판정 불가 |

인터뷰 건수만으로 상태를 올리지 않는다. 같은 조직·같은 사건·같은 문서를 반복 인용한 기록은 독립 corroboration으로 세지 않는다. 한 가설에 지지와 반대 증거가 공존하면 conflict를 남기고 적용 범위를 좁히거나 `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE` 중 증거에 맞는 상태를 선택한다.

### 2.2 Pilot 상태

| 상태 | 의미 |
|---|---|
| `UNSET` | 대상·범위·승인·측정 계약이 없음 |
| `PLANNED` | 시작 전 기준선, 범위, 책임자, 권리와 측정 방법이 승인됨 |
| `OBSERVED` | 승인된 pilot이 실행됐고 원자료 locator와 측정 결과가 존재함 |
| `INVALIDATED` | 중단 조건 발생, 측정 무효, 범위 이탈 또는 권리·보안 위반으로 결과를 사용할 수 없음 |

현재 pilot 상태는 `UNSET`이다.

### 2.3 가격과 미수집 값

- 실제 가격: `UNSET`
- pilot 비용: `UNSET`
- 절감률·전환율·사용자 수: `UNSET`
- 응답자가 근거 없이 제시한 추정은 사실값이 아니라 `INTERVIEW_REPORTED` 또는 `ASSUMED`로 기록한다.
- 공식 견적, 내부 원가 자료 또는 승인된 구매 문서가 없으면 숫자를 가격 결론으로 승격하지 않는다.

## 3. 검증 대상 역할

한 사람이 여러 역할을 맡을 수 있지만, 기록은 역할별 관점으로 분리한다. 예를 들어 같은 응답자가 실무와 구매를 모두 담당하면 동일 세션 아래 `PRACTITIONER`와 `BUDGET_OWNER` 기록을 별도 evidence record로 만든다.

| 역할 코드 | 역할 | 확인할 결정 | 섞지 말아야 할 관점 |
|---|---|---|---|
| `PRACTITIONER` | 방사선·부품·시스템 보증 자료를 찾고 정리하는 실무 사용자 | 실제 workflow, 시간, 문서, 재작업, 필요한 산출물 | 구매 권한이 없으면 가격·계약 결론으로 사용 금지 |
| `TECHNICAL_REVIEWER` | 판정 근거·적용성·추적성을 검토하거나 승인하는 사람 | 반려 조건, 필수 trace, 승인 기준, 감사 산출물 | 실무자의 조작 편의와 승인 요건을 동일시 금지 |
| `BUDGET_OWNER` | 도구·pilot·서비스 비용을 승인하는 구매자 또는 예산 소유자 | 구매 단위, 예산 출처, 승인 과정, 대체재, 반대 이유 | 가상 선호를 실제 구매 승인으로 승격 금지 |
| `DATA_RIGHTS_APPROVER` | 외부 원문·고객 자료 저장·처리·보존·삭제를 승인하는 사람 | 허용 데이터, 처리 위치, 법무·보안 조건, 중단 조건 | 공개 URL을 저장·AI 처리 권리로 간주 금지 |

### 역할 적합성 확인 질문

1. “가장 최근 유사 검토에서 직접 수행하거나 승인한 단계는 무엇입니까?”
2. “그 과정에서 본인이 결정할 수 있는 것과 다른 사람이 승인해야 하는 것은 무엇입니까?”
3. “도구·서비스 비용 또는 데이터 저장·처리를 최종 승인하는 역할은 누구입니까? 이름이나 연락처는 기록하지 않고 역할만 적겠습니다.”

최근 실제 관여 사례가 없으면 해당 역할의 evidence scope를 `OUT_OF_ROLE_SCOPE`로 메모하고 다른 역할의 답변으로 대체하지 않는다.

## 4. 가설 레지스트리

모든 비즈니스 결론은 아래 hypothesis ID 또는 새로 승인된 ID에 연결한다. 현재 상태는 전부 `UNVALIDATED`다.

| Hypothesis ID | 검증 전 가설 | 필요한 evidence | 주요 역할 | 현재 상태 |
|---|---|---|---|---|
| `H-PROBLEM-01` | 환경·BOM·시험 원문·완화·승인 단절이 최근 실제 검토에서 지연 또는 재작업을 만든다. | 최근 사례 workflow, 단계별 시간, 중단 원인, 반려·재작업 기록 | `PRACTITIONER`, `TECHNICAL_REVIEWER` | `UNVALIDATED` |
| `H-TRACE-01` | 출처·identity·조건·판정 trace를 한 패키지로 보존하는 것이 검토·인계에 유용하다. | 현재 전달 산출물, 반려 기준, 필수 locator, 실제 인계 사례 | `PRACTITIONER`, `TECHNICAL_REVIEWER` | `UNVALIDATED` |
| `H-HOLD-01` | 근거 부족 시 `HOLD` 이유와 다음 행동을 함께 제시하면 실제 workflow 의사결정에 유용하다. | 최근 불확실 사례, 현재 처리 방식, concept 반응, 유용·무용 조건 | 전 역할 | `UNVALIDATED` |
| `H-OUTPUT-01` | Evidence coverage, 판정 근거, 다음 행동, 변경 영향 중 보존 가치가 높은 산출물이 존재한다. | 실제 보존·전달 문서와 사용 시점, 필수 형식 | `PRACTITIONER`, `TECHNICAL_REVIEWER` | `UNVALIDATED` |
| `H-BASELINE-01` | 검토 cycle time과 재작업을 일관된 단위·분모로 측정할 수 있다. | timestamps, 작업 기록, 문서 이력 또는 재현 가능한 계산 | `PRACTITIONER`, `TECHNICAL_REVIEWER` | `UNVALIDATED` |
| `H-BUY-01` | SPECTRA에 적합한 구매 단위와 예산 경로를 특정할 수 있다. | 실제 구매 사례, 예산 범주, 승인 단계, 대체재, 보안·법무 조건 | `BUDGET_OWNER`, `DATA_RIGHTS_APPROVER` | `UNVALIDATED` |
| `H-PILOT-01` | 제한된 workflow pilot으로 시간·추적성·재작업 변화를 관찰할 수 있다. | 승인된 baseline, 동일 범위 비교, 측정 로그, guardrail 결과 | 전 역할 | `UNVALIDATED` |
| `H-RIGHTS-01` | 데이터 권리·보안·보존·삭제 조건이 제품 사용 또는 구매의 핵심 gate다. | 실제 승인 정책, 반려 사례, 허용 처리 범위 | `DATA_RIGHTS_APPROVER`, `BUDGET_OWNER` | `UNVALIDATED` |

### 가설 추가 규칙

- ID 형식: `H-<TOPIC>-NN`
- 한 가설에는 하나의 검증 가능한 예측만 둔다.
- claim, 영향을 받는 역할, 필요한 evidence, 반증 조건을 함께 기록한다.
- 인터뷰 중 나온 새 가설은 즉시 사실로 채택하지 않고 `UNVALIDATED`로 추가한다.

## 5. 30분 인터뷰 프로토콜

### 인터뷰 전 준비

- 응답자의 실명·회사명·연락처 대신 세션별 익명 ID를 준비한다. 예: `R-001`.
- 녹음·원문 보관은 별도 동의와 저장 권리가 있을 때만 수행한다. 이 저장소에는 넣지 않는다.
- Product UI를 보여 줄 경우 모든 값이 합성이고 인증 도구가 아님을 먼저 고지한다.
- 인터뷰어는 “구매하시겠습니까?”보다 최근 실제 행동과 문서를 먼저 묻는다.
- evidence log와 빈 baseline sheet를 준비한다.

### 0:00–3:00 — 범위·역할·동의

1. “오늘은 판매가 아니라 현재 업무를 이해하기 위한 인터뷰입니다. 답변은 익명 요약으로만 기록해도 괜찮습니까?”
2. “직접 수행하거나 승인한 가장 최근의 유사 검토는 무엇이었습니까?”
3. “그 사례에서 맡은 역할을 실무, 기술 검토·승인, 예산 승인, 데이터 권리 승인으로 나누면 어디에 해당합니까?”

기록: 익명 ID, 역할 코드, 최근 사례의 존재 여부, 수집 동의 범위, 저장 제한.

### 3:00–10:00 — 최근 실제 사례 재구성

1. “가장 최근 유사 검토를 시작부터 최종 전달 또는 중단까지 순서대로 설명해 주세요.”
2. “각 단계에서 어떤 문서·도구·spreadsheet를 열었습니까?”
3. “누가 어떤 산출물을 다음 사람에게 전달했고, 누가 승인했습니까?”
4. “어느 단계에서 가장 오래 멈췄습니까? 그때 무엇을 기다렸습니까?”
5. “어떤 근거 누락이나 조건 불일치가 재검토 또는 결재 반려를 만들었습니까?”

인터뷰어는 답변을 요약하기 전에 “제가 들은 순서가 맞는지” 되짚어 확인한다.

### 10:00–16:00 — 시간·비용 기준선

1. “그 한 건에 실제 작업한 시간과 달력상 경과 시간은 각각 어느 정도였습니까?”
2. “반복 입력, 수기 대조, 원문 추적, 재검토에 각각 어느 정도를 썼습니까?”
3. “대기 시간과 직접 작업 시간을 구분할 수 있습니까?”
4. “재작업은 어떤 조건에서 발생했고 몇 단계가 되돌아갔습니까?”
5. “비용은 시험·외주·라이선스 같은 직접비입니까, 내부 인력 시간입니까?”
6. “이 숫자를 확인할 timestamp, 문서 이력, timesheet, 견적 또는 계산 근거가 있습니까? 원문 자체가 아니라 접근 가능한 locator만 기록하겠습니다.”

응답자가 기억하지 못하면 숫자를 강요하지 않고 `UNSET`으로 둔다.

### 16:00–21:00 — 신뢰·산출물·승인

1. “현재 도구의 결과를 그대로 신뢰하지 못하거나 다시 확인하는 이유는 무엇입니까?”
2. “상급자·고객·다음 담당자에게 반드시 전달하거나 보존하는 산출물은 무엇입니까?”
3. “판정 근거에서 빠지면 반려되는 출처·identity·시험 조건·승인 항목은 무엇입니까?”
4. “변경이 생겼을 때 이전 검토 중 무엇을 다시 확인합니까?”
5. “현재 문서와 승인 이력의 최종 source of truth는 어디입니까?”

### 21:00–25:00 — 중립적 concept 검증

먼저 다음 한 문장만 제시한다.

> “SPECTRA는 환경·정확한 부품 증거·완화·정책을 연결하고, 근거가 부족하면 `HOLD` 이유와 다음 행동을 보여 주는 workflow 도구입니다. 현재 데모는 합성 프로토타입이며 실제 보증 결과가 아닙니다.”

그 다음 묻는다.

1. “방금 설명 중 현재 workflow에 실제로 연결되는 부분과 연결되지 않는 부분은 무엇입니까?”
2. “`HOLD`와 다음 행동이 명확한 결과는 언제 유용합니까? 언제 오히려 방해됩니까?”
3. “Evidence coverage, 판정 근거, 다음 행동, 변경 영향 중 실제로 보존하거나 전달할 것은 무엇입니까?”
4. “이 workflow가 있어도 기존 방식으로 되돌아갈 이유는 무엇입니까?”

칭찬이나 기능 요청을 구매 의사 또는 가치 실현으로 해석하지 않는다.

### 25:00–28:00 — 구매 단위·pilot 조건

1. “최근 비슷한 도구·분석·시험·컨설팅을 어떤 단위로 구매하거나 승인했습니까?”
2. “seat, 조직/프로젝트 workspace, 임무·BOM 검토 건별, 제한 기간 pilot, 구축·통합 서비스 중 현재 승인 구조와 가장 가까운 것은 무엇이며 왜 그렇습니까?”
3. “예산 출처, 승인 단계, 보안·법무·데이터 조건, 대체재와 반대 이유는 무엇입니까?”
4. “실제 pilot을 검토하려면 시작 전에 어떤 baseline과 중단 조건이 필요합니까?”

가격을 먼저 제시하거나 응답자에게 임의 숫자를 강요하지 않는다. 확인 가능한 구매·견적 근거가 없으면 `price=UNSET`이다.

### 28:00–30:00 — 확인·종료

1. 인터뷰어가 관찰된 사실, 응답자 추정, 미확인 항목을 구분해 요약한다.
2. “제가 잘못 이해했거나 빠뜨린 최근 실제 행동이 있습니까?”
3. “어떤 항목은 문서나 관찰로 corroborate할 수 있고, 어떤 항목은 접근 제한 때문에 확인할 수 없습니까?”
4. 후속 연락처를 이 저장소에 기록하지 않는다. 별도 승인된 운영 채널이 없다면 후속 수집을 수행하지 않는다.

## 6. 현재 업무 기준선 기록 계약

### 6.1 단위와 분모

시간·비용 숫자에는 아래 필드를 모두 요구한다.

| 필드 | 예시 형식 | 규칙 |
|---|---|---|
| `metric_name` | `active_review_time` | 측정 대상이 명확해야 함 |
| `value` | 빈 값 또는 숫자 | 모르면 `UNSET`; 범위이면 lower/upper 분리 |
| `unit` | `person_hour`, `calendar_day`, `KRW`, `USD` | 단위 없는 숫자 금지 |
| `denominator` | `per_component_mission_review` | 건·부품·BOM·임무·월 등 분모 필수 |
| `reference_period` | `2026-Q3`, 사례 시작·종료일 | 기준 기간 필수 |
| `method` | `timestamp_difference`, `time_log_sum`, `respondent_estimate`, `invoice_total` | 산정 방법 필수 |
| `source_locator` | 익명 문서 ID·접근 제한 사유 | 원문을 저장소에 복사하지 않음 |
| `evidence_class` | 계약 enum | 아래 Evidence log와 일치 |
| `confidence_level` | `HIGH / MEDIUM / LOW / UNKNOWN` | 아래 명시적 기준만 사용 |
| `assumptions` | 빈 값 또는 명시적 가정 | 계산·추정에 사용한 가정 |

### 6.2 신뢰 수준 기준

| 수준 | 허용 조건 |
|---|---|
| `HIGH` | 직접 관찰 또는 접근 가능한 문서·timestamp로 확인되고 산식이 재현됨 |
| `MEDIUM` | 인터뷰 발언이 독립 문서·관찰 또는 다른 역할의 독립 기록으로 corroborate됨 |
| `LOW` | 단일 응답자의 회상·추정이며 직접 확인 자료가 없음 |
| `UNKNOWN` | 산정 방법·기간·분모·출처 중 하나 이상이 불명확함 |

확률이나 임의 점수를 만들지 않는다. `LOW`와 `UNKNOWN`은 가격·절감률·pilot 성공 결론의 단독 근거로 사용하지 않는다.

### 6.3 비용 분리

- `DIRECT_COST`: 시험비, 외주비, 라이선스, 구매·시설 사용료
- `INTERNAL_LABOR`: 역할별 실제 투입 시간 × 승인된 내부 원가율. 원가율이 없으면 시간만 기록하고 비용은 `UNSET`
- `WAITING_TIME`: 달력상 대기. 인력 비용과 자동 합산하지 않음
- `REWORK_COST`: 재작업 시간과 직접비를 원인별로 분리
- `AVOIDED_COST`: 실제 회피가 관찰되고 counterfactual이 문서화되기 전에는 `UNSET`

## 7. Evidence log 계약

각 기록은 하나의 질문·관찰·문서 사실·계산 claim만 담는다.

### 7.1 필수 필드

| 필드 | 계약 |
|---|---|
| `record_id` | `BV-YYYYMMDD-NNN` 형식의 비식별 ID |
| `collected_at` | 날짜와 timezone; 시간 미상은 날짜만 |
| `respondent_role` | 역할 코드. 복수 역할은 record 분리 |
| `anonymous_respondent_id` | 세션 내부 익명 ID. 실명·회사·연락처 금지 |
| `collection_method` | `INTERVIEW / DIRECT_OBSERVATION / DOCUMENT_REVIEW / CALCULATION` |
| `question_or_observation` | 질문 또는 관찰 항목 |
| `short_factual_record` | 원문 전체가 아닌 짧은 사실 기록. 의견과 해석 분리 |
| `normalized_claim` | 단일 검증 가능한 claim |
| `evidence_class` | 아래 enum 중 하나 |
| `value_unit_denominator_period` | 숫자가 없으면 `NOT_APPLICABLE`; 있으면 모두 채움 |
| `source_locator_or_restriction` | 익명 locator 또는 접근 제한 사유 |
| `corroboration_status` | 아래 enum 중 하나 |
| `conflict_and_uncertainty` | 반대 증거, 회상 오차, 적용 범위 |
| `hypothesis_ids` | 영향을 받는 hypothesis ID 목록 |
| `next_action` | corroborate, clarify, reject, preserve limitation 등 |

### 7.2 Evidence class

- `INTERVIEW_REPORTED`: 응답자가 말한 최근 행동·수치·의견
- `DIRECTLY_OBSERVED`: 연구자가 실제 workflow나 artifact 사용을 관찰
- `DOCUMENTED`: 권한 있는 문서·로그·견적·승인 기록에서 확인
- `CALCULATED`: 명시된 입력·단위·산식으로 재현 가능
- `ASSUMED`: 검증 전 가정. 사업 결론을 단독 지지할 수 없음

### 7.3 Corroboration 상태

- `NONE`
- `PENDING`
- `CORROBORATED`
- `CONFLICTING`
- `NOT_APPLICABLE`

### 7.4 개인정보·기밀·권리 규칙

- 실명, 회사명, 이메일, 전화번호, 정확한 직함 조합 등 재식별 가능 정보를 저장하지 않는다.
- 고객 BOM, 계약서, 견적서, 시험 원문, 화면 캡처와 녹취를 Git에 넣지 않는다.
- 원문 보존이 필요하면 승인된 외부 저장 위치의 익명 locator, 접근 등급, 보존·삭제 조건만 기록한다.
- 접근 권리가 없거나 동의가 철회되면 locator를 `ACCESS_RESTRICTED` 또는 `CONSENT_WITHDRAWN`로 기록하고 evidence 사용을 중단한다.

## 8. 구매 단위와 가격 가설 기록

다음 후보는 비교 대상일 뿐 추천이나 확정 모델이 아니다.

| Candidate ID | 구매 단위 가설 | 확인할 구매자 | 확인할 evidence | 가격 |
|---|---|---|---|---|
| `BU-SEAT` | 사용자 seat | 팀 관리자·예산 소유자 | 실제 seat 구매 관행, 사용자 수 산정, 반대 이유 | `UNSET` |
| `BU-WORKSPACE` | 조직/프로젝트 workspace | 프로젝트·조직 예산 소유자 | 협업·tenant·보안 요건, 예산 항목 | `UNSET` |
| `BU-CASE` | 임무 또는 BOM 검토 건별 | 미션·부품 검토 발주자 | 검토 단위와 volume, 건별 승인·대체재 | `UNSET` |
| `BU-PILOT` | 제한 기간 pilot | pilot sponsor·예산 소유자 | 기간 승인, 성공·중단 조건, 데이터 범위 | `UNSET` |
| `BU-SERVICE` | 구축·통합·검증 서비스 | 프로젝트·조달·보안 승인자 | SOW, 통합 범위, 내부 역량, 조달 절차 | `UNSET` |

각 후보에 다음을 기록한다.

- 실제 구매자 역할
- 예산 출처와 회계 단위
- 승인·조달 단계와 예상이 아닌 실제 선행 사례
- 보안·법무·권리 조건
- 현재 대체재와 전환하지 않을 이유
- 지불 가격의 source locator 또는 `UNSET`
- 관련 evidence record ID와 `H-BUY-01` 상태 영향

“살 것 같다”, “유용해 보인다”는 실제 구매 승인 evidence가 아니다.

## 9. Pilot 계약

Pilot은 방사선 적합성 인증이 아니라 **증거 정리·추적·판정 설명 workflow 검증**으로 한정한다.

### 9.1 시작 전 필수 필드

```text
pilot_id: UNSET
pilot_status: UNSET
target_organization_type: UNSET
participant_roles: UNSET
use_case: UNSET
input_scope: UNSET
approved_data_scope: UNSET
baseline_period: UNSET
baseline_records: UNSET
success_metrics: UNSET
measurement_methods: UNSET
stop_conditions: UNSET
fail_closed_conditions: UNSET
security_rights_retention_deletion_approval: UNSET
responsible_owner: UNSET
independent_reviewer: UNSET
result_state: UNSET
```

필드가 완전하지 않으면 `PLANNED`로 올리지 않는다.

### 9.2 KPI 후보와 측정 계약

목표값은 baseline과 승인된 pilot 범위가 생긴 뒤 별도 설정한다. 현재 target은 모두 `UNSET`이다.

| KPI ID | 유형 | 정의·산식 | source | 현재 target |
|---|---|---|---|---|
| `KPI-CYCLE-01` | Primary outcome | 사례별 review-ready evidence package까지의 active person-hours와 calendar elapsed time. 두 시간을 분리 | timestamp, time log, workflow record | `UNSET` |
| `KPI-RETURN-01` | Primary outcome | evidence·traceability 누락으로 재검토 또는 반려된 case 수 / 동일 범위 검토 case 수 | review disposition, return reason | `UNSET` |
| `KPI-TRACE-01` | Primary outcome | 사전 합의된 필수 trace field 중 유효 locator와 reviewer 확인을 가진 field 수 / 필수 field 수 | output checklist, reviewer record | `UNSET` |
| `DRV-GAP-01` | Driver | 발견된 필수 evidence gap 중 owner·next action·due state가 명시된 gap 수 / 전체 필수 gap 수 | Evidence coverage log | `UNSET` |
| `DRV-FIND-01` | Driver | 특정 원문·판정 근거를 찾는 active minutes per retrieval task | observation/time log | `UNSET` |

### 9.3 Guardrail과 중단 조건

다음 중 하나가 발생하면 pilot 결과를 성공으로 집계하지 않고 중단·검토한다.

- 합성·가정·미승인 데이터가 실제 보증 근거로 표현됨
- `HOLD` 또는 `NOT_EVALUATED`가 지원·인증으로 승격됨
- 권리 미확인 원문, 개인정보 또는 고객 기밀이 승인 범위 밖에 저장·처리됨
- baseline과 pilot의 case 범위·역할·분모가 비교 불가능함
- 측정 로그가 누락돼 결과를 재현할 수 없음
- 참여자 또는 데이터 승인자가 동의를 철회함

이 경우 관련 result state는 `INVALIDATED` 또는 가설 상태 `INSUFFICIENT_EVIDENCE`로 남긴다.

## 10. 인터뷰 후 정리와 가설 판정

### 10.1 세션 종료 후 15분 절차

1. 개인정보·회사 식별자·원문 내용을 제거한다.
2. 한 record에 한 claim만 남기도록 evidence log를 분리한다.
3. 발언, 직접 관찰, 문서, 계산, 가정을 evidence class로 구분한다.
4. 숫자의 단위·기간·분모·산정 방법·locator·신뢰 수준을 검사한다.
5. 각 record를 hypothesis ID에 연결한다.
6. conflict와 제한을 기록하고 corroboration next action을 지정한다.
7. 증거가 없으면 hypothesis 상태를 바꾸지 않는다.

### 10.2 상태 변경 검토표

| 질문 | No일 때 |
|---|---|
| 가설과 직접 관련된 최근 실제 사례인가? | `INSUFFICIENT_EVIDENCE` 후보 |
| 역할 scope가 명확한가? | record 분리 또는 사용 보류 |
| 숫자의 단위·분모·기간·방법이 완전한가? | 값 `UNSET`, claim 제한 |
| source locator 또는 접근 제한 사유가 있는가? | corroboration `PENDING` 또는 사용 보류 |
| 독립 corroboration이 있는가? | `SUPPORTED_WITH_LIMITS`로 올리지 않음 |
| material conflict가 해결됐는가? | conflict 유지, 범위 축소 또는 판정 보류 |

상태 변경에는 최소한 supporting record ID, contradicting record ID, 적용 역할·상황, 알려진 한계와 다음 검증이 필요하다.

## 11. 빈 세션 기록 양식

```text
session_id: BV-SESSION-UNSET
date: UNSET
interviewer_id: ANON-UNSET
respondent_id: ANON-UNSET
role_codes: UNSET
consent_scope: UNSET
storage_restriction: UNSET

recent_case:
  case_scope: UNSET
  workflow_steps: UNSET
  tools_and_documents: UNSET
  approval_steps: UNSET
  longest_wait: UNSET
  rework_trigger: UNSET

baseline:
  active_time: UNSET
  elapsed_time: UNSET
  rework_time: UNSET
  waiting_time: UNSET
  direct_cost: UNSET
  internal_labor: UNSET
  unit_denominator_period_method_source: UNSET

value:
  useful_outputs: UNSET
  hold_useful_when: UNSET
  hold_not_useful_when: UNSET
  trust_blocker: UNSET

purchase:
  candidate_unit: UNSET
  buyer_role: UNSET
  budget_source: UNSET
  approval_process: UNSET
  security_legal_conditions: UNSET
  alternative: UNSET
  objection: UNSET
  price: UNSET

pilot:
  use_case: UNSET
  baseline_requirement: UNSET
  success_metric: UNSET
  stop_condition: UNSET
  approved_data_scope: UNSET
  status: UNSET

hypothesis_updates: UNVALIDATED
evidence_record_ids: UNSET
follow_up: UNSET
```

## 12. 자체 검증 체크리스트

- [ ] 모든 비즈니스 결론에 hypothesis ID와 필요한 evidence가 연결돼 있다.
- [ ] 아직 수집되지 않은 값은 `UNSET` 또는 `UNVALIDATED`다.
- [ ] 질문은 미래 선호보다 최근 실제 행동을 먼저 묻는다.
- [ ] 실무·기술 승인·구매·데이터 권리 역할이 구분된다.
- [ ] 시간·비용 숫자에는 단위·기간·분모·산정 방법·출처·신뢰 수준이 필요하다.
- [ ] Pilot 성공은 radiation assurance·인증 완료와 분리된다.
- [ ] 개인정보·고객 기밀·계약·원문을 저장소에 넣지 않는다.
- [ ] 인터뷰·발송·외부 수집을 수행하지 않았다.
- [ ] 허용 범위 밖 파일을 수정하지 않았다.
- [ ] `git diff --check`가 통과한다.

## 13. 현재 판정

- 실제 인터뷰: 0건
- 실제 관찰·고객 문서·구매 evidence: 0건
- 승인 pilot: 0건
- 가격·절감률·구매 의사: `UNSET`
- 모든 business hypothesis: `UNVALIDATED`
- Stage 9: `IN_PROGRESS`

이 프로토콜을 만들었다는 이유로 Stage 9 checklist를 완료 처리하지 않는다.
