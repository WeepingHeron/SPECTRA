# SPECTRA 채팅 세션·Workstream 운영 규칙

## 1. 기본 개념

- **Stage:** 프로젝트의 진행 순서. `ROADMAP.md`에서 관리한다.
- **Workstream:** 지속적으로 책임지는 전문 영역이다.
- **작업 패키지:** 하나의 산출물과 Exit Gate를 가진 구현·조사 단위다.
- **Session:** SPECTRA 프로젝트 안에서 실제로 열어 사용하는 **채팅방 하나**다.

Stage, Workstream, 작업 패키지와 Session은 서로 다른 개념이다. 한 채팅 세션에서 여러 작업 패키지와 Workstream을 연속으로 다룰 수 있고, 하나의 Workstream도 여러 채팅에서 이어질 수 있다.

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

위 십 단위 번호는 작업 순서나 채팅 세션 번호가 아니라 **책임 영역 식별자**다. 예를 들어 `docs/workstreams/10-contracts-schema/`의 `10`은 채팅 10이 아니라 Contracts Workstream 코드다. 의존 관계는 번호가 아니라 각 Workstream의 `BRIEF.md`에 기록한다.

## 3. 채팅 세션 번호

채팅 세션은 프로젝트 전체에서 다음 네 개를 기본으로 사용한다.

| 세션 ID | 실제 의미 | 기본 역할 |
|---:|---|---|
| `00-control-tower` | Control Tower 채팅방 | 독립 검증, 통합, 체크리스트와 Git |
| `10-primary-build` | 주 구현 채팅방 | 계약부터 합성 Vertical Slice까지 연속 구현 |
| `11-parallel-integration` | 병렬·후속 채팅방 | 10과 겹치지 않는 조사·통합 작업 |
| `12-final-assurance` | 최종 채팅방 | 전체 신뢰성, 제품 완성, 발표·시연 통합 |

작업 목표나 산출물이 바뀌어도 같은 채팅 안에서 계속한다. `R1`, `R2` 같은 라운드 접미사와 산출물별 신규 세션 번호는 사용하지 않는다. 세션 11·12는 새 채팅방을 실제로 열 때만 시작한다.

### 새 채팅을 여는 조건

다음 중 하나일 때만 남아 있는 `11` 또는 `12` 채팅을 연다.

- 현재 채팅의 컨텍스트가 너무 길어 안전한 연속 작업이 어려운 경우
- 서로 독립적인 작업을 실제로 병렬 진행해 대기 시간을 줄이는 경우
- 구현과 최종 독립 검증처럼 역할 분리가 필요한 경우

작은 기능 추가, 버그 수정, 재검증, Workstream 변경, 새로운 Exit Gate만으로는 채팅을 추가하지 않는다. 이들은 현재 채팅 안의 **작업 패키지**로 관리한다.

## 4. 병렬 작업 규칙

세션 10과 11에서 병렬 작업을 진행할 수 있다. 단, 병렬성 때문에 현재 진실과 Git 범위가 섞이지 않도록 다음을 지킨다.

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
