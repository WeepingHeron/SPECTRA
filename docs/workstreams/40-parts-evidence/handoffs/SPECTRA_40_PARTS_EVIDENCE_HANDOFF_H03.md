# 40 Parts Evidence Handoff H03

## Status

`READY_FOR_REVIEW`

작업 패키지 `40-parts-evidence-first-exact-part-evidence-path-v1`의 source-side exact identity와 TID 원문 locator는 확인했다. 그러나 승인 BOM, action별 권리 snapshot, 승인 storage, `PART_TEST_EVIDENCE v2` validator, 임무 적용성과 독립 review가 없고 보고서 내부 표기가 충돌하므로 decision 상태는 `PARTIAL_UNRESOLVED / HOLD`다. 지원 판정·부품 추천·비행 적합성 결론이 아니다.

## 조사 범위와 소유 파일

- 세션: `40-parts-evidence`
- 기준선: Workstream 40 계약 명세 통합 `4bd1362`, Control Tower 기록 `cf4200d`
- 변경: `docs/workstreams/40-parts-evidence/BRIEF.md`
- 변경: `docs/workstreams/40-parts-evidence/RESEARCH.md`
- 변경: `docs/workstreams/40-parts-evidence/CURRENT.md`
- 공통 schema·계약·루트 문서·다른 Workstream 파일은 수정하지 않았다.
- 실제 PDF는 공식 URL에서 임시 검토했지만 Git·Downloads·프로젝트 storage에 포함하지 않았다.
- commit·push하지 않았다.

## 첫 exact-part 후보

- 제조사: Texas Instruments
- exact orderable PN: `5962L1420901VXC`
- 제품: `SN55HVD233-SP`; 보고서 내 표기 `SN55HVD233-RHA`
- package/grade: CFP, TI `HKX`, 8 pin; Space/QML-V/RHA
- process: `LBC3S`
- die lot: `1634103DFB`
- assembly/test lot 및 date code: `7005041MTT / 1736A`
- die revision: `NOT_REPORTED`
- 승인 BOM component: 없음 → `BOM_MISSING`

위 값은 TI exact-part 페이지와 TID report에서 확인한 source claim이다. BOM-side `EXACT_MATCH`가 아니며 decision identity는 `PARTIAL_UNRESOLVED`다.

## 공식 출처와 권리 상태

- exact-part: <https://www.ti.com/product/SN55HVD233-SP/part-details/5962L1420901VXC>
- product/report index: <https://www.ti.com/product/SN55HVD233-SP>
- TID original: <https://www.ti.com/lit/rr/sllk019/sllk019.pdf>
- TI Terms: <https://www.ti.com/legal/terms-conditions/terms-of-use.html>
- 접근일: 2026-08-20
- report ID: `SLLK019`, February 2018; 별도 revision marker와 실제 test date는 `NOT_REPORTED`

TI Terms의 조건부 plain-text linking 근거로 `LOCATOR`만 조건부 허용으로 제안한다. `FETCH`, `PRIVATE_STORE`, `PROCESS_DOCUMENT_AI`, `PROCESS_VERTEX_AI`, `DISPLAY_INTERNAL`, `DISPLAY_EXTERNAL`, `REDISTRIBUTE`, commercial use는 권리 책임자의 project-specific snapshot 전까지 `UNCONFIRMED`다. 공개 열람 가능성을 저장·재배포·상업 이용 허가로 해석하지 않았다.

## 원문 무결성과 manifest 상태

- HTTP status/MIME: `200`, `application/pdf`
- observed byte size: `3568651`
- observed SHA-256: `623b9d19e3b7aba3e55151c7f73f34f47a48f9b36fde46049d6c8d2c79884fa2`
- header verification timestamp: `2026-08-20T04:33:36Z` — HTTP `Date`; manifest `retrieved_at`으로 사용 금지
- Last-Modified: `Mon, 05 Feb 2018 21:32:33 GMT`
- ETag: `"36740b-5647dcccedf1e"`

이는 임시 취득한 실제 bytes의 관찰값이며 승인 manifest/evidence hash가 아니다. storage generation, rights snapshot, scan/review/parser/retention 이력이 없어 `RAW_ARTIFACT_MANIFEST v2` 인스턴스는 만들지 않았다. 종료 코드는 `RAW_MANIFEST_REFERENCE_MISSING`, `RIGHTS_SNAPSHOT_NOT_ACTIVE`, `APPROVED_STORAGE_UNAVAILABLE`이다.

## TID 원문 locator와 내부 충돌

- p.1 title/abstract: exact PN과 report identity, 50 krad(Si) LDR/HDR within-spec 요약
- p.2 §1.2 Table 1: exact identity, package, process, lot/date code, quantity, facilities, Co-60 source, dose levels/rates, ambient condition
- p.3 §2.1–2.2: MIL-STD-883 TM 1019.9 Conditions A/D, LDR method
- p.4 §2.2–2.3/Figure 2: HDR facility, biased/unbiased setup, VCC 3.6 V와 bias circuit
- p.5 §2.4 Tables 2–3: HDR/LDR device groups와 dose steps
- p.6 §3.1: result summary와 표/방법 절에 대한 충돌 표기

