# 90 Business & Presentation — Current

## 상태

`RELEASE_VERIFIED — 11-slide 7-minute deck and public Console; measured rehearsal pending`

## Final Slide 08 & Public Console QA — 2026-08-25

- Slide 08 제목은 `실제 GCP에서는, 세 역할이 한 가지 실행의 근거를 나눠 검증한다.`로 확정했다. Mission·Parts·Assurance는 동일 Workflow의 서로 다른 증거 책임이며 같은 계산을 세 번 수행한다는 뜻이 아니다.
- 공개 1280×720 브라우저에서 deck 가로 overflow 0과 새 제목 표시를 확인했다. Console은 항목별 결과를 세 카드로 분리하고 문서 전체 overflow 없이 요약 panel만 스크롤한다.
- 공격 검증은 공개 live 쓰기 endpoint로 확대하지 않았다. 공개 호출자에게 Workflows 실행·Storage 쓰기 권한을 열 경우 반복 실행 비용, 로그 오염, 내부 경계 탐색과 service account 권한 확대 위험이 생기므로 독립 확인된 snapshot을 재생한다.
- unit 436개와 Assurance 공격 실행 47개, 공개 Cloud Run 동선, 문서 정합성과 현재 revision을 최종 확인했다. 사람 낭독·클릭 시간은 계속 `NOT_MEASURED`다.

## Cloud Presentation Runtime & Script v7 Refresh — 2026-08-25

- 발표 자료와 검증 콘솔의 기준 URL을 `https://spectra-demo-console-mwmfe3da5q-du.a.run.app`로 전환했다. 발표자는 서버를 켜지 않고 Presentation과 Evidence Console 두 탭만 연다. localhost는 Cloud Run 장애 시 fallback이다.
- 시작 문장은 전문어 `HOLD`와 숫자 중심 비유를 제거하고 `임무 조건·부품 정보·방사선 시험 자료를 한 흐름에서 대조해 확인한 것과 더 필요한 것을 보여준다`로 교체했다. Closing도 같은 제품 가치로 정렬했다.
- 대본은 필수 입력이 빠져도 확인 가능한 항목은 계속 검사하고 완료·불일치·추가 입력으로 나눈다는 현재 동작을 설명한다. 문서 파서와 저장 GCP Agent 경로는 분리되어 있고, 저장 공격 snapshot을 live 공격 실행으로 주장하지 않는다.
- Cloud Run 공개 URL의 `문서 검사`·`임무·부품·시험 연결`·`저장된 공격 검증`·`문서별 결과표`를 실제 브라우저에서 검증했다. 7분 시간표는 계속 계산값이며 사람 낭독·클릭 실측은 `NOT_MEASURED`다.

## Evidence-backed Business Slide & Simplified Flow — 2026-08-25

- Slide 02 본문은 특정 catalog part와 위성 사례를 발표 핵심에서 내려 `상용 기성 부품 (COTS)`만 표시한다. 엔진 범위를 넘는 `임무 적합성 입증` 대신 `조달 가능성 ≠ 방사선 근거 검증`으로 고치고, 정확한 부품 식별·TID·SEU·파괴성 SEE coverage·권리를 임무 조건과 대조한다고 명시했다. 본문에 없는 QML-V 용어 설명은 제거했다.
- 차폐 설명을 발표 첫 본문으로 이동하고 `01 · RADIATION & SHIELDING BASICS`로 재구성했다. 비전문가가 먼저 `우주 방사선 → 알루미늄 차폐 → 전자부품`을 이해한 뒤 문제 정의로 들어가며, TID·SEU 계산과 파괴성 SEE 시험 근거 확인을 구분한다.
- 실제 제출·발표 흐름은 `01 차폐 기초 → 02 COTS → 03 문제 정의 → 04 외부 근거가 확인한 사용자 부담 → 05 기존 방식 → 06 SPECTRA 전체 흐름 → 07 판단 원칙 → 08 GCP → 09 무결성 설계`다. 로드맵은 프로젝트에는 유지하되 제출 deck과 7분 발표에서 제외한다.
- Slide 03 제목은 도식에 없는 `계산`을 제거하고 `위성 부품을 검토할 자료가 여러 문서에 흩어져 있다`로 맞췄다. 우측은 사람 역할을 특정하지 않는 `흩어진 자료에서 확인해야 할 세 가지` 아래 `부품·조건·범위` 질문을 배치했다. 실제 공정·로트별 방사선 결과 비교 데이터는 없으므로 차이가 결과를 바꾼다고 주장하지 않고, 공개 COTS 자료의 패키지 불일치와 lot/die 미보고 때문에 동일 근거로 단정할 수 없다는 현재 증거 경계만 설명한다.
- Slide 04 문제 정의는 SPECTRA가 없는 근거를 보충한다는 오해를 막기 위해 `COTS 근거의 부족`을 제거하고, 공식 자료가 뒷받침하는 `근거의 분산과 반복 검토`로 한정했다.
- Slide 06의 `부품·시험·조건을 대조`는 현재 지원하지 않는 시험 조건까지 직접 비교한다는 오해가 있어 `부품·시험·조건의 연결 상태 확인`으로 낮췄다. 임무 조건·승인 BOM·방사선 시험 합성 원문 3개는 manifest 해시와 원문 줄에 결속해 Mission Case Core까지 연결했으며, exact identity·사건별 coverage·TID/SEU를 대조한다. 비교 불가능한 조건은 일치한다고 추정하지 않고 blocker·출처 위치·다음 행동과 함께 HOLD한다. 일반 자유형식 PDF/TXT의 자동 다중 문서 의미 매핑은 아직 범위 밖이다.
- Slide 07의 지원 범위는 구현에 맞춰 정밀화했다. EvidencePacket은 구조화된 임무 환경·부품 시험 근거·완화 가정을 판단 규칙과 출처에 연결하며, 일부 근거가 있어도 필수 근거가 빠지면 HOLD한다. Multi-Agent는 세 역할 모두가 같은 대조를 반복하는 구조가 아니라 Mission·Parts가 각 범위를 검증하고 Assurance가 입력 결속과 응답 해시를 재확인하는 구조다.
- 전체 장수는 `Cover + 01~09 + Closing`, 총 11장이다. Slide 04는 NASA·ESA·GAO 자료를 타깃 사용자별 애로사항에 연결하고, 실제 시간 절감 효과와 구매 의향은 사용자 조사가 필요하다고 분리한다.
- Slide 04 하단은 ESA를 유럽우주국, GAO를 미국 정부감사원으로 풀어 쓴다. Document AI·Gemini를 포함한 향후 확장 내용은 주 발표에서 말하지 않는다.
- canonical `FINAL_PRESENTATION_SCRIPT_7MIN.md` v7을 현재 11장과 검증 콘솔의 `문서 검사 · 임무·부품·시험 연결 · 저장된 공격 검증` 시연에 맞췄다. 발표·시연·탭 전환 6분 30초와 돌발 여유 30초를 합쳐 7분이며, 사람 낭독·클릭 측정은 `NOT_MEASURED`다.
- 콘솔 문구는 `실제 실행`을 `지금 실행`으로 바꿔 실제 evidence와 실행 시점을 구분하고, `미승인 후보`를 `원문에서 찾음`, `최종 보류 책임`을 `판단을 보류한 역할`로 교체했다. 네 메뉴는 `문서 검사 · 임무·부품·시험 연결 · 저장된 공격 검증 · 문서별 결과표`로 입력과 결과가 바로 드러나게 정렬했다.
- 발표 운영은 `발표·시연 7분 + 별도 질의응답 3분`으로 고정했다. Slide 04와 05는 합치지 않고 각각 사용자 부담과 기존 방식 대비라는 단일 역할을 유지한다. Slide 05는 Slide 04와 같은 넓은 좌우 대비 레이아웃으로 재구성하고, 네 질문과 네 대응을 큰 글자로 일대일 정렬했다.
- 주 발표 운영은 Presentation과 named `spectra-demo` 검증 콘솔 두 브라우저 탭만 사용한다. 콘솔은 발표 후반에 직접 전환하고, Slide 08의 링크도 `?presentation=1`을 사용한다. 네 번째 `문서별 결과표` 메뉴에는 공개 GCP 카탈로그와 감사로그를 같은 콘솔 안에 통합했지만 7분 본 시연에서는 열지 않는다. `임무·부품·시험 연결`은 합성 원문 3개의 해시·필드 위치를 adapter로 결속한 뒤 production Core의 다중 문서 대조와 변경 영향 분류를 실제 호출하되, 실제 승인 근거·방사선 assurance로 확대하지 않는다.
- Slide 08 GCP 화면은 로컬 parser와 저장 GCP 경로를 분리하고 무결성 표현을 `저장 이벤트 무결성 검증`으로 한정한다. GCP Console은 정상·body hash 위조·endpoint override의 run 결속과 정상 correlation ID, 최종 HOLD를 먼저 표시한다. Slide 09는 적은 공격 횟수를 전면에 내세우지 않고 Schema·Core·Identity·Hash·Fail-Closed·배포 격리의 시스템 조치에 집중한다.
- 01~09의 영문 kicker를 장별 역할 중심으로 축약하고, 큰 한글 제목은 결론, 바로 아래 한 줄은 근거·의미를 설명하도록 통일했다. 밑줄은 큰 한글 제목 내부의 핵심 구절에만 적용한다. Slide 02 비교표는 두 줄 영문 label과 오른쪽 설명을 수직 중앙 정렬했고, Slide 04의 양쪽 비교 본문·panel label을 발표 화면 크기로 확대했다.
- 최신 localhost 1280×720에서 11장 전체 x/y overflow 0과 Slide 02~06의 가독성을 시각 확인했다. 이번 변경의 Product·Simulation 직접 테스트 51개와 `git diff --check`가 통과했고 console warning/error는 0건이다. 사람 낭독·클릭 리허설은 계속 `NOT_MEASURED`이며, 이후 Core 통합·최종 회귀 상태는 바로 아래와 Control Tower CURRENT의 최신 항목을 따른다.
- Slide 07 지원 범위 문구를 EvidencePacket·GCP Agent 구현에 맞춰 `필수 근거 결측 → HOLD`, `Mission·Parts 개별 검증 → Assurance 입력·응답 무결성 재확인`으로 정밀화했다. localhost 1280×720에서 좌우 박스가 각각 `181.59 px`, slide scroll `1280×720`로 겹침·overflow 없이 표시되는 것을 재확인했다. 전체 Release 회귀 결과는 Control Tower CURRENT의 최신 항목을 따른다.

