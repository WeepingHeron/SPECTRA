# 40 Parts Evidence Handoff

## Status

`VERIFIED — H11 published source package / SOURCE_READY_COMPARISON_BLOCKED / HOLD`

## H11 published source package — 2026-08-25

- 실제 외부 PDF `33,130,232` bytes의 SHA-256을 검토된 artifact identity와 직접 결속하고, DOI·공식 JLU host·고정 record/artifact URL·CC BY 4.0·attribution/action 조건을 production source gate에서 재검증한다.
- raw PDF는 Git 밖에 두고 candidate manifest와 reviewed anchor, identity-free receipt만 저장소에 둔다. candidate와 anchor를 함께 바꾸는 재결속도 코드에 고정된 reviewed identity와 달라지면 차단한다.
- package composer가 source receipt와 H10 comparison receipt의 artifact hash를 다시 대조한다. 현재 source manifest/rights blocker 2개만 해소되고 exact identity·package·lot/die·mission·TID/destructive SEE blocker는 남는다.
- 실제 결과: `VALID / READY_FOR_REFERENCE_REVIEW`; package 결과: `VALID / SOURCE_READY_COMPARISON_BLOCKED / NOT_COMPARABLE / HOLD`.
- source/package 17개와 기존 comparison/evidence 22개, 총 39개 인접 테스트가 통과했다. 상세 범위와 권리 조건은 `PUBLISHED_SOURCE_PACKAGE_H11.md`에 기록했다.
- CC BY 검토는 저작권·유사권 범위이며 특허·상표·privacy, 과학 정확성, exact-part applicability와 법률 자문을 대신하지 않는다. actual EvidencePacket은 계속 0건이다.

## H10 published-reference comparison gate — 2026-08-25

- 공개 시험값과 현재 합성 입력의 비율을 production adapter가 직접 재계산하고, identity·package·lot/die·source manifest·단위·합성 조건·mission/destructive coverage blocker를 stable code로 다시 만든다.
- 현재 23LC reference는 `VALID / NOT_COMPARABLE / HOLD`; 약 `243.9×`는 `CALCULATED_REFERENCE_ONLY`이며 decision과 direct validation에는 사용하지 않는다.
- blocker 삭제, ratio 1 ULP 변조, optimistic PASS/direct validation, boolean·0·음수·NaN·Infinity, 단위·identity·hash·금지 필드 공격을 fail-closed 처리한다.
- H10 gate 10개와 기존 reference binding 5개, 총 15개 직접 테스트가 통과했다. 상세 계약과 경계는 `PUBLISHED_REFERENCE_COMPARISON_GATE_H10.md`에 기록했다.
- exact suffix/package/lot/die, 승인 raw manifest와 rights, mission applicability, TID 및 필요한 SEE coverage는 여전히 불완전하다. 실제 Evidence Packet은 0건이고 이 데이터 공백은 발표·직접 검증 신뢰도 리스크로 유지한다.
- 사용자 요청에 따른 다음 통합 시점에서 전체 회귀를 통과해 누적 integration unit의 commit·push 대상에 포함했다.

## H08 approved COTS BOM review target — 2026-08-25

