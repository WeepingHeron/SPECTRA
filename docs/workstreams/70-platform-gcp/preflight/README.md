# Raw Manifest v2 Preflight

이 preflight는 candidate manifest와 object creation receipt를 읽기 전용으로 검사한다. GCP object나 manifest 파일을 생성하지 않는다. fixture의 creation receipt는 실제 Cloud Storage 관찰 증거가 아니라 공격 계약을 검증하기 위한 `SYNTHETIC` 입력이다.

```bash
python3 docs/workstreams/70-platform-gcp/preflight/test_raw_manifest_preflight.py -v

python3 docs/workstreams/70-platform-gcp/preflight/raw_manifest_preflight.py \
  /absolute/path/to/single-preflight-request.json \
  --schema-root schemas
```

CLI의 실제 입력은 fixture 묶음이 아니라 단일 request 객체여야 한다. 통과 결과는 `RAW_MANIFEST_ISSUABLE / ISSUE_ALLOWED`, 실패 결과는 `RAW_MANIFEST_HOLD_NOT_ISSUED / HOLD_NOT_ISSUED`다. 실패 시 `manifest`는 항상 `null`이다.

발행 gate:

- raw manifest v2 schema
- Workstream-local `preflight-request.schema.json`의 request/context/receipt 자료형
- non-placeholder provider job reference
- 요청·manifest·rights·artifact·creation receipt의 tenant/zone 일치
- `IF_GENERATION_MATCH_0` create-only receipt와 exact `project_id/bucket_id/object_name/generation`
- 현재 유효한 rights snapshot, approval hash/history anchor와 `FETCH`/`PRIVATE_STORE` grant
- artifact SHA-256, byte size, MIME, malware `PASS`, validation과 reviewer
- parser input bundle hash와 manifest bundle hash 일치

fixture는 전부 `SYNTHETIC`이거나 reference-only HOLD 요청이다. 실제 SPENVIS/TI bytes, 수치, PDF 또는 승인 manifest는 포함하지 않는다.

## Stable code registry

| Gate | Stable codes |
|---|---|
| 입력/schema | `PREFLIGHT_INPUT_INVALID`, `RAW_MANIFEST_CANDIDATE_MISSING`, `RAW_MANIFEST_SCHEMA_INVALID` |
| provider | `PROVIDER_JOB_REFERENCE_MISSING`, `PROVIDER_JOB_REFERENCE_PLACEHOLDER` |
| tenant/zone | `TENANT_CONTEXT_MISSING`, `CROSS_TENANT_ACCESS_DENIED`, `RAW_ZONE_MISSING`, `RAW_MANIFEST_ZONE_MISMATCH` |
| rights | `RIGHTS_SNAPSHOT_MISSING`, `RIGHTS_TENANT_MISMATCH`, `RIGHTS_APPROVAL_MISSING`, `RIGHTS_SNAPSHOT_NOT_ACTIVE`, `DUPLICATE_RIGHTS_ACTION_GRANT`, `REQUIRED_ACTION_SET_INCOMPLETE`, `RIGHTS_ACTION_GRANT_MISSING`, `RIGHTS_ACTION_GRANT_STALE`, `RAW_RIGHTS_SNAPSHOT_MISMATCH` |
| create/generation | `CREATE_ONLY_PRECONDITION_MISSING`, `OBJECT_CREATION_RECEIPT_MISSING`, `DUPLICATE_OBJECT_CREATION_RECEIPT`, `UNEXPECTED_OBJECT_CREATION_RECEIPT`, `RAW_OVERWRITE_ATTEMPT`, `RAW_GENERATION_MISSING`, `RAW_GENERATION_MISMATCH`, `RAW_STORAGE_REF_MISMATCH`, `DUPLICATE_ARTIFACT_ID`, `DUPLICATE_STORAGE_REF` |
| integrity/review | `ARTIFACT_HASH_MISMATCH`, `ARTIFACT_SIZE_MISMATCH`, `MIME_CONTENT_MISMATCH`, `MALWARE_SCAN_NOT_PASSED`, `RAW_ARTIFACT_NOT_VALIDATED`, `RAW_ARTIFACT_REVIEW_MISSING`, `BUNDLE_HASH_MISMATCH` |

code의 의미를 바꿀 때는 기존 code를 재사용하지 않고 계약 version과 fixture를 함께 변경한다.

## 검증 순서

1. request가 object인지 확인한다.
2. `preflight-request.schema.json`으로 context, required action과 receipt의 모든 identifier·storage field 자료형을 검사한다. 실패하면 semantic traversal 없이 `PREFLIGHT_INPUT_INVALID`다.
3. reference-only request의 `candidate_manifest=null`은 `RAW_MANIFEST_CANDIDATE_MISSING`으로 종료한다.
4. candidate manifest를 공용 raw manifest v2 schema로 검사한다. 실패하면 collection/hash/map을 순회하지 않고 `RAW_MANIFEST_SCHEMA_INVALID`다.
5. schema-valid 값에 대해서만 rights, tenant/zone, receipt cardinality와 exact storage tuple, integrity/review를 검사한다.

`real-candidate-holds.json`의 `declared_preflight_gaps`는 외부 상태를 이 코드가 검증했다는 뜻이 아니다. Workstream 30/40 문서에서 전달된 gap을 **입력으로 선언한 reference-only fixture**이며, 발행 차단은 독립적으로 `RAW_MANIFEST_CANDIDATE_MISSING`이 보장한다.
