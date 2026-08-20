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

승인 BOM에서 시작하는 decision candidate에는 `manufacturer`와 `exact orderable part number`가 필요하지만, 공식 색인에서 발견한 discovery record는 exact PN이 미보고일 수 있다. 모든 identity 필드는 claim wrapper로 존재하며 미보고는 `NOT_REPORTED`로 보존하고 동일하다고 가정하지 않는다.

### 일치·불일치 판정표

| 판정 | 조건 | 증거 사용 | 기본 결과 |
|---|---|---|---|
| `EXACT_MATCH` | manufacturer와 exact orderable PN이 같고, 양쪽에 존재하는 package/grade/process/die/lot/date code에 모순이 없으며 해당 시험의 필수 traceability 필드가 모두 확인됨 | 적용성 검토로 진행 가능 | 아직 지원 아님 |
| `PARTIAL_UNRESOLVED` | exact PN이 미보고이고 승인 family relation이 없거나, exact PN 일치 뒤 process/die/lot/date code 등 필수 필드가 누락 | 후보 탐색·gap 표시만 | `HOLD` / `INSUFFICIENT_EVIDENCE` |
| `CONTRADICTED` | 하나 이상의 확인된 필드가 다름. 예: suffix/package, die revision, process, lot/date code | 해당 evidence를 그 BOM의 지원 근거로 사용 금지 | `CONFLICTING_EVIDENCE` 또는 `HOLD` |
| `FAMILY_ONLY` | exact PN은 `NOT_REPORTED`, manufacturer와 generic/base family relation은 원문 locator와 승인 rule로 확인 | schema-valid discovery·추가 조사 힌트만; support decision 금지 | `HOLD` / `INSUFFICIENT_EVIDENCE` |
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

### 원문 hash와 v2 내부 무결성 hash

- `artifact_sha256`: 승인된 원문 파일의 exact bytes. URL 내용이 바뀌었는지 검출한다.
- `evidence_content_sha256`: review와 integrity envelope를 제외한 evidence content projection의 canonical bytes. 추출 content 수정을 검출한다.
- `approval_target_sha256`: content hash와 사전 review assertions만 포함한 별도 projection. 승인 대상을 고정한다.
- `history[].entry_sha256`: 자기 hash를 제외한 append-only review entry와 직전 entry hash의 chain. review history 수정을 검출한다.

현재 `recordMetadata.content_hash` 하나로 이 의미들을 모두 표현하면 안 된다. v2의 정확한 projection, canonicalization, 배열 규칙과 검증 순서는 16.5절을 따른다. 전체 record를 내부 `record_sha256`로 hash하는 방식은 자기참조를 피할 수 없으므로 금지한다.

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
8. `APPROVED` 또는 `REJECTED`: 이름·시간·역할·사유·approval target hash와 history chain 포함

같은 사람이 자동 추출과 최종 기술 승인을 동시에 수행하지 않는 것을 기본 정책으로 제안한다. content 수정은 기존 승인을 덮어쓰지 않고 새 content/approval target hash와 `supersedes_evidence_content_sha256`를 만들며, review assertion 수정은 `supersedes_approval_target_sha256`를 만든다.

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
| `content_hash` 하나 | artifact hash, evidence content hash, approval target hash와 review entry hash chain을 self-reference 없는 projection으로 분리 | provenance pointer·fixture·검증기 변경 |
| `PART_TEST_EVIDENCE.evidence_types[]`와 단일 `cross_section` | event별 result 배열, curve point, subtype, no-event bound, destructive safe operating boundary | 구조적 breaking change 가능. schema v2 또는 parallel field 필요 |
| `test_conditions`가 facility/date/bias/temp만 지원 | standard/issue, source/particle/energy/LET/range/angle, flux/fluence, dose rate/steps, anneal, voltage/mode, sample/control, dosimetry 추가 | additive optional 후 event별 required 조건을 `allOf`로 강화 가능 |
| record-level `source.location` 문자열 하나 | claim-level structured locator 배열 | trace `input_pointer`·`origin_pointer` 규칙 확장 필요 |
| approval history 없음 | extractor/reviewer/approver, timestamps, role, status, reason, content/approval supersedes와 entry hash chain 추가 | review status와 별도 immutable history 계약 필요 |
| `trace.applicability.conditions[]`가 문자열 | 시험값–임무값–단위–comparison result–rule ID의 structured checks | 기존 문자열은 설명용으로 유지하고 새 checks를 additive로 추가 가능 |
| destructive SEE 정책이 boolean | required failure mode 목록과 부품 기술별 policy | Stage 5·의미 검증기·fixture 변경 필요 |

schema v1은 Stage 2 기준선을 깨지 않도록 동결한다. 실제 Stage 4 경로는 17절의 별도 `PART_TEST_EVIDENCE v2`와 versioned semantic gate를 권고하며, additive field 병행은 dual truth 위험 때문에 discovery-only prototype 밖에서는 사용하지 않는다.

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

## 15. 작업 패키지 2 — 구현 계약 명세의 범위

이 절부터는 `40-parts-evidence-contract-and-adversarial-fixture-spec-v1`의 구현 요청이다. 실제 schema나 validator는 Workstream 10 소유이므로 여기서는 수정하지 않는다. 실제 fixture 구현과 독립 공격 실행은 Workstream 60 소유이며, 이 문서는 입력·변이·기대 실패를 정의한다.

### 요구 수준 표기

| 표기 | 의미 | 누락 또는 위반 처리 |
|---|---|---|
| `required` | 해당 객체가 schema-valid이려면 항상 존재해야 함 | `INVALID_INPUT` + `HOLD` |
| `optional` | 없어도 계약 의미가 바뀌지 않는 보조 정보 | 누락만으로 차단하지 않음 |
| `conditional` | event type, field status, 정책 또는 `used_for_decision` 조건이 참일 때 필수 | 조건이 참인데 누락되면 표에 지정한 fail-closed 상태 |
| `forbidden` | 두 개의 진실, 근거 없는 승격 또는 안전하지 않은 값이므로 허용하지 않음 | `INVALID_INPUT`, `PROVENANCE_FAILURE` 또는 전용 오류 + `HOLD` |

후보 수집 레코드와 판정 사용 레코드를 같은 completeness 기준으로 강제하면, 원문에 없는 값을 채우거나 후보 자체를 잃게 된다. 따라서 v2는 각 증거 claim에 다음 상태 wrapper를 사용해야 한다.

```text
claim =
  | { status: VERIFIED, value, locators[1..n] }
  | { status: NOT_REPORTED, reason_code }
  | { status: NOT_APPLICABLE, rule_ref, rationale }
  | { status: CONFLICTING, alternatives[2..n] }

alternative = {
  alternative_id,
  value,
  source_claim_ref: { evidence_id, source_document_id, claim_path },
  locators[1..n]
}
```

- `VERIFIED`에서는 `value`와 최소 1개 locator가 `required`, `alternatives`는 `forbidden`이다.
- `NOT_REPORTED`에서는 `reason_code`만 요구하며 `value`, `locators`, `alternatives`는 `forbidden`이다. null·빈 문자열·`unknown` sentinel을 값으로 만들지 않는다.
- `NOT_APPLICABLE`에서는 승인 rule과 rationale을 요구하며 `value`, `locators`, `alternatives`는 `forbidden`이다.
- `CONFLICTING`에서는 top-level `value`와 `locators`가 `forbidden`이고 `alternatives`가 `required`다. 대안은 최소 2개이며 각각 value, 고유 source claim identity와 그 source에 실제로 resolve되는 최소 1개 locator를 가진다.
- alternative value는 claim type의 canonical value로 비교해 최소 2개의 서로 다른 값을 가져야 한다. 같은 canonical value를 source만 바꿔 반복하면 `CONFLICTING_ALTERNATIVE_DUPLICATE`, 대안이 2개 미만이면 `CONFLICTING_ALTERNATIVES_INSUFFICIENT`, 대안 locator가 없거나 source와 맞지 않으면 `CONFLICTING_ALTERNATIVE_LOCATOR_MISSING` 또는 `INVALID_SOURCE_LOCATOR`다.
- identity 필드의 `CONFLICTING`은 identity gate에서 반드시 `CONTRADICTED`로 전이한다. 모든 `CONFLICTING` claim은 `used_for_decision=false`다.
- `used_for_decision: true`가 되려면 해당 rule이 요구하는 모든 claim이 `VERIFIED`여야 한다.
- 원문이 제공하지 않은 confidence, 통계 경계, hash, locator는 생성하지 않는다.

## 16. `PART_TEST_EVIDENCE v2` 필드 계약

### 16.1 최상위 구조

