# Stage 4 Parts Evidence Source, Rights, Identity, and Applicability Research

## 기술 요약

Stage 4의 첫 구현 경로는 **BOM에서 출발해 공식 색인으로 후보를 찾고, 권리가 확인된 원문에서 정확한 부품 식별·시험 조건·사건 유형·원문 위치를 추출한 뒤, 사람 승인과 결정론적 적용성 gate를 통과시키는 흐름**이어야 한다. 공식 데이터베이스의 검색 결과나 보고서 존재만으로는 부품 지원 또는 비행 적합성을 뜻하지 않는다.

2026-08-19 현재 NASA GSFC/NEPP, ESA ESARAD/ESCIES, 제조사 공개 문서는 모두 유용하지만 역할이 다르다. NASA GSFC는 부품별 시험 보고서 탐색에 가장 직접적이고, NEPP/NTRS는 시험·보증 방법과 공식 문서 식별에 강하다. ESARAD는 ESA 및 계약 파트너 시험 보고서의 공개 색인을 제공하지만 보고서 다운로드에는 로그인 조건이 있고, ESA 자체가 상용부품 traceability와 최신본을 보장하지 않는다. 제조사 자료는 정확한 주문형 부품번호, 제품 revision, QML/RHA 상태와 최신 제품별 보고서에 강하지만 자동 수집·재배포 권한은 제조사와 문서마다 다르다.

현재 프로젝트에는 실제 BOM이 없다. 따라서 실제 부품 5~10종 선정과 모든 실제 수치 추출은 `HOLD`다. 이 문서는 데이터 수집·정규화·적용성 검토의 계약 초안만 확정하며, 특정 부품의 지원 판정이나 비행 적합성 결론을 포함하지 않는다.

## 1. 조사 범위와 판단 기준

- 조사일: `2026-08-19` (`Asia/Seoul`)
- 기준 계약: `docs/contracts/STAGE1_CONTRACT.md`, `schemas/*.schema.json`
- 사용한 실제 시험 수치: 없음
- 다운로드·저장한 시험 PDF: 없음
- 고객 자료: 접근·수집·저장하지 않음
- 권리 판단 수준: 운영 설계를 위한 1차 분류이며 법률 자문이 아니다. 개별 문서의 저작권 표기와 계정 약관은 수집 시 다시 확인한다.
- 보고서의 카탈로그 행과 검색 스니펫은 필드 존재 확인에만 사용하며 증거값으로 사용하지 않는다.

출처의 초기 적합성은 다음 네 역할로 구분한다.

- `DISCOVERY`: 후보 문서를 찾을 수 있음
- `METHOD_REFERENCE`: 시험·보증 방법을 정의하거나 해석을 도움
- `CANDIDATE_EVIDENCE`: 원문 검증 전의 부품 증거 후보
- `DECISION_ELIGIBLE`: 권리·식별·조건·원문 위치·사람 승인을 모두 통과한 경우에만 부여되는 후속 상태

이번 조사에서 `DECISION_ELIGIBLE`로 승인한 자료는 없다.

## 2. 증거 출처 비교표