- 발표의 COTS SRAM 범위에 맞춰 사용자가 기존 Space/QML-V/RHA TI CAN transceiver 선택을 철회하고 `Microchip Technology 23LC1024-I/SN`을 `SPECTRA_MVP_EXACT_PART_REVIEW_TARGET` 범위로 승인했다.
- Microchip 제품 페이지와 datasheet에서 현재 양산, 1 Mbit volatile SPI/SDI/SQI SRAM, industrial temperature, 8-lead SOIC exact catalog identity를 확인했다.
- ESA는 base product `23LC1024`가 GOMX-4B CubeSat의 CHIMERA COTS memory radiation experiment에 탑재되어 SEU·MBU·SEFI·latch-up을 관측한다고 밝힌다. BOM function은 이 실제 역할에 맞춰 `COTS_SPI_SRAM_RADIATION_EXPERIMENT_TARGET`으로 고정했다.
- ESA 페이지는 비행 exact suffix·lot/date code·die revision과 결과 artifact를 공개하지 않으므로 catalog exact identity와 flight-experiment family identity를 합치지 않는다.
- BOM component 계약에서 구매 수량을 제거했다. exact-part 승인·차폐·TID·per-device SEE evidence에는 수량을 쓰지 않는다.
- 총 SEE event 계산에만 별도 simulation input `analysis_device_count`를 사용한다. 이 값은 TID/차폐 결과에 영향을 주지 않으며 0·음수·소수·boolean은 `INVALID_INPUT / HOLD`다.
- 상세 결정과 source locator: `APPROVED_BOM_TARGET_H08.md`.
- 승인 대상 고정은 catalog comparison blocker만 닫는다. rights/raw manifest, exact test lot, event coverage, mission applicability와 independent packet review가 남아 assurance는 `HOLD`다.
- `23LC1024` PDIP의 공개 Am-Be neutron screening에서 SEU cross section `(4.10 ± 0.04) × 10^-9 cm²/device`를 확인해 reference comparison을 추가했다. 승인 `/I/SN`은 SOIC이고 공개 시험 suffix·lot·die가 없어 `PARTIAL_UNRESOLVED`; 현재 합성 `1.0 × 10^-6`과의 약 `243.9×`는 입력 수치 비교일 뿐 정확도·검증·적합성 지표가 아니다. 상태는 `REFERENCE_COMPARISON_AVAILABLE / NOT_COMPARABLE / HOLD`다.
- CHIMERA의 다른 세 COTS memory와 공개 radiation database를 재검색했지만 flight identity와 numerical test article을 함께 묶는 더 강한 exact memory 사례는 찾지 못했다. 더 넓은 COTS 사례로는 Φsat-1에서 실제 AI 처리를 수행하고 Co-60·proton·heavy-ion 시험이 발표된 Intel Movidius `Myriad 2`가 있으나, 복합 AI SoC라 현재 SRAM 모델의 대체품으로 사용하지 않는다. 조사 기록은 `COTS_FLIGHT_TEST_DATA_RECHECK_H09.md`에 보존했다.
- COTS candidate library, Product presentation binding, Evidence Console 35개와 published-reference comparison 5개, 합계 직접 테스트 40개 및 `git diff --check`가 통과했다. 브라우저 시각 재점검은 사용자의 UI 재검토 시점까지 보류했다.

H06 executable gate에서 재현된 embedded-NUL `relative_path` 예외 유출을 수정했다. 경로 resolve와 artifact stat/read의 예상 가능한 파일시스템 실패는 안정적인 provenance code로 `HOLD` 처리하며, 프로그래밍 오류는 숨기지 않는다. H08에서 catalog-level 승인 검토 대상 1개를 고정했지만 실제 decision-usable packet은 여전히 0건이다.

## H07 artifact path fail-closed remediation — 2026-08-24