## Compact 11-slide Main Deck — 2026-08-25

- 제품 시연과 겹치던 차폐 계산·ECC 상세 및 임무·부품 상세를 주 발표에서 제거했다. 기능·합성 snapshot·Q&A 근거는 코드에 유지하며 본문은 `Cover + 01~09 + Closing`, 총 11장이다.
- Slide 04를 다섯 개 큰 기호의 Evidence-to-Decision 흐름으로 유지하고, 후속 번호는 범위·신뢰성 06, GCP Multi-Agent 07, 공격 검증 08, 로드맵 09로 정렬했다.
- 변경 범위 Presentation/Product 결속 테스트 21개가 통과했다. 전체 회귀와 사람 7분 리허설은 실행하지 않았다.

## Early Evidence-to-Decision Architecture — 2026-08-24

- 멘토링 피드백을 반영해 전체 흐름을 초반으로 이동했고, 최신 기준선에서는 차폐 기초 01·문제 02 다음인 Slide 03에 현재 경계와 함께 다섯 단계 그림을 배치했다.
- `비정형 자료 → pypdf·SHA-256 intake → decision-ineligible 후보 → Mission·Parts·Assurance → 결정론적 gate → HOLD·근거·다음 행동`을 한 줄로 도식화했다.
- 06번은 임무 조건·정확한 부품 정보·방사선 시험 결과를 함께 대조하는 제품 정체성에 집중하고, 로컬/GCP 상태 rail과 콘솔 링크는 제거했다. 콘솔 시연은 발표 후반의 별도 화면에서만 진행한다.
- 다중 문서 결과표 링크는 주 발표 흐름과 Raw Evidence Console에 유지한다. 사람 7분 리허설은 계속 `NOT_MEASURED`다.

## Final Trust & Integrity alignment — 2026-08-24

- Multi-Agent 화면에 `Private Agent Access`, `Input Binding`, `Evidence Boundary`, `Fail-Closed Output` 네 신뢰 경계를 추가했다.
- `공개 IAM 주체 0`, body hash·revision 결속, 자체 승인·낙관 승격 차단, 오류 시 값 숨김·후속 호출 중단·`HOLD`만 표시한다.
- 인접 경계를 `SNAPSHOT + LOCAL REGRESSION · NOT PEN TEST / KMS / ASSURANCE`로 고정해 완전한 보안·침투시험·KMS 서명 배포·실제 방사선 assurance 완료로 확대하지 않는다.
- 최신 v2 발표 대본에도 같은 직접 답변과 한계를 추가했다. localhost 1280×720에서 13장 실제 순회 결과 x/y overflow 0, Product 17 tests와 Workspace 21 tests가 통과했다.
- 판정은 `VERIFIED — presentation trust boundary`; 사람 7분 리허설과 실제 보안 인증은 `NOT_EVALUATED`다.

H02 7분 발표 서사 패키지의 `INTEGRATED / commit 379f3ad`, H03 Business Validation Instrument의 `INTEGRATED / commit b2c8ef6`, H05 Runtime Alignment과 H08 Plain-Language Alignment의 `VERIFIED` 기준선은 유지한다. H09 `CHANGES_REQUESTED`를 반영해 표지, ECC 선택 이유, 보증 판단과 결과 전달 무결성을 초심자 흐름으로 정렬했다. WATCHDOG·TMR·SEL과 관련 runtime 합성 수치는 현재 사용자 결정에 연결되지 않으므로 주 발표·Product 시연에서 제외하고 기술 Q&A의 `현재 주 데모 범위 밖`으로만 남겼다.

2026-08-21 공식 평가 기준은 Multi-Agent·GCP 35, 신뢰성 20, 비즈니스·문제 정의 30, 팀 시너지·발표 15로 정정됐다. H11의 배점·시간 산술·Agent/Core 역할·fail-closed·발표 경계를 Control Tower가 독립 대조해 문서 계약을 `VERIFIED`로 판정했다. 이후 Workstream 70 H05는 H04 무결성 결함을 보완해 실제 revision·정상/공격 result와 함께 `VERIFIED`됐다. 다만 사람 리허설, Product H17 실제 브라우저, 실제 GCP `ASR-D02`는 각각 `NOT_MEASURED / NOT_EVALUATED / NOT_EVALUATED`이며 발표 후보가 이 범위를 넘을 수 없다.

## H14 Judge Audit & GCP Provenance Remediation — 2026-08-24

