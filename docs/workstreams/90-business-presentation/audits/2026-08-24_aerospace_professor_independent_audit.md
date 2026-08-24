# SPECTRA 발표 독립 심사위원 Audit

- 평가일: 2026-08-24 (Asia/Seoul)
- 평가 persona: 우주방사선·위성 시스템을 이해하는 우주항공 분야 교수
- 평가 방식: 구현·수정 없는 읽기 전용 심사
- 평가 대상:
  - `/Users/taehoon/Desktop/IAA/SPECTRA/demo/index.html`
  - `/Users/taehoon/Downloads/spectra_7min_presentation_script.md`
- HTML SHA-256: `fd1238b5c1e9d262bc7d8b3eee02c104e201f60f8c4592863944c97ff7df09e9`
- 대본 SHA-256: `e40b165c052e5038de26379690845a0f1f83a9cdb58b3cff92b9654360ffbba6`
- 화면 확인: 인앱 브라우저 1280×720에서 전체 슬라이드, ECC 전환, GCP 시나리오 전환 관찰
- 상태 경계: `SYNTHETIC`, H05 verified snapshot, 실제 environment run 0건, 승인 exact-part BOM/test source 0건, 실제 assurance `HOLD`

> 공정성 조건: 개인 발표 또는 2인 팀 리허설 부재는 감점하지 않는다. `팀 시너지 및 프레젠테이션` 15점은 실제 인원수나 발표 분담이 아니라 화면 완성도, 메시지 전달력, 대본-화면 정합성, 시연 안정성만으로 평가한다.

## 총평

**최종 점수: 64/100 — 기술심사 기준 조건부 불합격 우세**

근거 중심의 문제 정의, 역할 분리형 GCP 구조, `HOLD` 중심 fail-closed 철학은 경쟁력이 있다. 실제 브라우저에서도 화면 잘림이나 콘솔 오류 없이 작동했고 ECC 및 GCP 시나리오 전환도 안정적이었다.

그러나 발표 대본은 합성 고정 table과 H05 실행 snapshot을 실제 환경 해석, 실제 부품 검증, 실시간 GCP 실행 및 물리 신뢰성 증명으로 확대하는 구간이 많다. 현재 가장 큰 위험은 시스템의 할루시네이션이 아니라 **발표 문구 자체의 검증 범위 초과**다.

## 1. 100점 만점 채점과 항목별 근거

| 평가 항목 | 점수 | 근거 |
|---|---:|---|
| Multi-Agent 아키텍처 및 GCP 인프라 | **26/35** | Mission·Parts·Assurance 역할 분리, Workflows, Cloud Run 3종, failure isolation, `HOLD` 종결은 설득력 있다. H05 합성 GCP snapshot도 실제 구현 증거다. 다만 로컬 화면은 snapshot 재생인데 대본은 “실시간 방어 시연”이라고 부른다. Mission/Parts 실패 화면의 execution provenance도 authoritative H05 snapshot과 정확히 연결되어야 한다. |
| 할루시네이션 방어 및 무결점 신뢰성 | **8/20** | 결정론적 Core, Schema, RFC 8785, SHA-256, 범위 밖 계산 거부는 좋은 설계다. 반면 AP-8/AE-8·SHIELDOSE-2 실제 해석, 19개 공격의 보편적 False PASS 0, 1,000회 Monte Carlo, WORM 원천 차단 등 제출물에서 입증되지 않은 주장이 대본에 들어 있다. |
| 비즈니스 임팩트 및 문제 정의 | **18/30** | 환경·BOM·시험성적서·완화 정책의 단절이라는 문제는 실제 업무와 맞닿아 있다. 그러나 80~90%, 40~50%, 86%, 3~6개월 통계의 적용 범위가 검증되지 않았고, 고객 업무시간·반려율·파일럿 KPI는 `UNSET / UNVALIDATED`다. |
| 팀 시너지 및 프레젠테이션 | **12/15** | 개인 발표 여부와 무관하게 시각적 완성도, 정보 계층, 인터랙션, 화면 안정성이 우수하다. 감점은 오직 HTML 11개 번호 슬라이드와 대본 01~09의 화면명·번호·동선 불일치, 일부 과밀 화면과 지나치게 작은 경계 주석 때문이다. |
| **합계** | **64/100** | 과학·증거 경계의 P0 수정 전에는 높은 구현 완성도가 발표 과장으로 상쇄된다. |

## 2. 발표 중 즉시 감점될 수 있는 주장

1. **“데이터 무결성으로 궤도 방사선 신뢰성을 입증한다.”**
   해시는 전달된 byte의 동일성을 확인할 뿐 과학적 정확성, provenance, 권리, exact-part 적용성 또는 비행 승인을 입증하지 않는다.

2. **“소형위성 조기 실패의 86%가 방사선 취약 전자부품 결함이다.”**
   HTML에도 없는 인과 수치이며 대본에 직접 출처·모집단·실패 정의가 없다.

