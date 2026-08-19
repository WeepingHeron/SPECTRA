# 10 Contracts & Schema — Workstream Brief

## 역할

Contracts & Schema Workstream은 SPECTRA의 입력·출력·EvidencePacket·상태·단위·실패 계약을 소유한다. 계산값을 만들거나 방사선 적합성을 인증하지 않고, 다른 Workstream이 교환할 데이터를 기계 검증 가능하게 제한한다.

## 책임 범위

- 5종 데이터 분류와 provenance 필드
- 작업 검토·방사선 보증·처리 범위 상태의 분리
- Mission, BOM, Radiation Environment, Part Test Evidence, Shielding, Mitigation, User Policy 입력
- EvidencePacket의 입력·origin·정규화·적용성·규칙·판정·공백 추적
- 단위 호환성과 fail-closed 의미 규칙
- 정상·누락·오염·충돌 fixture와 단일 검증 명령

## 소유 파일

- `schemas/`
- `docs/contracts/`
- `docs/workstreams/10-contracts-schema/`
- `tests/schema/`

루트 `PROJECT_OVERVIEW.md`, `ROADMAP.md`, `CHECKLIST.md`와 Control Tower 문서는 읽기 전용 의존성이다. 완료 처리와 Git 반영은 Control Tower가 담당한다.

## 의존 관계

- Workstream 20 Simulation Core는 합성 입력·출력과 판정에 이 계약을 사용한다.
- Workstream 30 Environment Model은 모델 실행과 단위 provenance를 제공한다.
- Workstream 40 Parts Evidence는 정확한 부품 식별자와 원문 위치를 제공한다.
- Workstream 50 Mitigation & Policy는 승인 정책과 결정론적 규칙을 구체화한다.
- Workstream 60 Assurance & Evals는 의미 규칙과 False PASS fixture를 독립 검증한다.

## 검증 명령

```bash
python3 tests/schema/validate_contracts.py
```

성공 출력은 스키마 수, 정상 fixture 수, 기대 코드로 거부된 실패 fixture 수를 각각 표시해야 한다. 작업 세션은 성공 후에도 `READY_FOR_REVIEW`까지만 선언한다.
