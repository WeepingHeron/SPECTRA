# 20 Simulation Core — Workstream Brief

## 역할

Simulation Core Workstream은 SPECTRA의 결정론적 TID·SEE 계산, 완화 전후 비교, 합성 기준선과 재현 테스트를 소유한다. 실제 환경값이나 시험값을 만들지 않으며, 합성 수치 결과를 방사선 보증 판정으로 승격하지 않는다.

## 책임 범위

- Stage 1 EvidencePacket 입력 검증
- 합성 TID·SEE 계산 모듈 분리
- 차폐·기간·ECC·사용자 정책 비교
- 시험범위·파괴성 SEE·정책 승인 fail-closed rule
- 결과 JSON Schema와 EvidencePacket 출력
- 동일 입력 재현성, 범위 밖 입력과 False PASS 테스트
- 한 명령 검증과 비교 CLI
- Workstream 50의 v2 ECC·정책 계약을 사용하는 baseline/variant MVP Decision Engine
- 입력·출력·판정 차이, 무효화 근거와 blocking gap을 보존하는 machine-readable Change Impact

## 소유 파일

- `src/spectra_sim/`
- `simulation/`
- `tests/simulation/`
- `docs/workstreams/20-simulation-core/`

루트 문서, Workstream 10 계약과 Control Tower 문서는 읽기 전용 의존성이다. 체크리스트 완료, `VERIFIED`, `INTEGRATED`, commit·push는 Control Tower가 담당한다.

## 의존 관계

- Workstream 10의 7종 입력·EvidencePacket·상태·provenance 계약을 소비한다.
- Workstream 30은 합성 TID lookup을 실제 환경·차폐 모델 출력으로 교체한다.
- Workstream 40은 합성 부품 시험값을 실제 원문 추적 증거로 교체한다.
- Workstream 50은 현재 최소 정책 rule을 승인된 완화·조직 정책 엔진으로 확장한다.
- Workstream 60은 합성 False PASS 세트와 계산 재현성을 독립 검증한다.

## 검증 명령

```bash
python3 tests/simulation/run_all.py
```

성공하더라도 Workstream 20의 작업 채팅은 `READY_FOR_REVIEW`까지만 선언한다.
