# 40 Parts Evidence Handoff

## Status

`VERIFIED`

`40-parts-evidence-contract-and-adversarial-fixture-spec-v1` 문서 계약 패키지는 Control Tower 독립 검증을 통과했다. 실제 v2 schema·fixture 구현이나 Stage 4 완료를 뜻하지 않으며, 직전 출처·권리 조사 패키지의 `INTEGRATED` 판정은 유지한다. 실제 BOM과 권리 확인 원문이 없으므로 evidence ingest와 assurance decision은 계속 `HOLD`다.

## 조사 범위와 소유 파일

- 세션 ID: `40-parts-evidence`
- 현재 패키지: `40-parts-evidence-contract-and-adversarial-fixture-spec-v1`
- 기준선: Parts 조사 통합 commit `ed4e0f8`과 그 이후 Control Tower 기록 commit `375763c`; 다른 Workstream의 미통합 변경에는 의존하지 않음
- 읽기 전용 확인: 루트 개요·로드맵·체크리스트, Workstream 운영 규칙, Stage 1 계약, 현재 공통 schema와 schema validator/fixture 구조
- 변경: `docs/workstreams/40-parts-evidence/BRIEF.md`
- 변경: `docs/workstreams/40-parts-evidence/RESEARCH.md`
- 변경: `docs/workstreams/40-parts-evidence/CURRENT.md`
- 공통 schema, 계약, 루트 문서, 다른 Workstream 파일은 수정하지 않음
- 현재 작업트리의 Control Tower 문서, 공통 schema 3건, schema validator·fixture와 `.obsidian/` 변경은 사용자/다른 Workstream 소유로 보존했으며 이번 패키지에서 수정하거나 근거로 채택하지 않음
- 이번 패키지는 commit·push하지 않음

## 공식 출처와 권리 상태

- NASA GSFC Radiation Data Base: GSFC 부품 시험 보고서의 직접 discovery 경로. 현재 NEPP 임시 호스팅이며 문서별 copyright/third-party 표시를 확인해야 한다.
- NASA NEPP/NTRS: 시험·보증 방법과 NASA 문서 식별 경로. NTRS OpenAPI·bulk metadata 경로와 NASA STI 이용 조건을 확인했다.
- ESA ESARAD: ESA/계약 파트너 SEE·TID·DD 공개 색인. 보고서 다운로드 로그인, traceability·최신본 비보증, 요약 재현 조건을 확인했다.
- ESCIES/ESCC: TID 22900, SEE 25100 방법론 참고. 부품 시험 결과를 대신하지 않는다.
- 제조사: 제품별 report·datasheet·SMD/VID·PCN을 제공할 수 있으나 TI, Microchip, AMD, Infineon의 약관과 제한 범위가 다르다. 공개 열람을 재배포 허가로 보지 않는다.
- 고객 자료: 권한·격리·목적·보존·삭제·LLM 처리 승인이 없으므로 수집하지 않았다.
- 권리 상태는 문서별 `access_status`, `rights_status`, `allowed_actions`, terms URL과 원문 위치로 다시 확인하도록 설계했다.

## 부품 식별·적용성 규칙

- 실제 후보는 승인된 BOM의 `manufacturer + exact orderable part number`에서만 시작한다.
- package/grade/process/die/lot/date code의 누락은 `PARTIAL_UNRESOLVED`, 확인된 모순은 `CONTRADICTED`, generic/family 일치는 `FAMILY_ONLY`다.
- 누락과 모순을 모두 exact match로 만들지 않는다. 유사 부품은 추가 조사 후보일 뿐 지원 근거가 아니다.
- 시험과 임무의 TID material/dose/dose rate/bias/anneal/temperature, SEE particle/energy/LET/range/angle, 전압/mode/온도, sample/lot/statistical basis, report revision/PCN을 항목별 비교한다.
- 한 항목이라도 차단형이면 전체 trace를 `APPLICABLE`로 만들지 않는다.
- BOM 부재는 `BOM_MISSING`; 실제 부품 선정과 ingest는 `HOLD`다.

## 증거 정규화 초안과 영향

