# WS10 Contract Change Decision H01

## 결정

`APPROVE_MINIMAL_RECEIPTS / DEFER_FULL_PART_V2`

Workstream 80이 Workstream 31·40의 현재 결과를 test module import 없이 표시할 수 있도록 두 개의 독립적인 readiness receipt v1만 공통 계약으로 추가한다.

- `ENVIRONMENT_ISSUANCE_READINESS_RECEIPT 1.0.0`
- `PART_TEST_EVIDENCE_READINESS_RECEIPT 1.0.0`

기존 `RADIATION_ENVIRONMENT`와 `PART_TEST_EVIDENCE` v1 schema, EvidencePacket 1.0/1.1, semantic validator와 simulation engine은 변경하지 않는다. 전체 `PART_TEST_EVIDENCE 2.0.0` 구현은 이번 결정에 포함하지 않는다.

## 최소 계약 경계

두 receipt는 upstream 평가 결과의 상태와 blocker를 전달하는 비결정용 envelope다.

- `assurance_decision`은 항상 `HOLD`다.
- `used_for_decision`은 항상 `false`다.
- 현재 HOLD 상태는 blocker가 최소 1개이고 output reference를 가질 수 없다.
- receipt v1은 `ISSUED` 또는 `RECORD_VALIDATED`를 표현하지 않는다. 실제 output이 생기면 content-addressed reference와 production validator identity를 포함한 새 receipt version을 승인해야 한다.
- receipt에는 dose, cross section, 시험 수치, suitability, 권리 승인 또는 실제 evidence 본문을 넣지 않는다.
- Product는 receipt를 readiness 표시와 gap 설명에만 사용하고 EvidencePacket decision input으로 사용하지 않는다.

## Environment receipt

WS31 H06의 deployment trust-store 결과를 다음 필드로 투영한다.

- upstream gate version과 evidence class
- 목표 `RADIATION_ENVIRONMENT` schema identity
- `issuance_status`, `processing_status`, stable blocker codes
- H06 범위의 `HOLD_NOT_ISSUED` 상태만 허용한다. receipt v1은 source class와 무관하게 blocker가 최소 1개여야 하며 `ISSUABLE_CANDIDATE`를 표현하지 않는다. 향후 candidate 지원은 인증된 output binding을 가진 새 receipt version에서만 승인한다.

현재 실제 private review는 `HOLD_NOT_ISSUED`, `PROVENANCE_FAILURE`, output reference 없음으로만 표현할 수 있다. 이 receipt가 환경 contract 발행이나 과학적 검증을 대신하지 않는다.

## Parts receipt와 v2 결정

WS40 H06 test gate 결과를 다음 필드로 투영한다.

- test gate version과 `DISCOVERY_CANDIDATE/DEMO_ONLY` purpose
- 목표 `PART_TEST_EVIDENCE 2.0.0` 및 implementation status
- processing, identity, applicability 상태와 blocker codes
- H06 test gate 범위의 `CONTRACT_NOT_IMPLEMENTED/NOT_IMPLEMENTED` 상태만 허용한다.

현재 공통 `PART_TEST_EVIDENCE 2.0.0` schema는 구현하지 않는다. H06 test module은 production runtime이나 Product에서 import하면 안 된다. 따라서 현재 receipt는 `CONTRACT_NOT_IMPLEMENTED`, output reference 없음으로 닫힌다.

전체 v2는 BOM approval projection, typed locator와 rights, artifact/content/approval/history hash, event별 condition/result, structured applicability 및 non-filling migration을 함께 구현·검증할 수 있는 별도 통합 단위에서만 승인한다. 일부 필드만 additive하게 v1에 넣는 방식은 dual truth와 False PASS 위험 때문에 거부한다.

## Version dispatch와 호환성

`schemas/readiness-receipt.schema.json`이 kind별 v1 schema를 `oneOf`로 dispatch한다. 각 leaf schema는 `contract_version=1.0.0`을 고정하고 unknown version과 cross-kind field를 fail closed로 거부한다.

이 변경은 기존 schema를 참조하거나 수정하지 않는 additive contract다. 따라서 v1 packet과 기존 engine 동작은 보존된다. 향후 receipt v2는 기존 leaf schema를 변경하지 않고 새 version leaf와 dispatcher branch로 추가한다.

## Downstream 사용 조건

Workstream 80은 다음 조건에서만 연결할 수 있다.

1. 공통 dispatcher로 schema validation한다.
2. 알 수 없는 kind/version과 v1이 지원하지 않는 성공 상태는 표시하지 않고 `HOLD/DATA_UNAVAILABLE`로 닫는다.
3. output reference가 없는 receipt에서 환경 수치나 부품 시험 수치를 추론하지 않는다.
4. receipt의 `assurance_decision=HOLD`, `used_for_decision=false`를 변경하거나 실제 assurance로 확대하지 않는다.
5. upstream 전용 test module을 import하지 않는다.

## 검증 범위

- 두 현재 HOLD fixture의 dispatcher validation
- unknown version과 cross-kind field 거부
- HOLD receipt의 output reference 주입 거부
- v1 미지원 성공 상태와 output reference 주입 거부
- assurance 또는 decision-use 승격 거부
- 기존 schema direct validation으로 v1 기준선 보존 확인

실제 evidence, 실제 contract 발행, 권리, 과학적 정확성 또는 부품 suitability는 평가하지 않는다.
