# 80 Product & Dashboard — Current

## 상태

`VERIFIED — H04 Product UI prototype baseline`

H03 기능·snapshot·fail-closed 계약을 유지하면서 도메인 초심자용 정보 위계를 H04로 보완했다. Control Tower가 정적 계약과 전체 회귀를 독립 재실행했고 사용자가 실제 UI를 직접 조작해 현재 프로토타입의 시각 기준을 수용했다. 정확한 1280×720·1440×900 overflow와 console 증거는 독립 재현하지 못했으므로 이 판정은 발표용 합성 Product UI 프로토타입에 한정되며 Stage 8 완료가 아니다.

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
