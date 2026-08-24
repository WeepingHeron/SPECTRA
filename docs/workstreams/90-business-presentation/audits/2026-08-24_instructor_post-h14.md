# SPECTRA 교육 프로그램 강사 독립 재평가 — Post-H14

- 평가일: 2026-08-24
- 심사 persona: 교육 프로그램 강사
- 평가 방식: 발표·Product·Workspace·v2 대본·이전 감사 전수 확인, 현재 저장소 증거 교차 확인, 지정 직접 테스트 독립 재실행
- 공정성 원칙: 1인 수행과 2인 팀이 아님은 감점하지 않으며, 실제 리허설 미수행도 감점 요소로 사용하지 않는다. 팀 시너지는 책임 분리·협업 계약·독립 감사 구조로 평가한다.
- 브라우저 관찰: 이번 감사에서 신규 브라우저 렌더링은 수행하지 않았다. 정적 HTML/JavaScript와 Control Tower의 기존 localhost 관찰 기록을 구분해 사용했다.

## 검토 대상

- 프로젝트: `/Users/taehoon/Desktop/IAA/SPECTRA`
- 발표 화면: `/Users/taehoon/Desktop/IAA/SPECTRA/demo/index.html`
- Product: `/Users/taehoon/Desktop/IAA/SPECTRA/demo/product.html`
- Evidence Review Workspace: `/Users/taehoon/Desktop/IAA/SPECTRA/demo/workspace.html`
- 7분 대본: `/Users/taehoon/Downloads/spectra_7min_presentation_script_v2.md`
- 이전 감사: `/Users/taehoon/Desktop/IAA/SPECTRA/docs/workstreams/90-business-presentation/audits/2026-08-24-instructor-independent-presentation-audit.md`

## 증거 경계

- Slide 10의 버튼 1–3만 독립 확인된 저장 GCP 실행 기록으로 인정한다.
- 버튼 4–5는 `동작 원리 예시 · 실행 기록 아님`이며 GCP 실행 증거 점수를 부여하지 않는다.
- Product와 Workspace의 수치·case·identity는 합성 결과이며 실제 radiation assurance가 아니다.
- 실제 environment contract 발행은 0건이다.
- 승인 exact-part ingest와 decision-usable part packet은 0건이다.
- 최종 assurance는 `HOLD`다.
- Workspace가 구조를 정상 수용해도 `VALID / NOT_EVALUATED / HOLD`이며 실제 근거가 되지 않는다.

## 독립 재실행 결과

