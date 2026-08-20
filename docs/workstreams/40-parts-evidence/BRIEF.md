# 40 Parts Evidence — Workstream Brief

## 역할

Parts Evidence Workstream은 BOM의 실제 부품과 공개·승인된 방사선 시험 원문을 연결하고, TID·SEU·SEL·SEB·SEGR 증거를 시험 조건과 원문 위치까지 추적 가능한 후보 레코드로 정규화한다. 이 Workstream은 부품의 비행 적합성을 인증하거나, 유사 부품·검색 결과·제조사 일반론을 정확한 부품 시험 증거로 승격하지 않는다.

## 현재 작업 패키지

- 작업 패키지: `40-parts-evidence-first-exact-part-evidence-path-v1`
- 세션: `40-parts-evidence`
- 목표: MVP 기준 사례 후보로 공개적으로 식별 가능한 exact orderable part 1개를 선택하고, 공식 원문의 locator·권리 상태·시험 조건을 보존한 첫 TID 또는 SEE 정규화 경로를 만든다.
- 기준선: Workstream 40 조사·계약 명세 통합 commit `4bd1362`와 Control Tower 기록 commit `cf4200d`; 현재 공통 v1 schema와 raw artifact manifest v2 계약을 읽기 전용으로 대조한다.
- 비의존 범위: 승인 BOM, 미확인 상업 이용권, 승인 storage, 미구현 `PART_TEST_EVIDENCE v2`, 아직 연결되지 않은 Stage 3 임무 환경

## 소유 범위

- `docs/workstreams/40-parts-evidence/BRIEF.md`
- `docs/workstreams/40-parts-evidence/CURRENT.md`
- `docs/workstreams/40-parts-evidence/RESEARCH.md`

공통 `schemas/`, `docs/contracts/`, 루트 문서, 다른 Workstream 파일은 읽기 전용이다. 실제 시험 PDF, 고객 문서, 대용량 원문은 프로젝트 저장소에 넣지 않는다.

## 신뢰 경계

- 공식 데이터베이스는 후보 탐색 경로이며, 개별 보고서의 정확한 식별자·시험 조건·원문 위치가 확인돼야만 증거 후보가 된다.
- 공개 접근은 저장·재배포·상업 이용 권한을 자동으로 의미하지 않는다.
- TID, SEU, SEL, SEB, SEGR은 독립된 증거 유형으로 보존한다.
- `SYNTHETIC`, 검색 스니펫, 카탈로그 행, 부품군 자료는 실제 시험 수치가 아니다.
- 누락·충돌·범위 밖·권리 미확인·미승인 추출은 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`를 만든다.
- 결정론적 식별·적용성 gate가 판정하며 LLM은 후보 탐색·구조화·설명만 담당한다.

## 이번 패키지 Exit Gate

- exact orderable PN, 제조사, package와 grade가 공식 제조사 페이지와 시험 보고서에서 교차 확인됐다. 승인 BOM과의 `EXACT_MATCH`는 별도 gate로 남긴다.
- 최소 한 사건 유형의 claim이 report ID, 원문 페이지·절·표, 시험 조건과 실제 관찰값까지 역추적된다.
- TID·SEU·SEL·SEB·SEGR을 독립 상태로 유지하며 선택한 원문이 다루지 않는 사건 유형을 `NOT_REPORTED_IN_SELECTED_BUNDLE`로 표시한다.
- 공개 열람·locator 공유와 fetch·private storage·AI processing·내외부 표시·재배포·상업 이용을 분리한다.
- 원문은 Git에 넣지 않고, 실제 관찰 hash와 manifest 생성 차단 사유 및 작은 v2 정규화 후보만 문서로 제안한다.
- 원문 내부 충돌, BOM 부재, 권리 snapshot 부재, 임무 적용성 미확인은 support decision을 만들지 않고 `HOLD`로 끝난다.
- 현재 v1 schema에 맞추기 위해 미보고 시험일·온도·facility를 발명하지 않는다.
- 작업 채팅은 `READY_FOR_REVIEW`까지만 요청하며 commit·push하지 않는다.
