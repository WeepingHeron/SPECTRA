# SPECTRA 로드맵

## 운영 원칙

- 단계는 일정이 아니라 **검증 가능한 완료 조건(Exit Gate)**으로 종료한다.
- 합성 데이터와 실제 근거를 같은 결과로 섞지 않는다.
- 계산 가능한 값은 결정론적 코드가 만들고 LLM은 증거 탐색·구조화·설명에 한정한다.
- 필수 증거가 없으면 기능 완성보다 `HOLD`가 먼저다.
- 각 단계는 사용자 화면에서 확인 가능한 산출물과 재현 명령을 남긴다.
- 제품의 과학적 핵심, 대회 필수 실행 아키텍처와 실험적 확장을 섞어 완료를 주장하지 않는다.

## 번호 체계를 읽는 법

- **Stage**는 검증해야 할 결과의 순서이며, 번호는 주관 Workstream의 십 단위 앞자리와 맞춘다.
- **Workstream**은 전문 책임 영역이며 십 단위 번호를 사용한다.
- **Session**은 실제 채팅방이다. Workstream의 첫 채팅은 같은 십 단위 번호를 사용하고, 같은 Workstream에서 새 채팅이 필요할 때만 1단위로 증가한다.
- Workstream은 이후 Stage에서도 협업 역할로 다시 참여할 수 있지만, 각 Stage의 주관 번호는 항상 같은 앞자리로 맞춘다.

## Stage–Workstream–Session 대응표

| Stage | 검증 결과 | 주관 Workstream | 첫 채팅 | 주요 협업 Workstream | 선행 조건 | 현재 상태 |
|---:|---|---|---:|---|---|---|
| 1 | 프로젝트 계약과 기준선 | 10 Contracts & Schema | `10` | 00 Control Tower | 없음 | **IN_PROGRESS** — 계약·스키마는 통합, 팀 범위 검토 등 잔여 |
| 2 | 재현 가능한 합성 Vertical Slice | 20 Simulation Core | `20` | 10 Contracts, 00 Control Tower | 검증된 Stage 1 데이터 계약 | **COMPLETE** — 결정론적 합성 기준선과 Exit Gate 통합; 제품 UI는 Stage 8 범위 |
| 3 | 실제 환경·TID 모델 경로 | 30 Environment Model | `30` | 10 Contracts, 20 Simulation, 60 Assurance | 안정된 합성 입출력 경로 | **IN_PROGRESS / GATE VERIFIED** — intake·issuance 공격 65 tests와 readiness receipt는 통합; provider job ref·rights·승인 raw manifest·과학 교차검산이 없어 실제 contract 0건 |
| 4 | 실제 부품 TID·SEE 증거 경로 | 40 Parts Evidence | `40` | 10 Contracts, 60 Assurance | EvidencePacket 계약 | **IN_PROGRESS / TEST GATE VERIFIED** — exact-part test-only gate 7 tests와 readiness receipt는 통합; 승인 BOM·rights·임무 적용성·필요 SEE coverage가 없어 실제 packet 0건 |
| 5 | 제한된 설계 가정·판정 엔진 | 50 Mitigation & Policy | `50` | 20 Simulation, 40 Parts, 60 Assurance | 환경·부품 증거 인터페이스 | **IN_PROGRESS** — 차폐·ECC·판정 기준의 합성 Decision Engine 검증; 실제 ECC 효과·실제 evidence 연결 미구현. WATCHDOG·TMR·SEL runtime은 실험 보존 |
| 6 | 독립 보증·평가 기준선 | 60 Assurance & Evals | `60` | 20~50 구현 Workstream | 결정론적 계산·증거·판정 경로 | **IN_PROGRESS** — Core 공격 29개 False PASS 0 기준선 검증, runtime 18개는 별도 experimental profile; 실제 GCP D02는 `NOT_EVALUATED` |
| 7 | Multi-Agent·GCP 실행 경로 | 70 Platform & GCP | `70` | 30~60 전문 Workstream | 안정된 Core API·감사 계약 | **IN_PROGRESS / H05 VERIFIED / COMPETITION REQUIRED** — 교육용 GCP에 production Core-bound Cloud Run Agent 3개·Workflows·Storage·IAM·Logging 합성 E2E를 배포했고 body-hash·endpoint 공격을 차단했다. Workstream 60의 고정 revision `ASR-D02` 독립 공격은 아직 `NOT_EVALUATED`다. |
| 8 | 제품·대시보드 통합 | 80 Product & Dashboard | `80` | 60 Assurance, 70 Platform | 검증된 통합 API와 EvidencePacket | `IN_PROGRESS / ROADMAP LAB VERIFIED` — generated 합성 결과, H05 snapshot, readiness Workspace와 7개 확장 화면 검증; 실제 contract·원문 locator·live connector/API·CAD 계산 미통합 |
| 9 | 비즈니스·발표·최종 시연 | 90 Business & Presentation | `90` | 60 Assurance, 80 Product | Stage 8 제품 기준선 | `IN_PROGRESS / DECK VERIFIED` — `demo/index.html` 13장 localhost 검증, 근거 기반 문제·비즈니스 영향과 Trust & Integrity 경계 반영; 사람 7분 리허설과 사용자·비즈니스 측정 미완료 |