| 필드 | 수준 | 조건·제약 | 위반 코드/상태 |
|---|---|---|---|
| `schema_version` | `required` | 정확히 `2.0.0` | schema error / `INVALID_INPUT` |
| `kind` | `required` | `PART_TEST_EVIDENCE` | schema error / `INVALID_INPUT` |
| `record_purpose` | `required` | `DISCOVERY` 또는 `DECISION_CANDIDATE` | enum 오류는 `INVALID_INPUT` |
| `evidence_id` | `required` | packet 안에서 고유한 비어 있지 않은 ID | `DUPLICATE_EVIDENCE_ID` / `INVALID_INPUT` |
| `component_id` | `required` | 동일 packet의 BOM component를 참조 | `EVIDENCE_COMPONENT_NOT_FOUND` / `INVALID_INPUT` |
| `tested_identity` | `required` | 16.2 구조 사용 | identity gate로 전달 |
| `source_document` | `required` | 16.3 구조 사용 | provenance gate로 전달 |
| `test_campaign` | `required` | 공통 시험 조건과 sample 집합 | 누락 시 `INVALID_INPUT` |
| `event_records` | `required` | 최소 1개, event ID 고유, event별 구조 사용 | `EVENT_RECORD_MISSING` / `INVALID_INPUT` |
| `review` | `required` | 16.4 immutable review 구조 | 미승인 시 `REVIEW_NOT_APPROVED` / `VALID + HOLD` |
| `metadata.content` | `required` | `data_class`, `producer_id`, `created_at`만 포함하는 stable content metadata | 누락/enum 오류는 `INVALID_INPUT` |
| `metadata.runtime` | `optional` | `validated_at`, `validator_version`, `ingestion_run_id`; content/approval hash에서 제외 | decision provenance에는 기록하되 evidence claim으로 사용 금지 |
| `integrity` | `required` | 16.5의 self-reference 없는 content/approval hash 구조 | 누락 시 `MISSING_CONTENT_HASH` |
| `discovery_context` | `optional` | query, catalog row ID 등 탐색 보조. 수치 근거로 사용 금지 | decision trace가 참조하면 `DISCOVERY_ONLY_INPUT` |
| `evidence_types` | `forbidden` | v1 legacy 집계 필드. event type은 `event_records[].event_type`에서만 파생 | `LEGACY_DUAL_TRUTH` / `INVALID_INPUT` |
| `tid_test_limit` | `forbidden` | v1 단일 headline. TID event claim에서만 표현 | `LEGACY_DUAL_TRUTH` / `INVALID_INPUT` |
| `cross_section` | `forbidden` | v1 단일 headline. event별 curve/point에서만 표현 | `LEGACY_DUAL_TRUTH` / `INVALID_INPUT` |
| `test_conditions` | `forbidden` | v1 flat 조건. `test_campaign`과 event override로 대체 | `LEGACY_DUAL_TRUTH` / `INVALID_INPUT` |

### 16.2 부품 identity

원문 표기와 canonical 식별자를 분리하며 canonical 값은 승인된 정규화 규칙 ID를 가져야 한다.

| 필드 | 수준 | 조건·제약 | identity 판정 영향 |
|---|---|---|---|
| `manufacturer` | `required` claim | `VERIFIED` value는 raw, canonical ID, 필요 시 normalization rule ID를 함께 보존 | 미승인 alias면 `PARTIAL_UNRESOLVED`; `CONFLICTING`이면 `CONTRADICTED` |
| `orderable_part_number` | `required` claim | `VERIFIED` value는 suffix 포함 raw와 lossless canonical을 함께 보존; `NOT_APPLICABLE`은 금지 | `NOT_REPORTED`면 family relation 유무에 따라 `FAMILY_ONLY` 또는 `PARTIAL_UNRESOLVED`; `CONFLICTING`이면 `CONTRADICTED` |
| `generic_part_number` | `conditional` claim | family discovery를 주장하면 `VERIFIED`와 승인 family relation 필수 | exact PN `NOT_REPORTED`이며 승인 relation이 있으면 `FAMILY_ONLY` |
| `family_relation` | `conditional` | `FAMILY_ONLY`이면 relation type, registry/rule version, reviewer, source locator 필수 | 누락/미승인은 `IDENTITY_FIELD_UNRESOLVED` |
| `smd_or_vid`, `quality_grade` | `conditional` | BOM 또는 시험 원문이 식별에 사용하면 claim wrapper로 필수 | 미보고면 `PARTIAL_UNRESOLVED` 가능 |
| `package`, `temperature_grade`, `lead_finish` | `conditional` | policy가 radiation applicability 필드로 지정하거나 양쪽 중 한쪽이 보고하면 claim wrapper 필수 | 모순 시 `CONTRADICTED` |
| `technology`, `process_id`, `process_node` | `conditional` | 해당 event/policy가 공정 민감으로 지정하면 필수 claim | 미보고면 `PARTIAL_UNRESOLVED`; 모순이면 `CONTRADICTED` |
| `die_id`, `die_revision`, `mask_revision` | `conditional` | 원문/BOM/PCN 중 하나가 식별하면 claim wrapper 필수 | 모순이면 `CONTRADICTED` |
| `wafer_fab`, `wafer_lot` | `conditional` | lot-specific evidence 또는 policy 요구 시 필수 claim | 미보고면 `PARTIAL_UNRESOLVED` |
| `assembly_site`, `assembly_lot`, `test_lot` | `conditional` | package/assembly 민감 또는 policy 요구 시 필수 claim | 모순이면 `CONTRADICTED` |
| `lot_id`, `date_code` | `conditional` | lot/date-code 적용을 주장하려면 `VERIFIED` 필수 | 미보고면 `PARTIAL_UNRESOLVED`; 모순이면 `CONTRADICTED` |
| `sample_markings`, `sample_serials` | `optional` | 공개·권리 허용 범위에서만 보존 | 없다고 자동 mismatch하지 않음 |
| `pcn_relations` | `conditional` | 시험일 이후 procurement 또는 revision이면 확인 결과 필수 | 미확인 시 `MANUFACTURING_CHANGE_UNKNOWN` |
| suffix 제거 canonicalization | `forbidden` | ordering suffix, package, grade 문자를 삭제해 exact match를 만들 수 없음 | `IDENTITY_NORMALIZATION_LOSSY` |
| manufacturer 이름 유사도 자동 merge | `forbidden` | 승인 alias relation 없이 canonical ID를 같게 만들 수 없음 | `MANUFACTURER_ALIAS_UNAPPROVED` |

`DISCOVERY` record는 exact PN claim이 `NOT_REPORTED`여도 schema-valid하다. 승인된 `generic_part_number`와 `family_relation`이 있으면 `FAMILY_ONLY`, 그것도 없으면 `PARTIAL_UNRESOLVED`가 된다. `DECISION_CANDIDATE`는 exact PN과 manufacturer가 모두 `VERIFIED`여야 decision eligibility를 평가할 수 있고, 그렇지 않으면 record 자체를 버리지 않되 `used_for_decision=false`와 blocking status를 반환한다. family 자료는 어떤 경우에도 support decision 입력이 될 수 없다.

### 16.3 출처·권리·원문 위치

| 필드 | 수준 | 조건·제약 | 위반 코드/상태 |
|---|---|---|---|
| `document_id`, `issuer` | `required` | 문서 안정 식별자와 발행 주체 | 누락 시 schema error / `INVALID_INPUT` |
| `title` | `conditional` | 원문에 제목이 있으면 `VERIFIED`; 없으면 `NOT_REPORTED` claim | claim wrapper 누락 시 schema error / `INVALID_INPUT` |
| `landing_uri` | `required` | 공식 색인 또는 문서 landing 위치 | 누락 시 schema error / `INVALID_INPUT` |
| `document_uri` | `conditional` | 원문 접근 위치. 후보 보존에는 `NOT_REPORTED` 가능하나 decision 사용에는 `VERIFIED` 필수 | decision 사용 시 누락/깨짐은 `ORIGINAL_UNAVAILABLE` |
| `revision`, `publication_date` | `conditional` | 원문에 존재하면 `VERIFIED`; 없으면 `NOT_REPORTED` claim | 최신성 미해결 시 `DOCUMENT_REVISION_UNKNOWN` |
| `retrieved_at`, `access_method` | `required` | ISO timestamp와 public/login/API/customer-delivery 방식 | 누락 시 schema error / `INVALID_INPUT` |
| `terms_uri`, `rights_checked_at`, `rights_status` | `required` | rights 검토 근거와 상태. 미확인은 `rights_status=UNRESOLVED`로 명시 | 필드 누락은 `INVALID_INPUT`; 상태 미확인은 `RIGHTS_UNRESOLVED` |
| `allowed_actions.link/cache/extract_facts/quote/redistribute` | `required` | 각각 `ALLOWED`, `FORBIDDEN`, `UNRESOLVED` enum; 하나의 free text나 임의 boolean default로 대체 금지 | 필드 누락은 `INVALID_INPUT`; 필요한 action이 `UNRESOLVED`면 `RIGHTS_UNRESOLVED` |
| `authentication_scope`, `tenant_id`, `retention_policy` | `conditional` | 제한/고객 문서이면 필수 | 누락 시 `CUSTOMER_DATA_UNAUTHORIZED` |
| `artifact_ref` | `conditional` | cache 허용 및 원문을 저장했을 때만 존재 | 무단 저장이면 `RIGHTS_SCOPE_VIOLATION` |
| `artifact_sha256` | `conditional` | decision 사용 시 실제 원문 bytes로 계산된 hash 필수 | 누락/불일치 시 `ARTIFACT_HASH_MISSING`/`ARTIFACT_HASH_MISMATCH` |
| `locators[]` | `conditional` | decision에 사용되는 모든 claim마다 최소 1개 | `SOURCE_LOCATOR_MISSING` |
| 검색 snippet, 브라우저 생성 줄 번호, LLM 요약 locator | `forbidden` | 원문 locator가 아님 | `INVALID_SOURCE_LOCATOR` |
| 권리 미확인 PDF의 repo/object storage 저장 | `forbidden` | `cache=true` 확인 전 저장 금지 | `RIGHTS_SCOPE_VIOLATION` |

locator는 고유 `locator_id`와 `source_document_id`를 가지며 `media_type`별 discriminated union으로 구현한다. PDF는 page label/index와 section/table/figure/row/column 또는 bounding box, HTML은 heading/record key/text anchor와 snapshot time, database는 record ID/field/snapshot, datasheet·PCN은 document ID/revision/page/section을 사용한다.

### 16.4 검토·승인 이력

