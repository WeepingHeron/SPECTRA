# Stage 3 Environment/TID Model Research

## 1. 결론 요약

SPECTRA의 승인 검토용 첫 경로로 **SPENVIS 수동 실행 + 원본 출력 번들 고정 + 로컬 파서**를 권장한다. SPENVIS는 궤도 생성, trapped/solar particle 환경, SHIELDOSE-2 TID 계산과 ASCII 출력이 한 프로젝트 흐름으로 연결돼 SPECTRA의 초기 `MISSION → RADIATION_ENVIRONMENT → TID` 구조에 가장 가깝다.

다만 승인 범위는 좁다.

- 첫 궤도는 `LEO`, 원형, 고도·경사각 고정, 단일 mission segment 하나다.
- 첫 효과 모델은 Si target과 단순 Al spherical shielding의 SHIELDOSE-2다.
- 1, 2, 3, 4 `mm_Al_equivalent`만 SPECTRA가 허용하는 비교 지점으로 고정한다. 이는 SPENVIS 자체 한계가 아니라 SPECTRA Stage 3의 제품 범위 제한이다.
- 실제 허용 고도·경사각·시작일·기간은 Control Tower가 선정한 대표 시나리오 whitelist로 닫는다. 조사만으로 임의의 숫자 범위를 만들지 않는다.
- 모델 체인은 실행마다 정확히 기록한다. 제안 baseline은 `SPENVIS platform + orbit generator + AE9/AP9 v1.50 Mean + 명시적 solar-particle fluence model/configuration + SHIELDOSE-2`다.
- solar-particle source가 빠진 출력은 `total mission TID`로 부르지 않고 `trapped-particle dose component`로만 보관하며 보증 판정은 `HOLD`다.

현재 SPENVIS 약관은 상업 목적 사용에 Institute 또는 ESA의 허가를 요구한다. 공개 문서에서는 SPENVIS 사이트의 무인 자동 호출 권한과 모델 출력 재배포 권한을 확인하지 못했다. 따라서 **비상업 조사 목적의 사람이 실행하는 경로만 다음 단계 후보**이며, 제품 자동화·상업 이용·외부 재배포는 서면 확인 전 `HOLD`다.

## 2. 후보 도구 비교

| 후보 | 지원 범위와 TID 관련 출력 | 주요 입력 | 실행·출력 방식 | 이용·자동화·보관 제약 확인 | 초기 적합성 |
|---|---|---|---|---|---|
| SPENVIS + AE9/AP9 + solar fluence + SHIELDOSE-2 | Earth trajectory의 trapped proton/electron spectrum, solar-particle mission fluence, Al shielding 뒤 ionising dose. SHIELDOSE-2는 `spenvis_s2p.html` 입력·요약과 `spenvis_s2o.txt` 총 mission dose를 생성한다. | orbit/epoch/duration, trapped model version·run mode, solar model·confidence/config, shield depth, shielding geometry, target material | 등록 계정의 웹 UI. Advanced user는 combined run을 사용할 수 있다. HTML report와 ASCII table을 다운로드할 수 있다. | 사이트 사용은 무료지만 등록 필요. 프로젝트 입력·출력이 서버 프로젝트에 보존되며 사용자가 백업 책임을 진다. 상업 목적은 Institute/ESA 허가 필요. 공개 문서에서 무인 API 사용·출력 재배포 허가는 확인하지 못함. | **권장**. SPECTRA의 단순 LEO TID 흐름과 가장 직접적이다. 단, 수동·비상업 조사 경로로 제한하고 모든 원본을 즉시 백업해야 한다. |
| SPENVIS standard AP-8/AE-8 + SHIELDOSE-2 | 전체 radiation-belt 공간·스펙트럼 범위를 넓게 다루는 기존 표준 모델의 orbit-average spectrum과 dose | orbit, solar MIN/MAX와 모델 선택, shielding/target | 일반 SPENVIS UI 및 ASCII 출력 | SPENVIS와 동일. 공식 도움말도 AP-8/AE-8의 오래된 데이터·시간변화 한계를 설명하고 다른 모델의 coverage 확인용 교차검산을 권고한다. | **교차검산 후보**. 첫 primary로 고정하기보다 AE9/AP9 coverage 또는 결과 해석 검토 시 비교 실행한다. |
| NASA OLTARIS / HZETRN | Earth circular orbit/trajectory, shielding transport, target의 silicon dose, flux/fluence와 LET. ASCII table 전체를 zip으로 받을 수 있다. | start/end 또는 duration, altitude, inclination, environment components/model, slab/sphere/thickness distribution, material, response | 등록·관리자 승인 계정의 브라우저 UI와 compute-cluster job. Grid Engine ID, submission time, tagged TARIS version을 결과에 표시한다. | 무료이나 계정 승인 필요. 공개 사용자 가이드에는 API가 없고 UI 흐름만 문서화돼 있다. 프로젝트·job·결과는 사용자 삭제 가능하지만 기본 보존기간, 상업 이용, 재배포 조건은 확인하지 못함. 3D transport는 별도 계정 권한이 필요하다. | **후속 교차검산/고급 차폐 후보**. HZETRN transport와 재료/geometry 범위는 강점이지만 초기 단순 TID ingestion에는 복잡하고 권리·자동화 상태가 불명확하다. |

