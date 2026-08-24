# SPECTRA 발표 화면 해설·용어집·대본 초안

## 사용 계약

- package: `90-rubric-multi-agent-gcp-alignment-v1`
- submission: `H11`
- baseline: Workstream 90 H10 `READY_FOR_REVIEW`; Workstream 80 H15 `READY_FOR_REVIEW`; Workstream 70 H04 병렬 진행
- UI 정렬 기준: Workstream 80 H15 handoff와 current `demo/index.html`·`demo/product.html`
- 상태 상한: `READY_FOR_REVIEW`
- 모든 화면 수치는 `SYNTHETIC` 합성 예시이며 실제 환경 출력·부품 시험 결과가 아니다.
- 화면 1~7 대본 합계는 `PLANNED 212초(3분 32초)`다. 별도 표지 20초를 포함하면 `PLANNED 232초(3분 52초)`이며 사람 리허설 전에는 `MEASURED`로 바꾸지 않는다.
- H15 handoff와 current source에서 표지와 Product 02·03·04 문구를 exact 대조했다. H15 actual browser는 `NOT_EVALUATED`이며 `VERIFIED`를 주장하지 않는다.
- 전체 발표는 이해 우선 `PLANNED 6분 45초 core + 선택 1분 확장`이며, 문제·결정론적 Core·세 Agent의 증거 책임·GCP 실행 경계·fail-closed·제품 가치·한계·마무리를 core 안에 포함한다.

## 공식 평가 기준과 발표 증거

| 평가 항목 | 배점 | 주 발표에서 보여 줄 증거 | 현재 경계 |
|---|---:|---|---|
| Multi-Agent 아키텍처 및 GCP 인프라 완성도 | **35점** | Environment·Parts Evidence·Independent Assurance의 책임 분리, Workflows 순서, Cloud Run 역할 격리, Storage·Logging·IAM 감사 경계 | H04 실제 resource·execution·측정값은 `PENDING_H04_VERIFICATION` |
| 할루시네이션 방어 및 무결점 신뢰성 | **20점** | Agent가 숫자를 만들지 않음, 결정론적 Core가 계산·gate 소유, 범위 밖·누락·불일치·Agent 실패 시 `HOLD/NOT_EVALUATED` | 기존 `47 / 0` aggregate와 runtime 공격은 핵심 수치에서 제외 |
| 비즈니스 임팩트 및 문제 정의 | **30점** | 환경 모델·BOM·시험 PDF·승인의 단절과 exact-part 적용성 문제, Evidence Chain이 주는 검토·감사 가치 | 시간·비용 절감, 구매 의사와 pilot 가치는 `UNVALIDATED` |
| 팀 시너지 및 프레젠테이션 | **15점** | Workstream별 산출물이 공통 계약으로 연결되고 독립 검토가 선행 Agent의 결론을 그대로 승인하지 않는 구조, 6분 45초 대본·fallback | 사람 리허설은 `NOT_MEASURED` |

배점은 `35 / 20 / 30 / 15`로만 사용한다. 기술 기능 개수나 미검증 cloud 수치로 점수를 채우지 않는다.

## 0. 표지와 발표 시작 — `PLANNED 20초`

**표지 목표 문구**

- `SPECTRA`
- `위성 전자부품 방사선 검토를, 계산에서 근거와 판단까지 연결합니다.`
- `좋은 숫자보다, 믿을 수 있는 판단.`

**시작 대본**

“위성 부품을 고를 때 숫자 하나만 맞는다고 안전한 것은 아닙니다. 그 숫자가 어떤 임무와 부품, 시험 근거에서 왔는지 연결돼야 판단할 수 있습니다. SPECTRA는 이 계산과 근거, 그리고 보류해야 할 이유까지 한 흐름으로 보여 줍니다.”

**범위 선언 — 발표 전체에서 한 번만 말한다**

> 오늘 보시는 수치는 합성 데모이며 실제 방사선 보증 결과는 아닙니다.

이후 화면마다 `합성`, `실제 아님`, `0건`, `HOLD`를 기계적으로 반복하지 않는다. 해당 사실이 현재 결정이나 다음 행동을 바꾸는 장면에서만 다시 언급한다. 표지와 본문 01·07 사이의 wrap 이동은 설명하거나 약속하지 않는다.

## 1. 먼저 이해할 전체 이야기

1. 방사선 계산 도구가 있어도 그 결과가 정확한 임무·부품·시험 조건·승인과 연결되지 않으면 방사선 보증 근거가 되지 않는다.
2. 결정론적 Core가 계산과 gate를 소유하며 Agent는 방사선 숫자나 PASS를 생성하지 않는다.
3. Environment Agent는 임무·모델·출처 계보, Parts Evidence Agent는 정확한 부품·시험·권리, Independent Assurance Agent는 앞선 결과의 일관성과 증거 공백을 각각 책임진다.
4. H04의 목표 구조에서 Workflows가 호출 순서를 고정하고 Cloud Run이 역할을 분리하며 Storage·Logging·IAM이 원본·결과·감사 경계를 남긴다.
5. Agent 또는 데이터가 실패하거나 실제 근거가 없으면 결과를 추측하지 않고 `HOLD/NOT_EVALUATED`로 닫는다.
6. 합성 계산과 향후 GCP 실행 성공도 실제 방사선 assurance나 실제 부품 적합성을 뜻하지 않는다.

## 2. 화면별 해설

### 화면 1 — 문제: 끊어진 증거 연결

**이 화면의 질문**

환경 계산이 끝났는데도 왜 방사선 보증 판단을 바로 내릴 수 없는가?

**화면 요소가 뜻하는 것**

- `환경 계산 → BOM → 시험 PDF → 완화·승인`은 현재 업무에서 연결해야 할 네 묶음이다.
- 환경 출력의 임무 조건, BOM의 exact identity, 시험 조건과 원문 위치, ECC·정책·책임자가 같은 임무와 부품을 가리켜야 한다.
- 계산값 하나가 존재한다는 사실만으로 시험의 적용성, 자료 권리 또는 승인 책임이 증명되지는 않는다.

**발표자가 전달할 한 문장**

> 문제는 계산식이 없는 것이 아니라, 계산과 정확한 부품·시험·승인이 같은 대상을 가리킨다는 증거가 끊겨 있다는 것입니다.

**20~35초 대본 초안 — `PLANNED 22초`**

“방사선 환경을 계산하는 도구는 이미 있습니다. 하지만 그 출력이 이 임무의 정확한 부품, 같은 공정과 로트의 시험 조건, 실제 완화 설계와 승인에 연결되지 않으면 보증 결론은 낼 수 없습니다. SPECTRA가 해결하려는 문제는 바로 이 끊어진 증거 연결입니다.”

**말하면 안 되는 주장**

- 기존 환경 계산 도구가 부정확하거나 쓸모없다는 주장
- 이런 단절이 특정 실패율이나 손실액을 만든다는 미검증 수치
- SPECTRA가 방사선 시험이나 전문 검토를 대체한다는 주장

### 화면 2 — 입력: 임무와 정확한 BOM

**이 화면의 질문**

무엇을 알아야 “이 부품을 이 임무에서 검토한다”는 질문을 정확하게 만들 수 있는가?

**화면 요소가 뜻하는 것**