- `relative_path`의 NUL이 시작·중간·끝에 있을 때 `Path.resolve()`의 `ValueError`가 밖으로 새지 않고 `ARTIFACT_PATH_INVALID`로 닫힌다.
- resolve/stat/read 단계의 `OSError` 계열 접근 실패는 `ARTIFACT_ACCESS_ERROR`로 닫힌다. 누락 파일과 비정규 파일, read 시점의 삭제는 기존 artifact 무결성 의미에 맞춰 `ARTIFACT_HASH_MISMATCH`로 닫힌다.
- catch 범위는 `ValueError`와 `OSError`로 제한했다. 합성 `RuntimeError` 공격은 그대로 전파되어 프로그래밍 결함을 fail-closed 입력 오류처럼 숨기지 않음을 확인한다.
- 공격 fixture는 NUL prefix/middle/suffix와 missing file 4건을 추가해 총 25건이다. 별도 filesystem 공격은 resolve/stat/read `PermissionError` 3건과 unexpected `RuntimeError` 1건이다.
- 직접 검증: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.parts_evidence.test_evidence_gate` — 7 unittest methods, `OK`.
- Control Tower가 NUL prefix/middle/suffix와 파일 접근 실패를 직접 재현했고 7 tests가 통과했다. 공통 schema·runtime은 변경하지 않았으며 실제 packet과 승인 BOM 0건, `HOLD`를 유지한다.

## 이전 제출 상태 — H06 executable exact-part evidence gate

`READY_FOR_REVIEW — H06 executable exact-part evidence gate / HOLD`

H05 field map을 Workstream 40 전용 executable test contract로 전환했다. synthetic control 1개, 21 attack cases와 H05 discovery candidate를 직접 검증했으며 모든 경로가 `HOLD`, `used_for_decision=false`, recommendation 없음으로 닫힌다. 이 구현은 production `PART_TEST_EVIDENCE v2`가 아니다.

## H06 executable exact-part evidence gate — 2026-08-24

- 신규 test-only module: `tests/parts_evidence/evidence_gate.py`; 공통 schema/validator/runtime에서 import하지 않는다.
- 신규 fixtures: structure-valid synthetic control, 작은 synthetic text artifact, H05 discovery candidate, 21 executable attack cases.
- claim states `VERIFIED/NOT_REPORTED/CONFLICTING`, identity `PARTIAL_UNRESOLVED/FAMILY_ONLY/CONTRADICTED/EXACT_MATCH`의 의미를 분리했다. 실제 승인 BOM이 없는 fixture는 `EXACT_MATCH`에 도달하지 않는다.
- BOM approval version/component pointer/target hash/history, source locator, artifact identity, action rights, review hash chain, five event coverage, applicability와 decision-use를 독립 검증한다.
- synthetic hashes는 실제 작은 fixture bytes와 canonical synthetic projection에서 실행 시 계산한다. 실제 PDF hash, 승인자, 시험 수치·lot/date code를 만들지 않았다.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.parts_evidence.test_evidence_gate` — 5 unittest methods, 26 scenario checks, 21 attacks; 최종 `OK`.
- 첫 실행에서 out-of-range case가 code/HOLD에도 `APPLICABLE`을 유지한 결함을 검출했고 `NOT_APPLICABLE` 강등으로 수정 후 재통과했다.
- H05 candidate actual: `PROVENANCE_FAILURE / PARTIAL_UNRESOLVED / NOT_EVALUATED / HOLD`, decision false; BOM approval, rights, raw manifest, review, SEU·SEB·SEGR과 exact SEL identity gap 유지.
- 상세 계약·상태 전이·attack actual: `docs/workstreams/40-parts-evidence/EXECUTABLE_EXACT_PART_GATE_H06.md`.
- 실제 packet은 0건이며 production v2, Stage 4 완료, 추천·suitability를 주장하지 않는다.
- 남은 `CONTRACT_CHANGE_REQUEST`: Workstream 10/Control Tower의 versioned v2 schema/semantic gate, BOM approval projection, locator/manifest/rights, event condition과 applicability, migration/rollback.
- 공통 schema·engine, 다른 Workstream, Product와 루트 문서를 수정하지 않는다. commit·push하지 않는다.

## 이전 검증 상태 — H05 scoped assessment

`VERIFIED — H05 scoped assessment only / BOM_APPROVAL_MISSING / HOLD`

승인 BOM과 immutable approval reference가 제공되지 않아 decision-usable packet을 만들지 않았다. TI `5962L1420901VXC`, `SLLK019`, `SLLA381`은 discovery comparison으로만 유지하며 최종 상태는 `BOM_APPROVAL_MISSING / PARTIAL_UNRESOLVED / HOLD`다. H04 문서 패키지의 기존 `INTEGRATED` 판정은 유지한다.

### H05 Control Tower 독립 검토 — 2026-08-24

- 판정: `VERIFIED — approved-BOM 부재 시 발행 불가라는 범위 한정 assessment`; Stage 4 완료나 evidence packet 발행 승인이 아니다.
- 후보 자료를 승인 BOM으로 승격하지 않았고 TID 내부 conflict, SEL의 zero-event 한계, SEB·SEGR 공백, rights·mission applicability 미확인을 각각 독립 gap으로 유지했다.
- 실행 가능한 packet·fixture·validator가 없으므로 Workstream 40 구현 검증은 0건이다. schema 14개·정상 fixture 5개·실패 fixture 116개와 `git diff --check`만 재확인했다.
- 새 승인 BOM identity와 immutable approval reference가 들어오기 전에는 후보 검색을 반복하지 않는다. 입력이 들어오면 동일 exact-part gate에서 새 H06으로 재개한다.

## H05 approved-BOM exact-part evidence packet assessment — 2026-08-24

