# 80 Product & Dashboard — Current

## 상태

`VERIFIED — H42 Public Console; actual evidence and assurance remain HOLD`

## H42 Final Public Console QA — 2026-08-25

- Slide 08 제목을 `세 역할이 한 가지 실행의 근거를 나눠 검증한다.`로 확정해 세 역할이 서로 다른 실행을 만들거나 같은 계산을 세 번 한다는 오해를 줄였다.
- Evidence Console 오른쪽 결과 영역을 `항목별 검사 결과` 카드로 재구성했다. 각 카드는 `확인 완료 · 불일치 · 추가 입력 필요`, 확인 대상, 세부 설명, 책임 역할을 분리하며 1280×720에서는 문서 전체가 아니라 요약 panel만 독립 스크롤한다.
- 공개 revision `spectra-demo-console-00006-6mh`에서 합성 PDF를 실행해 `확인 2 · 불일치 0 · 추가 입력 1`, body `1280×720` overflow 0과 카드 3개를 확인했다.
- 공개 메뉴의 실행 경계를 재확인했다. 문서 검사는 live Cloud Run parser, 3개 입력 연결은 고정 합성 입력의 production Core live 실행, 공격 검증은 저장 snapshot, 전체 문서 결과는 공개 GCP catalog live read다.
- 전체 자동 회귀는 unit 415개와 Assurance 공격 실행 47개가 통과했다. 실제 방사선 assurance는 계속 `HOLD`다.

## H41 Cloud Console Readability & Public Runtime — 2026-08-25

- 네 메뉴를 2×2로 재배치하고, 결과 상단에 `확인 완료 · 불일치 · 추가 입력` 세 집계를 큰 숫자로 분리했다. event 본문·근거·상태 글자와 전체 문서 표의 행간·열 폭을 확대하고 파일명 표시는 숫자 prefix와 underscore를 제거했다.
- 동일 HTML이 hostname을 감지해 로컬과 Cloud Run 안내를 구분한다. Cloud Run에서는 파일이 GCP 인스턴스로 전송되고 임시 처리 후 삭제되며 GCS에는 저장되지 않는다는 문구를 입력 권리 확인 바로 아래 표시한다.
- 공개 URL에서 합성 PDF를 실제 실행해 `14 events · 확인 2 · 불일치 0 · 추가 입력 1`, Mission Case 5/5 근거 연결, 저장 공격의 hash/endpoint 차단, GCP 공개 문서 15건과 감사로그 영수증을 브라우저에서 재현했다.
- 변경 범위 Product 테스트 35개와 `git diff --check`가 통과했다. 이는 UI·결정론적 합성 동작·저장 snapshot 표시에 대한 검증이며 실제 방사선 assurance는 아니다.

## H40 Partial Evaluation Continuation — 2026-08-25

- 최종 fail-closed와 조기 계산 중단을 분리했다. 필수 입력 일부가 누락돼도 원문 span에 결속된 수치는 Agent별로 구조·단위·도메인 최소/최대·범위 순서·정수 조건을 계속 검사한다.
- `PARTIAL_EVALUATION_LEDGER_1.0.0`은 각 항목을 `VALIDATED · FAILED · NOT_EVALUATED`로 분리하고, claim boundary를 `STRUCTURE_UNIT_AND_DOMAIN_ONLY`로 제한한다. 시험값 진위·부품 rating·임무 적합성은 별도 근거 없이 승격하지 않는다.
- Local Console의 `agent_role`은 책임 범위를 보여주는 메타데이터다. 실제 `pypdf/TXT` 처리는 독립 Agent가 아니므로 `DOCUMENT_PARSER_AGENT`를 제거하고 `LOCAL_DOCUMENT_GATE`로 정정했다. Google Document AI·OCR·Gemini 호출은 0건이며 후속 확장으로 남는다.
- 앞 단계가 HOLD여도 완료·불일치·추가 입력 필요 수를 최종 보류 검토 단계에서 대조한다. 최종 HOLD는 유지하되 확인 가능한 결과를 숨기지 않는다.
- 실제 NASA Micron TID 요약에 잘못된 `23LC1024-I/SN · Microchip Technology`를 입력하면 39 krad(Si), 시료 13, LDC 201816의 3개는 숫자·단위·원문 위치를 확인하고 identity 문자열 2개는 불일치, 승인 BOM·임무 요구량 2개는 추가 입력 필요로 분리한다. 이는 시험값 진위나 임무 적합성 검증이 아니다.
- 콘솔 문구를 `확인 · 불일치 · 추가 입력 필요`, `최초 보류 책임`으로 정리하고 공개 카탈로그를 `전체 문서 결과` 메뉴에 통합했다.
- Product 회귀 169개, Python compile, `git diff --check`를 통과했다. 브라우저에서 실제 NASA 요약의 `3 확인 · 2 불일치 · 2 추가 입력 필요`, 공개 GCP 결과 15행, 임무 문서 2건의 잘못된 제조사 불일치 0건과 최신 deployment receipt를 확인했다.

## H39 Mission/Part/Test Cloud Catalog — 2026-08-25

- Local parser 입력 축을 부품 중심에서 `MISSION_PLAN · PART_SPEC · RADIATION_TEST`로 확장했다. 임무명·궤도 유형·고도·경사각·기간·차폐 두께 후보를 원문 span에 결속하고, 임무 계획에는 승인 BOM 대신 방사선 환경 연결 공백을 반환한다.
- NASA Landsat 9 `705 km · 98.2° · 5년`, ESA Sentinel-2 `786 km · 98.5° · 7년`, Microchip 23LC1024 `2.5–5.5 V · -40~85°C` 공식 출처 요약을 수동 test-data에 추가했다. 임무 조건은 방사선 환경 계산이 아니고 부품 명세는 방사선 시험이 아니다.
- `전체 문서 결과`는 GCP 공개 JSON을 우선 읽고 로컬 snapshot으로 fallback한다. 문서 15개를 처리 단계 표로 표시하고, 실제 조합은 환경·명세·exact identity·시험 근거 공백에서 fail-closed한다. 합성 Core만 final gate까지 실행하지만 `SYNTHETIC_ONLY / HOLD`다.
- 실제 브라우저에서 `GCP LIVE · PUBLIC READ`, 문서 15·공개 요약 6·final gate 5·승인 0, 공격·권리·손상 PDF의 구체 blocker, 16-event SHA-256 chain과 GCS generation receipt를 확인했다.
- 공개 원문 PDF를 복제하지 않고 공식 URL이 있는 로컬 작성 요약과 synthetic fixture만 배포했다. 실제 승인 BOM·고객 문서·비밀정보·방사선 assurance는 0이다.

## H38 Consolidated Two-Tab Demo — 2026-08-25

- 발표 운영을 `Presentation + spectra-demo`, 총 2개 탭으로 축소했다. Slide 03·09의 제품 링크는 `http://127.0.0.1:8765/demo/evidence-console.html`과 named target `spectra-demo`를 공유한다.
- 검증 콘솔 안에 `문서 1개 검사 · 3개 입력 연결 · 공격 검증 기록 · 전체 문서 결과` 네 모드를 두고, 공개 카탈로그 결과표를 동일 URL의 내부 패널로 내장했다. 합성 PDF 원문 링크도 새 창을 열지 않는다. `Roadmap Lab`은 유지하지만 주 발표 링크에서 제거했다.
- Local PDF/TXT parser는 실제 시험 문서의 TID dose·dose rate·LET·cross-section·fluence·particle energy·temperature·voltage·sample size·LDC 값을 원문 span과 단위에 결속한다. 숫자는 모두 `UNAPPROVED_CANDIDATE`이며 failure point·근사 tolerance를 rating이나 PASS로 승격하지 않는다. NASA·ESA 공개 관측값 3종을 source URL이 있는 요약 fixture로 추가했고, 한글 파일명은 URL 인코딩 후 loopback 서버에서 안전하게 복원한다.
- 사용자 환경의 8765에는 `/api/intake`가 없는 정적 Python server가 떠 있어 합성 3종이 빈 실패 행으로 끝나는 것을 재현했다. 해당 정적 server를 종료하고 `scripts/run_evidence_console.py --port 8765` 통합 server로 교체했다.
- Batch는 `/api/intake` 실패를 더 이상 조용히 삼키지 않고, 통합 server 실행 명령을 인접 오류 메시지로 표시한다. `file://` 실행도 같은 안내로 fail-closed한다.
- 교체 후 사용자 확인에서 기존 Local/GCP 두 탭은 원래부터 한 Console 안에 있었고, 별도 Batch 링크만으로는 실제 통합 화면이 아니라는 문제를 확인했다. H38에서 Batch를 Console의 세 번째 `여러 문서 표` 모드로 내장했다. 8765 실제 브라우저에서 URL이 `evidence-console.html`로 유지된 채 기존 terminal·summary가 숨겨지고 내장 결과표가 표시되는 것을 확인했으며, 합성 3종은 `documents 3 / candidates 7 / HOLD 3 / reference 3 / 3`, 3행, alert hidden으로 완료됐다.
- UI 컨펌 뒤 Control Tower가 변경 범위 직접 테스트 `tests.product.test_evidence_batch`와 `tests.product.test_product_data_binding`을 실행했다. 첫 실행은 화면의 최신 열 제목과 맞지 않는 stale assertion 1건만 실패했고, 기대값을 실제 UI 계약에 맞춘 뒤 21 tests가 모두 통과했다.
- 1280×720 실제 브라우저에서 Local 합성 PDF 13 events·후보 7개·최종 `HOLD`, GCP 저장 로그 13건·`SNAPSHOT ONLY · HOLD`, 여러 문서 표 `documents 3 / candidates 7 / HOLD 3 / reference 3 / 3`과 결과 3행을 독립 재현했다. 세 모드는 같은 `evidence-console.html` URL을 유지했고 Slide 03·09는 동일 `spectra-demo` 탭을 재사용했다.
- 이 검증은 로컬 합성 Product 통합과 저장 snapshot 표시에 한정한다. 실제 문서 정확도·OCR·Document AI·Gemini·live GCP·radiation assurance는 계속 `NOT_EVALUATED / HOLD`다. Product 전체 157개와 저장소 로컬 runbook 회귀가 통과했으며 Git 통합은 아직 수행하지 않았다.

## H37 Batch Evidence Provenance Table — 2026-08-25

- `Roadmap Lab`은 H36 상태로 동결하고 주 발표 시연 동선을 `Raw Evidence Console → Batch Evidence Review`로 고정했다.
- `demo/evidence-batch.html`의 단순 후보값 열을 `field · value · 원문 문자 위치` 카드로 바꾸고, 문서 열에 extraction engine과 PDF page count를 함께 표시한다.
- 정상 합성 PDF는 주문형번·제조사·TID·SEU·SEL·SEB·SEGR 7개 후보와 각 source span을 표시한다. 지시문 공격과 권리 미확인 문서는 후보를 노출하지 않고 최초 차단 관문·자연어 이유·stable code를 표시한다.
- 실제 사용자 파일은 reference가 없으므로 계속 `NOT_EVALUATED`이며 정확도·일치율을 생성하지 않는다. `3 / 3`은 고정 합성 control의 processing status·blocker·candidate set 대조에만 적용된다.
- localhost 실제 브라우저에서 합성 3종, 후보 카드 7개, HOLD 3건, reference `3 / 3`, 원문 span과 pypdf 4쪽 표시, x/y overflow 0과 console 오류 0을 관찰했다.
- 사용자 지시에 따라 정식 unit/attack test와 전체 회귀는 UI 컨펌 전까지 실행하지 않았다. 실제 문서 일반화·OCR·과학 정확성·actual evidence·radiation assurance는 계속 `NOT_EVALUATED / HOLD`다.
- 상태 상한은 `READY_FOR_REVIEW`다.

## H36 Local File to Receipt — 2026-08-25

- `demo/roadmap-lab.html`의 임의 로컬 파일 선택 경로를 단순 hash 표시에서 `LOCAL_BUNDLE_BINDING_RECEIPT_1.0.0` 생성까지 확장했다.
- 10 MB 이하 파일을 브라우저 메모리에서만 읽고 file SHA-256과 내부 canonical manifest SHA-256을 결속한다. 원문 bytes·로컬 절대경로·파일명·artifact identity·file/manifest hash는 다운로드 receipt에 포함하지 않는다.
- 자동 draft의 action rights 8종은 모두 `UNRESOLVED`이고 외부 승인 anchor가 없으므로 `PROVENANCE_FAILURE / HOLD_NOT_ISSUED / NOT_FOR_DECISION / HOLD`다.
- Step 01은 영수증 생성과 다운로드를 보여주고, Step 02는 원본 결속 통과 후 3번 `출처·권리`에서 멈춰 권리 manifest와 승인 anchor를 다음 행동으로 반환한다.
- localhost 실제 브라우저에서 임의 TXT 1건의 영수증 생성, 3번 관문 차단, x/y overflow 0과 console warning/error 0을 관찰했다. 사용자 지시에 따라 정식 unit/attack test와 전체 회귀는 UI 컨펌 전까지 실행하지 않았다.
- 실제 evidence ingest·권리 승인·provider 검증·과학적 적용성·assurance는 추가하지 않았다. 상태 상한은 `READY_FOR_REVIEW`다.

## H32 Batch Evidence Table & Early Architecture Link — 2026-08-24

