# H07 Authenticated Read-only GCP Connector

## 결론

H06 reducer 앞에 고정 H05 deployment만 관찰하는 connector를 구현했다. connector가 생성할 수 있는 `gcloud` 명령은 다음 네 종류뿐이다.

1. `workflows executions describe`
2. `logging read`
3. `storage objects describe`
4. `storage cat`

Workflow 실행, object 쓰기·복사·삭제, 배포, IAM 변경 경로는 제공하지 않는다. subprocess는 shell 없이 argv list로만 실행한다. execution ID는 UUID 형식만 받고 project, region, workflow, bucket, Agent service/revision은 trusted deployment anchor에서만 가져온다.

## 관찰·결속 순서

```text
fixed execution describe
→ exact correlation Cloud Run logs
→ expected result object metadata
→ result body read
→ same object metadata re-read
→ H06 event chain + reducer
```

Storage body는 Workflow가 반환한 exact bucket/object/generation과 결속한다. body read 전후 generation이 모두 Workflow generation과 같아야 하며, 저장 body와 Workflow 반환 `result`의 semantic object가 같아야 한다. Agent response는 선언 `response_sha256`를 재계산하고 Cloud Logging의 run/correlation/service/revision/status/codes와 대조한다. Mission의 `core_result_sha256`도 재계산한다. Logging 조회는 execution `startTime`~`endTime`으로 제한해 동일 correlation 밖의 광범위한 로그를 스캔하지 않는다.

H05 production Core의 `input_hash`는 Storage fixture 전체 hash가 아니다. H06 Core event에는 다음을 별도로 기록한다.

- `execution_input_sha256`: 실행에 사용된 exact Storage object binding
- `core_input_sha256`: deterministic Core canonical preimage
- `output_sha256`: deterministic Core canonical output
- `result_sha256`: Mission 응답에 포함된 Core result object

## 실패 경계

- invalid execution ID와 승격된 deployment anchor는 GCP 명령 실행 전에 거부한다.
- execution/resource/revision/correlation 불일치, incomplete Agent/log set, Agent/Core hash 변조는 event receipt를 만들지 않는다.
- result body read 전후 generation 불일치는 `RESULT_GENERATION_CHANGED_OR_MISMATCHED`로 닫는다.
- 정상 관찰도 `SYNTHETIC`, `HOLD`, `used_for_decision=false`다.
- `gcloud`가 credential을 요구한다는 사실과 호출 계정 identity attestation을 분리해 `GCLOUD_CREDENTIAL_REQUIRED_IDENTITY_NOT_ATTESTED`로 표시한다.

## 검증과 미완료 범위

H06 19개와 H07 9개, 합계 28개 직접 테스트가 통과했다. H07은 read-only command allowlist, 정상 completed receipt, command injection 형식, generation race/mismatch, Workflow/Storage result 불일치, Agent response 변조, assurance anchor 승격, non-finite API JSON과 credential 재인증 실패의 비밀 비노출 stable code를 검증한다.

injected runner 기반 계약 검증 후 actual active GCP credential로 H05 정상 execution을 조회했다. execution API, 시간 범위가 고정된 세 Agent log, result object generation/body를 대조해 `VALID / COMPLETE / SUCCEEDED / SYNTHETIC_ONLY / HOLD` receipt를 발행했다. 이는 actual orchestration 관찰이지만 실제 방사선 원문·권리·과학적 적용성을 검증하지 않으며 caller identity를 별도 attestation하지 않는다.

실행 entrypoint는 `platform/gcp-e2e-h04/scripts/collect_live_execution.py`다. 이 스크립트는 connector receipt를 지정한 로컬 파일에 저장할 뿐 GCP 상태는 변경하지 않는다.