- BOM은 Bill of Materials, 즉 설계에 들어가는 부품 목록이다.
- 부품 identity에는 manufacturer, exact part number(PN), process, die, lot과 quantity가 필요하다. 같은 제품군 이름이라도 제조 공정·die·lot가 달라지면 시험 근거의 적용성이 달라질 수 있다.
- 화면의 LEO 550 km, 97.6°, 1년과 `Example Semi / EX-100 / P1 / LOT-A / Memory ×2`는 모두 합성 fixture다.
- 승인 BOM은 0건이므로 이 identity를 실제 추천이나 구매 근거로 쓰지 않는다.

**발표자가 전달할 한 문장**

> 임무 조건과 제조사·정확한 부품번호·공정·die·lot·수량을 함께 고정해야 시험 근거의 적용성을 추적할 수 있습니다.

**20~35초 대본 초안 — `PLANNED 23초`**

“여기서는 합성 LEO 임무 하나와 메모리 부품 두 개로 질문을 고정합니다. BOM은 부품 목록이고, 이름만 맞추는 것이 아니라 제조사, 정확한 부품번호, 공정, die, lot, 수량까지 확인해야 합니다. 지금 화면의 identity는 합성 예시이며 승인된 실제 BOM은 0건입니다.”

**말하면 안 되는 주장**

- `EX-100`이 실제 판매·비행 부품이라는 주장
- 같은 PN이면 모든 process·die·lot 시험을 재사용할 수 있다는 주장
- 화면의 임무가 실제 고객 임무 또는 권장 LEO 기준이라는 주장

### 화면 3 — 환경·차폐: 고정 snapshot과 모델 범위

**이 화면의 질문**

합성 차폐 비교에서 무엇을 계산했고, 어디까지가 모델 범위인가?

**화면 요소가 뜻하는 것**

- TID는 임무 동안 누적되는 총 이온화 선량이다. `krad(Si)`는 실리콘이 흡수한 선량 기준이며 `1 krad = 1000 rad`, 흡수선량 환산에서 `1 rad = 0.01 Gy`다.
- 기본 2 mm 화면의 `6.0 krad(Si)`와 요구 TID `12.0 krad(Si)`는 합성 snapshot이다.
- 현재 계약의 계산 규칙은 `required TID = shielded mission TID × tid_design_factor`다. 여기서 설계계수 2는 합성 입력이지 업계 보편값이나 승인값이 아니다.
- deterministic snapshot은 같은 고정 입력·버전에서 같은 결과를 재현한다는 뜻이며 과학적 정확성의 증명은 아니다.
- 이산 lookup은 등록된 1/2/3/4 mm 값만 선택한다. interpolation은 등록값 사이를, extrapolation은 범위 밖을 추정하는 것이며 현재 데모는 둘 다 하지 않는다.
- 5 mm `OUT_OF_MODEL_SCOPE`는 이 합성 table의 범위 밖이라는 뜻이다. 일반 물리 모델이 5 mm를 계산할 수 없다는 뜻은 아니다.

**발표자가 전달할 한 문장**

> 이 화면은 등록된 합성 결과만 재현하며, 범위 밖 5 mm를 임의로 보간하거나 외삽하지 않고 `HOLD`합니다.

**20~35초 대본 초안 — `PLANNED 27초`**

“합성 예시에서 2밀리미터 차폐 후 TID는 6.0 krad(Si)이고, 화면의 요구량 12.0은 차폐 후 TID에 합성 설계계수 2를 곱한 값입니다. 이 값은 고정 snapshot입니다. 등록된 1·2·3·4밀리미터만 lookup하고, 5밀리미터는 이 표의 범위 밖이므로 추정하지 않고 `OUT_OF_MODEL_SCOPE`와 `HOLD`로 닫습니다.”

**말하면 안 되는 주장**

- 합성 TID가 실제 궤도에서 과학적으로 검증된 선량이라는 주장
- 설계계수 2가 보편 표준이나 승인된 정책이라는 주장
- 5 mm 차폐를 물리적으로 계산할 수 없다는 주장
- deterministic 또는 SHA-256이 모델의 과학적 진실성을 증명한다는 주장

### 화면 4 — 부품 증거: 계산 가능과 보증 충분성의 차이

**이 화면의 질문**

합성 fixture로 계산할 수 있다는 사실이 왜 실제 부품의 방사선 보증을 뜻하지 않는가?

**화면 요소가 뜻하는 것**

- synthetic fixture는 코드 경로와 판정 구조를 재현하기 위한 테스트 입력이다. physical evidence는 실제 환경 출력·정확한 부품 시험 원문·조건·권리처럼 현실의 주장에 적용 가능한 근거다.
- 화면의 TID `25 krad(Si)`와 SEU 단면적 `1×10⁻⁶ cm²/device`는 실제 시험 수치가 아니다.
- SEU 근거 하나가 부품에 필요한 모든 방사선 근거를 대신하지 않는다. 추가로 필요한 event mode와 시험 조건은 부품 기술과 승인된 정책으로 정한다.

**발표자가 전달할 한 문장**

> 합성 fixture가 계산된다는 것은 경로가 동작한다는 뜻이고, 실제 보증에는 event mode별 적용 가능한 원문·조건·권리가 별도로 필요합니다.

**20~35초 대본 초안 — `PLANNED 25초`**

“왼쪽은 합성 fixture로 계산 경로를 실행할 수 있다는 뜻입니다. 오른쪽은 실제 보증에 필요한 정확한 부품 시험 근거가 아직 없다는 뜻입니다. 같은 부품명만으로 충분하지 않고, 시험 원문과 조건·공정·로트·사용 권리가 지금 검토하는 부품에 적용되는지 연결해야 합니다.”

파괴성 단일사건 효과의 세부 명칭과 시험 범위는 현재 주 데모에서 읽지 않고 기술 Q&A에서만 다룬다.

**말하면 안 되는 주장**

- 합성 `25 krad(Si)`와 `1×10⁻⁶ cm²/device`가 실제 시험 결과라는 주장
- 모든 부품에 같은 event mode 시험 목록이 무조건 필요하다는 주장
- SEU가 낮으면 파괴성 SEE도 안전하다는 주장
- 공개 접근 가능한 PDF라면 권리 확인 없이 ingest해도 된다는 주장

### 화면 5 — 완화: ECC와 잔여 SEU

**이 화면의 질문**

ECC는 무엇을 줄이고, 무엇을 없애지 못하는가?

**화면 요소가 뜻하는 것**

- 우주 방사선 때문에 메모리에 저장된 정보가 뒤집히면 그 오류가 계산·제어 결과에 남을 수 있다. 현재 데모는 실제 ECC 하드웨어를 구현한 것이 아니라, 수정 가능한 오류를 고친다는 제한된 합성 설계 가정을 residual SEU 계산에 적용한다.
- raw SEU는 완화 전 합성 예상 오류 사건 수다. 현재 residual SEU는 검증된 실제 완화 효과가 아니라 제한된 합성 ECC 설계 가정을 계산에 적용한 뒤의 비교값이다.
- ECC는 Error Correcting Code, 즉 데이터 오류를 탐지·수정하는 기법이다. 적용 범위와 가정이 검증돼야 완화 효과를 주장할 수 있다.
- 합성 예시에서 raw `0.063072 events/mission`, ECC ON residual `0.0063072`, effectiveness factor `0.1`이 표시된다. ECC OFF면 residual은 `0.063072`다.
- ECC는 물리적 SEU 발생 자체를 없애지 않고 다른 event mode의 근거도 대신하지 않는다.
- 실제 설계 채택에는 해당 부품의 ECC 지원 여부, 발생 가능한 오류 패턴, 적용 조건과 효과 근거가 확인돼야 한다.

**발표자가 전달할 한 문장**