### 선택 근거

1. SPENVIS는 orbit generator에서 radiation sources와 SHIELDOSE-2까지 이어지고, 입력 보고서와 기계 파싱 가능한 ASCII 출력을 함께 제공한다.
2. Stage 3은 완전한 3D transport보다 provenance가 고정된 첫 실제 TID 경로가 우선이다. OLTARIS의 장점은 Stage 3 후반의 transport 교차검산에 더 가깝다.
3. SPENVIS의 project 단위 입력·출력 보존 구조는 원본 번들 해시와 실행 manifest 설계에 잘 맞는다.
4. SPENVIS 약관과 API 불확실성 때문에 브라우저 자동화나 비공개 endpoint 호출은 권장 경로에 포함하지 않는다.

## 3. 권장 첫 모델 경로

```text
사람이 승인된 SPENVIS 계정으로 프로젝트 생성
  → Earth orbit generator: 원형 LEO, 단일 segment
  → AE9/AP9 v1.50: Mean, default energy grid
  → solar-particle mission fluence: 모델명·버전·mode·confidence를 명시
  → SHIELDOSE-2: spherical Al, Si target, 1/2/3/4 mm
  → input report + source spectra + dose report + ASCII dose output 다운로드
  → 로컬 read-only raw bundle과 manifest에 SHA-256
  → 승인된 parser version으로 정규화
  → Stage 1 EvidencePacket 호환 envelope 생성
```

`AE9/AP9 Mean`은 불확실성을 포함한 보수 경계가 아니라 평균 run mode다. 따라서 첫 parser·provenance 경로 검증에는 쓸 수 있지만, 그것만으로 부품 적합성 또는 최종 mission assurance를 지원할 수 없다. percentile/perturbed/Monte Carlo 선택과 solar fluence confidence는 Workstream 60과 Control Tower가 정책으로 승인해야 한다.

### 사람이 사용하는 흐름

- 등록 계정에서 project를 만들고 orbit를 먼저 생성한다.
- 동일 project에서 trapped radiation과 solar-particle mission fluence를 실행한다.
- SHIELDOSE-2에서 shield depth, geometry, target을 선택한다.
- 결과 페이지에서 report와 ASCII 원본을 내려받는다.
- 프로젝트 입력을 변경해 이전 downstream output이 삭제될 수 있으므로, 각 run 직후 전체 원본을 외부 저장소에 백업한다.

### 자동화 가능 범위

- **허용 후보:** 다운로드 완료 후 로컬 파일 존재 여부, 파일명 allowlist, SHA-256, manifest, parser, schema validation, 단위 정규화, staleness 검사.
- **권한 미확인:** 로그인 자동화, HTTP form replay, scraping, 비공개 endpoint, 대량·반복 run, SPENVIS REST API. SPENVIS 5 자료에는 REST API가 목표로 언급되지만 현재 운영 사이트의 공개 API 계약·권한으로 간주하지 않는다.
- **OLTARIS:** 공식 사용자 가이드는 browser UI와 cluster job을 설명하고 공개 API를 문서화하지 않는다. 자동 제출은 `HOLD`다.

