# 00 Control Tower — Current State

## Status

`RELEASE_VERIFIED — PUBLIC DEMO ACTIVE; CORE ASSURANCE HOLD`

## Last verified

- 날짜: 2026-08-25
- 프로젝트 경로: `/Users/taehoon/Desktop/IAA/SPECTRA`
- Git 통합 체크포인트: 이번 통합 직전 push commit은 `719e480`이며, 현재 공개 Console·parser·catalog·발표 보완 통합 단위는 전체 회귀와 문서 정합성 검증 후 push 대상으로 승인됐다. 아래 “push 미수행” 문구는 각 과거 시점 기록이다.

## 현재 확인된 산출물

- 2026-08-25 최종 통합 회귀에서 schema 8, simulation 69, environment 65, parts evidence 39, Product 175, source adapters 14, value proof 12, GCP live adapter 35, GCP platform 13, ASR-D02 runner/reconciliation 6으로 unit 436개가 통과했다. Assurance 고정 공격 실행 47개도 failure·False PASS 0으로 통과했다. 최신 remediation manifest 때문에 historical H05 reconciliation이 실패하던 문제는 역사 target을 그대로 보존하도록 수정해, 과거 증거를 새 배포 증거로 재라벨하지 않는다.

- 공개 `spectra-demo-console`은 revision `00008-rwk`, image digest `sha256:63f925...97ee56`, URL `https://spectra-demo-console-mwmfe3da5q-du.a.run.app`에서 100% traffic을 처리한다. 실제 설정은 min 0, max 100, concurrency 20, timeout 120초, CPU 1, memory 512Mi이며 별도 service account를 사용한다. 문서 검사와 승인·권리 trust-bound 합성 Core는 요청마다 실행하고, 공격 검증은 저장 snapshot, 문서별 결과표는 공개 catalog live read로 분리한다.

- 공개 1280×720 브라우저 회귀에서 Slide 08 제목 `세 역할이 한 가지 실행의 근거를 나눠 검증한다.`, deck 가로 overflow 0, Console document overflow 0, 합성 PDF의 항목별 결과 카드 `확인 2 · 불일치 0 · 추가 입력 1`을 확인했다. 공개 공격 실행 endpoint는 쓰기 권한·비용·로그 오염·권한 확대 위험 때문에 추가하지 않았다.

- 2026-08-25 H40에서 “필수 입력 누락 → 이후 검사 전부 중단” 결함을 수정했다. 확인 가능한 수치는 계속 검사하고 확인·불일치·추가 입력 필요를 별도 ledger로 반환한다. 실제 NASA Micron 요약 + 잘못된 23LC1024 입력에서 `3 확인 · 2 불일치 · 2 추가 입력 필요`, 부품·시험 근거 검토 단계의 최종 보류를 브라우저로 재현했다. 로컬 `pypdf/TXT`는 독립 Agent가 아니므로 `DOCUMENT_PARSER_AGENT`를 제거해 `LOCAL_DOCUMENT_GATE`로 정정했다.

- 2026-08-25 H39에서 입력 축을 `MISSION_PLAN · PART_SPEC · RADIATION_TEST`로 분리했다. Landsat 9·Sentinel-2 임무 조건, Microchip 부품 명세, NASA·ESA 시험 공개값 요약을 15개 수동 test-data에 결합하고 Product 167 tests를 통과했다. 별도 공개 bucket `spectra-public-test-catalog-iceu-686`의 비로그인 HTTP 200·CORS·catalog/audit generation을 확인했으며 기존 private H04 실행 경로는 변경하지 않았다. 실제 브라우저 표는 문서 15·공개 요약 6·final gate 5·승인 0, 16-event chain과 GCP receipt를 표시한다. 실제 조합과 synthetic Core 완주 모두 assurance는 `HOLD`다.

- 2026-08-25 실제 제출·발표 deck은 로드맵을 제외한 `Cover + 01~09 + Closing`, 총 11장이다. Slide 05에 NASA·ESA·GAO 기반 사용자 부담과 미검증 비즈니스 경계를 추가했고, ESA·GAO 약어를 하단에 풀어 썼다. canonical v7 대본은 공개 Evidence Console의 Cloud Run PDF·Mission Case·저장 공격 기록 시연을 포함해 `6분 30초 + 여유 30초 = 7분`으로 계산했다. 사람 낭독·클릭 리허설은 `NOT_MEASURED`다.

