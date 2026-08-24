# SPECTRA 우주항공 교수 독립 재평가 — Post H14

- 평가일: 2026-08-24 (Asia/Seoul)
- 평가 persona: 우주방사선·위성 시스템을 이해하는 우주항공 분야 교수
- 평가 방식: 발표 자료 수정 없는 읽기·브라우저 관찰·직접 테스트 재현
- 비교 기준: `2026-08-24_aerospace_professor_independent_audit.md`의 **64/100**
- 공정성 조건: 개인 발표 또는 2인 리허설 부재는 감점하지 않음

## 평가 스냅샷

| 대상 | SHA-256 |
|---|---|
| `demo/index.html` | `fdb10581815695f487590e8f2ddf6e83f307d13661e811a740c9c3ac383af369` |
| `demo/product.html` | `a73d6dfe33ad7b752de1993590045ef88ec08377ea8105bfa7b15093187f815e` |
| `demo/workspace.html` | `3d2042877cf780ee9e2bd8cc948350e72694f38b1fa95ab0fe9cb620c185baf6` |
| `spectra_7min_presentation_script_v2.md` | `2651fed7fb7c4f9b4d79522de72a82b0cb7f0389f04788935e20f71581ca49f9` |

평가 경계는 다음과 같이 고정했다.

- Slide 10의 1–3만 독립 확인된 저장 실행 기록으로 인정한다.
- Slide 10의 4–5는 동작 원리 예시이며 GCP 실행 증거 점수를 주지 않는다.
- Product와 Workspace의 값은 합성 결과이며 실제 방사선 assurance가 아니다.
- 실제 environment contract, 승인 exact-part ingest, 실제 시험 원문은 0건이다.
- 최종 engineering gate는 `NOT_EVALUATED`, assurance는 `HOLD`다.

## 결론

**최종 점수: 82/100 — 이전 64점 대비 +18점**

현재 스냅샷은 이전 평가에서 지적한 가장 위험한 문제, 즉 합성 결과와 저장 snapshot을 실제 과학 검증·실시간 실행으로 확대하던 발표 경계를 대부분 바로잡았다. 특히 Slide 10, Product, Workspace, v2 대본이 같은 `SYNTHETIC / NOT_EVALUATED / HOLD` 의미를 공유하고, 자체 발행 trust anchor까지 거부하는 issuance gate가 추가된 점은 신뢰성 점수를 실질적으로 높인다.

다만 82점은 실제 방사선 assurance 달성을 뜻하지 않는다. 실제 환경·exact-part 근거가 0건인 상태에서 받을 수 있는 점수는 **안전한 구조, 구현 무결성, 정직한 경계 표시**에 대한 점수다. 과학적 적용성과 고객 가치 검증은 여전히 열려 있다.

## 1. 항목별 점수

| 평가 항목 | 이전 | 최신 | 증감 | 최신 평가 근거 |
|---|---:|---:|---:|---|
| Multi-Agent 아키텍처 및 GCP 인프라 | 26/35 | **31/35** | **+5** | Mission·Parts·Assurance 책임이 화면과 대본에서 구체화됐다. Slide 10의 authoritative 기록 3건은 정확한 execution ID·stable state와 결속되고, Parts/Assurance 예시는 실행 링크를 제거해 증거 오인을 막는다. Product도 source-bound H05 snapshot, revision, IAM, parity, log count를 별도 검증한다. |
| 할루시네이션 방어 및 무결점 신뢰성 | 8/20 | **16/20** | **+8** | v2 대본은 실제 모델·실제 부품·실시간 GCP·보편적 False PASS 0 주장을 철회했다. Product와 Workspace는 malformed·optimistic·actual self-declaration 입력에서 fail-closed한다. issuance gate는 payload 내부 승인, exact-match plain JSON anchor, 공격자 자체 발행 anchor를 모두 `HOLD_NOT_ISSUED`로 거부한다. |
| 비즈니스 임팩트 및 문제 정의 | 18/30 | **21/30** | **+3** | Evidence Review Workspace가 추상적인 근거 체인을 coverage, blocking gap, owner role, next action으로 바꿔 실제 업무 형태를 보여준다. v2 대본도 ROI·구매자·KPI를 미검증으로 유지한다. 다만 실제 고객, workflow baseline, 구매 단위, 개선량은 아직 없다. |
| 팀 시너지 및 프레젠테이션 | 12/15 | **14/15** | **+2** | 13장 deck과 v2 대본의 번호·시간·버튼 동선이 일치한다. Slide 10은 저장 기록과 설계 예시를 화면 중앙에서 명확히 나누며 브라우저에서 안정적으로 동작했다. 감점은 발표 화면에 남은 과장된 Cover/COTS 시각 주장에 한정한다. |
| **합계** | **64/100** | **82/100** | **+18** | 제출 신뢰성은 크게 개선됐지만 실제 evidence path와 과학 적용성은 미완료다. |