- package: `90-judge-audit-and-gcp-provenance-remediation-v1`
- submission: `H14`
- status ceiling: `READY_FOR_REVIEW`
- 네 persona audit의 공통 P0인 deck/script 번호 불일치, 확대된 live 표현과 H05 execution provenance 오연결을 교정했다.
- `demo/index.html`의 GCP 주 화면은 H05 authoritative snapshot의 세 기록만 전환한다.
  - 정상 합성 실행 `ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34`: Agent 3개 `VALID`, `engineering_gate=NOT_EVALUATED`, 최종 `HOLD`
  - body hash 위조 `3f5d9221-7b7a-4023-be3c-f933fdbaf070`: Mission `INPUT_BODY_SHA256_MISMATCH`, Core·Parts·Assurance 미호출, 최종 `HOLD`
  - endpoint override `df49b5c1-3883-468e-bf1e-67e87ee0b6a7`: Agent 호출 0회, `ENDPOINT_OVERRIDE_FORBIDDEN`, 최종 `HOLD`
- 주 화면에서 H04 `AGENT_TEST_FAILURE`를 GEO 범위 차단으로 바꾼 연결, body hash 위조를 Assurance 최종 PASS 위조 탐지로 바꾼 연결과 H05 snapshot 밖 실행을 제거했다.
- 상태 label은 `검증된 고정 GCP 실행 기록 · SNAPSHOT / NOT LIVE`이며, 버튼이 저장된 H05 실행 기록만 전환하고 새 Workflow를 시작하지 않는다고 인접 표기했다.
- Slide 01의 출처 없는 COTS 비율·조기 실패율·시험 대기기간은 제거하고, NASA의 COTS 검증 조건과 heavy-ion beam time 비용 압력만 공식 링크·접근일과 함께 남겼다. SPECTRA ROI와 시험 대체는 주장하지 않는다.
- 원본 Downloads 대본은 보존하고 `/Users/taehoon/Downloads/spectra_7min_presentation_script_v2.md`를 새로 작성했다. v2는 `Cover + 01~11 + Closing` exact 순서, `CALCULATED 405초 + 15초 전환 여유 = 420초`이며 사람 리허설은 `NOT_MEASURED`다.
- v2 Q&A 8개는 모두 `직접 답변 → 검증된 범위 → 안전장치 → 남은 한계` 순서로 약 20초 답변을 제공한다. 한 사람 구현의 팀 시너지는 세 Agent 책임 분리와 Control Tower 독립 재현으로만 설명한다.
- presentation direct test 5개와 H14 정적 provenance assertion, `git diff --check`가 통과했다. localhost 1280×720에서 13장 overflow 0, GCP 세 scenario exact DOM, console warning/error 0을 직접 확인했다.
- 실제 방사선 분석·실제 사용자 가치·사람 낭독 시간은 검증하지 않았고 전체 회귀는 실행하지 않았다.

## H13 Evidence-Bound Business Impact — 2026-08-24

- package: `90-evidence-bound-business-impact-v1`
- submission: `H13`
- status ceiling: `READY_FOR_REVIEW`
- 13장 구조와 슬라이드 번호를 유지한 채 `demo/index.html`의 02·03·11만 좁게 보완했다.
- Slide 02는 `환경 모델 출력 → BOM spreadsheet → 시험 PDF → 수기 조건 대조 → 검토·보완` 흐름과 exact part/process/lot·시험 조건·임무 적용성·권리/승인 trace의 수동 재연결 문제를 보여 준다. 실제 시간·반려율은 `UNSET / UNVALIDATED`다.
- Slide 03은 기존 시험 자원의 비용 압력으로 NASA COTS Parts Phase II의 공개 heavy-ion beam time `$1,000–$5,000/hour` 범위와 공식 URL·접근일을 인접 표기한다. 이는 SPECTRA 절감액·ROI·회피 비용이 아니며, 메시지는 근거 공백을 먼저 찾아 제한된 시험 시간을 우선순위화하되 시험을 대체하지 않는다는 것이다.
- Slide 11은 실제 데이터·AI 확장 로드맵을 유지하고 하단을 `기대 효과 → 파일럿 검증`으로 바꿨다. 화면 KPI는 `case당 active review time`, `trace completeness`, `보완 return rate` 세 개뿐이며 모두 `PILOT MEASURE · UNVALIDATED`, 현재 값은 `UNSET`이다.
- 기대 효과는 반복 evidence 조사·재검토 부담과 제한된 시험 자원 우선순위를 개선할 가능성일 뿐이다. 절감액·절감률·ROI 산식·숫자 scenario·시험 회피·승인 자동화·방사선 적합성 보장은 표시하지 않는다.
- presentation direct test 3개는 통과했다. localhost 1280×720에서 Slide 02·03·11의 가로·세로 overflow가 없고 Slide 03 source footnote가 화면 안에 표시되는 것을 직접 관찰했다. 전체 회귀와 사람 발표 리허설은 수행하지 않았다.
- NASA 공식 citation URL은 2026-08-24 접근 대상으로 확인했지만, 실행 환경의 NTRS PDF 다운로드가 완료되지 않아 원문 문장 재추출은 하지 못했다. 금액 범위는 프로젝트에 이미 고정된 출처 있는 문제 근거만 사용했으며 직접 인용문은 만들지 않았다.

### H13 Control Tower 독립 검토 — 2026-08-24

- 판정: `VERIFIED — evidence-bound business impact presentation patch`; 실제 사용자 가치·절감 효과 검증은 아니다.
- presentation direct test 3/3과 `git diff --check`를 재현했다.
- localhost 1280×720 실제 브라우저에서 13장, Slide 02의 `UNSET/UNVALIDATED`, Slide 03의 `$1,000–$5,000/hour`와 NASA source link, Slide 11의 세 `PILOT MEASURE · UNVALIDATED`를 확인했다.
- Slide 11 active content boundary 밖 overflow는 0이고 console warning/error도 0이었다. SPECTRA 절감액·ROI·시험 대체 주장은 추가되지 않았다.

## 2026-08-22 실제 발표 경로와 Antigravity 청사진 — Control Tower 최신화