`주관 Workstream`은 해당 Stage의 완료 증거를 만드는 책임 영역이다. `주요 협업 Workstream`은 입력이나 독립 검증을 제공하지만 그 Stage의 소유 채팅을 대신하지 않는다.

## MVP와 Stage의 관계

제품의 과학적 MVP 계약은 [`docs/MVP.md`](docs/MVP.md)에 둔다. MVP는 모든 Stage 완료의 축약어가 아니라, Stage 3·4·5·6·8에서 **한 개 실제 Evidence-to-Decision 경로**에 필요한 최소 결과만 통합한 제품 기준선이다.

- Stage 1·2의 계약과 합성 Vertical Slice는 이미 확보된 기반이다.
- Stage 3·4는 실제 환경 산출물 1개와 exact-part 증거 묶음 1개만 먼저 연결한다.
- Stage 5는 그 사례에 필요한 차폐·ECC 가정과 판정 기준만 결정론적으로 구현한다.
- Stage 6은 새 경로의 False PASS와 재현성을 검증한다.
- Stage 8은 결과 JSON, EvidencePacket과 Change Impact를 제품 UI에서 보여 준다.
- Stage 7은 Core MVP의 과학적 성립 조건과 분리하지만, 대회용 **Competition Demo Release**와 35점 아키텍처 평가에는 필수다.
- Stage 9는 실제 사용자·비즈니스 검증과 발표 완성도를 별도로 평가한다.

현재 상태는 `CORE MVP IN_PROGRESS / COMPETITION DEMO RELEASE IN_PROGRESS / ASSURANCE HOLD`다. 합성 계산·결정 엔진·공격 기준선, readiness receipt와 fail-closed Product Workspace가 통합됐다. 실제 Multi-Agent·GCP 합성 E2E는 H04 독립 공격에서 발견된 입력 무결성·Core 결합 결함을 H05에서 보완했고 Control Tower 독립 재검증을 통과했다. 다만 실제 GCP `ASR-D02` 공격은 계속 `NOT_EVALUATED`이며, 실제 환경·부품 contract도 0건이다. runtime 완화 계산은 실험적 확장이지 Release 선행 조건이 아니다.

발표의 Phase 01~03 항목은 `demo/roadmap-lab.html`에서 7개 화면으로 연결된다. Change Impact·local 문서 검토·H05 security snapshot은 제한된 합성 구현이고, source intake·COTS library·AI processor·CAD linkage는 외부 실행 전 readiness 또는 blocker gate다. 따라서 “로드맵 화면 구현”은 완료했지만 SPENVIS/NASA live connector, production COTS library, Document AI/Gemini 호출, authenticated HITL, 실제 CAD/3D shielding, KMS 운영과 penetration test 완료를 뜻하지 않는다.