| 필드 | 수준 | 조건·제약 | 위반 코드/상태 |
|---|---|---|---|
| `review.status` | `required` | `DISCOVERED`, `RIGHTS_CHECKED`, `HASHED`, `EXTRACTED`, `IDENTITY_REVIEWED`, `TECHNICAL_REVIEWED`, `APPLICABILITY_REVIEWED`, `APPROVED`, `REJECTED` | enum 오류는 `INVALID_INPUT` |
| `history[]` | `required` | 최소 1개, append-only; 각 entry는 16.5의 hash chain 구조 | 누락/순서 역전/chain 불일치는 `REVIEW_HISTORY_INVALID` |
| `history_head_sha256` | `required` | 현재 마지막 entry의 실제 `entry_sha256`와 일치 | 불일치는 `REVIEW_HISTORY_INVALID` |
| `history_anchor_ref` | `conditional` | `APPROVED` 또는 decision 사용 시 append-only 외부 audit/object generation의 `store_id`, `anchor_id`, `anchored_head_sha256` 필수 | 누락/외부 anchor 불일치는 `REVIEW_HISTORY_ANCHOR_MISSING`/`REVIEW_HISTORY_ANCHOR_MISMATCH` |
| `extractor` | `conditional` | 자동 추출 사용 시 engine/version/run ID 필수 | 누락 시 `EXTRACTION_PROVENANCE_MISSING` |
| `stage_assertions[]` | `conditional` | identity/technical/applicability 단계 완료 주장 시 stage, `actor_id`, `completed_at`, finding, `evidence_content_sha256` 필수 | 누락/현재 content hash 불일치는 `REVIEW_NOT_APPROVED` |
| `approved_by`, `approved_at`, `approved_target_sha256` | `conditional` | `APPROVED`이면 필수; 16.5에서 계산한 approval target을 참조 | 누락/불일치는 `REVIEW_NOT_APPROVED` |
| `supersedes_evidence_content_sha256` | `conditional` | 승인된 evidence content를 수정한 새 revision이면 필수 | 누락 시 `REVIEW_HISTORY_INVALID` |
| `supersedes_approval_target_sha256` | `conditional` | review assertion 변경으로 새 approval target을 만들면 필수 | 누락 시 `REVIEW_HISTORY_INVALID` |
| 승인 전 `used_for_decision: true` | `forbidden` | `APPROVED`만 판정 입력 가능 | `REVIEW_NOT_APPROVED` |
| 기존 승인 history 덮어쓰기 | `forbidden` | 새 record/hash와 supersedes relation을 생성 | `REVIEW_HISTORY_INVALID` |

### 16.5 자기참조 없는 hash와 canonicalization

#### hash 경계

| hash | 계산 대상 projection | 명시적 제외 | 변경 영향 |
|---|---|---|---|
| `integrity.evidence_content_sha256` | `schema_version`, `kind`, `record_purpose`, `evidence_id`, `component_id`, `tested_identity`, `source_document`, `test_campaign`, `event_records`, `metadata.content` | 전체 `integrity`, 전체 `review`, `discovery_context`, decision 결과, `metadata.runtime` | evidence claim·identity·원문·시험 조건이 바뀌면 변경 |
| `integrity.approval_target_sha256` | `{evidence_content_sha256, schema_version, evidence_id, stage_assertions}` projection | `approved_by`, `approved_at`, `approved_target_sha256`, 전체 `history`, supersedes 필드 | content hash 또는 사전 review assertion이 바뀌면 변경 |
| `review.history[].entry_sha256` | 해당 entry의 `{sequence, previous_entry_sha256, action, actor, role, occurred_at, target_type, target_sha256, rationale}` | 자기 자신의 `entry_sha256`와 record의 다른 필드 | entry 추가 시 새 entry hash만 생성; 기존 entry 수정은 chain 위반 |

`record_sha256`와 `approved_record_sha256`는 v2에서 `forbidden`이다. 전체 record envelope 자체를 내부 필드로 hash하지 않는다. 배포 시스템이 envelope hash를 원하면 v2 record 밖의 immutable object manifest에서 계산한다.

#### canonical serialization과 배열 규칙

1. 위 projection을 만든 뒤 RFC 8785 JSON Canonicalization Scheme 규칙으로 UTF-8, BOM 없음, 공백 없음의 bytes를 만든다.
2. object key는 JCS 규칙으로 정렬한다. 문자열은 Unicode normalization을 추가로 수행하지 않고 schema가 받은 code point를 그대로 보존한다.
3. schema는 모든 배열에 `order_semantics=SET | SEQUENCE | APPEND_CHAIN`을 지정해야 하며 미지정 배열은 `INVALID_INPUT`이다. `SET`은 hash 전에 schema의 stable key로 정렬한다: `event_records:event_id`, `sample_set:sample_id`, `locators:locator_id`, `alternatives:alternative_id`, `pcn_relations:relation_id`, `stage_assertions:(stage, actor_id, completed_at)`이다. key 중복은 hash 전에 `INVALID_INPUT`이다.
4. `SEQUENCE` 배열은 재정렬하지 않는다. dose step, cross-section point, voltage/sweep point는 명시적 `sequence` 오름차순으로 이미 저장돼야 하며 중복·역전이면 `INVALID_INPUT`이다.
5. `review.history`는 append 순서이며 정렬하지 않는다. sequence는 0부터 연속 증가하고 첫 entry의 `previous_entry_sha256`는 없으며 이후 entry는 바로 앞의 실제 `entry_sha256`를 참조한다.
6. SHA-256 결과는 lowercase 64-hex로 저장하지만 fixture 작성자가 digest를 임의 기입하지 않고 validator가 실제 canonical bytes에서 계산한다.

#### 검증 순서

1. hash 값을 신뢰하지 않은 상태로 schema와 ID/sequence uniqueness를 검사한다.
2. 권리가 허용된 artifact bytes와 `artifact_sha256`, locator resolution을 검사한다.
3. content projection을 canonicalize해 `evidence_content_sha256`를 재계산한다.
4. claim union과 identity/applicability 의미 gate를 검사한다.
5. history entry를 sequence 0부터 재계산해 chain과 `history_head_sha256`를 검증한다. 승인·decision record는 외부 append-only audit/object generation의 anchored head와도 비교한다.
6. 현재 content hash와 stage assertions로 approval target을 재계산한다.
7. `APPROVED`이면 `approved_target_sha256` 일치와 approval action history entry를 확인한다.
8. 모든 선행 gate가 통과한 뒤에만 `used_for_decision`을 평가한다.

#### 수정·supersedes 규칙

- evidence content를 수정하면 `evidence_content_sha256`와 `approval_target_sha256`가 모두 바뀐다. 기존 승인을 무효화하고 새 immutable revision에 `supersedes_evidence_content_sha256`, 새 stage assertions, 새 approval을 기록한다.
- content는 같고 stage assertion만 추가·수정하면 content hash는 유지되고 approval target hash는 바뀐다. assertion을 덮어쓰지 않고 새 revision/history action과 `supersedes_approval_target_sha256`를 기록한 뒤 다시 승인한다.
- history에 정상 action을 append하면 content hash와 approval target hash는 바뀌지 않고 새 entry/head hash와 새 외부 anchor event만 생긴다. 기존 entry를 수정·삭제·재정렬하면 해당 entry부터 chain이 깨져 `REVIEW_HISTORY_TAMPERED`다. 과거부터 전부 다시 hash한 chain도 이전 외부 anchored head와 supersedes 관계가 없으면 `REVIEW_HISTORY_ANCHOR_MISMATCH`다.
- approver/time/status 정정은 기존 값을 덮어쓰지 않고 correction/rejection/reapproval action을 append한다. approval target은 대상이 같으면 유지되지만 새 history entry hash가 생성된다.

#### self-reference 없는 정상 예시

```text
P_content = project(record, include = [schema_version, kind, record_purpose,
                    evidence_id, component_id, tested_identity, source_document,
                    test_campaign, event_records, metadata.content])
H_content = sha256(JCS(P_content))
P_approval = { evidence_content_sha256: H_content,
               schema_version, evidence_id, sorted(stage_assertions) }
H_approval = sha256(JCS(P_approval))
E0_without_hash = { sequence: 0, action: CREATED, target_type: EVIDENCE_CONTENT,
                    target_sha256: H_content, ... }
E0.entry_sha256 = sha256(JCS(E0_without_hash))
E1_without_hash = { sequence: 1, previous_entry_sha256: E0.entry_sha256,
                    action: APPROVED, target_type: APPROVAL_TARGET,
                    target_sha256: H_approval, ... }
E1.entry_sha256 = sha256(JCS(E1_without_hash))
```

예시는 hash 값을 발명하지 않고 계산 dependency만 보인다. 정상 fixture는 synthetic JSON의 실제 projection bytes에서 `H_content`, `H_approval`, entry hash를 테스트 중 계산해야 한다.

## 17. `PART_TEST_EVIDENCE v2`와 additive 확장 비교

| 비교 항목 | v1 additive 확장 | 별도 `PART_TEST_EVIDENCE v2` |
|---|---|---|
| 기존 v1 payload | 새 validator에서는 유지 가능 | v2 schema에는 직접 유효하지 않음; v1 validator는 계속 유지 |
| 구 validator와 새 payload | `additionalProperties: false` 때문에 새 필드를 거부하므로 양방향 호환 아님 | version별 validator 선택으로 명확히 분리 |
| legacy/new 필드 충돌 | `evidence_types`, `cross_section`, 새 event records가 서로 다른 값을 가질 수 있음 | legacy 필드를 금지해 단일 진실 유지 |
| event별 필수 조건 | optional additive 필드만으로는 기존 payload를 깨지 않고 강제하기 어려움 | event discriminator로 schema/semantic 필수 조건 강제 가능 |
| identity 누락/모순 분리 | 기존 `partIdentity` 의미를 바꾸면 Stage 2 fixture code가 달라짐 | v2 전용 identity gate와 오류 코드 사용 가능 |
| provenance·rights | 기존 `source` free text와 병행해 우회 가능 | typed rights와 claim locator를 decision gate에 직접 연결 |
| migration 비용 | 낮아 보이나 dual-read·우회 방어와 validator 분기가 누적 | 초기 migration과 adapter 비용이 명시적 |
| False PASS 위험 | 높음: legacy 값만 채운 optimistic packet이 새 gate를 우회할 수 있음 | 낮음: v2 decision eligibility를 한 경로에서 강제 |
| 권고 | discovery-only prototype에만 허용 | **실제 Stage 4 구현 권고안** |