`CONFLICTING`으로 보존한 항목:

- HDR dose rate: p.2 Table 1 및 p.5 Table 2의 65 rad(Si)/s 대 p.6 §3.1의 100 rad(Si)/s
- maximum irradiated dose: p.2/p.5의 최대 50 krad(Si) 대 p.6의 HDR 75/LDR 100 krad(Si) 열거
- LDR bias coverage: p.5 Table 3의 unbiased-only 대 p.6 §3.1의 biased/unbiased 열거

충돌 해결 전 report-wide dose rate, 최대 조사량과 LDR bias coverage는 decision operand로 사용할 수 없다. 50 krad(Si) within-spec 문구도 75/100 krad 보증이나 임무 적합성으로 승격하지 않는다.

## 사건 유형 분리

- `TID`: locator가 있는 discovery claim 후보이나 `HOLD`
- `SEU`: `NOT_REPORTED_IN_SELECTED_BUNDLE`
- `SEL`: `NOT_REPORTED_IN_SELECTED_BUNDLE`
- `SEB`: `NOT_REPORTED_IN_SELECTED_BUNDLE`
- `SEGR`: `NOT_REPORTED_IN_SELECTED_BUNDLE`

제품 페이지의 SEL 요약이나 별도 SEE report 존재를 선택한 TID bundle의 증거로 사용하지 않았다. 미보고를 미시험·면역·0 event 또는 해당 없음으로 바꾸지 않는다.

## 증거 정규화 초안과 계약 영향

- `RESEARCH.md` §23에 identity, report, rights, artifact, TID subrun, conflict alternatives, independent event coverage와 blocking gap의 field-level v2 discovery fixture를 제안했다.
- 현재 v1 schema는 `component_id`, 실제 `test_date`, 숫자 온도와 단일 facility를 필수로 요구한다. 원문은 시험일·숫자 온도를 보고하지 않고 HDR/LDR facility가 달라 값을 만들지 않고는 schema-valid하게 표현할 수 없다.
- claim locator, action rights, HDR/LDR subrun과 `CONFLICTING alternatives[]`도 v1에서 표현할 수 없어 실제 JSON fixture를 생성하지 않았다.
- Workstream 10은 `NOT_REPORTED` 시험일/온도, 다중 facility/subrun, locator와 conflict 대안을 보존하는 v2 schema/validator를 구현해야 한다.
- Workstream 70은 승인 rights snapshot과 immutable storage generation, malware/MIME/hash 검증, review와 retention 이력을 만들어야 한다.

## 검증 결과

- 공식 PDF 첫 7 physical page의 text와 p.1/p.2/p.5/p.6 render 대조 완료
- HTTP header, byte size, PDF format와 SHA-256 대조 완료
- 깨끗한 `cf4200d` archive:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py` — schema 11, valid 2, invalid 71; exit 0
  - `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py` — 위 schema 재통과, simulation 19; exit 0
- 현재 혼합 작업트리:
  - schema 14, valid 3, invalid 83; exit 0
  - simulation 28; exit 0
- `git diff --check` — exit 0
- 혼합 작업트리 결과는 다른 Workstream의 미통합 변경을 포함하므로 승인 기준선으로 사용하지 않는다.
- 제안한 v2 field map은 schema 미구현 상태이므로 실행 fixture PASS로 표현하지 않는다.

## HOLD와 알려진 한계

- `BOM_MISSING`
- `DOCUMENT_INTERNAL_CONFLICT`
- `RIGHTS_SNAPSHOT_NOT_ACTIVE`
- `RAW_MANIFEST_REFERENCE_MISSING`
- `APPROVED_STORAGE_UNAVAILABLE`
- `V2_REQUIRED_FIELD_MISSING`
- `REVIEW_APPROVAL_MISSING`
- `MISSION_ENVIRONMENT_UNAVAILABLE`
- `DESTRUCTIVE_SEE_EVIDENCE_MISSING`
- `MANUFACTURING_CHANGE_UNKNOWN`

## Control Tower 확인 요청

- exact PN과 p.2/p.5/p.6 locator 및 내부 충돌을 독립 재현해 달라.
- 이 후보를 MVP reference path로 승인할지 검토하되 BOM 채택·지원 판정과 분리해 달라.
- BOM owner에게 exact manufacturer/PN/package/grade와 process/die/lot/date-code policy를 요청해 달라.
- 권리 책임자와 Workstream 70에 action별 권리·storage 승인 경로를 지정해 달라.
- Workstream 10에 v2 discovery fixture가 실제 schema-valid하도록 구현을 요청해 달라.
- Stage 3·5가 임무 적용성과 required destructive SEE mode를 지정한 뒤에만 별도 SEE report ingest를 시작해 달라.
- 독립 검토 전 `VERIFIED`, `INTEGRATED`, Stage 4 완료 또는 루트 체크리스트 수정을 하지 말아 달라.
