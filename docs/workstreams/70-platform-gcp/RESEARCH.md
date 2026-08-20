# 70 Platform & GCP — GCP Evidence Storage & Rights Gate

## 1. 결론

SPECTRA의 최소 안전안은 **Cloud Storage를 원문 계층으로 사용하되, 공개 원문·제한 원문·고객 원문을 별도 IAM 경계로 분리하고 모든 바이트 이동 앞에 권리 gate를 두는 것**이다. 공개 URL은 다운로드 권한이 아니다. 권리 검토 전에는 locator와 약관 snapshot만 등록하며, 다운로드·비공개 저장·Document AI·Vertex AI·표시·재배포는 각각 독립 허용이 있어야 한다.

권장 물리 경계는 다음과 같다.

- 공개 원문과 제한 원문: 같은 shared evidence project 안의 **별도 bucket + 별도 service account**
- 고객 원문과 고객 파생값: 기본적으로 **tenant별 project + tenant별 bucket**
- manifest·감사 anchor·삭제 workflow: 별도 control project의 tenant-aware metadata 계층
- 합성 fixture: Git에는 소형 fixture만, runtime용은 별도 synthetic bucket
- prefix: 분류와 lifecycle 적용 보조일 뿐 보안 경계로 인정하지 않음

이번 문서는 구현 계약 초안이다. 승인된 project, region, bucket, database, KMS key와 실제 실행 증거는 모두 0건이며 Stage 7은 완료되지 않았다.

## 2. 전제와 용어

### 2.1 현재 기준선

- 실제 환경 모델 원문·출력: 0건
- 실제 부품 시험 PDF·수치: 0건
- 승인 BOM·고객 문서: 0건
- 승인 GCP resource와 실제 비용: 0개, 0원
- Workstream 30의 상업·자동화·재배포 권리는 미확인 항목이 있어 실제 run이 `HOLD`
- Workstream 40의 BOM, 문서별 저장·처리·재배포 권리와 승인 저장소가 없어 실제 ingest가 `HOLD`
- Workstream 50은 immutable policy approval/audit anchor를 Workstream 70에 요구하지만 실제 anchor는 없음

### 2.2 “수집”의 두 단계

`DISCOVER`는 URL, 문서 ID, issuer, 약관 위치만 기록하는 metadata-only 동작이다. `FETCH`는 원문 바이트를 다운로드해 quarantine으로 들이는 동작이다. 다음 순서에서 첫 “수집”은 `DISCOVER`이며, 권리 gate 전 `FETCH`는 금지한다.

```text
locator 발견·등록
  → rights snapshot 작성·독립 승인
  → FETCH 허용 여부 판정
  → 승인된 tenant quarantine으로 create-only upload
  → MIME/size/malware/hash 검증
  → immutable raw generation 확정
  → PROCESSING 허용 여부 재판정
  → 추출 후보 생성
  → 사람이 원문 locator와 정규화 값 검토
  → 승인된 파생 사실
  → RAW_ARTIFACT_MANIFEST와 EvidencePacket 연결
  → DISPLAY/REDISTRIBUTION 별도 gate
```

## 3. 데이터 구역과 경계

### 3.1 권장 구역

| Zone | 내용 | 물리 경계 | 접근 주체 | 근거 |
|---|---|---|---|---|
| `Z0_METADATA_INBOX` | locator, issuer, terms URL, 권리 요청 상태; 원문 bytes 없음 | control project의 metadata store 또는 작은 manifest bucket | rights reviewer, metadata registrar | 미확인 자료를 raw/AI 경로와 분리 |
| `Z1_PUBLIC_RAW` | 저장·처리가 명시적으로 허용된 외부 공개 원문 | shared evidence project의 전용 bucket | public-ingest SA, approved extractor SA, reviewer | 공개와 제한 자료의 IAM·lifecycle 혼합 방지 |
| `Z2_RESTRICTED_RAW` | 비공개 copy는 허용되나 표시·재배포가 제한된 원문 | 같은 project의 별도 bucket, 별도 SA; 필요 시 별도 project 승격 | restricted-ingest SA, 허용 processor, 지정 reviewer | “공개 접근 가능”과 “재사용 가능”을 분리 |
| `Z3_CUSTOMER_RAW` | 고객 BOM, 시험자료, CoC/lot trace | **tenant별 project와 raw bucket** 기본 | tenant upload SA, tenant processor SA, 해당 고객 reviewer | cross-tenant IAM·billing·KMS·삭제 blast radius 최소화 |
| `Z4_DERIVED` | 사람 확인 정규화 값, lineage, manifest, EvidencePacket용 사실 | source와 같은 tenant/rights 경계의 derived bucket/store | deterministic validator, reviewer, authorized product service | 파생값도 원문의 tenant·표시 제한을 상속 |
| `Z5_SYNTHETIC` | 명확한 `SYNTHETIC` fixture | 소형은 Git, runtime은 synthetic 전용 bucket | CI/test SA | 실제 원문·고객 데이터와 혼용 방지 |
| `Z6_AUDIT_CONTROL` | rights snapshot, approval hash, deletion tombstone, audit anchor | control project의 append-only 논리 store/log sink | rights approver, security auditor; workload write-only | 승인 이력과 data-plane 관리자 분리 |

`Z4_DERIVED`는 하나의 공유 bucket을 뜻하지 않는다. 공개 파생값, 제한 파생값, 고객 A 파생값은 각각 원 source 경계 안에 저장한다. 원문의 `tenant_id`, `rights_snapshot_id`, `raw_generation`, `artifact_sha256`를 상속하지 않은 파생값은 display 또는 decision에 사용할 수 없다.

