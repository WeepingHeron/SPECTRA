# SPECTRA 채팅 세션·Workstream 운영 규칙

Stage별 주관 Workstream, 첫 채팅과 선행 조건은 루트 [`ROADMAP.md`](../../ROADMAP.md)의 **Stage–Workstream–Session 대응표**를 기준으로 한다.

## 1. 기본 개념

- **Stage:** 프로젝트의 진행 순서. `ROADMAP.md`에서 관리한다.
- **Workstream:** 지속적으로 책임지는 전문 영역이다.
- **작업 패키지:** 하나의 산출물과 Exit Gate를 가진 구현·조사 단위다.
- **Session:** SPECTRA 프로젝트 안에서 실제로 열어 사용하는 **채팅방 하나**다.

Stage, Workstream, 작업 패키지와 Session은 서로 다른 개념이다. 한 채팅 세션에서 같은 Workstream의 여러 작업 패키지를 처리할 수 있지만, 다른 Workstream 구현으로 넘어갈 때는 그 Workstream의 십 단위 기본 세션을 새 채팅으로 연다.

## 2. Workstream 번호

| Workstream | 채팅 세션 범위 | 책임 |
|---:|---:|---|
| 00 Control Tower | `00`~`09` | 범위, 통합 검증, 체크리스트, Git 반영 |
| 10 Contracts & Schema | `10`~`19` | 입력·출력·EvidencePacket·상태 계약 |
| 20 Simulation Core | `20`~`29` | 결정론적 TID·SEU 계산과 합성 기준선 |
| 30 Environment Model | `30`~`39` | 궤도 환경·차폐·TID 모델 |
| 40 Parts Evidence | `40`~`49` | 실제 부품 시험자료 수집·정규화 |
| 50 Mitigation & Policy | `50`~`59` | ECC·스크러빙·TMR와 사용자 정책 |
| 60 Assurance & Evals | `60`~`69` | 독립 감사, False PASS, 공격 테스트 |
| 70 Platform & GCP | `70`~`79` | 저장·워크플로·권한·배포·모니터링 |
| 80 Product & Dashboard | `80`~`89` | 시나리오 입력, 결과, 근거 문서 UI |
| 90 Business & Presentation | `90`~`99` | 사용자 검증, 차별점, 발표·시연 |

십 단위 번호는 Workstream 식별자이면서 해당 Workstream의 **첫 채팅 세션 번호**다. 예를 들어 `10-contracts-and-schema`는 Contracts Workstream의 첫 채팅이고, 새 채팅이 필요하면 `11`, `12` 순으로 사용한다. Simulation Core는 반드시 `20-simulation-core` 채팅에서 시작한다.

## 3. 채팅 세션 번호

각 Workstream은 십 단위 기본 번호로 첫 채팅을 시작한다.

```text
00-control-tower          Control Tower 첫 채팅
10-contracts-and-schema  Contracts 첫 채팅
11-...                    Contracts에서 새 채팅이 실제로 필요할 때
12-...                    Contracts에서 다시 새 채팅이 필요할 때
20-simulation-core       Simulation Core 첫 채팅
21-...                    Simulation Core에서 새 채팅이 실제로 필요할 때
30-environment-model     Environment Model 첫 채팅
```

같은 Workstream 안에서는 작업 목표나 산출물이 바뀌어도 가능한 한 현재 채팅에서 계속한다. `R1`, `R2` 같은 라운드 접미사는 사용하지 않는다. 다른 Workstream 구현을 현재 채팅에 합치지 않는다.

### Handoff 파일 회차

채팅 번호와 handoff 제출 회차는 별도로 관리한다. 새로 만드는 모든 채팅 시작 템플릿은 작업 종료 시 사용할 handoff 파일명을 다음 형식으로 명시한다.

```text
SPECTRA_<채팅번호>_<작업패키지>_HANDOFF_H01.md
SPECTRA_<채팅번호>_<작업패키지>_HANDOFF_H02.md
```

- `H01`, `H02`는 같은 채팅에서 제출한 handoff의 순서이며 새 채팅이나 새 Session을 뜻하지 않는다.
- 같은 채팅에서 수정·재제출하면 다음 handoff 회차로 올린다.
- 새 채팅의 첫 handoff는 `H01`부터 시작한다.
- 이미 생성된 채팅 00~40의 번호 없는 handoff 파일은 이름을 바꾸지 않고 암묵적 `H01`로 취급한다. 해당 채팅의 다음 handoff부터 `H02`를 사용한다.
- handoff는 일회성 전달 파일이므로 기본 Downloads 폴더에 두고 프로젝트 저장소에는 넣지 않는다.

### 새 채팅을 여는 조건

