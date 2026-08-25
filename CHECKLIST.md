# SPECTRA 18:00 제출 체크리스트

이 파일만 현재 제출 승인 Gate로 사용한다. 장기 과학 MVP와 제출 후 확장은 [`docs/MVP.md`](docs/MVP.md), 상세 이력은 Workstream `CURRENT.md`에 둔다.

## A. 이미 완료된 제출 기반

- [x] 프로젝트 범위·비범위·데이터 분류·EvidencePacket 계약
- [x] 결정론적 합성 TID·SEE·차폐·ECC·정책·Change Impact
- [x] Core 고정 공격 29건 False PASS 0 기준선
- [x] 실제 GCP Cloud Run Agent 3개·Workflows·Storage·IAM·Logging 합성 E2E
- [x] H06 event contract, H07 actual read-only receipt, H08 `LIVE_API` timeline data
- [x] 환경 intake/readiness gate와 실제 후보의 fail-closed receipt
- [x] `23LC1024-I/SN` COTS reference package와 `NOT_COMPARABLE / HOLD` gate
- [x] Product/Evidence Console의 Cloud Run/로컬 PDF·TXT 검사·저장 GCP 기록·문서별 결과표
- [x] 발표 Phase 01~03 bounded workflow와 외부 blocker 표시
- [x] 실제 evidence·합성 fallback·미지원 범위의 구분
- [x] 구조화된 다중 문서 Mission Case Core: exact identity·TID/SEU·사건별 coverage를 source-local로 검증하고 미지원 시험 조건은 HOLD
- [x] 원문 3종 Mission Package adapter: 임무 조건·승인 BOM·방사선 시험 UTF-8 문서를 manifest SHA-256과 원문 줄에 결속하고, v2 승인 정책 및 권리 snapshot을 배포 신뢰 저장소와 대조한 뒤 Mission Case Core로 전달한다. 세 원문·정책·권리·이력 앵커는 Core 입력/출력 해시에 포함되며 변조·누락·자기 승인 주장은 fail-closed한다.
- [x] 변경 영향 가치 증명 Core: 기간·차폐·부품·사건별 근거 변경의 재검토 범위와 다음 행동을 결정론적으로 반환
- [x] 실제 PDF/TXT numeric 후보 추출: TID dose·dose rate·LET·cross-section·fluence·energy·temperature·voltage·sample size·LDC를 원문 span·단위에 결속하며 관측값을 rating으로 승격하지 않음
- [x] NASA·ESA 공개 관측값 3종을 출처 URL이 있는 `PUBLISHED SOURCE SUMMARY` 수동 fixture로 추가하고 실제값도 최종 HOLD 유지
- [x] 한글 수동 fixture 파일명을 URL 인코딩해 브라우저 요청 전 `LOCAL_CONSOLE_UNAVAILABLE`로 실패하던 경로 수정

## B. 공격 작업 마무리

- [x] ASR-D02 Phase 1 control + 공격 4건 actual evidence 보존
- [x] `D02-02` generation 404 구조화 fail-closed 로컬 보완
- [x] `D02-05` expected exact-part identity hash binding 로컬 보완
- [x] 직접 테스트·YAML parse·기존 evidence 재평가
- [x] 최소 범위 새 GCP revision 배포
- [x] 새 deployment target identity·source hash 잠금
- [x] control + `D02-02/04/05/10` batch 재공격
- [x] False Accept 0 / False PASS 0 / unexpected 0 확인
- [x] 최종 attack evidence와 CURRENT/발표 수치 동기화

## C. 발표·데모