## 4. 초기 지원 범위와 명시적 제외

### 지원 후보

| 항목 | Stage 3 첫 범위 | 분류/주의 |
|---|---|---|
| 궤도 | Earth `LEO`, 원형, 고도·경사각 고정, 단일 segment | SPECTRA scope restriction. 대표 입력값은 별도 승인 전 미정 |
| epoch/기간 | ISO 8601 UTC start와 명시적 duration/end | 모델의 solar-cycle 처리와 결과 `valid_for`에 필요 |
| 차폐 | spherical aluminum, 1/2/3/4 `mm_Al_equivalent` | 단순 등가 차폐. 실제 구조·방향성·국부 차폐가 아님 |
| target | silicon | 출력 단위는 원본에서 확인한 뒤 `rad(Si)`, `krad(Si)`, `Gy(Si)` 중 하나로 정규화 |
| source | trapped proton/electron + solar proton mission fluence | source별 모델명·버전·mode·confidence를 모두 고정해야 total mission dose로 취급 |
| output | shield depth별 mission-integrated absorbed dose와 particle contribution | 원본 파일 구조를 parser가 확인한 뒤에만 `CALCULATED` |

### 제외 범위

- elliptical/transfer/GEO/HEO, multi-segment, maneuvering 또는 uploaded trajectory
- 3D CAD, sector shielding, layered/custom materials, direction-dependent shielding
- 1~4 mm 밖의 차폐, 보간·외삽, Al과 다른 재료를 임의 Al-equivalent로 변환
- SEE/SEU rate, LET acceptance, NIEL, displacement damage, charging
- solar event worst case를 total fluence와 혼동하는 사용
- AE9/AP9 Mean을 confidence bound 또는 worst case로 표현하는 사용
- 원본에 없는 불확실성, 단위, 모델 version, 실행시각의 추정
- TID 결과만으로 부품 승인, 비행 적합성 또는 destructive SEE 안전성을 선언하는 사용

## 5. Stage 3 입력 계약 초안

실제 schema 수정 전의 변경 요청용 논리 계약이다.

| 필드 | 형식/단위 | 필수 이유 |
|---|---|---|
| `run_id` | 불변 string/UUID | 외부 실행, raw bundle, parser run 연결 |
| `mission_id` | string | 기존 `MISSION` 연결 |
| `orbit.body` | `EARTH` | 다른 행성 입력 차단 |
| `orbit.class` | `CIRCULAR_LEO` | 첫 범위 명시 |
| `orbit.altitude` | number `km` | 모델 입력 원문값 보존 |
| `orbit.inclination` | number `deg` | 모델 입력 원문값 보존 |
| `orbit.segment_count` | integer, 반드시 `1` | AE9/AP9 first-path 경계 |
| `mission.start_at`, `end_at` | ISO 8601 UTC | epoch와 validity 고정 |
| `mission.duration` | number + 원본 unit | end와 상호검산; year 환산 정의 필요 |
| `trapped_model` | name, exact version, run mode, percentile/runs/aggregate, energy grid ID | AE9/AP9 mode와 uncertainty가 결과 의미를 바꿈 |
| `solar_model` | name, exact version, model mode, confidence, prediction period, energy grid | mission dose의 solar contribution 재현 |
| `dose_model` | `SHIELDOSE-2` + 원본 report의 exact version/build | 계산 engine 식별 |
| `shielding` | material, geometry, thickness array + units | spherical Al 1/2/3/4 mm 강제 |
| `target_material` | `SILICON` | `rad(Si)` 의미 고정 |
| `tool_access_mode` | `HUMAN_WEB_UI` | 승인되지 않은 자동화 차단 |
| `operator`, `reviewer` | 내부 식별자 | human-in-the-loop 감사 |
| `terms_snapshot` | URL, retrieved_at, hash 또는 승인 record ID | 실행 시점 권리 상태 고정 |

입력 JSON은 UTF-8, 키 정렬, 명시적 number 표현 규칙을 가진 canonical serialization 후 SHA-256을 계산해야 한다. UI screenshot만 입력 기록으로 인정하지 않고, SPENVIS report에 재표시된 입력과 로컬 manifest를 상호검사한다.

