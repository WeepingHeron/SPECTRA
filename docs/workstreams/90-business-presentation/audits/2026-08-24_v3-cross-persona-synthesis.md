# SPECTRA v3 발표·Product Demo 교차 Audit 종합

- 평가 기준: Multi-Agent/GCP 35, 할루시네이션 방어·신뢰성 20, 비즈니스 임팩트·문제정의 30, 팀 시너지·프레젠테이션 15
- 평가 대상: `demo/index.html`, `demo/roadmap-lab.html`, `spectra_7min_presentation_script_v3.md`
- 공통 사실 경계: 실제 environment contract 0건, 승인 BOM exact-part evidence 0건, 실제 후보 판단 미사용, 최종 assurance HOLD
- 종합 판정: **CONDITIONAL GO**

## 점수

| 심사 페르소나 | Multi-Agent/GCP | 신뢰성 | 비즈니스 | 발표 | 총점 | 판정 |
|---|---:|---:|---:|---:|---:|---|
| 스타트업 대표 | 30 | 17 | 17 | 12 | **76** | CONDITIONAL GO |
| 기업 중간관리자 | 30 | 17 | 23 | 12 | **82** | CONDITIONAL GO |
| 우주항공 교수 | 31 | 16 | 22 | 12 | **81** | CONDITIONAL GO |
| 교육 프로그램 강사 | 32 | 19 | 23 | 13 | **87** | CONDITIONAL GO |
| **평균** | **30.75** | **17.25** | **21.25** | **12.25** | **81.5** | **CONDITIONAL GO** |

스타트업 대표의 낮은 비즈니스 점수는 기술 결함보다 구매자·예산 소유자·첫 pilot·문제 빈도 검증 부재에서 발생했다. 강사 점수는 공식 평가표에서 구현과 fail-closed 경계를 가장 높게 인정한 결과다.

## 네 Audit이 합의한 강점

1. 문제에서 제품까지의 흐름이 연결된다: 흩어진 Excel/PDF/BOM/시험 근거 → 검증 관문 → HOLD → 변경 시 선택적 재검사.
2. 결정론적 Core와 Mission·Parts·Assurance Agent의 책임 및 실패 경계가 명확하다.
3. 실제 TI 문서 후보에서도 AI 추출값을 승인값으로 쓰지 않고 적용성·SEE 공백 때문에 HOLD하는 장면이 가장 강한 시연이다.
4. ROI를 만들지 않고 pilot KPI로 active review time, trace completeness, return rate를 제시한 경계가 정직하다.

## P0 — 제출 전 닫아야 하는 공통 항목

### 1. 실제 TI 후보의 4번 관문 의미 수정

현재 UI는 PDF에서 주문형번과 제조사를 찾으면 4번 `대상 일치`를 PASS한다. 승인 BOM target이 0건이므로 이는 exact-match가 아니다. `후보 식별 완료`와 `승인 target exact-match`를 분리하고, 현재 exact-match는 `NOT_EVALUATED / HOLD`로 닫아야 한다.

### 2. 관문 수·상태 라벨·대본 일치

- UI의 “다섯 관문”을 실제 6개 관문과 통일한다.
- 합성 control을 선택해도 고정 노출되는 `ACTUAL REVIEW · HOLD`를 선택 상태에 따라 `SYNTHETIC CONTROL` / `ACTUAL CANDIDATE · NOT FOR DECISION`으로 분리한다.
- “실제 후보 3개”는 현장 live PDF 분석이 아니라 사전 생성한 실제 후보 receipt 검토임을 화면과 발화에서 명시한다.

### 3. 시연 동선 축소와 최종 브라우저 회귀

합성 3종 전체를 순회하지 않는다. 최종 동선은 `변조 control 1건 → 실제 TI receipt 1건 → ECC 재검사 1건`으로 고정한다. 발표 장치 해상도와 동일한 환경에서 새 탭, 후보 선택 후 재실행, Step 3, 초기화, fallback, overflow, console error를 확인한다.

### 4. 7분 실측 리허설

계산 시간 6:30은 실측이 아니다. 클릭 포함 목표는 6:40 이내로 두고, 실패 시 Product Demo는 TI 후보 HOLD 한 장면만 남긴다.

## P1 — 점수를 올리는 항목

1. 구매자·첫 pilot 가설을 한 문장으로 고정한다: 위성 개발사의 부품/RHA 검토 담당자를 사용자로, 기술 승인자와 품질·프로젝트 예산 책임자를 의사결정자로 검증한다. 확인된 고객처럼 말하지 않는다.
2. Slide 11에서 현재 구현, 합성 control, 향후 확장을 구분한다. 현재 구현은 로컬 문서 후보 추출 receipt 검토와 합성 변경 영향이다.
3. Product Demo가 로컬 검토 UI이며 화면 클릭이 새 GCP Workflow를 실행하지 않는다고 명확히 말한다.
4. 실제 TI 후보를 “exact part” 대신 “orderable part-number candidate”라고 부르고, TID 언급과 시험 적용성을 분리한다.

## 7분 발표에서 자르고 남길 것

- 자를 것: Slide 04 차폐 원리의 독립 설명과 Product Demo 합성 3종 전체 순회.
- 남길 것: 실제 TI 328쪽 PDF의 사전 추출 receipt에서 주문형번·제조사·TID 언급을 찾았지만 시험 조건·임무 적용성·파괴성 SEE가 없어 HOLD되는 장면.
- GCP: 정상 저장 기록과 공격 차단 한 건을 중심으로 설명하고, 1–3은 snapshot, 4–5는 실행 기록이 아닌 예시라는 경계를 유지한다.

## 권장 다음 작업 순서

1. Product UI exact-target gate와 상태 라벨 수정.
2. 변경 범위 직접 테스트와 발표 브라우저 E2E 1회.
3. v3 대본·조작 큐를 최종 UI와 다시 맞춤.
4. 7분 실측 리허설 및 정적 fallback 캡처 준비.
5. 마지막에만 발표자료의 Slide 11 현재/향후 구분과 buyer/pilot 한 문장을 반영.