## 2. 이전 대비 실제로 개선된 점

### 2.1 Slide 10의 증거 의미가 바로잡혔다

이전에는 로컬 snapshot 재생을 “실시간 GCP 시연”처럼 받아들일 위험이 있었고, Mission/Parts 실패 화면의 provenance도 불명확했다. 최신 화면은 다음을 명시한다.

- 1 정상 합성 실행: `ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34`
- 2 body hash 위조: `3f5d9221-7b7a-4023-be3c-f933fdbaf070`
- 3 endpoint override: `df49b5c1-3883-468e-bf1e-67e87ee0b6a7`
- 4–5: `동작 원리 예시 · 실행 기록 아님`, execution `해당 없음`
- 모든 버튼: snapshot 전환이며 새 Workflow를 시작하지 않음

브라우저에서 4–5 버튼을 직접 눌렀을 때 status와 telemetry가 모두 “실행 기록 아님”으로 바뀌고 execution link가 제거되는 것을 확인했다. 이는 단순 주석 추가가 아니라 실제 오인 경로를 닫은 개선이다.

### 2.2 대본의 과학·합성 경계가 크게 개선됐다

v2 대본은 다음을 발화 본문에 직접 포함한다.

- 13장 deck과 실제 화면명이 일치한다.
- 방사선 수치와 EX-100은 합성이다.
- 실제 environment run·승인 BOM·시험 원문은 0건이다.
- 차폐 table은 production deterministic Core의 고정 합성 결과다.
- ECC는 실제 하드웨어 성능이 아닌 제한된 합성 설계 가정이다.
- 1–3은 저장 기록, 4–5는 역할 설명 예시다.
- Product 가치와 KPI는 `UNSET / UNVALIDATED`다.

이로써 이전 대본의 AP-8/AE-8 실해석, RDM 4.1 VALID, 1,000회 Monte Carlo, WORM 원천 차단, 보편적 False PASS 0 같은 입증되지 않은 핵심 주장이 제거됐다.

### 2.3 Evidence Review Workspace가 제품 가설을 구체화했다

Workspace는 단순 결과 dashboard가 아니라 다음 검토 구조를 제공한다.