- `demo/evidence-batch.html`은 기존 loopback `/api/intake`를 재사용해 PDF/TXT 여러 개를 순차 처리하고, 문서별 후보·최초 중단 위치·자연어 이유·stable code·최종 `HOLD`를 단일 표에 표시한다.
- 고정 합성 3종은 정상 PDF의 승인 BOM 공백, 지시문 공격, 내부 표시 권리 미확인을 서로 다른 차단 경계로 재현한다. 세 scenario의 처리 상태·최초 blocker·exact candidate set이 고정 정답과 `3 / 3` 일치했다. 실제 사용자 파일에는 정답률을 표시하지 않는다.
- Raw Evidence Console과 발표 Slide 03에서 batch 표로 직접 이동한다. 발표 흐름은 현재 구현 경계와 제품 링크를 유지하고 그림 아래의 미래 기술 rail만 제거했으며 Document AI·Gemini API 호출은 0건이다.
- 변경 범위 직접 테스트 10개와 localhost 1280×720에서 합성 3종, 후보 7개, HOLD 3건, reference `3 / 3`, 가로 overflow 0을 확인했다. 공용 schema·Core·GCP 상태는 변경하지 않았다.
- 실제 document 일반화, OCR, 과학 정확성, actual evidence와 radiation assurance는 계속 `NOT_EVALUATED / HOLD`다.

## H31 Human-readable Console & Synthetic Unstructured PDF — 2026-08-24

- Raw Evidence Console의 기본 출력을 JSON wall에서 단계별 실행 타임라인과 GCP Agent 로그 표로 바꿨다. 원본 JSONL은 `원본 JSONL 보기` 토글에서 동일 응답 그대로 보존한다.
- `output/pdf/spectra_synthetic_unstructured_radiation_report.pdf`는 표지·메타데이터 표·다단 본문·합성 차트·SEE coverage 표·각주·회전 스탬프를 가진 4쪽 synthetic training artifact다. 모든 페이지가 실제 시험 보고서가 아님을 명시한다.
- 고정 ground truth 7개는 주문형번·제조사·TID·SEU·SEL·SEB·SEGR exact candidate만 대조한다. 실제 parser가 7개를 모두 source span과 함께 찾았고 `7 / 7 · 100%`를 표시하지만 실제 문서 일반화·OCR·과학 정확성·radiation assurance로 확대하지 않는다.
- 기본 macOS Python에 `pypdf`가 없을 때 서버는 장치에 이미 설치된 bundled PDF runtime으로 재실행한다. runtime 부재 시 PDF는 `PDF_EXTRACTOR_UNAVAILABLE / HOLD`로 닫힌다.
- 직접 테스트 24개, Product 전체 회귀 153개와 loopback PDF 통합에서 13개 순차 이벤트·후보 7개·`APPROVED_BOM_TARGET_MISSING / HOLD`를 확인했다. 실제 브라우저에서 합성 PDF 버튼, 7/7 reference, GCP 표 13행, raw toggle과 console warning/error 0을 확인했다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공용 schema·Core engine과 실제 evidence contract는 수정하지 않았다.

## H30 Raw Evidence Console — 2026-08-24

- `scripts/run_evidence_console.py`는 `127.0.0.1`에만 bind해 선택한 PDF/TXT를 기존 deterministic intake로 실제 처리하고, 수신·파싱·후보·승인 대상 대조·Assurance 미호출·최종 판단을 JSONL 이벤트 순서로 내보낸다.
- `demo/evidence-console.html`은 원시 JSONL과 같은 실행의 중단 위치·확인 사실·이유·다음 행동을 함께 표시한다. 원문과 임시 경로는 이벤트에 노출하지 않으며 임시 파일은 실행 후 제거한다.
- GCP 탭은 H05 Control Tower verified snapshot의 구조화 로그 13건만 읽기 전용으로 표시한다. 현재 Cloud Logging 조회, 새 Workflow 실행과 GCP 상태 변경은 없다.
- 직접 테스트 23개와 loopback HTTP 통합에서 정상 합성 TXT의 7개 이벤트·최종 `HOLD`, 저장 로그 `live=false / 13건 / HOLD`를 확인했다. 실제 브라우저 viewport는 도구 URL 정책으로 `NOT_EVALUATED`다.
- 승인 BOM target과 실제 environment/part contract가 없으므로 정상 파싱도 `NOT_FOR_DECISION / HOLD`다. OCR·LLM·live GCP·실제 방사선 assurance는 추가하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공용 schema·Core engine을 수정하지 않았다.

## H29 NASA Local Gate Product Binding — 2026-08-24

- production `evaluate_nasa_snapshot()`가 caller-supplied synthetic bytes를 검증한 deterministic receipt를 생성하고, Evidence Review 1단계가 readiness JSON과 함께 실제로 읽는다.
- 화면은 NASA control만 `CONTROL VALID · NO DECISION`으로 표시하고 SPENVIS provider reference와 승인 BOM 공백을 별도로 유지한다. receipt의 decision-use 승격·상태 손상은 `DATA_UNAVAILABLE · HOLD`로 닫힌다.
- source adapter·Evidence Review·Product binding 직접 테스트 42개와 localhost 1280×720의 세 상태·HOLD·overflow 0을 확인했다. live NASA fetch, actual evidence, external trusted anchors와 suitability는 추가하지 않았다.

## H28 Functional Evidence Review Demo — 2026-08-24

- 설명 중심 H27 허브를 세 bundled JSON을 실제로 읽고 검증하는 단일 제품 동선으로 교체했다. 주 화면 조작은 `근거 검사 실행 → local review action → 변경 영향 불러오기` 세 가지뿐이다.
- 1단계는 SPENVIS provider reference, NASA/COTS exact source와 rights 공백을 표시하고, 2단계는 합성 exact-part 후보의 PN·process·lot·TID와 세 가지 검토 action을 제공하며, 3단계는 generated MVP 결과 `0.063072 → 0.013072`와 environment/part gap을 함께 표시한다.
- 낙관 decision, fabricated approval/rights와 change-impact value rebinding 공격은 모두 `HOLD`로 닫힌다. 검토 action도 최종 승인이나 `PASS`를 만들지 않는다.
- 직접 테스트 10개와 Product binding 17개가 통과했다. localhost 1280×720에서 세 조작, 실제 fixture 값 표시, 최종 `FINAL ASSURANCE · HOLD`와 document/work/result x/y overflow 0을 확인했다.
- 실제 connector/API, actual evidence, authenticated audit와 radiation assurance는 추가하지 않았다. 공용 schema·Core 변경 요청은 없다.

## H27 Presentation-first 3-Step Product Demo — 2026-08-24

- 기존 Roadmap Lab의 7개 동급 기능 카드를 제거하고 `자료 연결 → AI 보조 검토 → 판단과 다음 행동`의 3단계 guided demo로 전면 재구성했다.
- 첫 화면에 “방사선 수치를 만들어 주는 AI가 아니라, 근거가 현재 판단에 쓸 수 있는지 검증하고 부족한 다음 행동을 보여 주는 제품”이라는 정의를 인접 배치했다.
- 각 단계는 발표 자료와 같은 검정 배경, 큰 흰색 제목, 얇은 경계선과 단일 흰색 선택 상태를 사용한다. 사용자는 하단 `다음` 버튼을 두 번 눌러 40초 권장 시연을 완료한다.
- 7개 상세 route는 삭제하지 않고 오른쪽 `Q&A ↗` 보조 링크로만 이동했다. 본 발표에서는 제목과 오른쪽 `SPECTRA ANSWER`만 설명하며 세부 도구를 열지 않는다.
- 발표 Slide 11 링크 문구도 `40초 제품 흐름 열기`로 바꿔 화면 목적을 기능 개수 대신 사용자 흐름으로 표현했다.
- Git 밖 7분 주 대본은 Slide 10 GCP 70초·Slide 11 제품 흐름 45초로 재배분해 계산 총 6분 45초와 전환 여유 15초를 유지했다. 실제 사람 낭독·탭 전환 시간은 계속 `NOT_MEASURED`다.
- Roadmap 직접 테스트 8개와 Product binding 17개가 통과했다. localhost 1280×720에서 1→2→3→초기화 동선, 단계별 결론과 `FINAL ASSURANCE · HOLD`, document/story/answer x/y overflow 0을 확인했다.
- 실제 connector·AI API·authenticated approval·CAD 계산·KMS·penetration test 또는 actual evidence는 추가하지 않았다. 최종 assurance는 계속 `HOLD`다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공용 schema·Core engine과 7개 상세 기능 계약을 수정하지 않았다.

## H26 Roadmap Lab bounded expansion — 2026-08-24

- `demo/roadmap-lab.html`은 발표 Phase 01~03의 7개 local 화면을 단일 진입점으로 연결한다. 상태는 `IMPLEMENTED_BOUNDED / READINESS_ONLY / BLOCKED_EXTERNAL`로 분리하고 전체 묶음은 `SYNTHETIC / LOCAL DEMO / ASSURANCE HOLD`다.
- Phase 01은 SPENVIS·NASA·COTS source readiness와 decision-ineligible COTS discovery registry를 표시한다. 별도 Python NASA snapshot gate는 caller-supplied local bytes의 hash·NASA allowlisted host·record/revision/time·action rights·exact orderable identity와 외부 anchor 결속을 검사하며, 실제 후보의 상한도 `READY_FOR_REVIEW / NOT_FOR_DECISION / HOLD`다.
- Phase 02는 합성 document extraction candidate의 source binding·local reviewer action과 Document AI/Gemini processor별 미구성·미승인 readiness를 분리한다. API 호출·credential·authenticated approval·actual audit trail은 0건이다.
- Phase 03은 authoritative generated result의 Change Impact, CAD revision 결속 readiness, H05 snapshot의 다섯 bounded control과 다섯 미구현·미평가 보안 gap을 표시한다. 실제 CAD parser·3D shielding 계산·KMS 운영·침투시험은 없다.
- 독립 red-team에서 발견한 COTS export identity 우회, document rights scope 누락, AI region display injection, security snapshot의 재계산 hash display 우회, synthetic policy `APPROVED` 용어 충돌을 모두 차단했다.
- 직접 테스트 11개 module 136 tests, 후속 P1 보완 대상 8개 module 95 tests가 통과했다. localhost 1280×720에서 Roadmap Lab 7 route와 발표 11번 링크, 수정된 Document Review·Change Impact·Security Posture를 확인했고 각 화면 x/y overflow는 0이다.
- 최종 통합 회귀에서 Product 전체 125 tests, source adapter 14 tests가 통과했고 인접 schema·simulation·environment·Assurance·GCP H05 회귀도 실패 없이 유지됐다.
- 발표 cover와 COTS 비교의 검증되지 않은 비용·납기·성능·면역 수치를 제거하고 `SYNTHETIC DEMO · ACTUAL EVIDENCE 0 · FINAL HOLD` 경계를 추가했다. Product binding 17 tests와 실제 1280×720 slide overflow 0을 확인했다.
- 실제 environment contract·승인 exact-part packet·live connector/API·과학적 assurance는 계속 0건이다. H26 검증은 로컬 기능과 fail-closed 경계만 `VERIFIED`하며 Stage 8과 Core MVP는 `IN_PROGRESS`, 최종 판단은 `HOLD`다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공용 schema·Core engine을 수정하지 않았다.

H21은 SPENVIS·NASA Public DB·COTS Evidence Library를 live 연동했다고 가장하지 않고, source별 connector readiness와 locator·권리·provenance 공백, blocker owner/action을 별도 fail-closed intake 화면에서 검토한다.

## H21 Evidence Source Intake — 2026-08-24

- 새 `demo/evidence-intake.html`은 remote dependency·API·telemetry·storage 없이 bundled synthetic sample 또는 사용자가 선택한 local JSON을 브라우저 메모리에서 검토한다.
- SPENVIS는 provider job reference·action별 권리·승인 raw manifest·provenance, NASA/COTS는 exact locator·권리·provenance가 모두 닫히기 전 `CONNECTOR_NOT_READY`를 유지한다.
- 세 source 모두 stable blocker code, 제한된 담당 역할과 다음 action만 표시한다. 정상 synthetic fixture도 `VALID / NOT_EVALUATED / HOLD`이며 connector나 decision input으로 사용하지 않는다.
- malformed JSON·nested shape 오류·중복/누락 source·`ACTUAL` 자기 승격·connector `READY`·decision `PASS`·`PASS` blocker·임의 locator/token 삽입은 source identity와 세부값을 숨긴 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫힌다.
- Audit export는 source ID, connector/requirement status, blocker code·owner·action code와 HOLD decision만 allowlist로 내보낸다. locator 원문·URL·로컬 경로·identity·설명 원문·raw evidence와 공학 수치는 제외한다.
- H21 직접 테스트 11개와 JavaScript syntax, fixture JSON parsing, `git diff --check`가 통과했다.
- localhost server는 실행했지만 Control Tower 브라우저 backend가 사라져 실제 1280×720 viewport·console 검증은 `NOT_EVALUATED`다. 자동 테스트를 브라우저 렌더링 증거로 확대하지 않는다.
- 실제 live connector, provider job reference, 승인 rights/raw manifest, exact source locator와 실제 contract는 계속 0건이다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H21은 새 독립 demo·fixture·test와 이 CURRENT 기록만 추가하며 H20 Workspace, 공용 schema·engine·발표 deck을 수정하지 않았다.

H20은 H19에서 검증된 synthetic Environment readiness receipt와 byte-equivalent인 내장 sample을 같은 validator 경로로 읽는 `환경 HOLD 샘플` 버튼을 추가했다. 발표자는 파일 선택 없이 blocker → 담당 역할 → 다음 행동 → `HOLD`를 설명한 뒤 초기화할 수 있다. 실제 contract나 공학 수치·suitability·assurance를 추가하지 않았다.

## H20 One-click Hold Demo Path — 2026-08-24