### 3.2 project·bucket·prefix·tenant 선택

| 수단 | 사용 | 사용하지 않는 이유/한계 |
|---|---|---|
| Project | 고객 tenant별 기본 경계, shared evidence와 control plane 분리 | 수가 늘면 IAM·budget·KMS 운영 부담 증가 |
| Bucket | 공개/제한/raw/derived/synthetic의 storage·IAM·lifecycle 경계 | bucket 하나 안 prefix만으로 권리 class를 나누지 않음 |
| Prefix | `tenant_id/artifact_id/revision` 정리, lifecycle 조건과 관찰성 보조 | 이름 규칙은 IAM 독립 경계가 아니며 오분류에 취약 |
| Tenant | 모든 request·manifest·SA binding의 필수 속성 | 문자열만 넣고 물리 IAM을 공유하면 격리로 인정하지 않음 |

초기 pilot에서 tenant별 project가 과도하면 **tenant별 bucket + tenant 전용 SA + IAM deny/condition + 독립 KMS key**를 임시 대안으로 검토할 수 있다. 다만 같은 project의 project-level 권한이 모든 tenant bucket으로 확대되지 않는지 Workstream 60 공격 검증을 통과해야 하며, 고객 계약이 project 격리를 요구하면 대안은 사용할 수 없다.

## 4. 권리 gate

### 4.1 권리 record

단일 상태 문자열은 실제 권리를 충분히 표현하지 못한다. 각 `rights_snapshot`은 아래를 가진다.

- `rights_snapshot_id`, immutable version, `artifact_candidate_id`
- issuer/rightsholder, document/terms locator, retrieved/checked time
- `valid_from`, `valid_until`, revocation check source
- purpose, geography/region, tenant, audience, attribution/disclaimer
- 허용 processor: `DOCUMENT_AI`, `VERTEX_AI`, 기타 서비스별 allowlist
- 허용 동작: `LOCATOR`, `FETCH`, `PRIVATE_STORE`, `PROCESS_DOCUMENT_AI`, `PROCESS_VERTEX_AI`, `DISPLAY_INTERNAL`, `DISPLAY_EXTERNAL`, `REDISTRIBUTE`
- reviewer와 independent approver, approval target hash, append-only history anchor
- conflicting source 또는 미해결 질문

상태는 빠른 fail-closed 분류이고, 실제 허용은 상태와 action grant를 모두 통과해야 한다. 더 넓은 상태로 자동 승격하지 않는다.

### 4.2 상태별 기본 허용 행렬

`✓`는 해당 상태의 기본 허용 후보, `C`는 고객 계약의 명시적 action grant가 있을 때만, `—`는 금지다. 어떤 `✓`도 만료·철회·충돌 또는 tenant 불일치를 이기지 못한다.

| 상태 | locator | 다운로드 | 비공개 저장 | Document AI | Vertex AI | 내부 표시 | 외부 표시 | 재배포 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `RIGHTS_UNCONFIRMED` | ✓ | — | — | — | — | — | — | — |
| `METADATA_ONLY` | ✓ | — | — | — | — | metadata만 | — | — |
| `PRIVATE_COPY_ALLOWED` | ✓ | ✓ | ✓ | — | — | locator/metadata만 | — | — |
| `PROCESSING_ALLOWED` | ✓ | ✓ | ✓ | processor allowlist 시 ✓ | processor allowlist 시 ✓ | 검토자에게만 추출 후보 | — | — |
| `DISPLAY_ALLOWED` | ✓ | ✓ | ✓ | 명시 grant 필요 | 명시 grant 필요 | ✓ | — | — |
| `REDISTRIBUTION_ALLOWED` | ✓ | ✓ | ✓ | 명시 grant 필요 | 명시 grant 필요 | ✓ | audience/scope grant 시 ✓ | 동일 조건·attribution 시 ✓ |
| `CUSTOMER_RESTRICTED` | ✓ | C | C | C | C | C | C | C |
| `FORBIDDEN` | 거부 근거 locator만 | — | — | — | — | — | — | — |

운영 규칙:

1. `RIGHTS_UNCONFIRMED`, 충돌, 만료, 철회, approver 부재는 `RIGHTS_GATE_HOLD`와 assurance `HOLD`다.
2. 공개 URL, 검색 가능성, 로그인을 통한 열람 가능성은 `FETCH` 허용 근거가 아니다.
3. `PROCESSING_ALLOWED`는 서비스별로 나눈다. Document AI 허용이 Vertex AI 허용을 뜻하지 않는다.
4. `DISPLAY_ALLOWED` 기본 범위는 인증된 내부 reviewer UI다. 고객·대중 UI는 external grant가 필요하다.
5. `REDISTRIBUTION_ALLOWED`도 문서 전체, 발췌, 파생 사실, 고객 전달의 범위·attribution을 각각 기록한다.
6. `CUSTOMER_RESTRICTED`는 grant의 상한이 아니라 계약 overlay다. 모든 동작은 tenant, purpose, region, processor, retention, audience 조건을 만족해야 한다.
7. 현재 snapshot보다 좁아지거나 철회되면 raw 접근, 처리 queue, derived display, export와 signed URL 발급을 즉시 닫고 재검토한다.

## 5. Cloud Storage 보안 기준선

### 5.1 모든 raw bucket의 필수 설정