- 사용자가 실제 발표에는 `demo/product.html`을 쓰지 않고 `demo/index.html`만 사용했다고 확인했다. 실제 사용한 최신 HTML은 Downloads의 `spectra_presentation.html`이며, 생성 시각 기준 실제 대본은 2026-08-21 13:55에 추가된 `spectra_7min_presentation_script.md`다. 01:55 구간의 부품 증거·ECC 통합 흐름을 사용했다.
- cover·01~09·COTS HTML은 발표 후 피드백을 Antigravity로 반영한 배치·문구 청사진이다. 디자인 자체를 대치하지 않고 저장소 `demo/index.html`의 기존 흑백 언어 안에서 참고한다.
- `spectra_slide_cots_comparison.html`은 기존 03을 대치하지 않고 03번에 삽입했다. 이후 기존 화면을 뒤로 이동하고 차폐 primer·비교·기술 스택·로드맵·Closing을 포함해 `Cover + 01~11 + Closing`, 총 13장으로 정렬했다.
- Downloads 대본과 COTS 청사진은 합성 fixture를 AP-8/AE-8·SHIELDOSE-2·Weibull 기반 검증 결과, `EX-100` 실제 성적서 결과 또는 ECSS 승인처럼 설명한다. 현재 실제 environment contract·승인 BOM·시험 원문·과학 교차검산은 없으므로 실제 발표 이력은 인정하되 assurance 대본 판정은 `CHANGES_REQUESTED`다. 저장소 COTS 화면은 해당 글자를 유지하면서 하단에 `원문·조건·적용성 독립 검증 전 / NOT_EVALUATED / HOLD`를 표시한다.
- `19/19`, `1,000회 Monte Carlo`, `Δ=0.0000`, WORM·전 과정 위변조 원천 차단, `완벽히 실행`, `실시간 GCP VERIFIED`는 현재 제출 증거와 일치하지 않는다. 다운로드 통합본의 버튼은 `/api/trigger-workflow` 실패 시 embedded snapshot을 `VERIFIED GCP EXECUTION`으로 표시하므로 실제 live 실행과 고정 snapshot도 구분되지 않는다.
- COTS 비율·고장률·방사선 원인 비율·시험 비용/대기, ECSS/RDM·표준 compliance와 기존 NASA/ESA 도구에 대한 비교 문구는 exact source·locator·적용 범위가 확인되지 않았다. 발표에 유지하려면 주장별 검증 가능한 출처와 제한을 붙여야 하며, 확인 전에는 삭제하거나 `UNVERIFIED`로 닫는다.
- 대본은 `5분 20초 + 1분 40초 라이브 데모 버퍼 및 Q&A`를 7분으로 묶어, 확정된 `발표 7분 + 질의응답 3분` 운영과도 맞지 않는다. 사람 낭독·클릭 리허설은 `NOT_MEASURED`다.
- 확대 주장이 포함된 Downloads 원본 자체의 `CHANGES_REQUESTED` 이력은 유지하지만, 이는 청사진의 배치·문구 사용을 금지하는 판정이 아니다. 저장소 통합본은 검증되지 않은 비교 숫자에 인접한 `NOT_EVALUATED / HOLD` 경계를 붙였고, localhost 버튼이 실제 Workflow를 새로 트리거하는 동작은 제거해 Control Tower verified H05 snapshot 전환으로 한정했다.
- 새 Workflow execution `ad392071-1554-43e8-9447-5b92d4790a48`은 Control Tower가 API·Storage generation·Cloud Run 시간창 로그로 독립 확인했다. Mission Agent가 합성 all-zero SHA-256 공격을 `INPUT_BODY_SHA256_MISMATCH`로 차단한 `INVALID_INPUT / NOT_EVALUATED / HOLD` 실행이며, 세 Agent 정상 실행이나 실제 방사선 보증처럼 말하지 않는다. 화면 본문은 기존 H05 snapshot만 표시하며 새 실행은 문서 증거로 분리한다.
- localhost 1280×720 실제 브라우저에서 13장 모두 horizontal·vertical overflow 0, console warning/error 0을 확인했다. 차폐 1/2/4/5 mm, 2 mm 고정 ECC OFF/ON, GCP 네 scenario, 6개 node, 35점 badge 제거, 범위·신뢰성 박스와 GCP decision 박스 정렬도 통과했다. Product 직접 테스트 16개, JavaScript syntax와 `git diff --check`가 통과해 **시각·상호작용 통합만 `VERIFIED`**다.
- Google Cloud Console 버튼은 실제 발표본의 stable Workflow 링크를 그대로 유지한다. 로그인 세션에서 Console이 `executions?...&rapt=...`로 이동할 수 있지만, `rapt` 인증 파라미터는 저장소에 저장하지 않는다.

## H11 Rubric and Multi-Agent/GCP Narrative Alignment — 2026-08-21

### 패키지와 공식 배점

- package: `90-rubric-multi-agent-gcp-alignment-v1`
- submission: `H11`
- status ceiling: `READY_FOR_REVIEW`
- 공식 배점은 모든 H11 기준 문서에서 다음으로 고정했다.
  - Multi-Agent 아키텍처 및 GCP 인프라 완성도: **35점**
  - 할루시네이션 방어 및 무결점 신뢰성: **20점**
  - 비즈니스 임팩트 및 문제 정의: **30점**
  - 팀 시너지 및 프레젠테이션: **15점**
- `BRIEF.md`와 `DEMO_SCREEN_GUIDE_GLOSSARY_SCRIPT.md`의 배점·발표 증거를 동일하게 정렬했다.

### 7분 core 서사

- 기존 `PLANNED 405초(6분 45초)`를 늘리지 않고 `문제와 제품 가치 → 결정론적 Core → 세 Agent의 증거 책임 → GCP 실행·격리·감사 → fail-closed → 사용자 행동과 차별점 → 한계·팀 연결·다음 단계 → 마무리`로 재배치했다.
- 산술은 `20 + 40 + 45 + 55 + 50 + 45 + 45 + 85 + 20 = 405초`다. 선택 확장 60초를 붙이면 `465초(7분 45초)`이며 사람 리허설은 `NOT_MEASURED`다.
- Agent/GCP 전용 live 화면이 없어 현재 deck 07 Evidence Chain을 배경으로 말한다. 화면 추가는 Workstream 80 change request로만 남겼다.

### Agent와 결정론적 Core의 책임

- Environment Agent는 임무·환경 모델 metadata, 버전과 provenance 조건을 확인한다.
- Parts Evidence Agent는 exact-part identity, 시험 event coverage, 원문 locator와 권리·출처 상태를 확인한다.
- Independent Assurance Agent는 앞선 결과와 Core 결과의 schema·status·hash·blocking gap 일관성을 독립 확인한다.
- 세 Agent는 방사선 숫자·시험값·최종 PASS를 생성하지 않는다. 계산·정책·gate는 결정론적 Core가 소유한다.
- 필수 입력 누락, 범위 밖, Agent 실패, invalid response와 결과 불일치는 `NOT_EVALUATED/HOLD`로 닫고 다음 역할이 빈칸을 추측하지 않는다.
- WATCHDOG·TMR·SEL runtime과 관련 합성 수치, runtime이 섞인 `47 / 0` aggregate는 주 발표와 핵심 신뢰성 수치에서 제외한다. ECC는 residual SEU 계산에 쓰는 제한된 합성 설계 가정이며 실제 하드웨어 구현이 아니다.

### GCP 실행 경계와 H04 상태

- H04 target은 `Cloud Storage synthetic input → Workflows → Environment Agent on Cloud Run → Parts Evidence Agent on Cloud Run → Independent Assurance Agent on Cloud Run → Storage result + Cloud Logging trace`다.
- Workflows는 호출 순서·context와 오류 전파, Cloud Run은 역할별 실행 격리, Storage는 exact object 경계, Logging은 run 상태·오류 trace, IAM은 호출 권한 경계를 맡는다.
- GCP는 단순 저장 방향이 아니라 실행·격리·감사 인프라로 설명한다. timeout·HTTP 오류·invalid response를 낙관적으로 우회하지 않는 fail-closed target이다.
- Workstream 70 H04 handoff는 아직 없으므로 다음은 모두 `PENDING_H04_VERIFICATION`이다.
  - 실제 resource명과 revision
  - Workflow execution ID와 Cloud Run request/log correlation ID
  - Storage generation·SHA-256 관측값
  - 실제 IAM binding 관측, latency, 비용과 성공 횟수
- H04가 성공하더라도 합성 fixture 실행 증거이며 실제 환경·승인 BOM·시험 원문이 없으면 최종 assurance는 `HOLD`다.
- 아래 H10 이하의 `live GCP resource 0` 문구는 각 과거 제출 당시 상태 기록이다. H11의 현재 발표 계약에서는 H04 병렬 실행 가능성을 반영해 실제 cloud 상태를 0이나 성공으로 단정하지 않고 `PENDING_H04_VERIFICATION`으로 대체한다.

### Q&A와 변경 경계