- 요청 기준 commit `d287d62`는 실제 검사 HEAD `d730ded`의 ancestor다. 현재 `main`/`origin/main`과 clean 시작 작업트리를 확인했고, 기준선 차이를 H05 문서와 handoff에 기록한다.
- repository와 `/Users/taehoon/Downloads`의 좁은 filename/reference 검색에서 승인자·승인 시각·승인 대상 hash/version/history anchor가 연결된 BOM item을 찾지 못했다.
- `schemas/bom.schema.json`은 형식 계약이고 합성 fixture approval/hash는 실제 BOM 또는 rights 승인이 아니다. Git 밖 private BOM/manifest 입력은 제공되지 않았다.
- TI exact-part page, `SLLK019`, `SLLA381`을 승인 BOM item으로 자동 채택하지 않았다. catalog exact PN과 test-article exact suffix/lot identity를 분리했다.
- TID는 `SLLK019` 내부 conflict와 BOM/rights/manifest/applicability gap 때문에 decision-ineligible다. SEL은 `REPORTED_IDENTITY_UNRESOLVED / ZERO_EVENTS_WITH_TEST_LIMITS`, SEU·SEB·SEGR은 독립 `EVIDENCE_MISSING` 상태다.
- Stage 3 environment와 Stage 5 event policy가 제공되지 않아 applicability는 `NOT_EVALUATED`다.
- action rights는 locator 외 `FETCH`, `PRIVATE_STORE`, `PROCESS_LOCAL/AI`, `DISPLAY_INTERNAL/EXTERNAL`, `REDISTRIBUTE`, `COMMERCIAL_USE`가 승인되지 않았다. 실제 PDF를 취득·저장·자동 처리하지 않았다.
- 공통 v1 schema에 맞추려고 test date, numeric temperature, facility, lot, rights, locator 또는 approval을 만들지 않았다. executable packet/fixture를 만들지 않았고 Workstream 40 direct test는 0개다.
- 현재 HEAD 회귀: `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`에서 schema 14, enum 4축, exact-one input 7종, valid 5, invalid 116이 통과했고 `git diff --check`도 통과했다. 이는 v2 구현 검증이 아니다.
- 시작 후 나타난 `src/spectra_env_adapter/**`, `tests/environment/test_issuance_gate.py` 병렬 변경은 수정·의존·stage하지 않았다.
- 상세 assessment와 `CONTRACT_CHANGE_REQUEST`: `docs/workstreams/40-parts-evidence/APPROVED_BOM_EVIDENCE_PACKET_H05.md`.
- 변경 대상은 Workstream 40 문서에 한정하며 공통 schema·validator·consumer·다른 Workstream·루트 문서를 수정하지 않는다.
- 현재 요청 상태 상한은 `READY_FOR_REVIEW`; `VERIFIED`, `INTEGRATED`, Stage 4 완료, 추천·suitability, commit·push를 수행하지 않는다.

## 이전 통합 상태 — H04 destructive SEE gap research

`INTEGRATED — H04 destructive SEE gap research / commit b2c8ef6 / HOLD`

`40-exact-part-destructive-see-gap-research-v1`에서 TI `SLLA381`의 SEL·SEB·SEGR coverage와 exact test-article identity를 조사했다. 제한된 SEL zero-event 결과는 확인했지만 exact suffix와 lot/date-code traceability가 없어 `PARTIAL_IDENTITY`이며, SEB·SEGR은 독립 공백이다. 최종 decision은 `HOLD`다. H03까지의 기존 `INTEGRATED` 판정은 유지한다.

## H04 destructive SEE gap research — 2026-08-20