> 현재 ECC ON은 실제 하드웨어가 아니라, 고칠 수 있는 메모리 오류가 줄어든다고 가정해 residual SEU를 계산하는 제한된 합성 설계 조건입니다.

이 절의 `0.0063072`는 발표 HTML의 동결 Stage 2 fixture다. H15 Product UI의 current generated payload는 residual `0.013072`를 표시하므로 두 화면의 값을 같은 결과 계층으로 합치지 않는다. Product 시연에서는 화면에 표시된 current 값을 따르고, `0.0063072`는 발표 HTML fallback에서만 해당 동결 fixture로 말한다.

**이해 우선 대본 — `PLANNED 50초`**

“ECC를 고려하는 이유는 방사선 사건을 없애기 위해서가 아닙니다. 메모리 정보가 잘못됐을 때 고칠 수 있는 오류가 줄어든다는 가정을 residual SEU 계산에 반영하기 위해서입니다. 현재 ECC ON은 실제 하드웨어 구현이나 효과 검증이 아니라 제한된 합성 설계 조건입니다. 화면의 변화도 고정 합성 사례 비교이지 실제 성능이 아닙니다. 실제 설계에 쓰려면 이 부품이 해당 ECC를 지원하는지, 예상 오류 패턴과 적용 조건, 효과 근거가 맞는지 확인해야 합니다.”

**말하면 안 되는 주장**

- ECC가 방사선 사건을 90% 방지한다는 실제 효과 주장
- SPECTRA에 실제 ECC 하드웨어가 구현됐거나 화면값으로 효과가 검증됐다는 주장
- residual 값이 실제 임무의 예측값 또는 정확도 검증값이라는 주장
- ECC가 모든 방사선 event mode를 해결한다는 주장
- `engineering_gate=PASS`를 최종 방사선 보증 PASS로 읽는 설명

### 기술 Q&A — WATCHDOG·TMR·SEL 보호 (`현재 주 데모 범위 밖`)

WATCHDOG·TMR·SEL 보호는 현재 사용자가 내릴 임무 설계 결정과 연결되지 않으므로 주 발표와 Product 시연에서 보여 주거나 수치를 읽지 않는다. 저장소에는 향후 실제 시스템 구조가 정해졌을 때 trade study에 사용할 수 있는 결정론적 계산·검증 코드, schema와 합성 fixture가 있다. 실제 하드웨어·장비 제어·현재 임무 채택·효과 입증은 없다.

- **WATCHDOG:** 정지·무응답 감지 뒤 재시작하는 구조를 가정하는 기술 Q&A 항목이다.
- **TMR:** 동일 기능의 복제 채널 3개와 다수결 voter를 가정하며 세 위성이 아니다.
- **SEL 보호:** TMR과 별개인 단일 device·전원 rail 과전류 보호 구조이며 세 장치를 전제로 하지 않는다.

`runtime`, `mitigation`, `false activation`, `projection`, `processing status`, `equation ID`, policy code와 hash도 주 대본에서 읽지 않는다.

### Product 03 — 보증 판단

**이 화면에서 따라갈 세 문장 — `PLANNED 35초`**

1. **확인된 것:** “합성 계산 규칙은 같은 입력에서 같은 결과로 재현되고, 지원 범위 밖에서는 값을 만들지 않습니다.”
2. **아직 필요한 것:** “실제 임무 환경과 정확한 부품 시험 근거, 독립 검토가 아직 연결되지 않았습니다.”
3. **그래서 내린 결정:** “그래서 실패라고 단정하는 대신 승인 판단을 보류합니다.”

**핵심 문장**

> HOLD는 불합격이 아니라, 지금 가진 근거로는 안전하다고 승인하지 않겠다는 상태입니다.

발표자는 네 개의 gap이나 `0건`을 하나씩 읽지 않는다. machine code, provenance·hash와 manufacturer·part·process·die·lot 묶음은 접힌 기술 상세 또는 Q&A에서만 설명한다.

### 화면 6 — 네 가지 신뢰성 안전장치

**이 화면의 질문**

SPECTRA는 틀릴 수 있는 상황에서 어떻게 정답인 척하지 않는가?

**화면 요소가 뜻하는 것**

- `같은 입력 → 같은 결과`: 같은 고정 입력과 버전으로 다시 계산하면 같은 결과를 만든다.
- `지원 범위 밖 → 계산 안 함`: 등록되지 않은 5 mm가 더 좋을 것이라고 추정하지 않는다.
- `실제 근거 부족 → 판단 보류(HOLD)`: 합성 수치 조건이 좋아도 실제 환경·부품·시험 근거가 없으면 승인하지 않는다.
- `전달된 숫자가 다름 → 숫자 숨김`: 계산 직후 기록 60초와 화면에 들어온 테스트 값 999초가 다르면 어느 값도 추측하지 않는다.
- 화면의 기존 `47 / 0` aggregate에는 현재 핵심 발표 범위 밖인 ASR-D03 runtime 18개가 포함된다. 따라서 H11 주 대본에서는 이 횟수를 읽거나 프로젝트 핵심 신뢰성 수치로 사용하지 않는다.
- core profile 후보인 기존 18개와 MVP/ECC 11개의 별도 수치는 Control Tower가 독립 재검증하기 전까지 `UNSET`으로 둔다.
- 다음 행동은 실제 환경 출력, 승인 BOM과 원문 시험 근거, 부품 기술·정책상 필요한 파괴성 SEE별 근거, 독립 보증 재검토다.

**발표자가 전달할 한 문장**

> SPECTRA의 신뢰성은 항상 답을 내는 것이 아니라, 틀릴 수 있는 상황에서 정답인 척하지 않는 것입니다.

**이해 우선 대본 초안 — `PLANNED 40초`**

“SPECTRA의 신뢰성은 네 가지로 확인합니다. 같은 고정 입력과 버전은 같은 결과를 내고, 등록되지 않은 5밀리미터는 더 좋을 것이라고 추정하지 않습니다. 실제 환경·부품·시험 근거가 없으면 판단을 보류하고, 계산 직후 원래 기록과 화면 테스트 값이 다르면 숫자를 숨깁니다. 핵심은 공격 횟수가 아니라 잘못되거나 누락된 데이터를 정상인 것처럼 통과시키지 않는 것입니다.”

**말하면 안 되는 주장**

- `Engineering gate PASS`가 최종 승인·인증·비행 적합성이라는 주장
- `HOLD`가 부품 불합격이나 프로젝트 실패를 뜻한다는 주장
- 모든 부품에 동일한 파괴성 SEE 시험 목록을 강제한다는 주장
- 화면의 `47 / 0` aggregate를 프로젝트 핵심 신뢰성 수치로 읽는 주장
- core profile을 Control Tower 독립 재검증 전에 별도 통과 수치로 제시하는 주장

### Product 04 — 숫자 변경 감지: 결과 전달 layer

**계산과 전달 단계의 구분**

- **현재 주 데모의 계산:** 차폐·TID·SEU·ECC와 근거 조건을 계산하고, 지원 범위 밖이면 값을 만들지 않는다.
- **숫자 변경 감지:** 그 계산이 끝난 뒤 결과가 Product 화면까지 전달되는 동안 값이 달라졌는지 확인한다.

**전환 문장**

> 앞에서는 차폐와 ECC가 바꾸는 값을 확인했습니다. 지금 보는 숫자 변경 감지는 계산이 끝난 뒤 그 결과가 화면까지 그대로 전달됐는지를 확인하는 별도 안전장치입니다.

