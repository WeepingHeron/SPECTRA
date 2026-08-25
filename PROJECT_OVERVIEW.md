# SPECTRA 프로젝트 소개

## 1. 한 문장 정의

**SPECTRA(Space Parts Evidence, Component Traceability, Radiation Assurance)는 위성의 임무 조건과 전자부품 목록(BOM)을 우주 방사선 환경 모델 및 정확한 부품 시험 증거와 대조하여, TID·SEU 분석을 재현하고 근거 공백에서는 판단을 보류하는 Multi-Agent 기반 방사선 증거 검증 플랫폼이다.**

> SPECTRA는 부품의 비행 적합성을 AI가 추측하거나 인증하는 시스템이 아니다. 어떤 계산과 시험 증거로 현재 판단에 도달했으며 무엇이 부족한지를 추적하고 감사한다.

현재 제품 정의와 장기 과학 MVP는 유지하되, 2026-08-25 제출은 별도 **Competition Submission Release**로 관리한다. 제출 Release의 진행 상태와 완료 Gate는 각각 [`ROADMAP.md`](ROADMAP.md), [`CHECKLIST.md`](CHECKLIST.md)에만 둔다.

Competition Submission Release의 실제 GCP 보완 검증은 locked Workflow `000006-d2a`에서 정상 control 1건과 공격 4건으로 수행했다. control의 deterministic Core parity가 일치했고 네 공격은 모두 fail-closed했지만, 이는 합성 데이터의 제한된 공격 세트일 뿐 침투시험·exact-part 적합성·방사선 보증 완료가 아니다.

## 2. 해결하려는 문제 — 계산보다 어려운 것은 근거를 연결하는 일

**소형위성 팀은 성능·가격·조달성 때문에 COTS 전자부품을 사용하지만, 임무별 방사선 환경과 정확한 부품 identity·시험 조건·완화 설계·승인 정책은 서로 다른 도구와 문서에 흩어져 있다. 그 결과 “이 시험 결과가 이 부품과 이 임무에 실제로 적용되는가”를 일관되고 재현 가능하게 검증하기 어렵다.**

문제는 방사선 계산식 하나가 없는 것이 아니다. 환경 모델 출력, BOM spreadsheet, 시험 PDF와 제조사·공정·로트 변경 정보가 서로 다른 형식으로 분리되어 있어, 같은 임무와 정확한 부품을 가리키는지 재현하고 감사하기 어렵다는 것이다.

### 확인된 산업·기술 근거

| 근거 | SPECTRA 문제 정의에 주는 의미 |
|---|---|
| NASA의 2024 Small Spacecraft 기술 보고서는 CubeSat이 COTS 부품을 흔히 사용하고, COTS가 일반적으로 MIL/QML 부품보다 방사선·신뢰성 검증이 덜 엄격하다고 설명한다. | 낮은 비용과 빠른 조달의 이점이 자동으로 임무 적합성 증거가 되지 않는다. |
| NASA RHA 지침은 부품의 application, 궤도·trajectory, 임무 기간과 spacecraft 내 위치가 검증 parameter space를 결정한다고 명시한다. | 같은 부품 시험자료도 임무와 적용 조건이 달라지면 그대로 재사용할 수 없다. |
| NASA NESC의 COTS Phase II 보고서는 TID·SEL 성능이 제조 공정과 lot에 민감하고, 작은 공정 변경도 방사선 성능을 바꿀 수 있다고 지적한다. | exact part number만으로는 부족하며 process·die·lot와 변경 이력을 함께 추적해야 한다. |
| 같은 NASA 보고서는 heavy-ion beam time을 대략 **시간당 1,000~5,000달러**로 제시하고 시설 확보도 점점 어렵다고 설명한다. | 모든 부품을 무차별 재시험하기보다 증거 공백과 위험을 먼저 좁혀 제한된 시험 예산의 우선순위를 정해야 한다. |
| GAO는 전자부품 공급망에서 단종·위조·추적성 위험과 구성관리 필요성을 다룬다. | 공급·공정·로트 변경이 기존 근거에 미치는 영향을 다시 검토해야 한다. |
| ESA Product Assurance는 부품·공정 적합성, 구성관리, 검사·감사와 시정조치의 통제를 요구한다. | 품질·미션 보증 담당자는 계산값뿐 아니라 근거와 변경 이력을 감사 가능한 형태로 유지해야 한다. |