| 출처 | 자료 유형과 공식 범위 | 접근·권리 제약 | 기대 필드 | 초기 적합성 |
|---|---|---|---|---|
| [NASA GSFC Radiation Data Base](https://nepp.nasa.gov/radhome/raddatabase/raddatabase.html) | GSFC 방사선 시험 데이터만 포함. 색인 필드는 Part Number, Function, Manufacturer, Date(s), File(s), Test Type, Category이며 행에서 시험 보고서로 이동한다. 현재 NEPP가 임시 호스팅한다. | 공개 색인. 전용 공개 API·대량 수집 허가는 확인하지 못했다. NASA STI의 일반 규칙상 문서는 저작권 표기가 없으면 복제·배포 가능할 수 있으나, 계약자·공동저자·제3자 자료는 별도 저작권일 수 있어 **문서별 확인 전 재배포 금지**. NASA 출처 표시와 비보증 표현 필요. | 정확/일반 부품번호, 제조사, 시험일, 보고서 파일명, TID/SEE/DD 분류; 원문에서 lot/date code, package, technology, 시설, 조건, 측정 결과 기대 | `DISCOVERY`, 원문 확인 후 `CANDIDATE_EVIDENCE` |
| [NASA NEPP](https://nepp.nasa.gov/) 및 [NASA STI/NTRS](https://sti.nasa.gov/) | EEE 부품 성능·고장 모드·시험 방법·신뢰성·공급망 지식, NEPP 기술 보고서와 워크숍, NTRS 공식 메타데이터·전문 문서. | NEPP Radhome은 현재 임시 호스팅. NTRS는 공개 메타데이터에 OpenAPI·연도별 bulk download를 권장하고 출처 표기를 요구한다. NASA STI는 정부 저작물과 민간 저작물을 구분하므로 문서 메타데이터·저작권 표기를 확인해야 한다. NASA 또는 상품 보증을 암시하면 안 된다. | NASA 문서 ID, 보고서 revision/date, 저자·기관, 배포 제한, 시험 방법, lot/date code, sample 수, 시험 시설·조건·결과 위치 | `METHOD_REFERENCE`, 일부 문서는 `CANDIDATE_EVIDENCE` |
| [ESA Radiation Test Database (ESARAD)](https://esarad.esa.int/) | ESA 또는 ESA 계약 아래 유럽 파트너가 수행한 SEE·TID·DD 시험 보고서. 공개 색인에 DUT part type, manufacturer, test type/method, function, technology, source, report date가 있다. | 색인은 공개지만 보고서 다운로드는 ESA Member State 회사·기관의 등록/로그인을 요구한다고 안내한다. 요약 일부는 보고서 번호와 ESARAD disclaimer를 명확히 인용할 때 복제를 허용한다. ESA는 정확성·완전성·적합성·승인을 보증하지 않고, 상용품 traceability와 최신본도 보장하지 않는다. 일반 ESA 출판물은 개인·비상업 복사 외 재배포·파생물에 사전 서면 허가가 필요하다. 기여 안내의 `FOR PUBLIC USE`/`ESA INTERNAL ONLY` 공개 범위 문구가 상식과 반대로 적혀 있어 권리 운영에 사용하지 않고 ESA 확인 전 `RIGHTS_UNRESOLVED`로 둔다. | ESARAD ID, report number/date/source, part type, manufacturer, technology, 시험 표준/방법, TID/SEE/DD; 원문에서 lot/date code, sample, 조건, 곡선·결과 위치 기대 | `DISCOVERY`; 로그인·권리·원문 확인 후 `CANDIDATE_EVIDENCE` |
| [ESCIES ESCC Radiation Standards](https://escies.org/webdocument/showArticle?id=229) | ESCC 22900 TID steady-state 시험 방법, ESCC 25100 SEE 시험 방법·지침 등 방법론 기준. 부품 시험 결과 자체는 아님. | ESCC 문서 자체의 legal disclaimer가 우선한다. 공개 ESCC 25100은 비상업 목적에서 사전 허가 없이 전체 무변경 복사 또는 식별자를 제거한 부분 복사를 허용하는 조건을 명시한다. 문서·issue별 조건을 다시 확인한다. | 시험 표준 번호·issue, 필수 시험 조건과 보고 항목, 방법 적합성 | `METHOD_REFERENCE` 전용 |
| 제조사 공개 제품 페이지·데이터시트·radiation report·SMD/VID·PCN | 정확한 주문형 part number, grade/package, 제품 revision, 제조사가 수행·의뢰한 TID/SEE 보고서, 보증 등급과 lot acceptance 정책. 예: TI 제품별 Radiation & Reliability Report, Microchip RH/RT 설명, AMD space radiation characterization, Infineon 제품별 공개/로그인 보고서. | 저작권과 사이트 약관 적용. 공개 열람은 재배포 허가가 아니다. 자동 scraping/data mining 금지 조항이 흔하고, 일부 보고서는 계정·NDA·지원 티켓이 필요하다. 문서별 URL·revision·copyright·허용 행위를 기록하고 원문은 저장소에 넣지 않는다. | exact orderable PN, SMD/VID, grade, package, technology/process, product revision, report ID/revision, 시험 lot/date code, sample 수, 조건, TID·SEE 결과, 제조 변경/PCN | `DISCOVERY`, 원문·권리·식별 확인 후 `CANDIDATE_EVIDENCE` |
| 고객 제공 시험자료·BOM·CoC/lot trace | 고객 비공개 exact BOM, procurement/lot/date code, CoC, wafer/assembly trace, 내부 시험·승인 기록 | 권한·목적·보존기간·고객 tenant·KMS·접근자·삭제 절차·재사용 금지·LLM 처리 허용 여부가 승인되기 전에는 수집 금지. 공개 출처와 물리·논리적으로 분리. | customer component ID, exact orderable PN, lot/date code, serial/wafer/assembly trace, 승인자, 배포 등급, 보존·삭제 정책 | 승인 전 `HOLD`; 승인 후에만 `CUSTOMER_VERIFIED` 후보 |

### 제조사별 권리 운영 예시

| 제조사 | 확인한 공식 문서/약관 | 운영 결론 |
|---|---|---|
| Texas Instruments | [TI Online Terms of Use](https://www.ti.com/legal/terms-conditions/terms-of-use.html), [TI Copyrights](https://www.ti.com/legal/terms-conditions/copyright.html), [제품별 radiation report가 연결된 예시 페이지](https://www.ti.com/product/ADS1282-SP) | 두 약관 페이지의 비상업 복제·배포 범위 표현이 동일하지 않고 자동 data mining도 금지한다. 충돌을 넓게 해석하지 않는다. 자동 수집·프로젝트 내 PDF 재배포는 `RIGHTS_UNRESOLVED`; 링크·문서 ID·짧은 사실 요약만 보존하고 필요 시 서면 허가를 받는다. |
| Microchip | [Website Terms of Use](https://www.microchip.com/en-us/about/legal-information/website-terms-and-conditions), [Radiation-Testing Standards and Ratings](https://www.microchip.com/en-us/products/power-management/discretes/aerospace-defense) | 콘텐츠는 저작권 보호되며 단일 컴퓨터의 개인적·Microchip 제품 관련 사용 외 배포·복제와 data mining이 제한된다. RH와 RT의 보증 범위도 다르므로 marketing label을 시험 증거로 대체하지 않는다. |
| AMD | [Terms of Use / Copyright](https://www.amd.com/en/legal/copyright.html), [AMD Space radiation overview](https://www.amd.com/en/solutions/aerospace-and-defense/space.html) | 개인·정보 목적 열람 범위가 중심이며 업무·공개 목적 복제·배포는 사전 허가가 필요하다. XRTC나 secure portal 자료는 해당 하위 약관/NDA를 별도 적용한다. |
| Infineon | [Terms of Use](https://www.infineon.com/legal/usage-terms), [공개·로그인 문서가 함께 표시되는 제품 페이지 예시](https://www.infineon.com/cms/en/product/high-reliability/space/power/rad-hard-mosfets/n-channel-rad-hard-power-mosfets/irhna67164scs/) | 정보·비상업 목적의 무변경 사용과 출처·저작권 표시 조건을 확인했다. 단, `MyInfineon` 등 제한 문서는 공개 자료로 취급하지 않고 계정 범위와 재사용 권한을 따로 확인한다. |

## 3. 권리 상태와 원문 취급 계약

공개 URL 하나로는 권리 상태를 표현할 수 없다. 다음 필드가 필요하다.

| 필드 | 의미 |
|---|---|
| `source_family` | `NASA_GSFC`, `NASA_NEPP_NTRS`, `ESA_ESARAD`, `ESA_ESCIES`, `MANUFACTURER`, `CUSTOMER` |
| `landing_uri`, `document_uri` | 색인과 원문 URL을 분리 |
| `document_id`, `title`, `issuer`, `revision`, `publication_date` | 문서의 안정 식별자와 버전 |
| `retrieved_at`, `access_method`, `authentication_scope` | 접근일, 공개/로그인/API/고객 전달 방식 |
| `terms_uri`, `rights_checked_at`, `rights_evidence_location` | 적용 약관과 확인 위치 |
| `access_status` | `PUBLIC`, `REGISTRATION_REQUIRED`, `RESTRICTED`, `UNAVAILABLE` |
| `rights_status` | `PERMITTED_WITH_CONDITIONS`, `PERMISSION_REQUIRED`, `CONFLICTING_TERMS`, `UNKNOWN`, `CUSTOMER_RESTRICTED` |
| `allowed_actions` | `LINK`, `CACHE`, `EXTRACT_FACTS`, `QUOTE`, `REDISTRIBUTE`를 각각 boolean으로 기록 |
| `attribution_text`, `disclaimer_text`, `third_party_content_present` | 필수 출처·면책 표시와 제3자 권리 |
| `artifact_sha256`, `media_type`, `byte_length` | 승인된 원본 바이트의 무결성. 추출 record hash와 분리 |
| `storage_class`, `retention_policy`, `tenant_id` | 원문 저장 위치, 보존·삭제, 고객 격리 |

운영 규칙은 다음과 같다.

1. `LINK`만 허용되면 URL·문서 ID·접근일·권리 기록만 프로젝트 데이터에 둔다.
2. `CACHE`가 승인된 원문은 Git이 아닌 접근 통제된 object storage에 저장하고 immutable generation과 SHA-256을 기록한다.
3. `EXTRACT_FACTS`가 승인돼도 원문 문장 전체나 표 전체를 복제하지 않고, 사실값과 짧은 locator만 저장한다.
4. `REDISTRIBUTE=false`이면 Evidence Packet·대시보드·내보내기에 PDF를 포함하지 않는다.
5. 권리 문구가 충돌하거나 문서 저작권자가 불명확하면 `RIGHTS_UNRESOLVED` 차단 gap을 만든다.
6. NASA·ESA·제조사가 SPECTRA의 결과를 승인·보증한 것처럼 표현하지 않는다.
7. NASA 공개 정보가 AI 후보 탐색에 사용돼도 결과는 SPECTRA가 책임지는 추출·판정으로 표시하고 NASA의 AI 제품 승인·정확성 보증을 암시하지 않는다.

## 4. 초기 부품 후보 선정 기준과 BOM 부재 정책

### BOM이 있을 때의 후보 선정 순서

1. 고객 BOM에서 `manufacturer + exact orderable part number`가 있는 행만 후보 큐에 넣는다.
2. 파괴성 SEE가 설계상 가능한 power MOSFET/GaN, regulator, latchup 가능 IC와 mission-critical memory/processor/FPGA를 우선한다.
3. TID와 SEE가 모두 필요한 부품, 변경 시 시스템 영향이 큰 부품, 수량이 많은 부품을 우선한다.
4. 공식 원문이 있고 lot/date code·process/die·package·시험 조건을 많이 확인할 수 있는 부품을 우선한다.
5. 공개 근거와 제조사 근거가 독립적으로 겹치는 부품을 우선하되, 서로 다른 lot·die·조건을 합쳐 하나의 증거처럼 만들지 않는다.
6. 초기 5~10종은 memory/processor/FPGA, power device/regulator, analog/interface 등 서로 다른 failure mode를 포함하도록 구성한다.
7. 선택 이유와 제외 이유를 남기고, 증거가 풍부하다는 이유만으로 실제 BOM에 없는 부품을 추가하지 않는다.

### BOM 부재 시 정책

- 현재 상태: `BOM_MISSING` → Workstream 작업 상태는 조사 설계에 한해 `READY_FOR_REVIEW`, 실제 부품 선정·수집·정규화·판정은 `HOLD`.
- 제조사나 데이터베이스에 보이는 부품을 데모 편의로 “초기 실제 부품”으로 선정하지 않는다.
- UI/fixture가 필요하면 존재하지 않는 명확한 `SYNTHETIC` 식별자를 사용하고 실제 보고서 링크·수치와 결합하지 않는다.
- 다음 입력이 확보될 때만 실제 후보 선정 작업을 재개한다: BOM 소유자, 용도 승인, exact orderable part number, manufacturer, package/grade, 수량, 가능한 lot/date code, mission criticality.

## 5. 정확한 부품 식별 최소 필드

### 식별 필드 초안

| 계층 | 최소 필드 | 사용 이유 |
|---|---|---|
| BOM 기준 | `component_id`, manufacturer raw/canonical, exact orderable part number raw/canonical, function, quantity | 시험 증거가 연결될 실제 설계 항목 |
| 주문·품질 | generic part number, manufacturer ordering code, SMD/VID/NSN, grade/qualification, package code/style, temperature grade, lead finish | 같은 base number 안의 등급·패키지·품질 차이 방지 |
| 실리콘·공정 | technology, process ID/node, die ID/revision, mask revision, wafer fab/site, wafer lot | radiation response에 영향을 줄 수 있는 제조 변경 추적 |
| 조립·로트 | assembly site, assembly lot, test lot, lot ID, Date Code, sample serial/marking | 시험 샘플과 비행품 traceability |
| 변경 이력 | datasheet/report revision, PCN/PDN ID, test date, procurement date | 시험 뒤 process/die 변경·stale 증거 탐지 |

`manufacturer`와 `exact orderable part number`는 후보 검색의 최소 입력일 뿐, 단독으로 최종 exact match를 증명하지 않는다. radiation response 적용에 필요한 package/process/die/lot/date code가 누락되면 그 필드는 `UNKNOWN`으로 보존하고 동일하다고 가정하지 않는다.

### 일치·불일치 판정표

| 판정 | 조건 | 증거 사용 | 기본 결과 |
|---|---|---|---|
| `EXACT_MATCH` | manufacturer와 exact orderable PN이 같고, 양쪽에 존재하는 package/grade/process/die/lot/date code에 모순이 없으며 해당 시험의 필수 traceability 필드가 모두 확인됨 | 적용성 검토로 진행 가능 | 아직 지원 아님 |
| `PARTIAL_UNRESOLVED` | manufacturer·exact PN은 같지만 process/die/lot/date code 등 필수 필드가 한쪽 또는 양쪽에서 누락 | 후보 탐색·gap 표시만 | `HOLD` / `INSUFFICIENT_EVIDENCE` |
| `CONTRADICTED` | 하나 이상의 확인된 필드가 다름. 예: suffix/package, die revision, process, lot/date code | 해당 evidence를 그 BOM의 지원 근거로 사용 금지 | `CONFLICTING_EVIDENCE` 또는 `HOLD` |
| `FAMILY_ONLY` | generic/base part, product family, 기능, 유사 기술만 일치 | 대체 후보·추가 조사 힌트만 | `HOLD` |
| `UNKNOWN_MANUFACTURING_CHANGE` | 시험 뒤 PCN/process/die 변경 여부를 확인하지 못함 | stale 후보로만 보존 | `STALE_EVIDENCE` 또는 `HOLD` |
| `NOT_APPLICABLE` | 다른 부품, 다른 기술 또는 시험이 해당 failure mode를 다루지 않음 | 판정 trace 사용 금지 | `HOLD` |

정규화는 대소문자·공백·하이픈·제조사 alias를 검색용 canonical key로 만들 수 있지만, 원문 문자열을 반드시 함께 보존한다. suffix 제거, generic number 변환, 구 제조사→인수 제조사 변환은 자동 동일시가 아니라 별도 alias relation이며 사람 확인이 필요하다.

현재 Stage 1 의미 검증은 BOM 또는 시험 증거 한쪽에만 identity 필드가 있어도 `PART_IDENTITY_MISMATCH`를 낸다. 실제 경로에서는 **누락(`UNRESOLVED`)과 모순(`MISMATCH`)을 분리**해야 한다. 이 변경은 Workstream 10 검토가 필요하다.

## 6. TID·SEU·SEL·SEB·SEGR 정규화 필드 초안

모든 결과는 공통 header와 독립 event record를 가진다. 하나의 `evidence_types[]`와 하나의 `cross_section`으로 여러 SEE를 대표하지 않는다.

### 공통 header

- `evidence_record_id`, `component_id`, `document_id`, `report_revision`
- `tested_identity` 전체 필드와 원문 표기
- `test_standard`, `test_standard_issue`, `facility`, `test_date`
- `sample_count`, `control_count`, sample/lot/date code/serial 목록
- `radiation_source_type`, particle/ion species, energy, LET와 LET basis, range, incidence angle
- `flux`, `fluence`, dosimetry/calibration, facility uncertainty
- `supply_voltages`, bias/operating mode, temperature, current limit, clock/workload/configuration
- package, lid/delid/thinning, orientation, atmosphere/vacuum
- `source_locator`의 page/section/table/figure/row/cell와 `artifact_sha256`
- extractor/version/time, reviewer/time, approval status와 review history

### 사건별 필드

| 유형 | 반드시 분리할 결과 필드 | 금지되는 대체 |
|---|---|---|
| `TID` | radiation source와 target material, dose unit, dose rate, dose steps, cumulative dose, biased/unbiased 상태, temperature, anneal 조건·시간, pre/in/post-irradiation 파라미터, specification limit, sample/control 수, 최대 **시험 도달량**과 최대 **규격 내 확인량**을 분리 | SEE 시험 중 부수적으로 누적된 dose를 전용 TID qualification처럼 사용, 최대 조사량과 guaranteed rating 동일시, dose-rate/anneal 외삽 |
| `SEU` | subtype(SEU/MBU 등), heavy-ion/proton 구분, device configuration/workload, LET 또는 particle energy, effective/surface LET, fluence/flux, observed event count, sensitive bit/device denominator, cross-section basis(`cm2/bit` 또는 `cm2/device`), 각 curve point, fit model/parameters, zero-event statistical bound | SEL/SEB/SEGR 부재의 증명, 단일 headline cross-section으로 curve·조건 대체, device↔bit 임의 변환 |
| `SEL` | trigger/detection current, supply·bias·temperature, current limit와 trip delay, event count, LET/energy/fluence, recovery/power cycle, destructive/non-destructive/latent damage 관찰, post-test electrical | SEU 수치나 ECC 결과로 대체, “no SEL observed”를 fluence·온도·전압·검출 기준 없이 immunity로 표현 |
| `SEB` | power device topology, `VDS/VGS/ID`와 load, rated breakdown 대비 시험점, temperature, ion LET/range/angle, step sequence, failure criterion, event count, safe operating boundary, post-test leakage/function | SEL·SEU 결과로 대체, 시험한 전압·LET 경계 밖 safe operating area 외삽 |
| `SEGR` | gate/drain bias, oxide/gate leakage 전·후, ion LET/range/angle, voltage step size, rupture/microbreak 판정 기준, event count, safe operating boundary, post-test 검사 | SEB·SEU 결과로 대체, 기능 유지만으로 gate integrity 증명 |

`no_event_observed`는 사건 수 0이라는 관측값이지 `immune=true`가 아니다. 검출 기준, 유효 fluence, sample 수, 조건 범위와 사전 정의된 통계 방법이 없으면 `ZERO_EVENT_BOUND_MISSING`으로 `HOLD`한다.

## 7. 시험 조건과 임무 조건의 적용성 비교

적용성은 `APPLICABLE`, `UNRESOLVED`, `NOT_APPLICABLE`의 단일 결론 전에 항목별 결과를 남긴다.

| 비교 영역 | 시험 측 필드 | 임무/BOM 측 필드 | `HOLD` 또는 불적용 조건 |
|---|---|---|---|
| 부품 identity | exact PN, manufacturer, package/grade, process/die, lot/date code | BOM·CoC·procurement trace | 누락, 모순, family-only, 제조 변경 미확인 |
| TID 범위 | 규격 내 확인 dose, material, source, dose rate, bias, anneal, temperature | shielded mission TID, design factor, material basis, duty cycle, temperature | 요구량 초과, material/단위 불변환, dose-rate/ELDRS·bias·anneal 불충분 |
| SEE 환경 | particle species, energy, LET, range, angle, flux/fluence | Stage 3 spectrum/LET/energy와 shielding | 필요한 spectrum 미제공, particle/LET/energy/range 미포괄, angle/geometry 미해결 |
| 전기 조건 | supply, bias, mode, clock, workload, current limit, `VDS/VGS/ID` | 실제 operating envelope와 worst case | 임무 worst case가 시험 범위를 초과, mode/voltage 미시험 |
| 열 조건 | irradiation temperature와 post-test temperature | mission min/max와 thermal state | SEL/파괴성 SEE worst-case 온도 미포괄 |
| 사건 coverage | 측정한 SEU/SEL/SEB/SEGR와 검출 기준 | 부품 기술과 정책이 요구하는 failure modes | 요구 사건 누락, SEU로 파괴성 SEE 대체 |
| 통계·샘플 | sample 수, lot 수, fluence, event 수, zero-event bound | 조직 최소 증거 정책 | sample/lot/통계 기준 미달 또는 미정 |
| 성능 파라미터 | 측정 전기 파라미터와 specification limit | 실제 회로의 critical parameters | 임무 핵심 파라미터 미측정 |
| 시간·변경 | report/test date, revision, PCN/process change | procurement date와 flight lot | 시험 뒤 변경 여부 미확인, 최신본 불명 |
| 방법 | standard와 issue, deviations, calibration | 조직 승인 시험 방법 | 표준/issue/편차 미확인 또는 조직 정책 불충족 |

항목별 비교에서 하나라도 차단형이면 전체 trace는 `APPLICABLE`이 될 수 없다. 문자열 설명만으로 낙관 판정하지 않고, 비교한 양쪽 값·단위·rule ID를 구조화해야 한다.

## 8. `HOLD`와 실패 코드 초안

| 코드 | 의미 | Stage 1 상태 매핑 제안 |
|---|---|---|
| `BOM_MISSING` | 실제 후보를 선택할 BOM 없음 | 작업 `HOLD`; packet 미생성 또는 `INSUFFICIENT_EVIDENCE` |
| `EXACT_PART_NUMBER_MISSING` | generic/family 정보만 존재 | `VALID` + `INSUFFICIENT_EVIDENCE` |
| `IDENTITY_FIELD_UNRESOLVED` | process/die/lot/date code 등 필수 identity 누락 | `VALID` + `HOLD` |
| `IDENTITY_CONFLICT` | 확인된 identity 필드 모순 | `CONFLICTING_EVIDENCE` + `HOLD` |
| `FAMILY_ONLY_EVIDENCE` | 유사 부품·부품군 자료 | `VALID` + `INSUFFICIENT_EVIDENCE` |
| `ORIGINAL_UNAVAILABLE` | 보고서 원문 접근 불가 | `PROVENANCE_FAILURE` + `HOLD` |
| `RIGHTS_UNRESOLVED` | 저장·추출·인용 권리 미확인/충돌 | `PROVENANCE_FAILURE` + `HOLD` |
| `ARTIFACT_HASH_MISSING` | 승인된 원문 바이트 해시 없음 | `PROVENANCE_FAILURE` + `HOLD` |
| `SOURCE_LOCATOR_MISSING` | page/table/figure/row 등 원문 위치 없음 | `PROVENANCE_FAILURE` + `HOLD` |
| `DOCUMENT_REVISION_UNKNOWN` | version/latest status 확인 불가 | `STALE_EVIDENCE` + `HOLD` |
| `MANUFACTURING_CHANGE_UNKNOWN` | 시험 뒤 process/die 변경 여부 불명 | `STALE_EVIDENCE` + `HOLD` |
| `TEST_CONDITION_MISMATCH` | 전압·온도·bias·mode 등 불일치 | `VALID` + `HOLD` (`NOT_APPLICABLE`) |
| `OUT_OF_TEST_SCOPE` | dose/LET/energy/voltage 범위 밖 | `VALID` + `HOLD` (`NOT_APPLICABLE`) |
| `TID_DOSE_RATE_UNRESOLVED` | dose rate/ELDRS 적용성 미해결 | `VALID` + `HOLD` |
| `DESTRUCTIVE_SEE_MODE_MISSING` | 요구 SEL/SEB/SEGR 개별 증거 누락 | `VALID` + `INSUFFICIENT_EVIDENCE` |
| `ZERO_EVENT_BOUND_MISSING` | 0 event의 조건·통계 경계 없음 | `VALID` + `HOLD` |
| `REVIEW_NOT_APPROVED` | 추출·적용성 사람 검토 미승인 | `VALID` + `HOLD` |
| `CUSTOMER_DATA_UNAUTHORIZED` | 고객 권한·격리·목적 승인 없음 | 수집 중단, packet 사용 금지 |

잘못된 JSON이나 허용되지 않은 단위는 `INVALID_INPUT`, 모델이 지원하지 않는 환경 계산은 `OUT_OF_MODEL_SCOPE`다. “증거가 부족함”과 “처리 자체가 실패함”을 같은 코드로 만들지 않는다.

## 9. 원문 위치·해시·검토·승인 이력 계획

### 두 개의 해시

- `artifact_sha256`: 승인된 원문 파일의 exact bytes. URL 내용이 바뀌었는지 검출한다.
- `record_sha256`: canonical JSON으로 정규화한 추출 레코드. 추출 수정 이력을 검출한다.

현재 `recordMetadata.content_hash` 하나로 두 의미를 모두 표현하면 안 된다. 공통 schema에는 원문 artifact hash와 추출 record hash를 분리할 필요가 있다.

### 원문 locator

각 주장·수치·identity 필드마다 다음 locator를 허용한다.

- PDF: page label과 PDF page index, section, table/figure ID, row/column 또는 bounding box
- HTML: stable heading, table row key, element/text anchor, captured retrieval time
- 데이터베이스: source record ID, field name, landing URI, record revision/snapshot time
- 데이터시트/PCN: document ID/revision, page, table/section, effective date

검색 스니펫, 브라우저 줄 번호, 생성형 요약은 원문 locator가 아니다.

### 검토 상태

1. `DISCOVERED`: 공식 색인에서 후보 발견
2. `RIGHTS_CHECKED`: 접근·저장·추출·인용 범위 확인
3. `HASHED`: 승인 원문의 artifact hash와 문서 ID 고정
4. `EXTRACTED`: 자동/수동 추출과 locator 생성
5. `IDENTITY_REVIEWED`: BOM–tested identity 검토
6. `TECHNICAL_REVIEWED`: 사건 유형·조건·단위·곡선 검토
7. `APPLICABILITY_REVIEWED`: 임무 조건과 항목별 비교
8. `APPROVED` 또는 `REJECTED`: 이름·시간·역할·사유·이전 record hash 포함

같은 사람이 자동 추출과 최종 기술 승인을 동시에 수행하지 않는 것을 기본 정책으로 제안한다. 수정은 기존 승인 기록을 덮어쓰지 않고 새 `record_sha256`와 supersedes relation을 만든다.

## 10. 제안 수집·정규화 흐름

```text
승인된 BOM
  → exact identity query 생성
  → 공식 색인에서 후보 URL/문서 ID 수집
  → 권리·접근 gate
  → 원문을 격리 저장소에서 해시 고정(허용된 경우만)
  → claim-level locator와 event별 후보 추출
  → 사람 identity/technical review
  → Stage 3 임무 환경과 항목별 적용성 비교
  → Stage 5 정책에 필요한 사건별 증거 제공
  → Stage 6 독립 공격·재현 검토
  → 승인된 trace만 Stage 7 workflow로 전달
```

검색과 LLM 추출은 후보를 만들 수 있지만 `rights_status`, canonical part match, 단위 변환, range 비교, 사건별 gate, 최종 상태는 결정론적 코드와 사람 승인이 담당한다.

## 11. Stage 3·5·6·7 계약 영향

### Stage 3 Environment Model

- SEE 적용성에 particle species별 spectrum, energy, LET, shielding 뒤 환경과 model/version/hash가 필요하다.
- TID에는 target material과 dose 단위, dose-rate 관련 임무 가정, shielded mission dose가 필요하다.
- Stage 3이 TID만 제공하고 SEE spectrum/LET를 아직 제공하지 않으면 SEU·SEL·SEB·SEGR 적용성은 `UNRESOLVED`로 남긴다.

### Stage 5 Mitigation & Policy

- `require_destructive_see_evidence: boolean`은 부족하다. 부품 기술·회로에 따라 `required_failure_modes: [SEL, SEB, SEGR]`를 개별 지정해야 한다.
- ECC/scrubbing은 SEU 계열에만 연결하고 SEL·SEB·SEGR gate를 통과시키지 못한다.
- SEL current limiting/power cycling은 완화 설계와 복구 증거이지, 미시험 파괴성 SEE를 없애는 증거가 아니다.
- zero-event bound, 최소 fluence/sample/lot, 허용 시험 표준·issue, required operating envelope 정책이 필요하다.

### Stage 6 Assurance & Evals

- suffix 제거 유사 부품 승격, manufacturer alias 오매핑, evidence-only identity 필드를 mismatch로 오분류하는 공격을 시험한다.
- SEU cross-section을 SEL/SEB/SEGR로 복사, no-event를 immunity로 승격, 최대 조사량을 TID rating으로 승격, dose-rate/온도/전압 범위 외삽을 차단한다.
- 변경된 URL content, hash 불일치, locator 누락, 저작권 불명, 미승인 추출, 충돌 보고서를 False PASS 세트에 포함한다.

### Stage 7 Platform & GCP

- 공개 metadata, 저작권 원문, 고객 자료를 bucket/project/tenant와 IAM·KMS로 분리한다.
- object generation, artifact SHA-256, legal hold/retention/deletion, access log를 보존한다.
- rights gate 전에 Document AI/Vertex AI로 원문을 전송하지 않는다.
- 자동 수집은 source별 약관·API·rate limit을 준수하며 scraping 금지 출처는 사람이 제공한 승인 문서만 처리한다.
- 고객 자료는 training/logging/telemetry 포함 여부와 region을 승인 계약에 포함한다.

## 12. 공통 schema 변경 요청 초안

이번 Workstream은 schema를 수정하지 않는다. Workstream 10에 다음 호환성 검토가 필요하다.

| 현재 계약 | 필요한 변화 | 호환 영향 |
|---|---|---|
| `partIdentity`가 manufacturer, part number, process, die, lot, date code만 지원 | raw/canonical manufacturer·orderable PN, generic PN, SMD/VID, package, grade, technology, fab/assembly/wafer trace, marking, PCN relation 추가 | 기존 fixture에는 optional additive로 시작 가능. exact-match 의미 검증 변경 필요 |
| 한쪽에만 identity 필드가 있어도 `PART_IDENTITY_MISMATCH` | `UNRESOLVED`와 `CONTRADICTED` 분리 | 의미 gate·실패 fixture 변경. 기존 fail-closed 성격은 유지하되 error code가 달라짐 |
| `source.license_or_access`가 optional free text | access/rights/allowed-actions/terms/attribution/third-party 필드 구조화 및 `PUBLISHED` 결정 입력에서 필수화 | 공통 metadata version 상승 가능. 기존 fixture migration 필요 |
| `content_hash` 하나 | artifact hash와 normalized record hash 분리 | provenance pointer·fixture·검증기 변경 |
| `PART_TEST_EVIDENCE.evidence_types[]`와 단일 `cross_section` | event별 result 배열, curve point, subtype, no-event bound, destructive safe operating boundary | 구조적 breaking change 가능. schema v2 또는 parallel field 필요 |
| `test_conditions`가 facility/date/bias/temp만 지원 | standard/issue, source/particle/energy/LET/range/angle, flux/fluence, dose rate/steps, anneal, voltage/mode, sample/control, dosimetry 추가 | additive optional 후 event별 required 조건을 `allOf`로 강화 가능 |
| record-level `source.location` 문자열 하나 | claim-level structured locator 배열 | trace `input_pointer`·`origin_pointer` 규칙 확장 필요 |
| approval history 없음 | extractor/reviewer/approver, timestamps, role, status, reason, supersedes hash 추가 | review status와 별도 immutable history 계약 필요 |
| `trace.applicability.conditions[]`가 문자열 | 시험값–임무값–단위–comparison result–rule ID의 structured checks | 기존 문자열은 설명용으로 유지하고 새 checks를 additive로 추가 가능 |
| destructive SEE 정책이 boolean | required failure mode 목록과 부품 기술별 policy | Stage 5·의미 검증기·fixture 변경 필요 |

schema v1은 Stage 2 기준선을 깨지 않도록 유지하고, Stage 4 확장 필드를 optional로 추가한 뒤 의미 gate version을 명시하거나 `PART_TEST_EVIDENCE v2`를 병행하는 방안을 Control Tower와 Workstream 10이 결정해야 한다.

## 13. 확인하지 못한 사항과 다음 행동

| 미확인/보류 | 현재 상태 | 다음 행동 |
|---|---|---|
| 실제 BOM과 초기 5~10종 | `HOLD` | Control Tower가 승인된 BOM owner와 최소 identity 필드를 제공 |
| GSFC/NEPP 개별 보고서의 copyright·third-party status | 문서별 미확인 | 첫 후보 문서마다 NTRS metadata·표지·copyright notice를 확인 |
| ESARAD 보고서 다운로드 자격과 재사용 범위 | `RIGHTS_UNRESOLVED` | ESA 계정 자격과 개별 report terms 확인. 기여 안내의 반전 문구는 ESA에 질의 |
| 제조사 자동 수집/API 허용 범위 | 대체로 미확인 또는 금지 | scraping 금지 출처는 자동화하지 않고 링크 기반 수동 승인 경로 사용 |
| 고객 자료 저장·LLM 처리 권한 | 미승인 | DPA/NDA, tenant, region, retention/deletion, model processing 승인을 계약화 |
| mission SEE spectrum/LET interface | Stage 3 미구현 | Workstream 30과 event별 비교 단위·spectrum contract 합의 |
| mode별 destructive SEE 정책 | Stage 5 미구현 | Workstream 50이 부품 기술별 required modes와 승인 정책 정의 |
| schema v2 범위 | 제안만 존재 | Workstream 10이 additive/migration 방식을 검토하고 Workstream 60이 공격 fixture 설계 |

## 14. 공식 출처 목록

- [NASA GSFC Radiation Data Base](https://nepp.nasa.gov/radhome/raddatabase/raddatabase.html) — 접근일 2026-08-19
- [NASA Electronic Parts and Packaging Program](https://nepp.nasa.gov/) — 접근일 2026-08-19
- [NASA STI: Use of NASA STI](https://sti.nasa.gov/disclaimers/) — 접근일 2026-08-19
- [NASA STI: Harvesting Data from NTRS](https://sti.nasa.gov/harvesting-data-from-ntrs/) — 접근일 2026-08-19
- [NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) — 접근일 2026-08-19. 기술 문서 권리의 직접 근거는 NASA STI terms이며, 이 페이지는 NASA 식별자·AI·비보증 표현의 보조 근거로만 사용
- [NASA NEPP: Radiation Hardness Assurance for Space Systems](https://nepp.nasa.gov/docuploads/A6B8B953-E2DD-4D92-AB8A873A04F0B10A/NSREC02_SC_Poivey.pdf) — archive data의 lot/date code, technology, bias·application 조건 검토 원칙 확인; 접근일 2026-08-19
- [NASA NEPP: Resources for Radiation Test Data](https://nepp.nasa.gov/files/26964/2014-561-OBryan-Final-Pres-NEPPweb-SEEMAPLD-TN36664.pdf) — GSFC/ESCC 검색 필드와 lot/process 주의점 확인; 접근일 2026-08-19
- [ESA Radiation Test Database](https://esarad.esa.int/) — 접근일 2026-08-19
- [ESA Publications Copyright](https://www.esa.int/About_Us/ESA_Publications/Copyright) — 접근일 2026-08-19
- [ESCIES ESCC Radiation Standards](https://escies.org/webdocument/showArticle?id=229) — 접근일 2026-08-19
- [ESCC 22900 Issue 5](https://escies.org/escc-specs/published/22900.pdf) — TID 방법 식별; 접근일 2026-08-19
- [ESCC 25100 Issue 2](https://escies.org/escc-specs/published/25100.pdf) — SEE 방법과 문서별 legal disclaimer 확인; 접근일 2026-08-19
- [TI Online Terms of Use](https://www.ti.com/legal/terms-conditions/terms-of-use.html), [TI Copyrights](https://www.ti.com/legal/terms-conditions/copyright.html) — 접근일 2026-08-19
- [Microchip Website Terms of Use](https://www.microchip.com/en-us/about/legal-information/website-terms-and-conditions) — 접근일 2026-08-19
- [AMD Terms of Use / Copyright](https://www.amd.com/en/legal/copyright.html) — 접근일 2026-08-19
- [Infineon Terms of Use](https://www.infineon.com/legal/usage-terms) — 접근일 2026-08-19