`60 → 999`는 해킹 성공이나 새 계산 결과가 아니다. 전달 과정의 부분 불일치를 일부러 만든 고정 오류 주입 테스트이며, 서로 다르면 숫자를 숨기고 판단을 보류하는지를 확인한다.

### H11 주 발표 — 세 Agent의 증거 책임과 GCP 실행 경계

**한 문장 원칙**

> Agent가 방사선 숫자를 만드는 것이 아니라, 서로 다른 증거 책임을 나누고 결정론적 Core의 결과를 근거 없이 PASS로 승격하지 못하게 합니다.

| 역할 | 책임 | 하지 않는 일 | 실패할 때 |
|---|---|---|---|
| Environment Agent | 임무·환경 모델 metadata, 버전과 provenance 필수 항목을 확인하고 결정론적 Core 호출 결과를 전달 | 환경 수치 창작, 범위 밖 추정, 과학 정확성 승인 | `NOT_EVALUATED/HOLD` |
| Parts Evidence Agent | exact-part identity, 시험 event coverage, 원문 locator, 권리·출처 상태를 확인 | 유사 부품 근거를 exact match로 승격, 시험값 창작, 최종 적합성 승인 | `NOT_EVALUATED/HOLD` |
| Independent Assurance Agent | 앞선 두 결과와 Core 결과의 schema·status·hash 일관성, 차단 gap과 최종 상태를 독립 확인 | 앞 Agent의 결론을 그대로 복사, 누락된 근거를 PASS로 보정 | `NOT_EVALUATED/HOLD` |

**초심자 대본 — `PLANNED 55초`**

“세 Agent는 계산을 셋으로 나누는 구조가 아닙니다. Environment Agent는 이 결과가 어떤 임무와 환경 모델에서 왔는지 확인합니다. Parts Evidence Agent는 정확한 부품과 시험 원문, 조건과 권리가 연결됐는지 확인합니다. Independent Assurance Agent는 앞의 결론을 그대로 믿지 않고 결과 형식과 상태, 데이터 지문과 증거 공백을 다시 확인합니다. 실제 숫자 계산과 최종 gate는 결정론적 Core가 소유합니다. 어느 역할이 실패해도 다음 Agent가 빈칸을 추측해 채우지 않고 `NOT_EVALUATED`와 `HOLD`로 닫습니다.”

**GCP 목표 실행 흐름 — `PLANNED 50초`**

`Cloud Storage synthetic input → Workflows → Environment Agent on Cloud Run → Parts Evidence Agent on Cloud Run → Independent Assurance Agent on Cloud Run → Storage result + Cloud Logging trace`

“GCP를 쓰는 이유는 파일을 클라우드에 올리기 위해서만이 아닙니다. H04 목표에서 Workflows가 세 역할의 호출 순서와 실행 식별자를 고정하고, Cloud Run이 역할별 서비스를 분리합니다. Storage는 합성 입력과 결과의 exact object 경계를, Logging은 같은 실행의 상태와 오류를, IAM은 누가 어떤 역할을 호출할 수 있는지를 남깁니다. timeout, HTTP 오류, 잘못된 응답이 생기면 다음 단계로 낙관적으로 우회하지 않고 `HOLD`로 끝내는 실행·격리·감사 인프라입니다.”

현재 H04는 병렬 진행 중이다. 다음 필드는 검증 전 발표에서 읽거나 추정하지 않는다.

| H04 증거 필드 | H11 상태 |
|---|---|
| 실제 Cloud Run·Workflows·Storage resource명 | `PENDING_H04_VERIFICATION` |
| Workflow execution ID·Cloud Run request/log correlation ID | `PENDING_H04_VERIFICATION` |
| Storage object generation·SHA-256 관측값 | `PENDING_H04_VERIFICATION` |
| 실제 IAM binding 관측, latency, 비용, 성공 횟수 | `PENDING_H04_VERIFICATION` |

GCP 실행이 나중에 성공하더라도 입력은 합성 fixture이고 실제 환경·승인 BOM·시험 원문이 없으므로 최종 방사선 assurance는 계속 `HOLD`다.

**화면 운용 경계**

- 현재 H15 화면에는 이 Agent/GCP 아키텍처의 live 상태 화면이 없다. H11은 발표 deck 07 Evidence Chain을 배경으로 위 책임 구조를 말한다.
- 실제 H04 증거를 화면에 추가하려면 Workstream 80 change request와 H04 검증 결과가 먼저 필요하다.
- WATCHDOG·TMR·SEL runtime은 이 Agent/GCP 흐름과 핵심 신뢰성 설명에서 제외한다.

### 화면 7 — Evidence Chain과 다음 경로

**이 화면의 질문**

SPECTRA는 판단과 함께 무엇을 남기며, 현재 로컬 데모와 미래 GCP 배포는 어떻게 다른가?

**화면 요소가 뜻하는 것**

- Evidence Chain 5단계는 `Input → Model → Integrity → Rights → Decision`이다.
- run ID는 특정 계산 실행을 식별한다. SHA-256은 파일이나 preimage의 동일성·변조 탐지를 돕지만 과학적 진실성·적용성·권리를 증명하지 않는다.
- provenance는 값이 어느 입력·모델·버전·계산·원문에서 왔는지 남기는 계보이다.
- rights gate는 저장·처리·재배포 권한을 확인하기 전 ingest를 막는 경계다. ingest는 외부 자료를 시스템에 들여와 구조화·저장하는 과정이다.
- 현재 Product는 로컬 합성 snapshot을 표시하며 실제 환경 model run과 승인 BOM·시험 PDF는 0이다.
- Workstream 70 H04가 실제 GCP E2E를 병렬 진행 중이므로 resource·호출·IAM·로그·비용의 현재 상태는 `PENDING_H04_VERIFICATION`이다. H11은 0이나 성공으로 단정하지 않는다.

**발표자가 전달할 한 문장**

> SPECTRA는 입력부터 권리와 판정까지 계보를 남기고, 근거가 부족하면 다음에 확보할 증거를 요구하며 `HOLD`합니다.

**20~35초 대본 초안 — `PLANNED 25초`**

“마지막은 Evidence Chain입니다. 입력, 모델, 실행 무결성, 자료 권리, 최종 판단을 한 줄로 남깁니다. 현재 Product는 로컬 합성 snapshot이고 실제 환경 run과 승인 BOM·시험 PDF는 0입니다. GCP 실행 증거는 H04 독립 검증 전이라 resource명과 execution ID, 비용과 성공 수치를 아직 말하지 않습니다. `HOLD`는 실패가 아니라 다음 근거를 요구하는 안전한 결과입니다.”

**말하면 안 되는 주장**

- SHA-256이 자료 내용의 과학적 진실성·권리·작성자 신원을 증명한다는 주장
- H04 독립 검증 전에 실제 GCP resource명, execution ID, latency, 비용 또는 성공 횟수를 말하는 주장
- target architecture나 배포 성공을 실제 방사선 assurance 완료로 확대하는 주장
- Product 04의 `PLANNED 70초` 결과 전달 오류 테스트를 이 화면에서 반복하는 것. 연결은 “앞의 세 안전장치는 계산 재현, 지원 범위와 증거 공백을 확인했습니다. 마지막으로 계산은 60초였는데 화면에 전달된 값만 999초로 달라진 상황을 일부러 만들어 보겠습니다” 한 문장으로 제한한다.

## 3. 초심자용 용어집