- `PART_TEST_EVIDENCE v2`의 최상위, identity, source/rights/locator, review, event별 필드를 `required / optional / conditional / forbidden`으로 구체화했다.
- H02에서 `record_sha256`/`approved_record_sha256`를 v2 금지 필드로 바꾸고, evidence content·approval target·review history entry hash를 서로 다른 projection으로 분리했다. JCS canonicalization, set/sequence 배열 규칙, 검증 순서와 content/review 수정별 supersedes 관계를 명시했다.
- exact PN을 required claim wrapper로 바꿔 `NOT_REPORTED`인 discovery record도 schema-valid하게 했다. 승인 family relation이 있으면 `FAMILY_ONLY`, 없으면 `PARTIAL_UNRESOLVED`, verified mismatch 또는 `CONFLICTING`이면 `CONTRADICTED`다.
- `CONFLICTING` claim은 top-level value 대신 최소 2개의 `alternatives[]`를 요구하며 각 대안에 서로 다른 canonical value, source claim identity와 유효 locator를 보존한다. 대안 누락·locator 누락·중복 값과 decision 사용을 fail-closed로 막는다.
- v1 additive 확장은 현재 `additionalProperties: false`와 충돌하고 legacy/new 필드의 이중 진실을 만들 수 있어 실제 Stage 4 경로로 권고하지 않는다. v1 합성 기준선은 동결하고 별도 v2 validator를 두는 방안을 Workstream 10 변경 요청으로 남겼다.
- v1→v2 adapter는 누락값을 생성하지 않고 `NOT_REPORTED`와 blocking gap으로 변환하며, artifact hash·locator·재승인 전에는 decision 입력을 금지한다.
- identity 판정 우선순위는 `INVALID_INPUT` → `CONTRADICTED` → `FAMILY_ONLY` → `PARTIAL_UNRESOLVED` → `EXACT_MATCH`다. 확인된 모순이 누락보다 우선하며, family와 unresolved는 모두 decision-ineligible이다.
- TID, SEU, SEL, SEB, SEGR을 독립 event record로 분리했다.
- TID의 시험 도달량과 규격 내 확인량, dose rate·bias·anneal을 분리한다.
- SEU는 curve point, particle/LET/energy, event count, fluence, bit/device denominator와 fit을 기록한다.
- SEL은 current threshold/limit/recovery/latent damage, SEB·SEGR은 power bias와 safe operating boundary·failure criterion을 각각 기록한다.
- `no event observed`는 면역이 아니며 조건·fluence·sample·통계 경계가 없으면 `HOLD`다.
- Stage 3에는 spectrum/LET/energy와 TID material contract, Stage 5에는 개별 destructive failure mode 정책, Stage 6에는 identity·event substitution·range extrapolation 공격 fixture, Stage 7에는 rights-gated 격리 저장·IAM/KMS·hash/audit 경로가 필요하다.
- 공통 schema에는 identity 확장, 구조화된 rights, artifact/record hash 분리, claim locator, event별 results, review history, structured applicability가 필요하다. Workstream 10 검토 전 수정하지 않았다.
- suffix 제거, manufacturer alias, process/die/lot 불일치, SEU→SEL 대체, zero-event 면역 승격, 최대 조사량→보증 등급 승격, 범위 외삽, hash·locator·review 누락·불일치, legacy dual truth를 차단하는 합성 공격 fixture 명세를 입력 변이·기대 코드·안전 종료 상태 수준으로 작성했다.
- H02로 self-reference 없는 정상 hash chain, content/history 변조, family/unresolved/exact conflict paired case, `CONFLICTING` 대안 정상·누락·중복·decision 공격 fixture를 추가했다.
- Workstream 10·30·50·60·70이 구현할 입력, 출력, 오류 코드와 Exit Gate를 각각 명시했다. 현재 패키지는 변경 요청이며 공통 schema나 타 Workstream 구현을 직접 변경하지 않았다.

## 검증 결과