- `PROJECT_OVERVIEW.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- `docs/workstreams/README.md`
- `docs/workstreams/00-control-tower/BRIEF.md`
- `docs/workstreams/00-control-tower/CURRENT.md`
- `docs/workstreams/00-control-tower/CONTROL_TOWER_SESSION_TEMPLATE.md`

## 현재 진실

- 2026-08-25 구조화된 다중 문서 Mission Case Core와 변경 영향 가치 증명 Core를 Control Tower에서 통합했다. Mission Case는 승인 BOM과 시험 claim의 manufacturer·orderable part number·package·process·die·lot을 실제 비교하고 TID·SEU 계산 및 TID/SEU/SEL/SEB/SEGR coverage를 source-local로 유지한다. 현재 모델이 비교하지 못하는 입자종·에너지·LET·fluence·온도·bias와 파괴성 SEE 적용성은 추정하지 않고 `NOT_EVALUATED / HOLD`한다. Mission Package adapter는 합성 UTF-8 원문 3종을 manifest SHA-256과 원문 줄에 결속하고, v2 승인 정책의 scope/content/approval/history 해시와 권리 snapshot의 bundle/action/history를 배포 신뢰 저장소에 대조한다. 통과한 세 원문 해시와 승인·권리 앵커는 Mission Case `evidence_binding`을 통해 Core 입력/출력 해시에 포함된다. 일반 자유형식 PDF/TXT의 자동 다중 문서 의미 매핑, 실제 사용자 효율·구매 의향, 실제 방사선 assurance는 증명하지 않는다.
- 2026-08-25 승인된 최소 배포로 image digest `sha256:cb2193...04bb`, Workflow `000006-d2a`, Mission `00007-s86`, Parts `00007-44k`, Assurance `00007-dk9`를 새 target으로 잠갔다. 정상 control은 local/deployed Core canonical hash와 semantic object가 일치해 `CONTROL_PASS`, `D02-02/04/05/10`은 모두 기대 stable code의 `SAFE_FAILURE`다. 이 5-execution batch의 False Accept·False PASS·unexpected는 0, 나머지 12건은 `NOT_EVALUATED`, 최종 assurance는 `HOLD`다. 새 control의 H07 receipt와 Product timeline은 `VALID / OBSERVED / LIVE_API / HOLD`로 갱신했다. 아래 Phase 1 실패 문장은 결함 발견 이력이다.
- 2026-08-25 사용자 승인 범위의 actual GCP `ASR-D02` Phase 1 공격 `02/04/05/10`을 locked Workflow `000005-32c`에서 실행했다. 정상 control은 `CONTROL_PASS`, 공격 4건은 `SAFE_FAILURE` 2, `FALSE_ACCEPT` 1(exact part number 변조 수용), `UNEXPECTED_RESULT` 1(generation 404로 Workflow 실패), False PASS 0이다. 나머지 12건은 `NOT_EVALUATED`이며 Stage 6·7은 계속 `IN_PROGRESS`; H05 경로는 두 결함 보완 전 `CHANGES_REQUESTED`다. 배포·IAM 변경과 push는 수행하지 않았다.
- 2026-08-25 H06 event contract와 H07 fixed-resource read-only connector를 구현했다. Workflow/Storage/세 Agent/Core를 동일 execution/correlation에 결속하고 sequence·timestamp·SHA-256 chain·deployment revision·Storage generation·Agent/log/Core hash를 검증한다. H05 실제 구조에 맞춰 execution object hash와 Core canonical input hash를 분리했으며 H06/H07 직접 테스트 28개가 통과했다. connector는 execution describe·logging read·object describe/cat만 허용하고 GCP mutation 경로가 없다.
- 2026-08-25 첫 H07 조회는 credential 재인증 만료로 안전하게 닫혔다. 재인증 후 Logging을 execution 시간 범위로 제한해 동일 정상 execution의 API·세 Agent log·Storage generation/body를 actual read-only 수집했고 `VALID / COMPLETE / SUCCEEDED / SYNTHETIC_ONLY / HOLD` receipt를 발행했다. H08 data는 `LIVE_API / live_api_observed=true / fallback_used=false`와 실제 8-event timestamp/hash chain으로 재생성됐다. actual live·fallback·낙관 승격·non-finite·snapshot 변조·결정성 H08 테스트 7개가 통과했으며 Product HTML 시각 연결은 보류했다.
- 2026-08-25 Phase 1 실행 전에는 기존 H05 evidence만 reconciliation했다. exact locked target·generation/hash·세 Agent log·Core parity가 완전한 정상 control 1건만 `CONTROL_PASS`로 평가했고, 관련 H05 공격 사례는 exact mutation/필수 관찰값 차이로 소급하지 않았다. 당시 공격 16건은 평가 0·`NOT_EVALUATED`, False Accept/PASS는 `NOT_COMPUTED`였으며 이후 상태는 위 Phase 1 문장이 대체한다.
- 2026-08-25 `23LC1024` 공개 시험의 실제 외부 PDF를 JLU DOI/고정 locator, `33,130,232` bytes, SHA-256, CC BY 4.0 attribution/action 조건에 결속하는 production source gate와 reference package composer를 구현했다. candidate+anchor 동시 재결속, content/URL/license/action/optimistic decision 공격을 포함한 source/package 17개와 기존 인접 22개, 총 39개 테스트가 통과했다. source manifest/rights blocker만 해소됐고 exact suffix/package/lot/die·mission·TID/destructive SEE 공백은 남아 `SOURCE_READY_COMPARISON_BLOCKED / NOT_COMPARABLE / HOLD`, actual EvidencePacket 0건이다.
- 최종 Competition Demo Release에서는 실제 GCP Workflow 요청, Agent별 진행·실패 상태, immutable input/output hash, Storage generation, 최종 Core/Assurance 판정을 같은 실행 ID로 시각화한다. `GCP 실행 성공`과 `evidence 검증/assurance`를 별도 축으로 표시하고, live 연결 실패 시 검증된 고정 결과 fallback으로 전환하되 라이브처럼 표시하지 않는다.
- 2026-08-25 공개 `23LC1024` 시험값과 SPECTRA 합성 입력을 검토하는 deterministic comparison gate를 구현했다. 게이트는 저장된 blocker를 신뢰하지 않고 exact identity·package·lot/die·source manifest·단위·합성 조건을 재평가하며, 현재 결과를 `VALID / NOT_COMPARABLE / HOLD`, 숫자 비율을 `CALCULATED_REFERENCE_ONLY`로 제한한다. optimistic PASS/direct validation, ratio 1 ULP, boolean·비유한수·단위·identity·hash 공격을 포함한 신규 10개와 기존 binding 5개, 총 15개 테스트가 통과했다. exact-part 데이터 불완전성은 발표·직접 검증 리스크로 명시했으며 실제 Evidence Packet은 계속 0건이다. 사용자 요청에 따른 다음 통합 시점에서 전체 회귀를 통과해 누적 integration unit의 commit·push 대상에 포함했다.
- 2026-08-25 `evidence-console.html` 하나에서 `문서 1개 검사 · 3개 입력 연결 · 공격 검증 기록 · 전체 문서 결과`를 전환하는 통합을 검증했다. Local 합성 PDF는 후보 7개·최종 `HOLD`, GCP는 저장 로그 13건·`SNAPSHOT ONLY · HOLD`, 공개 문서 결과는 15행과 감사 해시 체인을 같은 URL 안에서 표시한다.
- `3개 입력 연결` 첫 실행은 manifest로 고정한 합성 임무·승인 BOM·방사선 시험 원문 3개를 adapter로 파싱해 production Mission Case Core에 전달하고, 원문 해시·줄 위치, exact identity 6필드, TID·SEU 계산, TID·SEU·SEL·SEB·SEGR source-local coverage와 미지원 조건 HOLD를 표시한다. 두 번째 실행은 production Review Impact Core로 기간·차폐·부품번호 변경의 재검토 범위와 다음 행동을 반환한다. 실제 승인 근거·방사선 assurance는 계속 0건/HOLD다.
- 2026-08-25 Local parser에 보수적 numeric field 추출을 추가했다. TID dose·dose rate·LET·cross-section·fluence·energy·temperature·voltage·sample size·LDC는 정확한 원문 span과 단위를 가진 미승인 후보로만 반환하며 failure dose를 rating으로 해석하지 않는다. NASA·ESA published observation 요약 3종을 수동 fixture로 추가했고, 한글 파일명 header 인코딩 실패로 발생하던 `LOCAL_CONSOLE_UNAVAILABLE`도 수정했다.
- 변경 범위 직접 테스트 21개와 Product 전체 157개, schema 17개·정상 fixture 5개·실패 fixture 116개, simulation 55개, environment·Assurance·GCP H05 local runbook, 인접 readiness·parts·source·local assurance 32개가 통과했다. 두 stale UI 문구 assertion은 현재 화면 계약에 맞춰 보완한 뒤 해당 범위 전체를 재검증했다.
- 현재 제출·발표 deck은 `Cover + 01~09 + Closing`, 총 11장이다. 순서는 `차폐 → COTS → 문제 → 기존 방식 → 외부 근거 기반 사용자 부담 → SPECTRA 흐름 → 판단 원칙 → GCP → 무결성 설계`다. 09는 시스템 조치와 actual GCP 평가 범위 `4 / 16`, 나머지 12 `NOT_EVALUATED`, `FINAL HOLD`를 함께 표시한다. 로드맵은 주 발표에서 제외했고 사람 낭독·클릭 리허설은 아직 `NOT_MEASURED`다.
- 최종 제출 회귀에서 schema 17개·valid fixture 5개·invalid fixture 116개, simulation 58, environment 65, Assurance 47 attack executions/False PASS 0, GCP platform 13, GCP live adapter 35, Product 157 tests가 통과했다. `git diff --check`도 통과했고 변경 파일 secret scan의 유일한 두 hit는 토큰 저장을 금지하는 문서 속 literal `rapt=...` 예시였다.
- 같은 localhost에서 Evidence Console의 합성 비정형 PDF는 실제 parser `13 events`, 고정 정답 `7 / 7`, 최종 `HOLD`로 종료했다. Batch 화면은 합성 3문서·후보 7·HOLD 3·reference `3 / 3`을 재현했고 가로 overflow가 없었다. 브라우저 자동화가 부모 화면 로드 시 주입한 `MutationObserver` 오류는 앱 코드에 해당 API가 없고 batch 직접 탭 오류 0으로 분리됐으므로 제품 결함 수치에 포함하지 않는다.
- 이 통합은 로컬 합성 Product·고정 GCP snapshot·발표 운영만 `VERIFIED`한다. 실제 environment contract 0건, 승인 exact-part Evidence Packet 0건, Document AI·Gemini 호출 0건은 바뀌지 않는다. 실제 GCP `ASR-D02`는 이제 Phase 1 네 공격만 평가됐고 나머지 12건은 `NOT_EVALUATED`; 최종 assurance는 `HOLD`다.
- 2026-08-25 발표의 COTS SRAM 범위에 맞춰 사용자가 Microchip `23LC1024-I/SN`을 SPECTRA MVP exact-part 검토 대상으로 승인하고 기존 Space/QML-V/RHA TI CAN transceiver 선택을 대체했다. Microchip 공식 자료에서 현재 양산되는 1 Mbit SPI/SDI/SQI SRAM임을 확인했고, ESA는 base product `23LC1024`를 GOMX-4B/CHIMERA의 COTS memory radiation experiment 탑재품으로 명시한다. 공개 Am-Be neutron screening의 PDIP `23LC1024` SEU cross section `(4.10 ± 0.04) × 10^-9 cm²/device`를 별도 reference로 결속했지만 승인 `/I/SN`은 SOIC이고 exact suffix·lot/die가 없어 직접 검증에는 사용하지 않는다. 현재 합성 cross section과의 약 `243.9×`는 입력값 차이일 뿐 정확도·적합성 지표가 아니다. CHIMERA 나머지 memory와 공개 radiation database 재검색에서도 flight identity와 numerical test article을 함께 닫는 더 강한 memory 사례는 찾지 못했다. Φsat-1의 Intel Movidius `Myriad 2`는 실제 비행·TID/SEE 데이터가 있는 강한 COTS 사례지만 복합 AI SoC라 현재 SRAM 모델의 대체품으로 사용하지 않는다. BOM identity·차폐·TID·per-device evidence에서 구매 수량을 제거하고, 총 SEU 집계에만 별도 `analysis_device_count`를 사용한다. COTS library·Product binding·Evidence Console 35개와 reference comparison 5개, 합계 직접 테스트 40개 및 diff check가 통과했으며 브라우저 재점검은 보류했다. 이는 catalog target과 비교 reference를 고정한 것이며 decision-usable exact-part packet은 계속 0건, assurance는 `HOLD`다.
- 2026-08-24 `Roadmap Lab`을 비전문가가 따라갈 수 있는 `자료 선택 → 6개 gate 검사 → 변경 후 재검사` 3단계로 통합했다. 합성 정상은 6개 gate를 통과하되 승인으로 승격되지 않고, 변조는 hash gate 2, 오부품은 identity gate 4에서 멈춘다. ECC·차폐·부품 변경은 각각 gate 6·5·4를 다시 연다. 브라우저 로컬 JSON/PDF/TXT는 최대 10 MB를 메모리에서만 읽고 provenance가 없으면 gate 3에서 닫는다.
- Git 밖 실제 SPENVIS 9개와 TI 후보 5개를 새 local bundle gate로 직접 결속했다. 두 묶음 모두 파일 hash 결속은 재현됐지만 action별 권리와 외부 승인 anchor가 없어 `PROVENANCE_FAILURE / HOLD_NOT_ISSUED / HOLD`다. UI에는 raw bytes·경로·식별자·hash 없이 source class·개수·blocker code만 담은 receipt를 연결했다. SPENVIS 내부 일관성 11개는 재현됐으나 독립 comparator·승인 tolerance·독립 reviewer가 없어 과학 교차검산은 `NOT_EVALUATED`다.
- local bundle, document intake, exact-part readiness, review audit, CAD change와 HW-SW change impact adapter를 정상·변조·경로 탈출·prompt injection·낙관 PASS·자기검토·hash rebinding 공격으로 독립 검증했다. 이 구현은 후보를 구조화하고 재검토 범위를 만드는 로컬 기능만 `VERIFIED`하며, 실제 environment contract·exact-part Evidence Packet·suitability·radiation assurance를 발행하지 않는다.
- 최종 통합 회귀에서 schema 17개·정상 fixture 5개·실패 fixture 116개, simulation 55, environment 65, Product 140, GCP H05 local 12, 인접 readiness·parts·source·assurance gate 32 tests를 통과했다. Assurance는 평가된 공격 실행 47회·False PASS 0이고 실제 GCP `ASR-D02` 1건은 계속 `NOT_EVALUATED`다. 1280×720 브라우저에서 실제 후보 gate 3 차단, 합성 정상 6개 gate 통과, ECC·차폐·부품 변경의 gate 6·5·4 재개방, overflow·console 오류 0을 확인했다.
- 2026-08-24 production NASA local snapshot gate를 기능형 Evidence Review 1단계에 연결했다. synthetic bytes의 hash·NASA allowlist·revision·action rights·exact identity를 검증한 deterministic receipt만 소비하며 화면 상한은 `CONTROL VALID · NO DECISION`이다. source adapter·Evidence Review·Product binding 42 tests와 localhost 1280×720 상태 표시·HOLD·overflow 0을 확인했다. live NASA fetch·actual evidence·trusted external anchors·suitability는 0건이다.
- 2026-08-24 Roadmap Lab을 설명형 허브에서 기능형 Evidence Review로 교체했다. bundled evidence readiness·document candidate·generated MVP JSON을 실제로 읽어 `근거 검사 → 검토 action → 변경 영향`을 수행한다. 낙관 decision·fabricated approval/rights·value rebinding 공격을 포함한 직접 테스트 10개와 Product binding 17개, localhost 1280×720의 세 조작·fixture 값 표시·최종 HOLD·전체 panel overflow 0을 확인했다. 이 로컬 제품 동선만 `VERIFIED`이며 실제 evidence·connector·authenticated audit·radiation assurance 완료가 아니다.
- 2026-08-24 발표 로드맵 Phase 01~03을 `Roadmap Lab` 7개 local 화면과 NASA snapshot intake gate로 제품화했다. Control Tower 직접 테스트 11개 module 136 tests와 red-team 후속 8개 module 95 tests, localhost 1280×720의 hub·발표 링크·수정 화면 overflow 0을 확인했다. 상태는 bounded 구현 3, readiness 2, external blocker 2이며 전체는 `SYNTHETIC / HOLD`다. 실제 SPENVIS/NASA connector, production COTS library, Document AI/Gemini 호출, authenticated HITL, CAD/3D 계산, KMS와 penetration test는 완료되지 않았다.
- 같은 회차의 독립 red-team P1 다섯 건을 보완했다. COTS audit export에서 identity-bearing record ID를 제거했고, local document action right를 `SYNTHETIC_DEMO_ONLY`로 표시했으며, AI region과 security snapshot display 값을 exact allowlist로 닫고, generated policy approval을 `SYNTHETIC_` 상태로 인접 표기했다. NASA synthetic control 권리는 `SYNTHETIC_CONTROL_ONLY`로 분리했다.
- 통합 회귀는 schema 17개·정상 fixture 5개·실패 fixture 116개, simulation 55, environment 65, Product 125, GCP H05 local 12, source adapter 14 tests를 통과했다. Assurance는 47 attack executions·False PASS 0이고 `ASR-D02` 1건은 계속 `NOT_EVALUATED`다. 최초에 존재하지 않는 `tests/schema/run_all.py`를 호출한 명령 오류 1건은 올바른 `tests/schema/validate_contracts.py`와 readiness 8 tests로 바로 재검증했으며 제품 실패가 아니다.
- 2026-08-24 readiness 최종 통합 회귀에서 schema 17개·정상 fixture 5개·실패 fixture 116개, simulation 55, environment 65, Product 17, GCP H05 local 12 tests를 재현했다. 추가 직접 회귀는 readiness schema 8, exact-part test gate 7, local readiness QA 3, Evidence Review Workspace 21 tests가 모두 통과했다. Assurance는 47 attack executions·False PASS 0을 유지하며 실제 GCP `ASR-D02`는 `NOT_EVALUATED`다.
- Workstream 10 readiness receipt v1, Workstream 31 issuance time fail-closed, Workstream 40 artifact path fail-closed, Workstream 60 local readiness 공격, Workstream 80 H19 Workspace를 독립 검증해 각 좁은 구현 범위를 `VERIFIED`로 판정했다. actual environment contract 0건, 승인 BOM exact-part packet 0건, suitability와 실제 방사선 assurance `HOLD`는 바뀌지 않는다.
- 발표 13장을 localhost 1280×720에서 실제 순회해 모든 화면 x/y overflow 0을 확인했다. Multi-Agent 화면의 Trust & Integrity는 private 접근·입력 결속·자체 승인 차단·fail-closed만 주장하고 `NOT PEN TEST / KMS / ASSURANCE` 경계를 인접 표시한다. 이 표현 패키지만 `VERIFIED`이며 완전한 보안 또는 보안 인증을 뜻하지 않는다.
- 2026-08-24 최종 통합 회귀에서 schema 14개·정상 fixture 5개·실패 fixture 116개, simulation 55, environment 23, Product 16, GCP H05 local 12 tests와 Assurance 47 attack executions/False PASS 0을 재현했다. `ASR-D02` preparation은 prepared attack 16개·control 1개·failure 0이지만 live execution 0으로 계속 `NOT_EVALUATED`다. JSON 형식, Python·shell syntax, staged diff와 비밀정보 경계도 확인한 뒤 57개 파일을 commit `889dc94`로 통합했다. 이 Git 통합은 실제 environment contract, exact-part evidence, 과학적 적합성 또는 radiation assurance 완료를 뜻하지 않는다.
- 2026-08-24 루트 문서 정합성 감사를 수행했다. schema 14개·정상 fixture 5개·실패 fixture 116개, simulation 55, environment 23, Product 16, GCP H05 local 12 tests와 Assurance 47 attack executions/False PASS 0을 재현했다. 이 회귀는 합성·계약·표현 경로의 현재 동작만 확인하며 실제 방사선 과학·부품 suitability·권리·`ASR-D02`를 검증하지 않는다.
- 루트 README의 Stage 2 시점 설명, ROADMAP의 `ASR-D02 진행 중`, Stage 7의 미표시 검증 항목과 초기 `현재 우선순위/다음 작업`을 현재 증거에 맞게 갱신했다. H05 합성 GCP 계약·resource·E2E·장애 격리 항목만 완료로 표시했고, 비용 기준선·전체 배포 공격·실제 evidence 경로는 미완료로 유지했다.
- 2026-08-22 사용자 확인으로 실제 발표 경로는 `demo/product.html`이 아니라 `demo/index.html` 단독이었고, 실제 사용한 최신 원본은 Downloads의 `spectra_presentation.html`이었다. 개별 cover/01~09/COTS HTML은 발표 후 피드백을 반영한 배치·문구 청사진이다. Control Tower는 이 실제 발표본을 저장소 기준으로 동기화한 뒤 기존 흑백 deck 디자인을 유지하면서 `spectra_slide_cots_comparison.html`을 03번에 **삽입**하고, 차폐 이유·1/4/5 mm 의미·전체 흐름 설명을 추가해 `Cover + 01~11 + Closing`, 총 13장으로 통합했다.
- 새 GCP Workflow execution `ad392071-1554-43e8-9447-5b92d4790a48`을 재인증 후 독립 조회했다. Workflow `spectra-h04-e2e` revision `000005-32c`에서 `SUCCEEDED`했고, all-zero expected SHA-256을 가진 합성 공격 입력을 Mission revision `spectra-h04-mission-00006-4f5`가 `INPUT_BODY_SHA256_MISMATCH`로 차단했다. 실제 Storage result generation `1787290937657357`과 05:42:16~17Z Cloud Run structured log가 `INVALID_INPUT / NOT_EVALUATED / HOLD`에 일치한다. Parts·Assurance가 호출되지 않은 것은 Mission 단계 fail-closed 결과다. 이 실행은 추가 공격 차단 증거로 `VERIFIED`지만, 세 Agent 정상 실행·실제 환경·부품 보증 증거로 확대하지 않고 기존 H05 snapshot과 별도 표시한다.
- 2026-08-22 Product H17 후속 후보를 실제 diff와 실행 harness로 재검증했다. 1·4 mm는 TID만 표시하고 Residual SEU는 `—`, 2 mm는 ECC OFF `0.063072` / ON `0.013072`, 5 mm는 수치를 만들지 않고 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`로 닫는다. 제거된 35점 badge를 계속 요구하던 stale 테스트 기대값을 Control Tower가 바로잡고 네 두께·ECC 상태 검사를 추가했으며 Product 직접 테스트 16개와 JavaScript syntax가 통과했다. 실제 `file://` 브라우저는 URL 정책으로 차단돼 viewport·console·수평 overflow·상하 4박스 정렬은 `NOT_EVALUATED`이며 H17은 아직 `VERIFIED`로 승격하지 않는다.
- Downloads 생성 시각 기준 실제 사용 대본은 `spectra_7min_presentation_script.md`의 2026-08-21 13:55 추가본이다. 이 파일은 실제 발표 이력으로 인정하지만 AP-8/AE-8·SHIELDOSE-2 기반 실제 계산, 정확 부품 성적서, 79% 저감, 19개 평가, False PASS 0, 실시간 실행과 비행 승인 표현을 포함해 현재 증거 범위를 넘으므로 canonical assurance 대본으로는 `CHANGES_REQUESTED`다.
- 저장소 `demo/index.html` 시각 통합은 localhost `http://127.0.0.1:8766/index.html`의 실제 1280×720 브라우저에서 13장 모두 document/inner horizontal·vertical overflow 0, console warning/error 0을 확인했다. 범위·신뢰성 화면의 상단 두 박스는 `129 px`, 하단 네 박스는 `73 px`로 각 행의 상·하 기준선이 일치했고, GCP 화면의 두 decision 박스도 `114 px`로 정렬됐다. 35점 badge는 없고 6개 node·세 Agent·H05 synthetic snapshot·`HOLD` 범위만 표시된다.
- 같은 브라우저에서 차폐 1/2/4 mm는 각각 TID `8.0/6.0/3.5 krad(Si)`와 `VALID`, 5 mm는 `계산 안 함 / OUT_OF_MODEL_SCOPE / HOLD`로 닫혔다. ECC는 2 mm 고정 시나리오에서 OFF `0.063072`, ON `0.013072`이며 실제 효과가 아니라는 문구를 유지한다. 직접 테스트 16개, JavaScript syntax와 `git diff --check`도 통과했다. 이 판정은 **발표 deck의 시각·상호작용 통합만 `VERIFIED`**한 것이며 COTS 비교 수치·과학 정확성·실제 환경·부품 suitability는 계속 `NOT_EVALUATED / HOLD`다.
- Google Cloud Console 버튼은 실제 발표본과 같은 stable Workflow URL `.../spectra-h04-e2e?project=iceu-686` 연결을 유지한다. 로그인된 Console이 인증 과정에서 `executions?...&rapt=...`로 이동시키는 동작을 코드에 토큰과 함께 고정하지 않는다.

