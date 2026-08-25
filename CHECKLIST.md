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
- [x] Product/Evidence Console의 local PDF/TXT·저장 GCP 기록·batch review
- [x] 발표 Phase 01~03 bounded workflow와 외부 blocker 표시
- [x] 실제 evidence·합성 fallback·미지원 범위의 구분
- [x] 구조화된 다중 문서 Mission Case Core: exact identity·TID/SEU·사건별 coverage를 source-local로 검증하고 미지원 시험 조건은 HOLD
- [x] 변경 영향 가치 증명 Core: 기간·차폐·부품·사건별 근거 변경의 재검토 범위와 다음 행동을 결정론적으로 반환

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
- [x] Slide 09에 actual GCP 공격 평가 범위를 `4 / 16 평가 · SAFE_FAILURE 4 · False Accept 0 · False PASS 0 · 12 NOT_EVALUATED`로 인접 표시하고 `FINAL HOLD` 경계 유지
- [x] 로드맵을 실제 제출·발표에서 제거하고 비즈니스 근거를 추가한 `Cover + 01~09 + Closing`, 총 11장과 7분 대본을 동기화
- [x] localhost 1280×720 제출 deck 11장 전체 x/y overflow 0
- [x] 새 발표 deck 탭에서 console warning/error 0 확인; Console 자동화 주입 `MutationObserver` 오류는 앱 소스에 해당 API가 없어 별도 도구 잡음으로 분리
- [x] Evidence Console 핵심 동선 smoke test
- [x] Evidence Console 1280×720 첫 화면에 `HOLD · 중단 위치 · 7 / 7의 제한된 의미 · 다음 행동`이 스크롤 없이 함께 보이도록 정리
- [x] GCP Logs를 정상 실행·body hash 위조·endpoint override별로 구분하고, 각 실행의 run ID와 저장 snapshot에 존재하는 정상 correlation ID, 최종 `HOLD`를 화면만으로 추적 가능하게 표시; 공격 correlation은 근거에 없음을 그대로 표시
- [x] GCP Logs 화면에 `ENDPOINT_OVERRIDE_FORBIDDEN · Agent 호출 0회` 근거 표시
- [x] 근거 범위를 넘던 `8-event hash chain 검증`을 `저장 이벤트 무결성 검증`으로 낮춤
- [x] Local PDF parser와 저장 GCP Agent 경로가 아직 별도라는 사실을 Slide 06·08·시연 대본에서 같은 문장으로 유지
- [x] GCP 13개 로그 표보다 먼저 핵심 세 결론 노출: `정상 실행도 HOLD · hash mismatch 조기 차단 · endpoint 사전 차단`
- [x] `?presentation=1` 발표 모드에서 `여러 문서 표` 탭을 숨기고 Local·GCP 두 모드만 표시
- [x] 최신 코드로 port 8765 서버 재시작 후 deck 11장, Local sample, GCP 3 runs를 브라우저에서 preflight
- [ ] 사람 7분 발표·탭 전환 리허설 1회 측정: 목표 6분 30초 이하, 최대 7분, Local PDF → GCP Logs → Closing 포함 — 자동 클릭 동선과 6:30 시간 산술은 확인, 사람 낭독은 `NOT_MEASURED`
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
- [x] 전체 로컬 회귀 1회
- [x] 비밀정보·private raw evidence·불필요한 생성물 Git 경계 확인
- [x] 이전 제출 Release 체크포인트 commit·push (`516701c`, `origin/main`)
- [x] 최신 11장 발표본·7분 대본·audit 후속 변경을 README·PROJECT_OVERVIEW·MVP·ROADMAP·CURRENT와 최종 동기화
- [x] 변경 범위 직접 테스트 23개와 `git diff --check` 재실행
- [x] 발표·Evidence Console 핵심 브라우저 회귀: 1280×720 deck overflow 0, Local·GCP 동선 정상. 앱 코드 경고·오류는 없고 Browser 자동화 주입 `MutationObserver` 오류 1건은 앱 소스에 해당 API가 없어 도구 잡음으로 분리
- [x] 제출 파일·서버 URL·두 탭 순서 최종 확인: Presentation → `evidence-console.html?presentation=1`
- [x] 최신 변경 전체 로컬 검증 완료
- [ ] 사람 리허설 후 사용자 확인 시 한 번에 commit·push

## 다음 실행 순서

1. [x] P0-1 · GCP Logs와 대본의 정상/공격 실행 근거 일치
2. [x] P0-2 · Slide 09 공격 평가 범위와 `12 NOT_EVALUATED` 표시
3. [x] P0-3 · Evidence Console 720p 핵심 결론 가시성
4. [x] P0-4 · 브라우저 제품 오류 분리와 최신 서버 preflight
5. [ ] P0-5 · 자동 클릭 동선·fallback 완료; 사람 7분 낭독 리허설만 남음
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
