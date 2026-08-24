# H06 Live Execution Event Contract

## 결론

GCP Workflow 실행을 Product에서 단계별로 시각화하기 위한 backend event contract와 deterministic reducer를 구현했다. 현재 범위는 caller-supplied event stream의 구조·revision·hash chain·인과 순서를 검증하는 로컬 contract다. Google API를 호출하거나 live transport를 인증하지 않는다.

정상 synthetic control은 다음처럼 종료한다.

```text
VALID
COMPLETE / SUCCEEDED
workflow_succeeded=true
workflow_success_is_business_pass=false
evidence_status=SYNTHETIC_ONLY
assurance_decision=HOLD
```

## 이벤트 흐름

```text
WORKFLOW_STARTED
→ STORAGE_INPUT_BOUND
→ Mission Agent
→ Deterministic Core
→ Parts Agent
→ Assurance Agent
→ STORAGE_RESULT_BOUND
→ WORKFLOW_COMPLETED
```

각 이벤트는 동일한 project/region/workflow/execution/correlation identity를 사용하고 0부터 연속된 sequence, timezone-aware timestamp, `previous_event_sha256`와 `event_sha256` hash chain을 가진다. Workflow·Cloud Run Agent·Storage·Core source ID와 revision은 `platform/gcp-e2e-h04/live-deployment-anchor.json`에 결속된다.

## 상태 분리

- `observation_mode`: `LIVE_API` 또는 `SNAPSHOT_REPLAY`
- `stream_status`: event contract 상태인 `IN_PROGRESS`, `COMPLETE`, `INVALID`
- `execution_status`: GCP orchestration 상태인 `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`
- `evidence_status`: 현재 고정 deployment에서는 항상 `SYNTHETIC_ONLY` 또는 `NOT_EVALUATED`
- `assurance_decision`: 항상 `HOLD`

Workflow가 `SUCCEEDED`여도 Agent가 안전한 `INVALID_INPUT/HOLD`를 반환했을 수 있다. 따라서 `workflow_success_is_business_pass=false`를 고정한다.

## Fail-closed 검증

- event body hash와 predecessor chain 변조
- execution/correlation 혼합
- sequence 중복·도약, event ID 중복, timestamp 역행
- Agent/deployment revision 교체
- input object hash와 Agent/Core execution-input hash 불일치
- Core 자체 canonical input hash와 execution object hash의 잘못된 동일시
- success terminal의 component/Agent 누락
- completion 선행과 Assurance 인과 순서 위반
- synthetic `PASS` 승격
- deployment anchor를 `ACTUAL/PASS`로 자기 승격
- duplicate Agent role
- unknown field와 non-finite number

직접 공격 테스트 19개가 통과했다. partial stream은 `VALID / IN_PROGRESS / HOLD`, 실패 Workflow는 `VALID / COMPLETE / FAILED / HOLD`, 훼손 stream은 `INVALID_INPUT / INVALID / HOLD`로 닫힌다.

## 현재 한계와 다음 단계

event hash chain은 무결성 결속이며 source authenticity나 Google API 응답을 인증하지 않는다. receipt는 이를 `INTEGRITY_ONLY_NOT_AUTHENTICATED`로 명시하고 다음 limitation을 유지한다.

- `GCP_API_NOT_CALLED_BY_REDUCER`
- `LIVE_TRANSPORT_AUTHENTICITY_NOT_ESTABLISHED`
- `SCIENTIFIC_EVIDENCE_NOT_VALIDATED`

Core event는 저장된 실행 입력에 대한 `execution_input_sha256`와 Core 계산 preimage의 `core_input_sha256`를 분리한다. H05 production Core의 canonical 입력은 Storage fixture 전체가 아니므로 두 값을 같다고 가정하지 않는다.

후속 H07에서 고정 project/region의 Workflows execution, Cloud Logging과 Cloud Storage generation만 read-only 조회하는 connector를 구현했고 실제 정상 execution receipt를 발행했다. H08은 이를 `LIVE_API` Product data로 변환했다. Product HTML 시각 연결과 caller identity attestation은 다음 단계다.
