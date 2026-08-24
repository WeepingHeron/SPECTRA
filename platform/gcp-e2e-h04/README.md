# SPECTRA H04/H05 Competition Multi-Agent GCP E2E

이 디렉터리는 실제 `iceu-686` 교육용 project에서 합성 fixture만 처리하는 최소 Competition Demo Release 구현이다. H05는 H04 리소스를 유지하면서 production Core 결합, canonical body 재해시, 고정 endpoint와 production test backdoor 제거를 보완한다. 실제 SPENVIS bundle, BOM, 시험 PDF, 고객 자료와 권리 미확인 원문은 입력으로 허용하지 않는다.

## 실행 구조

```text
private Cloud Storage synthetic object
  -> Workflows (fixed mission -> parts -> assurance order)
  -> three authenticated Cloud Run services
  -> create-only Cloud Storage result + structured Cloud Logging
```

세 서비스는 동일한 작은 Python runtime을 사용하지만 Cloud Run service와 runtime service account가 분리된다. `spectra-h04-workflow` service account만 각 서비스의 `roles/run.invoker`를 가지며 bucket에는 `roles/storage.objectViewer`와 `roles/storage.objectCreator`만 가진다. Agent service account에는 project role을 부여하지 않는다. endpoint는 unauthenticated access를 허용하지 않는다.

Mission Agent는 다운로드된 JSON body를 shared canonical byte 계약으로 다시 해시해 exact generation의 metadata SHA 및 expected SHA와 비교한 뒤, 고정 case/model로 production `src/spectra_sim/mvp_engine.py::run_mvp_decision`을 호출한다. 중복 방사선 계산식은 없다. mismatch는 `INPUT_BODY_SHA256_MISMATCH`로 Parts/Assurance 전에 종료한다. Parts Agent는 synthetic exact-part identity, 사건 coverage와 선언 hash를 확인한다. Assurance Agent는 앞선 두 결과의 status, data class, input/response hash를 독립 확인한다. 어떤 정상 합성 실행도 `engineering_gate=NOT_EVALUATED`, `assurance_decision=HOLD`를 벗어나지 않는다.

2026-08-25 ASR-D02 Phase 1은 deployed revision `000005-32c`에서 generation 404가 구조화된 result 없이 Workflow `FAILED`로 끝나고, exact part number 단독 변조가 `EXACT_PART_IDENTITY_MATCHED`로 소비되는 결함을 확인했다. 현재 working tree는 metadata lookup 404를 `INPUT_GENERATION_MISMATCH`로 정규화하고, 관측 identity를 고정 `expected_identity_sha256`과 비교해 `PART_IDENTITY_MISMATCH`로 닫도록 보완했다. 이 보완은 로컬 테스트만 통과했으며 아직 배포하지 않았다. 기존 locked revision과 Phase 1 실패 증거는 그대로 보존한다.

Workflow의 agent HTTP timeout·오류는 `AGENT_TRANSPORT_FAILURE`, response 계약 오류는 `AGENT_RESPONSE_INVALID`로 변환한다. Agent URL은 Workflow deployment environment에 고정되고 execution args의 URL override는 `ENDPOINT_OVERRIDE_FORBIDDEN`으로 Agent 호출 전에 닫힌다. production `test_mode/failure_role` 경로는 없으며 malformed fixture로 failure를 시험한다. 결과는 `ifGenerationMatch=0`으로 create-only 저장한다. 실행 후 runner가 실제 저장된 result bytes를 다시 내려받아 SHA-256을 관찰한다. 합성 input/result는 30일 후 삭제 lifecycle 대상이며, bucket 기본 soft delete 7일과 versioning off를 사용한다.

## 로컬 검증

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s platform/gcp-e2e-h04/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.gcp_live.test_live_execution_events
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.gcp_live.test_read_only_connector
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.gcp_live.test_product_timeline
PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py
```

`src/spectra_gcp_adapter/live_execution_events.py`는 live Product connector가 사용할 실행 event contract다. `read_only_connector.py`는 trusted anchor의 고정 H05 execution·log·result object만 읽어 H06 event로 변환하며 Workflow 실행이나 GCP mutation 명령을 만들지 않는다. 고정 H05 deployment identity는 `live-deployment-anchor.json`에 두며, 정상 Workflow `SUCCEEDED`도 business PASS 또는 radiation assurance로 승격하지 않는다. 로컬 injected-runner 검증과 actual 정상 execution read-only receipt를 모두 완료했으며 caller identity attestation은 별도 범위다.

고정 execution을 실제로 읽을 때는 새 실행을 만들지 않는 collector만 사용한다. 이 명령은 execution·logs·result object를 조회하고 로컬 receipt 파일만 기록한다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 platform/gcp-e2e-h04/scripts/collect_live_execution.py \
  --execution ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34 \
  --output docs/workstreams/70-platform-gcp/evidence/h07-live-execution-receipt.json
```

receipt 수집 후 Product timeline data를 재생성한다. live receipt가 유효하지 않으면 builder는 이를 라이브로 표시하지 않고 verified H05 snapshot fallback을 명시한다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 demo/build_gcp_live_timeline.py
```

## 배포와 H05 실행

active account가 직접 재인증되어 있고 gcloud project가 `iceu-686`인지 확인한 뒤 실행한다.

```bash
bash platform/gcp-e2e-h04/scripts/deploy.sh
PYTHONDONTWRITEBYTECODE=1 python3 platform/gcp-e2e-h04/scripts/run_e2e.py \
  --output docs/workstreams/70-platform-gcp/evidence/h05-e2e-runs.json
PYTHONDONTWRITEBYTECODE=1 python3 platform/gcp-e2e-h04/scripts/verify_deployed_core_parity.py \
  --runs docs/workstreams/70-platform-gcp/evidence/h05-e2e-runs.json \
  --output docs/workstreams/70-platform-gcp/evidence/h05-core-parity.json
```

배포 스크립트는 repo 전체가 아니라 service/shared contract, production `src/spectra_sim`, 필요한 schema와 고정 합성 fixture만 임시 build context에 stage한다. 기존 bucket, repository, service account 4개, Cloud Run service 3개와 Workflow 1개를 생성 또는 갱신하며 H05에서는 기존 리소스를 유지했다. runner는 정상 Core, body+metadata+expected SHA 동시 위조, parts hash 오염, malformed part, endpoint override, 제거된 legacy test-control 입력을 실행한다. Document AI, Vertex AI, Cloud SQL, BigQuery, KMS는 생성하거나 호출하지 않는다.

## 정리 명령

정리는 검토자가 실행 증거 보존 여부를 결정한 뒤 별도 승인으로 수행한다. 다음 명령은 삭제 대상이 명시된 재현용 목록이며 이 패키지에서는 자동 실행하지 않는다.

```bash
gcloud workflows delete spectra-h04-e2e --location=asia-northeast3 --project=iceu-686
gcloud run services delete spectra-h04-mission --region=asia-northeast3 --project=iceu-686
gcloud run services delete spectra-h04-parts --region=asia-northeast3 --project=iceu-686
gcloud run services delete spectra-h04-assurance --region=asia-northeast3 --project=iceu-686
gcloud storage rm --recursive gs://spectra-h04-iceu-686
gcloud storage buckets delete gs://spectra-h04-iceu-686
gcloud artifacts repositories delete spectra-h04 --location=asia-northeast3 --project=iceu-686
```

service account와 API disable은 다른 사용 여부를 확인하지 않고 삭제·비활성화하면 안 되므로 자동 cleanup 범위에서 제외한다.
