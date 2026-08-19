# SPECTRA 로드맵

## 운영 원칙

- 단계는 일정이 아니라 **검증 가능한 완료 조건(Exit Gate)**으로 종료한다.
- 합성 데이터와 실제 근거를 같은 결과로 섞지 않는다.
- 계산 가능한 값은 결정론적 코드가 만들고 LLM은 증거 탐색·구조화·설명에 한정한다.
- 필수 증거가 없으면 기능 완성보다 `HOLD`가 먼저다.
- 각 단계는 사용자 화면에서 확인 가능한 산출물과 재현 명령을 남긴다.

## 번호 체계를 읽는 법

- **Stage**는 검증해야 할 결과의 순서다. `Stage 2`가 채팅 20이나 Workstream 20을 뜻하지 않는다.
- **Workstream**은 전문 책임 영역이며 십 단위 번호를 사용한다.
- **Session**은 실제 채팅방이다. Workstream의 첫 채팅은 같은 십 단위 번호를 사용하고, 같은 Workstream에서 새 채팅이 필요할 때만 1단위로 증가한다.
- Workstream 번호는 실행 순서가 아니다. 예를 들어 Assurance Workstream 60은 Platform Workstream 70의 결과까지 포함해 Stage 6에서 주관 검증할 수 있다.

## Stage–Workstream–Session 대응표

| Stage | 검증 결과 | 주관 Workstream | 첫 채팅 | 주요 협업 Workstream | 선행 조건 | 현재 상태 |
|---:|---|---|---:|---|---|---|
| 0 | 프로젝트 계약과 기준선 | 00 Control Tower, 10 Contracts | `00`, `10` | — | 없음 | **IN_PROGRESS** — 계약·스키마는 통합, 팀 범위 검토 등 잔여 |
| 1 | 재현 가능한 합성 Vertical Slice | 20 Simulation Core | `20` | 10 Contracts, 00 Control Tower | 검증된 Stage 0 데이터 계약 | **HOLD** — 채팅 20 인수·재검증 대기 |
| 2 | 실제 환경·TID 모델 경로 | 30 Environment Model | `30` | 10 Contracts, 20 Simulation, 60 Assurance | 안정된 합성 입출력 경로 | `NOT_STARTED` |
| 3 | 실제 부품 TID·SEE 증거 경로 | 40 Parts Evidence | `40` | 10 Contracts, 60 Assurance | EvidencePacket 계약 | `NOT_STARTED` |
| 4 | 완화·사용자 정책 엔진 | 50 Mitigation & Policy | `50` | 20 Simulation, 40 Parts, 60 Assurance | 환경·부품 증거 인터페이스 | `NOT_STARTED` |
| 5 | Multi-Agent·GCP 실행 경로 | 70 Platform & GCP | `70` | 30 Environment, 40 Parts, 50 Policy, 60 Assurance | Stage 2~4 서비스 계약 | `NOT_STARTED` |
| 6 | 독립 신뢰성·성능 검증 | 60 Assurance & Evals | `60` | 20~70 전체 구현 Workstream | 통합 실행 경로와 공격 세트 | `NOT_STARTED` |
| 7 | 제품·비즈니스·최종 시연 | 80 Product, 90 Business | `80`, `90` | 60 Assurance, 70 Platform | Stage 6 검증 기준선 | `NOT_STARTED` |

`주관 Workstream`은 해당 Stage의 완료 증거를 만드는 책임 영역이다. `주요 협업 Workstream`은 입력이나 독립 검증을 제공하지만 그 Stage의 소유 채팅을 대신하지 않는다.

### 병렬 진행 해석

- Stage 완료 표시는 Exit Gate 순서대로 관리한다.
- 선행 계약이 검증됐다면 후속 Workstream의 조사·준비 작업은 병렬로 시작할 수 있다.
- 병렬 시작은 앞 Stage가 완료됐다는 뜻이 아니다. 의존 결과가 없으면 `HOLD` 또는 미검증 후보로 남긴다.
- 예: 채팅 20이 합성 Vertical Slice를 구현하는 동안 채팅 30은 환경 모델 이용 조건을 조사할 수 있지만, Stage 2 통합 완료는 Stage 1의 안정된 출력 경로가 필요하다.

## 전체 흐름

```text
Stage 0  프로젝트 계약
   ↓
Stage 1  재현 가능한 합성 Vertical Slice
   ↓
Stage 2  실제 환경·TID 모델 연결
   ↓
Stage 3  실제 부품 TID·SEE 증거 연결
   ↓
Stage 4  완화·정책 엔진
   ↓
Stage 5  Multi-Agent·GCP 통합
   ↓
Stage 6  신뢰성·성능 검증
   ↓
Stage 7  비즈니스·최종 시연 검증
```

## Stage 0 — 프로젝트 계약과 기준선

> 주관: Workstream 00·10 · 첫 채팅: `00-control-tower`, `10-contracts-and-schema` · 다음 Stage 전달: 검증된 데이터·판정 계약

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

## Stage 1 — 합성 Vertical Slice 통합

> 주관: Workstream 20 · 첫 채팅: `20-simulation-core` · 선행: Stage 0 데이터 계약 · 검토: Workstream 00

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

## Stage 2 — 실제 환경·TID 모델 연결