- [x] GCP 구조 뒤에 공격 방어·신뢰성 슬라이드 1장 추가
- [x] Slide 09는 공격 횟수 카운터를 제거하고 Schema·Core·Identity·Hash·Fail-Closed·배포 격리의 시스템 조치에 집중
- [x] 로드맵을 실제 제출·발표에서 제거하고 비즈니스 근거를 추가한 `Cover + 01~09 + Closing`, 총 11장과 7분 대본을 동기화
- [x] 공개 Cloud Run 1280×720 제출 deck 11장 전체 x/y overflow 0
- [x] 새 발표 deck 탭에서 console warning/error 0 확인; Console 자동화 주입 `MutationObserver` 오류는 앱 소스에 해당 API가 없어 별도 도구 잡음으로 분리
- [x] Evidence Console 핵심 동선 smoke test
- [x] 공개 Cloud Run `spectra-demo-console` 배포: 발표 자료·문서 검사·임무·부품·시험 연결·저장된 공격 검증·문서별 결과표를 서버 실행 없이 접근
- [x] Cloud Run 전용 최소권한 service account, 실제 revision 설정(min 0/max 100·concurrency 20·timeout 120초), 업로드 임시 처리 후 삭제·GCS 미저장 문구와 동작 정렬
- [x] 공개 URL에서 합성 PDF `확인 2 / 불일치 0 / 추가 입력 1`, Mission Case, 저장 공격 2건, 공개 카탈로그·감사로그 브라우저 검증
- [x] Evidence Console 1280×720 첫 화면에 `HOLD · 중단 위치 · 7 / 7의 제한된 의미 · 다음 행동`이 스크롤 없이 함께 보이도록 정리
- [x] GCP Logs를 정상 실행·body hash 위조·endpoint override별로 구분하고, 각 실행의 run ID와 저장 snapshot에 존재하는 정상 correlation ID, 최종 `HOLD`를 화면만으로 추적 가능하게 표시; 공격 correlation은 근거에 없음을 그대로 표시
- [x] GCP Logs 화면에 `ENDPOINT_OVERRIDE_FORBIDDEN · Agent 호출 0회` 근거 표시
- [x] 근거 범위를 넘던 `8-event hash chain 검증`을 `저장 이벤트 무결성 검증`으로 낮춤
- [x] Local PDF parser와 저장 GCP Agent 경로가 아직 별도라는 사실을 Slide 06·08·시연 대본에서 같은 문장으로 유지
- [x] GCP 13개 로그 표보다 먼저 핵심 세 결론 노출: `정상 실행도 HOLD · hash mismatch 조기 차단 · endpoint 사전 차단`
- [x] `?presentation=1` 발표 모드의 메뉴를 `문서 검사 · 임무·부품·시험 연결 · 저장된 공격 검증 · 문서별 결과표`로 정리하고 공개 카탈로그를 같은 콘솔 내부에 표시
- [x] NASA Landsat 9·ESA Sentinel-2 임무 조건, Microchip 23LC1024 명세, NASA·ESA 방사선 시험 공개값 요약을 분리된 입력 축으로 추가
- [x] 전용 공개 GCS bucket에 test-data 17개 객체와 catalog·audit·deployment receipt를 업로드하고 비로그인 HTTP 200·CORS·generation 확인
- [x] `문서별 결과표`를 `문서 · 자료 역할 · 처리 경로 · 현재 결과 · 보류 지점` 5열로 정리하고, 문서 15개·공개 요약 6개·최종 단계 도달 5개·판단 보류 15개, 세 입력 조합 4개와 16-event hash chain + GCP receipt를 브라우저 확인
- [x] 필수 입력 일부가 누락돼도 확인 가능한 수치의 원문 위치·숫자 형식·단위·기본 입력 범위 검사를 계속 수행하고 `확인 / 불일치 / 추가 입력 필요`를 분리
- [x] Local Console에는 실행 Agent가 아닌 책임 역할을 표시하고, `Document Parser Agent` 오인을 제거해 실제 `pypdf/TXT` 단계는 `문서 입력·추출 단계`로 명시
- [x] 앞 단계가 보류돼도 완료·불일치·추가 입력 필요 ledger를 최종 보류 검토 단계에서 대조하고, 가능한 검사 결과를 숨기지 않음
- [x] 실제 NASA Micron 요약 + 잘못된 23LC1024 입력으로 `3개 확인 · 2개 불일치 · 2개 추가 입력 필요 · 부품·시험 근거 검토 역할에서 보류` 재현
- [x] 공개 GCP Catalog 15개 행에 부분 확인 집계와 최초 보류 책임을 반영
- [x] 공개 revision `spectra-demo-console-00008-rwk`에서 deck 11장, Cloud Run PDF, 승인·권리 바인딩 Mission Case, 변경 영향, 저장 공격 기록, 공개 catalog를 브라우저에서 preflight
- [x] 결과표 가독성·Mission Case 신뢰 바인딩 개선본 Cloud Run 재배포 — 1280×720 deck overflow 0, 네 메뉴 고정, 15개 문서 결과표·감사 기록, 브라우저 warning/error 0 확인
- [ ] 사람 7분 발표·탭 전환 리허설 2회 측정: 중앙값 6분 30초 이하, 최대 7분, Cloud Run PDF → Mission Case 2회 → 저장 공격 기록 → Closing 포함 — 자동 클릭 동선과 시간 산술은 확인, 사람 낭독은 `NOT_MEASURED`
- [x] 시연 실패 fallback 확정: 새 값을 만들지 않고 저장 화면 또는 말로 `HOLD · 이유 · 다음 행동`만 설명

## D. 메시지·비즈니스·책임 경계