- 기준 HEAD: `4920b6e`
- 신규 문서: `docs/workstreams/40-parts-evidence/DESTRUCTIVE_SEE_GAP_RESEARCH.md`
- 최소 색인: `docs/workstreams/40-parts-evidence/RESEARCH.md` §24
- 공식 source 범위: TI product/technical/radiation documents, NASA NEPP·GSFC Radiation Data Base·NTRS·JPL, ESA ESARAD·ESCIES/ESCC, DLA SMD.
- TI `SLLA381–March 2018`은 HVD233-SP, SMD base `5962L1420901VX`, LBC3S, 8-pin CFP를 기록하지만 exact `5962L1420901VXC`, grade, die/wafer lot, A/T lot와 date code는 기록하지 않는다. exact identity는 `PARTIAL_IDENTITY`다.
- SEL: `REPORTED_IDENTITY_UNRESOLVED`; nested result `ZERO_EVENTS_WITH_TEST_LIMITS`. 보고서는 Device #1의 7 runs, `59Pr`, 45°, `LETEFF 92.01 MeV-cm²/mg`, 125°C, VCC 3.6 V, combined fluence `7.0 × 10^7`, zero observed SEL과 95% upper bound를 p.7–10/Appendix B에 기록한다.
- 명시적 SEL detection threshold와 post-test electrical/latent-damage 결과는 확인하지 못해 condition completeness는 `PARTIAL`이다. zero events를 immunity·mission suitability로 승격하지 않는다.
- exact TI product page/datasheet의 86 MeV-cm²/mg headline과 `SLLA381`의 `LETEFF 92.01`은 basis가 명시적으로 연결되지 않아 `BASIS_UNRESOLVED`다.
- SEB: `NOT_REPORTED_IN_SELECTED_BUNDLE`. §2 mechanism mention은 test result가 아니다.
- SEGR: `NOT_REPORTED_IN_SELECTED_BUNDLE`. report results/summary와 text search에서 event result를 확인하지 못했다.
- SET는 보고되지만 SEU·SEFI를 닫지 않는다. SEL도 SEB·SEGR을 닫지 않는다.
- 공식 공개 검색 범위 결론: `NO_EXACT_DESTRUCTIVE_SEE_SOURCE_FOUND_WITHIN_SEARCH_SCOPE`. 전 세계 자료 부재를 뜻하지 않는다.
- rights: TI public view와 조건부 locator만 확인했다. fetch/storage/AI processing/display/redistribution/commercial use는 `RIGHTS_UNRESOLVED`; 실제 SEE PDF를 Git·Downloads·project storage에 저장하지 않았다.
- remaining gates: `BOM_MISSING`, `EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED`, `SEL_TEST_COMPLETENESS_PARTIAL`, `SEB_EVIDENCE_MISSING`, `SEGR_EVIDENCE_MISSING`, `RIGHTS_UNRESOLVED`, `MISSION_APPLICABILITY_UNAVAILABLE`, `REVIEW_APPROVAL_MISSING`.
- 자체 검증: H04 source register에 공식 URL·문서 revision/date 또는 `NOT_DISPLAYED`·접근일·locator를 기록했고, `git diff --check`를 통과했다. 문서-only 변경이므로 schema·simulation runtime 회귀 테스트는 실행하지 않았다.
- 공통 schema, fixture, 계산·assurance 코드, 다른 Workstream, demo와 루트 문서를 수정하지 않았다. commit·push·merge하지 않는다.

### H04 Control Tower 통합 판정

- 공식 source의 exact catalog suffix와 base SMD test-article identity를 분리하고, SEL zero-event 제한을 immunity로 승격하지 않으며 SEB·SEGR 공백을 독립 유지한 문서 패키지만 검증했다.
- 실제 PDF, 승인 BOM, rights snapshot, raw manifest와 임무 적용성은 포함하지 않았고 최종 decision은 계속 `HOLD`다.
- H04 문서 패키지는 commit `b2c8ef6`로 `INTEGRATED`했다. Stage 4 실제 evidence Exit Gate 완료를 뜻하지 않는다.

## H03 Control Tower 독립 검증 — 2026-08-20

- TI exact-part 페이지에서 `5962L1420901VXC`, `SN55HVD233-SP`, Space/QML-V/RHA, CFP `HKX` 8 pin을 재확인했다.
- 공식 `SLLK019` PDF에서 exact PN, `LBC3S`, die lot `1634103DFB`, A/T lot/date code `7005041MTT/1736A`, HDR/LDR facility와 시험 조건을 재확인했다.
- 임시로 다시 받은 공식 PDF는 `3,568,651` bytes, PDF 1.4, SHA-256 `623b9d19e3b7aba3e55151c7f73f34f47a48f9b36fde46049d6c8d2c79884fa2`로 handoff와 일치했다. 검증 후 임시 파일을 삭제했다.
- Table 1·2의 HDR `65 rad(Si)/s`, 최대 `50 krad(Si)`, LDR unbiased 표기와 §3.1의 HDR `100 rad(Si)/s`, `75/100 krad(Si)`, LDR biased/unbiased 열거가 실제로 충돌함을 재현했다.
- TI 약관은 조건부 plain-text link를 허용하지만 자동 수집을 금지하고 비상업·개인 사용 외 복제·표시·배포를 일반 허용하지 않는다. 따라서 locator 외 action을 `UNCONFIRMED`로 둔 권리 판정은 안전하다.
- 이 패키지는 **실제 source discovery와 locator 검증**에 한해 `VERIFIED`다. 승인 BOM 비교, rights snapshot, raw manifest, schema-valid v2 fixture, 임무 적용성, SEE coverage가 없으므로 MVP의 exact-part evidence Exit Gate와 Stage 4는 미완료다.