| 용어 | 한글 이름 / 쉬운 설명 | 이 화면에서의 의미 | 주의할 오해 |
|---|---|---|---|
| assurance | 보증 검토 / 결과를 실제 판단에 써도 되는지 근거와 승인을 확인하는 과정 | 계산 완료와 최종 판단을 분리 | 인증 완료나 `PASS`와 같은 뜻이 아님 |
| 고장 대응 방법(runtime mitigation) | 동작 중 고장을 버티거나 복구하는 구조의 trade study | **현재 주 데모 범위 밖** 기술 Q&A | 실제 하드웨어 제어, 현재 임무 채택 또는 효과 입증을 뜻하지 않음 |
| 자동 재시작(WATCHDOG) | 정지·무응답 감지 뒤 다시 시작하는 구조 | **현재 주 데모 범위 밖** 기술 Q&A | 실제 WATCHDOG 하드웨어나 장비 제어가 구현됐다는 뜻이 아님 |
| 3중 다수결(TMR) | 동일 기능의 복제 채널 3개와 다수결 voter를 가정 | **현재 주 데모 범위 밖** 기술 Q&A | 세 위성이 아니며 실제 신뢰도 효과가 입증된 것도 아님 |
| 과전류 전원 보호(SEL 대응) | 한 device·전원 rail의 위험 전류를 차단·복구하는 별도 구조 | **현재 주 데모 범위 밖** 기술 Q&A | TMR·세 장치 가정이 아니며 실제 보호 하드웨어도 없음 |
| 숫자 변경 감지 | 계산 뒤 결과가 화면까지 전달되는 동안 값이 달라졌는지 확인 | Product 04의 고정 오류 주입 테스트 | 고장 대응 trade study와 다른 layer이며 해킹 성공도 뜻하지 않음 |
| 테스트용 사본(clone) | 원본을 보존한 채 시험하기 위해 만든 별도 사본 | 사본의 `60`만 `999`로 변경 | 원본 payload가 손상됐다는 뜻이 아님 |
| 변경된 테스트 결과 | 오류·잘못된 수정·부분 변조를 재현하기 위해 숫자 하나를 바꾼 사본 | `60 → 999초` | `999`가 새 계산이나 실제 중단 시간이라는 뜻이 아님 |
| 정상 계산 당시 저장한 원래 기록 | 정상 결과를 만들 때 함께 저장한 내용과 데이터 지문 입력 | 원래 기록은 `60`, 화면 입력은 `999`를 가리킴 | 원래 기록만으로 과학 정확성·권리까지 증명하지 않음 |
| 부분 불일치·부분 변조 | 결과 일부만 바뀌어 원래 기록과 맞지 않는 상태 | 숫자 하나가 달라진 합성 시연 | 해커 침입·공격자 신원·프로젝트 전체 보안 검증과 같지 않음 |
| 결과 사용 불가(`DATA_UNAVAILABLE`) | 들어온 결과를 신뢰해 표시할 수 없는 처리 상태 | 대상 숫자·식별 정보를 숨김 | 실제 값이 0이거나 부품이 불합격이라는 뜻이 아님 |
| 평가하지 않음(`NOT_EVALUATED`) | 믿을 수 있는 입력이 없어 수치 조건을 평가하지 않은 상태 | 변경된 record의 공학 평가를 중단 | 평가 결과가 나쁨 또는 FAIL이라는 뜻이 아님 |
| BOM | 부품 목록 / 설계에 들어가는 부품과 수량의 명세 | 화면 2의 합성 Memory ×2 입력 | 승인 BOM이나 실제 구매 목록이 아님 |
| exact identity | 정확한 부품 식별 / 시험자료가 같은 대상을 가리키는지 확인하는 식별자 묶음 | manufacturer·PN·process·die·lot | 제품군 이름이 같다고 동일 부품 근거가 되지 않음 |
| PN | 정확한 부품번호(Part Number) | 합성 `EX-100` | 실제 판매 부품이나 추천 품목이 아님 |
| process | 제조 공정 | 합성 `P1` | PN이 같아도 공정 변경 영향을 무시하면 안 됨 |
| die | 반도체 다이 / 실제 회로가 만들어진 칩 판본 | 실제 evidence 적용성에 필요한 identity | 현재 화면에는 실제 die 정보가 없음 |
| lot | 제조 로트 / 같은 생산 묶음 | 합성 `LOT-A` | 다른 lot의 시험을 자동 동일시하지 않음 |
| TID | 총 이온화 선량 / 임무 동안 누적되는 방사선 선량 효과 | 합성 차폐 후 `6.0 krad(Si)` | 실제 환경 출력이나 시험 선량이 아님 |
| SEE | 단일사건 효과 / 한 입자 사건이 만드는 영향의 상위 개념 | SEU·SEL·SEB·SEGR을 구분하는 범주 | 서로 다른 mode를 하나의 수치로 대체하지 않음 |
| SEU | 단일사건 업셋 / 저장 정보 등이 순간적으로 바뀌는 오류 | raw·residual SEU 합성 비교 | SEL·SEB·SEGR 근거를 대신하지 않음 |
| SEL | 단일사건 래치업 / 기생 전도 경로가 켜지는 현상 | **현재 주 데모 범위 밖** 기술 Q&A | 화면의 합성 placeholder가 실제 증거가 아님 |
| SEB | 단일사건 번아웃 / 전력 소자 등에 파괴를 일으킬 수 있는 현상 | 독립 event evidence 0건 | 모든 부품에 동일하게 적용되는 시험 요구는 아님 |
| SEGR | 단일사건 게이트 파열 / gate 절연막 손상 가능 현상 | 독립 event evidence 0건 | SEU 수치로 안전성을 대신 판단하지 않음 |
| krad(Si) | 실리콘 기준 킬로라드 / `1 krad=1000 rad`, `1 rad=0.01 Gy` | TID 표시 단위 | 단위 설명이 합성값의 과학 정확성을 보증하지 않음 |
| 설계계수 | 요구 여유를 정하는 사용자·정책 입력 | `요구 TID = 차폐 후 TID × 2` | 2가 보편 표준이나 승인값이 아님 |
| 차폐 | 재료로 방사선 영향을 낮추는 설계 수단 | 합성 1·2·4 mm 비교 | 두께 하나만으로 실제 부품 적합성이 결정되지 않음 |
| 재현 가능 | 같은 입력·버전으로 다시 실행하면 같은 결과 | 첫 번째 안전장치 `같은 입력 → 같은 결과` | 같은 결과가 과학적으로 정확하거나 실제 임무에 적용 가능하다는 뜻은 아님 |
| 지원 범위 | 현재 모델이 값을 제공하도록 등록된 범위 | 1·2·3·4 mm는 등록, 5 mm는 범위 밖 | 범위 밖 값을 더 좋을 것이라고 추정하지 않음 |
| 오류 주입 테스트 | 일부러 잘못된 값을 넣어 안전하게 멈추는지 확인하는 시험 | 테스트용 사본의 `60 → 999` 변경 | 실제 공격이나 새 계산 결과가 아님 |
| 잘못된 PASS(False PASS) | 실제로는 멈춰야 하는데 통과한 경우 | core profile 수치는 독립 재검증 전 `UNSET` | 기존 `47 / 0` aggregate에는 주 범위 밖 runtime 18개가 포함돼 핵심 수치로 사용하지 않음 |
| 고정 합성 테스트 세트 | 미리 정한 가짜 사례 모음 | 단위·범위·식별·증거·정책·결과 변경 검증 | 실제 임무·GCP·과학 정확성 전체를 대표하지 않음 |
| deterministic | 결정론적 / 같은 고정 입력·버전이면 같은 결과 | snapshot 재현성 | 과학적 정확성이나 실제 적용성의 증명이 아님 |
| snapshot | 고정 결과 묶음 / 미리 계산·검증해 저장한 화면 값 | 브라우저가 물리 계산하지 않고 표시 | live model run이나 실측값이 아님 |
| lookup | 등록값 조회 / table의 정확한 항목 선택 | 1/2/3/4 mm만 사용 | 연속 물리 모델 계산과 같지 않음 |
| interpolation | 보간 / 등록값 사이 값을 추정 | 현재 데모는 하지 않음 | 3 mm가 table에 있다고 임의 중간값을 만드는 것이 아님 |
| extrapolation | 외삽 / 등록 범위 밖 값을 추정 | 5 mm에서 금지 | 범위 밖을 낙관적으로 계산하지 않음 |
| ECC | 오류정정코드 / 데이터 오류를 찾고 고치는 기법 | 제한된 합성 설계 가정의 residual SEU 비교 | 실제 하드웨어 구현·효과 검증이 아니며 물리적 사건과 다른 event mode를 없애지 않음 |
| raw SEU | 완화 전 SEU 예상량 | 합성 `0.063072 events/mission` | 실제 임무 예측값이 아님 |
| residual SEU | 합성 ECC 가정을 계산에 적용한 뒤 남는 비교값 | 발표 HTML ECC ON 합성 `0.0063072` | 실제 ECC 하드웨어 효과 측정값이 아님 |
| synthetic fixture | 합성 시험 입력 / 코드 경로를 재현하기 위한 가짜 사례 | 임무·BOM·환경·시험·정책 입력 | 실제 부품 evidence로 승격하지 않음 |
| physical evidence | 물리적 실제 근거 / 현실의 환경·시험·부품에 적용 가능한 원문과 조건 | 현재 0건인 실제 evidence | 단순 PDF 존재만으로 적용성과 권리가 충족되지 않음 |
| blocking gap | 승인을 막는 증거 공백 | `SYNTHETIC_ONLY` | 부품 불합격과 같은 뜻이 아님 |
| fail-closed | 안전하게 닫기 / 확신할 수 없으면 숫자를 추측하지 않고 멈추는 원칙 | 범위 밖·증거 부족·부분 불일치에서 비노출과 `HOLD` | 시스템 오류를 숨기거나 60을 자동 정답으로 복구하는 정책이 아님 |
| HOLD | 판단 보류 / 다음 근거를 요구하는 안전 상태 | 방사선 evidence와 숫자 변경 감지 장면의 최종 판단 | 실패·불합격·PASS와 동일하지 않음 |
| run ID | 계산 실행 식별자 | `sim-3cc00f2c824db56d` 등 snapshot 실행 연결 | 사람·고객·승인자 신원을 뜻하지 않음 |
| SHA-256/hash | 데이터 지문 / 같은 bytes인지 확인하는 기술 상세 | 정상 계산 당시 기록과 결과의 동일성 확인 보조 | 과학적 진실성·권리·전자서명·작성자 신원을 증명하지 않음 |
| integrity | 결과 일치성 확인 / 화면 입력과 정상 계산 당시 기록이 같은 내용을 가리키는지 확인하는 기술 용어 | Evidence Chain의 기술 상세와 `숫자 변경 감지` 장면의 내부 원리 | 주 대본에서 이해를 전제로 하지 않으며 프로젝트 전체 보안을 뜻하지 않음 |
| provenance | 출처 계보 / 값의 입력·모델·버전·원문·계산 경로 | 판정 재현과 감사 연결 | 출처가 있다는 사실만으로 품질이 충분하지 않음 |
| rights gate | 권리 관문 / 저장·처리·재배포 권한 확인 전 차단 | Evidence Chain의 4단계 | 공개 접근 가능과 사용 권한은 같지 않음 |
| ingest | 자료 반입 / 외부 자료를 시스템에 들여와 구조화·저장 | 권리 확인 뒤 수행할 단계 | 현재 실제 BOM·시험 PDF ingest가 있다는 뜻이 아님 |
| GCP resource | GCP 자원 / 클라우드 저장·실행·IAM·로그 등에 쓰는 실제 자원 | H04 독립 검증 전 `PENDING_H04_VERIFICATION` | target 구조만으로 실제 생성·실행 성공을 뜻하지 않음 |
| Environment Agent | 임무·환경 모델 metadata와 provenance 책임 역할 | 결정론적 Core 결과의 입력·출처 조건 확인 | 방사선 수치를 생성하거나 과학 정확성을 승인하지 않음 |
| Parts Evidence Agent | exact-part 시험 근거·권리 책임 역할 | identity·event coverage·원문 locator·권리 상태 확인 | 유사 부품을 exact match로 승격하거나 시험값을 만들지 않음 |
| Independent Assurance Agent | 앞선 결과를 독립 재검토하는 역할 | schema·status·hash·blocking gap 일관성 확인 | 누락 근거를 보정하거나 PASS를 창작하지 않음 |
| Workflows | Agent 호출 순서와 실행 context를 고정하는 GCP orchestration 서비스 | timeout·오류·invalid response의 fail-closed 흐름 | H04 검증 전 실제 execution ID나 성공을 주장하지 않음 |
| Cloud Run | 역할별 Agent 서비스를 분리 실행하는 GCP target | 공개 endpoint 없이 역할·service account 격리 목표 | H04 검증 전 실제 service·revision·request를 주장하지 않음 |
| Cloud Storage·Logging·IAM | 입력·결과 object, 실행 trace, 호출 권한의 저장·감사 경계 | generation·hash·run ID·권한을 연결할 H04 target | 실제 관측값은 모두 `PENDING_H04_VERIFICATION` |