### 병렬 진행 해석

- Stage 완료 표시는 Exit Gate 순서대로 관리한다.
- 선행 계약이 검증됐다면 후속 Workstream의 조사·준비 작업은 병렬로 시작할 수 있다.
- 병렬 시작은 앞 Stage가 완료됐다는 뜻이 아니다. 의존 결과가 없으면 `HOLD` 또는 미검증 후보로 남긴다.
- 예: 채팅 20이 Stage 2 합성 Vertical Slice를 구현하는 동안 채팅 30은 환경 모델 이용 조건을 조사할 수 있지만, Stage 3 통합 완료는 Stage 2의 안정된 출력 경로가 필요하다.

## 전체 흐름

```text
Stage 1  프로젝트 계약
   ↓
Stage 2  재현 가능한 합성 Vertical Slice
   ↓
Stage 3  실제 환경·TID 모델 연결
   ↓
Stage 4  실제 부품 TID·SEE 증거 연결
   ↓
Stage 5  완화·정책 엔진
   ↓
Stage 6  독립 보증·평가 기준선
   ↓
Stage 7  Multi-Agent·GCP 통합
   ↓
Stage 8  제품·대시보드 통합
   ↓
Stage 9  비즈니스·발표·최종 시연
```

## Stage 1 — 프로젝트 계약과 기준선

> 주관: Workstream 10 · 첫 채팅: `10-contracts-and-schema` · 거버넌스·독립 검토: Workstream 00 · 다음 Stage 전달: 검증된 데이터·판정 계약

### 목표

무엇을 만들고 무엇을 주장하지 않을지 고정한다.

### 주요 작업

- 프로젝트 소개, 로드맵, 체크리스트 확정
- Git 저장소와 기본 디렉터리 구조 구성
- 데이터 분류 및 Evidence Packet 스키마 정의
- TID·SEE·완화·정책 용어집 작성
- 평가 기준별 성공 지표 정의
- 의사결정 기록 형식과 변경 승인 규칙 정의

### 산출물

