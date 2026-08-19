# SPECTRA Workstream 및 세션 번호 규칙

## 1. 기본 개념

- **Stage:** 프로젝트의 진행 순서. `ROADMAP.md`에서 관리한다.
- **Workstream:** 지속적으로 책임지는 전문 영역. 십 단위 번호를 사용한다.
- **Session:** 하나의 독립적인 산출물과 검증 조건을 갖는 작업 단위다.

Stage와 Workstream은 동일하지 않다. 예를 들어 Environment Workstream은 Stage 2에서 시작하지만 이후 검증·GCP·시연 단계에서도 계속 사용된다.

## 2. Workstream 번호

| 번호 | Workstream | 책임 |
|---:|---|---|
| 00 | Control Tower | 범위, 통합 검증, 체크리스트, Git 반영 |
| 10 | Contracts & Schema | 입력·출력·EvidencePacket·상태 계약 |
| 20 | Simulation Core | 결정론적 TID·SEU 계산과 합성 기준선 |
| 30 | Environment Model | 궤도 환경·차폐·TID 모델 |
| 40 | Parts Evidence | 실제 부품 시험자료 수집·정규화 |
| 50 | Mitigation & Policy | ECC·스크러빙·TMR와 사용자 정책 |
| 60 | Assurance & Evals | 독립 감사, False PASS, 공격 테스트 |
| 70 | Platform & GCP | 저장·워크플로·권한·배포·모니터링 |
| 80 | Product & Dashboard | 시나리오 입력, 결과, 근거 문서 UI |
| 90 | Business & Presentation | 사용자 검증, 차별점, 발표·시연 |

십 단위 번호는 작업 순서가 아니라 **책임 영역 식별자**다. 의존 관계는 번호가 아니라 각 Workstream의 `BRIEF.md`에 기록한다.

## 3. 11·12와 같은 세부 번호 기준

`10`은 Contracts & Schema라는 상위 Workstream을 의미하고, `11`, `12` 등은 그 안의 개별 작업 세션을 의미한다.

예시:

```text
10  Contracts & Schema Workstream
11  EvidencePacket v1 스키마
12  Mission·BOM 입력 스키마
13  SimulationResult·판정 스키마
19  Contracts Workstream 통합 검토

20  Simulation Core Workstream
21  기존 합성 데모 이관
22  TID 계산 모듈 분리
23  SEE 계산 모듈 분리
24  합성 검증 세트
29  Simulation Core 통합 검토
```

### 새 세부 번호를 만드는 조건

다음 중 하나 이상이 달라지면 새로운 번호를 부여한다.

- 최종 산출물이 독립적으로 존재한다.
- 입력·출력 계약이 다르다.
- 수정 책임 파일 영역이 다르다.
- 별도의 검증 명령이나 Exit Gate가 필요하다.
- 다른 세션의 완료를 기다리지 않고 독립적으로 검토할 수 있다.

### 새 번호를 만들지 않는 조건

- 같은 산출물의 버그 수정
- 같은 테스트 실패의 후속 수정
- 컨텍스트가 길어져 대화만 새로 시작하는 경우
- 리뷰 의견을 반영하지만 완료 조건이 변하지 않는 경우

같은 작업을 새 대화에서 계속할 때는 기존 세션 ID를 그대로 사용한다. `R1`, `R2` 같은 라운드 접미사는 붙이지 않는다.

```text
10-contracts-and-schema  최초 작업
10-contracts-and-schema  새 대화에서 같은 작업 계속
10-contracts-and-schema  리뷰 수정과 재검증
```

새 세션 번호는 주요 목표나 Exit Gate가 실질적으로 달라질 때만 만든다. 작은 산출물 추가, 버그 수정, 대화 교체는 기존 세션에서 이어간다.

### 권장 예약 번호

- `X0`: Workstream 자체와 장기 계약
- `X1~X8`: 독립 작업 패키지
- `X9`: Workstream 통합·종료 검토
- `00-control-tower`: Control Tower 세션
- `00-Cnn`: 중간 통합 Checkpoint

작업이 8개를 넘는다면 억지로 번호를 재사용하지 말고 `30-01`, `30-02`처럼 두 자리 하위 번호로 전환한다.

## 4. 세션 분할 원칙

한 세션은 다음 범위를 권장한다.

- 핵심 목표 1개
- 주요 산출물 1~2개
- 책임 Workstream 1개
- 검증 명령 1세트
- 명확한 Exit Gate 1개

세션 이름은 번호와 산출물을 함께 적는다.

```text
11-evidence-packet-schema
21-synthetic-demo-import
31-spenvis-output-contract
41-nasa-part-evidence-pack
51-ecc-scrubbing-policy
61-false-pass-eval-set
```

## 5. 상태 체계

| 상태 | 의미 |
|---|---|
| `NOT_STARTED` | 시작 전 |
| `IN_PROGRESS` | 작업 중이며 검증 미완료 |
| `READY_FOR_REVIEW` | 작업 세션이 검토를 요청한 상태 |
| `VERIFIED` | Control Tower가 독립 검증 완료 |
| `INTEGRATED` | 기준 브랜치 반영과 상위 흐름 검증 완료 |
| `CHANGES_REQUESTED` | 수정 가능한 구체적 문제가 있어 재검증이 필요한 상태 |
| `HOLD` | 증거·선택·외부 조건이 부족해 진행 보류 |

작업 세션은 `READY_FOR_REVIEW`까지만 선언한다. `VERIFIED`, `INTEGRATED`와 루트 `CHECKLIST.md`의 `[x]` 표시는 Control Tower가 담당한다.

## 6. 세션이 읽어야 하는 최소 컨텍스트

새 작업 세션은 전체 대화 기록 대신 다음을 읽는다.

1. `PROJECT_OVERVIEW.md`
2. 해당 Workstream의 `BRIEF.md`
3. 해당 Workstream의 `CURRENT.md`
4. 관련 `schemas/` 계약
5. 직전 세션의 인수인계

과거 세션 전체 기록은 현재 상태만으로 판단할 수 없을 때만 참고한다.

## 7. 프로젝트 폴더 간결성

- 프로젝트 폴더에는 구현, 실행, 검증, Workstream 운영과 장기 인수인계에 계속 필요한 디렉터리와 파일을 둔다.
- 활성 Workstream 디렉터리와 그 안의 `BRIEF.md`, `CURRENT.md`, 스키마, 검증 자료는 프로젝트의 영속 workflow로 유지한다.
- 한 번 사용하고 끝나는 세션 시작 템플릿, 복사용 프롬프트와 임시 보고서만 기본 Downloads 폴더에 저장한다.
- 활성 Workstream 디렉터리는 산출물이 아직 완성되지 않았다는 이유로 삭제하지 않는다.
- 관련 없는 placeholder, 중복 문서와 세션별 기록 사본은 미리 만들지 않는다.
- 일회성 파일이 반복 사용되는 프로젝트 계약으로 승격될 때만 Control Tower 검토 후 프로젝트로 이동한다.