## 4. 7개 본문 화면 연속 대본 — `PLANNED 3분 32초`

| 화면 | 계획 시간 | 발표 대본 |
|---:|---:|---|
| 1 | 22초 | “계산 도구는 이미 있지만 환경 출력, 정확한 부품, 시험 조건과 승인이 서로 다른 파일에 흩어져 있습니다. 이 네 가지가 같은 임무와 부품을 가리킨다는 연결이 없으면 계산값만으로 보증 결론을 낼 수 없습니다.” |
| 2 | 23초 | “그래서 합성 임무 하나와 부품 하나에서 시작합니다. BOM은 부품 목록이며 제조사, 정확한 부품번호, 공정, die, lot, 수량을 함께 확인해야 합니다. 화면의 LEO와 EX-100은 합성 예시이고 승인 BOM은 0건입니다.” |
| 3 | 27초 | “합성 2밀리미터 snapshot은 차폐 후 TID 6.0, 요구 TID 12.0 krad(Si)를 보여 줍니다. 요구량은 차폐 후 TID에 합성 설계계수 2를 곱한 값입니다. 등록된 1·2·3·4밀리미터만 조회하고 5밀리미터는 이 표의 범위 밖이라 추정하지 않습니다.” |
| 4 | 25초 | “합성 fixture로 계산할 수 있다는 것과 실제 보증 근거가 충분하다는 것은 다릅니다. 시험 원문과 조건·공정·로트·사용 권리가 지금 검토하는 정확한 부품에 적용되는지 연결해야 합니다.” |
| 5 | 50초 | “현재 ECC ON은 실제 하드웨어가 아니라, 고칠 수 있는 메모리 오류가 줄어든다고 가정해 residual SEU를 계산하는 제한된 합성 설계 조건입니다. 화면의 변화는 실제 효과 검증이 아닙니다. 실제 채택에는 부품의 ECC 지원, 오류 패턴, 적용 조건과 효과 근거가 필요합니다.” |
| 6 | 40초 | “신뢰성은 네 가지입니다. 같은 고정 입력과 버전은 같은 결과를 내고, 등록되지 않은 5밀리미터는 계산하지 않습니다. 실제 환경·부품·시험 근거가 없으면 `HOLD`하고, 계산 직후 원래 기록과 화면 테스트 값이 다르면 숫자를 숨깁니다. 핵심은 공격 횟수가 아니라 잘못되거나 누락된 데이터를 정상인 것처럼 통과시키지 않는 것입니다.” |
| 7 | 25초 | “마지막 Evidence Chain은 입력, 모델, 무결성, 권리, 판정을 연결합니다. 현재 Product는 로컬 합성 snapshot이고 실제 환경 run과 승인 BOM·시험 PDF는 0입니다. GCP resource와 execution·비용 증거는 H04 독립 검증 전이라 `PENDING_H04_VERIFICATION`입니다. `HOLD`는 실패가 아니라 다음 근거를 요구하는 안전한 결과입니다.” |
| 합계 | **212초** | **`PLANNED 3분 32초` — 표지 제외, 사람 리허설 미실행** |