- Environment, Exact Part, TID, SEL, SEB, SEGR, Rights, Scientific Crosscheck의 8개 coverage
- blocking gap별 stable code, owner role, required evidence, next action
- malformed JSON, unknown status, duplicate gap, optimistic decision, actual self-declaration의 fail-closed 처리
- export 시 raw evidence, 로컬 경로, 개인정보, 실제 dose와 case identity를 제외하는 allowlist
- 입력이 없거나 손상되면 식별자와 수치를 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`

이는 “근거를 연결한다”는 설명을 사용자가 수행할 수 있는 review workflow로 전환한 실질적 진전이다.

### 2.4 issuance gate의 독립 신뢰 경계가 강화됐다

직접 재실행 결과:

| 직접 검사 | 결과 |
|---|---|
| Environment issuance gate | **25/25 PASS** |
| Evidence Review Workspace | **13/13 PASS** |
| Product binding | **17/17 PASS** |

특히 다음 공격이 모두 `HOLD_NOT_ISSUED`로 닫힌다.

- evidence payload 안에 스스로 `trusted_anchor`를 선언
- out-of-band 형식을 흉내 낸 exact-match plain JSON anchor
- 공격자가 anchor ID·approver·history reference를 직접 선택
- classification 변경 후 과거 anchor target 재사용
- raw manifest, storage generation, rights snapshot의 anchor binding 불일치

이 결과는 “JSON 안에 승인 필드를 써 넣으면 actual로 승격할 수 있는가?”라는 중요한 자체 발행 공격을 막는다. 단, 외부 authenticator가 아직 구성되지 않았으므로 실제 contract 발행 성공을 입증한 것은 아니다.

## 3. 여전히 막히는 치명적 결함과 감점 요소

### 3.1 실제 environment issuance path가 0건이다 — 가장 큰 blocker

현재 gate는 공격을 안전하게 거부하지만 실제로 인증된 environment contract를 발행한 사례는 없다. exact-match anchor도 authenticator가 없으므로 의도적으로 `HOLD_NOT_ISSUED`다. 따라서 지금 입증된 것은 **안전한 거부 동작**이지 실제 SPENVIS/환경 evidence의 과학적·권리적 사용 가능성이 아니다.

### 3.2 승인 exact-part ingest가 0건이다

EX-100은 합성 identity다. 실제 part number뿐 아니라 manufacturer, process, die revision, package, lot/date code, test bias·temperature·fluence·LET coverage와 원문 권리가 결속된 승인 packet이 없다. TID·SEU fixture는 SEL을 대신할 수 없고, 부품 종류에 따라 SEB·SEGR 적용성도 별도 판단해야 한다.

### 3.3 Workspace는 아직 actual evidence intake가 아니다

Workspace는 `SYNTHETIC / DEMO_ONLY`만 허용하고 issuance authentication이 `MISSING`인 fixture를 검토한다. 실제 authenticated issuance root, 실제 part packet, revocation·staleness·rights 변경을 받아 Product 판단까지 연결하는 end-to-end 경로는 없다. 현재 Workspace는 훌륭한 **review UX prototype**이지 운영 가능한 assurance workspace가 아니다.

### 3.4 로컬 테스트는 과학 정확도 검증이 아니다

25+13+17 테스트는 schema, binding, integrity, fail-closed behavior를 입증한다. 환경 모델의 물리 정확도, exact-part 시험 적용성, 임무 geometry, shielding transport, lot variation 또는 비행 적합성은 입증하지 않는다. H05 snapshot도 2026-08-20의 저장 기록이며 발표 당일 cloud current state가 아니다.

### 3.5 비즈니스 효과는 여전히 가설이다

Workspace가 제품 형태를 보여주지만 실제 엔지니어의 active review time, trace completeness, 보완 return rate, 구매 주체와 예산은 측정되지 않았다. 비즈니스 30점 만점에서 가장 큰 잔여 감점이다.

### 3.6 발표 화면에는 아직 과장된 시각 주장이 남아 있다

v2 대본은 안전하지만 화면 자체에는 다음이 남아 있다.

- Cover: “데이터 무결성으로 궤도 방사선 신뢰성을 입증한다.”
- COTS 비교: “필연적 채택”, “수억 원”, “98% 절감”, “수십 배”, “100% SEL 면역”, “극도로 안전”

발표자가 읽지 않겠다고 말해도 심사위원은 화면의 표를 증거 주장으로 본다. 이는 과학적 엄밀성과 시각적 메시지 사이의 마지막 큰 불일치다.

## 4. 지금 바로 할 수 있는 제품·증거·검증 작업 우선순위 3개

> 아래는 발표 문구 수정이 아니라 실제 제품·evidence path를 진전시키는 작업이다.

### 우선순위 1 — 인증된 실제 environment issuance 1건 닫기

out-of-band authenticator를 실제로 구성하고, provider job reference, 모델·버전·geometry, raw manifest v2, immutable storage generation, rights action grants, independent scientific crosscheck가 결속된 environment candidate 하나를 gate에 통과시킨다. 성공 결과와 함께 anchor revocation, stale rights, generation mismatch, classification drift 공격을 재실행한다.

완료 기준:

- 합성 control이 아닌 authenticated actual candidate 1건
- raw artifact·권리·storage·crosscheck의 exact binding
- 독립 reviewer가 재현 가능한 issuance receipt
- 공격 입력은 계속 `HOLD_NOT_ISSUED`

### 우선순위 2 — 승인 exact-part EvidencePacket 1건 구축

실제 BOM의 한 부품을 선택해 exact orderable identity, die/process/package/lot, 시험 조건, 원문 hash·storage generation·rights를 결속한다. TID, SEU, SEL과 부품 유형에 따른 SEB·SEGR applicability를 event별로 분리한다. 유사 부품군 보고서나 zero-event 표현을 exact-part immunity로 승격하지 않는다.

완료 기준:

- 승인 BOM identity와 시험 원문의 exact match
- event별 coverage와 test limit 기록
- rights와 provenance가 decision-eligible
- destructive SEE 공백은 명시적 blocking gap

### 우선순위 3 — Environment+Part의 actual-candidate end-to-end 결속 공격

우선순위 1과 2의 결과를 Workspace와 Product가 읽는 versioned contract로 연결한다. actual/synthetic 혼합, stale anchor, revoked rights, part lot drift, model version drift, body/result hash mismatch, duplicate evidence ID를 공격하고 어느 한 결속이 깨져도 식별자·수치가 숨겨지며 `NOT_EVALUATED / HOLD`가 유지되는지 독립 검증한다.

완료 기준:

- issuance receipt → Workspace coverage → Product decision의 trace ID 연결
- actual과 synthetic 상태를 섞어 optimistic decision을 만들 수 없음
- audit export가 민감 raw evidence를 유출하지 않음
- 독립 공격 manifest와 재현 가능한 machine-readable 결과

## 5. 최종 발표 반영 대기열

> 아래 항목은 제품·증거 작업과 분리한 제출 직전 발표 정리 항목이다.

### P0

1. Cover의 “궤도 방사선 신뢰성을 입증한다”를 실제 현재 상태에 맞는 문장으로 교체한다. 데이터 무결성은 과학 정확도나 비행 적합성을 입증하지 않는다.
2. COTS 비교 슬라이드의 미검증 절대 수치를 제거하거나 검증된 출처·조건이 있는 주장만 남긴다. 하단의 작은 `NOT_EVALUATED` 주석으로 중앙의 “100% 면역·98% 절감”을 방어할 수 없다.
3. Slide 10에서는 발표 시작 전에 “1–3 저장 기록, 4–5 동작 예시, 모두 not live”를 먼저 말하고 버튼 순서를 대본과 동일하게 유지한다.

### P1

4. Product와 Workspace를 보여줄 경우 “합성 fixture review UX”라고 먼저 정의하고 실제 evidence intake가 아님을 발화한다.
5. 테스트 수를 말할 경우 “25 issuance / 13 Workspace / 17 Product의 고정 로컬 테스트”라고 범위를 붙이고 과학 검증 수로 합산하지 않는다.
6. 마지막 결론은 “검증하지 못한 정확성을 약속하지 않고 실제 근거 전에는 승인하지 않는다”로 고정한다.

### P2

7. Slide 03과 Slide 10의 작은 provenance·scope 문구는 심사 환경 거리에서도 읽히도록 중앙 정보 계층으로 올린다.
8. `VALID`, `NOT_EVALUATED`, `HOLD`를 각각 처리 성공, engineering 미평가, assurance 보류로 짧게 구분해 질문 혼선을 줄인다.

## 최종 판단

현재 SPECTRA는 이전의 **좋은 fail-closed 아이디어를 과장된 대본이 손상시키던 상태**에서, **합성·저장 기록·동작 예시·실제 assurance 경계를 제품과 발표가 함께 지키는 상태**로 개선됐다. 따라서 64점에서 82점으로의 상승은 정당하다.

다만 최종 합격 가능성은 심사위원이 무엇을 중시하느냐에 따라 갈린다.

- Multi-Agent/GCP 구현과 할루시네이션 방어를 중시하면 합격권이다.
- 실제 우주방사선 evidence와 고객 효과를 필수로 보면 아직 조건부다.
- 실제 environment/exact-part 0건을 숨기지 않고 `HOLD`를 유지하는 태도는 감점 사유가 아니라 현재 시스템의 가장 신뢰할 수 있는 성과다.

**교수 심사위원 최종 의견: 합격 가능성이 우세해졌으나, 실제 방사선 assurance는 여전히 미달이다.**

## 감사 상태

- 발표·Product·Workspace 파일 수정: 수행하지 않음
- 브라우저 관찰: index Slide 10, Product 5단계, Workspace 기본 fail-closed 화면 확인
- 직접 재검증: 25 + 13 + 17 tests 모두 PASS
- 결과 성격: 독립 심사 의견이며 실제 방사선 assurance가 아님