## 현재 패키지 조사 범위와 소유 파일

- 세션 ID: `40-parts-evidence`
- 현재 패키지: `40-parts-evidence-first-exact-part-evidence-path-v1`
- 기준선: Workstream 40 계약 명세 통합 commit `4bd1362`와 Control Tower 기록 commit `cf4200d`
- 변경: `docs/workstreams/40-parts-evidence/BRIEF.md`, `RESEARCH.md`, `CURRENT.md`
- 공통 schema·계약·루트 문서·다른 Workstream 파일은 수정하지 않음
- 실제 PDF는 공식 URL에서 임시 검토했지만 Git·Downloads·프로젝트 storage에 넣지 않음
- 현재 혼합 작업트리의 사용자·다른 Workstream 변경은 보존했으며 stage·commit·push하지 않음

## 현재 패키지 공식 출처와 권리 상태

- 선택 후보: Texas Instruments exact PN `5962L1420901VXC` (`SN55HVD233-SP`), Space/QML-V/RHA, CFP `HKX` 8 pin.
- 원문: TI `SLLK019`, February 2018 TID report. exact PN, process `LBC3S`, die lot `1634103DFB`, A/T lot/date code `7005041MTT/1736A`와 TID 조건을 page/table locator로 확인했다.
- 공식 URL, 접근일, 문서 ID, 페이지·절·표 locator와 action별 권리 상태는 `RESEARCH.md` §23에 기록했다.
- TI 약관의 조건부 plain-text linking을 근거로 `LOCATOR`만 조건부 허용으로 제안했다. fetch·private storage·AI processing·내외부 표시·재배포·상업 이용은 권리 책임자 승인 전 `UNCONFIRMED`다.
- 실제 관찰 artifact는 HTTP `application/pdf`, 3,568,651 bytes, SHA-256 `623b9d19e3b7aba3e55151c7f73f34f47a48f9b36fde46049d6c8d2c79884fa2`다. 승인 manifest/hash로 승격하지 않는다.

## 현재 패키지 부품 식별·적용성 규칙

- exact PN은 TI exact-part 페이지와 SLLK019 p.1/p.2 Table 1에서 교차 확인됐다. 이는 `VERIFIED_SOURCE_CLAIM`이지 BOM `EXACT_MATCH`가 아니다.
- 승인 component가 없으므로 decision identity는 `PARTIAL_UNRESOLVED / BOM_MISSING`이다. die revision과 실제 test date도 `NOT_REPORTED`다.
- 보고서 p.2/p.5와 p.6 사이의 HDR dose rate, 최대 조사량, LDR bias coverage 충돌을 `CONFLICTING alternatives[]`와 locator로 보존했다.
- 임무의 TID material/dose/dose rate/bias/anneal/temperature/lifetime/shielding 입력이 없어 applicability는 `NOT_EVALUATED`다.

## 현재 패키지 증거 정규화 초안과 영향

- 선택 bundle은 `TID` 하나다. report identity, exact part/lot/date code, facility, source, dose rate, bias, temperature, sample 수, within-spec dose와 locator를 field-level v2 discovery fixture로 제안했다.
- SLLK019의 50 krad(Si) within-spec 문구는 기록하되 지원 등급이나 75/100 krad 보증으로 승격하지 않는다.
- SEU·SEL·SEB·SEGR은 각각 `NOT_REPORTED_IN_SELECTED_BUNDLE`이다. 제품 페이지의 SEL 요약이나 별도 SEE report 존재를 이 TID bundle의 증거로 사용하지 않았다.
- 현재 v1 schema는 실제 test date, 숫자 온도와 단일 facility를 필수로 요구하며 claim locator·rights·subrun·conflict를 표현하지 못한다. 값을 발명하지 않기 위해 JSON fixture를 만들지 않고 v2 구현용 작은 field map만 제안했다.
- raw manifest v2도 승인 storage generation, rights snapshot, malware/review/parser 이력이 없어 만들지 않았다. 실제 artifact 관찰값은 향후 ingest 시 재검증 입력일 뿐이다.

## 현재 패키지 검증 결과