- `demo/workspace.html`의 `환경 HOLD 샘플`은 `demo/data/readiness-environment-hold-v1.json`과 동일한 synthetic receipt를 `resolveReadinessReceipt()`에 전달한다. 별도 성공 경로나 parser 우회는 없다.
- 화면은 `ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED → ENVIRONMENT_EVIDENCE_OWNER → 배포 소유 인증기 구성·Gate 재실행`과 `HOLD_NOT_ISSUED / PROVENANCE_FAILURE / NOT_EVALUATED / HOLD`만 표시한다.
- 초기화는 identity를 숨기고 export를 비활성화한 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 복귀한다.
- Workspace 직접 테스트 22개가 fixture 동등성, 정상 HOLD, malformed·optimistic receipt 차단과 export redaction을 통과했다.
- localhost 실제 브라우저 1280×720에서 one-click sample → blocker/owner/action → HOLD → reset 동선을 확인했다. document와 세 panel의 x/y overflow는 0이고 console warning/error도 0이다.
- 실제 environment contract, 승인 evidence와 assurance evidence는 계속 0건이다. H20은 발표 시연 동선 단축이며 실제 Evidence-to-Decision 발행이 아니다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공용 schema·engine·upstream Workstream·발표 deck은 수정하지 않았다.

H19는 Control Tower가 검증한 `schemas/readiness-receipt.schema.json` dispatcher의 Environment·Part v1 receipt를 기존 Evidence Review Workspace가 직접 소비하도록 연결했다. upstream `tests/parts_evidence`나 다른 test module을 import하지 않고, WS80 내부 fixture와 브라우저 validator로 제한된 readiness 상태만 표시한다.

## H19 Readiness Receipt Integration — 2026-08-24

- `demo/data/readiness-environment-hold-v1.json`은 `ENVIRONMENT / SYNTHETIC_CONTROL / HOLD_NOT_ISSUED`, `demo/data/readiness-part-contract-not-implemented-v1.json`은 `PART / DEMO_ONLY / CONTRACT_NOT_IMPLEMENTED`를 보여 주는 UI용 synthetic fixture다.
- 화면은 source class/purpose, processing·identity·applicability의 제한된 상태, blocker code와 blocker별 담당 역할·다음 행동만 표시한다. receipt/source identity, 공학 수치, suitability, actual output reference와 decision-use는 표시하거나 export하지 않는다.
- Environment v1은 `HOLD_NOT_ISSUED`, Part v1은 `CONTRACT_NOT_IMPLEMENTED`, 모든 v1은 `used_for_decision=false / assurance_decision=HOLD`일 때만 ready model이 된다.
- optimistic issuance candidate, implemented target, decision-use·assurance 상향, cross-kind field, unknown version/kind, malformed nested type, 빈·중복·`PASS` blocker는 identity·세부값을 숨긴 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫힌다.
- Workspace 직접 테스트 21개와 기존 Product binding 17개가 통과했다. 공용 schema나 upstream test module import는 없다.
- localhost 실제 브라우저 1280×720에서 두 fixture의 파일 선택, status·blocker·owner/action 표시, x/y overflow 0, console warning/error 0을 확인했다. Reset은 identity를 숨기고 export를 비활성화한 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 돌아간다.
- Control Tower 직접 검증과 최종 회귀에서 Workspace 21 tests와 기존 Product 17 tests가 통과했다. 실제 environment/part contract, 승인 BOM, 시험 evidence, suitability와 assurance evidence는 계속 0건이다. H19는 receipt 상태 가시화이며 실제 Evidence-to-Decision 발행이나 Product assurance 연결이 아니다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H19는 공용 schema·engine·upstream Workstream·발표 파일을 수정하지 않았다.

H18은 발표용 `demo/index.html`과 Product prototype `demo/product.html`을 결합하거나 수정하지 않고, 별도 `demo/workspace.html`에서 로컬 evidence readiness JSON을 검토한다. 8개 coverage 영역, blocking gap의 stable code·담당 역할·필요 evidence·다음 행동, 최종 `NOT_EVALUATED / HOLD`와 비민감 audit export를 한 화면에 표시한다.

## H18 Evidence Review Workspace — 2026-08-24

- `demo/data/review-workspace-synthetic.json`은 `SYNTHETIC / DEMO_ONLY` sample이다. 실제 environment/part contract, 승인 BOM, 시험 원문, rights 승인과 실제 dose는 0건이다.
- 브라우저는 선택된 JSON을 메모리에서만 읽고 서버 업로드·API·telemetry·local/session storage를 사용하지 않는다. 입력 형식의 허용된 상태를 표시할 뿐 수치·identity·suitability·ROI·assurance를 계산하거나 추정하지 않는다.
- 정상 sample은 8개 coverage와 4개 blocking gap을 표시하되 `VALID`를 입력 구조 처리 상태로만 사용하고 `engineering_gate=NOT_EVALUATED / assurance_decision=HOLD`를 유지한다.
- malformed JSON, 잘못된 nested type, duplicate gap ID, unknown coverage status, `ACTUAL` 자기 선언, 인증되지 않은 issuance root, optimistic decision과 dose field 삽입은 identity·세부값을 숨긴 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다.
- Audit export는 allowlist 기반으로 coverage domain/status, stable gap code, owner role, next action code와 decision만 내보낸다. case ID·mission/BOM/package reference, gap 설명 원문, raw evidence, local path, 개인정보와 실제 dose 값은 제외한다.
- H18 전용 직접 테스트 13개는 정상 intake부터 wrapper consumer, 공격별 fail-closed와 export redaction, JavaScript syntax, 원격 dependency 0을 실행 검증한다.
- localhost 실제 브라우저에서 sample load와 Reset, 1280×720·1440×900 document overflow 0, 모든 gap owner/action·Decision·export 첫 화면 가시성, console warning/error 0을 확인했다. 인앱 브라우저에서 export 링크의 정규 data URL과 filename 활성화는 확인했지만 download event는 제공되지 않았고 연결된 Chrome이 없어 실제 파일 생성 관측은 `NOT_EVALUATED`다.
- 작업 중 공유 dirty worktree의 `demo/index.html` 해시가 외부 병렬 변경으로 달라졌으나 H18은 해당 파일과 `demo/product.html`을 수정하거나 되돌리지 않았다. 기존 Product suite의 GCP 문구 기대값 1건도 이 외부 deck 변경 때문에 실패했으며 H18 범위에서 수정하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H18은 공용 schema/engine이나 실제 evidence contract를 만들지 않았다.

H17은 발표와 Product의 ECC residual을 generated production MVP Core `0.013072`로 통일하고, Product 05를 runtime WATCHDOG가 아닌 Core 결과 전달 무결성 시연으로 전환했다. Product 보증 판단은 상·하 exact 4열이며, 발표 07은 GCP 배포·세 Agent 책임·정상 HOLD·변조 차단 HOLD만 주 화면에 남긴다. 실제 환경 run·승인 BOM·시험 원문은 0건이고 모든 assurance는 계속 `HOLD`다.

2026-08-21 범위 감사에 따라 H15의 runtime 주 동선 제거 방향은 유지한다. Competition Demo 연결은 Workstream 70이 검증한 Agent 실행 ID·GCP 상태·HOLD 결과를 읽기 전용으로 표시하며, Product가 Agent 상태나 cloud 성공을 하드코딩하지 않는다. 기존 WATCHDOG `60→999` 주 화면은 H17에서 Core 결과 전달 무결성 시연으로 교체했다.

## 2026-08-22 Control Tower 후속 검증

- 사용자 확인상 실제 발표는 `demo/index.html` 단독 경로였고 `demo/product.html`은 사용하지 않았다. 따라서 아래 H17 Product 검증은 보존되는 별도 후보 이력이며, 현재 발표 deck 통합 완료의 증거로 사용하지 않는다.
- 실제 `demo/product.html` diff에서 1·4 mm는 TID만 표시하고 Residual SEU를 `—`로 닫으며, ECC OFF는 비활성화한다.
- 2 mm는 generated Decision Engine의 ECC OFF `0.063072`와 ON `0.013072`를 각각 표시하고 설명을 `BASELINE / VARIANT 결정 엔진 결과 · 실제 완화 성능 아님`으로 유지한다.
- 5 mm는 TID·Residual SEU를 만들지 않고 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`를 표시한다.
- 제거된 `평가 비중 35점` badge를 계속 요구하던 stale test assertion을 제거하고, 위 네 두께·ECC 상태를 DOM harness로 직접 검증하도록 `tests/product/test_product_data_binding.py`를 보강했다.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_product_data_binding`은 16개 테스트를 통과했고 JavaScript syntax와 `git diff --check`도 통과했다.
- 별도 `demo/product.html`의 실제 1920×1080 렌더링은 이번 회차에 다시 열지 않았으므로 H17 Product 후보는 아직 `VERIFIED`가 아니다. 다만 실제 발표 대상인 `demo/index.html`은 localhost 1280×720에서 13장 overflow 0, console warning/error 0, 1/2/4/5 mm와 ECC OFF/ON, 범위·신뢰성 상·하 박스 정렬, GCP 화면을 Control Tower가 직접 검증했다. 이 발표 deck 검증을 Product H17 검증으로 확대하지 않는다.

## H17 Visual Alignment, Core Value & Integrity Scope — 2026-08-21

- `demo/index.html`은 `mvp-product-result.js`를 직접 소비해 ECC OFF/ON의 production MVP Core `0.063072 / 0.013072`를 표시한다. 권위 residual과 run ID를 HTML에 중복 하드코딩하지 않는다.
- 발표 06은 `결정 과정의 네 가지 신뢰성 원칙`으로 범위를 명시하고 runtime이 섞인 과거 `47회 / 0` aggregate와 `60 ≠ 999` 예시를 주 화면에서 제거했다.
- 발표 07의 6개 node는 동일 grid·높이·padding·중앙 화살표를 사용한다. GCP 배포·Agent 3개·최소권한·로그 13건을 한 줄로 요약하고 정상/변조 카드에는 명사형 `최종 HOLD`만 남겼다. revision·execution ID·stable code는 접힌 기술 상세에 있다.
- Product 보증 판단의 causal row와 action row는 동일한 `repeat(4,minmax(0,1fr)) / gap 8px` 경계를 사용한다. 하단 네 번째 `다음 — 실제 근거를 연결한 뒤 재검토` 카드를 추가했다.
- Product 05는 `결과 전달 무결성`이다. generated MVP Core variant의 Residual SEU만 테스트용 deep clone에서 변경하고 source result ID와 input/output hash는 그대로 둔다. Core 기록과 다르면 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫고 Reset으로 원본 `0.013072`를 복구한다.
- runtime WATCHDOG/TMR/SEL consumer·fixture·기존 공격 테스트는 실험 기준선으로 보존하지만 주 화면에서는 WATCHDOG·60·999·`신뢰성 안전장치 4/4`가 노출되지 않는다.
- Product 직결 테스트 16개가 source parity, stale `0.0063072` UI 0건, Core mutation 단일 필드, hash anchor 보존, 4열 카드, GCP snapshot, wheel/smooth와 Reset을 검사한다.
- 실제 1920×1080 `file://` 브라우저 검증은 제어 환경의 URL 정책이 차단해 `NOT_EVALUATED`다. 우회하지 않았고 자동 DOM harness를 실제 viewport 증거로 확대하지 않는다.
- Workstream 90 change request: ECC 값을 `0.013072`, Product 05를 `결과 전달 무결성`, 발표 06을 Core 신뢰성 원칙, 발표 07을 간소화된 GCP 흐름으로 맞춰야 한다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공통 engine/schema/fixture는 수정하지 않았다.

## H16 GCP Workflow Visibility & Tone Alignment — 2026-08-21

- `demo/build_gcp_snapshot.py`가 H05 `e2e-runs / core-parity / inventory-and-logs` evidence에서 byte-deterministic JSON·JS wrapper를 생성한다. source path·schema version·evidence 최종 관측 시각·canonical preimage·snapshot SHA-256을 보존한다.
- 발표 deck 07을 6단계 `Storage 입력 → Workflows → Mission → Parts → Assurance → Storage·Logging`으로 교체하고, Multi-Agent·GCP 평가 비중 35%, 정상 execution과 두 차단 execution, IAM·로그·Console 확인 링크를 표시한다.
- Product는 5단계 `검토 조건 → 수치 변화 → 보증 판단 → GCP 실행 → 숫자 변경 감지`로 확장했다. GCP 화면은 read-only이며 H05 revision·execution ID를 snapshot에서만 읽는다.
- 정상 GCP 실행 `SUCCEEDED`와 Agent 3개 `VALID`는 보증 PASS가 아니다. 정규 snapshot의 최종 상태는 `NOT_EVALUATED / HOLD`이며 실제 환경 run·승인 BOM·시험 원문은 0건이다.
- endpoint override는 Agent 호출 0회로 차단되고, body/hash 위조도 stable code와 `HOLD`로 닫힌다. snapshot 누락·hash/state 변조 시 UI는 ID와 수치를 표시하지 않고 `DATA_UNAVAILABLE / HOLD` fallback을 유지한다.
- 두 HTML의 사용자 노출 한국어 설명 문장을 `~다`로 정렬했다. 질문형 제목·버튼·라벨·상태 code는 문장 종결 규칙에서 제외한다.
- Product 자동 테스트 15개가 exporter 결정론, provenance/hash, exact H05 revision·execution, 5단계 navigation, 6단계 workflow, stale GCP 0 문구 제거, 말투, JS syntax와 기존 binding·signed-zero·number-change·wheel/smooth 회귀를 검사한다.
- 인앱 브라우저의 URL 정책이 `file://` 접근을 차단해 실제 viewport·Console 링크·console warning/error 0은 `NOT_EVALUATED`다. 자동 DOM/JS harness 결과를 실제 브라우저 확인으로 확대하지 않는다.
- Workstream 90 change request: 발표 대본에서 deck 07을 H05 snapshot 기반 Multi-Agent GCP 흐름으로, Product 동선을 5단계와 exact 화면명으로 갱신해야 한다. Workstream 80은 Workstream 90 파일을 수정하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공통 GCP·simulation·assurance 계약은 수정하지 않았다.

## H15 Cover and Product Clarity Remediation — 2026-08-21

