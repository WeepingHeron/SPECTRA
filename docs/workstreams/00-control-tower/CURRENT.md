# 00 Control Tower — Current State

## Status

`IN_PROGRESS`

## Last verified

- 날짜: 2026-08-24
- 프로젝트 경로: `/Users/taehoon/Desktop/IAA/SPECTRA`
- Git 통합 체크포인트: 직전 기준 `1cbf7e5` 위 Roadmap Lab·NASA snapshot gate·발표 truth boundary·Product Workspace 동선을 최종 검증했다. 이 문서를 포함하는 main commit으로 `origin/main`에 통합하며 ignored `instructions/`와 Git 밖 private evidence는 포함하지 않는다.

## 현재 확인된 산출물

- `PROJECT_OVERVIEW.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- `docs/workstreams/README.md`
- `docs/workstreams/00-control-tower/BRIEF.md`
- `docs/workstreams/00-control-tower/CURRENT.md`
- `docs/workstreams/00-control-tower/CONTROL_TOWER_SESSION_TEMPLATE.md`

## 현재 진실

- 2026-08-24 Roadmap Lab을 발표 중심 3단계 제품 시연으로 전면 재설계했다. 7개 기술 카드를 주 동선에서 제거하고 `자료 연결 → AI 보조 검토 → 판단과 다음 행동`만 남겼으며, 상세 route는 Q&A 보조 링크로 유지했다. 직접 테스트 8+17개와 localhost 1280×720의 두 번 `다음` 클릭, 마지막 초기화, 전체·story·answer overflow 0을 확인했다. 이는 표현·시연 동선 `VERIFIED`이며 실제 evidence·외부 연동 완료가 아니다.
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
2. Workstream 40이 승인 BOM exact-part 1개를 고정하고 권리 확인 원문, 시험 조건·임무 적용성, TID와 필요한 파괴성 SEE coverage를 연결한다.
3. Workstream 60이 사용자 승인과 고정 revision 범위를 확인한 뒤 실제 GCP `ASR-D02`를 수행하고 False Accept/PASS와 관찰 증거를 제출한다. 실행 전 상태는 `NOT_EVALUATED`다.
4. 실제 environment·part contract가 생기면 Workstream 80이 합성 fallback과 분리된 Evidence-to-Decision 경로와 원문 locator를 Product에 연결한다.
5. Workstream 90은 실제 사용자 1명의 5분 실행·판정 이유·다음 행동 탐색을 측정하고 COTS·과학·비용 주장을 출처·범위에 맞게 정리한다.
6. 공통 계약·Core 수정 시에만 인접 회귀를 넓히고, 전체 회귀와 commit·push는 검증 가능한 통합 단위가 정리된 뒤 한 번 수행한다. 실제 environment·parts evidence가 없으면 방사선 assurance는 계속 `HOLD`다.

## 다음 Control Tower 검증 항목

- 프로젝트 구조가 문서와 일치하는가?
- 작업 채팅이 현재 작업 패키지의 `READY_FOR_REVIEW` 인수인계를 남겼는가?
- 실제 변경과 체크리스트 완료 표시가 일치하는가?
- Git에 올릴 변경만 명확히 분리돼 있는가?
