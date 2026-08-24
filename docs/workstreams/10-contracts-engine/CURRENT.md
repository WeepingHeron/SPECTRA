# Workstream 10 — Contracts & Engine Current

## 상태

`VERIFIED — readiness receipt v1 integration unit`

## 현재 변경

WS31 H06와 WS40 H06의 결과를 WS80이 test module import 없이 소비할 수 있도록 additive readiness receipt 계약 2개와 version dispatcher를 추가했다.

- Environment issuance readiness receipt v1
- Part Test Evidence v2 readiness receipt v1
- 두 현재 상태용 synthetic/HOLD fixture
- version dispatch와 fail-closed 공격을 검증하는 direct schema test

기존 EvidencePacket 1.0/1.1, `RADIATION_ENVIRONMENT`, `PART_TEST_EVIDENCE` v1, common semantic validator와 simulation engine은 변경하지 않았다.

## 결정 경계

전체 `PART_TEST_EVIDENCE 2.0.0` production schema는 아직 `NOT_IMPLEMENTED`다. 이번 receipt는 그 사실과 upstream readiness만 전달하며 evidence 본문·수치·승인·권리·suitability를 생성하지 않는다. 모든 receipt는 `assurance_decision=HOLD`, `used_for_decision=false`다.

상세 결정: `docs/workstreams/10-contracts-engine/CONTRACT_CHANGE_DECISION_H01.md`

## 검증

- direct readiness receipt schema tests: 8/8 통과
- 기존 schema direct validation: schema 17, 정상 fixture 5, 실패 fixture 116 통과
- `git diff --check`: 통과
- 최종 통합 회귀: simulation 55, Product 17, GCP 12와 readiness 인접 회귀 전체 통과

## 다음 Gate

Control Tower가 schema diff, version dispatch, optimistic mutation attacks와 v1 보존을 독립 재검증했다. Environment의 actual/synthetic 낙관 승격과 Parts의 미구현 contract 승격은 모두 schema에서 거부되며 통합 범위는 readiness receipt에 한정한다.

Control Tower 공격 검토에서 발견된 낙관 조합을 수정했다. Environment receipt v1은 actual/synthetic 구분 없이 `HOLD_NOT_ISSUED`와 blocker 최소 1개만 허용한다. 따라서 `ACTUAL_REVIEW` 또는 `SYNTHETIC_CONTROL + ISSUABLE_CANDIDATE + VALID + blockers=[]`가 모두 거부된다. Parts receipt v1은 `W40_TEST_CONTRACT + HOLD_NOT_READY + IMPLEMENTED`도 거부한다.