다음 중 하나일 때만 해당 Workstream 범위 안에서 다음 1단위 번호의 채팅을 연다.

- 현재 채팅의 컨텍스트가 너무 길어 안전한 연속 작업이 어려운 경우
- 같은 Workstream 안의 독립 작업을 병렬 진행해 대기 시간을 줄이는 경우
- 같은 Workstream 안에서 역할 분리가 필요한 경우

작은 기능 추가, 버그 수정, 재검증과 새로운 Exit Gate만으로는 채팅을 추가하지 않는다. 이들은 현재 채팅 안의 **작업 패키지**로 관리한다. 반대로 Workstream이 바뀌면 작은 작업이어도 해당 십 단위의 첫 채팅으로 넘긴다.

## 4. 병렬 작업 규칙

서로 다른 Workstream 채팅 또는 같은 Workstream의 후속 채팅에서 병렬 작업을 진행할 수 있다. 단, 병렬성 때문에 현재 진실과 Git 범위가 섞이지 않도록 다음을 지킨다.

- 시작 전에 각 채팅의 작업 패키지, 소유 파일·디렉터리와 Exit Gate를 `CURRENT.md`에 기록한다.
- 두 채팅이 같은 파일을 동시에 수정하지 않는다. 루트 문서, 공통 schema와 공유 계약은 한 채팅에만 쓰기 소유권을 부여한다.
- 다른 채팅의 미검증 변경에 의존하지 않고 마지막 `INTEGRATED` 기준선을 사용한다.
- 의존 작업이 끝나지 않았으면 가짜 입력이나 추정으로 완료하지 않고 `HOLD` 또는 명시적 stub으로 남긴다.
- 각 채팅은 `READY_FOR_REVIEW`까지만 요청하며, 00 Control Tower만 독립 검증 후 commit·push한다.
- 충돌 가능성이 생기면 새 브랜치를 무조건 만들기보다 먼저 파일 소유 범위를 다시 나눈다.

병렬 작업은 **서로 기다릴 이유가 없는 작업**에만 효과적이다. 같은 계약이나 같은 코드의 선후 관계가 강하면 한 채팅에서 순차적으로 처리한다.

## 5. 상태 체계

| 상태 | 의미 |
|---|---|
| `NOT_STARTED` | 시작 전 |
| `IN_PROGRESS` | 작업 중이며 검증 미완료 |
| `READY_FOR_REVIEW` | 작업 채팅이 작업 패키지 검토를 요청한 상태 |
| `VERIFIED` | Control Tower가 독립 검증 완료 |
| `INTEGRATED` | 기준 브랜치 반영과 상위 흐름 검증 완료 |
| `CHANGES_REQUESTED` | 수정 가능한 구체적 문제가 있어 재검증이 필요한 상태 |
| `HOLD` | 증거·선택·외부 조건이 부족해 진행 보류 |

작업 채팅은 각 작업 패키지에 대해 `READY_FOR_REVIEW`까지만 선언한다. `VERIFIED`, `INTEGRATED`와 루트 `CHECKLIST.md`의 `[x]` 표시는 Control Tower가 담당한다. 작업 패키지 통합은 채팅 세션 종료를 의미하지 않는다.

## 6. 채팅이 읽어야 하는 최소 컨텍스트

새 채팅을 실제로 열 때는 전체 과거 대화 대신 다음을 읽는다.

1. `PROJECT_OVERVIEW.md`
2. 해당 Workstream의 `BRIEF.md`
3. 해당 Workstream의 `CURRENT.md`
4. 관련 `schemas/` 계약
5. 직전 채팅의 인수인계와 현재 작업 패키지

과거 세션 전체 기록은 현재 상태만으로 판단할 수 없을 때만 참고한다.

## 7. 프로젝트 폴더 간결성

- 프로젝트 폴더에는 구현, 실행, 검증, Workstream 운영과 장기 인수인계에 계속 필요한 디렉터리와 파일을 둔다.
- 활성 Workstream 디렉터리와 그 안의 `BRIEF.md`, `CURRENT.md`, 스키마, 검증 자료는 프로젝트의 영속 workflow로 유지한다.
- 한 번 사용하고 끝나는 채팅 시작 템플릿, 복사용 프롬프트와 임시 보고서만 기본 Downloads 폴더에 저장한다.
- 활성 Workstream 디렉터리는 산출물이 아직 완성되지 않았다는 이유로 삭제하지 않는다.
- 관련 없는 placeholder, 중복 문서와 채팅별 기록 사본은 미리 만들지 않는다.
- 일회성 파일이 반복 사용되는 프로젝트 계약으로 승격될 때만 Control Tower 검토 후 프로젝트로 이동한다.