출처: [NASA Small Spacecraft Technology 2024](https://ntrs.nasa.gov/citations/20250000142), [NASA Avionics RHA Guidelines](https://ntrs.nasa.gov/citations/20210018053), [NASA COTS Parts Phase II](https://ntrs.nasa.gov/citations/20220018183), [GAO-11-404](https://www.gao.gov/products/gao-11-404), [ESA Product Assurance](https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Product_Assurance)

### 실제 업무에서 끊기는 지점

1. 환경 모델은 선량·입자 결과를 만들지만 특정 BOM의 시험 증거 적용성을 판정하지 않는다.
2. 시험 보고서는 존재해도 정확한 부품번호·공정·die·lot·온도·bias·선량률이 현재 설계와 다를 수 있다.
3. 차폐와 ECC 같은 계산 가정은 어떤 결과에 적용됐는지 추적되지 않으면 임의의 완화율처럼 오용되기 쉽다.
4. 부품·궤도·차폐·정책이 바뀌어도 이전 계산과 승인 중 무엇이 무효가 됐는지 자동으로 드러나지 않는다.
5. 근거가 부족한 상태가 명시적 `HOLD`가 아니라 낙관적인 PASS 또는 불필요한 전면 재시험으로 이어질 수 있다.

마지막 항목은 SPECTRA가 검증할 **실무 가설**이며, 실제 발생 빈도와 절감 효과는 사용자 인터뷰와 pilot으로 측정해야 한다.

따라서 SPECTRA의 역할은 기존 환경 모델이나 방사선 시험을 대체하는 것이 아니다. **환경 계산 → 정확한 부품 증거 적용성 → 제한된 설계 가정 → 변경 영향 → 독립 감사**를 하나의 Evidence Chain으로 연결해, 현재 지원 가능한 주장과 아직 부족한 근거를 구분하는 것이다.

## 3. 주요 사용자와 비즈니스 가치

| 사용자 | 해결하려는 업무 | 제공 가치 |
|---|---|---|
| 소형위성 제작사·대학 CubeSat 팀 | 초기 부품 선정과 시험 계획 | 위험 부품과 증거 공백의 조기 발견 |
| 위성 서브시스템 공급사 | 고객 임무별 부품 증거 패키지 작성 | 반복 조사·문서화 비용 절감 |
| 부품 유통사·시험기관 | 추가 시험 수요와 대체 부품 식별 | 시험·컨설팅 기회 구체화 |
| 품질·미션 보증 담당자 | 설계 변경과 승인 근거 감사 | 재현 가능한 계산·출처·승인 이력 확보 |

현재 입증된 제품 가치는 빠진 근거와 재검토 지점을 승인 전에 찾고, `HOLD` 이유와 다음 행동을 반환하는 동작까지다. 임무·BOM 단위 분석, 조직용 구독, 전용 배포와 시험기관 연계는 확장 가설이며, 구매자·예산 책임자·도입 방식·비용 절감·지불 의향은 실제 인터뷰 전까지 **UNVALIDATED**다. 실제 운영 계약이 없으므로 UI에 임의의 owner·reviewer·승인 상태를 만들지 않는다.

## 4. 프로젝트 범위

제품의 과학적 범위와 대회 시연의 아키텍처 범위를 분리한다.

- **Core Product Scope:** 고정된 LEO 임무 1개와 exact-part 1개를 대상으로 환경 모델, 부품 시험 증거, 결정론적 TID·SEU 계산, 제한된 차폐·ECC 가정과 fail-closed 판정을 연결한다. 단일 완료 기준은 [`docs/MVP.md`](docs/MVP.md)를 따른다.
- **Competition Demo Release:** 위 Core를 역할이 분리된 Multi-Agent 흐름으로 실행하고 실제 GCP 저장·실행·오케스트레이션·감사 로그 증거를 남긴다. 이는 채점 필수 범위지만 실제 방사선 보증 완료를 뜻하지 않는다.
- **Experimental Archive:** WATCHDOG·TMR·SEL 보호의 합성 runtime 계산은 과거 검증 이력을 보존하되 현재 제품 판단·주 발표·핵심 신뢰성 지표에서 제외한다.

### 초기 범위

- LEO 대표 임무 시나리오
- COTS catalog 검토 대상 `23LC1024-I/SN` 1종과 exact-part evidence가 확보된 뒤의 확장 경로
- 차폐·임무 기간에 따른 TID 계산과 마진 비교
- 시험 단면적이 존재하는 부품의 SEU 발생률 추정
- ECC 미적용·적용의 잔여 SEU 비교와 가정 provenance
- TID, SEU, 파괴성 SEE 증거의 독립 감사
- 설계 변경 전·후 비교 보고서

### 초기 범위에서 제외

- 부품 또는 위성의 비행 적합성 인증
- 실제 방사선 조사 시험의 대체
- 모든 궤도·행성·부품에 대한 일반화
- 근거가 없는 최신 상용부품의 성능 추정
- 완전한 3D 방사선 수송·차폐 해석
- SEL·SEB·SEGR을 SEU 수치만으로 대체 판정
- 실제 WATCHDOG·TMR·SEL 보호장치 또는 탑재 소프트웨어의 구현·제어
- 합성 runtime 완화 수치를 현재 임무의 채택 설계나 입증된 효과로 주장

## 5. 입력과 산출물

### 입력

- 임무: 궤도, 고도, 경사각, 시작 시점, 기간
- 설계: 차폐 재료·등가 두께, 적용 기준, TID 설계 계수
- BOM: 부품번호, 제조사, 기능, 공정·다이·로트 정보
- 제한된 설계 가정: 차폐 조건, ECC 적용 여부와 근거·분류
- 판정 기준: TID 설계 계수, 허용 잔여 SEU, 파괴성 SEE 증거 요구
- 증거: 환경 모델 출력, 시험 보고서, 데이터시트, 내부 검토 문서

### 핵심 산출물

1. **Mission Radiation Profile**
   모델·버전·입력·불확실성을 포함한 환경 및 차폐 뒤 선량
2. **Evidence Coverage Matrix**
   부품별 TID·SEU·파괴성 SEE 증거와 적용 조건
3. **Radiation Analysis Comparison**
   차폐·ECC 가정 전후의 TID·잔여 SEU와 적용 근거 비교
4. **Change Impact Report**
   부품·궤도·차폐·완화 변경으로 무효화된 증거와 판정 변화
5. **Evidence Packet**
   원문, 해시, 계산식, 입력 버전, 판정 규칙과 승인 이력
6. **안전한 판정**
   `SUPPORTED_WITH_MITIGATION`, `CONDITIONAL`, `HOLD`, `INSUFFICIENT_EVIDENCE`

## 6. TID와 SEE 판정 구조

### TID

```text
TID 요구량 = 예상 임무 TID × 사용자 설계 계수
지원 조건 = 확인된 부품 시험 범위 ≥ TID 요구량
```

사용자는 설계 계수와 요구 정책을 정하지만, 부품 시험 한계는 근거 문서에서 가져와야 한다. 시험 범위를 넘어 외삽하지 않는다.

### SEU

```text
완화 전 총 SEU = 환경 입자 스펙트럼 × 부품 시험 단면적 × analysis_device_count × 기간
잔여 SEU = 완화 전 SEU × 검증된 완화 모델
```

사용자는 허용 잔여 오류 기준을 정한다. ECC는 실제 하드웨어 구현이 아니라, 명시된 효과 모델이 수정 가능한 오류에만 적용되는 제한된 계산 가정이다. 근거가 합성 또는 가정이면 실제 적합성 판단에 사용하지 않는다.

구매 수량은 부품 identity·차폐·TID 적용성 판단에서 제외한다. 장치 수에 따라 총 SEU를 집계할 때만 별도 분석 입력 `analysis_device_count`를 사용하며, 이 값이 exact-part 증거 적용성을 바꾸지는 않는다.

SEU가 낮더라도 SEL·SEB·SEGR과 같은 파괴성 SEE 증거가 없으면 최종 판단을 보류한다.

## 7. Multi-Agent 아키텍처

Multi-Agent는 방사선 수치를 자율 생성하는 장치가 아니라, 서로 다른 증거 책임을 분리하고 한 Agent의 누락이나 오류가 낙관적인 최종 판정으로 전파되지 않게 하는 실행 구조다.

### Orchestrator

고정된 workflow 상태를 관리하고 각 Agent의 schema-valid 결과만 다음 단계로 전달한다. 최종 과학 판정은 생성하지 않는다.

### Mission Environment Agent

임무·차폐 입력을 검증하고 승인된 방사선 모델의 실행 계약을 생성한다. 직접 수치를 창작하지 않으며 결정론적 계산 서비스를 호출한다.

### Parts Evidence Agent

BOM 식별자를 정규화하고 NASA·ESA·제조사·고객 자료에서 시험 증거 후보를 찾는다. 정확한 부품번호, 공정, 로트, 시험 조건과 원문 위치를 구조화한다.

### Independent Assurance Agent

환경 결과와 부품 증거를 독립적으로 재검토한다. 조건 불일치, 출처 누락, 범위 밖 외삽, 미승인 커스텀 정책을 발견하면 판정을 보류한다.

### 비에이전트 영역

단위 변환, TID·SEU 계산, 정책 평가, 스키마 검증과 최종 판정 게이트는 결정론적 코드가 담당한다. LLM은 증거 후보 탐색·구조화·설명에만 사용한다.

## 8. GCP 인프라 방향

| 구성 | 역할 |
|---|---|
| Cloud Storage | 원본 BOM, 모델 출력, 시험 보고서와 결과 버전 보관 |
| Cloud Run | Orchestrator와 세 Agent API, 결정론적 계산·판정 호출 |
| Workflows 또는 Pub/Sub | 환경 검증 → 부품 증거 검증 → 독립 감사 순서와 실패 격리 |
| Cloud Logging | Agent별 요청 ID, 상태, 오류 코드와 실행 이력 |
| IAM | Agent별 service account와 최소권한 경계 |
| Document AI / Vertex AI | PDF 추출·근거 구조화 확장; 사용 시 후보값으로만 처리 |
| Cloud SQL / BigQuery / KMS | 관계형 이력·평가 분석·고객 암호화가 필요할 때 확장 |

대회 최소 구현은 Cloud Run, Cloud Storage, 실제 오케스트레이션 1회, Agent별 IAM과 로그를 포함한다. 단순 아키텍처 그림이나 로컬 mock만으로 GCP 구현 완료를 주장하지 않는다.

## 9. 신뢰성 계약

모든 값은 다음 중 하나로 분류한다.

- `PUBLISHED`: 신뢰할 수 있는 외부 출처에서 확인
- `CALCULATED`: 고정된 입력과 코드로 재현 가능
- `ASSUMED`: 사용자 또는 연구자가 명시적으로 설정
- `SYNTHETIC`: 데모·테스트 전용
- `CUSTOMER_VERIFIED`: 고객 자료와 승인 절차로 확인

필수 원칙은 다음과 같다.

- 모든 주장에 출처, 버전, 페이지·표 위치 또는 계산 실행 ID를 연결한다.
- 정확한 부품번호·공정·로트가 다르면 자동 동일시하지 않는다.
- 모델명, 버전, 입력, 출력 해시와 불확실성을 보관한다.
- 미승인 커스텀 정책으로 PASS를 만들지 않는다.
- 근거가 없거나 충돌하면 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`를 반환한다.
- 핵심 품질 목표는 **False PASS 0건**이다.

## 10. 데이터 전략

### 환경·계산 모델 후보

- [ESA SPENVIS](https://www.spenvis.oma.be/): 궤도 입자환경, TID, LET, SEU 모델
- [NASA OLTARIS](https://oltaris.nasa.gov/): 방사선 수송과 차폐 분석 참고

### 부품 시험 증거 후보

- [NASA GSFC Radiation Database](https://nepp.nasa.gov/radhome/RadDatabase/RadDataBase.html)
- [NASA NEPP](https://nepp.nasa.gov/pages/About-NEPP.cfm)
- [ESA Radiation Reports](https://esarad.esa.int/)
- 제조사 공개 시험 보고서와 고객 보유 자료

공개 데이터는 프로토타입에는 충분할 수 있지만 최신 상용부품, 공정 변경과 로트별 차이를 완전히 포괄하지 않는다. 실제 데이터 범위는 수집·정규화 후 다시 평가한다.

## 11. 기존 도구와의 차이

SPENVIS·OMERE는 환경과 방사선 영향을 계산하고 FASTRAD는 차폐 분석을 지원한다. 전문기관은 BOM 검토와 시험 컨설팅도 제공한다.

SPECTRA의 정체성은 새로운 물리 계산기를 만드는 것이 아니라 다음 공백을 해결하는 것이다.

> **환경 모델 결과와 정확한 부품 시험 증거를 연결하고, 계산의 재현성·데이터 무결성·변경 영향을 독립적으로 감사하는 Evidence Assurance 계층**

## 12. 평가 기준 대응

| 평가 항목 | 비중 | SPECTRA의 증명 과제 |
|---|---:|---|
| Multi-Agent 아키텍처 및 GCP 인프라 완성도 | 35 | 역할별 계약, Agent 장애 격리, 실제 GCP E2E 실행·로그·IAM 증거 |
| 할루시네이션 방어 및 무결점 신뢰성 | 20 | 출처 추적, 결정론적 계산, 오염·누락 데이터의 fail-closed와 False PASS 0 |
| 비즈니스 임팩트 및 문제 정의 | 30 | 증거 단절 문제, 사용자 결정과 검토·시험 비용 절감 가설 |
| 팀 시너지 및 프레젠테이션 | 15 | 역할 분담, 일관된 데모 흐름, 시간 내 설명과 Q&A |

## 13. 현재 상태

- 프로젝트 문서와 검증 가능한 Workstream 운영 구조가 마련됐다.
- Stage 2 결정론적 합성 TID·SEE 기준선이 통합됐으며 모든 합성 실행은 `SYNTHETIC/HOLD`를 유지한다.
- Stage 3은 사람 주도 SPENVIS 실행의 실제 원본 bundle 1세트·9개와 실제-format parser 후보를 확보했고, checksum·입력 gate의 fail-closed 동작을 검증했다. 다만 provider job reference·action별 권리·승인 raw manifest가 없어 제품 contract 발행은 0건이며 계속 `HOLD`다.
- Stage 4의 부품 증거 출처·권리·identity·적용성 조사와 exact-part/TID 원문 후보 1건은 확보했지만, 승인 BOM·권리 manifest·임무 적용성·필요 SEE coverage를 통과한 ingest는 0건이다.
- 실제 환경 원본은 Git 밖 private evidence bundle로만 보존하며 dose 값은 제품 입력·fixture·문서에 발행하지 않았다. 실제 부품 시험자료의 승인 ingest와 과학적 교차검산은 아직 완료하지 않았다.
- Competition Submission Release용 합성 Multi-Agent·GCP 경로는 교육용 project에 production Core-bound Cloud Run Agent 3개, Workflows, Storage, IAM, Logging으로 실제 배포됐다. Phase 1에서 발견한 exact-part `FALSE_ACCEPT`와 generation `UNEXPECTED_RESULT`를 보완한 새 revision을 배포했고, control 1건과 네 공격의 actual 재검증은 `CONTROL_PASS 1 / SAFE_FAILURE 4 / False Accept·False PASS·unexpected 0`이다. H06~H08 read-only receipt와 Product timeline도 새 정상 execution으로 갱신했다.
- 발표·검증 콘솔은 별도 공개 Cloud Run `spectra-demo-console` revision `00009-zpm`에 배포됐다. `문서 검사`는 요청마다 `pypdf/TXT` 규칙 기반 parser를 실행한다. `임무·부품·시험 연결`은 고정 합성 Mission Case와, 사용자가 역할을 지정한 세 문서의 후보 교차 대조를 지원한다. 직접 문서 경로는 승인·권리·Mission Case 결속 전까지 `NOT_FOR_DECISION / HOLD`다. `저장된 공격 검증`은 공개 쓰기 권한을 열지 않고 독립 확인된 snapshot을 표시하며, `문서별 결과표`는 공개 GCP catalog를 읽는다.
- 최신 통합 회귀는 unit 447개와 Assurance 공격 실행 47개가 통과했고, 공개 1280×720 deck·Console 동선을 확인했다. 사람 7분 낭독·탭 전환 시간은 아직 `NOT_MEASURED`다.
- 발표의 Phase 01~03 확장 항목은 source intake·document review·Change Impact/CAD readiness를 bounded workflow로 구현했다. 현재 주 시연은 발표와 단일 Evidence Console을 사용하며, 실제 connector·AI API·CAD 계산·KMS·침투시험 완료로 확대하지 않는다.
- 실제 비행 적합성 또는 과학적 정확도 검증을 완료하지 않았다.

장기 과학 MVP와 제출 Release 경계는 [docs/MVP.md](docs/MVP.md), Release 완료·후속 범위는 [ROADMAP.md](ROADMAP.md), 제출 승인 상태는 [CHECKLIST.md](CHECKLIST.md)를 따른다.