- `demo/index.html`: `COVER` 표지 추가, 본문 01~07 유지, CSS `slide-enter` 진입 효과와 `prefers-reduced-motion` 경계 추가. H14 wheel controller와 양 끝 clamp는 변경하지 않았다.
- `demo/product.html`: truth strip을 한 줄로 축약하고 실제 근거 0건을 한 묶음으로 배치했다. TID/SEU/Residual SEU는 `repeat(3,minmax(0,1fr))`, `min-width:0`, tabular numbers를 사용한다.
- ECC는 메모리 정보 뒤집힘→수정 가능한 오류 탐지·정정→잔여 논리 오류 감소의 인과와, 사건 자체·파괴성 SEE를 없애지 않는 경계 및 실제 채택 근거 조건을 인접 표시한다.
- Product 02의 runtime 탭/control은 제거했다. 저장소의 runtime 계산·schema·fixture·payload·consumer는 향후 trade study용으로 그대로 보존했다.
- Product 03은 `확인된 것 / 아직 필요한 것 / 그래서 내린 결정`으로 재구성했다. machine code와 식별자·invalidation은 접힌 기술 상세에만 둔다.
- Product 04는 hardware 완화가 아니라 계산 결과가 Product로 전달될 때의 숫자 변경 감지임을 상단에서 설명한다. 기존 `60 → 999 → 비노출 → HOLD → Reset` consumer는 변경하지 않았다.
- 실제 브라우저 viewport/console과 표지 포함 실제 장치 wheel 왕복은 H15에서 재실행하지 않아 `NOT_EVALUATED`다. 사용자가 H14 기본 wheel 동작을 수용했다는 이전 확인만 유지한다.
- `CONTRACT_CHANGE_REQUEST`: 정규 H05 MVP variant residual(`0.013072`)과 H15 문구에 남은 Stage 2 ECC fixture residual(`0.0063072`)의 Product 표시 기준을 Control Tower가 후속 계약에서 명확히 해야 한다. H15는 generated payload를 변경하거나 브라우저에 authoritative 값을 중복 하드코딩하지 않았다.

## H14 Control Tower 독립 검토 — 2026-08-21

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_product_data_binding`: 13 tests 통과.
- `git diff --check`: 통과.
- 사용자가 실제 `file://` 발표 장치에서 기본 wheel 이동이 작동한다고 확인했다. 첫↔마지막 wrap/전체 왕복은 필요하지 않다는 사용자 결정을 수용하며 H15 Exit Gate에서 제외한다.
- 고정 화면 wheel controller, 네 안전장치, Product 04의 기존 H10 integrity 경로는 구현·회귀 측면에서 유지 가능하다.
- 그러나 `demo/index.html`은 H14 고정 화면 복귀 과정에서 기존의 부드러운 전환 효과를 잃었다.
- Product 01은 상단 rail·answer·panel·0건 row·footer에서 같은 범위 제한을 반복한다. Product 03도 네 개의 큰 gap card로 같은 근거 공백을 되풀이해 화면 밀도와 설명력이 낮다.
- TMR fixture는 복제 채널 3개·독립 오류·common-mode 0·voter 비취약·repair 없음의 합성 가정이다. SEL fixture는 TMR과 무관한 단일 device scope 전원 보호 경로다. 현재 화면과 H14 설명은 이 차이와 현재 임무 비채택 상태를 충분히 노출하지 않는다.
- 따라서 H14의 화면 명료성 Exit Gate는 `CHANGES_REQUESTED`다. H09/H10 production integrity 검증 기준선과 이전 `VERIFIED` 패키지는 유지한다.
- 후속 지침: `instructions/SPECTRA_80_COVER_AND_PRODUCT_CLARITY_REMEDIATION_H15.md`.

## H14 Screen-First Reliability Story — 2026-08-20

### 발표 deck 06 — 네 가지 안전장치

- kicker: `06 · RELIABILITY`
- 제목: `SPECTRA는 모를 때 숫자를 만들지 않습니다.`
- 보조 문장: `같게 계산하고, 범위 밖에서는 멈추고, 근거를 요구하고, 바뀐 결과는 숨깁니다.`
- `01 다시 계산해도 같음`: `같은 입력 → 같은 결과`, `같은 고정 입력 → 같은 결과`
- `02 모르는 범위는 계산 안 함`: `지원 범위 밖 → 계산 안 함`, `5 mm → 계산 안 함`
- `03 증거가 없으면 보류`: `실제 근거 부족 → 판단 보류(HOLD)`, `실제 근거 0건 → HOLD`
- `04 바뀐 숫자는 숨김`: `전달된 숫자가 다름 → 숫자 숨김`, `60 ≠ 999 → 숫자 숨김`
- 03 카드에 `합성 수치 조건 PASS · 실제 보증 아님`, 실제 환경·승인 BOM·시험 원문 0건, GCP resource 0개와 최종 `HOLD`를 보존했다.
- 주 화면에서는 `False PASS`, fail-closed, integrity, assurance를 이해 전제로 사용하지 않는다.

### `47 / 0` 범위

- 화면 하단에 `고정 합성 오류·공격 실행 47회`와 `잘못 PASS한 경우 0`을 크게 표시한다.
- 바로 옆에 `검증된 고정 합성 세트 기준 · 실제 GCP·과학 정확성 전체 검증 아님`을 표시한다.
- 47회는 assurance manifest의 단위 오류, 범위 밖 입력, 부품 식별 불일치, 증거 누락, 미승인 정책과 결과 변경을 포함한 고정 합성 실행 기준이다. 모든 공격, 실제 시스템 보안, 실제 GCP 또는 과학 정확성 전체 검증으로 확대하지 않는다.

### Product 04 연결

- 상단 label: `신뢰성 안전장치 4/4 · 전달 중 숫자 변경`
- 연결 문장: `앞에서는 재현성·지원 범위·증거 공백을 확인했습니다. 여기서는 계산 뒤 전달된 숫자가 바뀌었는지만 봅니다.`
- H13의 `계산 직후 기록 60초 → 화면에 들어온 테스트용 값 999초 → 서로 다름 → 숫자 숨김 → 판단 보류(HOLD)`와 세 control을 유지했다.
- 주 카드에는 `복구 중 서비스 중단 시간`을 먼저 쓰고 `WATCHDOG`는 접힌 기술 상세로 이동했다.
- `999`는 새 계산 결과가 아니라 오류 주입 테스트용 사본임을 카드 안에서 표시한다.
- H10 `createAttackDemoController()`와 H09 `resolveProductData()`를 그대로 재사용하며 새 검증기·공식·정책·hash 규칙을 추가하지 않았다.

### 고정 화면 wheel intent controller

- H13의 root native scroll-snap, 연속 문서 scroll과 `scrollIntoView()` 경로를 제거했다.
- JavaScript 실행 시 `.slide`는 기본 비노출이고 현재 한 화면만 `display:grid`로 활성화된다. no-JavaScript fallback만 전체 정적 화면을 순서대로 보여 준다.
- wheel controller는 `setTimeout`/`clearTimeout`을 사용하지 않는다. 따라서 trailing event가 release timer를 계속 뒤로 미루는 H11/H12 lifecycle이 없다.
- 첫 이동 시점 `movedAt`은 trailing event로 갱신하지 않는다. re-arm은 150ms quiet gap, 120ms 이후 감쇠 대비 1.8배 impulse, 명확한 반대 방향 impulse, 또는 이동 뒤 900ms hard age와 threshold를 넘는 새 impulse 중 하나로만 허용한다.
- `deltaMode` line/page는 화면 이동 threshold에 맞게 정규화하지만 cursor, pointermove, hover와 focus는 controller 입력이 아니다.
- 자동 harness에서 같은 좌표·pointermove 0으로 line-mode 독립 입력 6회 `01→07`, 역방향 6회 `07→01`, 1초 이상 감쇠·반대 부호 tail은 한 장, 직후 새 impulse는 다음 한 장을 확인했다.
- wheel event API에는 장치 공통 gesture-end phase가 없고 실제 발표 장치 trace를 수집하지 못했다. 실제 mouse/trackpad acceptance 전에는 성공으로 주장하지 않는다.

### Product 02 — 고장 대응 방법

- `Runtime 완화` tab을 `고장 대응 방법`으로 교체했다.
- 질문: `오류가 생겼을 때 시스템은 어떻게 버티고 복구할까요?`
- 중심 문장: `이 방법들은 방사선 사건을 없애지 않고, 오류가 발생했을 때 영향을 줄이거나 복구하도록 돕습니다.`
- 쉬운 선택명: `자동 재시작(WATCHDOG)`, `3중 다수결(TMR)`, `과전류 전원 보호(SEL 대응)`.
- 각 선택은 `문제가 생김 → 대응 동작 → 남는 영향·대가`를 표시한다.
  - 자동 재시작: 시스템 정지 → 멈춤 확인·재시작 → 잘못 감지 가능, production record의 재시작 1회·중단 60초.
  - 3중 다수결: 한 장치 오류 → 세 장치 계산·다수 선택 → 장치·전력·복잡도 증가, production record의 p=0.1(10%)·시스템 실패 가능성 0.028(2.8%).
  - 과전류 전원 보호: 위험한 과전류 → 전원 차단·재가동 → 실제 사건·잘못 감지 모두 재가동 가능, production record의 전원 재시작 2회·중단 32초.
- 공통 문구는 `합성 계산 결과 · 실제 완화 효과 검증 아님 · 근거 부족으로 HOLD`다.
- 수치 문장은 `record.projection`과 TMR `controlInputs`에서 표시 형식으로만 투영된다. WATCHDOG/TMR/SEL 공식, downtime 합산과 정책 threshold는 브라우저에서 계산하지 않는다.
- false activation, projection, processing 상태, stable code, equation/result/packet ID와 input/output hash는 접힌 기술 상세로 이동했다.

### H14 검증 상태

- Product 13 tests 통과: H08~H13 consumer, signed-zero, Reset, 1/2/4/5 mm, ECC와 runtime fail-closed 회귀 유지.
- 정적 검증에서 06의 카드 4개, exact 문구 16개, `47회 / 0`, 범위 고지와 전문 내부어 비의존을 확인했다.
- 실행 deck harness에서 고정 화면 정·역방향 wheel 7장, 긴 관성 한 장 제한, cursor 이동 없는 다음 intent, 키보드·버튼·Home/End·clamp와 06 진입을 확인했다.
- Product DOM harness에서 `60 → 999 → 서로 다름 → 숫자 숨김 → HOLD → 복원`과 세 control을 유지했다.
- Product DOM harness에서 세 고장 대응 method의 쉬운 이름·문제·대응·대가와 production runtime exact 값을 실행 검증했다.
- H11/H12의 idle release timer는 다시 추가하지 않았다. H14 controller는 fixed `movedAt`과 새 impulse 조건을 사용한다.
- Workstream 90 H09 instruction의 네 안전장치, `47/0` 범위와 Product 04 연결 label을 exact 대조했다. H09 실제 산출물은 병렬 작업 상태라 최종 제출 뒤 재대조가 필요하다.
- `demo/index.html` H14 SHA-256: `7d518be78acfd4e3b76f1c1be4044b72a3d78bbbc5b7ebfcb6663e632f3b4c9d`.
- 실제 발표 장치의 stationary-cursor wheel 01↔07, trackpad 관성, 1280×720·1440×900 viewport와 console warning/error는 `NOT_EVALUATED`다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H14는 `READY_FOR_REVIEW` 상한을 지키며 commit·push·통합 판정을 수행하지 않는다.

## H13 Actual Wheel and Plain-Language Remediation — 2026-08-20

### wheel lifecycle 재진단과 구조 변경

- H11/H12 controller는 `delta`, `locked`, `releaseTimer`를 두고 마지막 유효 wheel event 이후 180ms가 지나야 잠금을 해제했다.
- 실제 마우스·트랙패드의 잔여 또는 관성 event와 다음 독립 입력 사이가 180ms보다 짧으면 timer가 계속 재설정되어 `locked=true`가 유지된다. cursor 이동은 controller의 해제 조건이 아니며, 사용자가 커서를 움직이는 동안 우연히 충분한 무입력 시간이 생겨 다시 반응한 것으로 보일 수 있다.
- wheel event 자체에는 모든 장치에서 공통으로 쓸 수 있는 제스처 종료 phase가 없으므로 H12의 zero/noise cutoff나 임의 multiplier/timer를 다시 조정하지 않았다.
- 앱의 wheel listener, `preventDefault`, delta 정규화, lock/timer 상태 머신을 전부 제거했다.
- root scroller에 `scroll-snap-type: y mandatory`, 각 7개 화면에 `scroll-snap-align: start`와 `scroll-snap-stop: always`를 적용했다. 장치 lifecycle과 관성 처리는 브라우저의 native scroll에 맡기고 앱은 정착한 가장 가까운 화면에 진행 표시만 맞춘다.
- 키보드 Arrow/Page Up/Page Down/Space/Home/End, 하단 버튼, 01·07 clamp는 `scrollIntoView()` 기반으로 유지한다. pointermove·hover·focus 변화는 어떤 re-arm 조건에도 쓰지 않는다.

### 초심자용 `04 · 숫자 변경 감지`