## 6. Stage 3 출력·provenance 계약 초안

### 원본 번들 manifest

| 필드 | 필수 내용 |
|---|---|
| `run_id` | 입력과 동일한 ID |
| `provider` | `ESA/BIRA-IASB SPENVIS` |
| `platform_version` | 실제 결과/사이트에서 확인한 SPENVIS version |
| `model_chain[]` | orbit generator, trapped, solar, dose 모델 각각의 name/version/config hash |
| `submitted_at`, `completed_at`, `downloaded_at` | UTC. 제공되지 않은 시각은 추정하지 않고 null + gap |
| `project_ref`, `provider_job_ref` | 비밀정보가 아닌 내부/외부 식별자 |
| `raw_files[]` | original filename, media type, byte size, SHA-256, 역할, source URL/location |
| `bundle_hash` | 정렬된 manifest와 raw file hash 목록의 SHA-256 |
| `terms_state` | research/commercial/automation/redistribution 각각 `CONFIRMED`, `UNCONFIRMED`, `DENIED`, `NOT_APPLICABLE` |
| `parser` | parser name/version/code commit, executed_at, input bundle hash, output hash |

최소 raw allowlist 후보는 orbit report, trapped-model report와 `spenvis_tri.txt`, solar report와 `spenvis_sef.txt`, `spenvis_s2p.html`, `spenvis_s2o.txt`다. 실제 첫 실행에서 생성 파일과 report 내 model/version 표시를 확인한 뒤 allowlist를 확정한다. 파일명이 있다는 이유만으로 완전성을 인정하지 않는다.

### 정규화 출력

| 필드 | 형식/단위 | 규칙 |
|---|---|---|
| `environment_id`, `mission_id`, `run_id` | string | EvidencePacket과 manifest 연결 |
| `quantity_name` | `MISSION_ABSORBED_DOSE_SI` 또는 `TRAPPED_DOSE_COMPONENT_SI` | source completeness에 따라 이름 분리 |
| `shield_depth` | number, `mm_Al_equivalent` | 원본 point와 일대일 연결; 보간 없음 |
| `dose_total` | number, 원본 단위 + 정규 단위 | `rad(Si)` 변환은 고정 상수와 conversion version 기록 |
| `dose_by_source[]` | electron/proton/solar 등 원본이 제공하는 항목 | 합계와 tolerance 내 일치 검사 |
| `valid_for` | start/end UTC | mission 입력과 일치해야 함 |
| `uncertainty_representation` | model mode/confidence/percentile 또는 `NOT_PROVIDED` | 임의 오차막대 금지 |
| `data_class` | `CALCULATED` | raw model output과 재현 가능한 parser provenance가 모두 있을 때만 |
| `content_hash`, `input_hash`, `output_hash`, `bundle_hash` | `sha256:<64 hex>` | 서로 다른 경계의 hash를 구분 |

모델 출력 자체는 `PUBLISHED`가 아니라 외부 계산 결과다. SPECTRA에서는 `CALCULATED`로 분류하고 provider raw output, model chain과 parser run을 함께 보존한다. 원본 파일이나 실행 chain이 빠지면 `CALCULATED`로 승격하지 않는다.

## 7. 종료 상태 규칙

| 상태 | 조건 | assurance 처리 |
|---|---|---|
| `OUT_OF_MODEL_SCOPE` | whitelist 밖 mission, 비원형/다중 segment, 비Earth, 1~4 mm 밖 차폐, 비Al/복합/3D geometry, 미지원 target, 승인되지 않은 model/version/mode, 필요한 source를 모델이 지원하지 않음 | `HOLD` 또는 `INSUFFICIENT_EVIDENCE`; 지원 판정 금지 |
| `STALE_EVIDENCE` | 현재 승인 allowlist와 raw report의 platform/model version 불일치, 약관 snapshot/권리 승인 만료, parser가 지원하는 output signature와 불일치, 승인된 reference run 이후 model chain 변경 | `HOLD`; 재실행 또는 재검토 필요 |
| `PROVENANCE_FAILURE` | input/output/bundle hash 누락·불일치, model version/run time/source config 누락, report와 manifest 입력 불일치, raw file 누락, parser가 모르는 컬럼·단위 | `HOLD`; 숫자 노출을 결정 입력으로 사용 금지 |
| `MODEL_FAILURE` | provider job 실패, error sentinel, 비유한/음수 dose, source 합계 불일치, incomplete download | `HOLD`; 재시도 전 원인 기록 |
| `HOLD` | 상업·자동화·재배포 권한 미확인, solar model/confidence 미승인, 사람이 검토하지 않음, only trapped component, uncertainty policy 미승인, Stage 2 adapter 미통합 | 처리 status와 별도의 assurance decision으로 유지 |