- H02 깨끗한 `375763c` snapshot에서 `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 통과; exit 0
- 같은 snapshot에서 `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py` — 위 schema 검증 재통과 및 simulation test 19개 통과; exit 0
- H02 현재 작업트리에서 동일 명령 재실행 — 병렬 Workstream 변경을 포함한 schema 11개, 정상 fixture 2개, 실패 fixture 47개와 simulation test 19개 통과; 모두 exit 0
- `git diff --check` — 통과
- 위 검증은 기존 v1 계약·합성 simulation 회귀 결과다. 이번 문서에서 명세한 v2 schema와 공격 fixture는 아직 Workstream 10·60이 구현하지 않았으므로 실행 검증 완료로 표시하지 않는다.
- 검증 시 작업트리에 다른 Workstream의 미통합 공통 schema 변경이 존재했다. 테스트 통과 사실은 기록하되, 그 변경을 이번 패키지의 기준선이나 승인 근거로 사용하지 않는다.

## 실제 데이터 사용 여부

- 실제 시험 수치: 사용하지 않음
- 실제 부품 후보 5~10종: 선정하지 않음
- 실제 시험 PDF: 다운로드·저장하지 않음
- 실제 artifact hash·locator: 생성하지 않음
- 임의 confidence·통계 경계·보증 등급: 생성하지 않음
- 고객 문서/BOM: 접근·수집하지 않음
- `PUBLISHED`, `CUSTOMER_VERIFIED`, 실제 `CALCULATED` EvidencePacket: 생성하지 않음
- 조사에는 공식 웹페이지와 문서의 존재·필드·이용 조건만 사용했다.

## HOLD와 알려진 한계

- `BOM_MISSING`: 실제 부품 후보 선정 불가
- `RIGHTS_UNRESOLVED`: GSFC/NEPP·ESA·제조사 개별 원문의 저장·추출·재배포 권리를 문서별로 아직 확인하지 않음
- `ORIGINAL_UNAVAILABLE`: ESARAD 일부 보고서는 로그인 없이 원문 확인 불가
- `MANUFACTURING_CHANGE_UNKNOWN`: 실제 후보가 없어 PCN/process/die/lot/date code 비교 미수행
- `MISSION_ENVIRONMENT_UNAVAILABLE`: Stage 3의 SEE spectrum/LET 경로가 없어 적용성 계산 미수행
- `SCHEMA_CHANGE_PENDING`: Workstream 10이 v2 schema, version dispatch, non-filling adapter와 semantic gate를 구현·검토해야 함
- `ADVERSARIAL_FIXTURES_PENDING`: Workstream 60이 명세된 합성 artifact/fixture와 기대 오류 코드를 구현·실행해야 함
- `POLICY_OWNER_UNASSIGNED`: event별 필수 identity·임무 적용성·destructive SEE 종료 규칙의 승인 owner가 미지정
- `APPROVED_STORAGE_UNAVAILABLE`: 권리 상태에 따라 원문을 격리·보존할 승인 저장소/IAM/KMS/audit 경로가 미지정
- ESARAD 기여 안내의 public/internal 문구가 반대로 보이는 모순은 ESA 확인 전 운영 규칙으로 사용하지 않음
- 이 조사 결과는 법률 자문, 부품 인증, 비행 적합성 결론이 아니다.

## Control Tower 확인 요청

- 현재 패키지의 `PART_TEST_EVIDENCE v2` 선택과 additive 확장 배제 근거를 검토해 달라.
- H02의 세 수정 사항—hash projection 경계, exact PN claim 상태 전이, `CONFLICTING alternatives[]`—가 자기참조·도달 불가 상태·값 보존 모순을 해소했는지 재검토해 달라.
- Workstream 10에 v2 schema/version dispatch/non-filling adapter/identity·provenance semantic gate 구현을 할당해 달라.
- Workstream 60에 명세된 공격 fixture를 실제 fixture bytes·실제 계산 hash·유효/무효 locator를 사용해 구현하고 expected code를 검증하도록 할당해 달라.
- Workstream 30·50·70에 각각 환경 비교 contract, 사건별 정책, rights-gated storage 계약과 Exit Gate 확인을 요청해 달라.
- 기존 `RESEARCH.md`의 출처·권리 분류가 프로젝트의 공개 데모와 향후 상업 이용 범위를 충분히 차단하는지 계속 검토해 달라.
- 실제 후보 선정을 시작할 승인 BOM과 최소 identity 필드의 owner를 지정해 달라.
- 누락 identity를 mismatch와 구분하는 의미 gate 변경이 기존 False PASS 방어를 약화하지 않는지 검토해 달라.
- 실제 원문 수집 전 권리 검토 책임자와 승인 가능한 storage를 지정해 달라.
- 독립 검토 전 `VERIFIED`, `INTEGRATED`, Stage 4 완료 또는 루트 체크리스트 `[x]`로 변경하지 말아 달라.

## 이전 패키지 Control Tower 독립 검증 — 2026-08-19

- 판정: `INTEGRATED` — **출처·권리·identity·적용성 조사·설계 패키지**만 검증·통합했다. Stage 4 실제 증거 경로 완료 판정이 아니다.
- 공식 출처: NASA·ESA·ESCIES·제조사 공식 URL 16개의 접근 상태를 확인하고, NASA GSFC DB·NASA STI/NTRS·ESARAD·ESA copyright·ESCC 22900/25100의 핵심 주장을 원문에서 재현했다.
- 방법론 대조: NASA NEPP 자료에서 lot/date code·technology·process·bias·application 조건과 lot별 변동 위험을 확인했고, ESCC 22900/25100에서 TID와 SEE의 독립 시험 조건·단위·보고 필드를 확인했다.
- 계약 대조: 현재 identity 의미 검증, 단일 `content_hash`, 자유형 rights, 단일 `cross_section`, 제한된 `test_conditions`, 문자열 applicability와 destructive SEE boolean의 확장 필요성이 실제 Stage 1 schema와 일치한다.
- 재실행: `python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 통과.
- False PASS 검토: BOM 부재, family-only·부분 식별·모순, 사건 유형 대체, zero-event 면역 승격, 권리·hash·locator·review 누락을 모두 지원 근거에서 제외한다.
- 데이터 분류: 실제 BOM·부품 후보·시험 수치·시험 PDF·고객 자료·실제 EvidencePacket은 모두 0건이다.
- 제한: Microchip 약관은 이번 자동 접근에서 403으로 원문 재확인하지 못했다. 문서가 해당 권리를 `RIGHTS_UNRESOLVED`로 유지하므로 운영 허가 근거로 사용하지 않는다.