- 화면 순서를 `검토 조건 → 수치 변화 → 보증 판단 → 숫자 변경 감지`로 정리했다.
- 질문은 `계산 뒤 숫자가 바뀌면 어떻게 할까요?`, 중심 문장은 `계산 직후 기록과 화면에 들어온 값이 다르면, 숫자를 숨기고 판단을 보류합니다.`로 표시한다.
- 세 카드는 `01 · 계산 직후 기록 — 60초`, `02 · 화면에 들어온 값 — 테스트용 사본 999초`, `03 · 처리 결과 — 서로 다름 → 숫자 숨김 → 판단 보류(HOLD)`만 주 흐름으로 보여 준다.
- control은 Workstream 90 H08과 exact하게 `테스트용 숫자 바꾸기 → 두 기록 비교하기 → 정상 상태로 되돌리기`를 사용한다.
- `결과 검증`, integrity, assurance attack, consumer, preimage, hash, result/input/output ID, sibling anchor, reason code는 주 화면 설명에서 제거했다. 기존 H10 기술 경로 확인에 필요한 값은 접힌 `기술 상세`에만 남겼다.
- H10 `buildWatchdogAttackPayload()`·`createAttackDemoController()`와 H09 `resolveProductData()`를 그대로 재사용했다. 새 검증기·공식·정책·hash 규칙은 추가하지 않았다.
- 확인 범위는 Product가 계산 모듈에서 받은 결과 파일의 부분 불일치를 그대로 표시하지 않는지에 한정된다. 60초의 과학 정확성, 실제 방사선 assurance, 프로젝트 전체 무결성·보안, 전자서명과 GCP 보안은 검증하지 않는다.

### H13 검증 상태

- Product 13 tests 통과: H08 canonical parity, H09 signed-zero, H10 controller/Reset, H12 4단계 분리와 runtime fail-closed 회귀를 유지했다.
- native scroll harness에서 같은 화면 좌표를 전제로 pointermove 0회인 6회 정방향 snap `01→02→03→04→05→06→07`과 6회 역방향 snap `07→06→05→04→03→02→01`을 실행했다. 앱 wheel/pointer listener가 0이고 한 native snap이 한 화면만 갱신됨을 확인했다.
- 같은 harness에서 버튼·Arrow·Page Up/Down·Space·Home/End와 양 끝 clamp, 기존 snapshot을 실행했다.
- Product DOM harness에서 `60초 → 999초 → 서로 다름 → 숫자 숨김 → HOLD → 60초 복원`과 세 control label을 실행했다.
- Workstream 90 H08 실제 runbook의 화면명·중심 문장·카드명·control·처리 문구와 exact 대조했다.
- `demo/index.html` H13 SHA-256: `1f5b7aa6810b12ec75936d05509924faac5edf584d7f342df82decfa895a3ded`.
- 이 자동 harness는 실제 wheel hardware와 Chrome native scroll-snap 동작을 증명하지 않는다. 현재 작업 환경에서 `file://` URL 직접 조작은 browser policy로 허용되지 않아 실제 stationary-cursor 01↔07 왕복, 장시간 trackpad 관성 1장 제한, 1280×720·1440×900 viewport와 console warning/error는 `NOT_EVALUATED`다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H13은 `READY_FOR_REVIEW` 상한을 지키며 commit·push·통합 판정을 수행하지 않는다.

## H12 Beginner Result Integrity Screen — 2026-08-20

### Product 정보 구조와 초심자 화면

- Product stepper를 `검토 조건 → 수치 변화 → 보증 판단 → 결과 검증`의 네 단계로 확장했다.
- `02 수치 변화`에는 `방사선 수치 / Runtime 완화`만 남기고 `Assurance 공격` mode와 공격 panel을 완전히 제거했다.
- `03 보증 판단`의 “그렇다면 화면에 들어온 결과 자체를 믿어도 될까요?” control로 독립 `04 결과 검증` 화면에 진입한다.
- 4번 화면은 `정상 계산 결과 → 변경된 테스트 결과 → Product 판단` 세 카드와 `결과 숫자 바꾸기 → 원래 계산 기록과 대조 → 정상 결과로 되돌리기` control을 사용한다.
- WATCHDOG는 `자동 복구 감시 기능(WATCHDOG)`, downtime은 재시작·복구 동안 서비스를 사용할 수 없는 합성 시간으로 설명한다.
- `60 → 999초`는 실제 중단 시간이나 새 계산이 아니라 원본을 보존한 테스트용 사본에서 결과 파일 숫자 하나가 잘못 바뀐 상황을 재현하는 값이라고 바로 표시한다.
- 차단 상태는 `결과 사용 불가(DATA_UNAVAILABLE) / 평가하지 않음(NOT_EVALUATED) / 판단 보류(HOLD)`의 한국어 우선 순서다. reason code와 preimage/hash 내부어는 접힌 `기술 상세`에만 둔다.

### 기존 H10 경로 재사용

- 고정 변경은 기존 `buildWatchdogAttackPayload()`가 원본 deep clone의 WATCHDOG downtime만 `60 → 999`로 바꾼다.
- 단계 controller는 기존 `createAttackDemoController()`를 그대로 사용한다.
- 대조는 기존 H09 `resolveProductData()`와 runtime preimage verification path를 그대로 호출한다.
- 새 검증기, WATCHDOG/TMR/SEL 공식, 정책 threshold, hash 생성 또는 assurance 판단을 추가하지 않았다.
- 차단 뒤 WATCHDOG projection·result ID·input/output hash는 비노출되고 exact reason은 `RUNTIME_PREIMAGE_VALUE_MISMATCH`; TMR·SEL과 radiation residual은 유지된다.

### 추가 wheel 결함 원인과 수정

- H11 controller는 `deltaY=0`과 같은 무의미한 trailing wheel event도 release timer를 계속 뒤로 미뤘다. 일부 `file://` 브라우저/마우스 조합에서는 실제 wheel 동작이 끝난 뒤에도 이 event가 이어져 lock이 해제되지 않고, cursor 이동 뒤 event stream이 달라질 때만 다시 반응하는 것처럼 보일 수 있다.
- 유효 입력 절댓값이 1 미만인 zero/noise는 gesture 생명주기를 연장하지 않도록 변경했다.
- `deltaMode`가 line이면 16, page이면 100의 UI 이동 단위로 정규화하고 pixel mode는 원값을 사용한다. 이는 물리 계산이 아닌 입력 장치 event 단위 정규화다.
- 유효한 trackpad 관성 stream은 기존처럼 마지막 유효 event 뒤 180ms까지 한 gesture로 잠겨 여러 화면을 건너뛰지 않는다.
- 동일 좌표에서 pointermove 없이 line-mode `deltaY=3` gesture와 zero trailing event를 반복해 `01→02→03→04`, 이어서 `04→03→02→01`을 한 화면씩 이동하는 회귀를 추가했다.

### H12 검증 상태

- Product DOM harness에서 버튼으로 1→2→3→4, 4→3, Home/End, 숫자키 4, Alt+방향키, Reset을 실행했다.
- 같은 harness에서 정상 `60초 → 테스트 999초 → 원래 기록 불일치 → 비노출/HOLD → 정상 60초 Reset`과 세 control label을 확인했다.
- H08~H10 controller/consumer, H11 900ms 관성 공격, 모든 deck 입력과 snapshot 회귀를 Product suite에서 유지한다.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding`: H11 기존 12개를 포함한 13 tests 통과.
- H12 wheel 보완 뒤 `demo/index.html` SHA-256은 `99d8d1088fc330afdb24b878b750ad516a2bbd359306f91cf8de122f1c70ae22`; 생성 JSON/JS hash는 H10 기준선과 동일하다.
- Workstream 90 H07 actual 문서와 화면 순서, 세 control, `원래 기록과 불일치`, 세 한국어 우선 상태를 exact 대조했다.
- 실제 `file://` 브라우저는 이 작업 환경의 URL policy 때문에 자동 조작할 수 없다. 정책상 다른 browser surface나 localhost로 우회하지 않으며 실제 재현, 세 viewport, 전체 왕복과 console error 0은 review 필수다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H12는 `READY_FOR_REVIEW` 상한을 지키며 commit·push·통합 판정을 수행하지 않는다.

## H11 기준 상태

`READY_FOR_REVIEW — H11 Deck Beginner Clarity and Wheel Remediation`

H10 Product 공격 데모와 합성 snapshot을 유지하면서 발표 deck의 장시간 wheel·trackpad 관성 stream이 두 장을 넘길 수 있는 결함을 닫고, 03·04·06·07 화면의 초심자 오해 가능 문구를 최소 보완했다.

## H11 Deck Beginner Clarity and Wheel Remediation — 2026-08-20

### 구현

- 기존 wheel handler의 고정 `620ms` unlock을 제거하고 마지막 wheel 이벤트마다 release timer를 다시 잡는 gesture controller를 추가했다.
- threshold를 넘어 한 장 이동하면 controller가 잠기며, 이벤트 stream이 계속되는 동안에는 방향과 관계없이 추가 이동하지 않는다.
- 마지막 이벤트 후 `180ms` 무입력 구간이 지나야 delta와 lock이 초기화된다. 이후의 새 gesture만 다음 한 장을 이동한다.
- 다음·이전 버튼과 Arrow Right/Left, Page Down/Up, Space, Home, End 및 첫·마지막 장 clamp는 기존 동작을 유지한다. 특정 slide index 예외 분기는 없다.
- 03 화면은 `요구량 = 차폐 후 TID × 설계계수 2`, 등록된 `1/2/3/4 mm` 이산 lookup과 5 mm의 합성 table 범위 밖 의미를 명시한다.
- 04 화면은 `합성 fixture로 계산 가능`과 `실제 보증에는 근거 필요`를 한국어 우선으로 바꿨다.
- 06 화면은 `Engineering gate PASS`를 `합성 수치 조건 PASS · 보증 아님`, `Blocking gap`을 `승인을 막는 증거 공백`으로 좁히고, 다음 행동을 `부품 기술·정책상 필요한 파괴성 SEE별 근거 확보`로 한정했다.
- 07 화면은 로컬 데모의 실측 GCP resource·호출·비용만 0이며 실제 배포 시 저장·실행·로그·전송 비용 측정이 필요함을 명시한다.

### H11 검증

- 실행 기반 deck harness에서 100ms 간격 wheel 이벤트 10개, 총 900ms 관성 stream은 `01 → 02` 한 번만 이동했다. 같은 stream의 반대 방향 노이즈는 `02`를 유지했다.
- 마지막 이벤트 후 181ms 무입력 뒤 새 wheel gesture는 `02 → 03`으로 정확히 한 장 이동했다.
- 다음/이전 버튼, Arrow/Page/Space/Home/End와 양 끝 clamp를 같은 harness에서 검증한다.
- snapshot run ID 5개, `1/2/4/5 mm`, ECC `0.0063072/0.063072`, `OUT_OF_MODEL_SCOPE`, `SYNTHETIC`, `HOLD` 존재와 새 deck SHA-256을 고정 테스트로 확인한다.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding`: H10 기존 11개를 포함한 12 tests 통과.
- 새 deck SHA-256은 `fe340836edeec64b451bb4242be044981b2397b7bd2941aa695c51d202fa5cde`이며 Product test 기대값으로 고정했다.
- 실제 `file://` 브라우저는 작업 환경 URL policy 때문에 자동 조작할 수 없다. localhost나 다른 browser surface로 우회하지 않으며 1280×720·1440×900·1920×1080, horizontal overflow와 console warning/error 0은 review에서 확인해야 한다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H11은 `READY_FOR_REVIEW` 상한을 지키며 commit·push·통합 판정을 수행하지 않는다.

## H10 기준 상태

`VERIFIED — H10 Assurance Attack Demo`

H09의 production canonical preimage와 fail-closed consumer를 그대로 호출하는 60~90초 조작형 공격 데모를 Product UI에 추가했다. WATCHDOG deep clone의 downtime만 `60 → 999`로 바꾸고 preimage·result hash·sibling anchor를 유지하면 해당 record만 수치·ID·hash를 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫힌다.

## H10 Control Tower 독립 검증 — 2026-08-20

- 변경 범위가 `demo/product.html`, `demo/README.md`, Product 테스트와 Workstream 80 문서에 한정되고 exporter·생성 JSON/JS·발표 HTML·공통 schema·engine·Assurance 파일은 변경하지 않았음을 확인했다.
- Product binding 11개 테스트를 재실행해 H10 controller·Reset, H09 signed-zero, H08 canonical number parity·stale-hash, JavaScript syntax, exporter byte determinism과 JSON/wrapper exact를 모두 통과했다.
- 생성 payload와 동결 발표 HTML의 SHA-256이 기준선과 동일하고 `git diff --check`가 통과했다.
- 실제 브라우저 1280×720·1440×900에서 `Assurance 공격 → 공격 입력 만들기 → 동일 consumer로 검증 → 정상 원본으로 Reset`을 직접 실행했다. 정상 `1 / 1 / 60 s`, 공격 입력 `60 → 999 s`, 차단 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, reason `RUNTIME_PREIMAGE_VALUE_MISMATCH`, 수치·ID·hash 비노출과 TMR·SEL·방사선 residual 유지를 확인했다.
- 두 viewport 모두 horizontal overflow 0, 핵심 control viewport 내 노출, console warning/error 0이었고 Reset 뒤 정상 원본과 초기 control이 복원됐다.
- H10 Product 공격 데모 패키지만 `VERIFIED`다. 사람 리허설 시간은 여전히 `PLANNED 70초`이며 실제 environment·parts evidence·GCP resource는 0, 최종 assurance는 계속 `HOLD`다. 아직 commit·push하지 않았다.

## H10 Assurance Attack Demo — 2026-08-20

### 구현

- `수치 변화` 단계의 기본 정상 UI는 유지하고 발표자가 명시적으로 여는 `Assurance 공격` mode를 추가했다.
- 정상 WATCHDOG는 정규 payload에서 `false activation 1 / reboot 1 / downtime 60 s`, `VALID / NOT_EVALUATED / HOLD`와 result ID·input/output hash를 표시한다.
- `공격 입력 만들기`는 원본 payload를 직접 변경하지 않고 deep clone의 `computed_projection.downtime_total_seconds`만 `999`로 바꾼다. production preimage, result output hash와 sibling integrity anchor는 갱신하지 않는다.
- `동일 consumer로 검증`은 H09의 `resolveProductData()`를 그대로 호출한다. 별도 검증기, runtime 공식, hash 생성, policy threshold나 assurance 판정을 만들지 않는다.
- 차단된 WATCHDOG는 reason `RUNTIME_PREIMAGE_VALUE_MISMATCH`, projection `null`, result ID·input/output hash `—`로 렌더링된다. `999`는 `UNTRUSTED` 공격 입력 미리보기에만 나타난다.
- TMR·SEL 정상 record와 H05 방사선 residual은 유지되며, 공격 mode Reset은 byte 불변 원본 model로 돌아간다. 전역 데모 초기화는 기존 1단계 정상 UI로 복귀한다.