다음 명령을 현재 Desktop working-tree snapshot에서 직접 실행했다.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.environment.test_issuance_gate
→ Ran 25 tests · OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_evidence_review_workspace
→ Ran 13 tests · OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_product_data_binding
→ Ran 17 tests · OK
```

환경 gate의 자체 발행 exact-match anchor 공격은 실제 신뢰 루트로 승격되지 않고 `ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED / HOLD_NOT_ISSUED`로 닫힌다. 이는 fail-closed 구현 증거이지 실제 authenticator나 environment contract 발행 증거는 아니다.

## 최종 점수

**85/100점 — 안정적 합격권, 실제 Evidence Path 전에는 최종 제품 보증 불가**

| 평가 항목 | 배점 | 이전 | 현재 | 증감 | 현재 근거 |
|---|---:|---:|---:|---:|---|
| Multi-Agent 아키텍처 및 GCP 인프라 | 35 | 29 | **31** | **+2** | Mission·Parts·Assurance의 증거 책임이 Slide 10, Product, Workspace 전반에서 더 명확해졌다. Workflows의 순서·차단, private Cloud Run 3종, Storage·IAM·Logging 경계와 저장 execution ID 3건이 구체적이다. 1–3 저장 기록과 4–5 설계 예시도 UI·코드·대본에서 분리됐다. 다만 Parts/Assurance 개별 차단의 authoritative execution은 아직 없고 실제 evidence traffic도 0건이다. |
| 할루시네이션 방어 및 무결점 신뢰성 | 20 | 12 | **18** | **+6** | v2 대본이 합성 수치, 실제 근거 0건, snapshot-not-live, `HOLD`를 일관되게 말한다. environment 자체 발행 공격, Workspace의 malformed/optimistic/unauthenticated input, Product binding 공격이 모두 fail-closed 테스트를 통과했다. 다만 실제 authenticator·actual contract·exact-part validator가 없으므로 현재 검증은 합성·계약·표시 경계에 한정된다. |
| 비즈니스 임팩트 및 문제 정의 | 30 | 18 | **22** | **+4** | 과장된 실패율·원인 통계를 제거하고, Evidence Review Workspace가 coverage 8항목, blocking gap, owner role, next action, redacted audit export로 문제를 실제 업무 화면으로 바꿨다. 그러나 사용자 인터뷰·구매자·가격·active review time·trace completeness·return rate는 여전히 `UNSET / UNVALIDATED`다. 발표의 유일한 대표 비용 수치 `$1k–$5k/hour`도 현재 연결된 NASA COTS Phase II 보고서에서 확인되지 않아 출처 결함이 남는다. |
| 팀 시너지 및 프레젠테이션 | 15 | 11 | **14** | **+3** | 13장 deck과 v2 대본의 화면 순서·시간 계약이 일치하고, Q&A가 직접 답변→검증 범위→안전장치→한계 구조로 정리됐다. 역할 분리와 독립 재현이 1인 프로젝트에서도 협업 가능한 경계로 표현된다. 리허설 미측정은 감점하지 않았다. 다만 Cover의 “신뢰성을 입증한다”는 시각 문구는 전체 `HOLD` 경계보다 강하다. |
| **합계** | **100** | **70** | **85** | **+15** | **이전의 발표 정합성·과장 결함은 대부분 닫혔고, 남은 감점은 실제 evidence·business validation 부재에 집중된다.** |

## 이전 대비 실제 개선

### 1. 대본–화면 구조 불일치 해소

이전 대본은 11장 기준이어서 13장 HTML과 두 장씩 어긋났다. v2는 Cover+01~11+Closing 13장을 정확히 열거하고 405초 원고+15초 전환 여유를 계산한다. 각 구간의 화면 이름도 최신 deck과 일치한다.

### 2. 합성 결과의 실제 검증 확대 표현 제거

이전 대본의 실제 AP-8/AE-8 계산, 실제 TID·SEU `VALID`, ECC 79% 실제 효과, 1,000회 Monte Carlo, WORM 완전 차단, 실시간 Workflow 표현이 v2에서 제거됐다. v2는 수치를 `production deterministic Core의 고정 합성 table`, ECC를 `제한된 합성 설계 가정`, GCP를 `검증된 고정 snapshot`으로 제한한다.

### 3. GCP provenance와 시연 권한 분리

Slide 10은 다음을 화면과 코드에서 동시에 구분한다.

- 1 정상 합성 실행: 저장 execution `ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34`
- 2 입력 body hash 위조: 저장 execution `3f5d9221-7b7a-4023-be3c-f933fdbaf070`
- 3 endpoint override 차단: 저장 execution `df49b5c1-3883-468e-bf1e-67e87ee0b6a7`
- 4 Parts 차단: 동작 원리 예시, 실행 기록 아님
- 5 Assurance 차단: 동작 원리 예시, 실행 기록 아님

정적 deck이 새 Workflow를 호출하지 않는다는 문구도 명시됐다. 따라서 4–5에는 실행 증거 점수를 주지 않았다.

### 4. Product가 발표용 계산 화면에서 판단 workflow로 확장

Product는 Scenario→Analysis→Assurance→GCP snapshot→Result Integrity의 5단계로 정리됐다. 상단에 `합성 데모 · 실제 보증 아님 / 현재 결론 HOLD`를 고정하고, 실제 환경 run·승인 BOM·시험 원문 0건을 표시한다. 결과 변조 시 숫자와 식별자를 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는 동작이 17개 binding 테스트로 재현됐다.

### 5. Evidence Review Workspace 추가

Workspace는 단순 dashboard보다 실제 검토 업무에 가깝다.

- Environment, Exact Part, TID, SEL, SEB, SEGR, Rights, Scientific Crosscheck 8개 coverage를 분리한다.
- blocking gap에 담당 역할, 필요한 evidence, 다음 action code를 연결한다.
- `ACTUAL` 자기 선언, 인증되지 않은 issuance root, optimistic decision, malformed 구조를 거부한다.
- export에서 raw evidence, 로컬 경로, 개인정보, dose, case identity를 제외한다.
- 입력 구조가 정상이어도 실제 contract 0건이면 `NOT_EVALUATED / HOLD`를 유지한다.

13개 직접 테스트 통과는 이 계약 경계의 동작 증거다. 실제 evidence ingestion 또는 과학 보증 증거로 확대하지 않는다.

## 치명적 결함과 감점 요소

### Critical 1 — 실제 Evidence Path가 한 건도 닫히지 않음

실제 environment contract와 승인 exact-part ingest가 모두 0건이다. 따라서 현재 제품은 “합성 입력을 안전하게 거부·보류하는 시스템”까지는 증명하지만, 실제 mission evidence를 받아 최종 review packet으로 연결하는 end-to-end 제품 가치는 아직 증명하지 못한다.

### Critical 2 — 환경 trust root가 구현되지 않음

plain JSON exact-match anchor와 자체 생성 anchor를 거부하는 것은 옳다. 그러나 KMS/public-key/immutable trust-store 기반 authenticator가 없기 때문에 모든 `ACTUAL_REVIEW`가 `HOLD_NOT_ISSUED`로 끝난다. 안전하지만 실제 발행 경로는 없다.

### Critical 3 — exact-part v2 contract와 승인 BOM input 부재

승인 BOM, approval target/history, raw manifest, action별 rights snapshot, exact test article identity, event별 TID·SEU·SEL·SEB·SEGR applicability가 없다. Workstream 40의 공격 15축은 구현 요구 명세이며 현재 v2 validator 실제 실행은 0건이다.

### High 1 — Business validation 0

실제 사용자 workflow, 반복 조사 시간, 반려율, trace completeness, 구매자와 가격이 검증되지 않았다. Workspace는 제품 가설의 품질을 높였지만 사업 효과를 측정한 결과는 아니다.

### High 2 — `$1k–$5k/hour`의 출처 연결이 확인되지 않음

deck과 v2 대본은 이 값을 NASA/TM-20220018183 COTS Phase II에 연결한다. 그러나 공식 NASA NTRS 요약은 이 보고서가 COTS 비용을 다루지 않는다고 설명하며, 보고서 검색에서도 해당 beam-time 범위를 확인하지 못했다. 별도 1차 출처를 연결하거나 발표에서 제거해야 한다.

- NASA COTS Phase II: <https://ntrs.nasa.gov/citations/20220018183>

### Medium 1 — Cover의 “입증한다”가 실제 상태보다 강함

Cover는 “데이터 무결성으로 궤도 방사선 신뢰성을 입증한다”고 표시한다. v2 첫 문장이 즉시 합성 경계를 설명하지만, 실제 assurance `HOLD`와 contract 0건을 고려하면 “판단 근거를 검증한다”가 더 정확하다.

### Medium 2 — Parts/Assurance 예시와 실행 기록이 같은 시연 영역에 있음

라벨은 충분히 개선됐지만 5개 버튼이 한 그룹에 있어 빠른 시연에서 4–5가 실제 GCP 실행으로 오해될 가능성은 남는다. 현재 대본은 이 경계를 두 번 말하므로 발표자가 그대로 지키면 감점 위험은 낮다.

## 지금 바로 할 수 있는 제품·증거·검증 작업 우선순위 3개

발표 문구 수정이 아니라 실제 제품과 증거 경로를 전진시키는 작업만 제시한다.

### P1. 환경 issuance authenticator와 trust-root 경로 구현·공격 검증

목표는 plain JSON anchor가 아니라 KMS 서명, 공개키 검증 또는 immutable trust-store에 결속된 out-of-band issuance root를 구현하는 것이다.

- review payload와 trust root를 별도 channel로 유지한다.
- signer/key identity, key version, approval scope, timestamp, revocation 상태를 contract에 결속한다.
- 자체 발행 root, stale key, wrong key version, history rewrite, payload/hash 동시 위조를 직접 공격한다.
- 성공 기준은 실제 인증 경로를 통과한 candidate 1건과 모든 공격의 `HOLD_NOT_ISSUED`; 이것만으로 과학 정확성을 주장하지 않는다.

### P2. `PART_TEST_EVIDENCE v2` validator와 승인 BOM intake vertical slice 구현

현재 Workstream 40의 문서 명세를 실행 가능한 schema·semantic gate·fixture로 전환한다.

- exact manufacturer/PN/package/grade/process/die/lot/date-code policy를 lossless하게 표현한다.
- BOM approval target/history, raw artifact generation/hash, action별 rights, source locator를 결속한다.
- TID·SEU·SEL·SEB·SEGR을 독립 event record로 유지하고 substitution을 금지한다.
- 문서에 정의된 15개 공격을 실제 fixture와 stable code로 구현한다.
- 승인 BOM·rights 입력이 아직 없으면 synthetic control만 통과시키고 decision-use는 계속 `false / HOLD`로 둔다.

### P3. Workspace를 actual-contract-ready intake와 비민감 pilot 측정기로 확장

Workspace는 현재 의도적으로 `SYNTHETIC / DEMO_ONLY`만 수용한다. 다음 단계는 실제 contract를 바로 승인하는 것이 아니라 인증 상태를 보존하는 별도 input version을 추가하는 것이다.

- authenticated environment candidate와 approved-BOM packet을 별도 version dispatch로 수용한다.
- `AUTHENTICATED`, `RIGHTS_ACTIVE`, `SCIENTIFICALLY_REVIEWED`를 서로 다른 상태로 유지한다.
- raw artifact는 브라우저에 노출하지 않고 redacted receipt만 표시·export한다.
- 한 개의 비민감 review case로 active review time, trace completeness, 보완 return event를 측정한다.
- malformed/optimistic/identity substitution/rights downgrade 공격과 browser rendering을 함께 검증한다.

## 최종 발표 반영 대기열

다음은 제품 작업과 분리한 제출 직전 발표 반영 항목이다. 이번 감사에서는 발표 파일을 수정하지 않았다.

1. **Cover 문구 경계 정렬**
   - “궤도 방사선 신뢰성을 입증한다”를 실제 상태에 맞는 “방사선 판단 근거를 검증한다” 수준으로 낮춘다.

2. **beam-time 비용 출처 해결**
   - `$1k–$5k/hour`를 직접 뒷받침하는 1차 출처를 연결하거나, 찾지 못하면 Slide 01·03과 대본에서 숫자를 제거한다.

3. **Slide 10 권한 문장 그대로 유지**
   - 시작 전에 “1–3 저장 기록, 4–5 동작 원리 예시, 어느 버튼도 새 Workflow를 실행하지 않음”을 반드시 말한다.
   - 4–5를 execution ID 또는 GCP 실제 차단 증거와 연결하지 않는다.

4. **25/13/17 테스트의 의미 제한**
   - issuance 25, Workspace 13, Product 17 tests는 계약·fail-closed·표시 binding 검증이라고만 말한다.
   - 과학 정확성, 실제 부품 suitability, radiation assurance 검증으로 확대하지 않는다.

5. **Workspace의 제품 가치 한 문장 추가 여부 결정**
   - 제한 시간에 넣는다면 “무엇이 빠졌는지뿐 아니라 담당 역할과 다음 행동까지 연결한다” 한 문장으로만 소개한다.
   - 별도 live demo를 추가해 Slide 10의 80초를 잠식하지 않는다.

6. **최종 한계 문장 유지**
   - 실제 environment run·승인 BOM·시험 원문 0건, 사용자 가치 `UNVALIDATED`, 최종 `HOLD`를 Closing 또는 Q&A에서 유지한다.

## 최종 판단

SPECTRA는 이전 감사의 **70점 조건부 합격권**에서 **85점 안정적 합격권**으로 개선됐다. 점수 상승은 새로운 기능 수보다 다음 세 가지에서 발생했다.

1. 합성·실제·snapshot·설계 예시를 정확히 구분했다.
2. Multi-Agent 책임을 화면·대본·Product·Workspace에서 일관되게 연결했다.
3. fail-closed 주장을 25/13/17 직접 테스트로 재현했다.

현재 가장 큰 한계는 발표 완성도가 아니라 실제 Evidence Path다. 실제 trust root, 승인 BOM, exact-part v2 packet, rights와 과학 교차검산이 없으므로 radiation assurance는 계속 `HOLD`가 맞다. 이 경계를 유지하는 한 교육 프로그램 제출물로는 강한 합격권이다. 상위권 또는 실제 제품 신뢰성 평가로 올라가려면 우선순위 P1–P3 중 최소 한 경로를 실제 non-synthetic evidence와 독립 검증으로 닫아야 한다.

## 감사 결론

- 판정: **PASS — evidence-bound prototype**
- 총점: **85/100**
- 이전 대비: **+15점**
- 실제 radiation assurance: **HOLD**
- actual environment contract: **0건**
- approved exact-part ingest: **0건**
- Slide 10 GCP execution credit: **버튼 1–3만 인정**