Product 04 연결 문장은 “앞에서는 차폐와 ECC가 바꾸는 값, 근거 연결과 `HOLD`를 확인했습니다. 지금 보는 숫자 변경 감지는 계산이 끝난 뒤 그 결과가 화면까지 그대로 전달됐는지를 확인하는 별도 안전장치입니다”로 제한한다. 상세는 `PLANNED 70초` 결과 전달 오류 테스트 runbook을 사용하며 이 212초 대본에 중복 추가하지 않는다.

## 5. 현재 구현·목표 문구·미구현 경계

| 구분 | 현재 사실 |
|---|---|
| 현재 구현 | `demo/index.html` 7개 본문 화면과 현재 소스의 번호 없는 표지, 합성 snapshot, 1/2/4/5 mm 경계, ECC OFF/ON, 최종 `HOLD`, Product 숫자 변경 감지 |
| H15 제출 문구 | 번호 없는 표지; ECC 인과·채택 조건; Product 03의 `확인된 것 → 아직 필요한 것 → 그래서 내린 결정`; Product 04의 계산 결과 생성 layer·결과 전달 layer 구분 |
| H15 대조 상태 | 2026-08-21 H15 `READY_FOR_REVIEW` handoff와 current source의 표지·Product 02·03·04 문구 exact 대조 완료. H15 actual browser는 `NOT_EVALUATED`, Control Tower `VERIFIED` 전 |
| 주 데모 밖 실험 범위 | 시스템 수준 고장 대응 대안의 계산·검증 코드와 합성 fixture는 주 발표에서 사용하지 않으며, 실제 하드웨어·장비 제어·현재 임무 채택·효과 입증을 뜻하지 않는다. |
| 미구현·0 | 실제 환경 model run, 승인 BOM, 실제 시험 PDF·실제 수치 |
| H04 검증 대기 | 실제 GCP resource명·execution ID·generation/hash·IAM 관측·latency·비용·성공 횟수는 `PENDING_H04_VERIFICATION` |
| 미검증 | 합성값의 과학적 정확성, 실제 부품 적합성·인증, 실제 사용자 시간·비용 절감, 구매 의사, pilot 가치 |

## 6. 전체 발표 구조 — 이해 우선 `PLANNED 6분 45초 core + 선택 1분`

### 6분 45초 core — `PLANNED 405초`

| 구간 | 시간 | 화면·행동 | 핵심 대사 |
|---|---:|---|---|
| 표지·범위 선언 | 0:00–0:20, 20초 | H15 제출 표지 | 표지 시작 대본 뒤 “오늘 보시는 수치는 합성 데모이며 실제 방사선 보증 결과는 아닙니다”를 한 번만 말한다. |
| 문제와 제품 가치 | 0:20–1:00, 40초 | 발표 deck 1~2 | “계산 도구가 없는 것이 아니라 환경 출력, 정확한 부품 목록, 시험 원문과 승인이 같은 임무·부품에 연결되지 않는 것이 문제입니다. SPECTRA는 계산값과 함께 연결된 근거, 보류 이유와 다음 행동을 남깁니다.” |
| 결정론적 Core | 1:00–1:45, 45초 | 발표 deck 3·Product 02 | 차폐·TID·SEU를 같은 입력·버전에서 재현하고 5 mm는 추정하지 않는다. ECC ON은 실제 하드웨어가 아니라 residual SEU 계산용 제한된 합성 설계 가정이다. 계산과 gate는 Agent가 아닌 결정론적 Core가 소유한다. |
| 세 Agent의 증거 책임 | 1:45–2:40, 55초 | 발표 deck 7 Evidence Chain 배경 | Environment는 임무·모델·provenance, Parts Evidence는 exact-part 시험·권리, Independent Assurance는 schema·status·hash·gap 일관성을 책임진다. 어느 Agent도 숫자나 PASS를 만들지 않는다. |
| GCP 실행·격리·감사 | 2:40–3:30, 50초 | 발표 deck 7 배경; H04 target flow를 말로 설명 | Workflows가 순서를 고정하고 Cloud Run이 역할을 분리하며 Storage·Logging·IAM이 object·trace·호출 권한을 남긴다. 실제 resource명·execution ID·latency·비용·성공 횟수는 `PENDING_H04_VERIFICATION`이다. |
| fail-closed 보증 판단 | 3:30–4:15, 45초 | Product 03 → Product 04 압축 동선 | 실제 근거 누락, 범위 밖, Agent 실패, 결과 불일치에서 숫자나 판정을 추측하지 않고 `NOT_EVALUATED/HOLD`로 닫는다. 화면의 runtime 수치와 `47 / 0` aggregate는 읽지 않는다. |
| 사용자 행동과 차별점 | 4:15–5:00, 45초 | Product 03 다음 행동·발표 deck 7 | “무엇이 부족해 승인을 보류했는지와 다음에 연결할 환경·부품·시험 근거를 보여 줍니다.” 같은 입력 재현, 범위 밖 비추정, 증거 부족 비승인, 전달 불일치 비노출을 한 번에 정리한다. |
| 한계·팀 연결·다음 단계 | 5:00–6:25, 85초 | 현재 진실·다음 경로 원고 | 실제 환경 run·승인 BOM·시험 원문은 0이다. H04 cloud 증거는 전부 검증 대기다. Environment·Parts·Assurance·Platform·Product 산출물이 공통 계약으로 연결되며, 다음은 H04 독립 검증 → 실제 임무 환경·권리 → exact-part 시험 근거 → 실제 ECC 채택 근거 → 사용자 pilot 순서다. |
| 마무리 | 6:25–6:45, 20초 | 결론 화면 | “SPECTRA의 목표는 항상 답을 내는 것이 아닙니다. 믿을 수 있는 근거가 있을 때만 답하고, 그렇지 않으면 왜 멈췄는지와 다음 행동을 보여 주는 것입니다.” |
| 합계 | **405초** |  | **`PLANNED 6분 45초`** |

시간 산술: `20 + 40 + 45 + 55 + 50 + 45 + 45 + 85 + 20 = 405초`.

### 선택 가능한 1분 확장 — `PLANNED 60초`

core 사실과 결론은 바꾸지 않고 발표 시간이 허용될 때만 붙인다.