### H10 검증

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding`: 기존 10개를 포함한 11 tests 통과.
- 같은 suite에서 정상 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32`, 고정 `60 → 999` 공격, exact reason, WATCHDOG 비노출, TMR·SEL·radiation residual 유지와 Reset 복원을 실행했다.
- 공격 전후 전역 source의 `JSON.stringify()` exact equality, clone 분리, mutation을 되돌린 clone과 원본의 exact equality, preimage·result hash·sibling anchor 불변을 확인했다.
- 저장 payload hash는 JSON `bb17e926f3c13dd5b37c12a4fc59826e2b061be7ee6ad45fe83675c30c0d6398`, JS wrapper `adc54afc2fcd1da792fc2cabc6079d16134e2557905b4d175e5007a576ad8a41`로 기준선과 동일하다.
- JavaScript syntax와 원격 runtime dependency 0, `git diff --check`, 발표 HTML SHA-256 `96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5`를 확인했다.
- 실제 브라우저의 `file://` 열기는 작업 환경 URL 정책에 의해 차단됐다. 정책상 localhost나 다른 브라우저 표면으로 우회하지 않았으며 1280×720·1440×900, console warning/error 0과 실제 클릭 동선은 review에서 확인해야 한다.
- 실제 사람 리허설 전 예상 동선은 `PLANNED 70초`: mode 진입·정상 설명 15초, 공격 입력 생성 15초, 동일 consumer 차단 25초, 영향 범위·Reset 15초.
- `CONTRACT_CHANGE_REQUEST`: 없음. H10은 `READY_FOR_REVIEW`이며 `VERIFIED/INTEGRATED`를 선언하지 않는다.

## H09 기준 상태

`INTEGRATED — H09 Signed Zero Integrity / commit 32b6131`

H08의 production canonical preimage 방식과 numeric parity를 유지하면서 deep number comparison이 `+0/-0` 변조를 허용하던 결함을 H09로 보완했다. JSON number 비교는 `Object.is()`만 사용하며 signed zero가 다르면 대상 runtime record만 fail-closed한다.

## H09 Control Tower 독립 검증 — 2026-08-20

- 수정 범위가 `demo/product.html`, Product 테스트, README와 Workstream 80 문서에 한정되고 exporter·생성 JSON/JS·발표 HTML·공통 schema·runtime engine·Assurance 파일은 변경하지 않았음을 확인했다.
- Product binding 10개 테스트를 재실행해 기존 H08 numeric parity·stale-hash 공격, exporter byte determinism, JSON/wrapper exact, JavaScript syntax와 원격 dependency 0을 포함해 모두 통과했다.
- WATCHDOG result의 `true_target_event_count`만 `+0 → -0`으로 바꾸고 production preimage·result hash·sibling anchor를 유지한 직접 공격은 `RUNTIME_PREIMAGE_VALUE_MISMATCH`로 종료됐다. 대상 record는 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`였고 TMR과 H05 radiation residual `0.013072`는 유지됐다.
- 반대 방향 `-0 → +0`, 정상 negative-zero control과 H08 `p=0.001`·1e-6 경계 아래·위·1e-7 controls도 Product suite에서 통과했다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32`, 세 method의 `NOT_EVALUATED / HOLD`와 warning/error 0을 확인했다.
- H09는 공통 계약이나 engine을 바꾸지 않았으므로 지침에 따라 schema·simulation·environment·assurance 전체 회귀는 반복하지 않았다.

### 판정

H09 Signed Zero Integrity 패키지는 독립 검증 후 commit `32b6131`로 `INTEGRATED`됐다. H05 Product binding의 기존 `VERIFIED`, H07 발표 note와 H08 production canonical preimage 보완을 유지한다. Stage 8 완료를 의미하지 않으며 실제 environment·parts evidence와 GCP resource는 여전히 0, 최종 assurance는 `HOLD`다.

## H09 Signed Zero Integrity — 2026-08-20

### 구현

- `demo/product.html`의 `jsonDeepExact()` number 비교에서 `Object.is(left, right) || left === right`를 `Object.is(left, right)`로 교체했다.
- 일반 finite number와 같은 부호의 zero는 그대로 통과하고 `Object.is(+0, -0) === false`인 signed-zero 차이만 거부한다.
- Exporter, 생성 JSON/JS, `demo/index.html`, runtime calculator와 공통 계약은 변경하지 않았다.
- 브라우저는 runtime 계산식과 policy threshold를 재구현하지 않는다.

### 재현과 공격 결과

- 수정 전 WATCHDOG `computed_projection.true_target_event_count`만 `+0 → -0`으로 바꾸고 production preimage·result output hash·sibling anchor를 유지하면 `ready=true / VALID / HOLD`로 수용됐다.
- 수정 후 같은 공격은 WATCHDOG만 `ready=false`, `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`로 닫힌다.
- test-only direct record에서 preimage와 result가 모두 `-0.0/-0`인 정상 control은 `ready=true / HOLD`다. 이 control의 result만 `-0 → +0`으로 바꾸면 대상 record가 fail-closed한다.
- 두 공격 모두 다른 TMR/SEL record와 H05 radiation residual `0.013072`를 유지한다.
- H08 result/preimage 동시 변조, format-valid fake hash, `p=0.001`, 1e-6 아래·위, 1e-7 및 negative-zero input controls는 계속 통과한다.

### H09 검증

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding`: 10 tests 통과.
- JavaScript syntax, 원격 runtime dependency 0, exporter byte-identical, JSON/wrapper exact와 H08/H07 회귀를 같은 Product suite에서 확인했다.
- 수정 후 직접 재현에서 공격 WATCHDOG `ready=false`, TMR `ready=true`, H05 radiation residual `0.013072`를 관측했다.
- 지침에 따라 schema·simulation·environment·assurance 전체 회귀는 반복하지 않았다.
- 실제 browser 재확인은 작업 채팅의 `file://` URL 제약 때문에 미실행이다. H08 Control Tower가 검증한 정상 WATCHDOG/TMR/SEL 조작과 warning/error 0은 유지되며 H09 review에서 signed-zero 보완 후 실제 브라우저 재확인이 필요하다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H08 Control Tower 독립 검증 — 2026-08-20

- Product binding 10개 테스트, `p=0.001`, 1e-6 경계 아래·위, 1e-7 계열, `-0.0` control, 제출된 stale-hash 공격, JavaScript syntax, 원격 dependency 0과 생성물 hash를 독립 재실행해 통과했다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32`와 세 record의 `VALID / NOT_EVALUATED / HOLD`, warning/error 0을 확인했다.
- 추가 numeric edge 공격에서 WATCHDOG result 본문의 `true_target_event_count`만 `0`에서 `-0`으로 바꾸고 기존 production preimage·output hash·sibling anchor를 유지해도 consumer가 `ready=true`로 수용했다.
- 원인은 `jsonDeepExact()`의 number 비교가 `Object.is(left, right) || left === right`여서 `Object.is(0, -0)`의 불일치를 뒤의 `0 === -0`이 다시 허용하기 때문이다. 제출된 negative-zero control은 정상 결과가 통과하는지만 확인하고 `+0/-0` 본문 변조는 공격하지 않는다.
- 최종 assurance는 계속 `HOLD`라 낙관적 PASS로 승격되지는 않았지만, H08 필수 조건인 result 본문 변조 fail-closed와 production preimage exact binding을 충족하지 못한다.

### 판정

H08은 `CHANGES_REQUESTED`다. H05 Product binding의 기존 `VERIFIED`와 H07의 발표 note·stale-hash 보완 결과는 유지한다. H09에서는 JSON number 비교의 `+0/-0` 구분과 해당 공격 회귀만 직접 보완하며 전체 저장소 회귀는 반복하지 않는다.

## H08 Cross-runtime Canonical Number Parity — 2026-08-20

### 구현

- `demo/build_product_data.py`가 runtime result의 root `output_hash`를 제외한 객체를 Workstream 20의 `canonical_runtime_json()`으로 직렬화해 `integrity.output_hash_preimage`에 보존한다.
- JSON과 `file://` wrapper는 같은 payload에서 함께 생성되므로 preimage를 별도로 손으로 관리하지 않는다.
- `demo/product.html`은 Python number lexical form을 재구성하지 않는다. preimage UTF-8 SHA-256과 `result.output_hash`, preimage parsed value와 result body, sibling result/input/output anchor를 모두 독립 확인한다.
- 실패는 해당 method record만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫고 projection·result ID·input/output hash를 숨긴다. 다른 정상 runtime record와 H05 radiation 결과는 유지된다.
- 브라우저는 WATCHDOG/TMR/SEL 공식이나 policy threshold를 계산하지 않는다.
- H07에서 검증된 `demo/index.html`은 변경하지 않았다.

### Numeric parity control

| control | production projection | production/browser hash | consumer |
|---|---:|---|---|
| TMR `p=0.001` | `2.998e-06` | `sha256:f52eb2e2966c9e188d576a4bb24e47bb9d47743c9b89b34fe0461ce9868c9d76` | `ready=true / HOLD` |
| TMR `p=0.0005` | `7.4975e-07` | `sha256:15b26c811b5db8755ffbc5a14572d815aaad60bce7649b98081ce8f83b8ca73d` | `ready=true / HOLD` |
| TMR `p=0.0006` | `1.079568e-06` | `sha256:5a1f580fed38afadb8247a027333c566ed31a7afa9e393326e2ed19601a6a13b` | `ready=true / HOLD` |
| TMR `p=0.0002` | `1.19984e-07` | `sha256:a4000ff7b4206550fdee7843a970ef408389fae34b9fbc73cb7dd5d89076ddb5` | `ready=true / HOLD` |
| TMR `p=-0.0` | `0.0` | `sha256:2ff8447baf939c6092f9a2970ea7a57e208b9d051630bcce0b57fada5d19842e` | `ready=true / HOLD` |

`number` schema minimum 0은 `-0.0`을 유효 numeric value로 받아들이며 engine도 `VALID`와 projection `0.0`을 생성한다. 기존 WATCHDOG preimage는 integer-valued float `60.0`과 `0.0` lexical form을 명시적으로 보존한다.

### 공격 결과

- result 본문만 변조하고 preimage/hash 유지, preimage만 변조하고 result 유지, result와 preimage를 함께 변조하고 stale hash 유지, result·preimage·sibling hash에 같은 임의 format-valid hash 주입을 모두 대상 record `ready=false`로 닫는다.
- 실패 record는 projection `null`, result ID와 input/output hash `—`, assurance `HOLD`다.
- result object key 순서만 바꾼 동일 JSON value는 preimage parsed value와 deep exact match하므로 정상 통과한다.
- 모든 개별 공격에서 Product model과 H05 radiation residual은 정상 유지된다.

### 검증 상태

- Product binding 10 tests 통과: exporter 2회 byte-identical, JSON/wrapper exact, production API/schema exact, numeric parity 5 controls, preimage mutation 공격, JavaScript syntax, 원격 dependency 0, H07 발표 HTML SHA-256 회귀 포함.
- schema 14개, valid fixture 5개, invalid fixture 116개 통과.
- simulation 55 tests, environment 23 tests, raw-manifest preflight 2 tests 통과.
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 공격 실행 47개, control 4개, failure 0, false pass 0, `NOT_EVALUATED` 1.
- 생성 JSON SHA-256 `bb17e926f3c13dd5b37c12a4fc59826e2b061be7ee6ad45fe83675c30c0d6398`, JS SHA-256 `adc54afc2fcd1da792fc2cabc6079d16134e2557905b4d175e5007a576ad8a41`.
- H08에서 변경하지 않은 발표 HTML SHA-256 `96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5`.
- `git diff --check` 통과.
- 실제 browser 재확인은 작업 채팅의 `file://` URL 제약 때문에 미실행이다. H07 Control Tower가 검증한 세 runtime method·warning/error 0과 세 viewport 기준에서 `demo/index.html`은 H08 동안 byte 불변이다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공통 canonical contract를 변경하지 않고 production preimage를 Product payload 보조자료로 사용했다.

## H07 Control Tower 독립 검증 — 2026-08-20