권고안은 다음과 같다.

1. v1 schema/validator/fixture는 통합된 Stage 2 합성 기준선으로 동결한다.
2. 실제 부품 경로는 packet 또는 input-level `schema_version=2.0.0`으로 v2 validator를 선택한다.
3. v1→v2 adapter는 값을 채워 넣지 않는다. 없는 필드는 `NOT_REPORTED` claim과 blocking gap으로 변환한다.
4. v1 `cross_section`을 event type 추론으로 SEL·SEB·SEGR에 복사하지 않는다.
5. v1 payload에서 변환된 v2 record는 재검토·실제 artifact hash·locator가 없으면 `used_for_decision=false`다.
6. v1과 v2 결과를 같은 packet에서 허용할 경우 rule result는 schema version과 exact input pointer를 함께 기록하고, v1 trace는 실제 지원 판정에 사용할 수 없게 한다.
7. v1 exact PN에 검증 가능한 원문 locator가 없으면 문자열을 `discovery_context.legacy_values`에 보존하되 v2 exact PN claim은 `NOT_REPORTED`로 만든다. locator 재검토 없이 `VERIFIED`로 승격하지 않는다.
8. v1 family/generic 값은 승인 family relation과 locator가 확인된 경우에만 `FAMILY_ONLY`가 된다. 그렇지 않으면 `PARTIAL_UNRESOLVED`와 `MIGRATION_REVIEW_REQUIRED`다.
9. v1의 여러 값이 충돌해도 각 값의 source claim identity와 locator를 만들 수 없으면 불완전한 `CONFLICTING` claim을 생성하지 않는다. legacy 값은 discovery context에 격리하고 claim은 `NOT_REPORTED`로 두며 재추출을 요구한다.
10. v1 hash는 v2 `evidence_content_sha256`, `approval_target_sha256` 또는 history entry hash로 복사하지 않는다. 변환된 실제 v2 projection에서 content hash를 새로 계산하고 review는 `DISCOVERED`부터 새 chain으로 시작한다.

## 18. 결정론적 identity 판정표와 우선순위

### 평가 전제

- 비교는 raw 값 보존 후 승인된 lossless 정규화 규칙만 적용한다.
- manufacturer alias는 versioned alias registry의 명시 relation과 reviewer를 요구한다.
- “필수 비교 필드”는 고정 전역 목록이 아니라 event type과 승인 policy가 만든다. manufacturer와 exact orderable PN claim 객체는 항상 존재하지만, discovery record에서는 exact PN claim의 `NOT_REPORTED`가 허용된다.
- 하나의 evidence record가 여러 BOM component에 연결되면 component별로 독립 판정한다.

### 우선순위

1. claim 객체 자체 누락, malformed union 또는 BOM reference 오류 → identity status를 만들지 않고 `INVALID_INPUT`.
2. manufacturer/exact PN/필수 identity claim이 `CONFLICTING`, 또는 양쪽의 `VERIFIED` 값이 하나라도 다름 → `CONTRADICTED`.
3. manufacturer는 `VERIFIED`, exact PN은 `NOT_REPORTED`, generic PN과 승인 family relation은 `VERIFIED` → `FAMILY_ONLY`.
4. exact PN이 `NOT_REPORTED`이고 승인 family relation이 없거나, anchor는 일치하지만 다른 필수 identity/alias/PCN이 미해결 → `PARTIAL_UNRESOLVED`.
5. manufacturer와 exact PN을 포함한 모든 필수 비교 claim이 `VERIFIED`이고 같으며 모순·stale gap이 없음 → `EXACT_MATCH`.

모순이 있으면 동시에 누락 필드가 있어도 `CONTRADICTED`가 우선한다. `FAMILY_ONLY`는 exact PN 불일치를 숨기지 않는다. exact PN이 양쪽에서 보고됐고 다르면 family가 같아도 `CONTRADICTED`다.

| 판정 | 결정 조건 | processing/assurance 종료 | decision 사용 |
|---|---|---|---|
| `EXACT_MATCH` | 승인 alias가 적용된 manufacturer와 exact PN 일치, policy-required identity claim 모두 `VERIFIED`·동일, PCN stale gap 없음 | identity gate 통과; 다음 applicability gate로 진행 | 아직 자동 지원 아님 |
| `PARTIAL_UNRESOLVED` | exact PN `NOT_REPORTED`이며 승인 family relation 없음, 또는 필수 identity/PCN `NOT_REPORTED`·alias 미승인이고 확인된 모순 없음 | `VALID + INSUFFICIENT_EVIDENCE`; blocking `IDENTITY_FIELD_UNRESOLVED` | `used_for_decision=false` |
| `CONTRADICTED` | identity claim이 `CONFLICTING`, 하나 이상의 양측 `VERIFIED` anchor/필수 identity가 다름, 또는 alias registry가 다른 법인을 가리킴 | `CONFLICTING_EVIDENCE + HOLD`; field-specific conflict code | `used_for_decision=false` |
| `FAMILY_ONLY` | manufacturer `VERIFIED`, exact PN `NOT_REPORTED`, generic PN과 승인 family relation `VERIFIED` | `VALID + INSUFFICIENT_EVIDENCE`; `FAMILY_ONLY_EVIDENCE` | schema-valid discovery record로만 사용; support decision 절대 금지 |

필드별 conflict code는 `PART_NUMBER_CONFLICT`, `MANUFACTURER_CONFLICT`, `PROCESS_CONFLICT`, `DIE_CONFLICT`, `LOT_CONFLICT`, `DATE_CODE_CONFLICT`, `PACKAGE_GRADE_CONFLICT`로 분리하고 상위 `IDENTITY_CONFLICT`도 함께 반환한다.

## 19. event별 최소 필드와 누락 종료 상태

### 공통 event 필드

모든 event record는 `event_id`, `event_type`, `test_method.name/issue`, sample set, facility/date, radiation source, electrical/thermal conditions, result claims, claim locators를 가진다. 공통 필드가 원문에 없으면 claim을 `NOT_REPORTED`로 남길 수 있지만 decision eligibility는 event별 표를 따른다.

| event | decision 사용에 필요한 최소 `VERIFIED` 필드 | conditional/optional | 금지 대체 | 최소 필드 누락 시 종료 |
|---|---|---|---|---|
| `TID` | source type, target material, dose unit, dose rate, bias/operating state, temperature, sample/control count, dose steps 또는 검증 범위, `maximum_irradiated_dose`, `maximum_within_spec_dose`, 측정 파라미터·spec limit, locator | anneal 조건은 수행/표준·정책 요구 시 `conditional`; facility uncertainty는 보고 시 `optional` | 최대 조사량을 규격 내 확인량/보증 등급으로 복사, SEE 중 부수 dose를 전용 TID 증거로 승격 | provenance 누락이면 `PROVENANCE_FAILURE + HOLD`; 시험 의미 필드 누락이면 `VALID + INSUFFICIENT_EVIDENCE`; 요구 dose 초과면 `VALID + HOLD/NOT_APPLICABLE` |
| `SEU` | particle class, species 또는 proton energy, LET basis 또는 energy basis, flux, fluence, observed event count, denominator value/basis, cross-section points와 `cm2/device`/`cm2/bit` basis, device configuration/workload, temperature/bias, locator | fit model/parameters는 rate 계산에 사용 시 `conditional`; zero-event statistical bound는 0 event를 제한 근거로 사용할 때 `conditional` | device↔bit 무근거 변환, headline cross-section만으로 curve 대체, SEL/SEB/SEGR 대체 | cross-section/range 누락은 `VALID + INSUFFICIENT_EVIDENCE`; 0 event bound 누락은 `VALID + HOLD`; basis 불일치는 `INVALID_INPUT` |
| `SEL` | particle/LET 또는 energy, flux/fluence, supply/bias, worst-case temperature 근거, trigger/detection current, current limit와 trip delay, observed event count, recovery/power-cycle 결과, destructive/latent-damage 및 post-test electrical, locator | zero-event bound는 0 event 주장 시 `conditional` | SEU/ECC로 대체, 조건 없는 `immune`, 단순 기능 회복을 latent damage 없음으로 대체 | 필드/통계 누락은 `VALID + INSUFFICIENT_EVIDENCE` 또는 `HOLD`; 다른 event 대체는 `EVIDENCE_TYPE_SUBSTITUTION + HOLD` |
| `SEB` | device topology, particle/LET/range/angle, flux/fluence, `VDS/VGS/ID`와 load, temperature, voltage step sequence, failure criterion, observed events, verified safe operating boundary, post-test leakage/function, locator | rated-breakdown 비율은 rating source가 있을 때 `conditional` | SEL/SEU 수치 대체, 시험 전압·LET 밖 safe boundary 외삽 | 핵심 condition 누락은 `VALID + INSUFFICIENT_EVIDENCE`; 범위 초과는 `VALID + HOLD/NOT_APPLICABLE` |
| `SEGR` | particle/LET/range/angle, flux/fluence, gate/drain bias, voltage step size, rupture/microbreak criterion, gate leakage 전·후, observed events, verified safe operating boundary, post-test inspection, locator | 추가 물리 분석은 원문 보고 시 `optional` | SEB/SEU 수치 대체, 기능 유지로 gate integrity 증명 | 핵심 condition 누락은 `VALID + INSUFFICIENT_EVIDENCE`; 범위 초과는 `VALID + HOLD/NOT_APPLICABLE` |

`maximum_irradiated_dose`, `maximum_within_spec_dose`, manufacturer guaranteed rating은 서로 다른 claim type이다. guaranteed rating은 manufacturer qualification 문서와 locator가 있을 때만 별도 evidence로 존재하며 시험 보고서의 최대 dose에서 계산하지 않는다.

## 20. 공격 fixture 명세

### fixture 작성 규칙