## 이전 패키지 Git 통합

- 브랜치: `main`
- 검증된 통합 commit: `ed4e0f8` — `docs(parts): integrate verified Stage 4 evidence research`
- 원격: `origin` (`https://github.com/WeepingHeron/SPECTRA.git`), push 완료
- 제외: 사용자 소유의 미추적 `.obsidian/`
- 현재 계약·공격 fixture 명세 패키지: 미커밋·미푸시, Control Tower 검토 대기

## Control Tower 독립 검증 — 2026-08-20

- 판정: `CHANGES_REQUESTED`
- 검토 범위: `40-parts-evidence-contract-and-adversarial-fixture-spec-v1`의 문서 계약과 공격 fixture 명세만 검토했다. 직전 출처·권리 조사 패키지의 `INTEGRATED` 판정은 유지한다.
- 깨끗한 기준선 재실행: commit `375763c` archive에서 schema 9개, 정상 fixture 1개, 실패 fixture 27개와 simulation test 19개가 모두 통과했다.
- 현재 작업트리 참고 재실행: 병렬 Workstream 10의 미통합 변경을 포함한 schema 11개, 정상 fixture 2개, 실패 fixture 47개와 simulation test 19개가 통과했다. 이 결과는 Workstream 40 승인 근거로 사용하지 않았다.
- 문서 구조 검사: 필수 16~22절이 존재하고 공격 fixture ID 17개가 모두 고유하며 `git diff --check`가 통과했다.
- 원문 대조: ESCC 22900의 TID dose rate·bias·anneal·temperature·sample 조건과 ESCC 25100의 독립 SEE mode·fluence·cross-section 조건이 명세 방향과 일치한다.

### 수정이 필요한 계약 모순

1. `record_sha256`를 “canonical v2 record bytes의 실제 hash”로 정의하면서 동일 record 안에 `record_sha256`, `approved_record_sha256`와 history의 record hash를 넣었다. hash 대상 projection과 제외 필드가 없어 자기참조가 발생한다. evidence content hash와 review-entry/hash-chain 범위를 분리하고 canonicalization·제외 필드·검증 순서를 명시해야 한다.
2. `orderable_part_number.raw/canonical`을 항상 `required`로 두었지만 identity gate는 exact PN을 확인하지 못한 유효 후보를 `FAMILY_ONLY`로 분류한다. 현재 명세대로면 해당 후보는 schema 단계에서 `INVALID_INPUT`이 되어 `FAMILY_ONLY`에 도달할 수 없다. exact-PN claim wrapper 또는 discovery candidate 타입을 분리하고 도달 가능한 상태 전이를 명시해야 한다.
3. claim의 `value`를 `CONFLICTING`에서 `forbidden`으로 정의하면서 동시에 충돌한 각 값과 locator를 보존하도록 요구한다. 충돌 대안의 값·locator를 담는 명시적 `alternatives[]` 구조 또는 동등한 discriminated union이 필요하다.

### 재검증 Exit Gate

- 위 세 모순을 `RESEARCH.md`의 필드 표, 상태 전이, migration 및 관련 공격 fixture에 일관되게 수정한다.
- self-reference 없는 canonical hash 예시와 변조 공격을 명세한다.
- exact PN 미확인 family 후보, exact PN 누락 unresolved 후보, verified PN conflict의 paired fixture 상태를 구분한다.
- `CONFLICTING` 값 두 개와 각각의 유효 locator를 보존하는 정상 예시와 누락 공격을 추가한다.
- 다음 handoff는 기존 번호 없는 제출을 암묵적 `H01`로 보고 `/Users/taehoon/Downloads/SPECTRA_40_PARTS_EVIDENCE_HANDOFF_H02.md`로 작성한다.
- Workstream 40은 다시 `READY_FOR_REVIEW`까지만 요청하며 공통 schema, 다른 Workstream 변경, commit·push를 수행하지 않는다.