`STALE_EVIDENCE`의 고정 시간 임계값은 현재 근거가 없어 만들지 않는다. 시간 경과보다 model/version/terms/parser/reference-baseline 변화 이벤트를 우선 사용하며, 캘린더 기반 만료는 Control Tower 정책 결정이 필요하다.

## 8. 기존 계약과 Stage 간 영향

### Workstream 10 변경 요청 — 직접 수정하지 않음

1. `radiation-environment.schema.json`은 `particle_flux` 단일 scalar를 필수로 요구한다. TID-only 모델 출력은 energy spectrum 또는 dose-by-source를 제공하며 의미 있는 단일 flux로 축약할 수 없다. TID-only variant에서 `particle_flux`를 optional로 하거나 spectrum artifact 참조를 별도 타입으로 분리해야 한다.
2. `model_name`/`model_version` 한 쌍으로는 orbit, trapped, solar, transport/dose의 모델 chain을 표현할 수 없다. `model_chain[]` 또는 run manifest reference가 필요하다.
3. `calculation_run`은 하나의 engine/version만 허용하고 raw artifact 목록, bundle hash, parser version, rights state를 담지 못한다. 별도 `external_model_run`/`artifact_manifest` 계약이 필요하다.
4. `MISSION`에는 원형 여부, body, segment count와 end time이 없다. 첫 path scope 검증 필드가 필요하다.
5. `SHIELDING.material=ALUMINUM_EQUIVALENT`만으로 geometry와 target을 표현할 수 없다. `geometry`, `target_material`, thickness-point identity가 필요하다.
6. processing status와 assurance decision의 기존 분리는 그대로 유지한다. `HOLD`를 processing status에 추가하지 않는다.

### Stage 2

- 합성 lookup을 직접 덮어쓰지 말고 external model adapter가 동일 result envelope를 생성해야 한다.
- Stage 2가 `particle_flux`를 요구하는 동안에는 실제 TID-only 결과를 dummy flux로 채우지 않는다. adapter 연결은 계약 변경 승인 전 `HOLD`다.
- 합성 `engineering_gate=PASS`와 실제 model provenance gate를 분리한다.

### Stage 4

- 부품 TID 시험 범위와 비교할 값은 target material이 Si이고 source completeness가 확인된 mission dose여야 한다.
- trapped-only component, missing solar source, mean-only uncertainty 미승인 결과는 부품 지원 판정에 사용하지 않는다.

### Stage 5

- 사용자 TID design factor는 환경 model uncertainty를 대신하지 않는다.
- 1~4 mm 지점만 선택 가능하며 중간 두께를 선형 보간하지 않는다.
- 실제 3D 구조를 `mm_Al_equivalent` 하나로 표현한 가정은 승인된 applicability 조건으로 노출한다.

### Stage 6

- raw bundle hash, parser golden file, unknown-column/unknown-unit fail-closed, model/version drift, missing-source 공격 테스트가 필요하다.
- AE9/AP9 mode와 solar confidence 선택을 독립 검토하고, AP-8/AE-8 또는 OLTARIS는 동일 값 기대가 아니라 order-of-magnitude/구성 차이 조사용 교차검산으로 설계한다.
- reference run은 실제 model output을 확보한 뒤에만 만든다. 이 문서에는 실제 수치가 없다.

## 9. 이용·권리·데이터 보관 상태

