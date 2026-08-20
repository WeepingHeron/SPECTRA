# 40 Parts Evidence — Workstream Brief

## 역할

Parts Evidence Workstream은 BOM의 실제 부품과 공개·승인된 방사선 시험 원문을 연결하고, TID·SEU·SEL·SEB·SEGR 증거를 시험 조건과 원문 위치까지 추적 가능한 후보 레코드로 정규화한다. 이 Workstream은 부품의 비행 적합성을 인증하거나, 유사 부품·검색 결과·제조사 일반론을 정확한 부품 시험 증거로 승격하지 않는다.

## 현재 작업 패키지

- 작업 패키지: `40-parts-evidence-contract-and-adversarial-fixture-spec-v1`
- 세션: `40-parts-evidence`
- 목표: 실제 BOM·원문을 만들지 않고 Workstream 10과 60이 구현할 수 있는 `PART_TEST_EVIDENCE v2`, 호환성, 결정론적 identity 판정과 공격 fixture 명세를 확정한다.
- 기준선: `ed4e0f8`에 통합된 직전 Workstream 40 조사 패키지, `INTEGRATED` Stage 1 EvidencePacket 계약, 통합된 Stage 2 합성 기준선과 Stage 3 조사 계약을 사용한다.
- 비의존 범위: 미검증 실제 시험값과 아직 구현되지 않은 Stage 3 실제 SEE 환경 출력

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

- 필드별 `required / optional / conditional / forbidden` 규칙이 구현 가능한 수준으로 기록됐다.
- additive 확장과 `PART_TEST_EVIDENCE v2`의 호환성·migration·False PASS 위험을 비교하고 권고안을 선택했다.
- `EXACT_MATCH`, `PARTIAL_UNRESOLVED`, `CONTRADICTED`, `FAMILY_ONLY`의 결정론적 우선순위와 종료 상태가 있다.
- TID·SEU·SEL·SEB·SEGR별 최소 필드, 금지 대체와 누락 시 종료 상태가 분리됐다.
- identity·사건 유형·범위·provenance·review 공격 fixture가 입력 변이, 기대 오류 코드와 안전 종료 상태까지 명세됐다.
- Workstream 10·30·50·60·70의 입력·출력 계약과 Exit Gate가 기록됐다.
- evidence content, approval target, review history entry의 hash projection이 자기참조 없이 분리되고 canonicalization·검증 순서·supersedes 규칙이 있다.
- exact PN 미확인 family 후보, exact PN 미보고 unresolved 후보와 verified exact PN conflict가 schema-valid한 서로 다른 상태로 도달한다.
- `CONFLICTING` claim은 최소 두 개의 서로 다른 값·source claim identity·유효 locator를 보존하며 decision에 사용되지 않는다.
- H02 정상·공격 fixture가 content/history 변조, family/unresolved/conflict 상태와 conflicting alternative 위반을 각각 검증한다.
- 실제 BOM·시험 수치·가짜 hash·가짜 locator·임의 confidence를 만들지 않았다.
- 작업 채팅은 `READY_FOR_REVIEW`까지만 요청하며 commit·push하지 않는다.