## H02 변경 요청 반영 — 2026-08-20

- hash 자기참조: `record_sha256`와 `approved_record_sha256`를 v2에서 금지하고, `evidence_content_sha256`, `approval_target_sha256`, `history[].entry_sha256`의 projection과 제외 필드를 분리했다.
- canonicalization: RFC 8785 JCS, UTF-8/no BOM, set 배열별 stable key, sequence 배열 보존, history append order와 실제 SHA-256 재계산 순서를 명시했다.
- history 변조 방어: 승인·decision record의 history head를 외부 append-only audit/object generation에 고정해 공격자가 전체 chain을 다시 계산해도 이전 anchor와의 불일치를 검출하도록 했다.
- 수정 이력: evidence content 변경과 review assertion 변경의 hash 영향 및 `supersedes_evidence_content_sha256`/`supersedes_approval_target_sha256`를 분리했다. 정상 append는 content/approval target을 바꾸지 않고 새 history entry hash만 만든다.
- family 도달성: `record_purpose`와 exact PN claim wrapper를 도입해 family discovery와 unresolved discovery를 schema-valid하게 보존하면서 둘 다 decision 사용을 차단했다. verified exact PN conflict와 identity `CONFLICTING`은 항상 `CONTRADICTED`다.
- conflicting 보존: 최소 2개의 서로 다른 alternative value, source claim identity, 대안별 locator를 요구하고 대안 부족·locator 누락·중복 값·decision 연결 오류 코드를 추가했다.
- fixture: 기존 17개 공격 명세를 유지·정정하고 H02 hash 4개, identity paired 6개, conflicting 5개 fixture를 추가했다. 모두 구현 명세이며 실제 fixture 파일이나 digest를 생성하지 않았다.
- 회귀: 깨끗한 `375763c`와 병렬 변경이 있는 현재 작업트리 결과를 분리해 위 검증 결과에 기록했다.
- 상태: `READY_FOR_REVIEW`; commit·push하지 않음.


## Control Tower H02 독립 재검증 — 2026-08-20

- 판정: `VERIFIED` — `40-parts-evidence-contract-and-adversarial-fixture-spec-v1` 문서 계약 패키지에 한정한다. 실제 v2 schema·fixture 구현과 Stage 4 완료를 뜻하지 않는다.
- 회귀 재실행: 현재 혼합 작업트리에서 schema 11개, 정상 fixture 2개, 실패 fixture 65개와 simulation test 19개가 모두 통과했다. 이 회귀 결과는 v2 명세의 실행 검증 근거로 승격하지 않았다.
- 형식 검사: `git diff --check` 통과.
- hash 계약: `artifact_sha256`, `evidence_content_sha256`, `approval_target_sha256`, `history[].entry_sha256`의 대상 projection과 제외 필드가 분리돼 자기참조가 제거됐다. 승인·decision history head는 외부 immutable anchor와 대조하도록 명시됐다.
- identity 상태: `record_purpose`와 exact-PN claim wrapper로 exact PN 미보고 discovery가 schema-valid하며, 승인 family relation 유무에 따라 `FAMILY_ONLY`와 `PARTIAL_UNRESOLVED`에 도달한다. 확인된 exact-PN 충돌은 `CONTRADICTED`가 우선한다.
- conflicting claim: 서로 다른 canonical value 두 개 이상과 대안별 source identity·locator를 요구하고, 불완전·중복·decision 사용 공격을 별도 종료 코드로 정의했다.
- 구조 점검: `parts-v2-*` fixture ID 32개가 모두 고유했다. H02 hash 4개, identity paired 6개, conflicting 5개 명세가 포함됐다.
- 데이터 경계: 실제 BOM·부품 후보·시험 PDF·시험 수치·artifact hash·EvidencePacket은 여전히 0건이다. 따라서 evidence ingest와 assurance decision은 `HOLD`, Stage 4는 `IN_PROGRESS`를 유지한다.
- Git: 검증된 문서 패키지는 아직 커밋·푸시하지 않았다. 다른 Workstream의 미통합 변경과 분리해 의미 있는 통합 묶음에서 반영한다.
