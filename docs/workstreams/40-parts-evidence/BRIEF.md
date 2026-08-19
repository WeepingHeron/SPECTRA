# 40 Parts Evidence — Workstream Brief

## 역할

Parts Evidence Workstream은 BOM의 실제 부품과 공개·승인된 방사선 시험 원문을 연결하고, TID·SEU·SEL·SEB·SEGR 증거를 시험 조건과 원문 위치까지 추적 가능한 후보 레코드로 정규화한다. 이 Workstream은 부품의 비행 적합성을 인증하거나, 유사 부품·검색 결과·제조사 일반론을 정확한 부품 시험 증거로 승격하지 않는다.

## 현재 작업 패키지

- 작업 패키지: `40-parts-evidence-source-rights-identity-applicability-v1`
- 세션: `40-parts-evidence`
- 목표: Stage 4 구현 전에 출처·권리·부품 식별·시험 유형·적용성·검토 이력 계약을 설계한다.
- 기준선: `INTEGRATED`인 Stage 1 EvidencePacket 계약에 의존하고, 통합된 Stage 2 합성 기준선과 Stage 3 조사 계약을 인터페이스 참고로 사용한다.
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

- 공식 출처별 제공 자료, 접근 방식, 권리 상태와 제약이 출처 URL·접근일과 함께 기록됐다.
- BOM 부재 시 실제 부품을 임의 선정하지 않는 `HOLD` 정책이 있다.
- 정확 일치, 부분 식별, 모순, 부품군 유사성을 구분하는 규칙이 있다.
- TID·SEU·SEL·SEB·SEGR 정규화 필드와 적용성 비교 항목이 분리됐다.
- 원문 위치·해시·검토·승인 이력과 고객 자료 격리 경로가 설계됐다.
- Stage 3·5·6·7 및 공통 schema의 변경 필요성이 기록됐다.
- 실제 시험 수치나 원문 PDF를 저장·판정에 사용하지 않았다.
- 작업 채팅은 `READY_FOR_REVIEW`까지만 요청하며 commit·push하지 않는다.