- Public Access Prevention `enforced`; 가능하면 organization/folder/project constraint와 bucket setting을 함께 사용한다.
- Uniform bucket-level access를 켜고 object ACL을 사용하지 않는다.
- raw object writer는 create-only. read, delete, IAM 변경 권한을 주지 않는다.
- 사람 계정은 group 기반 reviewer 역할만 받고 직접 upload/download 관리자 역할을 받지 않는다.
- ingest, validator, Document AI broker, Vertex AI broker, display broker, deletion worker를 서로 다른 SA로 분리한다.
- project-level broad Storage Admin/Owner/Editor를 runtime SA에 부여하지 않는다.
- 고객 SA에는 자신의 tenant project/bucket 이외 권한이 없어야 하며 control-plane service는 tenant binding을 요청과 manifest 양쪽에서 비교한다.
- bucket 이름이나 object metadata에 고객명, 원문 제목, BOM PN 같은 민감 정보를 넣지 않고 opaque ID를 사용한다.

IAM 최소 역할은 커스텀 역할을 우선 검토한다. ingest에는 create와 필요한 metadata read만, validator에는 quarantine read와 승인된 promote/copy만, processor에는 승인 generation read와 derived write만, display에는 display-eligible derived read만, deletion worker에는 승인 delete와 tombstone write만 부여한다. key 관리자, key 사용 주체, bucket 관리자, rights approver와 auditor는 분리한다.

### 5.2 Google 기본 암호화와 CMEK

| 선택 | 장점 | 비용·운영 부담 | 최소안 |
|---|---|---|---|
| Google 기본 암호화 | 별도 key resource·rotation·가용성 운영 없음, 모든 저장 데이터에 기본 적용 | 고객이 key lifecycle·crypto boundary를 직접 제어하지 못함 | 공개·일반 제한 자료의 시작점 후보 |
| CMEK | key location, rotation, IAM, disable/destroy와 key-use audit 제어; tenant별 crypto boundary 가능 | Cloud KMS key/version과 crypto operation 비용, key IAM·rotation·복구·지역 정합성 운영, key disable/destroy 시 데이터 접근 불능 위험 | 고객 계약·규제·crypto-shredding·tenant key 분리가 요구될 때 `Z3/Z4` 기본 후보 |

CMEK rotation은 이후 암호화 작업에 새 primary version을 사용하지만 기존 object를 자동으로 새 key version으로 다시 암호화했다는 가정은 금지한다. rewrite 계획과 비용을 별도로 승인한다. retention-locked object를 암호화한 key를 파괴해 데이터를 읽을 수 없게 만드는 행위는 삭제 계약과 감사 승인을 거쳐야 한다.

### 5.3 signed URL

기본은 인증된 application proxy다. signed URL이 꼭 필요하면 다음을 모두 요구한다.

- rights와 tenant가 유효한 특정 `bucket/object#generation`의 `GET` 한 동작만 허용
- 제안 TTL 5분 이하; 이는 SPECTRA 운영 상한이며 GCP 허용 최대치가 아님
- 발급자, 최종 사용자, tenant, artifact/generation, rights snapshot, 목적, 만료, 요청 ID 기록
- 1회성 application token 또는 redemption broker로 재사용·대량 발급을 탐지
- query string을 애플리케이션·분석 로그에 남기지 않음
- 권리 철회 시 신규 발급 즉시 차단; 이미 발급된 URL은 즉시 개별 취소할 수 없으므로 짧은 TTL과 signing key incident 절차로 잔여 위험 제한

signed URL은 소유자 인증 없이 소지자가 만료 전 사용할 수 있으므로 Cloud Storage 로그만으로 최종 수령 주체를 충분히 증명할 수 있다고 가정하지 않는다. 발급 broker의 별도 audit record가 필수다.

## 6. 무결성, overwrite 방지와 lineage

### 6.1 raw object identity

모든 raw object는 다음 tuple로 식별한다.

```text
raw_ref = {
  project_id,
  bucket_id,
  object_name,          # opaque artifact/revision ID
  generation,           # immutable Cloud Storage generation
  sha256,               # application-calculated bytes digest
  mime_declared,
  mime_detected,
  byte_size,
  source_locator,
  retrieved_at,
  rights_snapshot_id,
  tenant_id
}
```

- 첫 업로드는 `ifGenerationMatch=0` precondition을 사용한다. 같은 이름이 이미 있으면 `412`를 성공 재시도로 취급하지 않고 `RAW_OBJECT_ALREADY_EXISTS`로 종료한다.
- raw bytes를 overwrite하지 않는다. 정정·재수집은 새 `artifact_revision_id`와 새 object name/generation을 만들고 `supersedes`를 연결한다.
- read, copy, delete, promotion은 manifest의 exact generation precondition을 사용한다.
- SHA-256은 client-side 또는 승인 validator가 bytes에서 계산하며 provider checksum이나 ETag를 대신 쓰지 않는다.
- manifest는 object name만 참조하지 않고 exact generation과 SHA-256을 모두 요구한다.

### 6.2 공통 schema와 연결 키

현재 `raw-artifact-manifest.schema.json`은 artifact별 generation, tenant, rights snapshot, quarantine/validation 상태, detected MIME과 deletion lineage가 없다. `evidence-packet.schema.json`은 raw manifest를 직접 참조하지 않는다. Workstream 10에 다음 versioned 변경을 요청한다.

```text
RAW_ARTIFACT_MANIFEST v2
  manifest_id
  artifact_id + artifact_revision_id
  tenant_id + zone
  storage_ref {project, bucket, object, generation}
  integrity {sha256, byte_size, declared_mime, detected_mime}
  source {locator, retrieved_at}
  rights_snapshot_id
  validation {quarantine_status, malware_scan, mime_check, hash_check, reviewer}
  lineage {supersedes, derived_record_ids, deletion_state}

EvidencePacket vNext
  raw_manifest_refs[] {
    manifest_id, artifact_id, generation, artifact_sha256,
    rights_snapshot_id, source_locator, claim_locator_ids[]
  }
```