| 항목 | SPENVIS | OLTARIS | 현재 결정 |
|---|---|---|---|
| 계정/비용 | 무료, 등록 필요 | 무료, 등록 후 관리자 승인 | 사람 조사 계정만 후보 |
| 비상업 조사 | 약관 준수·acknowledgement 전제의 사용 가능성 확인 | 일반 사용 가능성 확인 | 계정 승인 후 수동 조사 가능 |
| 상업 이용 | Institute 또는 ESA permission 필요 | 공개 자료에서 확인 못함 | 양쪽 모두 서면 확인 전 `HOLD` |
| 자동화 | 운영 사이트 공개 API/권한 미확인 | 공개 API 미문서화 | HTTP/browser automation `HOLD`; 로컬 후처리만 허용 후보 |
| 서버 보관 | project input/output 보존, 삭제 가능, 사용자가 백업 책임 | DB에 project, job, result 저장 및 사용자 삭제 가능 | 민감 입력 업로드 금지; run 직후 승인 저장소 백업 |
| 출력 재배포 | site material 복제 제한과 third-party model IP 존재; output 재배포 권리 명시 확인 못함 | 공개 자료에서 확인 못함 | raw output 외부 재배포 `HOLD`; 내부 접근통제 저장만 후보 |
| acknowledgement | 결과 사용 출판·발표에 SPENVIS acknowledgement 필요 | 공개 가이드에서 별도 문구 확인 못함 | SPENVIS attribution 필수 metadata |

## 10. 확인하지 못한 항목과 다음 조치

1. SPENVIS team에 다음을 서면 문의한다: SPECTRA의 상업적 제품 평가·사용 허가 절차, 무인/API/batch 호출 허용 여부와 rate limit, raw/derived output 내부 보관·고객 전달·발표 재배포 권리, model별 third-party 조건, 계정·project 보존기간.
2. OLTARIS administrator에 상업 이용, 자동 제출/API, 결과 보관기간, raw/derived output 재배포 조건을 문의한다.
3. Control Tower/Workstream 60이 AE9/AP9 run mode와 solar model·confidence를 승인한다. 임의 confidence는 사용하지 않는다.
4. Workstream 10이 TID-only environment variant, model chain, raw artifact manifest 변경 요청을 검토한다.
5. Stage 2 통합 기준선과 adapter 연결 위치를 다시 대조했다. 현재 `particle_flux` 필수값과 외부 model-chain provenance 계약이 맞지 않으므로 Workstream 10 계약 변경 전 연결은 `HOLD`다.
6. 승인된 사람 계정과 권리 확인 후 대표 원형 LEO 하나를 실행하고, 생성 파일 목록·report version·단위·column signature를 검증한다.
7. 첫 raw bundle은 원문 위치만 기록하고 저장소에는 복사하지 않는다. 보관 권리와 승인된 object storage 경로가 확정된 뒤 checksum manifest만 Git에 둘지 결정한다.

현재 실제 모델 실행·출력·수치·과학적 교차검산은 **0건**이다. 따라서 Stage 3 구현 완료나 실제 TID 보증을 주장하지 않는다.

## 11. 공식 출처 기록

모든 출처 접근일은 `2026-08-19`다. 발행·갱신일을 페이지에서 확인하지 못한 경우 `미표시`로 기록했다.