- 부품·기관·수치는 전부 명시적 `SYNTHETIC` fixture 전용 값만 사용한다.
- 실제 부품번호, 실제 시험 수치, 실제 고객 자료를 fixture에 섞지 않는다.
- hash가 필요한 fixture는 저장된 작은 fixture artifact의 실제 bytes로 테스트 중 계산한다. 반복 문자나 임의 digest를 “유효 hash”로 사용하지 않는다.
- locator가 필요한 fixture는 fixture artifact에 실제 존재하는 section/row/cell을 가리킨다. 존재하지 않는 locator는 오직 locator 공격 case의 변이로만 만든다.
- 임의 confidence를 만들지 않는다. zero-event bound case는 “경계 없음” 자체를 공격 조건으로 사용한다.
- 각 case는 target code가 반드시 포함되는지와 `SUPPORTED_WITH_MITIGATION`이 불가능한지를 모두 assert한다. `NON_EVIDENTIARY_SOURCE_INPUT` 같은 독립 안전 코드가 함께 나와도 target code가 사라지면 실패다.

### 필수 공격 case

| fixture ID | 기준 fixture와 변이 | 기대 primary code | 기대 종료와 필수 assertion |
|---|---|---|---|
| `parts-v2-suffix-stripped-false-exact` | BOM과 evidence의 exact PN suffix가 다르지만 normalizer가 suffix를 제거해 같은 canonical PN과 `EXACT_MATCH`를 생성 | `IDENTITY_NORMALIZATION_LOSSY`, `PART_NUMBER_CONFLICT` | `CONFLICTING_EVIDENCE + HOLD`; exact/support 금지 |
| `parts-v2-manufacturer-alias-mismap` | 서로 다른 manufacturer raw 값을 승인 alias relation 없이 같은 canonical ID로 매핑 | `MANUFACTURER_ALIAS_UNAPPROVED` 또는 verified registry conflict이면 `MANUFACTURER_CONFLICT` | `PARTIAL_UNRESOLVED` 또는 `CONTRADICTED`; support 금지 |
| `parts-v2-process-conflict` | 양쪽 `VERIFIED` process claim만 다르게 변이 | `PROCESS_CONFLICT`, `IDENTITY_CONFLICT` | `CONFLICTING_EVIDENCE + HOLD` |
| `parts-v2-die-conflict` | 양쪽 `VERIFIED` die ID/revision만 다르게 변이 | `DIE_CONFLICT`, `IDENTITY_CONFLICT` | `CONFLICTING_EVIDENCE + HOLD` |
| `parts-v2-lot-conflict` | 양쪽 `VERIFIED` lot/date-code 중 하나를 다르게 변이 | `LOT_CONFLICT` 또는 `DATE_CODE_CONFLICT`, `IDENTITY_CONFLICT` | `CONFLICTING_EVIDENCE + HOLD` |
| `parts-v2-missing-lot-is-unresolved` | BOM은 lot을 `VERIFIED`, evidence lot은 `NOT_REPORTED`; mismatch로 분류하도록 공격 | `IDENTITY_FIELD_UNRESOLVED` | `PARTIAL_UNRESOLVED`, `VALID + INSUFFICIENT_EVIDENCE`; `CONTRADICTED`가 아니며 support 금지 |
| `parts-v2-seu-substituted-for-sel` | policy가 SEL을 요구하지만 SEU event의 cross-section/zero-event claim을 SEL coverage로 연결하거나 event type만 SEL로 변경 | `EVIDENCE_TYPE_SUBSTITUTION`, `DESTRUCTIVE_SEE_MODE_MISSING` | `VALID + INSUFFICIENT_EVIDENCE/HOLD`; SEL rule PASS 금지 |
| `parts-v2-zero-event-promoted-to-immunity` | observed event count 0만 있고 bound/detection/fluence coverage가 미해결인데 `immune=true` 또는 rule PASS로 변이 | `ZERO_EVENT_BOUND_MISSING`, `IMMUNITY_CLAIM_UNSUPPORTED` | `VALID + HOLD`; optimistic decision 금지 |
| `parts-v2-max-dose-promoted-to-rating` | `maximum_irradiated_dose`를 `maximum_within_spec_dose` 또는 guaranteed rating으로 복사하고 독립 parameter/qualification locator를 제거 | `TID_RATING_NOT_ESTABLISHED`, locator가 없으면 `SOURCE_LOCATOR_MISSING` | `PROVENANCE_FAILURE` 우선 또는 `VALID + HOLD`; TID margin PASS 금지 |
| `parts-v2-test-range-extrapolated` | mission/policy requirement가 verified dose/LET/energy/voltage boundary를 넘는데 applicability와 rule을 PASS로 변이 | `OUT_OF_TEST_SCOPE`, `DECISION_TRACE_NOT_APPLICABLE` | `VALID + HOLD`, applicability `NOT_APPLICABLE` |
| `parts-v2-artifact-hash-missing` | decision-used claim의 `artifact_sha256` 제거 | `ARTIFACT_HASH_MISSING` | `PROVENANCE_FAILURE + HOLD`; support 금지 |
| `parts-v2-artifact-hash-mismatch` | 실제 fixture bytes와 다른 digest로 변이 | `ARTIFACT_HASH_MISMATCH` | `PROVENANCE_FAILURE + HOLD`; support 금지 |
| `parts-v2-claim-locator-missing` | decision-used claim의 locator 배열 제거 | `SOURCE_LOCATOR_MISSING` | `PROVENANCE_FAILURE + HOLD`; support 금지 |
| `parts-v2-claim-locator-broken` | locator를 artifact에 없는 page/row/cell로 변이 | `INVALID_SOURCE_LOCATOR` | `PROVENANCE_FAILURE + HOLD`; support 금지 |
| `parts-v2-review-not-approved` | review를 `TECHNICAL_REVIEWED` 이하로 두거나 approver/approved target hash를 제거하면서 decision trace 사용 | `REVIEW_NOT_APPROVED` | `VALID + HOLD`; `used_for_decision=false` 강제 |
| `parts-v2-approved-target-stale` | 승인 뒤 evidence content 또는 stage assertion을 수정하되 approval target과 해당 supersedes relation을 갱신하지 않음 | `CONTENT_HASH_MISMATCH` 또는 `APPROVAL_TARGET_HASH_MISMATCH`, `REVIEW_NOT_APPROVED` | `PROVENANCE_FAILURE + HOLD` |
| `parts-v2-legacy-dual-truth` | v2 event record와 서로 다른 v1 `cross_section` 또는 `tid_test_limit`을 함께 삽입 | `LEGACY_DUAL_TRUTH` | `INVALID_INPUT + HOLD` |

Workstream 60은 각 공격의 반대편 정상 fixture도 가져야 한다. 예를 들어 lot이 양쪽에서 같은 경우와 evidence 쪽이 `NOT_REPORTED`인 경우를 분리해, 누락을 모순으로 오탐하지 않으면서 둘 다 지원 판정으로 승격되지 않는지 확인한다.

### H02 hash 정상·변조 fixture

| fixture ID | 구성 또는 변이 | 기대 결과 |
|---|---|---|
| `parts-v2-hash-chain-valid` | synthetic content projection에서 content hash를 계산하고, stage assertions로 approval target을 계산한 뒤 두 history entry를 실제 bytes로 연쇄 계산 | schema-valid; 모든 hash 재계산 일치. 다른 gate가 충족된 경우에만 decision 평가 진행 |
| `parts-v2-content-tampered-after-approval` | 정상 fixture의 identity 또는 event claim을 바꾸고 저장된 content/approval hash와 history는 유지 | `CONTENT_HASH_MISMATCH`, `APPROVAL_TARGET_HASH_MISMATCH`, `REVIEW_NOT_APPROVED`; `PROVENANCE_FAILURE + HOLD` |
| `parts-v2-review-history-entry-tampered` | content와 approval target은 유지하되 과거 history entry의 actor/action/time 중 하나를 바꾸고 entry hash·후속 link는 유지 | `REVIEW_HISTORY_TAMPERED`; `PROVENANCE_FAILURE + HOLD` |
| `parts-v2-review-history-rechained-without-supersedes` | 과거 entry를 바꾸고 이후 entry/head hash를 공격자가 다시 계산했지만 이전 외부 anchored head와 supersedes relation이 없음 | `REVIEW_HISTORY_ANCHOR_MISMATCH`; 승인 무효·`HOLD` |

정상 fixture에는 digest literal을 명세서에서 제공하지 않는다. Workstream 60이 저장한 synthetic fixture의 실제 canonical bytes에서 기대 hash를 계산하고, 변조 fixture는 그 정상 fixture를 한 필드씩 바꿔 만든다.

### H02 identity paired fixture

| 상태 | 정상 fixture | 공격 fixture | 기대 판정과 assertion |
|---|---|---|---|
| exact PN 미확인 family 후보 | `parts-v2-family-discovery-valid`: `record_purpose=DISCOVERY`, manufacturer `VERIFIED`, exact PN `NOT_REPORTED`, generic PN/family relation `VERIFIED` | `parts-v2-family-used-for-decision`: 같은 record를 support trace에 연결 | 정상은 `FAMILY_ONLY + INSUFFICIENT_EVIDENCE`; 공격은 `DISCOVERY_ONLY_INPUT`/`FAMILY_ONLY_EVIDENCE`, support 금지 |
| exact PN 누락 unresolved 후보 | `parts-v2-exact-pn-unresolved-valid`: exact PN `NOT_REPORTED`, 승인 family relation 없음 | `parts-v2-unresolved-promoted-to-exact`: same candidate를 `EXACT_MATCH`로 변조 | 정상은 `PARTIAL_UNRESOLVED`; 공격은 `EXACT_PART_NUMBER_UNVERIFIED`, support 금지 |
| 확인된 exact PN conflict | `parts-v2-exact-pn-conflict-valid`: BOM/evidence exact PN이 각각 `VERIFIED`이고 서로 다르거나 claim alternatives가 유효 | `parts-v2-conflict-hidden-by-family`: family가 같다는 이유로 `FAMILY_ONLY`/exact를 생성 | 정상은 `CONTRADICTED + HOLD`; 공격은 `PART_NUMBER_CONFLICT`, `IDENTITY_CONFLICT`, support 금지 |