EvidencePacket은 연결 시 현재 object bytes의 SHA-256을 다시 계산하거나 검증된 immutable manifest digest를 확인한다. packet의 expected hash와 다르면 어떤 이름·locator가 같아도 `ARTIFACT_HASH_MISMATCH + PROVENANCE_FAILURE + HOLD`다.

### 6.3 중복

같은 tenant/rights zone 안에서 SHA-256 중복이 발견되면 새 원문으로 promote하지 않고 `DUPLICATE_ARTIFACT` 후보로 연결한다. 다른 tenant의 hash가 같아도 object 존재나 고객 identity를 노출하지 않으며 cross-tenant deduplication으로 물리 object를 공유하지 않는다. rights snapshot, locator와 customer deletion 의무가 다르기 때문이다.

## 7. 수명주기와 삭제

### 7.1 보호 기능의 차이

| 기능 | 보호 대상 | 읽기/비용 특성 | 최소 선택 |
|---|---|---|---|
| Soft delete | 최근 삭제된 object와 bucket의 복구 창 | soft-deleted bytes도 저장 비용 대상; 복원 전 읽을 수 없음 | raw bucket 7일 시작 후보. 고객 즉시 삭제 요구와 호환성 확인 필수 |
| Object Versioning | overwrite/delete 때 noncurrent version 유지 | version 수 기본 상한이 없고 각 version 저장 비용 발생; bucket 삭제 보호 아님 | create-only 설계에서는 기본 `OFF`; 필요 시 lifecycle로 version 수/기간 상한 |
| Retention policy | 정한 기간 전 object 삭제 금지 | lifecycle delete와 고객 삭제도 막을 수 있음 | 법적/계약 보존 기간 확정 전 raw에 적용하지 않음 |
| Bucket Lock/locked retention | retention policy 감소·제거를 사실상 되돌릴 수 없게 고정 | 잘못 고정하면 법적 삭제·고객 삭제와 충돌 | 이번 최소안 `OFF`; 법무·고객·보안 공동 승인 뒤 별도 bucket에만 적용 |

Cloud Storage의 현재 기본 soft delete가 7일일 수 있으므로 실제 bucket 생성 전 effective policy를 조회해 명시적으로 승인한다. “기본값이므로 결정하지 않았다”는 허용하지 않는다.

### 7.2 삭제 계약

1. ingest 전 `retention_basis`, `delete_by`, legal hold, soft-delete residual window와 log retention을 결정한다. 충돌하면 `RETENTION_DELETION_CONFLICT + HOLD`로 수집하지 않는다.
2. 삭제 요청이 오면 새 read/process/display/export/signed URL 발급을 먼저 막고 deletion case ID를 만든다.
3. exact raw generation, noncurrent/soft-deleted generation, derived facts, embeddings/index, caches, EvidencePacket decision eligibility와 export copy를 lineage graph로 열거한다.
4. 각 store에서 삭제 또는 접근 불능 처리하고 tombstone에는 opaque artifact ID, tenant, action time, actor, 법적 근거, 결과만 남긴다. 원문 title/URL/BOM 값은 audit에 불필요하면 남기지 않는다.
5. Cloud Audit Logs 등 삭제할 수 없거나 별도 보존 의무가 있는 기록의 범위와 기간은 고객 계약에 사전 고지한다. log에는 원문 내용이나 signed URL query를 넣지 않는다.
6. soft delete 기간 중 bytes가 물리적으로 잔존한다면 “완전 삭제”로 선언하지 않고 `DELETION_PENDING_EXPIRY`로 표시한다. 즉시 물리 삭제가 계약상 필요하면 soft delete 없는 별도 bucket 정책을 ingest 전에 승인해야 한다.

권리 철회는 삭제 요청과 동일한 access/display 차단을 즉시 수행하되, 보존 의무가 있으면 raw를 restricted quarantine으로 옮기는 것이 아니라 exact generation에 대한 접근을 닫고 별도 legal decision을 기다린다. 임의 copy는 새 권리 위반이 될 수 있다.

### 7.3 비용 상한

- upload gateway에서 source family별 MIME allowlist, object 최대 byte size, bundle 총량, tenant quota와 일/월 ingest quota를 검사한다. 값은 실제 sample과 budget 승인 전 미정이며, 미설정 상태에서는 실제 ingest `HOLD`다.
- `Content-Length`만 믿지 않고 stream byte count와 최종 object metadata를 비교한다.
- Object Versioning은 기본 off; 켤 경우 `numNewerVersions`/age lifecycle 상한과 비용 경보를 함께 승인한다.
- incomplete multipart/resumable upload, quarantine failure와 orphan derived object의 만료 정책을 둔다.
- storage class 전환은 access pattern과 minimum storage duration/early deletion 비용을 검토한 뒤 적용한다. 초기 소량 검토 원문은 Standard 후보이며 임의 Archive 이동은 하지 않는다.
- tenant별 stored bytes, object count, soft-deleted bytes, noncurrent bytes, Class A/B operations, retrieval/egress, log ingest, KMS operations, Document AI/Vertex AI usage를 budget dashboard의 별도 지표로 둔다.

## 8. 처리 경계와 안전 종료

### 8.1 gate 순서

