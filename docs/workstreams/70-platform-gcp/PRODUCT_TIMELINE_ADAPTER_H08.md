# H08 GCP Product Timeline Adapter

## 결론

H07 live receipt와 기존 Control Tower verified H05 snapshot을 하나의 Product-safe timeline contract로 변환하는 adapter를 구현했다. live receipt가 모든 계약을 통과할 때만 `display_mode=LIVE_API`를 사용한다. 조회 실패·변조·낙관적 assurance 승격·불완전 event receipt는 라이브로 표시하지 않는다.

첫 실제 read-only 조회는 gcloud credential 재인증 만료로 `GCLOUD_AUTH_REAUTH_REQUIRED / NOT_OBSERVED / HOLD`로 닫혔다. 재인증 후 Cloud Logging을 execution 시작~종료 시각으로 제한해 다시 수집했고, 현재 Product payload는 다음 상태다.

```text
display_mode=LIVE_API
live_api_observed=true
fallback_used=false
timeline_kind=AUTHENTICATED_API_OBSERVATION_IDENTITY_NOT_ATTESTED
workflow_success_is_business_pass=false
assurance_decision=HOLD
```

## 표시 계약

- `LIVE_API`: H07 connector와 H06 reducer가 모두 `VALID / COMPLETE / SUCCEEDED / HOLD`이고 event stream hash가 있을 때만 허용한다.
- `VERIFIED_SNAPSHOT_FALLBACK`: live가 관찰되지 않았지만 canonical hash가 유효한 H05 snapshot을 사용할 때다.
- `DATA_UNAVAILABLE`: live receipt와 snapshot 모두 신뢰할 수 없을 때다.

fallback의 일곱 단계는 실제 event replay가 아니라 저장 snapshot의 요약이다. 그래서 timestamp를 만들지 않고 모두 `occurred_at=null`로 유지한다. Workflow `SUCCEEDED`와 Agent `VALID`도 business 또는 radiation PASS로 승격하지 않는다.

## 산출물과 검증

- adapter: `src/spectra_gcp_adapter/product_timeline.py`
- builder: `demo/build_gcp_live_timeline.py`
- actual successful read-only receipt: `evidence/h07-live-execution-receipt.json`
- Product data: `demo/data/gcp-product-timeline.json`, `.js`

H08 직접 테스트 7개는 auth failure fallback, valid/actual live 우선순위, optimistic live 승격 차단, snapshot 변조 차단, non-finite live timeline, timeline hash와 exporter 결정성을 검증한다. H06~H08 직접 테스트는 합계 35개다. 현재는 data adapter까지만 연결했고 Product HTML 시각 요소 변경은 다음 UI 점검 회차로 남긴다.

## 다음 단계

Product UI는 다음 점검 회차에 `display_mode`, `live_api_observed`, `timeline_kind`, `source_codes`를 그대로 표시해야 한다. 재현 시에는 collector와 builder를 순서대로 실행한다. 현재 identity는 active gcloud credential을 사용했다는 범위이며 별도 caller attestation은 하지 않았으므로 `IDENTITY_NOT_ATTESTED`를 유지한다.