세 정상 fixture는 모두 schema-valid다. 여기서 “정상”은 안전한 상태 전이가 올바르다는 뜻이지 support 가능하다는 뜻이 아니다.

### H02 `CONFLICTING` claim 정상·공격 fixture

| fixture ID | 구성 또는 변이 | 기대 결과 |
|---|---|---|
| `parts-v2-conflicting-alternatives-valid` | 서로 다른 canonical value 2개, 고유 alternative/source claim ID와 실제 resolve되는 locator를 각각 제공 | schema-valid `CONFLICTING`; identity claim이면 `CONTRADICTED`; `used_for_decision=false` |
| `parts-v2-conflicting-one-alternative` | alternative 하나 제거 | `CONFLICTING_ALTERNATIVES_INSUFFICIENT`; `INVALID_INPUT + HOLD` |
| `parts-v2-conflicting-alternative-locator-missing` | 한 alternative의 locator 제거 | `CONFLICTING_ALTERNATIVE_LOCATOR_MISSING`; `PROVENANCE_FAILURE + HOLD` |
| `parts-v2-conflicting-duplicate-value` | source ID는 다르지만 두 alternative의 canonical value를 같게 변이 | `CONFLICTING_ALTERNATIVE_DUPLICATE`; `INVALID_INPUT + HOLD` |
| `parts-v2-conflicting-used-for-decision` | 유효 `CONFLICTING` claim을 decision trace 입력으로 연결 | `CONFLICTING_CLAIM_DECISION_FORBIDDEN`; `HOLD`, support 금지 |

## 21. Workstream 간 입력·출력 계약과 Exit Gate

### Workstream 10 — Contracts & Schema

**입력:** 16~20절의 v2 필드 규칙, identity 우선순위, event별 최소 필드, 오류 코드와 migration 규칙.

**출력:** versioned v2 schema 세트, validator 선택 규칙, claim discriminated union, self-reference 없는 hash projection/validator, 의미 gate, v1→v2 non-filling adapter, 정상·실패 fixture와 migration 문서.

**Exit Gate:**

- v1 Stage 1/2 검증이 기존 결과를 유지한다.
- v2는 legacy dual truth를 거부하고 event별 필수 조건을 강제한다.
- exact PN `NOT_REPORTED`는 승인 family relation 유무에 따라 `FAMILY_ONLY` 또는 `PARTIAL_UNRESOLVED`, 확인된 exact PN conflict와 identity `CONFLICTING` claim은 `CONTRADICTED`로 구분된다.
- family discovery와 partial candidate는 schema-valid하지만 decision-ineligible이고, malformed claim만 `INVALID_INPUT`이 된다.
- content/approval/history hash가 16.5의 서로 다른 projection과 순서로 재계산되며 content·history 변조를 구분해 거부한다.
- `CONFLICTING`은 서로 다른 대안 2개 이상과 각 source/locator를 강제하고 decision 사용을 거부한다.
- v1 변환 record와 미승인 v2 record는 support decision에 사용되지 않는다.
- schema-only 검사와 semantic gate를 한 명령으로 실행하며 모든 target error code를 검증한다.

### Workstream 30 — Environment Model

**입력:** Workstream 40이 비교해야 할 TID material/dose/dose-rate context와 SEE particle/energy/LET 범위 요구.

**출력:** `environment_id`, model/version/run hash, valid time, shielding/material basis, TID value/unit, particle class별 spectrum, energy bins 또는 LET representation, geometry/angle 가정, 단위와 uncertainty provenance.

**Exit Gate:**

- TID와 SEE applicability 입력을 구분하고 각 값의 origin pointer를 제공한다.
- spectrum/LET가 없는 TID-only 결과는 SEE 적용성을 `UNRESOLVED`로 명시한다.
- Workstream 40이 시험 범위 포함 여부를 결정론적으로 비교할 수 있는 단위·bin boundary가 있다.
- 실제 run이 없으면 `SYNTHETIC` 또는 `HOLD`를 유지한다.

### Workstream 50 — Mitigation & Policy

**입력:** component별 event coverage, identity/applicability status, zero-event bound 유무, destructive event gaps.

**출력:** `required_failure_modes[]`, event별 최소 sample/fluence/range/bound 정책, 허용 test standard/issue, operating envelope, 승인 상태와 예외 승인 이력.

**Exit Gate:**

- boolean destructive gate 대신 SEL·SEB·SEGR 요구를 개별 표현한다.
- ECC/scrubbing/TMR의 적용 failure mode가 명시되고 destructive SEE gate를 통과시키지 않는다.
- 미승인 policy와 예외는 지원 판정을 만들지 못한다.
- 부품 기술에 적용하지 않는 event는 `NOT_APPLICABLE` 근거와 승인 rule을 가진다.

### Workstream 60 — Assurance & Evals

**입력:** 20절 공격 fixture 명세와 Workstream 10의 v2 schema/validator.

**출력:** synthetic-only 정상/공격 fixtures, target code assertions, optimistic-decision 공격 결과, False PASS 집계와 독립 재현 명령.

**Exit Gate:**

- 모든 필수 공격에서 target code와 안전 종료 상태가 재현된다.
- `SUPPORTED_WITH_MITIGATION` False PASS가 0건이다.
- 누락과 모순의 paired fixture가 각각 기대 status를 내며, 누락을 exact match로 승격하지 않는다.
- family-only, exact-PN unresolved, exact-PN conflict paired fixture가 각각 schema-valid한 안전 상태와 공격 차단을 재현한다.
- content 변조와 history 변조가 서로 다른 target code로 검출되고 기존 approval을 무효화한다.
- `CONFLICTING` 대안 수·locator·중복 값·decision 금지 fixture가 모두 target code를 재현한다.
- hash와 locator는 실제 fixture artifact에 대해 계산·해결되고 가짜 provenance를 사용하지 않는다.
- 공격 세트는 향후 Stage 7 배포 경로에서도 같은 결과를 낼 수 있게 독립 패키징된다.

### Workstream 70 — Platform & GCP

**입력:** typed rights, allowed actions, artifact hash, evidence content/approval target/history entry hash projection, locator, review history와 tenant/retention 요구.

**출력:** rights gate, 공개/저작권/고객 자료의 분리 storage, immutable object generation, KMS/IAM, hash verification, locator resolver, history head를 고정하는 append-only review/audit anchor, deletion/retention evidence.

**Exit Gate:**

- `cache=false` 또는 rights 미확인 원문은 storage·Document AI·Vertex AI로 전달되지 않는다.
- artifact bytes와 SHA-256/object generation이 일치하지 않으면 처리 중단한다.
- 고객 tenant 간 object·metadata·log 접근이 격리된다.
- evidence content 수정은 새 content/approval target hash와 `supersedes_evidence_content_sha256`, review assertion 수정은 새 approval target과 `supersedes_approval_target_sha256`를 만들고 기존 history를 보존한다.
- 승인·decision record의 `history_head_sha256`는 외부 immutable anchor와 일치해야 하며 전체 chain 재계산만으로 과거 anchor를 대체할 수 없다.
- provenance·rights·review 실패가 optimistic final decision으로 전파되지 않는다.

## 22. 이 작업 패키지의 남은 HOLD

| 항목 | 상태 | 재개 조건 |
|---|---|---|
| 실제 BOM과 초기 부품 5~10종 | `BOM_MISSING / HOLD` | 승인 BOM owner와 exact identity 입력 확보 |
| 실제 원문·수치·artifact hash·locator | `ORIGINAL_UNAVAILABLE / HOLD` | 문서별 접근·저장·추출 권리와 승인 storage 확보 후 실제 bytes 검증 |
| 법적 재사용 판단 | `RIGHTS_UNRESOLVED / HOLD` | 권리 검토 책임자의 문서별 승인 |
| Stage 3 SEE 환경 | `MISSION_ENVIRONMENT_UNAVAILABLE / HOLD` | spectrum/energy/LET 출력 계약과 실제 provenance |
| schema/validator 구현 | Workstream 10 미착수 | v2 범위 승인과 소유 채팅 구현 |
| 공격 fixture 실행 | Workstream 60 미착수 | v2 validator와 synthetic fixture artifact 구현 |
| mode별 destructive policy | Workstream 50 미착수 | component technology별 required failure mode 승인 |
| 승인 storage·외부 계정 | Workstream 70/Control Tower 결정 필요 | IAM/KMS/tenant/retention과 ESA·제조사 계정 권한 승인 |

이 명세는 실제 부품 증거가 아니며 `PUBLISHED`, `CUSTOMER_VERIFIED`, 실제 `CALCULATED` 값을 추가하지 않는다. v2가 구현돼도 실제 BOM·원문·환경·정책·독립 검증이 모두 연결되기 전에는 Stage 4 지원 판정을 만들 수 없다.

## 23. 작업 패키지 3 — 첫 exact-part Evidence Path

### 23.1 선택 결과와 안전한 종료 상태

MVP 기준 사례의 첫 공개 후보로 Texas Instruments의 exact orderable part `5962L1420901VXC`를 선택했다. 이 선택은 부품 지원·비행 적합성·BOM 채택이 아니라 **원문 추적 경로 검증용 후보 선정**이다.