- 제출된 stale projection·policy·stable code·anchor·format-valid fake hash 공격은 모두 대상 record를 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫았고, 정상 고정 WATCHDOG·TMR·SEL control은 production hash와 일치했다.
- Product 9개, schema 14/5/116, simulation 55개, environment 23개, raw-manifest preflight 2개를 재실행해 모두 통과했다.
- assurance manifest 1.2.0은 22 case 중 21개 평가, 공격 실행 47개, control 4개, failure 0, False PASS 0이며 실제 GCP `ASR-D02` 1개는 `NOT_EVALUATED`다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32` 전환과 `VALID / NOT_EVALUATED / HOLD`, warning/error 0을 확인했다.
- 발표용 `.slide4-note`는 1280×720, 1440×900, 1920×1080 모두 line count 1, document horizontal overflow 0이었다.
- 추가 유효 경계값 TMR `p=0.001`은 production에서 `processing_status=VALID`, result schema error 0, projection `2.998e-06`과 output hash `sha256:f52e...d76`을 생성했다. 브라우저는 같은 number를 `0.000002998`로 직렬화해 `sha256:e7e2...791`을 계산하고 정상 record를 `ready=false`로 거부했다.
- 원인은 Python과 JavaScript의 JSON number lexical representation 차이이며, 현재 path별 integer-to-float 보정만으로 production canonical bytes를 일반적으로 재현할 수 없다.

### 판정

H07은 `CHANGES_REQUESTED`다. stale-hash False PASS와 발표 문구 줄바꿈은 해소됐지만 schema-valid production result를 오탐 거부하는 canonical parity 결함이 남아 있다. H05의 기존 `VERIFIED` 기준선은 유지한다.

## H07 Runtime Result Integrity Remediation — 2026-08-20

### 구현

- `demo/product.html`이 root `output_hash`를 제외한 runtime result 본문을 재귀 key 정렬, compact separator, UTF-8 규칙으로 canonicalize하고 self-contained SHA-256으로 검증한다.
- 재계산 content hash와 `result.output_hash` 비교가 필수이며 sibling integrity anchor는 보조 검사로 유지한다.
- 정적 runtime 영역은 검증 전부터 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, 수치·ID·hash `—`로 시작한다. 정상 검증을 통과한 record만 화면 model에 투영된다.
- 개별 record 검증 실패는 해당 method만 닫으며 다른 정상 runtime record와 H05 radiation result는 유지한다.
- WATCHDOG/TMR/SEL 계산식, downtime 합산, policy threshold는 브라우저에서 계산하지 않는다.
- `demo/index.html`의 지정 안내 문구에 `slide4-note` class를 부여해 공통 `.lead`를 바꾸지 않고 desktop에서 `max-width:none; white-space:nowrap`을 적용했다. 900 px 이하에서는 안전한 줄바꿈을 허용한다.

### 결함 재현과 공격 결과

- 수정 전: WATCHDOG `downtime_total_seconds`만 `60 → 999`로 바꾸고 기존 result/sibling hash를 유지하면 `ready=true`, `downtime=999`가 관측됐다.
- 수정 후 projection 본문만 변조, policy만 변조, stable code만 변조, projection+sibling anchor 변조, projection+result/sibling hash를 같은 format-valid 가짜 값으로 변조한 경우 모두 대상 record가 `ready=false`로 닫혔다.
- 실패 record는 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`로 관측됐다.
- runtime result의 object key 순서만 역전한 동일 content는 세 canonical production hash와 일치하며 정상 통과했다.

### H07 검증 결과

- Product binding 9 tests 통과. exporter 2회 byte-identical, JSON/wrapper 동일성, production API/schema exact match, canonical content hash, 모든 H07 mutation과 검증 전 정적 비노출을 포함한다.
- schema 14개, valid fixture 5개, invalid fixture 116개 통과.
- simulation 55 tests, environment 23 tests, raw-manifest preflight 2 tests 통과.
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 공격 실행 47개, control 4개, failure 0, false pass 0, `NOT_EVALUATED` 1.
- JavaScript syntax와 원격 runtime dependency 0 검사 통과.
- `git diff --check` 통과.
- 생성 JSON SHA-256 `83275c83ad1dd1f6e81a0b372c4c5f6a45760fa2d4ba279e52481531f14078d9`, JS SHA-256 `c63565b46438200da5df82d4b8c810adbb7a260efc6bd8f8097416a22cf75c97`.
- 변경된 발표 HTML SHA-256 `96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5`.

### 작업 채팅 미실행 항목과 Control Tower 보완

- 작업 채팅은 로컬 `file://` 보안 정책 때문에 실제 viewport·console을 재현하지 못했지만, Control Tower가 `demo/`만 임시 localhost로 제공해 독립 검증했다.
- 세 desktop viewport의 `.slide4-note` line count 1, horizontal overflow 0과 Product UI warning/error 0은 확인됐다.
- 남은 제한은 실제 browser viewport가 아니라 위 Python/JavaScript canonical number parity다.
- `CONTRACT_CHANGE_REQUEST`: 없음. production runtime calculator, schema, Assurance 파일은 읽기 전용으로 유지했다.

## H06 Control Tower 독립 검증 — 2026-08-20

- Product binding 9개, schema 14/5/116, simulation 55개, environment 23개, raw-manifest preflight 2개를 재실행해 모두 통과했다.
- assurance manifest 1.2.0은 22 case 중 21개 평가, 공격 실행 47개, control 4개, failure 0, False PASS 0이며 실제 GCP `ASR-D02` 1개는 `NOT_EVALUATED`다.
- WATCHDOG record의 `computed_projection.downtime_total_seconds`만 `60`에서 `999`로 바꾸고 기존 `result.output_hash`와 sibling integrity anchor를 그대로 둔 독립 공격에서 UI consumer가 `ready=true`와 변조된 `999`를 반환했다.
- 현재 consumer는 sibling anchor와 result의 hash 문자열이 같은지만 확인하고 runtime result 본문으로부터 canonical SHA-256을 다시 계산하지 않는다. 따라서 형식상 정상인 stale hash가 content integrity를 증명하지 못한다.
- 보완 회차는 브라우저에서 production canonical 규칙으로 본문 hash를 독립 검증하고, 검증 전 수치를 렌더링하지 않으며, 실패 record만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫아야 한다.
- 발표용 `demo/index.html`의 SEL·SEB·SEGR 근거 안내 문구는 넓은 화면에서 한 줄로 보이도록 전용 text box 폭도 함께 보완한다.

### 판정

H06는 `CHANGES_REQUESTED`다. H05 Product result binding의 `VERIFIED` 기준선에는 영향을 주지 않으며, 수정 회차도 완료 상태 상한은 `READY_FOR_REVIEW`다.

## H06 Runtime Mitigation Result Binding — 2026-08-20

### 구현

- `demo/build_product_data.py`가 `evaluate_runtime_mitigation()`을 세 Workstream 20 fixture에 직접 호출한다.
- 기존 H05 payload에 명시적 `runtime_mitigation_results` collection을 추가하고 각 record에 fixture reference, 필요한 control input, integrity anchor와 production result 전체를 보존한다.
- result에는 method, equation ID, result ID, processing/engineering/assurance, data class, normalized counts, computed/declared projection 비교, policy evaluation, stable error codes, input/output hash가 원형 그대로 들어간다.
- Product UI의 “수치 변화” 단계에 `방사선 수치 / Runtime 완화` 보기를 추가했다. 기존 방사선 경로는 기본값으로 유지하고 runtime 보기에서 WATCHDOG·TMR·SEL 보호를 선택한다.
- 세 runtime 결과 모두 수치 바로 위에 `SYNTHETIC / NOT_EVALUATED / HOLD`를 표시한다. `VALID` 계산 결과를 assurance support로 표현하지 않는다.
- stable error code는 사람이 읽는 다음 행동과 짝지어 표시하지만 새 판정·근거·추천을 만들지 않는다.
- 브라우저는 production projection을 포맷해 표시할 뿐 WATCHDOG/TMR 공식, downtime 합산, policy threshold를 재계산하지 않는다.

### 정규 runtime 기준선

| method | equation / result | projection | 상태 |
|---|---|---|---|
| WATCHDOG | `WATCHDOG_TRUE_FALSE_PATH_V1` / `runtime-56ed7f4695cfe899` | false activation 1, reboot 1, downtime 60 s | `VALID / NOT_EVALUATED / HOLD` |
| TMR | `TMR_3P2_MINUS_2P3_V1` / `runtime-14be42f0ba024e6a` | p=0.1, system failure probability 0.028 | `VALID / NOT_EVALUATED / HOLD` |
| SEL_PROTECTION | `SEL_TRUE_FALSE_PATH_V1` / `runtime-6363f78ef979b057` | true 1 + false 1, power cycles 2, downtime 32 s | `VALID / NOT_EVALUATED / HOLD` |

세 record의 `data_class`는 `SYNTHETIC`이다. policy는 `DRAFT`, approval/evidence eligibility는 false이며 stable codes는 `BLOCKING_EVIDENCE_GAP`, `MITIGATION_APPLICABILITY_UNRESOLVED`, `NON_EVIDENTIARY_MITIGATION`, `NON_EVIDENTIARY_POLICY`, `POLICY_NOT_APPROVED`다.

### Fail-closed binding

- collection 누락·method set 불일치·unknown method는 runtime collection 전체를 unavailable로 처리한다.
- 개별 record의 schema/runtime version, engine, method, result/equation ID, projection, declared comparison, policy summary, status/data class, stable codes, input/output hash 또는 integrity anchor가 손상되면 해당 record의 수치·ID·hash를 숨긴다.
- 모든 runtime fallback은 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`이며 다른 정상 record와 기존 H05 radiation result는 유지된다.
- Runtime result ID·hash·projection은 HTML에 중복 하드코딩하지 않는다.

### H06 테스트 범위

- exporter 2회 byte-identical과 저장 JSON/JS exact match
- JSON-wrapper payload 동일성
- 세 runtime result schema 통과
- production API 재호출 결과와 payload result/projection/ID/hash exact match
- WATCHDOG·TMR·SEL exact control 값 검증
- UI consumer의 세 method 선택 model과 metrics 투영
- collection 누락, 개별 projection 손상, unknown method, valid-shape hash 변조, optimistic assurance, schema version drift 공격의 fail-closed 결과
- 기존 MVP/scope/EvidencePacket/Change Impact H05 테스트 유지
- JavaScript syntax, 원격 runtime dependency 0, 발표용 `demo/index.html` SHA-256 불변

### H06 실행 결과

- Product binding 9 tests 통과
- schema 14개, valid fixture 5개, invalid fixture 116개 통과
- simulation 55 tests 통과(그중 runtime calculator 24 tests 포함)
- environment 23 tests 통과
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 47 attack executions, 4 controls, failures 0, false passes 0, `NOT_EVALUATED` 1
- raw manifest preflight 2 tests 통과
- exporter 2회 JSON/JS 및 저장 artifact `cmp` 동일
- JSON SHA-256 `83275c83ad1dd1f6e81a0b372c4c5f6a45760fa2d4ba279e52481531f14078d9`
- JS SHA-256 `c63565b46438200da5df82d4b8c810adbb7a260efc6bd8f8097416a22cf75c97`
- `git diff --check` 통과
- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지

### 제한

- runtime 결과는 합성 fixture의 결정론적 control이며 실제 mitigation 성능이나 방사선 assurance 증거가 아니다.
- 자동 생성 정적 artifact이며 backend, 실제 evidence ingestion, GCP 저장은 없다.
- `CONTRACT_CHANGE_REQUEST`: 없음. Workstream 20 runtime calculator와 공통 schema는 읽기 전용으로 사용했다.

## H05 Product Result Binding — 2026-08-20

### 구현

- `demo/build_product_data.py`가 기존 `run_mvp_decision()`을 실행해 MVP baseline/variant 전체 결과를 보존한다.
- 같은 exporter가 기존 `run_simulation()`으로 1 mm, 4 mm, 범위 밖 5 mm scope 결과를 생성한다. 2 mm ECC OFF/ON은 MVP baseline/variant가 authoritative source이며 새 mitigation 계약을 예상하지 않는다.
- 하나의 payload를 key-sorted compact JSON으로 직렬화해 `demo/data/mvp-product-result.json`과 `globalThis.SPECTRA_MVP_PRODUCT_RESULT=...` wrapper를 함께 생성한다.
- exporter는 현재 시각, UUID, 머신별 절대 경로를 추가하지 않는다. engine fixture의 고정 `created_at`과 content-derived ID만 보존한다.
- `demo/product.html`은 로컬 wrapper를 읽어 case ID, baseline/variant, run/result ID, processing/engineering/assurance, TID/SEU metrics, blocking gaps, EvidencePacket ID, Change Impact ID와 invalidation을 표시한다.
- 브라우저는 값을 포맷하고 선택된 정규 record를 표시할 뿐 물리 계산·보간·외삽·임계값·정책 판정을 수행하지 않는다.
- payload 누락, 구조 손상, assurance 불변식 위반 또는 5 mm fail-closed 불변식 위반은 수치와 ID를 모두 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다.

### H05 생성 기준선

| 구분 | ID | processing | engineering | assurance | 주요 결과 |
|---|---|---|---|---|---|
| MVP 전체 | `mvp-cb826edb88ea5b67` | `VALID` | `NOT_EVALUATED` | `HOLD` | case `mvp-synthetic-ecc-policy-001` |
| baseline · 2 mm ECC OFF | `result-2ac48c19edb2f179` | `VALID` | `NOT_EVALUATED` | `HOLD` | TID 6.0, residual 0.063072 |
| variant · 2 mm ECC ON | `result-619f2bd08363a162` | `VALID` | `NOT_EVALUATED` | `HOLD` | TID 6.0, residual 0.013072 |
| scope · 1 mm ECC ON | `sim-d5a72077d684f459` | `VALID` | `PASS` | `HOLD` | TID 8.0 |
| scope · 4 mm ECC ON | `sim-ddf29f8ab807196d` | `VALID` | `PASS` | `HOLD` | TID 3.5 |
| scope · 5 mm ECC ON | `sim-27e031f2388ab6fc` | `OUT_OF_MODEL_SCOPE` | `NOT_EVALUATED` | `HOLD` | metrics 없음 |

MVP variant의 수치 규칙 일부는 `PASS`지만 aggregate `engineering_gate`는 `NOT_EVALUATED`이며 assurance는 `HOLD`다. H04의 수기 Stage 2 ECC snapshot `0.0063072`를 Product UI의 2 mm variant 결과로 더 이상 사용하지 않는다. 발표용 `demo/index.html`의 동결 snapshot은 변경하지 않는다.

### H05 자동 검증

- Workstream 80 전용 테스트는 exporter 2회 byte 동일성, JSON-wrapper payload 동일성, MVP/simulation schema와 EvidencePacket semantic gate, UI consumer의 실제 payload 투영, 누락·손상 fallback, authoritative ID·metrics 중복 하드코딩 금지, JavaScript syntax, 원격 런타임 의존성 0을 검증한다.
- 기준 커밋 clean archive에 H05 소유 파일만 적용한 독립 실행에서 Product binding 7개 테스트가 통과했다.
- 같은 clean archive의 schema, simulation, environment, assurance, raw-manifest preflight 전체 회귀 결과는 H05 handoff에 명령과 실제 결과를 기록한다.
- 작업 트리에는 H05 시작 전부터 다른 Workstream이 수정 중인 공통 schema가 있으며, H05는 이를 수정·복원하지 않았다. 현재 작업 트리 회귀와 clean-baseline 회귀는 분리해서 기록한다.
- 발표용 `demo/index.html` SHA-256은 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880`이다.