| Gate | 필수 검사 | 실패 시 차단 |
|---|---|---|
| G0 Discovery | locator, issuer, terms locator, tenant | FETCH 이후 전부 |
| G1 Rights | action별 grant, approver, validity, processor/region/audience | 다운로드·저장·AI·표시·재배포 |
| G2 Upload/Quarantine | tenant route, create-only precondition, size/MIME allowlist | raw promotion·추출 |
| G3 Integrity/Safety | SHA-256, byte size, detected MIME, PDF parser sandbox/malware policy | Document AI·Vertex AI·review UI |
| G4 Processing Rights | exact service, purpose, region, logging/retention 조건 | 해당 AI 호출 |
| G5 Human Review | locator-resolved 값, identity, unit, applicability, approval target hash | derived approval·EvidencePacket decision |
| G6 Display/Export | current rights snapshot, tenant/audience, derived lineage | internal/external display·download |

악성 PDF 판정 도구와 정책은 아직 선택되지 않았다. scan engine/version/signature/time이 없는 `PASS`를 만들지 않으며, unknown/encrypted/active-content/polyglot PDF는 `MALWARE_SCAN_INCONCLUSIVE` 또는 `MIME_CONTENT_MISMATCH`로 quarantine에서 `HOLD`한다.

### 8.2 추출 실패와 tenant 혼선

- extraction timeout/필드 누락/단위 불명은 후보만 남기고 `EXTRACTION_FAILED` 또는 `EXTRACTION_INCOMPLETE`; 사람이 확인한 값으로 승격하지 않는다.
- request tenant, SA tenant binding, bucket project, manifest tenant, output tenant 중 하나라도 다르면 `TENANT_CONTEXT_MISMATCH`; read와 error detail의 교차-tenant 노출까지 차단한다.
- raw hash와 processing input hash가 다르면 processor를 호출하지 않는다.
- processing output은 `input_generation`, `input_sha256`, processor name/version/run ID, rights snapshot을 갖는다.
- 사람 승인 후 raw/rights/identity가 바뀌면 승인 target을 무효화하고 파생 display와 EvidencePacket을 `HOLD`로 전이한다.

## 9. 감사와 운영

### 9.1 감사 이벤트

Cloud Audit Logs의 Admin Activity는 기본 관리 변경 증거로 사용한다. Cloud Storage와 Cloud KMS의 Data Access `DATA_READ`/`DATA_WRITE`를 raw, derived, audit-control project에 명시적으로 켜는 것이 후보 기준선이다. Data Access logs는 기본 비활성일 수 있고 로그 양·비용이 커질 수 있으므로 실제 project에서 effective 설정과 예상량을 승인한다.

SPECTRA application audit는 다음을 추가한다.

- rights snapshot 생성·승인·만료·철회 주체
- 업로더/ingest SA, source locator, tenant route, raw generation/hash
- validator와 scan result/version
- Document AI/Vertex AI broker, processor, purpose, input generation, output ID
- reviewer/approver와 approval target/history anchor
- internal/external display, export, signed URL issuer/recipient/expiry
- delete requester/approver/worker, raw/derived/index/cache별 결과

로그 reader는 `Private Logs Viewer` 등 별도 auditor group으로 제한하고 workload는 audit event write-only로 둔다. log sink destination, retention 기간, tamper protection, 개인정보 최소화와 비용은 생성 전 결정한다.

### 9.2 운영 역할

| 역할 | 할 수 있는 일 | 할 수 없는 일 |
|---|---|---|
| Source registrar | locator/metadata 등록 | 원문 fetch, 권리 승인 |
| Rights reviewer/approver | action grant 검토/승인 | storage IAM·raw 수정, 기술값 승인 |
| Uploader/ingest SA | 승인 ticket으로 create-only quarantine upload | read/delete/overwrite/권리 변경 |
| Validator SA | exact generation 검사, promote 요청 | rights 승격, EvidencePacket 승인 |
| Processor broker SA | 현재 grant가 있는 generation만 지정 processor에 전달 | 임의 bucket list, 외부 display |
| Technical reviewer | 추출값과 locator 검토 | rights 승인, tenant IAM 변경 |
| Display broker | display-eligible derived 값만 제공 | raw unrestricted read, 권리 변경 |
| Deletion worker | 승인 case의 lineage 삭제 | 임의 delete, retention override |
| Security auditor | IAM/log/anchor read | data-plane write |

## 10. 필수 공격 사례

| 공격 | 탐지 조건 | 오류 코드 후보 | 차단되는 후속 단계 | 결과 |
|---|---|---|---|---|
| 공개 URL의 `RIGHTS_UNCONFIRMED` PDF 저장·처리 | rights snapshot 없거나 action `FETCH/PRIVATE_STORE/PROCESS_*` 미허용 | `RIGHTS_ACTION_NOT_ALLOWED` | download, upload, AI, display, packet link | `HOLD` |
| 고객 A 문서를 고객 B SA가 조회 | SA tenant binding, request tenant, project/bucket/manifest tenant 불일치 | `CROSS_TENANT_ACCESS_DENIED` | object metadata/read, error detail, derived query | `HOLD` |
| 같은 object name overwrite로 원문 교체 | create에 `ifGenerationMatch=0` 누락 또는 기존 live generation 존재 | `RAW_OVERWRITE_ATTEMPT` | promotion, extraction, manifest update | `HOLD` |
| 다른 hash를 기존 EvidencePacket에 연결 | packet expected hash/generation과 manifest/current bytes 불일치 | `ARTIFACT_HASH_MISMATCH` | rule evaluation, display/export | `PROVENANCE_FAILURE + HOLD` |
| 권리 만료·철회 뒤 derived display 지속 | display 시 current rights가 expired/revoked 또는 derived snapshot이 stale | `RIGHTS_REVOKED_DERIVED_STILL_ACTIVE` | display, export, signed URL, optimistic decision | `HOLD` |
| private bucket에서 signed URL 과다 발급 | tenant/user/artifact rate·동시 active URL·목적 상한 초과, long TTL | `SIGNED_URL_POLICY_VIOLATION` | URL issuance; active incident escalation | `HOLD` |
| soft delete/versioning 비용 무제한 증가 | soft-deleted/noncurrent bytes·version count·budget threshold 초과 또는 lifecycle 없음 | `STORAGE_RETENTION_BUDGET_EXCEEDED` | 신규 ingest/overwrite, policy 확대 | `HOLD` |
| 삭제 뒤 추출값·색인·log locator 잔존 | deletion graph의 required store가 미완료, log minimization/retention 예외 미기록 | `DELETION_PROPAGATION_INCOMPLETE` | deletion completion, future decision/display | `HOLD` |