- 2026-08-21 범위 감사에서 SPECTRA의 Core Product를 환경 모델·정확한 부품 시험 증거·결정론적 TID/SEU·차폐/ECC·fail-closed로 고정했다. WATCHDOG·TMR·SEL protection runtime은 과거 검증 이력을 보존하는 실험 범위이며 현재 제품 판단·주 발표·Core 신뢰성 집계에서 제외한다.
- 공식 평가 기준은 Multi-Agent·GCP 35, 신뢰성 20, 비즈니스·문제 정의 30, 팀 시너지·발표 15다. Multi-Agent·GCP는 과학적 Core와 역할은 분리하지만 Competition Demo Release의 필수 Stage다.
- 교육용 project `iceu-686`, region `asia-northeast3`에 private Cloud Run Agent 3개, Workflows, Storage, IAM, Logging 합성 E2E가 실제 배포됐다. 사용자는 비용 제한을 두지 않았으며 resource는 계속 배포 중이다. H04 독립 공격에서 발견한 body-hash 우회·Core 미결합·runtime endpoint 교체 가능성은 H05에서 보완했고, 로컬 12 tests·실제 revision·정상/공격 result를 독립 재검증해 H05를 `VERIFIED`로 판정했다.

- SPECTRA의 문제·범위·평가 기준 문서는 작성됐다.
- Stage 1~9 로드맵과 단계별 체크리스트가 존재하며, 각 Stage 번호는 주관 Workstream 앞자리와 일치한다.
- 결정론적 합성 TID·SEE 기준선은 Workstream 20이 프로젝트에 통합했고, 모든 결과가 `SYNTHETIC/HOLD`를 유지한다.
- 실제 SPENVIS 원본 bundle 1세트·9개와 parser 후보는 Git 밖에서 checksum·구조 검증했지만, provider reference·권리·승인 raw manifest 부족으로 제품 contract 발행은 0건이다. 실제 부품 시험자료의 승인 ingest와 과학적 교차검산도 미완료다.
- Multi-Agent·GCP H05 구현·배포 증거와 발표 deck의 합성 snapshot 표시는 `VERIFIED`지만 Workstream 60의 고정 revision `ASR-D02`와 비용 기준선 전까지 Stage 7 완료로 승격하지 않는다.
- 검증된 Stage 1 계약 기준선은 커밋 `303adb9`로 비공개 `origin/main`에 반영됐다. 해당 커밋 메시지의 `Stage 0` 표기는 번호 정렬 이전의 역사적 명칭이다.
- 채팅 세션 10의 Contracts & Schema 작업은 4차 수정 후 독립 재검증과 Git 통합을 완료했다.
- 세션은 실제 채팅방을 뜻한다. Workstream은 십 단위로 구분하고 첫 채팅도 같은 번호를 사용하며, 같은 Workstream에서 새 채팅이 필요할 때만 1단위로 증가한다.
- 잘못된 Control Tower 안내로 채팅 10에서 시작된 Workstream 20 후보는 채팅 20이 소유권을 인수해 보완했고, 번호를 Stage 1 계약 / Stage 2 합성 기준선으로 정렬했다.
- Workstream 20은 독립 재실행으로 schema fixture 28개(정상 1·실패 27), simulation 19개 테스트와 5개 비교 시나리오를 통과했다. 지원 판정 승격·4.1 mm 외삽·비직렬화 입력 공격도 안전하게 `HOLD`로 종료해 합성 기준선 패키지를 `INTEGRATED`로 판정했다.
- Stage 2 Exit Gate는 완료됐다. 원본 위치가 없던 외부 데모·CSV 이관은 대상에서 제외했고 제품 대시보드·완화 선택 UI는 Stage 8로 귀속했다. 이는 Workstream 20의 향후 Stage 5 계산 협업까지 종료됐다는 뜻은 아니다.
- Workstream 30의 SPENVIS·OLTARIS 공식 도구·권리 조사와 Stage 3 계약 초안을 독립 대조해 조사 패키지를 `INTEGRATED`로 판정했다. 이 문장은 당시 조사 회차 기록이며, 이후 실제 SPENVIS 원본 bundle과 parser 후보를 확보했다. 과학적 교차검산과 승인 contract 발행은 여전히 0건이고 Stage 3은 `IN_PROGRESS`다.
- Workstream 40의 NASA·ESA·ESCIES·제조사 출처, 권리, 부품 identity, 사건별 시험 증거와 적용성 계약 초안을 독립 대조해 조사 패키지를 `INTEGRATED`로 판정했다. 승인 BOM·실제 원문·실제 수치·EvidencePacket은 0건이며 Stage 4는 `IN_PROGRESS`다.
- Workstream 40의 후속 `PART_TEST_EVIDENCE v2`·공격 fixture 문서 명세 H02는 이전 세 계약 모순을 해소해 commit `4bd1362`로 `INTEGRATED`됐다. 실제 schema·fixture 구현, BOM·원문·시험 수치는 없으므로 Stage 4는 `IN_PROGRESS`, 실제 판단은 `HOLD`를 유지한다.
- Workstream 10 H01~H04 누적 보완분은 schema 11개, 정상 2개, 실패 71개, simulation 19개와 provenance·operand·중복 shadowing 독립 공격을 통과해 commit `4bd1362`로 `INTEGRATED`됐다.
- `.gitignore`에 `.obsidian/`을 추가했다. 새로 만드는 채팅 시작 템플릿은 handoff 제출 회차를 `H01`, `H02` 형식으로 명시하며, 기존 채팅 00~40의 파일명은 변경하지 않는다.
- Workstream 50 H02는 watchdog false-positive/SEL false-trip 합산과 TMR failure-probability 의미를 보완해 독립 검증을 통과했다. 판정은 문서 계약 패키지 `VERIFIED`이며 실제 schema·engine·fixture·실제 효과 데이터는 0건, Stage 5는 `IN_PROGRESS`다.
- Workstream 70의 GCP Evidence Storage & Rights Gate H01은 권리 action gate, tenant/IAM 경계, generation+SHA-256 lineage, 보존·삭제·감사·비용 위험을 공식 GCP 문서와 대조해 `VERIFIED`로 판정했다. 실제 GCP resource·실행·비용 증거는 모두 0이며 Stage 7은 `IN_PROGRESS`다.
- 발표를 위해 문제 정의를 COTS 채택 자체가 아니라 임무 환경·정확한 부품 identity·시험 조건·완화·승인 사이의 증거 단절로 구체화하고 NASA 근거와 검증되지 않은 실무 가설을 분리했다.
- Workstream 80의 self-contained 오프라인 HTML 데모를 흑백 중심의 미니멀 UI로 보완하고 1440×900·1920×1080, 7개 화면, 키보드·버튼·스크롤, 범위 밖 5 mm, ECC ON/OFF, console error 0을 독립 검증했다. 발표용 합성 UI 패키지만 `VERIFIED`이며 Stage 8은 `IN_PROGRESS`다.
- Workstream 90의 최초 원고는 9개 화면·9분 15초여서 7분 발표 조건과 맞지 않아 `CHANGES_REQUESTED`였다. 이 판정은 이후 H02 7분 주본으로 해소된 과거 검토 이력이며, 현재 판정은 아래의 `VERIFIED`다.
- Workstream 10 H05의 EvidencePacket 1.0/1.1, MITIGATION·USER_POLICY·RAW_ARTIFACT_MANIFEST v2 계약을 독립 재검증했다. schema 14개, 정상 fixture 3개, 실패 fixture 83개, simulation 19개와 별도 version·rights·generation·support 승격 변조가 통과해 H05 계약 패키지를 `VERIFIED`로 판정했다. 실제 계산·정책 승인·GCP 상태는 여전히 0이다.
- 발표 운영 시간은 데모 포함 7분, 질의응답 3분으로 확정됐다. 90 발표 원고는 사용자가 해당 채팅에 그대로 전달하며, UI 보완은 Control Tower가 직접 구현하지 않고 기존 채팅 80이 H02로 수행한다.
- Workstream 80 H02는 별도 handoff 없이 실제 산출물로 검증했다. 1280×720·1440×900·1920×1080의 7개 화면, 2번 문장, wheel·Home/End·버튼, 5 mm 범위 밖, ECC ON/OFF와 console error 0이 통과해 발표 UI 패키지를 `VERIFIED`로 판정했다. 발표 원고를 7개 화면에 맞춘 뒤 실제 7분 리허설 1회가 남아 있다.
- Workstream 60 H01의 독립 공격 기준선을 재실행했다. schema·semantic 공격 17개, simulation 공격 1개와 재현성 control 1개가 통과했고 평가된 18개 공격의 False PASS는 0건이다. 완화 engine과 실제 GCP 공격 2개는 `NOT_EVALUATED`로 분리되어 있어 H01은 `VERIFIED`, Stage 6은 `IN_PROGRESS`로 판정했다.
- Workstream 80 H03은 별도 `demo/product.html`을 실제로 생성했고 고정 snapshot·fail-closed·원격 의존성 0 계약과 회귀 테스트가 통과했다. 다만 실제 viewport·console 검증이 없고 9~11px 보조문구, 영문 전문용어와 균일한 카드 위계로 도메인 초심자 가시성이 부족해 `CHANGES_REQUESTED`로 판정했다. 발표용 `demo/index.html`은 변경하지 않고 H04에서 Product UI만 보완한다.
- Workstream 80 H04는 한국어 질문·결론 우선, 조작별 해석, `수치 조건 통과 → 실제 근거 부족 → HOLD → 다음 행동` 인과 흐름과 가독성 대비를 보완했다. 정적 계약·전체 회귀가 통과했고 사용자가 실제 조작 후 현재 기준을 수용해 발표용 합성 Product UI 프로토타입을 `VERIFIED`로 판정했다. 지정 viewport·console은 Control Tower가 독립 캡처하지 못했으며 실제 API·원문 통합 UI는 여전히 미구현이다.
- Workstream 90 H02는 발표 HTML과 H04 Product UI를 결합한 6분 40초 설명·20초 여유의 7분 주본, Product UI 실제 조작 4분, 우선 Q&A 4개 2분 25초와 30초 fallback을 작성했다. 실제 UI의 1·2·4·5 mm, ECC 미적용/적용, 모든 `HOLD`와 browser warning/error 0을 확인해 발표 서사 패키지를 `VERIFIED`로 판정했다. 사람 낭독·탭 전환 7분 리허설과 OS 네트워크 차단 리허설은 미실측이며 Stage 9 비즈니스 검증도 미완료다.
- 기존 문서에는 초기 범위와 Stage별 Exit Gate만 있고 단일 MVP 완료 계약이 없었다. `docs/MVP.md`에 고정 LEO 임무 1개, exact-part 1개, 실제 환경 산출물·시험 증거·결정론적 완화·정책·Assurance·Product UI를 연결하는 Core MVP를 정의했다. 합성 UI만으로는 MVP가 아니며, 정확한 `HOLD`도 정상 제품 결과다. 현재 상태는 `MVP IN_PROGRESS`다.
- Workstream 20 H01 MVP Decision Engine은 schema 14·fixture 3/83·simulation 28·assurance 19 evaluated 회귀와 canonical EvidencePacket·Change Impact를 재현했지만, `NaN/Infinity` 입력이 구조화된 `HOLD`가 아닌 일반 `ValueError` traceback으로 종료돼 `CHANGES_REQUESTED`다. 기존 Stage 2 통합 판정에는 영향이 없다.
- Workstream 40 H03은 TI exact PN `5962L1420901VXC`와 `SLLK019` TID report의 identity·locator·hash 및 문서 내부 충돌을 독립 재현해 discovery candidate를 `VERIFIED`로 판정했다. 승인 BOM·rights snapshot·raw manifest·v2 fixture·임무 적용성·SEE coverage가 없어 decision은 `PARTIAL_UNRESOLVED/HOLD`, MVP와 Stage 4는 미완료다.
- Workstream 30은 사용자가 SPENVIS에 로그인해 실제 산출물을 대화형으로 확보 중이다. 해당 진행 파일은 20·40 검증과 분리했으며 완료 판정을 내리지 않았다.
- Workstream 20 H02는 비유한 숫자 3종과 하위 계산 오류를 stable machine-readable `INVALID_INPUT/NOT_EVALUATED/HOLD`로 보완했다. schema 14·fixture 3/83·simulation 31·environment 8·assurance 19 evaluated 회귀와 정상 canonical 결과를 독립 재현해 합성 MVP Decision Engine 기준선을 `VERIFIED`로 판정했다.
- Workstream 30 H03은 실제 SPENVIS 원본 9개, artifact-set hash, 실제-format parser와 4개 TID 후보의 `HOLD`를 재현했다. 그러나 동일 artifact 하나를 모든 필수 source role로 중복 매핑해도 completeness gate를 통과해 `CHANGES_REQUESTED`다. 실제 environment contract는 provider job reference·권리·raw manifest도 없어 계속 `HOLD`다.
- 채팅 31 H01은 source-role exact-one, artifact ID/path 재사용과 manifest duplicate ID 우회를 보완했고 기존·전체 회귀와 실제 bundle 9/9를 통과했다. 다만 NUL path 입력이 구조화된 provenance HOLD 대신 `ValueError`를 발생시켜 `CHANGES_REQUESTED`다. 실제 contract emission은 계속 `HOLD`다.
- Workstream 60 H02는 MVP Decision Engine D01 하위 공격 11개를 실제 실행 대상으로 추가했다. 기존 18개 공격과 합쳐 평가된 공격 실행 29개에서 False PASS 0, failure 0을 독립 재현해 `VERIFIED`로 판정했다. live GCP `ASR-D02` 1개는 계속 `NOT_EVALUATED`다.
- Workstream 70 H02 raw manifest preflight는 제출 fixture와 전체 회귀를 통과했지만 malformed schema 입력 4종이 예외를 발생시키고, creation receipt가 exact project/bucket/object identity에 결합되지 않아 storage ref 변조가 `ISSUE_ALLOWED`로 통과했다. H01 문서 설계는 `VERIFIED`를 유지하되 H02 구현은 `CHANGES_REQUESTED`다.
- 채팅 31 H02는 embedded NUL 앞·중간·끝과 예상 가능한 path/file 오류를 stable provenance HOLD로 보완했다. environment 23개와 전체 회귀, 실제 bundle 9/9·값 비노출 parser 구조를 독립 재현해 구현 패키지를 `VERIFIED`로 판정했다. 실제 contract emission과 Stage 3은 계속 `HOLD/IN_PROGRESS`다.
- Workstream 70 H03은 malformed 입력을 semantic traversal 전에 차단하고 synthetic creation receipt를 exact project/bucket/object/generation에 결합했다. 별도 11개 공격과 전체 회귀를 통과해 local preflight 구현을 `VERIFIED`로 판정했다. 실제 GCP resource·rights·manifest·비용은 0이고 `ASR-D02`는 계속 `NOT_EVALUATED`다.
- 위 누적 검증 범위 76개 파일은 commit `379f3ad`로 `main`과 `origin/main`에 통합했다. 이는 각 패키지의 Git 통합만 뜻하며 Stage 3~9 완료, 실제 environment contract, 실제 parts evidence, 실제 GCP 또는 radiation assurance 완료를 뜻하지 않는다.
- Workstream 20 H03 보완은 runtime result의 `processing_status`를 공통 enum `$ref`에 정렬하고 processing 상태의 `NOT_EVALUATED` 사용을 제거했다. 전용 24개, simulation 55개, environment 23개, product 7개, preflight 2개와 assurance 29 evaluated attack executions/False PASS 0을 독립 재현해 합성 runtime calculator 패키지를 `VERIFIED`로 판정했다. 실제 효과 데이터·승인 policy·Stage 3·4 evidence가 없으므로 assurance는 계속 `HOLD`다.
- Workstream 60 H03은 production runtime API를 직접 공격하는 `ASR-D03`을 추가했다. 전체 회귀에서 평가된 공격 실행 47개, control 4개, failure 0, False PASS 0을 독립 재현해 `VERIFIED`로 판정했다. 실제 GCP `ASR-D02`는 `NOT_EVALUATED`이고 Stage 6은 계속 `IN_PROGRESS`다.
- Workstream 80 H06의 production runtime 결과 연결과 9개 Product 회귀는 재현됐지만, 브라우저가 runtime result 본문에서 canonical `output_hash`를 재계산하지 않는다. WATCHDOG downtime만 60에서 999로 변조하고 stale hash를 유지해도 수치가 표시됨을 재현해 H06만 `CHANGES_REQUESTED`로 판정했다. H05의 `VERIFIED`는 유지한다.
- Workstream 80 H07은 H06 stale-hash False PASS를 닫았고 실제 브라우저에서 세 runtime control, console error 0, 발표 안내 문구의 1280×720·1440×900·1920×1080 한 줄과 horizontal overflow 0을 확인했다. 그러나 schema-valid TMR `p=0.001`의 projection `2.998e-06`을 JavaScript가 `0.000002998`로 직렬화해 production hash와 달라지고 정상 record를 거부했다. Python/JavaScript canonical number parity가 남아 H07은 `CHANGES_REQUESTED`, H05 `VERIFIED`는 유지한다.
- Workstream 80 H08은 production canonical preimage로 일반 Python/JavaScript number parity와 기존 stale-hash 공격을 닫았고 Product 10개 테스트, numeric boundary controls와 실제 브라우저 세 runtime control·console warning/error 0을 통과했다. 그러나 result의 numeric `0`만 `-0`으로 바꾸고 기존 preimage·hash를 유지한 공격을 `jsonDeepExact()`가 수용해 H08은 `CHANGES_REQUESTED`다. assurance는 계속 `HOLD`이며 H05 `VERIFIED`는 유지한다.
- Workstream 80 H09는 `Object.is()` number 비교로 `+0/-0` 양방향 본문 변조를 닫았다. Product 10개 테스트, 직접 signed-zero 공격, H08 numeric parity·stale-hash 회귀와 실제 브라우저 WATCHDOG/TMR/SEL·console warning/error 0을 독립 재현해 H09 runtime integrity 패키지를 `VERIFIED`로 판정했다. 실제 API·environment·parts evidence·GCP resource는 미통합이고 assurance는 계속 `HOLD`다.
- commit 직전 전체 회귀에서 schema 14개·정상 5개·실패 116개, simulation 55개, environment 23개, Assurance 공격 실행 47개·False PASS 0, Product 10개와 raw-manifest preflight 2개를 통과했다. live GCP `ASR-D02` 1개는 계속 `NOT_EVALUATED`다.
- Workstream 10 H06, 20 H03, 60 H03과 80 H09는 commit `32b6131`, Workstream 40 H04와 90 H03 문서 패키지는 commit `b2c8ef6`로 통합했다. 이 Git 통합은 실제 environment contract, 실제 parts evidence, 실제 GCP, 실제 사용자 검증 또는 radiation assurance 완료를 뜻하지 않는다.
- Workstream 80 H10은 기존 H09 consumer를 그대로 사용한 60→999 stale-preimage 공격 데모를 구현했다. Product 11개 테스트와 실제 브라우저 1280×720·1440×900에서 정상 → 공격 입력 → 대상 record 수치·ID·hash 비노출 및 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD` → Reset, horizontal overflow 0과 console warning/error 0을 독립 재현해 `VERIFIED`로 판정했다. 사람 동선은 `PLANNED 70초`, 실제 assurance는 계속 `HOLD`다.
- Workstream 90 H04는 `PLANNED 85초` 교체 산술과 안전 경계는 통과했지만 H10 완료 후에도 실제 control label·순서·Reset 관측 대신 `H10 대조 필요`와 `H10 미제출` 문구를 남겼다. H04는 `CHANGES_REQUESTED`이며 H05에서 문서 정합성만 보완한다.
- Workstream 90 H05는 H04의 pre-H10 상태와 placeholder를 제거하고 검증된 H10 실제 control 5개·경고 label·정상/공격/차단/Reset 관측에 runbook을 정렬했다. stale 문구 0건, exact label 대조, `85/240/420초` 산술과 `git diff --check`를 독립 재현해 문서 정합성 패키지를 `VERIFIED`로 판정했다. 시간은 계속 `PLANNED`이며 사람 리허설과 Stage 9은 미완료다.
- Workstream 80 H14의 Product 13 tests와 H09 문서 정합성은 재현했고 사용자는 실제 발표 장치의 기본 wheel 이동을 수용했다. 그러나 부드러운 전환 소실, Product의 범위 제한 반복, TMR·SEL 가정과 현재 비채택 상태의 설명 부족으로 H14와 Workstream 90 H09를 `CHANGES_REQUESTED`로 판정했다. 첫↔마지막 wrap은 사용자 결정으로 후속 Exit Gate에서 제외한다.
- Workstream 80 H15는 번호 없는 표지, 고정 화면 smooth entry, Product 범위 문구 축약, ECC 채택 이유, equal metric grid, runtime 확장 예시 구분, 보증 판단 재구성을 담당한다. Workstream 90 H10은 같은 구조의 초심자 대본·용어집·Q&A를 병렬 정렬한다. 도료·코팅 차폐는 이번 데모 범위에서 제외한다.
- 사용자가 채팅에 전달할 작업 지침과 change request는 해당 `docs/workstreams/<workstream>/instructions/`에 생성해 링크로 전달한다. 작업 채팅이 완료 후 제출하는 handoff는 같은 계층의 `handoffs/`에 저장한다. 두 폴더 모두 Git에서 제외하며, 기존 추적 handoff 6개는 로컬 파일을 보존한 채 Git index에서 제거했다. 작업 지침에는 항상 `병렬 가능 작업`을 포함하고 후보가 없으면 그 이유와 선행 의존성을 적는다.

## 알려진 한계

- 승인된 실제 환경 contract·실제 부품 시험자료·과학적 교차검산이 없어 실제 방사선 보증을 검증할 수 없다. Git 밖 SPENVIS 원본 bundle과 parser 후보는 제품 판정 입력으로 발행하지 않았다.
- Workstream 10~90의 현재 `BRIEF.md`·`CURRENT.md`는 존재한다. 이후 새 채팅을 만들 때만 해당 채팅의 회차가 표시된 handoff를 추가한다.
- 병렬 채팅은 같은 파일을 동시에 수정하지 않고 마지막 `INTEGRATED` 기준선만 의존해야 한다.
- Workstream 경계를 넘겨 생성된 산출물은 올바른 십 단위 채팅으로 소유권을 이전하고 다시 `READY_FOR_REVIEW`를 제출해야 한다.

## 다음 권장 작업

1. Workstream 30이 확보한 SPENVIS bundle에 provider job reference, action별 권리, 승인 raw manifest와 과학적 교차검산을 연결해 environment contract 발행 가능성을 판정한다.
2. Workstream 40이 고정된 COTS 승인 검토 대상 `23LC1024-I/SN`에 권리 확인 원문, ESA 비행·시험 article의 exact suffix/lot/die identity, 시험 조건·임무 적용성, TID와 필요한 SEE coverage를 연결한다.
3. Workstream 70이 `D02-02` generation 404를 구조화된 fail-closed result로 정규화하고 `D02-05` expected exact-part identity binding을 구현한다. 새 revision 배포 후 Workstream 60이 동일 두 공격을 재실행하되, 현재 실패 증거와 target lock은 보존한다. 나머지 12개 `ASR-D02` 공격은 test endpoint/IAM 범위를 별도 승인받기 전 `NOT_EVALUATED`다.
4. 실제 environment·part contract가 생기면 Workstream 80이 합성 fallback과 분리된 Evidence-to-Decision 경로와 원문 locator를 Product에 연결한다.
5. Workstream 90은 실제 사용자 1명의 5분 실행·판정 이유·다음 행동 탐색을 측정하고 COTS·과학·비용 주장을 출처·범위에 맞게 정리한다.
6. 공통 계약·Core 수정 시에만 인접 회귀를 넓히고, 전체 회귀와 commit·push는 검증 가능한 통합 단위가 정리된 뒤 한 번 수행한다. 실제 environment·parts evidence가 없으면 방사선 assurance는 계속 `HOLD`다.

## 다음 Control Tower 검증 항목

- 프로젝트 구조가 문서와 일치하는가?
- 작업 채팅이 현재 작업 패키지의 `READY_FOR_REVIEW` 인수인계를 남겼는가?
- 실제 변경과 체크리스트 완료 표시가 일치하는가?
- Git에 올릴 변경만 명확히 분리돼 있는가?
