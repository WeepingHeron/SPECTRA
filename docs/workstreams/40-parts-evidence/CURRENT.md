# 40 Parts Evidence Handoff

## Status

`INTEGRATED`

이 상태는 `40-parts-evidence-source-rights-identity-applicability-v1` 조사·설계 패키지의 검증·Git 통합에만 적용한다. Stage 4의 실제 부품 5~10종 수집·정규화·지원 판정이 완료됐다는 뜻이 아니다. 실제 BOM과 권리 확인 원문이 없으므로 실제 부품 evidence ingest와 assurance decision은 계속 `HOLD`다.

## 조사 범위와 소유 파일

- 세션 ID: `40-parts-evidence`
- 기준선: `INTEGRATED` Stage 1 EvidencePacket 계약
- 읽기 전용 확인: 루트 개요·로드맵·체크리스트, Control Tower, Contracts & Schema, Stage 1 계약, 통합된 Workstream 20 기준선과 Workstream 30 조사 계약
- 생성: `docs/workstreams/40-parts-evidence/BRIEF.md`
- 생성: `docs/workstreams/40-parts-evidence/RESEARCH.md`
- 생성: `docs/workstreams/40-parts-evidence/CURRENT.md`
- 공통 schema, 계약, 루트 문서, 다른 Workstream 파일은 수정하지 않음
- 작업 채팅 제출 당시에는 commit·push하지 않았으며, 이후 Control Tower가 독립 검증과 통합을 담당했다.

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

- TID, SEU, SEL, SEB, SEGR을 독립 event record로 분리했다.
- TID의 시험 도달량과 규격 내 확인량, dose rate·bias·anneal을 분리한다.
- SEU는 curve point, particle/LET/energy, event count, fluence, bit/device denominator와 fit을 기록한다.
- SEL은 current threshold/limit/recovery/latent damage, SEB·SEGR은 power bias와 safe operating boundary·failure criterion을 각각 기록한다.
- `no event observed`는 면역이 아니며 조건·fluence·sample·통계 경계가 없으면 `HOLD`다.
- Stage 3에는 spectrum/LET/energy와 TID material contract, Stage 5에는 개별 destructive failure mode 정책, Stage 6에는 identity·event substitution·range extrapolation 공격 fixture, Stage 7에는 rights-gated 격리 저장·IAM/KMS·hash/audit 경로가 필요하다.
- 공통 schema에는 identity 확장, 구조화된 rights, artifact/record hash 분리, claim locator, event별 results, review history, structured applicability가 필요하다. Workstream 10 검토 전 수정하지 않았다.

## 실제 데이터 사용 여부

- 실제 시험 수치: 사용하지 않음
- 실제 부품 후보 5~10종: 선정하지 않음
- 실제 시험 PDF: 다운로드·저장하지 않음
- 고객 문서/BOM: 접근·수집하지 않음
- `PUBLISHED`, `CUSTOMER_VERIFIED`, 실제 `CALCULATED` EvidencePacket: 생성하지 않음
- 조사에는 공식 웹페이지와 문서의 존재·필드·이용 조건만 사용했다.

## HOLD와 알려진 한계

- `BOM_MISSING`: 실제 부품 후보 선정 불가
- `RIGHTS_UNRESOLVED`: GSFC/NEPP·ESA·제조사 개별 원문의 저장·추출·재배포 권리를 문서별로 아직 확인하지 않음
- `ORIGINAL_UNAVAILABLE`: ESARAD 일부 보고서는 로그인 없이 원문 확인 불가
- `MANUFACTURING_CHANGE_UNKNOWN`: 실제 후보가 없어 PCN/process/die/lot/date code 비교 미수행
- `MISSION_ENVIRONMENT_UNAVAILABLE`: Stage 3의 SEE spectrum/LET 경로가 없어 적용성 계산 미수행
- ESARAD 기여 안내의 public/internal 문구가 반대로 보이는 모순은 ESA 확인 전 운영 규칙으로 사용하지 않음
- 이 조사 결과는 법률 자문, 부품 인증, 비행 적합성 결론이 아니다.

## Control Tower 확인 요청

- `RESEARCH.md`의 출처·권리 분류가 프로젝트의 공개 데모와 향후 상업 이용 범위를 충분히 차단하는지 검토해 달라.
- 실제 후보 선정을 시작할 승인 BOM과 최소 identity 필드의 owner를 지정해 달라.
- Workstream 10에 `PART_TEST_EVIDENCE v2` 또는 additive schema 확장 검토를 요청해 달라.
- 누락 identity를 mismatch와 구분하는 의미 gate 변경이 기존 False PASS 방어를 약화하지 않는지 검토해 달라.
- Workstream 30·50·60·70에 각각 환경 인터페이스, mode별 정책, 공격 fixture, rights-gated storage 계약 확인을 요청해 달라.
- 실제 원문 수집 전 권리 검토 책임자와 승인 가능한 storage를 지정해 달라.
- 독립 검토 전 `VERIFIED`, `INTEGRATED`, Stage 4 완료 또는 루트 체크리스트 `[x]`로 변경하지 말아 달라.

## Control Tower 독립 검증 — 2026-08-19

- 판정: `INTEGRATED` — **출처·권리·identity·적용성 조사·설계 패키지**만 검증·통합했다. Stage 4 실제 증거 경로 완료 판정이 아니다.
- 공식 출처: NASA·ESA·ESCIES·제조사 공식 URL 16개의 접근 상태를 확인하고, NASA GSFC DB·NASA STI/NTRS·ESARAD·ESA copyright·ESCC 22900/25100의 핵심 주장을 원문에서 재현했다.
- 방법론 대조: NASA NEPP 자료에서 lot/date code·technology·process·bias·application 조건과 lot별 변동 위험을 확인했고, ESCC 22900/25100에서 TID와 SEE의 독립 시험 조건·단위·보고 필드를 확인했다.
- 계약 대조: 현재 identity 의미 검증, 단일 `content_hash`, 자유형 rights, 단일 `cross_section`, 제한된 `test_conditions`, 문자열 applicability와 destructive SEE boolean의 확장 필요성이 실제 Stage 1 schema와 일치한다.
- 재실행: `python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 통과.
- False PASS 검토: BOM 부재, family-only·부분 식별·모순, 사건 유형 대체, zero-event 면역 승격, 권리·hash·locator·review 누락을 모두 지원 근거에서 제외한다.
- 데이터 분류: 실제 BOM·부품 후보·시험 수치·시험 PDF·고객 자료·실제 EvidencePacket은 모두 0건이다.
- 제한: Microchip 약관은 이번 자동 접근에서 403으로 원문 재확인하지 못했다. 문서가 해당 권리를 `RIGHTS_UNRESOLVED`로 유지하므로 운영 허가 근거로 사용하지 않는다.

## Git 통합

- 브랜치: `main`
- 검증된 통합 commit: `ed4e0f8` — `docs(parts): integrate verified Stage 4 evidence research`
- 원격: `origin` (`https://github.com/WeepingHeron/SPECTRA.git`), push 완료
- 제외: 사용자 소유의 미추적 `.obsidian/`