| ID | 공식 출처 | 발행/갱신 | 이 문서에서 지지하는 주장 | 제약/메모 |
|---|---|---|---|---|
| S1 | [SPENVIS home](https://www.spenvis.oma.be/) | platform 4.6.14 release: 2026-03-05 | ESA WWW interface, 무료·등록 필요, current platform version | run 당시 version은 결과 원문에서 다시 확인 |
| S2 | [SPENVIS Terms and Conditions](https://www.spenvis.oma.be/conditions.php) | 미표시 | ESA software IP, personal-use copy 제한, commercial purpose permission, acknowledgement, user backup responsibility, liability boundary | 약관은 변경될 수 있으므로 run마다 snapshot 필요 |
| S3 | [Using the SPENVIS system](https://www.spenvis.oma.be/help/system/spenvis.html) | 2018-03-12 | project에 input/output 보존, orbit/grid 재실행 시 downstream output 삭제, HTML/ASCII output | 오래된 help page; current UI로 재확인 필요 |
| S4 | [SPENVIS Earth orbit generator](https://www.spenvis.oma.be/help/models/sapre_earth.html) | 검색 결과 기준 2018 계열, 페이지 명시일 재확인 필요 | low/GEO/high eccentric orbit, mission/segment/epoch/duration, advanced trajectory upload | first path는 circular single segment로 더 좁힘 |
| S5 | [SPENVIS AE9/AP9 help](https://www.spenvis.oma.be/help/models/ae9ap9.html) | page LastChangedDate 2016-07-05 | v1.00/1.30/1.50, Mean/Percentile/Perturbed/Monte Carlo, one-segment limit, report와 `spenvis_tri.txt` | advanced-user 기능; current run report 우선 |
| S6 | [SPENVIS trapped radiation help](https://www.spenvis.oma.be/help/models/trep.html) | 2026-02-23 | standard vs AE9/AP9, advanced access, output files, downstream deletion | AE9/AP9에는 orbit-averaged spectrum만 생성 |
| S7 | [SPENVIS solar particle models](https://www.spenvis.oma.be/help/models/sep.html) | 검색 결과 기준 2018 계열, 명시일 재확인 필요 | SAPPHIRE/ESP/JPL-91 등, mission duration와 confidence, magnetic shielding correction | solar model/confidence 선택은 아직 미승인 |
| S8 | [SPENVIS dose models](https://www.spenvis.oma.be/help/models/dose.html) | 미표시 | shield depth 0.05–20 mm, geometry/target input, SHIELDOSE-2 report와 ASCII total mission dose | SPECTRA는 1–4 mm만 허용 |
| S9 | [SPENVIS output files](https://www.spenvis.oma.be/help/models/outputs.html) | 미표시 | output download, report/ASCII names, structured header variable/unit metadata | 실제 first run의 signature를 golden file로 확정 필요 |
| S10 | [SPENVIS combined run](https://www.spenvis.oma.be/help/models/radcomb.html) | 검색 결과 기준 2018 계열 | advanced user가 model suite를 한 명령으로 연속 실행 | 공개 API 또는 무인 자동화 허가를 뜻하지 않음 |
| S11 | [SPENVIS trapped-model background](https://www.spenvis.oma.be/help/background/traprad/traprad.html) | 검색 결과 기준 2018 계열 | AP-8/AE-8 coverage·age·time limitations, coverage 밖 negative flux와 cross-check 권고 | model suitability는 mission별 검토 필요 |
| O1 | [OLTARIS home](https://oltaris.nasa.gov/) | 미표시 | HZETRN tool, free/approved registration, Earth circular orbit inputs and AP8/AP9 capability | evolving tool set; current capabilities can change |
| O2 | [OLTARIS User Guide](https://oltaris.nasa.gov/static_pages/OLTARIS_USER_GUIDE/sendfile) | revision date 미표시 | browser UI, account activation, circular orbit input, silicon dose, geometry/transport, ASCII downloads, job ID/version/time, deletion behavior | figures 일부가 current UI와 다를 수 있다고 문서가 경고 |
| O3 | [NASA/TP-2010-216722](https://oltaris.nasa.gov/help_documentation/OLTARIS_TP_216722.pdf) | 2010 | OLTARIS/HZETRN architecture and verification background | 최신 model/config는 current change log로 확인 필요 |

## 12. 재현 가능한 조사 방법

1. 위 공식 URL만 열고 페이지의 tool scope, input, output, access, rights 문구를 확인한다.
2. 날짜가 표시된 help page는 날짜를 기록하고, 표시되지 않으면 추정하지 않는다.
3. SPENVIS terms에서 commercial permission, backup, acknowledgement, IP 문구를 다시 확인한다.
4. 각 tool guide에서 `API`, `automation`, `commercial`, `redistribution`, `retention`을 검색한다. 없다는 사실은 허가가 아니라 `UNCONFIRMED`로 기록한다.
5. 공개 문서와 로그인 후 UI가 다르면 로그인 후 확인 결과를 새 source record로 추가하되 기존 기록을 덮어쓰지 않는다.
6. 실제 output이 확보되기 전에는 숫자 예시, sample hash 또는 가짜 run ID를 만들지 않는다.