| 구분 | 관찰값 | 근거 | 상태 |
|---|---|---|---|
| 제조사 | Texas Instruments | exact-part 페이지, TID 보고서 | `VERIFIED_SOURCE_CLAIM` |
| exact orderable PN | `5962L1420901VXC` | exact-part 페이지; SLLK019 p.1, p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| 제품명 | `SN55HVD233-SP` / 보고서 표기 `SN55HVD233-RHA` | TI 제품 페이지; SLLK019 p.1, p.2 Table 1 | alias 관계는 제조사 원문 안에서만 관찰; exact PN이 우선 |
| package | CFP, TI package code `HKX`, 8 pin | exact-part 페이지; SLLK019 p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| grade | Space, QML-V, RHA | exact-part 페이지; SLLK019 p.1 | `VERIFIED_SOURCE_CLAIM` |
| technology/process | `LBC3S` | SLLK019 p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| die lot | `1634103DFB` | SLLK019 p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| assembly/test lot | `7005041MTT` | SLLK019 p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| date code | `1736A` | SLLK019 p.2 Table 1 | `VERIFIED_SOURCE_CLAIM` |
| die revision | 원문에서 확인하지 못함 | SLLK019 검토 범위 | `NOT_REPORTED` |
| 승인 BOM component | 제공되지 않음 | 프로젝트 입력 부재 | `BOM_MISSING` |

따라서 source-side exact identity는 재현되지만 BOM-side 비교 대상이 없다. decision candidate identity는 `EXACT_MATCH`로 승격하지 않고 `PARTIAL_UNRESOLVED`와 `BOM_MISSING`으로 종료한다. 제조사 페이지의 package/grade와 보고서의 exact PN이 일치해도 승인 BOM을 대신하지 않는다.

### 23.2 공식 원문과 locator

| 자료 | URL | 접근일 | 문서 식별자·revision | 이 패키지에서 확인한 위치 |
|---|---|---|---|---|
| TI exact-part 페이지 | <https://www.ti.com/product/SN55HVD233-SP/part-details/5962L1420901VXC> | 2026-08-20 | 웹 페이지, revision 미적용 | exact PN, Space/QML-V/RHA, CFP(HKX), 8 pin |
| TI 제품 페이지 | <https://www.ti.com/product/SN55HVD233-SP> | 2026-08-20 | 웹 페이지, revision 미적용 | QMLV RHA, SMD PN, HKX와 공식 radiation report 링크 |
| TI TID report | <https://www.ti.com/lit/rr/sllk019/sllk019.pdf> | 2026-08-20 | `SLLK019`, February 2018; 별도 revision marker는 확인되지 않아 `NOT_REPORTED` | p.1 title/abstract; p.2 §1.2 Table 1; p.3 §2.1–2.2; p.4 §2.2–2.3/Figure 2; p.5 §2.4 Tables 2–3; p.6 §3.1 |
| TI 이용 약관 | <https://www.ti.com/legal/terms-conditions/terms-of-use.html> | 2026-08-20 | Terms of Use 웹 페이지 | §1 Use of Site Content; §4 Linking; §5 Disclaimer |

PDF page는 파일의 1-based physical page를 뜻한다. locator는 페이지 하나만 쓰지 않고 `page + section/table/figure + claim field`를 함께 사용한다. 보고서의 시험 실행일은 확인하지 못했다. `February 2018`은 문서 발행월이지 시험일로 복사하지 않는다.

### 23.3 artifact 무결성 관찰과 manifest 생성 차단

공식 URL에서 검토 목적으로 임시 취득한 bytes에 대해 다음 값을 실제 계산·대조했다. 원문은 Git, Downloads handoff 또는 프로젝트 storage에 넣지 않았다.

| 필드 | 실제 관찰값 |
|---|---|
| header verification timestamp | `2026-08-20T04:33:36Z` — HTTP `Date`; artifact download time으로 사용 금지 |
| source locator | `https://www.ti.com/lit/rr/sllk019/sllk019.pdf` |
| HTTP status | `200` |
| declared MIME | `application/pdf` |
| detected format | PDF 1.4 |
| byte size | `3568651` |
| SHA-256 | `623b9d19e3b7aba3e55151c7f73f34f47a48f9b36fde46049d6c8d2c79884fa2` |
| HTTP Last-Modified | `Mon, 05 Feb 2018 21:32:33 GMT` |
| HTTP ETag | `\"36740b-5647dcccedf1e\"` |

이 hash는 검토 시점에 취득한 실제 artifact bytes의 관찰값일 뿐 승인 raw artifact manifest나 승인 evidence content hash가 아니다. 다음 필드가 없으므로 `RAW_ARTIFACT_MANIFEST v2` 인스턴스를 만들지 않는다.

- 승인 `tenant_id`, `run_id`, `zone`과 immutable `project_id/bucket_id/object_name/generation`
- 실제 quarantine·malware scan·MIME/hash check workflow와 reviewer
- 권리 책임자가 승인한 `rights_snapshot_id`, approval target/scope hash, history anchor
- 승인 parser name/version/commit과 실제 input/output hash
- 파생 record ID와 retention/deletion 정책

manifest 제안의 종료는 `RAW_MANIFEST_REFERENCE_MISSING`, `RIGHTS_SNAPSHOT_NOT_ACTIVE`, `APPROVED_STORAGE_UNAVAILABLE`이다. schema의 `source.retrieved_at`에는 향후 승인 ingest가 실제로 시작·완료된 시각을 기록하며 위 header 확인 시각을 대입하지 않는다. 실제 storage가 생기면 위 관찰 hash를 업로드된 exact generation bytes에서 다시 계산하고 일치시켜야 하며, 현재 값을 신뢰해 복사만 해서는 안 된다.

### 23.4 권리 action matrix

TI 약관은 비상업적 또는 개인적 목적의 다운로드·복제·표시·배포를 일정 조건 아래 허용하지만, 상업 이용 허가를 일반적으로 부여하지 않는다. 또한 조건부 plain-text link는 허용하고 자동 data mining/scraping은 제한한다. 이 문서는 법률 자문이 아니며, SPECTRA의 데모·상업 범위에 맞는 승인 snapshot은 권리 책임자가 별도로 만들어야 한다.

| action | 관찰 근거 | 운영 상태 | 이유 |
|---|---|---|---|
| `LOCATOR` | TI Terms §4의 조건부 plain-text linking | `ALLOWED_CONDITIONALLY` | TI 소유임을 오인시키지 않고 방해·프레이밍하지 않는 직접 링크만 제안 |
| `FETCH` | TI Terms §1의 비상업/개인 목적 조건 | `UNCONFIRMED` | 프로젝트 사용 목적과 승인 주체가 확정되지 않음 |
| `PRIVATE_STORE` | 같은 조건부 이용 문구 | `UNCONFIRMED` | 승인 storage·retention·권리 snapshot 없음 |
| `PROCESS_DOCUMENT_AI` | 명시 허가 확인 못함 | `UNCONFIRMED` | 원문 외부 processor 제공 권한 미확인 |
| `PROCESS_VERTEX_AI` | 명시 허가 확인 못함 | `UNCONFIRMED` | cloud processor·region·retention 승인 없음 |
| `DISPLAY_INTERNAL` | 비상업/개인 목적 조건과 프로젝트 범위 불일치 가능 | `UNCONFIRMED` | audience와 목적 승인 필요 |
| `DISPLAY_EXTERNAL` | 상업/공개 데모 범위 미확인 | `UNCONFIRMED` | 공개 열람 가능성과 재표시 권리는 다름 |
| `REDISTRIBUTE` | 조건부 비상업 이용 외 일반 허가 확인 못함 | `UNCONFIRMED` | PDF를 Git·handoff에 포함하지 않음 |
| commercial use | 일반 허가 확인 못함 | `UNCONFIRMED` | TI 또는 권리 책임자 확인 필요 |

검토를 위해 임시 취득한 PDF는 이 action matrix의 운영 승인으로 승격하지 않는다. 저장소에는 locator, locator에서 확인한 작은 사실, 실제 관찰 hash와 `HOLD` 사유만 남긴다.

### 23.5 TID claim 정규화 후보

선택한 bundle은 `TID` 하나만 포함한다. 아래는 구현 전 field-level fixture proposal이며 현재 v1 JSON fixture가 아니다. `component_id`, 시험일과 단일 facility를 발명하지 않았고 review approval/hash chain도 만들지 않았다.

| 경로 | 값 또는 상태 | 원문 locator | decision 사용 |
|---|---|---|---|
| `record_purpose` | `DISCOVERY` | 프로젝트 분류 | 금지 |
| `component_ref` | `NOT_REPORTED` | 승인 BOM 없음 | 차단 |
| `identity.manufacturer` | Texas Instruments | exact-part 페이지; SLLK019 p.1 | source claim만 허용 |
| `identity.orderable_part_number` | `5962L1420901VXC` | exact-part 페이지; SLLK019 p.1, p.2 Table 1 | source claim만 허용 |
| `identity.package` | CFP / `HKX` / 8 pin | exact-part 페이지; SLLK019 p.2 Table 1 | source claim만 허용 |
| `identity.grade` | Space / QML-V / RHA | exact-part 페이지; SLLK019 p.1 | source claim만 허용 |
| `identity.process` | `LBC3S` | SLLK019 p.2 Table 1 | source claim만 허용 |
| `identity.die_lot` | `1634103DFB` | SLLK019 p.2 Table 1 | source claim만 허용 |
| `identity.assembly_test_lot` | `7005041MTT` | SLLK019 p.2 Table 1 | source claim만 허용 |
| `identity.date_code` | `1736A` | SLLK019 p.2 Table 1 | source claim만 허용 |
| `identity.die_revision` | `NOT_REPORTED` | 확인 범위 전체 | 차단 가능 gap |
| `report.document_id` | `SLLK019` | p.1 header | provenance만 허용 |
| `report.publication` | February 2018 | p.1 header | 시험일로 사용 금지 |
| `report.revision` | `NOT_REPORTED` | p.1 header | 최신성 검토 gap |
| `report.test_date` | `NOT_REPORTED` | 확인 범위 전체 | 차단 |
| `event_type` | `TID` | report title/abstract | 다른 SEE event로 복사 금지 |
| `method` | MIL-STD-883 TM 1019.9, Conditions A/D | p.3 §2.1 | source claim만 허용 |
| `radiation_source` | Co-60 gamma | p.2 Table 1; p.3–4 §2.2 | source claim만 허용 |
| `temperature` | ambient room temperature; numeric value `NOT_REPORTED` | p.2 Table 1 | 숫자 생성 금지 |
| `sample_quantity` | 57 including 1 control | p.2 Table 1 | bundle context만 허용 |
| `within_spec_through` | 50 krad(Si) | p.2 Table 1; p.6 §3.1 opening sentence | 제한된 source claim; support 판정 금지 |
| `hdr.facility` | TI SVA, Santa Clara, CA | p.2 Table 1; p.4 §2.2 | source claim만 허용 |
| `hdr.dose_rate` | `CONFLICTING` | alternatives 아래 참조 | 금지 |
| `hdr.bias` | biased and unbiased groups | p.4 §2.2–2.3; p.5 Table 2 | source claim만 허용 |
| `ldr.facility` | RAD/Aeroflex, Colorado Springs, CO | p.2 Table 1; p.3 §2.2 | source claim만 허용 |
| `ldr.dose_rate` | 0.01 rad(Si)/s = 10 mrad(Si)/s | p.2 Table 1; p.5 Table 3 | source claim만 허용 |
| `ldr.bias_coverage` | `CONFLICTING` | p.5 Table 3 vs p.6 §3.1 bullets | 금지 |
| `maximum_irradiated_dose` | `CONFLICTING` | p.2/p.5 vs p.6 §3.1 bullets | 금지 |
| `applicability` | `NOT_EVALUATED` | 임무 환경·정책 없음 | 차단 |
| `used_for_decision` | `false` | 모든 blocking gap 집계 | 필수 |
| `termination` | `HOLD` | `BOM_MISSING`, rights/storage/review/applicability gaps, document conflict | 필수 |

