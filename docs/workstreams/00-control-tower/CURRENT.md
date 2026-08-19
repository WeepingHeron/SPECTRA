# 00 Control Tower — Current State

## Status

`IN_PROGRESS`

## Last verified

- 날짜: 2026-08-19
- 프로젝트 경로: `/Users/taehoon/Desktop/IAA/SPECTRA`
- Git 상태: 로컬 `main`이 비공개 `origin/main`을 추적한다. 루트 README 기준선 `15be27b` 이후 Workstream 30 조사 패키지를 검증했으며, 사용자 소유의 미추적 `.obsidian/`은 통합에서 제외한다.

## 현재 확인된 산출물

- `PROJECT_OVERVIEW.md`
- `ROADMAP.md`
- `CHECKLIST.md`
- `docs/workstreams/README.md`
- `docs/workstreams/00-control-tower/BRIEF.md`
- `docs/workstreams/00-control-tower/CURRENT.md`
- `docs/workstreams/00-control-tower/CONTROL_TOWER_SESSION_TEMPLATE.md`

## 현재 진실

- SPECTRA의 문제·범위·평가 기준 문서는 작성됐다.
- Stage 1~9 로드맵과 단계별 체크리스트가 존재하며, 각 Stage 번호는 주관 Workstream 앞자리와 일치한다.
- 결정론적 합성 TID·SEE 기준선은 Workstream 20이 프로젝트에 통합했고, 모든 결과가 `SYNTHETIC/HOLD`를 유지한다.
- 실제 환경 모델 출력과 실제 부품 시험자료는 아직 수집·검증되지 않았다.
- Multi-Agent·GCP 구현과 배포 증거는 아직 없다.
- 검증된 Stage 1 계약 기준선은 커밋 `303adb9`로 비공개 `origin/main`에 반영됐다. 해당 커밋 메시지의 `Stage 0` 표기는 번호 정렬 이전의 역사적 명칭이다.
- 채팅 세션 10의 Contracts & Schema 작업은 4차 수정 후 독립 재검증과 Git 통합을 완료했다.
- 세션은 실제 채팅방을 뜻한다. Workstream은 십 단위로 구분하고 첫 채팅도 같은 번호를 사용하며, 같은 Workstream에서 새 채팅이 필요할 때만 1단위로 증가한다.
- 잘못된 Control Tower 안내로 채팅 10에서 시작된 Workstream 20 후보는 채팅 20이 소유권을 인수해 보완했고, 번호를 Stage 1 계약 / Stage 2 합성 기준선으로 정렬했다.
- Workstream 20은 독립 재실행으로 schema fixture 28개(정상 1·실패 27), simulation 19개 테스트와 5개 비교 시나리오를 통과했다. 지원 판정 승격·4.1 mm 외삽·비직렬화 입력 공격도 안전하게 `HOLD`로 종료해 합성 기준선 패키지를 `INTEGRATED`로 판정했다.
- Workstream 30의 SPENVIS·OLTARIS 공식 도구·권리 조사와 Stage 3 계약 초안을 독립 대조해 조사 패키지를 `INTEGRATED`로 판정했다. 실제 모델 실행·출력·과학적 교차검산은 0건이며 Stage 3은 `IN_PROGRESS`다.

## 알려진 한계

- 실제 환경 모델·실제 부품 시험자료·과학적 계산 엔진은 아직 없어 실제 방사선 보증을 검증할 수 없다.
- Workstream 10~90의 `BRIEF.md`·`CURRENT.md`는 필요 시 생성해야 한다.
- 병렬 채팅은 같은 파일을 동시에 수정하지 않고 마지막 `INTEGRATED` 기준선만 의존해야 한다.
- Workstream 경계를 넘겨 생성된 산출물은 올바른 십 단위 채팅으로 소유권을 이전하고 다시 `READY_FOR_REVIEW`를 제출해야 한다.

## 다음 권장 작업

1. Workstream 10에 TID-only environment variant, model chain과 raw artifact manifest 계약 변경을 요청한다.
2. 대표 원형 LEO 입력과 AE9/AP9·solar model uncertainty 정책을 승인하기 전 실제 run은 `HOLD`한다.
3. Workstream 40 조사 결과는 별도로 검증하고, 실제 부품 수치나 지원 판정은 아직 만들지 않는다.

## 다음 Control Tower 검증 항목

- 프로젝트 구조가 문서와 일치하는가?
- 작업 채팅이 현재 작업 패키지의 `READY_FOR_REVIEW` 인수인계를 남겼는가?
- 실제 변경과 체크리스트 완료 표시가 일치하는가?
- Git에 올릴 변경만 명확히 분리돼 있는가?