추가 안전 종료:

| 조건 | 오류 코드 후보 | 결과 |
|---|---|---|
| MIME 선언과 magic/content 불일치 | `MIME_CONTENT_MISMATCH` | quarantine + `HOLD` |
| malware scan 실패·미결론 | `MALWARE_SCAN_INCONCLUSIVE` | processor/reviewer UI 차단 + `HOLD` |
| duplicate raw | `DUPLICATE_ARTIFACT` | 새 promotion 금지, 같은 tenant의 기존 ref 검토 |
| rights 상태 충돌·만료 | `RIGHTS_CONFLICT` / `RIGHTS_SNAPSHOT_EXPIRED` | 모든 확대 동작 차단 + `HOLD` |
| retention과 삭제 의무 충돌 | `RETENTION_DELETION_CONFLICT` | ingest 전 차단 + `HOLD` |

## 11. 실제 resource 생성 전 승인 항목

### 11.1 결정 필요

- organization/folder/project 구조, billing account와 project owner
- 고객 tenant별 project 대 bucket 대안의 선택과 예외 기준
- data residency, Cloud Storage/Document AI/Vertex AI/KMS region 정합성
- bucket 수·이름, Standard/기타 storage class, soft delete 기간
- Object Versioning, retention policy, Bucket Lock 사용 여부와 법적 삭제 matrix
- default encryption 대 CMEK, key project/location/rotation/destroy/recovery 책임
- service account 목록, custom IAM roles, break-glass와 access review 주기
- Data Access logs 범위, log sink/retention, 개인정보 최소화
- signed URL 사용 여부와 TTL/rate/recipient audit
- MIME/size/quota, malware/PDF sandbox, retry와 quarantine expiry
- budget amount, alert recipients, per-service quota와 자동 ingest circuit breaker

### 11.2 승인 전 실행하면 안 되는 명령 범주

사용자와 Control Tower가 위 결정을 승인하고 예상 비용을 검토하기 전 다음 명령·API 호출은 금지한다.

- `gcloud projects create`, billing account link, service/API enable
- `gcloud storage buckets create/update`, object upload/copy/delete
- IAM policy binding, service account/key 생성
- KMS key ring/key/version 생성·rotation·disable/destroy
- Audit Logs 설정, log sink/bucket 생성
- Document AI processor와 Vertex AI endpoint/job 호출
- budget, alert, quota 또는 retention lock 변경

### 11.3 비용 항목

금액은 region, storage class, 데이터량, 요청량과 계약이 없으므로 현재 확정하지 않는다. 견적에는 최소 다음을 포함한다.

- live, noncurrent, soft-deleted, quarantine raw와 derived storage GB-month
- Class A/B operation, restore, retrieval, early deletion, egress/region transfer
- Cloud Logging Data Access ingest·retention·sink storage와 query
- Cloud KMS key version 및 cryptographic operations, rotation/rewrite
- Document AI page processing, Vertex AI tokens/embedding/index/grounding
- malware scanning/sandbox compute와 queue, metadata database
- tenant별 project 고정 운영, monitoring, budget/alert와 인력 key/rights review 비용

실제 budget 숫자와 alerts가 승인되기 전 실제 ingest와 AI processing은 `HOLD`다.

## 12. Git 정책

Git에 둘 수 있는 것은 schema, manifest의 비민감·권리 허용 metadata, 소형 `SYNTHETIC` fixture, 문서와 테스트 코드뿐이다. 다음은 Git 금지다.

- 실제 PDF, 모델 output bundle, BOM, 고객 문서와 원문 발췌
- signed URL, credential, service account key, access token, KMS material
- 민감 source locator, 고객명/tenant mapping, 원문을 복구할 수 있는 대형 encoding
- 실제 원문과 같은 것으로 오인될 수 있는 fixture

manifest를 Git에 두려면 object URI를 opaque logical ref로 치환하고 tenant·권리 검토를 통과해야 한다. hash도 해당 고객/문서의 존재를 누설할 위험이 있으면 control store에만 둔다.

## 13. Workstream 전달 요구사항

### Workstream 10 — Contracts & Schema

- `RAW_ARTIFACT_MANIFEST v2`, `rights_snapshot`, exact generation과 tenant/zone 필드
- EvidencePacket의 `raw_manifest_refs[]`와 rights/display eligibility
- rights, integrity, processing status와 assurance decision을 서로 다른 축으로 유지
- deletion tombstone/lineage와 stable error code enum

### Workstream 30 — Environment Model

- provider별 `FETCH/PRIVATE_STORE/PROCESS/DISPLAY/REDISTRIBUTE` 권리 확인
- raw bundle allowlist, expected MIME/size, model run/terms snapshot과 generation linkage
- 실제 run 전 승인 tenant/zone과 source completeness gate

### Workstream 40 — Parts Evidence