`CONFLICTING` 대안은 값을 버리거나 하나를 임의 선택하지 않고 다음처럼 보존한다.

| claim | alternative value | source claim identity | locator |
|---|---|---|---|
| HDR dose rate | 65 rad(Si)/s | `SLLK019-table1-hdr-rate` | p.2 §1.2 Table 1, “Dose Rate” |
| HDR dose rate | 65 rad(Si)/s | `SLLK019-table2-hdr-rate` | p.5 §2.4 Table 2 title |
| HDR dose rate | 100 rad(Si)/s | `SLLK019-section3-hdr-rate` | p.6 §3.1, HDR bullet |
| maximum irradiated dose | 50 krad(Si) | `SLLK019-table1-dose-levels` | p.2 §1.2 Table 1, dose levels/passed levels |
| maximum irradiated dose | 50 krad(Si) | `SLLK019-tables2-3-dose-levels` | p.5 §2.4 Tables 2–3 |
| maximum irradiated dose | HDR 75 / LDR 100 krad(Si)까지 열거 | `SLLK019-section3-post-dose-list` | p.6 §3.1, HDR/LDR bullets |
| LDR bias coverage | only unbiased groups | `SLLK019-table3-ldr-groups` | p.5 §2.4 Table 3 |
| LDR bias coverage | biased/unbiased post-dose groups가 열거됨 | `SLLK019-section3-ldr-groups` | p.6 §3.1, LDR bullets |

같은 canonical value인 첫 두 HDR 대안은 하나의 65 rad(Si)/s 대안으로 병합하고 locator 배열 두 개를 보존한 뒤, 100 rad(Si)/s 대안과 비교해야 한다. `CONFLICTING`의 최소 두 **서로 다른 값** 규칙을 위반하지 않는다. 이 conflict가 해결되기 전에는 report-wide dose rate, 최대 조사량, LDR bias coverage를 decision operand로 사용할 수 없다. 50 krad(Si) “within specification” 문구는 75/100까지의 보증 등급으로 외삽하지 않는다.

### 23.6 독립 사건 유형 coverage

| 사건 유형 | 선택 bundle 상태 | 허용되는 결론 |
|---|---|---|
| TID | 원문 locator가 있는 claim 후보이나 conflict·rights·BOM·applicability 때문에 `HOLD` | 원문이 TID를 시험했다는 사실과 제한된 관찰값만 표시 |
| SEU | `NOT_REPORTED_IN_SELECTED_BUNDLE` | 미시험·면역·0 event라고 말할 수 없음 |
| SEL | `NOT_REPORTED_IN_SELECTED_BUNDLE` | 제품 페이지의 요약 문구나 별도 SEE report를 이 TID bundle로 대체할 수 없음 |
| SEB | `NOT_REPORTED_IN_SELECTED_BUNDLE` | 해당 없음이라고 추론할 수 없음 |
| SEGR | `NOT_REPORTED_IN_SELECTED_BUNDLE` | 해당 없음이라고 추론할 수 없음 |

TI 제품 페이지에는 별도의 SEE report 링크와 SEL 관련 마케팅 요약이 존재하지만 이번 bundle에서는 그 원문 시험 조건·locator를 정규화하지 않았다. 따라서 SEL·SEU·SEB·SEGR 상태를 변경하지 않는다.

### 23.7 현재 v1 schema와 작은 fixture 제안

현재 `schemas/part-test-evidence.schema.json`은 `component_id`, 단일 `facility`, 정확한 `test_date`, 자유형 bias와 숫자 `temperature_c`를 필수로 요구하고, event별 locator·rights·claim 상태·HDR/LDR subrun·충돌 대안을 표현하지 못한다. 원문은 시험일과 숫자 온도를 보고하지 않고 HDR/LDR facility가 다르므로 schema-valid v1 fixture를 만들려면 값을 발명하거나 정보를 손실해야 한다.

따라서 이번 패키지는 JSON fixture 파일을 만들지 않고 위 표를 **작은 `PART_TEST_EVIDENCE v2` discovery fixture 제안**으로 남긴다. 구현 시 Exit Gate는 다음과 같다.

1. Workstream 10이 통합된 v2 명세를 schema/validator로 구현한다.
2. 승인 BOM component가 없으면 `component_ref=NOT_REPORTED`, identity `PARTIAL_UNRESOLVED`, `used_for_decision=false`가 schema-valid해야 한다.
3. claim locator는 raw manifest의 exact artifact revision/generation/hash와 일치해야 한다.
4. 서로 다른 HDR rate와 최대 조사량·LDR bias 대안은 `CONFLICTING alternatives[]`로 보존돼야 한다.
5. `test_date`, numeric temperature, die revision, revision marker를 임의 기본값으로 채우지 않는다.
6. TID 이외 네 사건 유형은 독립 coverage gap으로 남고 support decision이 `HOLD`여야 한다.

### 23.8 적용성 및 최종 HOLD

이 보고서는 특정 lot/date code와 시험 조건의 관찰 결과다. 임무의 TID material conversion, 누적 dose, dose rate, bias duty cycle, anneal, 온도, 수명, shielding과 manufacturing change를 비교하지 않았다. `QML-V`, `RHA`, report의 pass 문구나 50 krad(Si) 관찰을 임무 보증 또는 비행 적합성으로 바꾸지 않는다.

| blocking code | 사유 | 재개 조건 |
|---|---|---|
| `BOM_MISSING` | 승인 component와 exact identity 비교 불가 | BOM owner가 exact manufacturer/PN/package/grade와 필요 lot/process policy 제공 |
| `DOCUMENT_INTERNAL_CONFLICT` | dose rate, 최대 조사량, LDR bias coverage 표기가 충돌 | TI 정정본·시험 raw log 또는 승인 reviewer의 source resolution |
| `RIGHTS_SNAPSHOT_NOT_ACTIVE` | action별 승인 snapshot 없음 | 권리 책임자의 목적·audience·processor별 승인 |
| `RAW_MANIFEST_REFERENCE_MISSING` | 승인 storage generation과 검증 이력 없음 | Workstream 70 ingest 후 exact reference 생성 |
| `V2_REQUIRED_FIELD_MISSING` | v2 schema/validator 미구현 | Workstream 10 구현 및 fixture 검증 |
| `REVIEW_APPROVAL_MISSING` | 독립 source/identity review 없음 | 승인 reviewer가 exact projection에 서명 |
| `MISSION_ENVIRONMENT_UNAVAILABLE` | 시험–임무 적용성 비교 입력 없음 | Stage 3 환경과 Stage 5 policy 연결 |
| `DESTRUCTIVE_SEE_EVIDENCE_MISSING` | SEL·SEB·SEGR 원문 증거 없음 | 필요 mode별 독립 보고서 ingest; SEU로 대체 금지 |

최종 상태는 `PARTIAL_UNRESOLVED / HOLD`다. 첫 exact-part 원문 경로와 실제 artifact 관찰값은 확보했지만, 이 결과는 지원 판정·부품 추천·비행 적합성 결론이 아니다.

## 24. H04 destructive SEE gap research index

- 상세 문서: [`DESTRUCTIVE_SEE_GAP_RESEARCH.md`](DESTRUCTIVE_SEE_GAP_RESEARCH.md)
- 결론: TI `SLLA381–March 2018`에서 제한된 SEL zero-event 결과를 확인했지만 보고서가 exact suffix `5962L1420901VXC`와 lot/date-code traceability를 직접 기록하지 않아 `PARTIAL_IDENTITY`다.
- exact-part SEL 상태는 `REPORTED_IDENTITY_UNRESOLVED`, nested observation은 `ZERO_EVENTS_WITH_TEST_LIMITS`다. SEB·SEGR은 각각 `NOT_REPORTED_IN_SELECTED_BUNDLE`이며 SEL로 대체하지 않는다.
- 공식 TI·NASA NEPP/GSFC/NTRS/JPL·ESA ESARAD/ESCIES·DLA 공개 검색 범위의 결론은 `NO_EXACT_DESTRUCTIVE_SEE_SOURCE_FOUND_WITHIN_SEARCH_SCOPE`다. 전 세계 자료 부재의 증명이 아니다.
- 승인 BOM, rights snapshot, raw manifest와 mission applicability가 없으므로 최종 decision은 `HOLD`다.