- 우선 Q&A는 `왜 세 Agent인가`, `Agent 할루시네이션 방어`, `왜 GCP인가`, `실제 배포됐는가`, `Agent 실패 시 처리`, `GCP 성공과 실제 부품 적합성의 차이` 여섯 질문으로 정렬했다.
- 각 답변의 첫 문장은 결론형이며 `PLANNED 30~45초`다.
- Workstream 80 change request: Agent/GCP 책임 구조와 H04 검증 상태를 평가용 화면에 추가하되, 검증 전 live 필드는 `PENDING_H04_VERIFICATION`으로 표시한다.
- Product/demo 코드·테스트·Workstream 70·80·공통 계약·engine·루트 문서는 수정하지 않았다.
- 문서 전용 H11이라 Product 테스트와 전체 회귀는 실행하지 않는다.
- `CONTRACT_CHANGE_REQUEST`: H10의 ECC residual 결과 계층 결정을 유지하고, Workstream 80 Agent/GCP 평가 화면은 H04 검증 뒤 별도 소유 작업으로 요청한다.

## H10 Cover and Product Clarity Narrative — 2026-08-21

### 패키지와 범위

- package: `90-cover-and-product-clarity-narrative-v1`
- submission: `H10`
- status ceiling: `READY_FOR_REVIEW`
- 수정 파일은 `DEMO_SCREEN_GUIDE_GLOSSARY_SCRIPT.md`, `ASSURANCE_ATTACK_DEMO_RUNBOOK.md`, 이 `CURRENT.md`와 H10 handoff다.
- Product/demo 코드·테스트·Workstream 80·공통 계약·engine·루트 문서는 수정하지 않았다.

### 초심자 주 발표 정렬

- 표지에 `SPECTRA`, `위성 전자부품 방사선 검토를, 계산에서 근거와 판단까지 연결합니다.`, `좋은 숫자보다, 믿을 수 있는 판단.`을 두고 20초 시작 대본을 추가했다.
- `오늘 보시는 수치는 합성 데모이며 실제 방사선 보증 결과는 아닙니다.`를 시작에서 한 번 말하고, 이후에는 판단이 바뀌는 지점에서만 합성·0건·`HOLD` 경계를 말한다.
- 주 흐름은 `차폐·TID·SEU·ECC → 정확한 부품 근거 연결 → 5 mm 범위 밖 차단 → 보증 판단 HOLD → 결과 전달 숫자 변경 차단`이다.
- ECC ON은 실제 하드웨어 구현이 아니라 수정 가능한 메모리 오류가 줄어든다는 제한된 합성 설계 가정을 residual SEU 계산에 적용한 것이다. 발표 HTML의 `0.063072 → 0.0063072`는 동결 합성 fixture 비교일 뿐 실제 효과가 아니며, 실제 채택에는 부품 지원·오류 패턴·적용 조건·효과 근거가 필요하다. Product 시연에서는 current generated payload의 화면값을 따른다.
- WATCHDOG·TMR·SEL과 `10%→2.8%`, `1회·60초`, `2회·32초` runtime 수치는 주 대본과 Product 시연에서 읽지 않는다. 관련 계산·schema·합성 fixture는 실제 하드웨어·장비 제어·현재 임무 채택·효과 입증이 아니며, 용어집의 기술 Q&A에서만 `현재 주 데모 범위 밖`으로 설명한다.
- Product 03은 실제 label인 `확인된 것 → 아직 필요한 것 → 그래서 내린 결정` 세 문장만 따라간다. `HOLD`는 불합격이 아니라 현재 근거로 안전하다고 승인하지 않겠다는 상태다.
- Product 04는 차폐·TID·SEU·ECC 계산과 분리된 결과 전달 layer다. 화면에는 고정 오류 주입 값 `60 → 999`가 보이지만 주 대본에서는 숫자를 읽지 않고 `원래 기록 → 일부러 바꾼 테스트 값 → 불일치 시 숫자 숨김·판단 보류`로만 설명한다.
- 화면의 기존 `47 / 0` aggregate에는 핵심 발표 범위 밖 ASR-D03 runtime 18개가 포함되므로 H10에서는 공격 횟수나 잘못 PASS 0을 핵심 신뢰성 수치로 말하지 않는다. core profile 후보인 기존 18개와 MVP/ECC 11개는 Control Tower 독립 재검증 전 `UNSET`이다.

### 가치·경계·다음 단계

- 제품 가치는 `계산값만 보여 주는 도구가 아니라, 어떤 근거가 연결됐고 무엇이 부족해 판단을 보류했는지까지 보여 줍니다.`로 정리했다.
- 차별점은 같은 입력의 재현, 지원 범위 밖 비추정, 실제 근거 부족 시 비승인, 전달 숫자 불일치 시 비노출이다.
- 실제 environment model run, 승인 BOM, 시험 원문·실제 수치, live GCP resource·호출·실측 비용은 0이다. 합성값의 과학 정확성, 실제 부품 적합성·인증, 실제 사용자 가치와 프로젝트 전체 보안도 검증되지 않았다. 최종 assurance는 계속 `HOLD`다.
- 다음 경로는 실제 임무 환경과 권리·출처 → 승인 BOM exact-part 시험 근거 → 실제 부품 ECC 지원·오류 패턴·효과 근거와 채택 정책 → 독립 assurance·실제 GCP 운영 검증이다.
- 마무리는 `SPECTRA의 목표는 항상 답을 내는 것이 아닙니다. 믿을 수 있는 근거가 있을 때만 답하고, 그렇지 않으면 왜 멈췄는지와 다음 행동을 보여 주는 것입니다.`로 유지했다.

### 시간과 H15 대조 상태

- 이해 우선 core: `20 + 35 + 50 + 35 + 40 + 70 + 45 + 90 + 20 = 405초`, 즉 `PLANNED 6분 45초`.
- 선택 확장: `20 + 20 + 20 = 60초`; 전체 `405 + 60 = 465초`, 즉 `PLANNED 7분 45초`.
- 7개 본문 화면 fallback은 `212초`, 표지 포함 `232초`로 모두 `PLANNED`다.
- 사람 낭독·클릭·탭 전환 리허설은 `NOT_MEASURED`다.
- 2026-08-21 Workstream 80 H15 `READY_FOR_REVIEW` handoff와 current source에서 번호 없는 표지, ECC 설명, Product 03의 인과 label, Product 04의 화면명·제목·control·처리 문구와 계산/전달 layer 문장을 exact 대조했다. H15 actual browser는 `NOT_EVALUATED`이고 Control Tower `VERIFIED` 전이다.
- H15가 기록한 계약 차이를 인수했다. 발표 HTML의 동결 Stage 2 residual은 `0.0063072`, Product current generated payload residual은 `0.013072`다. H10은 두 값을 같은 결과 계층으로 합치지 않고 Product 시연에서는 current 화면값, 발표 HTML fallback에서는 동결 fixture 값을 사용한다.
- 문서 전용 H10이므로 Product 테스트와 저장소 전체 회귀는 실행하지 않는다.
- `CONTRACT_CHANGE_REQUEST`: Product가 어느 residual 결과 계층을 대표할지 Control Tower 후속 계약이 필요하다. H10은 authoritative source·consumer·수치를 변경하지 않는다.

## H09 Control Tower 독립 검토 — 2026-08-21

- H14 source와 네 안전장치·`47/0` 범위·Product 04 control의 exact 정합성은 확인했다.
- `git diff --check`는 통과했다.
- H09는 TMR을 `세 장치가 같은 계산`으로 설명하지만, 정확한 가정은 동일 기능의 복제 채널 3개와 제한된 독립 오류 fixture다. 세 위성 가정이 아니라는 설명과 현재 임무 설계 비채택 경계가 빠졌다.
- SEL 과전류 보호는 TMR과 별개의 단일 device/전원 rail 보호 경로이며 세 장치 가정이 아니다. 이 구분도 주 대본과 용어집에서 명시해야 한다.
- ECC의 기능은 설명했지만 실제로 왜 고려하는지와 실제 부품 지원·오류 패턴·효과 근거가 있어야 채택할 수 있다는 의사결정 문장이 부족하다.
- Product 보증 판단의 네 gap을 그대로 읽는 방식보다 `확인된 것 / 아직 필요한 것 / 현재 결정`으로 설명해야 한다.
- 따라서 H09의 초심자 명료성 Exit Gate는 `CHANGES_REQUESTED`다. 이전 H08 `VERIFIED`는 유지한다.
- 후속 지침: `instructions/SPECTRA_90_COVER_AND_PRODUCT_CLARITY_NARRATIVE_H10.md`.