3. **“Rad-Hard 부품은 제조사가 SEL 100% 면역을 보증한다.”**
   시험 LET 범위, 온도, 바이어스, fluence, lot identity 없이 면역을 절대화할 수 없다. `zero events within test limits`는 면역이 아니다.

4. **“AP-8/AE-8와 SHIELDOSE-2 기반 2 mm 결과가 6.0 krad다.”**
   현재 화면 값은 합성 고정 이산 table이다. 실제 SPENVIS environment contract와 과학 교차검산 전이므로 실제 모델 산출물처럼 말하면 안 된다.

5. **“TID 25 krad로 RDM 4.1을 만족해 VALID이고 Weibull 적분도 VALID다.”**
   화면은 TID와 SEU를 모두 `SYNTHETIC`으로 표시한다. 25/6과 25/12 중 어느 비율을 margin으로 부르는지도 불명확하다.

6. **“ECC로 실제 오류가 79% 감소했다.”**
   0.063072와 0.013072의 합성 fixture 비교는 가능하지만 실제 SEC-DED 성능, scrub 주기, MBU, memory size, duty cycle을 검증하지 않았다.

7. **“False PASS 0건이다.”**
   고정 manifest의 평가 가능 공격 범위로 한정해야 한다. 실제 GCP `ASR-D02`는 `NOT_EVALUATED`이며 우주방사선 전체에 대한 False PASS 0이 아니다.

8. **“4대 Fail-Closed를 실시간 GCP에서 시연한다.”**
   로컬 HTML은 H05 snapshot을 재생하며 GCP를 새로 호출하지 않는다. “검증된 합성 실행 기록 재생”이 정확하다.

9. **“0.013072에서 0.013073으로 1비트 변조됐다.”**
   10진 문자열 값의 변경은 곧 단일 bit flip을 의미하지 않는다. “결과 본문 값 변경”이라고 표현해야 한다.

10. **“1,000회 Monte Carlo에서 비트 오차 0으로 물리 신뢰성을 증명했다.”**
    제출물에서 확인되지 않는다. 구현 parity가 맞더라도 모델의 과학적 타당성이나 실제 환경 적용성을 증명하지 않는다.

## 3. 가장 설득력이 약한 슬라이드·대본 구간 5개

### 1) 슬라이드 01 / 대본 00:20~00:50

산업 통계가 화면에서는 “출처 후보·독립 검증 전”인데 대본에서는 NASA·ESA 확정 통계와 방사선 인과관계로 승격된다. 발표 초반 신뢰를 잃을 수 있다.

### 2) COTS 비교 슬라이드

Rad-Hard와 COTS의 가격, 납기, 성능, TID, SEL을 지나치게 단순한 양극으로 표현한다. 하단의 작은 `NOT_EVALUATED / HOLD` 주석이 중앙의 강한 절대 주장을 상쇄하지 못한다.

### 3) 환경·차폐 대본 01:35~01:55

합성 table을 AP-8/AE-8·SHIELDOSE-2 실제 해석처럼 설명한다. 실제 environment run 0건이라는 현재 상태와 가장 직접적으로 충돌한다.

### 4) 부품·ECC 대본 01:55~02:30

가상 EX-100과 합성 TID/SEU fixture를 “VALID로 확보”했다고 말한다. exact identity를 핵심 가치로 내세우는 발표에서 가상 부품을 실제 검증 부품처럼 말하면 치명적이다.

### 5) GCP 시연 및 Q8

H05 snapshot이 입증하는 것은 합성 입력의 실행, 데이터 전달 무결성, fail-closed 동작이다. 이를 “실시간”, “완벽히 실행”, “물리 신뢰성 증명”, “원천 차단”으로 확대하면 가장 좋은 구현 증거의 신뢰까지 손상된다.

## 4. 예상 질문 10개와 좋은 답변 기준

1. **6.0 krad는 실제 SPENVIS 결과인가?**
   “아니다. 현재는 합성 이산 table이며 실제 environment run은 0건이다. 원문·버전·geometry·권리·교차검산 전에는 assurance에 쓰지 않는다.”

2. **EX-100은 실제 주문 가능한 부품인가?**
   “아니다. 설명용 synthetic identity다. 승인 exact BOM/test source는 0건이며 실제 part/die/process/package/lot 조건이 일치하기 전에는 HOLD다.”

3. **RDM 2.0과 4.1은 각각 무엇인가?**
   dose, required dose, part limit의 분모·분자를 단위와 함께 정의해야 한다. 정의를 즉시 설명하지 못하면 4.1 주장을 철회해야 한다.

4. **TID가 낮아지면 SEL도 안전한가?**
   “아니다. TID는 누적 효과이고 SEL은 단일사건효과다. exact-part heavy-ion 근거 없이 서로를 대체하지 않는다.”