- 공식 PDF 첫 7 physical page의 text와 p.1/p.2/p.5/p.6 render를 대조해 title, exact PN, Table 1–3, §2 시험 조건과 §3.1 충돌을 확인했다.
- HTTP header, byte size, detected PDF format와 SHA-256을 실제 bytes에서 대조했다.
- 깨끗한 통합 기준선 `cf4200d` archive: `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py` — schema 11개, 정상 fixture 2개, 실패 fixture 71개 통과; exit 0.
- 같은 깨끗한 기준선: `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py` — schema 회귀 재통과 및 simulation test 19개 통과; exit 0.
- 현재 혼합 작업트리: schema 14개, 정상 fixture 3개, 실패 fixture 83개와 simulation test 28개 통과; 두 명령 모두 exit 0. 다른 Workstream의 미통합 변경을 포함하므로 이 수치는 기준선 승인 근거로 사용하지 않는다.
- `git diff --check` — 통과.
- 이번 field map은 v2 schema가 아직 구현되지 않아 실행 가능한 fixture PASS로 표현하지 않는다.

## 현재 패키지 실제 데이터 사용 여부

- 실제 exact part 후보 1개와 TID 보고서의 locator 확인값을 사용했다. BOM 채택·support 판단은 하지 않았다.
- 실제 PDF는 공식 URL에서 임시 검토했지만 프로젝트·handoff에 포함하지 않았다.
- 실제 artifact hash를 계산했지만 승인 manifest/evidence content hash로 승격하지 않았다.
- 가짜 hash·locator·수치, 임의 confidence·통계 경계·보증 등급, 고객 자료는 만들거나 사용하지 않았다.

## 현재 패키지 HOLD와 알려진 한계

- `BOM_MISSING`: 승인 component와 exact identity 비교 불가
- `DOCUMENT_INTERNAL_CONFLICT`: HDR dose rate, 최대 조사량, LDR bias coverage 표기가 충돌
- `RIGHTS_SNAPSHOT_NOT_ACTIVE`: 공개 locator 외 action의 프로젝트 이용 권한 미승인
- `RAW_MANIFEST_REFERENCE_MISSING` / `APPROVED_STORAGE_UNAVAILABLE`: exact generation·scan·review·retention 이력 없음
- `V2_REQUIRED_FIELD_MISSING`: 제안한 discovery fixture용 공통 schema/validator 미구현
- `REVIEW_APPROVAL_MISSING`: source·identity·conflict resolution 독립 검토 없음
- `MISSION_ENVIRONMENT_UNAVAILABLE`: TID 시험–임무 적용성 비교 미수행
- `DESTRUCTIVE_SEE_EVIDENCE_MISSING`: SEL·SEB·SEGR 독립 증거 없음; SEU도 선택 bundle에서 미보고
- 이 결과는 법률 자문, 부품 추천, 인증 또는 비행 적합성 결론이 아니다.

## 현재 패키지 Control Tower 확인 요청

- 후보 `5962L1420901VXC`의 MVP reference path 적합성과 SLLK019 내부 충돌을 독립 재현해 달라.
- Workstream 10에 `NOT_REPORTED` 시험일/숫자 온도, 다중 facility/subrun, locator와 conflict alternatives를 보존하는 v2 schema 구현을 요청해 달라.
- Workstream 70과 권리 책임자에게 action별 rights snapshot, 승인 storage generation, malware/hash/MIME 검증과 retention을 요청해 달라.
- BOM owner에게 exact manufacturer/PN/package/grade와 required process/die/lot/date-code policy를 요청해 달라.
- Stage 3·5가 임무 적용성과 필요한 destructive SEE mode를 지정한 뒤에만 별도 SEE report ingest를 시작해 달라.
- 독립 검토 전 `VERIFIED`, `INTEGRATED`, Stage 4 완료 또는 루트 체크리스트 `[x]`로 변경하지 말아 달라.

## 이전 계약 패키지 — 조사 범위와 소유 파일

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

## 이전 계약 패키지 — 공식 출처와 권리 상태