### 남은 제한

- 브라우저 viewport·console·실제 `file://` 조작은 이용 가능한 브라우저 제어 경로가 있을 때 재확인해야 한다.
- JSON/JS는 정적 build artifact이며 자동 refresh, backend, HTTP API, 실제 evidence ingestion은 없다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H05는 공통 계약을 변경하지 않았다.

## H04 초심자 가시성 보완 — 2026-08-20

### 정보 구조 변경

- 단계명을 `검토 조건 / 수치 변화 / 보증 판단`으로 한국어 우선 표시하고 영문은 보조 표기로 이동
- 각 단계 최상단에 5초 안에 읽는 질문과 한 문장 답 배치
  - “어떤 임무와 부품을 검토하나요?”
  - “차폐와 ECC가 어떤 값을 바꾸나요?”
  - “수치 조건을 통과해도 왜 HOLD인가요?”
- `차폐 후 누적선량(TID)`, `완화 전 오류(SEU)`, `완화 후 잔여 오류`처럼 용어 바로 옆에 한국어 뜻 표시
- 차폐·ECC·5 mm 조작 직후 다음 해석 문장을 수치 카드 위에 크게 갱신
  - TID `8 → 6 → 3.5 krad` 감소
  - ECC 잔여 SEU `0.063072 → 0.0063072` 감소
  - 5 mm는 지원 범위 밖이라 값 추정 안 함
- 보증 판단을 `합성 수치 조건 통과 → 실제 근거 부족 → 판단 보류(HOLD) → 증거 4가지 확보` 인과 흐름으로 연결
- 기존 5행 Evidence Coverage와 별도 Action Plan을 환경·BOM identity·시험 원문·파괴성 SEE의 `공백 ↔ 다음 행동` 네 쌍으로 통합
- run ID·model·합성 policy approval은 접힌 “기술 세부정보”로 이동

### 가독성 경계

- 핵심 질문 27px 이상, 답 16px 이상, 카드 제목·상태 13px 이상, 보조문구 12px 이상
- 10px는 footer의 비핵심 메타정보에만 사용하고 9px·11px 일반 텍스트 제거
- 보조색을 `#929ca4`로 높여 기본 배경 `#050607` 대비 계산값 7.26:1 확보
- 1280×720에서는 글자를 줄이지 않고 contract note·상세 설명·기술 상세 본문을 후순위로 숨김

### H04 자동 검증

- 질문 3/3, 동적 해석 핵심문 3/3, 기술 용어 인접 한국어 설명 확인
- 검증된 run ID 5/5 exact match, assurance `HOLD` 5/5
- JavaScript syntax 통과, remote request API·지원 판정 승격 token 0
- schema 14개·정상 fixture 3개·실패 fixture 83개 통과
- simulation 19개와 비교 scenario 통과
- assurance 21 case: 19 evaluated PASS, 2 `NOT_EVALUATED`, failure 0, false pass 0
- `git diff --check` 통과
- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- 1280×720·1440×900 overflow, interaction, Reset, console error: Chrome 검증 필요

### H04 Control Tower 독립 검증 — 2026-08-20

- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- `demo/product.html` inline script 2개 syntax 통과, 원격 reference 0, 고정 run ID 5개, 필수 한국어 label과 해석 문장 확인
- 9~11px 규칙은 footer용 10px 1개만 남고 핵심 문구에서 제거됨
- schema 14개·정상 fixture 3개·실패 fixture 83개 통과
- simulation 19개와 5개 합성 비교 scenario 통과
- assurance 21 case 중 19 evaluated, 2 `NOT_EVALUATED`, False PASS 0
- `git diff --check` 통과
- 사용자가 실제 UI의 단계 이동과 조작을 확인하고 현재 가시성을 프로토타입 기준선으로 수용함
- Workstream 90의 H02 준비 과정에서도 1·2·4·5 mm, ECC 미적용/적용, 단계 이동, Reset, 모든 최종 `HOLD`와 browser warning/error 0을 실제 조작으로 재확인함

실제 Chrome의 지정 viewport overflow는 Control Tower가 독립 캡처하지 못했다. console warning/error 0과 전체 조작은 Workstream 90의 H02 준비 과정에서 재확인했다. 이후 멘토링 피드백이 들어오면 같은 채팅 80에서 새 UI 작업 패키지로 개선한다.

발표용 `demo/index.html`은 동결하고, 별도 `demo/product.html`에 Evidence-to-Decision Workspace를 구현했다. H01·H02 검증 이력은 아래에 보존한다. H03의 기능·snapshot·fail-closed 정적 계약은 통과했지만 실제 viewport·interaction·console 검증이 없고, 도메인 초심자 관점에서 정보 위계와 가시성이 부족해 H04 보완 전에는 `READY_FOR_REVIEW`로 승격하지 않는다.

## H03 Control Tower Review — 2026-08-20

- `demo/product.html` 존재와 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지 확인
- inline script 2개 syntax 통과, 원격 reference 0, 고정 run ID 5개 확인
- schema 14개·정상 fixture 3개·실패 fixture 83개, simulation 19개, assurance 21 case 중 19 evaluated·2 `NOT_EVALUATED` 재실행 통과
- 1·2·4·5 mm, ECC ON/OFF, 최종 `HOLD`, JavaScript fallback 계약 확인
- 인앱 브라우저의 `file://` 접근이 보안 정책으로 차단되어 Control Tower의 실제 viewport·console 검증은 수행하지 못함
- 소스에 9~11px font-size 규칙이 15개 있고 영문 전문용어와 낮은 대비 보조문구가 많아, 주요 상태와 의미를 초심자가 빠르게 읽기 어렵다는 사용자 피드백을 재현 가능한 개선 요구로 수용

### H04 변경 방향

- 한국어 결론을 먼저 표시하고 영문 계약명은 보조로 둔다.
- 각 단계에서 “무엇을 입력했나 / 무엇이 달라졌나 / 왜 HOLD인가 / 다음에 무엇을 해야 하나” 중 하나를 가장 크게 보여 준다.
- 작은 글자·낮은 대비·동일한 카드 위계를 줄이고 기술 세부정보는 후순위로 이동한다.
- 발표용 `index.html`, 고정 snapshot과 fail-closed 동작은 변경하지 않는다.

## H03 Product UI Prototype

### 구현

- 슬라이드가 아닌 단일 application shell과 `Scenario → Analysis → Assurance` 3단계 workflow
- 합성 LEO 임무, 단일 부품 exact identity fixture, 승인 BOM 0건 표시
- 1·2·4·5 mm 차폐 선택과 2 mm 전용 ECC ON/OFF 비교
- 검증된 다섯 run만 소비하고 물리 계산·보간·외삽·판정을 브라우저에서 수행하지 않음
- 1·4·5 mm에서는 ECC OFF를 비활성화해 검증되지 않은 조합 생성 차단
- 5 mm는 값 없이 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`
- Evidence Coverage에서 실제 환경 출력, 승인 BOM, 시험 원문, 파괴성 SEE와 실제 policy approval 공백 노출
- 환경 출력 확보 → exact identity 확인 → 권리 확인 원문 연결 → 파괴성 SEE 근거/시험 계획의 Action Plan
- stepper·이전/다음·숫자키 1/2/3·Alt+방향키와 `Reset demo` 지원
- JavaScript 미실행 시 `SYNTHETIC / NOT PHYSICAL EVIDENCE / ASSURANCE: HOLD` 안전 fallback

### H03 자동 검증 — 2026-08-20

- `demo/product.html`: 3개 단계, 다섯 엔진 run ID와 표시값 exact match
- 외부 CDN·font·asset·network API 0, assurance 승격 token 0
- JavaScript syntax: bundled Node.js `--check` 통과
- `demo/index.html` SHA-256: `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py`: simulation 19개와 비교 scenario 통과
- `git diff --check`: 통과
- 1280×720·1440×900 overflow, 전체 조작, Reset, console error: 브라우저 검증 필요

기존 오프라인 HTML 데모의 사실·snapshot·조작 계약을 유지하면서 7분 발표용 한글 타이포그래피와 상태 표현을 정제했다. 별도 handoff는 없지만 Control Tower가 실제 산출물을 직접 재현해 H02 패키지를 검증했다. 이 판정은 발표 UI에 한정되며 Stage 8 전체 통합 완료를 뜻하지 않는다.

## H02 변경

- 한글 본문 stack을 `Apple SD Gothic Neo`, `Noto Sans KR`, system sans-serif 순서로 조정
- 제목 weight를 500으로 낮추고 자간 `-0.025em`, 행간 `1.14`, 최대 크기·너비를 함께 축소
- 첫 화면 제목–본문 여백 확대, 720px 높이 전용 제목·카드 밀도 보정
- 좌측 원형·사선 brand mark 제거, 상단 `SPECTRA` 텍스트만 유지
- 우측 상단 전역 상태 badge 제거
- 6번 화면에 `SYNTHETIC / NOT PHYSICAL EVIDENCE / ASSURANCE: HOLD` 전용 상태 설명 추가
- 2번 하단 문장을 “승인 BOM 0건. 화면의 부품 identity는 합성이며, 실제 추천이 아닙니다.”로 축약하고 1280px 이상 한 줄 유지
- 기존 7개 화면, wheel·키보드·버튼, 정적 fallback과 모든 합성 snapshot 유지

## H02 자동 검증 — 2026-08-20

- HTML 정적 계약: 7개 화면, brand mark 0, 전역 badge 0, 전용 assurance 상태 3/3, 원격 asset 0
- JavaScript syntax: bundled Node.js `--check` 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py`: simulation 19개와 5개 비교 scenario 통과
- `git diff --check`: 통과
- 브라우저 1280×720, 1440×900, 1920×1080: 7개 화면 overflow 0, 2번 문장 밀림 0
- wheel 01→02, Home/End 01↔07, 버튼 이동, console error 0 확인
- 5 mm `OUT_OF_MODEL_SCOPE/HOLD`, ECC OFF/ON `0.063072`/`0.0063072` exact match
- 별도 screenshot·handoff 제출은 없으며, 실제 7분 발표 시간은 발표자 리허설로 한 번 측정해야 한다.

## 구현 범위

- `demo/index.html`: 7개 화면 self-contained 발표 데모
- `demo/README.md`: 실행법, 발표 흐름, 신뢰성 경계, 내장 snapshot
- 좌우 키·Page Up/Down·Space·마우스·트랙패드 스크롤·화면 버튼 이동과 진행 표시
- 1·2·4 mm 및 범위 밖 5 mm 고정 snapshot 비교
- ECC ON/OFF 고정 snapshot 비교
- JavaScript 미실행 시 전체 화면 정적 fallback

## 소비한 합성 기준선

| 시나리오 | run ID | 핵심 결과 |
|---|---|---|
| 1 mm + ECC | `sim-d5a72077d684f459` | TID 8.0, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 2 mm + ECC | `sim-3cc00f2c824db56d` | TID 6.0, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 4 mm + ECC | `sim-ddf29f8ab807196d` | TID 3.5, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 2 mm + no ECC | `sim-b74d7317282b2a82` | raw=residual SEU 0.063072, `VALID/PASS/HOLD` |
| 5 mm + ECC | `sim-27e031f2388ab6fc` | 값 없음, `OUT_OF_MODEL_SCOPE/NOT_EVALUATED/HOLD` |

브라우저는 이 결과를 표시만 하며 물리식·보간·외삽·판정을 JavaScript로 재구현하지 않는다.

## 신뢰성 경계

- 합성 fixture의 수치·identity·SEL 표시는 실제 환경·부품·시험 증거가 아니다.
- `engineering_gate=PASS`는 합성 수치 조건 비교일 뿐 보증 PASS가 아니다.
- 모든 선택에서 assurance `HOLD`와 `SYNTHETIC`이 유지된다.
- 실제 환경 모델 run, 승인 BOM, 시험 원문·수치·artifact, policy operand와 GCP resource는 0이다.
- 실제 path는 provenance-complete 환경 출력, 승인 BOM과 event별 원문, rights gate, 독립 assurance, 이후 GCP 저장·감사 실행 순서다.

## Control Tower 독립 검증 — 2026-08-20

- `python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `python3 tests/simulation/run_all.py`: simulation 19개 통과, 5개 시나리오 snapshot exact match
- 브라우저 7개 화면, 버튼·키보드·스크롤 전환과 console error 0 확인
- 1440×900 및 1920×1080에서 7개 화면의 가로·세로 overflow 0 확인
- 5 mm 입력은 값 없이 `OUT_OF_MODEL_SCOPE`; ECC OFF/ON은 `0.063072`/`0.0063072`로 전환되고 assurance `HOLD` 유지
- 외부 URL, CDN, 원격 asset, `fetch`, WebSocket 없음
- 흑백 중심 visual hierarchy와 축약 문구를 적용해 발표 화면의 텍스트 밀도를 낮춤

작업 채팅의 별도 handoff와 screenshot 폴더는 제출되지 않았다. 실제 산출물은 독립 재현 가능하므로 데모 패키지는 `VERIFIED`로 판정하지만, Stage 8의 실제 API·EvidencePacket·원문 연결과 변경 영향 UI는 여전히 미구현이다. commit·push하지 않았다.