5. **SEB·SEGR coverage는 어디 있는가?**
   SRAM SEU 합성 비교만 구현했으며 SEL은 blocking gap, SEB/SEGR은 부품 유형별 적용성조차 별도 평가 대상이라고 답해야 한다.

6. **ECC 79%의 모델과 가정은 무엇인가?**
   두 합성 Core 값의 deterministic comparison임을 밝히고 실제 SEC-DED, scrubbing, MBU, memory organization 검증은 하지 않았다고 제한해야 한다.

7. **왜 Multi-Agent인가?**
   생성형 AI 세 개가 방사선 숫자를 만드는 것이 아니라 Mission·Parts·Assurance의 책임·권한·failure domain을 Cloud Run 서비스로 분리한 구조라고 설명해야 한다.

8. **해시가 맞으면 성적서가 과학적으로 맞는가?**
   “아니다. 승인된 preimage와 byte가 같다는 뜻뿐이다. 출처·권리·exact identity·시험 조건·적용성은 별도 gate다.”

9. **False PASS 0의 분모는 무엇인가?**
   manifest version, 평가 공격 수, control 수, `NOT_EVALUATED` 제외 항목을 구분해야 한다. 보편적 0으로 답하면 안 된다.

10. **고객 비용이나 검토시간을 실제로 얼마나 줄였는가?**
    “아직 측정하지 않았다”고 먼저 답하고 case당 active review time, trace completeness, 보완 return rate의 파일럿 측정 계획을 제시해야 한다.

## 5. 제출 전 수정 우선순위

### P0 — 반드시 수정

- 대본의 AP-8/AE-8·SHIELDOSE-2 실제 계산, TID/SEU `VALID`, RDM 4.1, 1,000회 Monte Carlo, WORM 원천 차단 주장을 삭제하거나 합성 범위로 교정한다.
- “실시간 GCP 시연”을 “H05 검증 합성 snapshot 재생”으로 바꾼다.
- `False PASS 0`의 manifest, 분모, control, `NOT_EVALUATED` 제외 범위를 발화 안에서 제한한다.
- 산업 통계와 COTS 절대 수치를 검증하거나 주 화면에서 제거한다. 작은 하단 주석만으로는 부족하다.
- HTML 11개 번호 슬라이드와 대본 01~09의 번호·화면명·발화·버튼 동선을 일치시킨다.
- Mission/Parts 실패 execution이 authoritative H05 기록으로 증명되지 않으면 “로컬 fault-injection 시나리오”로 표시한다.

### P1 — 점수 상승에 직접 영향

- 첫 문장을 “신뢰성을 입증한다”에서 “실제 근거가 입증되기 전에는 승인하지 않는다”로 변경한다.
- Environment Agent, Parts Evidence Agent, Independent Assurance Agent, deterministic Core의 책임 경계를 한 화면에서 보여준다.
- exact identity에 part number 외 die/process/package/lot/test bias/temperature/LET coverage를 포함한다.
- 파일럿 대상 고객, workflow 단계, baseline과 세 KPI의 측정 방법을 구체화한다.
- H05 snapshot이 증명하는 GCP 실행 무결성과 증명하지 않는 과학적 assurance를 나란히 제시한다.

### P2 — 완성도 개선

- 1280×720에서 슬라이드 03·10의 작은 출처와 경계 문구를 본문 배지로 올린다.
- NASA REAG·ESCIES를 “정적 PDF 저장소에 불과하다”고 단정하지 않고 SPECTRA가 보완하는 조건 추적·변경 영향 기능을 비교한다.
- 발표 전 `SYNTHETIC`, `H05 SNAPSHOT`, `HOLD`, `실제 근거 0건` 용어를 일관되게 말하도록 대본을 정리한다.

## 6. 최종 합격 가능성 판단

현재 상태는 **항공우주 기술심사에서 불합격 가능성이 더 높다.** 시각적 완성도와 GCP 구현은 강하지만, AP-8/AE-8, exact part, RDM, SEL coverage, Monte Carlo 검증을 질문받으면 대본의 범위 초과가 빠르게 드러난다.

다만 P0를 수정하면 합격 경쟁력이 크게 올라간다. 가장 안전하고 강한 결론은 다음과 같다.

> SPECTRA는 아직 검증하지 못한 정확성을 약속하는 시스템이 아니라, 실제 환경·정확한 부품 근거·데이터 무결성이 확인되기 전에는 승인하지 않는 시스템이다.

이 문장을 발표 전체의 경계로 유지하면 현재의 실제 environment/part evidence 0건과 최종 `HOLD`가 실패가 아니라 시스템의 기술적 정직성과 fail-closed 설계 증거로 작동한다.

## 감사 상태

- 파일 수정·구현 평가: 수행하지 않음
- 브라우저 렌더링: 관찰 완료
- 개인 발표·2인 리허설 부재 감점: **없음**
- 판정 상태: **독립 심사 의견 / 실제 방사선 assurance 아님**