- [x] 실제 파일럿 사용자·고객 인터뷰·구매 의향·가격·ROI가 없음을 확인
- [x] 실제 계획이 없는 `첫 파일럿 사용자는 ...` 문장을 발표·대본에 추가하지 않음
- [x] 타깃 사용자 문제를 NASA·ESA·GAO 근거와 함께 정리: `COTS 근거의 부족·분산·재검토`
- [x] 비즈니스 가치는 측정되지 않은 절감률 대신 현재 제품 동작으로 설명: `빠진 근거와 재검토 지점을 승인 전에 찾고 다음 행동을 반환`
- [x] 구매자·예산 책임자·도입 방식은 검증 전까지 발표 사실로 단정하지 않고 `미검증 / 향후 검증 대상`으로 유지
- [x] 사람 팀 역할·협업 성과는 확인된 사실이 없어 만들지 않고, Mission·Parts·Assurance는 시스템 증거 책임 분리라고 Q&A에 고정
- [x] `reviewer / owner`는 개인 이름이 아니라 결측을 해결할 조직 역할임을 Q&A 답변으로 고정
- [x] 승인 인계 설명을 Q&A에 고정: `SPECTRA는 자동 승인하지 않고, 부족한 근거와 다음 행동을 표시하며 최종 판단은 조직이 지정한 기술 검토자가 담당`
- [x] 실제 운영 계약 전에는 Evidence Console에 임의의 담당자·승인 상태·receipt identity를 생성하지 않음
- [x] `7 / 7`을 일반 PDF 정확도 100%, 후보 추출을 승인 exact-part 검증, Workflow 성공을 방사선 assurance로 말하지 않는 발표 금지 문구 재확인
- [x] 기술 용어를 대본에서 한국어로 축약: 동일 제조사·부품번호·공정·로트, 같은 규칙의 입력 해시, 항상 같은 오류 코드, 같은 저장 객체 버전

## E. 문서·제출

- [x] README·PROJECT_OVERVIEW·MVP·ROADMAP·CHECKLIST 역할 정리
- [x] 과거 채팅/Workstream 진행 규칙을 현재 실행 기준에서 제거
- [x] Stage 1·2·5 완료, Stage 3·4·8 제한 완료, Stage 6·7·9 오늘 활성으로 재분류
- [x] Phase 01~03 bounded 완료와 외부 확장을 분리
- [x] 최신 전체 자동 회귀: unit 436개와 Assurance 공격 실행 47개, failure·False PASS 0
- [x] 비밀정보·private raw evidence·불필요한 생성물 Git 경계 확인
- [x] 이전 제출 Release 체크포인트 commit·push (`516701c`, `origin/main`)
- [x] 최신 11장 발표본·7분 대본·audit 후속 변경을 README·PROJECT_OVERVIEW·MVP·ROADMAP·CURRENT와 최종 동기화
- [x] ASR-D02 historical H05 reconciliation이 최신 remediation manifest를 역사 증거에 잘못 요구하던 회귀 수정: H05 target을 보존하고 최신 target으로 재라벨하지 않음
- [x] `git diff --check`, Python compile, 공개 catalog hash·fixture 정합성 재실행
- [x] 발표·Evidence Console 핵심 브라우저 회귀: 공개 URL 1280×720 deck overflow 0, Cloud Run PDF·Mission Case·저장 공격·catalog 동선 정상
- [x] 제출 파일·서버 URL·두 탭 순서 최종 확인: Presentation → `evidence-console.html?presentation=1`
- [x] 최신 변경 전체 로컬 검증 완료
- [x] 다섯 persona 최신 독립 audit: 평균 84.4점, 전원 `CONDITIONAL GO`; `AUDIT_LATEST_2026-08-25.md`에 원문·공통 P0·즉시 보완 기록
- [x] 사용자 확인에 따라 현재 검증 단위를 commit·push 대상으로 승인

## 다음 실행 순서

1. [x] P0-1 · GCP Logs와 대본의 정상/공격 실행 근거 일치
2. [x] P0-2 · Slide 09 공격 횟수 블록 제거, 안정성 설계 조치 중심으로 정리
3. [x] P0-3 · Evidence Console 720p 핵심 결론 가시성
4. [x] P0-4 · 브라우저 제품 오류 분리와 최신 서버 preflight
5. [ ] P0-5 · Cloud Run PDF → Mission Case 2회 → 저장 공격 기록 → Closing 자동 클릭 동선·fallback 완료; 사람 7분 낭독 리허설 2회만 남음
6. [x] P1-1 · 타깃 사용자 문제·비즈니스 가치 문장 정리, 허위 파일럿 주장 금지
7. [x] P1-2 · reviewer/자동 승인 경계와 기술 용어 Q&A 정리
8. [x] P1-3 · 문서 동기화·직접 테스트·최종 회귀
9. [x] Release · 사용자 확인에 따라 현재 검증 단위를 commit·push; 사람 7분 리허설은 별도 미완료

## 제출 후 Backlog — 오늘 Gate 아님

- ASR-D02 나머지 12건, IAM/OIDC·test endpoint 공격
- 실제 SPENVIS/NASA connector와 승인 environment contract
- exact flight/test suffix·lot/die·TID/SEE evidence packet
- Document AI·Gemini·authenticated HITL
- 실제 CAD/3D shielding, Cloud SQL·BigQuery·KMS, penetration test
- 사용자 인터뷰·가격·절감 시간 검증

## 제출 판정

- `READY_TO_SUBMIT`: B·C·D·E의 P0 및 제출 필수 미완료 항목이 모두 닫힘
- `SUBMISSION_BLOCKED`: 배포 재검증 또는 발표/문서 QA가 실패
- 실제 방사선 보증 상태는 제출 여부와 무관하게 `HOLD`