| 확장 | 시간 | 내용 |
|---|---:|---|
| Evidence Chain 보충 | 20초 | 입력 → 모델 → 결과 일치성 → 권리 → 판정의 다섯 단계와 run ID·출처 계보를 설명한다. |
| GCP 보충 | 20초 | Workflows·Cloud Run·Storage·Logging·IAM의 실행·격리·감사 역할을 설명하고 H04 실제 증거 필드는 `PENDING_H04_VERIFICATION`이라고 말한다. |
| 기술 Q&A 보충 | 20초 | 데이터 지문만 비교하지 않고 정상 계산 당시 기록의 내용과 들어온 결과도 대조한다는 원리를 설명한다. |
| 합계 | **60초** | **`PLANNED 1분`** |

전체 확장 산술: `405 + 60 = 465초 = 7분 45초`. 1분 확장을 빼도 문제·결정론적 Core·Agent 책임·GCP 실행 경계·fail-closed·가치·한계·다음 단계·마무리는 core에 모두 남는다. 모든 시간은 사람 리허설 전 `PLANNED`다.

## 7. H11 우선 Q&A — 질문당 `PLANNED 30~45초`

### Q1. 왜 하나의 AI가 아니라 세 Agent인가요?

**결론:** 계산을 세 번 시키기 위해서가 아니라 서로 다른 증거 책임을 분리하고 독립 검토가 앞선 결론을 그대로 승인하지 못하게 하기 위해서입니다.

Environment Agent는 임무·모델·provenance, Parts Evidence Agent는 exact-part 시험·권리, Independent Assurance Agent는 schema·status·hash·blocking gap을 맡습니다. 숫자 계산과 gate는 결정론적 Core가 소유하고, Agent는 누락된 값을 상상해 채우지 않습니다.

### Q2. Agent가 할루시네이션을 만들면 어떻게 막나요?

**결론:** Agent의 자연어 출력에는 계산이나 최종 PASS 권한이 없습니다.

Core의 schema와 결정론적 함수가 숫자와 상태를 만들고, 지원 범위 밖·필수 필드 누락·불일치·invalid response는 `NOT_EVALUATED/HOLD`로 닫습니다. Independent Assurance도 실제 근거가 없는 결과를 PASS로 승격할 수 없습니다. 화면의 기존 `47 / 0` aggregate는 runtime 범위가 섞여 있어 핵심 신뢰성 수치로 사용하지 않습니다.

### Q3. 왜 GCP가 필요한가요? 로컬에서 실행하면 안 되나요?

**결론:** GCP의 가치는 단순 저장이 아니라 순서 고정, 역할 격리, object identity와 감사 trace를 실제 실행 경계로 만드는 데 있습니다.

H04 목표에서 Workflows가 순서와 실행 context를 고정하고 Cloud Run이 역할을 분리합니다. Storage는 exact object generation과 결과를, Logging은 같은 run의 상태·오류를, IAM은 호출 권한을 남깁니다. 다만 실제 H04 증거는 아직 독립 검증 전입니다.

### Q4. GCP가 실제로 배포됐나요?

**결론:** H04 독립 검증 전이므로 실제 배포 완료를 주장하지 않습니다.

resource명, Workflow execution ID, Cloud Run request/log correlation ID, Storage generation·hash, IAM 관측, latency, 비용과 성공 횟수는 모두 `PENDING_H04_VERIFICATION`입니다. target architecture와 구현 진행 사실을 live E2E 성공 증거로 바꾸지 않습니다.

### Q5. 한 Agent가 멈추면 나머지가 계속 진행하나요?

**결론:** 실패한 역할을 건너뛰고 낙관적인 결론을 만들지 않습니다.

Workflows target contract는 timeout·HTTP 오류·invalid response를 구조화된 실패로 처리하고 최종 결과를 `NOT_EVALUATED/HOLD`로 닫습니다. 실제 failure execution ID와 log는 H04 검증 전 `PENDING_H04_VERIFICATION`입니다.

### Q6. GCP 실행이 성공하면 실제 부품을 안전하다고 말할 수 있나요?

**결론:** 아닙니다. 실행 성공과 방사선 assurance는 서로 다른 주장입니다.

합성 fixture가 세 Agent와 GCP 경로를 통과해도 실제 임무 환경, 승인 BOM, exact-part 시험 원문과 권리가 없으면 최종 판단은 `HOLD`입니다. cloud 성공은 orchestration·격리·감사 증거일 뿐 실제 부품 적합성 증거가 아닙니다.

## 8. 가치·차별점·한계·다음 단계 체크

### 제품 가치

> 계산값만 보여 주는 도구가 아니라, 어떤 근거가 연결됐고 무엇이 부족해 판단을 보류했는지까지 보여 줍니다.

### 차별점

- 같은 입력은 같은 결과로 재현한다.
- 지원하지 않는 범위는 추정하지 않는다.
- 실제 근거가 부족하면 승인하지 않는다.
- 계산 뒤 전달된 숫자가 달라지면 숨긴다.
- AI는 근거 후보 탐색·구조화·설명을 돕고, 결정론적 코드는 계산·정책·gate를 담당한다. 이유와 다음 행동이 명확한 `HOLD`도 정상 제품 결과다.
- 사용자 시간·비용 개선, 구매 의사와 pilot 가치는 아직 `UNVALIDATED`다.

### 현재 한계

- 모든 데모 값은 `SYNTHETIC`이다.
- 승인된 실제 environment contract·BOM·시험 원문은 0이다.
- H04 실제 GCP resource명·execution ID·관측값·latency·비용·성공 횟수는 독립 검증 전 `PENDING_H04_VERIFICATION`이다.
- 시스템 수준 고장 대응 대안과 관련 합성 수치는 현재 주 발표·Product 시연에서 다루지 않는다.
- 과학 정확성·인증·비행 suitability·프로젝트 전체 보안을 검증한 결과가 아니다.

### 다음 단계

1. 실제 임무 환경 산출물과 권리·출처를 연결한다.
2. 승인 BOM의 exact-part 시험 근거를 연결한다.
3. 실제 부품의 ECC 지원, 오류 패턴·적용 조건·효과 근거와 채택 정책을 검토한다.
4. H04의 실제 Workflows·Cloud Run·Storage·Logging·IAM 실행 증거를 독립 검증한다.
5. 실제 근거를 연결한 뒤 독립 assurance와 GCP 운영 경계를 함께 재검토한다.
6. 사용자 인터뷰·사람 리허설·pilot으로 제품 가치 가설을 측정한다.

### 마무리 핵심

> SPECTRA의 목표는 항상 답을 내는 것이 아닙니다. 믿을 수 있는 근거가 있을 때만 답하고, 그렇지 않으면 왜 멈췄는지와 다음 행동을 보여 주는 것입니다.

`CONTRACT_CHANGE_REQUEST`:

1. H15가 기록한 결과 계층 결정을 인수한다. 발표 HTML의 동결 Stage 2 residual `0.0063072`와 Product current generated payload residual `0.013072` 중 Product가 어느 결과 계층을 대표할지 Control Tower 후속 계약이 필요하다. H11은 값을 통합하거나 authoritative source를 변경하지 않는다.
2. Workstream 80에 Agent/GCP 아키텍처와 H04 검증 상태를 보여 줄 평가용 화면을 요청한다. H04 검증 전 실제 resource·execution·측정값은 모두 `PENDING_H04_VERIFICATION`으로 표시해야 하며, H11은 Product/demo 코드를 수정하지 않는다.