## H09 Screen-First Reliability Narrative

### 현재 작업 상태

- package: `90-screen-first-reliability-narrative-v1`
- submission: `H09`
- status ceiling: `READY_FOR_REVIEW`
- deck 06 설명을 `같은 입력 → 같은 결과`, `지원 범위 밖 → 계산 안 함`, `실제 근거 부족 → 판단 보류(HOLD)`, `전달된 숫자가 다름 → 숫자 숨김`의 네 안전장치로 정렬했다.
- `47회 / 잘못 PASS 0`은 단위·범위·식별·증거·정책·결과 변경을 포함한 고정 합성 오류·공격 실행 세트로만 한정했다. 모든 공격, 실제 GCP `ASR-D02`, 과학 정확성 또는 실제 evidence 검증 완료 주장이 아니다.
- Product 04는 `Assurance Attack`이 아니라 네 번째 안전장치의 `결과 전달 오류 테스트` 또는 `오류 주입 테스트`로 연결했다.
- `재현 가능`, `지원 범위`, `오류 주입 테스트`, `잘못된 PASS(False PASS)`, `고정 합성 테스트 세트`를 초심자용 용어집에 추가했다.
- Product 02의 `Runtime 완화`를 주 대본에서 `고장 대응 방법`으로 설명하고, 자동 재시작·3중 다수결·과전류 전원 보호를 각각 `무엇을 하는가 → 어떤 대가가 남는가`로 정리했다. 현재 합성 수치 `1회·60초`, `10%→2.8%`, `2회·32초`와 실제 효과 미검증·최종 `HOLD`를 함께 말한다.
- `runtime`, `false activation`, `projection`, `processing status`, `equation ID`, policy code와 hash는 주 대본의 이해 전제에서 제외했다.
- 기존 제품 가치·한계·다음 단계·마무리는 유지했다. Product 02 설명을 core에 포함하면서 이해 우선 core는 `PLANNED 390초`, 선택 1분 포함 전체는 `PLANNED 450초`다. 화면 06 이해를 늘린 7개 deck 화면 연속본은 별도로 `PLANNED 202초`이며 사람 리허설은 수행하지 않았다.
- current `demo/index.html`의 deck 06 네 카드·`47 / 0` 범위 문구와 `demo/product.html`의 Product 04 새 맥락 label·연결 문장을 source 기준 exact 대조했다. 이는 H14의 `VERIFIED` 또는 실제 browser 검증을 뜻하지 않는다.
- current Product 02 source의 탭 `고장 대응 방법`, 질문 `오류가 생겼을 때 시스템은 어떻게 버티고 복구할까요?`, 중심 문장, `자동 재시작·3중 다수결·과전류 전원 보호`, `문제가 생김 → 대응 동작 → 남는 영향·대가`, 합성 수치와 `합성 계산 결과 · 실제 완화 효과 검증 아님 · 근거 부족으로 HOLD`를 exact 대조했다. `WATCHDOG/TMR/SEL 대응`은 보조 기술명, 내부 상태·equation·policy·hash는 접힌 기술 상세에만 있다.
- Product/demo 코드, 테스트, Workstream 80, 루트 문서는 수정하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H08 H07 Presentation Copy & Current-State Remediation

### Control Tower 독립 검증 — 2026-08-20

- H07의 provenance 오탈자, H12 미제출 stale 문구와 이전 H10 85초 표현이 제거됐음을 확인했다.
- 장면명·제목·중심 문장·세 카드·세 control·처리 문구를 H13 current Product source와 exact 대조했다.
- `60초 → 999초 → 서로 다름 → 숫자 숨김·판단 보류`가 주 대본에 기술 식별자 없이 설명되고, 기술 용어는 Q&A·용어집에만 남았음을 확인했다.
- `70 / 360 / 420초` 산술과 모든 `PLANNED`, 실제 evidence·GCP 0 및 과학 정확성·보안 비검증 경계를 재확인했다.
- `git diff --check`가 통과했다. H08 문서 정합성 패키지만 `VERIFIED`이며 사람 리허설과 H13 actual browser는 여전히 `NOT_EVALUATED`다.

### 변경 범위

- `DEMO_SCREEN_GUIDE_GLOSSARY_SCRIPT.md`의 provenance 조사 오탈자를 자연스러운 `남기는 계보이다`로 수정했다.
- 화면 7과 연결 문장의 이전 H10 시간 표현을 현재 독립 `숫자 변경 감지`의 `PLANNED 70초`로 정렬했다.
- `ASSURANCE_ATTACK_DEMO_RUNBOOK.md`의 H12 미제출 상태를 현재 사실로 갱신했다. H12 handoff와 Product 13개 테스트 통과 증거는 제출됐지만 실제 `file://` browser·viewport·console 검증은 `NOT_EVALUATED`다.
- 사용자 설명 검토에서 `결과 검증`이라는 장면명이 이해되지 않은 실패를 반영해 H13 목표 `숫자 변경 감지`와 세 문장 인과관계로 주 대본을 좁혔다.

### 유지한 계약

- 초심자용 숫자 변경 감지 주본 `PLANNED 70초`
- `6분 core 360초 + 선택 1분 60초 = 420초`
- H12 화면·control·카드·한국어 우선 상태 exact label
- 실제 environment·parts evidence와 GCP resource 0, 과학 정확성·보안·전자서명 비검증, 최종 `HOLD`
- 제품 가치·차별점·한계·다음 단계·마무리 내용
- Product 테스트와 저장소 전체 회귀는 문서 전용 H08에서 반복하지 않았다.
- 현재 dirty working tree의 H13 Product source에서 화면명·제목·중심 문장·세 카드·세 control·처리 문구를 exact 대조했다. H13 handoff·테스트·실제 browser 검증은 아직 확인되지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H07 Beginner Integrity Story and Closing

### 패키지와 변경

- package: `90-beginner-integrity-story-and-closing-v1`
- submission: `H07`
- baseline: Workstream 80 H10·Workstream 90 H05 `VERIFIED`; H11·H06 `READY_FOR_REVIEW`
- status ceiling: `READY_FOR_REVIEW`
- `ASSURANCE_ATTACK_DEMO_RUNBOOK.md`를 방사선 수치 변화와 분리된 독립 `숫자 변경 감지` 장면의 `PLANNED 70초` 초심자 대본으로 다시 작성했다.
- `DEMO_SCREEN_GUIDE_GLOSSARY_SCRIPT.md`에 assurance·결과 일치성·자동 복구 감시 기능·서비스 중단 시간·테스트용 사본·원래 기록·부분 불일치와 세 안전 상태를 추가하고 `6분 core + 선택 1분` 구조를 통합했다.
- 제품 가치·차별점·한계·다음 단계·마무리를 6분 core 안에 포함했다.

### 초심자 인과관계