- 문서별 action grant와 고객 계약 overlay를 v2 source rights에 연결
- exact PDF locator, artifact hash, claim locator와 deletion lineage 요구
- 승인 BOM owner, tenant, retention/processor permission 없으면 ingest `HOLD`

### Workstream 50 — Mitigation & Policy

- policy pack/custom exception approval history head를 `Z6_AUDIT_CONTROL` anchor에 연결
- rights 철회·raw 삭제 시 transitive decision operand와 기존 지원 판정 무효화

### Workstream 60 — Assurance & Evals

- 10절 공격 8건과 MIME/malware/duplicate/retention conflict paired fixtures 구현
- IAM cross-tenant deny를 실제 배포 전 emulator 또는 isolated test project에서 검증
- rights expiry/revocation과 deletion propagation 후 display·decision false PASS 0 확인

## 14. 공식 GCP 근거와 확인 범위

공식 문서는 `2026-08-20`에 확인했다. 실제 console/project 설정은 조회하지 않았다.

| ID | 공식 문서 | 이 설계에서 사용한 내용 |
|---|---|---|
| G1 | [Public access prevention](https://docs.cloud.google.com/storage/docs/public-access-prevention) | bucket 또는 organization policy로 anonymous/public grant 차단 |
| G2 | [Uniform bucket-level access](https://docs.cloud.google.com/storage/docs/uniform-bucket-level-access) | ACL을 끄고 bucket-level IAM만 사용 |
| G3 | [Cloud Storage overview](https://docs.cloud.google.com/storage/docs/introduction) | object generation identity, 기본 7일 soft delete 설명 |
| G4 | [Object Versioning](https://docs.cloud.google.com/storage/docs/object-versioning) | noncurrent version, bucket deletion 한계, version 수·비용 상한 없음, soft delete 권고 |
| G5 | [Object Lifecycle Management](https://docs.cloud.google.com/storage/docs/lifecycle) | delete/class transition와 retention/hold의 상호작용 |
| G6 | [Request preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions) | generation-match로 race/overwrite 방지, mismatch 시 412 |
| G7 | [CMEK for Cloud Storage](https://docs.cloud.google.com/storage/docs/encryption/customer-managed-keys) | 기본 암호화와 CMEK의 key lifecycle·rotation·audit·접근불능 위험 |
| G8 | [Signed URLs](https://docs.cloud.google.com/storage/docs/access-control/signed-urls) | URL 소지자는 만료 전 계정 없이 접근 가능 |
| G9 | [Enable Data Access audit logs](https://docs.cloud.google.com/logging/docs/audit/configure-data-access) | Data Access 기본 비활성 가능성, 명시 활성화와 로그 비용 |
| G10 | [Cloud Storage access logs](https://docs.cloud.google.com/storage/docs/access-logs) | 대부분의 API audit에는 Cloud Audit Logs 권장, usage log의 용도와 한계 |
| G11 | [Cloud Storage pricing](https://cloud.google.com/storage/pricing) | live/noncurrent/soft-deleted bytes, operations, restore·network 등 비용 구성 |

이 공식 문서는 GCP 기능 동작을 뒷받침하며 개별 원문의 저장·처리·표시·재배포 권리를 부여하지 않는다.

## 15. 미결정과 현재 판정

- 실제 GCP organization/project/billing/region/budget owner: 미정
- tenant 수와 고객 계약, DPA/NDA, data residency: 없음
- CMEK 의무와 key owner/rotation/destroy 절차: 미정
- soft delete/retention/log retention과 삭제 SLA: 미정
- malware scanner/PDF sandbox, 최대 file/bundle/quota: 미정
- Document AI/Vertex AI processor별 권리·region·logging 조건: 미승인
- Data Access log 예상량과 보존 기간: 미정
- 실제 resource, raw artifact, run, cost evidence: 모두 0

따라서 문서 설계 패키지만 `READY_FOR_REVIEW` 후보이며 실제 ingest, processing, display, Stage 7 완료는 `HOLD`다.

## 16. 작업 패키지 2 — Rights/Raw Manifest Preflight

### 16.1 발행 계약

`preflight/raw_manifest_preflight.py`는 candidate manifest와 object creation receipt를 읽기 전용으로 검사한다. 파일·GCP object·권리 record를 생성하지 않는다.

| 결과 | 의미 | manifest 반환 |
|---|---|---|
| `RAW_MANIFEST_ISSUABLE / ISSUE_ALLOWED` | schema와 모든 발행 gate 통과 | 입력 candidate의 복사본; 실제 저장은 별도 승인 작업 |
| `RAW_MANIFEST_HOLD_NOT_ISSUED / HOLD_NOT_ISSUED` | 하나 이상의 차단 code | 항상 `null` |

통과해도 raw provenance 발행 가능성만 뜻하며 radiation assurance는 `HOLD`다. 합성 정상 fixture의 `ISSUE_ALLOWED`를 실제 GCP object나 실제 권리 승인 증거로 승격하지 않는다.

필수 gate:

1. `raw-artifact-manifest-v2.schema.json` 검증
2. placeholder가 아닌 provider-issued job reference
3. request/manifest/rights/artifact/creation receipt의 tenant와 zone 일치
4. `IF_GENERATION_MATCH_0`, creation outcome `CREATED`, exact generation
5. active rights status, approval target hash, history anchor
6. 최소 `FETCH`와 `PRIVATE_STORE` action grant; 요청한 추가 action도 각각 `ALLOWED`
7. artifact SHA-256, byte size, detected MIME와 creation receipt 일치
8. quarantine `VALIDATED`, malware `PASS`, MIME/hash `MATCH`, reviewer/time
9. parser input bundle hash와 manifest bundle hash 일치

검사 우선순위는 schema/input 오류를 `INVALID_INPUT`, rights expiry/revocation을 `STALE_EVIDENCE`, 그 밖의 발행 실패를 `PROVENANCE_FAILURE`로 반환한다. 모든 실패의 assurance는 `HOLD`다.

### 16.2 공격 fixture

합성 fixture는 정상 발행 후보 1개와 다음 공격을 최소 차이 mutation으로 검증한다.

- existing object에 대한 overwrite 시도
- creation receipt와 manifest generation 불일치
- rights snapshot 누락, 만료, 필수 action 미승인
- request와 manifest의 cross-tenant 혼선
- 실제 관찰 receipt와 manifest SHA-256 불일치
- detected MIME 불일치
- malware scan 미통과
- reviewer/review time 누락

실제 후보 fixture는 raw bytes·수치·PDF를 포함하지 않고 reference-only gap만 보존한다. SPENVIS는 provider job reference, active rights approval, tenant/zone, immutable cloud generation이 없어 `HOLD_NOT_ISSUED`다. TI locator는 fetch/private-store 권리, 승인 tenant/storage generation과 review가 없어 `HOLD_NOT_ISSUED`다.

### 16.3 SPENVIS 권리 문의

`SPENVIS_RIGHTS_INQUIRY_DRAFT.md`는 한 번의 문의에 non-commercial research, commercial evaluation/product, automation, local/private cloud storage, deterministic/Document AI/Vertex AI processing, internal/external display, raw/derived redistribution, retention/deletion과 third-party model 조건을 분리해 묻는다. stable provider job/run reference와 hash provenance 표시 권리도 함께 확인한다.

초안은 `DRAFT_NOT_SENT`다. 회신이 일부 action만 답하면 나머지를 허용으로 추론하지 않는다. 회신 원문 보관, rightsholder 확인, independent approval과 action별 snapshot이 끝나기 전 실제 manifest 발행은 계속 `HOLD`다.

## 17. H03 — malformed input와 storage receipt binding 보완

### 17.1 Control Tower 결함 재현과 원인

H02는 candidate schema 오류를 기록한 뒤에도 semantic collection/hash/map 순회를 계속했다. 따라서 rights action·artifact ID·receipt ID의 list와 string 형태 malware scan에서 Python `TypeError`/`AttributeError`가 발생했다. 또한 receipt가 artifact ID/revision, generation, hash, size, MIME만 가졌기 때문에 manifest의 `project_id`, `bucket_id`, `object_name`을 바꿔도 다른 object의 receipt를 재사용할 수 있었다.

### 17.2 H03 검증 순서

1. request가 object가 아니면 `PREFLIGHT_INPUT_INVALID`로 즉시 종료한다.
2. Workstream 70 내부 `preflight-request.schema.json`이 request context, required action, receipt collection과 모든 receipt field의 자료형을 검사한다.
3. `candidate_manifest=null`은 reference-only 상태로 `RAW_MANIFEST_CANDIDATE_MISSING`을 반환한다.
4. candidate manifest schema 오류가 하나라도 있으면 semantic traversal을 수행하지 않고 `RAW_MANIFEST_SCHEMA_INVALID`로 반환한다. top-level rights object 자체가 없으면 안전한 membership 검사로 `RIGHTS_SNAPSHOT_MISSING`만 추가한다.
5. schema-valid candidate에서만 set/map key, timestamps, validation object와 receipt를 순회한다.
6. receipt는 `(artifact_id, artifact_revision_id)`로 정확히 1개여야 하고, manifest와 `project_id/bucket_id/object_name/generation` 전체가 일치해야 한다.
7. project/bucket/object 또는 generation이 다르면 `RAW_STORAGE_REF_MISMATCH`; generation mismatch에는 기존 `RAW_GENERATION_MISMATCH`도 함께 반환한다.
8. manifest artifact에 대응하는 receipt가 없으면 `OBJECT_CREATION_RECEIPT_MISSING`, 동일 key가 여러 개면 `DUPLICATE_OBJECT_CREATION_RECEIPT`, manifest에 없는 key면 `UNEXPECTED_OBJECT_CREATION_RECEIPT`다.

모든 오류 결과는 `RAW_MANIFEST_HOLD_NOT_ISSUED`, `HOLD_NOT_ISSUED`, `manifest=null`, assurance `HOLD`다.

### 17.3 schema 소유권 경계

`preflight-request.schema.json`은 Workstream 70의 실행 adapter 입력 계약으로만 추가했다. 공용 `raw-artifact-manifest-v2.schema.json`은 수정하지 않았다. 향후 creation receipt를 공용 EvidencePacket 또는 manifest 계약에 포함하려면 Workstream 10이 다음 필드를 versioned schema로 소유해야 한다.

- `artifact_id`, `artifact_revision_id`
- `project_id`, `bucket_id`, `object_name`, `generation`
- create precondition과 creation outcome
- observed SHA-256, byte size, detected MIME
- observer/source와 실제 GCP audit reference

H03 합성 receipt에는 observer나 실제 Cloud Audit reference가 없으며 실제 GCP 관찰 증거로 사용할 수 없다.

### 17.4 declared gap 경계

`real-candidate-holds.json`의 gap은 preflight가 SPENVIS/TI 외부 상태를 확인해 산출한 결과가 아니다. Workstream 30/40의 현재 상태를 reference-only request가 `declared_preflight_gaps`로 전달한 것이다. 테스트 이름도 `declared_gap_reference...`로 고정했다. gap 선언이 없거나 축소돼도 `candidate_manifest=null` 자체가 `RAW_MANIFEST_CANDIDATE_MISSING`으로 발행을 차단한다.