- `PROJECT_OVERVIEW.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- 데이터·판정 스키마
- 최소 검증 세트 명세

### Exit Gate

- 동일한 입력·판정·산출물 범위를 팀원이 일관되게 설명할 수 있다.
- `PUBLISHED / CALCULATED / ASSUMED / SYNTHETIC / CUSTOMER_VERIFIED`가 스키마에 존재한다.
- 프로젝트가 인증이나 실제 방사선 시험 대체를 주장하지 않는다.

## Stage 2 — 합성 Vertical Slice 통합

> 주관: Workstream 20 · 첫 채팅: `20-simulation-core` · 선행: Stage 1 데이터 계약 · 검토: Workstream 00

### 목표

현재 합성 데모를 프로젝트 내부의 재현 가능한 기준선으로 통합한다.

### 주요 작업

- 합성 시뮬레이터·테스트 데이터·대시보드 이관
- TID 계산, SEE 계산, 정책 판정 모듈 분리
- 입력·출력 JSON Schema 작성
- 완화 전·후 결과와 근거 패킷 연결
- 정상·경계·증거누락·범위초과 테스트 구성
- 로컬 실행법과 테스트 명령 문서화

### 사용자 시연

- 동일 부품에서 차폐만 변경해 TID 결과 비교
- 동일 환경에서 ECC 유무로 잔여 SEU 비교
- 차폐를 늘려도 파괴성 SEE 증거가 없으면 계속 `HOLD`
- 지원 범위 밖 입력은 `OUT_OF_MODEL_SCOPE`

### Exit Gate

- 새 환경에서도 한 명령으로 시뮬레이션과 테스트를 재현한다.
- 합성 데이터가 모든 화면과 결과에서 `SYNTHETIC`으로 표시된다.
- 고정 테스트에서 False PASS가 0건이다.

## Stage 3 — 실제 환경·TID 모델 연결

> 주관: Workstream 30 · 첫 채팅: `30-environment-model` · 선행: Stage 2 입출력 경로 · 검토 지원: Workstream 60

### 목표

합성 환경값을 출처가 고정된 실제 모델 출력으로 교체한다.

### 주요 작업

- 초기 지원 궤도와 모델을 1개 흐름으로 제한
- SPENVIS 등 후보 도구의 이용 조건과 자동화 방식을 확인
- 모델 입력 계약: 궤도, 시점, 기간, 태양 조건, 차폐
- 모델 출력 파서와 단위 정규화 구현
- 모델명·버전·입력·출력 해시 저장
- 대표 시나리오의 참조 결과와 교차검산
- 불확실성·신뢰수준의 표시 규칙 정의

### 권장 초기 범위

- LEO 대표 궤도 3개 이하
- 알루미늄 등가 차폐 1~4 mm
- TID 중심, SEE용 LET 스펙트럼은 후속 연결 가능하도록 저장

### Exit Gate

- 동일 입력으로 모델 결과를 재생성하거나 고정 출력의 무결성을 확인한다.
- 합성값과 실제 모델값이 저장·화면·API에서 혼동되지 않는다.
- 지원 범위 밖 입력을 외삽하지 않고 보류한다.

## Stage 4 — 실제 부품 TID·SEE 증거 연결

> 주관: Workstream 40 · 첫 채팅: `40-parts-evidence` · 선행: Stage 1 EvidencePacket 계약 · 검토 지원: Workstream 60

### 목표

정확한 부품과 시험 조건을 추적할 수 있는 Evidence Packet을 만든다.

### 주요 작업

- 실제 부품 5~10종 선정
- NASA·ESA·제조사 보고서 수집 및 사용 권한 기록
- 원문 해시, 버전, 페이지·표 위치 저장
- 부품번호·제조사·공정·다이·로트 정규화
- TID 선량·성능 변화·시험 최대범위 추출
- SEE 단면적–LET 또는 에너지 곡선과 시험조건 추출
- 파괴성 SEE 증거를 SEU와 분리
- 자동 추출값의 사람 검토·승인 흐름 구축

### Exit Gate

- 각 수치에서 원문 위치까지 역추적할 수 있다.
- 부품군 유사성만으로 정확한 부품 증거를 대체하지 않는다.
- 시험 조건이 임무 적용 조건과 다르면 자동 PASS하지 않는다.

## Stage 5 — 제한된 설계 가정 및 판정 엔진

> 주관: Workstream 50 · 첫 채팅: `50-mitigation-policy` · 선행: Stage 3·4 인터페이스 · 계산 연계: Workstream 20

### 목표

방사선 분석에 직접 필요한 차폐·ECC 가정과 판정 기준을 명시적이고 재현 가능한 입력으로 고정한다.

### 활성 입력

- 차폐 재료·등가 두께
- 내방사선 부품 대체
- ECC 유형과 수정 가능 비트 수

WATCHDOG·TMR·SEL 보호, 스크러빙, 체크포인트·재시도와 예비 장치 전환은 실제 시스템 구조가 정해진 뒤의 trade study 후보로 둔다. 현재 구현과 테스트는 `experimental runtime`으로 보존하며 Core Product 또는 Competition Demo의 사용자 판단에 사용하지 않는다.

### 정책 입력 후보

- TID 설계 계수와 최소 잔여 마진
- 최대 잔여 SEU 횟수 또는 확률
- SEFI·SEL·SEB 증거 요구 수준

### 신뢰성 규칙

- 완화 효과에 근거가 없으면 `ASSUMED`로 표시하고 최종 PASS에 사용하지 않는다.
- 판정 기준의 출처·버전·적용 범위가 없으면 최종 지원 판정에 사용하지 않는다.

### Exit Gate

- 완화 전·후 결과가 분리되고 동일 입력으로 재현된다.
- 서로 다른 완화 방법이 영향을 주는 고장 유형을 구분한다.
- ECC가 SEL·SEB 위험을 제거했다고 판정하지 않는다.

## Stage 6 — 독립 보증·평가 기준선

> 주관: Workstream 60 · 첫 채팅: `60-assurance-evals` · 검토 대상: Workstream 20~50의 결정론적 계산·증거·정책 결과

### 목표

정상 데모뿐 아니라 누락·오염·충돌 데이터에서도 안전하게 실패함을 증명한다.

### 검증 세트

- 정확한 부품 일치 / 유사 부품 오탐
- 시험 단위 변환 오류
- 시험 범위 밖 외삽 요청
- 오래된 제조 공정·로트 자료
- 출처 링크 손상·해시 불일치
- SEE 단면적 누락
- 파괴성 SEE 자료 누락
- 미승인 커스텀 정책
- 계산·증거·정책 모듈 간 상충 결과

### 핵심 지표

- False PASS: 0
- 계산 재현율: 100%
- 근거 링크·페이지 정확도
- 부품 식별 정확도
- 필수 필드 추출 정확도
- 변경 영향 탐지율
- 결정론적 검증 처리시간

### Exit Gate

- 독립 검증 세트에서 False PASS가 0건이다.
- 알려진 한계와 미지원 범위가 결과에 노출된다.
- 계산·증거·정책 결과가 동일 입력에서 재현된다.

## Stage 7 — Multi-Agent 및 GCP 통합

> 주관: Workstream 70 · 첫 채팅: `70-platform-gcp` · 선행: Workstream 30~60 서비스·감사 계약

### 목표

Core Evidence-to-Decision 경로를 역할이 분리된 Agent와 실제 GCP 서비스로 실행하고, 장애 격리·권한·로그 증거를 남긴다. 이 Stage는 Competition Demo Release 필수 조건이다.

### 주요 작업

- Orchestrator와 Mission Environment·Parts Evidence·Independent Assurance Agent 계약 구현
- Cloud Run에 Agent API와 결정론적 Core 호출 배포
- Cloud Storage에 합성 입력·중간 결과·최종 EvidencePacket을 generation과 SHA-256으로 연결
- Workflows 또는 Pub/Sub로 고정 실행 순서, timeout과 실패 격리 구현
- Agent별 service account 최소권한과 Cloud Logging correlation ID 기록
- 고정 합성 정상 1건과 Agent 실패·오염 입력 공격을 실제 배포 경로에서 실행
- Document AI·Vertex AI·Cloud SQL·BigQuery·KMS는 최소 E2E 이후 채점 기여와 시간 대비 효과가 있을 때 확장

### 장애 시나리오

- 환경 모델 실패 또는 오래된 출력
- PDF 추출 필드 누락·단위 오인
- 부품 식별자 충돌
- Auditor 불일치
- 모델·규칙 버전 변경
- 권한 없는 고객 문서 접근

### Exit Gate

- 각 에이전트 입력·출력·실패 상태가 로그와 Evidence Packet에 남는다.
- 한 에이전트 실패가 낙관적인 최종 판정으로 전파되지 않는다.
- 실제 GCP resource, 요청·응답·로그와 실행 증거가 존재한다.
- Stage 6 공격 세트가 배포 경로에서도 계속 통과한다.

## Stage 8 — 제품·대시보드 통합

> 주관: Workstream 80 · 첫 채팅: `80-product-dashboard` · 선행: Stage 7 통합 API · 신뢰성 지원: Workstream 60

### 목표

사용자가 임무·BOM을 입력하고 판정, 근거, 공백과 변경 영향을 한 흐름에서 이해하도록 제품 경험을 완성한다.

### 주요 작업

- 임무·BOM·차폐·완화·정책 입력 흐름
- TID·SEE 결과와 완화 전후 비교
- Evidence Coverage Matrix와 원문 위치 연결
- `HOLD`·증거 공백·미지원 범위의 명시적 표시
- 변경 전후 영향 보고서
- 데이터 분류와 계산 실행 ID 노출
- 라이브 실패에 대비한 검증된 고정 결과 fallback

### Exit Gate

- 핵심 흐름을 한 화면씩 이해할 수 있다.
- 모든 주요 수치에서 출처 또는 데이터 분류로 이동할 수 있다.
- 실패·누락 상태가 성공 화면으로 렌더링되지 않는다.
- 대표 시나리오를 반복 재현할 수 있다.

## Stage 9 — 비즈니스 검증과 최종 시연

> 주관: Workstream 90 · 첫 채팅: `90-business-presentation` · 선행: Stage 8 제품 기준선 · 근거 검토: Workstream 60

### 목표

기술적으로 흥미로운 데모를 실제 사용자가 이해하고 비용을 지불할 수 있는 문제 해결로 연결한다.

### 주요 작업

- 잠재 사용자 인터뷰
- 현재 검토 시간·인력·시험비용 기준선 조사
- 가장 가치 있는 산출물과 구매 단위 검증
- 기존 도구·컨설팅 대비 차별점 재검증
- 임무 변경 전·후 시연 시나리오 확정
- 7분 설명과 3분 질의응답 근거 준비
- 보안·책임 한계·운영비 정리

### 최종 시연 흐름

```text
BOM·임무 입력
→ 환경·TID 계산
→ 부품 시험 증거 대조
→ 완화 방법·정책 선택
→ 완화 전후 위험 비교
→ 독립 감사
→ Evidence Packet과 Action Plan
```

### Exit Gate

- 최소 1개 사용자군이 문제와 산출물의 가치를 확인한다.
- 절감 시간 또는 회피 비용 가설을 수치와 근거로 제시한다.
- 기존 계산 도구가 아니라 Evidence Assurance 계층이라는 정체성이 시연에서 드러난다.
- 모든 주요 수치에 출처 또는 데이터 분류가 보인다.

## 현재 우선순위

1. **Stage 3:** 확보된 SPENVIS bundle에 provider job reference, action별 권리, 승인 raw manifest와 과학적 교차검산을 연결해 실제 environment contract 1개를 발행할 수 있는지 판정한다.
2. **Stage 4:** 승인 BOM의 exact orderable part 1개를 고정하고 권리 확인 원문, 시험 조건·임무 적용성, TID와 필요한 파괴성 SEE coverage를 연결한다.
3. **Stage 6·7:** 사용자 승인과 고정 revision 범위를 확보한 뒤 실제 GCP `ASR-D02`를 수행한다. 실행 전까지 상태는 `NOT_EVALUATED`다.
4. **Stage 8:** 실제 environment·part contract가 생기면 현재 generated 합성 payload와 분리된 실제 Evidence-to-Decision 입력 경로를 Product에 연결한다.
5. **Stage 9:** 실제 사용자 1명으로 5분 실행·판정 이유·다음 행동 탐색을 측정하고, 검증되지 않은 COTS·과학·비용 주장은 삭제하거나 출처·범위와 함께 제한한다.
6. 공통 계약이나 Core를 바꾸지 않는 동안은 변경 Workstream 테스트만 실행하고, 전체 회귀와 commit·push는 검증 가능한 통합 단위가 정리된 시점에 한 번 수행한다.

세부 완료 항목과 증거는 [CHECKLIST.md](CHECKLIST.md)에서, 채팅 번호와 파일 소유 규칙은 [docs/workstreams/README.md](docs/workstreams/README.md)에서 관리한다.