- 자동 복구 감시 기능의 정상 합성 서비스 중단 시간은 `60초`다.
- 원본을 보존한 테스트용 사본의 숫자만 `60 → 999`로 바꾸며, `999`는 새 계산이나 실제 중단 시간이 아니다.
- 정상 계산 당시 저장한 원래 기록 `60`과 화면 입력 `999`가 맞지 않으면 어느 값도 추측하지 않는다.
- 주 대본은 `계산 직후 기록 60초 → 화면 테스트 값 999초 → 서로 다르면 숫자 숨김·판단 보류` 세 문장으로 설명하며 기술 식별자는 Q&A로 내린다.
- 이 시연은 Product runtime result의 부분 불일치를 fail-closed로 처리하는 합성 시연이며 해커 방어·전자서명·공격자 인증·GCP 보안·과학 정확성 검증이 아니다.

### 시간과 UI 대조

- 숫자 변경 감지 주본: 세 문장 `20 + 20 + 20초`와 범위 고지 `10초`, 합계 `70초`, `PLANNED`
- 6분 core: `35 + 60 + 40 + 70 + 45 + 90 + 20 = 360초`, `PLANNED`
- 선택 확장: `20 + 20 + 20 = 60초`; 전체 `420초 = 7분`
- 현재 dirty working tree의 H12 Product HTML에서 화면 순서, 카드·control·상태명과 중심 문구를 exact 대조했다. H12 handoff와 Product 13개 테스트 통과 증거는 제출됐지만 실제 `file://` browser·viewport·console 검증은 `NOT_EVALUATED`이며 H12는 아직 `VERIFIED`가 아니다.
- 사람 낭독·실제 클릭·탭 전환은 미실행이며 `MEASURED` 시간이 없다.
- Product 테스트와 전체 저장소 회귀는 문서 전용 H07에서 반복하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H06 Screen Guide, Glossary and Script

### 패키지와 산출물

- package: `90-screen-guide-glossary-script-v1`
- submission: `H06`
- baseline: Workstream 80 H10 `VERIFIED`, Workstream 90 H05 `VERIFIED`
- status ceiling: `READY_FOR_REVIEW`
- 신규: `docs/workstreams/90-business-presentation/DEMO_SCREEN_GUIDE_GLOSSARY_SCRIPT.md`
- handoff: `docs/workstreams/90-business-presentation/handoffs/SPECTRA_90_SCREEN_GUIDE_GLOSSARY_SCRIPT_HANDOFF_H06.md`

### 작성 범위

- 전체 이야기를 5문장으로 정리하고 `demo/index.html` 화면 1~7마다 질문·요소 의미·핵심 한 문장·20~35초 대본·금지 주장을 작성했다.
- BOM exact identity, TID·SEE 계열, 단위·설계계수, snapshot·lookup 범위, ECC, evidence·fail-closed, integrity·rights·GCP 용어를 초심자용 네 열 용어집으로 정의했다.
- 현재 합성 snapshot 값만 사용한 7개 화면 연속 대본은 `22 + 23 + 27 + 25 + 25 + 28 + 25 = 175초`, 즉 `PLANNED 2분 55초`다.
- H10 85초 무결성 공격 설명과 중복하지 않고 화면 7 뒤 한 문장 연결부만 뒀다.

### 사실 경계와 남은 대조

- 모든 화면 값은 `SYNTHETIC`이며 실제 environment·parts evidence와 live GCP resource·호출·실측 비용은 0이다.
- `1 krad = 1000 rad`, `1 rad = 0.01 Gy`, `(Si)`의 실리콘 흡수선량 기준을 단위 설명으로만 사용하며 합성값의 과학 정확성을 주장하지 않는다.
- 설계계수 2를 보편값·승인값으로, 5 mm 범위 밖을 일반 물리 계산 불가로, SEU를 파괴성 SEE 근거로, SHA-256을 과학적 진실성·권리 증명으로 확대하지 않는다.
- 현재 비용 0은 로컬 데모의 실측 GCP 비용 0이며, 실제 배포 시 저장·실행·로그·네트워크 비용을 별도 측정해야 한다.
- H11은 지침만 확인했으며 실제 HTML·handoff가 아직 없어 exact label 대조는 `NOT_PERFORMED`다.
- 사람 낭독 리허설은 미실행이며 시간은 `PLANNED`다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H05 Control Tower 독립 검증 — 2026-08-20

- 변경 범위가 runbook·Workstream 90 CURRENT·handoff에 한정되고 Product 구현·테스트·Workstream 80·공통 계약과 engine을 변경하지 않았음을 확인했다.
- runbook에서 pre-H10 상태·미제출·검증 전·후속 대조 placeholder를 독립 검색해 0건을 확인했다.
- 실제 H10 UI의 `수치 변화 보기 →`, `Assurance 공격`, `공격 입력 만들기`, `동일 consumer로 검증`, `정상 원본으로 Reset`, `신뢰하지 않는 공격 입력 (UNTRUSTED)`가 코드와 runbook에서 exact match함을 확인했다.
- 정상·공격·차단·보존·Reset 관측과 합성 Product integrity 한계가 H10 검증 결과를 넘지 않으며, 실제 GCP 보안·전자서명·공격자 인증·방사선 assurance로 확대되지 않았다.
- `18 + 18 + 32 + 17 = 85`, `155 + 85 = 240`, `400 + 20 = 420` 산술과 `PLANNED` 표기를 재검산했고 `git diff --check`가 통과했다.
- H05 문서 정합성 패키지는 `VERIFIED`다. 사람 낭독·클릭·탭 전환 시간은 아직 `MEASURED`가 아니며 Stage 9과 Git 통합은 미완료다.

## H05 Assurance Attack Demo Runtime Alignment

### 패키지와 변경

- package: `90-assurance-attack-demo-runtime-alignment-v1`
- submission: `H05`
- baseline: Workstream 80 H10 `VERIFIED`, Workstream 90 H04 `CHANGES_REQUESTED`
- status ceiling: `READY_FOR_REVIEW`
- pre-H10 상태 문구와 후속 대조 placeholder를 모두 제거했다.
- 실제 동선을 `수치 변화 보기 →` → `Assurance 공격` → `공격 입력 만들기` → `동일 consumer로 검증` → `정상 원본으로 Reset`으로 확정 반영했다.
- 실제 경고 label `신뢰하지 않는 공격 입력 (UNTRUSTED)`과 차단·보존·Reset 관측값을 runbook cue에 정렬했다.
- fallback을 구현 제출 전 대응이 아니라 발표 현장의 UI 실행·탭 전환 실패 대응으로 갱신했다.

### 검증 상태와 경계

- H10은 1280×720·1440×900 실제 브라우저에서 horizontal overflow 0, 핵심 control 노출, console warning/error 0과 정상 → 공격 → 차단 → Reset 동선이 검증됐다.
- 차단 뒤 WATCHDOG는 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, reason `RUNTIME_PREIMAGE_VALUE_MISMATCH`, 수치·result ID·input/output hash `—`다. TMR·SEL·방사선 residual `0.013072`는 유지되고 Reset 뒤 정상 원본이 복원된다.
- 이는 합성 Product integrity 검증이다. 실제 GCP 보안·전자서명·공격자 인증·방사선 assurance 검증이 아니며 실제 environment·parts evidence와 live GCP resource는 0이다.
- `85초`, fallback `30초`, 전체 `6:40 + 0:20 = 7:00`은 계속 계산된 `PLANNED` 계약이다. 사람 리허설은 수행하지 않았다.
- Product 테스트와 저장소 전체 회귀는 H05 지침에 따라 반복하지 않았다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H04 Control Tower 독립 검토 — 2026-08-20