- NASA GSFC Radiation Data Base: GSFC 부품 시험 보고서의 직접 discovery 경로. 현재 NEPP 임시 호스팅이며 문서별 copyright/third-party 표시를 확인해야 한다.
- NASA NEPP/NTRS: 시험·보증 방법과 NASA 문서 식별 경로. NTRS OpenAPI·bulk metadata 경로와 NASA STI 이용 조건을 확인했다.
- ESA ESARAD: ESA/계약 파트너 SEE·TID·DD 공개 색인. 보고서 다운로드 로그인, traceability·최신본 비보증, 요약 재현 조건을 확인했다.
- ESCIES/ESCC: TID 22900, SEE 25100 방법론 참고. 부품 시험 결과를 대신하지 않는다.
- 제조사: 제품별 report·datasheet·SMD/VID·PCN을 제공할 수 있으나 TI, Microchip, AMD, Infineon의 약관과 제한 범위가 다르다. 공개 열람을 재배포 허가로 보지 않는다.
- 고객 자료: 권한·격리·목적·보존·삭제·LLM 처리 승인이 없으므로 수집하지 않았다.
- 권리 상태는 문서별 `access_status`, `rights_status`, `allowed_actions`, terms URL과 원문 위치로 다시 확인하도록 설계했다.

## 이전 계약 패키지 — 부품 식별·적용성 규칙

- 실제 후보는 승인된 BOM의 `manufacturer + exact orderable part number`에서만 시작한다.
- package/grade/process/die/lot/date code의 누락은 `PARTIAL_UNRESOLVED`, 확인된 모순은 `CONTRADICTED`, generic/family 일치는 `FAMILY_ONLY`다.
- 누락과 모순을 모두 exact match로 만들지 않는다. 유사 부품은 추가 조사 후보일 뿐 지원 근거가 아니다.
- 시험과 임무의 TID material/dose/dose rate/bias/anneal/temperature, SEE particle/energy/LET/range/angle, 전압/mode/온도, sample/lot/statistical basis, report revision/PCN을 항목별 비교한다.
- 한 항목이라도 차단형이면 전체 trace를 `APPLICABLE`로 만들지 않는다.
- BOM 부재는 `BOM_MISSING`; 실제 부품 선정과 ingest는 `HOLD`다.

## 이전 계약 패키지 — 증거 정규화 초안과 영향

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

## 이전 계약 패키지 — 검증 결과

- H02 깨끗한 `375763c` snapshot에서 `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 통과; exit 0
- 같은 snapshot에서 `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py` — 위 schema 검증 재통과 및 simulation test 19개 통과; exit 0
- H02 현재 작업트리에서 동일 명령 재실행 — 병렬 Workstream 변경을 포함한 schema 11개, 정상 fixture 2개, 실패 fixture 47개와 simulation test 19개 통과; 모두 exit 0
- `git diff --check` — 통과
- 위 검증은 기존 v1 계약·합성 simulation 회귀 결과다. 이번 문서에서 명세한 v2 schema와 공격 fixture는 아직 Workstream 10·60이 구현하지 않았으므로 실행 검증 완료로 표시하지 않는다.
- 검증 시 작업트리에 다른 Workstream의 미통합 공통 schema 변경이 존재했다. 테스트 통과 사실은 기록하되, 그 변경을 이번 패키지의 기준선이나 승인 근거로 사용하지 않는다.

## 이전 계약 패키지 — 실제 데이터 사용 여부

- 실제 시험 수치: 사용하지 않음
- 실제 부품 후보 5~10종: 선정하지 않음
- 실제 시험 PDF: 다운로드·저장하지 않음
- 실제 artifact hash·locator: 생성하지 않음
- 임의 confidence·통계 경계·보증 등급: 생성하지 않음
- 고객 문서/BOM: 접근·수집하지 않음
- `PUBLISHED`, `CUSTOMER_VERIFIED`, 실제 `CALCULATED` EvidencePacket: 생성하지 않음
- 조사에는 공식 웹페이지와 문서의 존재·필드·이용 조건만 사용했다.

## 이전 계약 패키지 — HOLD와 알려진 한계

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

## 이전 계약 패키지 — Control Tower 확인 요청

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
- 다음 handoff는 기존 번호 없는 제출을 암묵적 `H01`로 보고 `docs/workstreams/40-parts-evidence/handoffs/SPECTRA_40_PARTS_EVIDENCE_HANDOFF_H02.md`로 작성한다.
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


## Git 통합 — 2026-08-20

- 브랜치: `main`
- commit: `4bd1362` — `feat(contracts): integrate verified provenance and evidence contracts`
- 원격: 비공개 `origin/main` push 완료
- 포함 범위: Workstream 10 H01~H04 누적 provenance/operand/exact-one 계약과 Workstream 40의 검증된 PART_TEST_EVIDENCE v2 문서 명세
- 제외 범위: Workstream 50의 미검증 계약 설계, 실제 Stage 3·4 데이터·원문·모델 실행