> 주관: Workstream 30 · 첫 채팅: `30-environment-model` · 선행: Stage 1 입출력 경로 · 검토 지원: Workstream 60

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

## Stage 3 — 실제 부품 TID·SEE 증거 연결

> 주관: Workstream 40 · 첫 채팅: `40-parts-evidence` · 선행: Stage 0 EvidencePacket 계약 · 검토 지원: Workstream 60

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

## Stage 4 — 완화 및 사용자 정책 엔진

> 주관: Workstream 50 · 첫 채팅: `50-mitigation-policy` · 선행: Stage 2·3 인터페이스 · 계산 연계: Workstream 20

### 목표

임의의 완화율 입력을 구체적인 설계 선택과 정책으로 교체한다.

### 완화 입력 후보

- 차폐 재료·등가 두께
- 내방사선 부품 대체
- ECC 유형과 수정 가능 비트 수
- 메모리 스크러빙 주기
- TMR과 투표 구조
- Watchdog·재부팅 시간
- 체크포인트·재시도
- SEL 전류 감지·전원 차단
- 예비 장치 전환

### 정책 입력 후보

- TID 설계 계수와 최소 잔여 마진
- 최대 잔여 SEU 횟수 또는 확률
- 최대 재부팅 횟수와 장애시간
- SEFI·SEL·SEB 증거 요구 수준
- 조직 기본 정책과 승인된 예외

### 신뢰성 규칙

- 완화 효과에 근거가 없으면 `ASSUMED`로 표시하고 최종 PASS에 사용하지 않는다.
- 커스텀 정책에는 변경 사유·사용자·승인자·전후 판정을 저장한다.
- 허용 한도를 높여 기본 정책을 우회하면 `CUSTOM_POLICY_NOT_APPROVED`를 반환한다.

### Exit Gate

- 완화 전·후 결과가 분리되고 동일 입력으로 재현된다.
- 서로 다른 완화 방법이 영향을 주는 고장 유형을 구분한다.
- ECC가 SEL·SEB 위험을 제거했다고 판정하지 않는다.

## Stage 5 — Multi-Agent 및 GCP 통합

> 주관: Workstream 70 · 첫 채팅: `70-platform-gcp` · 선행: Workstream 30·40·50 서비스 계약 · 감사 연계: Workstream 60

### 목표

에이전트 협업과 GCP 인프라가 실제 처리 흐름과 장애 격리에 기여하도록 구현한다.

### 주요 작업

- Mission Environment Agent 계약 구현
- Parts Evidence Agent 계약 구현
- Independent Assurance Agent 계약 구현
- Cloud Storage 원문·결과 버전 관리
- Document AI 추출 후보 파이프라인
- Cloud Run 결정론적 계산·정책 서비스
- Cloud SQL 증거 관계·승인 이력
- Workflows/Pub/Sub 오케스트레이션
- BigQuery 품질 지표 및 평가 결과
- IAM/KMS 고객 데이터 격리

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
- 실제 GCP 실행 증거와 비용 기준선이 존재한다.

## Stage 6 — 신뢰성·성능 검증

> 주관: Workstream 60 · 첫 채팅: `60-assurance-evals` · 검토 대상: Workstream 20~70의 통합 결과

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
- 에이전트 간 상충 결과

### 핵심 지표

- False PASS: 0
- 계산 재현율: 100%
- 근거 링크·페이지 정확도
- 부품 식별 정확도
- 필수 필드 추출 정확도
- 변경 영향 탐지율
- 시나리오 처리시간과 GCP 비용

### Exit Gate

- 독립 검증 세트에서 False PASS가 0건이다.
- 알려진 한계와 미지원 범위가 결과에 노출된다.
- 시연 실패를 대비한 고정 결과와 복구 절차가 있다.

## Stage 7 — 비즈니스 검증과 최종 시연

> 공동 주관: Workstream 80·90 · 첫 채팅: `80-product-dashboard`, `90-business-presentation` · 선행: Stage 6 검증 기준선

### 목표

기술적으로 흥미로운 데모를 실제 사용자가 이해하고 비용을 지불할 수 있는 문제 해결로 연결한다.

### 주요 작업

- 잠재 사용자 인터뷰
- 현재 검토 시간·인력·시험비용 기준선 조사
- 가장 가치 있는 산출물과 구매 단위 검증
- 기존 도구·컨설팅 대비 차별점 재검증
- 임무 변경 전·후 시연 시나리오 확정
- 10분 설명과 질의응답 근거 준비
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

1. Stage 0의 남은 팀 범위·비범위 검토를 닫되, 이미 통합된 계약·스키마를 다시 미완료로 돌리지 않는다.
2. 채팅 `20-simulation-core`가 현재 미검증 합성 Vertical Slice 후보를 인수·재검증한다.
3. Stage 1 통합과 충돌하지 않는 범위에서 채팅 `30`의 환경 모델 이용 조건 조사와 채팅 `40`의 실제 증거 후보 조사를 병렬 준비할 수 있다.
4. Stage 1 Exit Gate가 통과되면 Stage 2·3의 실제 경로를 각각 하나로 제한해 연결한다.

세부 완료 항목과 증거는 [CHECKLIST.md](CHECKLIST.md)에서, 채팅 번호와 파일 소유 규칙은 [docs/workstreams/README.md](docs/workstreams/README.md)에서 관리한다.