- `PLANNED 85초` 구간 합계와 기존 Product 240초 안의 `155 + 85 = 240` 교체 산술, 정상·공격·차단 상태 구분, 합성·비보증 경계와 30초 fallback은 적합하다.
- 그러나 H10 제출과 실제 브라우저 검증이 끝난 뒤에도 runbook은 pre-H10 상태 문구와 후속 대조 placeholder를 유지했다. 실제 control label·순서와 복원 관측을 문서에 확정 반영하지 않아 제출 자체의 필수 후속 대조가 완료되지 않았다.
- H04는 `CHANGES_REQUESTED`다. H05에서 실제 H10 label과 검증 결과만 좁게 정렬하고 `PLANNED` 시간을 `MEASURED`로 승격하지 않는다. Product 구현·테스트는 변경하지 않는다.

## H04 Assurance Attack Demo Runbook

### 패키지

- package: `90-assurance-attack-demo-runbook-v1`
- submission: `H04`
- baseline: `main / d287d62`
- status ceiling: `READY_FOR_REVIEW`
- 산출물: `docs/workstreams/90-business-presentation/ASSURANCE_ATTACK_DEMO_RUNBOOK.md`
- handoff: `docs/workstreams/90-business-presentation/handoffs/SPECTRA_90_ASSURANCE_ATTACK_DEMO_RUNBOOK_HANDOFF_H04.md`

### 작성 범위

- 정상 WATCHDOG `1 / 1 / 60 s`와 `VALID / NOT_EVALUATED / HOLD` 경계를 한국어 대사와 화면 cue로 대응했다.
- clone의 downtime만 `60 → 999`로 바꾸고 production preimage·hash를 stale로 두는 공격을 설명했다.
- H09 consumer의 `RUNTIME_PREIMAGE_VALUE_MISMATCH` 탐지 뒤 대상 record 수치·result ID·input/output hash 비노출과 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`를 명시했다.
- 기존 7분 Product 구간 `1:20–5:20` 후반의 85초를 교체해 전체 발표시간을 늘리지 않는 산술 계약을 정의했다.
- 발표 현장에서 공격 UI 실행이나 탭 전환이 실패할 때 기존 self-contained Product 정상 화면으로 설명하는 `PLANNED 30초` fallback과 20초 이내 Q&A를 포함했다.

### 현재 경계

- H04 제출 때 남았던 UI label·동선 대조 항목은 H10 `VERIFIED` 결과를 기준으로 H05에서 해소했다.
- 85초 주본과 30초 fallback은 계산된 `PLANNED` 시간이다. 사람 낭독·클릭·탭 전환은 아직 `MEASURED`하지 않았다.
- 모든 값은 `SYNTHETIC`이다. 실제 environment·parts evidence와 live GCP resource는 0이며 실제 방사선 assurance, GCP security, 전자서명 또는 공격자 인증을 주장하지 않는다.
- 기존 7분 주본의 계산된 핵심 설명 `6:40`과 여유 `0:20` 계약은 변경하지 않았다.
- demo, Product 테스트, Workstream 80, 공통 schema·engine·Assurance 파일은 수정하지 않았다.

## H03 Business Validation Instrument

### 패키지

- package: `90-business-validation-instrument-v1`
- submission: `H03`
- baseline: `main / 4920b6e`
- status ceiling: `READY_FOR_REVIEW`
- 실제 인터뷰·발송·외부 수집: 0건
- 실제 pilot·구매·가격·절감 결과: 0건 / `UNSET`

### 변경 범위

- 신규: `docs/workstreams/90-business-presentation/BUSINESS_VALIDATION_PROTOCOL.md`
- 갱신: `docs/workstreams/90-business-presentation/CURRENT.md`
- 빈 기록 양식: `/Users/taehoon/Downloads/SPECTRA_BUSINESS_VALIDATION_EVIDENCE_LOG_TEMPLATE.md`
- 발표 원고, demo, schema, source, simulation, tests, 다른 Workstream: 수정하지 않음
- commit·push·merge: 수행하지 않음

### 정의한 계약

- 역할: `PRACTITIONER / TECHNICAL_REVIEWER / BUDGET_OWNER / DATA_RIGHTS_APPROVER`
- 가설 8개: 문제 단절, trace, HOLD+다음 행동, 산출물, baseline 측정, 구매, pilot, 권리 gate
- 가설 상태: `UNVALIDATED / PARTIALLY_SUPPORTED / SUPPORTED_WITH_LIMITS / CONTRADICTED / INSUFFICIENT_EVIDENCE`
- evidence class: `INTERVIEW_REPORTED / DIRECTLY_OBSERVED / DOCUMENTED / CALCULATED / ASSUMED`
- pilot 상태: `UNSET / PLANNED / OBSERVED / INVALIDATED`
- 구매 후보: seat, workspace, case, pilot, service; 모든 가격 `UNSET`
- 30분 인터뷰: 역할·최근 사례 → workflow → 시간·비용 → 신뢰·산출물 → 중립 concept → 구매·pilot → 확인 순서
- 개인정보·고객 기밀·계약·원문은 저장소에 넣지 않고 익명 locator와 접근 제한만 기록

### 현재 판정

모든 business hypothesis는 `UNVALIDATED`다. 실제 인터뷰·관찰·문서·계산 evidence가 없으므로 Stage 9은 계속 `IN_PROGRESS`이며 checklist를 완료 처리하지 않는다.

### H03 Control Tower 통합 판정

- 인터뷰·pilot·구매·가격 수치를 만들지 않고 모든 가설을 `UNVALIDATED`, 가격과 기준선을 `UNSET`으로 유지하는 실행 도구 문서만 검증했다.
- 개인정보·고객 기밀·원문을 저장소 밖에 두는 경계와 evidence class·가설 상태·pilot 상태의 fail-closed 기록 규칙을 확인했다.
- H03 문서 패키지는 commit `b2c8ef6`로 `INTEGRATED`했다. 실제 사용자 검증이나 비즈니스 가치 입증을 뜻하지 않는다.

## H02 통합 기준선

### 검증된 범위

- 발표 HTML 문제·Evidence Chain 화면과 H04 Product UI를 결합한 7분 주본
- 계산된 핵심 설명 6분 40초와 전환 여유 20초
- Product UI `검토 조건 → 수치 변화 → 보증 판단` 실제 조작 4분
- 1·2·4·5 mm, ECC 미적용/적용과 모든 최종 `HOLD`
- 우선 Q&A 4개 예상 2분 25초와 백업 Q&A 6개
- Product UI 실패 시 발표 HTML 30초 fallback
- schema 14개, 정상 fixture 3개, 실패 fixture 83개, simulation 19개와 Workstream 60 H01 기준 반영

### 산출물

- `/Users/taehoon/Downloads/SPECTRA_DEMO_PRESENTATION.md`

### 독립 검증 결과

- 시간 계약 합계: `0:50 + 0:30 + 4:00 + 1:00 + 0:20 = 6:40`, 여유 20초
- 우선 Q&A 합계: `40 + 45 + 30 + 30 = 145초`, 35초 여유
- UI 버튼명과 화면 단계가 `demo/product.html`과 일치
- 고정 snapshot 값과 현재 테스트 수치 일치
- 실제 UI 조작에서 browser warning/error 0
- 실제·합성, 구현·설계·미구현과 `NOT_EVALUATED` 경계 유지

### 미완료

- 발표자 실제 발화와 탭 전환을 포함한 7분 사람 리허설
- OS 네트워크를 끈 상태의 fallback 리허설
- 사용자 인터뷰와 현재 업무 시간·비용 기준선
- 구매 단위·가격·pilot 가치 검증
- 실제 Multi-Agent·GCP 시연

### 판정

발표 서사 패키지만 `VERIFIED`다. Stage 9은 `IN_PROGRESS`이며 실제 비즈니스 가치나 제품 완료를 주장하지 않는다. commit·push는 Control Tower가 누적 변경 전체를 다시 확인한 뒤 결정한다.
