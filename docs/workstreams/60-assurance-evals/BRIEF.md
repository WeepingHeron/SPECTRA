# 60 Assurance & Evals — Workstream Brief

## 역할

Assurance & Evals Workstream은 구현팀의 PASS 주장이나 정상 walkthrough를 승인 근거로 사용하지 않는다. 현재 통합된 schema·semantic gate와 결정론적 계산 경로를 독립 fixture로 변조하고, 누락·오염·충돌 입력이 낙관 판정으로 종료되는지 재현한다.

## 책임 범위

- v1/v2 version boundary와 downgrade 공격
- 합성·가정 입력의 지원 판정 승격 공격
- exact part/process/die/lot identity 불일치
- TID·SEE 단위, 시험 범위와 파괴성 SEE 증거 gate
- raw artifact generation·SHA-256·rights reference lineage
- 사용자 정책 승인·scope와 완화 failure-mode mapping
- 계산·증거·정책 결과 상충
- Workstream 20 MVP Decision Engine의 입력 gate, 정책·증거 gate와 Change Impact 후조건 공격
- 고정 공격 세트의 False PASS와 결정론적 재현성 보고
- 미구현 engine·실제 원문·GCP 상태를 `NOT_EVALUATED`로 분리

## 평가 profile

- **Core profile:** schema·provenance·exact identity·TID/SEE·차폐·ECC·판정 기준·Change Impact 공격. 제품과 발표의 핵심 신뢰성 근거다.
- **Experimental runtime profile:** WATCHDOG·TMR·SEL protection 공격. 과거 검증을 보존하지만 Core 공격 수와 합치지 않는다.
- **Deployed GCP profile:** 실제 Cloud Storage generation·SHA-256·IAM·Agent 경계와 E2E 결과를 공격한다. 로컬 synthetic receipt로 통과 처리하지 않는다.

## 소유 파일

- `docs/workstreams/60-assurance-evals/`
- `tests/assurance/`

공용 schema, `src/spectra_sim/`, 기존 schema/simulation 테스트와 루트 문서는 읽기 전용이다. 실제 결함은 우회 수정하지 않고 재현 fixture와 `CHANGES_REQUESTED` 후보로 전달한다. commit·push와 `CHECKLIST.md` 완료 표시는 Control Tower가 담당한다.

## 판정 계약

- 평가 가능한 공격은 기대 코드 또는 안전한 `HOLD`/`OUT_OF_MODEL_SCOPE`/`NOT_EVALUATED` 결과와 일치해야 한다.
- 오염 입력의 무오류 수락, `SUPPORTED_WITH_MITIGATION`, `CONDITIONAL` 또는 기대하지 않은 계산 PASS는 False PASS 후보다.
- 의존성이 없는 항목만 False PASS 분모에 포함한다.
- “False PASS 0”은 `tests/assurance/manifest.json`에 고정된 평가 가능 공격에만 적용한다.
- runner는 machine-readable JSON을 출력하고 mismatch나 False PASS에서 비정상 종료한다.

## 검증 명령

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py
git diff --check
```

작업 채팅은 검증 후에도 `READY_FOR_REVIEW`까지만 선언한다.
