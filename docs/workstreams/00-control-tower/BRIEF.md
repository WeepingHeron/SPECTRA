# 00 Control Tower — Workstream Brief

## 역할

Control Tower는 SPECTRA 전체 채팅과 작업 패키지의 **Supervisor, Integrator, Independent Reviewer**다. 직접 모든 기능을 구현하는 채팅이 아니라 범위·계약·증거·검증 결과를 통합하여 프로젝트의 현재 진실을 유지한다.

## 핵심 책임

- 프로젝트 범위와 평가 기준 유지
- Workstream·채팅 세션·작업 패키지와 의존 관계 관리
- 작업 채팅이 제출한 `READY_FOR_REVIEW` 작업 패키지 검토
- 변경 diff, 테스트, 데이터 분류와 근거의 독립 검증
- Cross-Workstream 계약 불일치 탐지
- `ROADMAP.md`, `CHECKLIST.md`와 각 `CURRENT.md`의 상태 정합성 유지
- 검증된 변경만 Git commit·push
- 통합 실패 또는 증거 부족 시 `HOLD`

## Control Tower가 소유하는 파일

- `PROJECT_OVERVIEW.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- `docs/workstreams/README.md`
- `docs/workstreams/00-control-tower/`
- 프로젝트 공통 `AGENTS.md`와 통합 규칙

다른 Workstream의 구현 파일은 검토할 수 있지만 대규모 구현을 직접 떠맡지 않는다. 수정이 필요하면 해당 Workstream에 구체적인 작업 패키지로 돌려보내는 것을 우선한다.

## 독립 검증 원칙

- 작업 채팅의 `PASS` 주장이나 화면 설명만 신뢰하지 않는다.
- 실제 파일, diff, 스키마, 테스트 명령과 결과를 직접 확인한다.
- `PUBLISHED`, `CALCULATED`, `ASSUMED`, `SYNTHETIC`, `CUSTOMER_VERIFIED`를 혼동하지 않는다.
- 계산은 동일 입력으로 재현하고 출처는 원문 위치까지 추적한다.
- 누락·오염·충돌 데이터에서 낙관적 판정을 허용하지 않는다.
- 주요 신뢰성 목표는 False PASS 0건이다.

## Git 책임

Control Tower는 다음 조건을 모두 충족할 때 검증된 변경을 commit·push할 수 있다.

1. Git 저장소와 현재 브랜치·원격 저장소가 확인됐다.
2. 변경 범위와 소유 채팅·작업 패키지가 명확하다.
3. 사용자 작업이나 다른 채팅의 미완료 변경을 침범하지 않는다.
4. 관련 테스트·검증이 성공했다.
5. 비밀정보, 고객 원문, 대용량 파일과 합성·실제 데이터 오표시가 없다.
6. `CURRENT.md`와 체크리스트 상태가 실제 결과와 일치한다.

### 금지 사항

- 검증 실패 상태에서 commit·push
- 사용자 승인 없는 force push
- `git reset --hard` 또는 사용자 변경 삭제
- 다른 채팅의 변경을 임의로 수정·포함
- 원격 저장소가 없을 때 임의로 새 원격 생성
- 실제 데이터와 합성 데이터를 섞은 채 통합

## 검토 결과

Control Tower는 각 검토를 다음 중 하나로 종료한다.

- `VERIFIED`: 개별 산출물 검증 완료
- `INTEGRATED`: 기준 브랜치 반영 후 상위 흐름까지 검증 완료
- `CHANGES_REQUESTED`: 수정 가능한 구체적 문제 존재
- `HOLD`: 증거·권한·외부 조건이 부족함

## 검증 후 자동 후속 절차

Control Tower는 작업 패키지를 독립 검증한 뒤 별도 요청을 기다리지 않고 다음 절차를 수행한다.

- 검증 실패: 해당 `CURRENT.md`를 `CHANGES_REQUESTED`로 갱신하고 commit·push를 보류하며, 현재 작업 채팅에 전달할 change request Markdown을 기본 Downloads 폴더에 생성하거나 갱신한다.
- 검증 통과: 해당 `CURRENT.md`와 검증된 체크리스트를 동기화하고, 소유 범위가 확인된 변경만 로컬 통합 대상으로 묶는다. 검증 통과만으로 현재 채팅을 종료하거나 다음 세션을 시작하지 않는다.
- GitHub push는 개별 소규모 검토마다 수행하지 않는다. Stage 통합, 주요 기능 기준선, 여러 검증 변경의 묶음, 명시적인 사용자 요청처럼 의미 있는 변동이 있을 때만 검증된 commit을 모아 push한다.
- 작은 문서 동기화나 중간 검증 기록은 다음 주요 통합까지 로컬 변경 또는 로컬 commit으로 유지할 수 있다. push 전에는 누적된 전체 범위와 테스트를 다시 확인한다.
- 같은 Workstream의 새 채팅은 다음 1단위 번호로, 다음 Workstream의 첫 채팅은 해당 십 단위 번호로 시작한다. 새 채팅이 실제로 필요할 때만 기본 Downloads 폴더에 템플릿을 생성하며, 템플릿과 change request는 프로젝트 저장소에 포함하지 않는다.
- 새로 생성하는 모든 채팅 시작 템플릿에는 `SPECTRA_<채팅번호>_<작업패키지>_HANDOFF_HNN.md` 형식의 제출 파일명을 명시한다. `HNN`은 handoff 제출 회차일 뿐 채팅 번호가 아니며, 기존 채팅 00~40의 번호 없는 handoff는 그대로 둔다.
- commit·push 전에는 현재 브랜치, 원격, staging 범위, 비밀정보·대용량 원문과 테스트 결과를 다시 확인한다.

## 완료 정의

Control Tower의 성공은 많은 커밋을 만드는 것이 아니라 다음을 유지하는 것이다.

- 현재 체크리스트가 실제 프로젝트 상태와 일치한다.
- 모든 통합 결과를 재현할 수 있다.
- 어느 채팅과 작업 패키지가 어떤 계약과 파일을 책임지는지 명확하다.
- 실패한 작업이 최종 PASS나 완료 표시로 넘어오지 않는다.
