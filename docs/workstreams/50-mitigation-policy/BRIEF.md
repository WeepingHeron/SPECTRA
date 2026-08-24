# 50 Mitigation & Policy — Workstream Brief

## 역할

Workstream 50은 SPECTRA Core가 직접 사용하는 차폐·ECC 가정과 최소 판정 기준을 **결정론적 입력·판정 계약**으로 만든다. LLM이 완화율이나 최종 판정을 생성하지 못하게 한다.

현재 Stage 3의 실제 환경·차폐 출력과 Stage 4의 승인 BOM·실제 시험 증거가 없으므로, 이번 패키지는 계약 조사와 설계 명세까지만 제공한다. Stage 5 구현 완료, 실제 완화 효과, 비행 적합성 또는 `SUPPORTED_WITH_MITIGATION`은 주장하지 않는다.

## 현재 활성 범위

- 차폐, 부품 대체와 ECC의 failure-mode 경계
- 입력·출력·단위·계산식 또는 계산 불가 조건
- TID design factor, residual SEU와 destructive SEE 요구의 최소 판정 계약
- `PUBLISHED`, `CALCULATED`, `ASSUMED`, `SYNTHETIC`, `CUSTOMER_VERIFIED`의 판정 사용 조건
- 정상·누락·오염·범위 밖·failure-mode substitution 공격 fixture 명세
- Workstream 10·20·40·60 전달 요구사항

## 실험 보존 범위

WATCHDOG·TMR·SEL protection, scrubbing, checkpoint/retry와 spare switching의 기존 문서·schema·계산·테스트는 삭제하지 않는다. 다만 실제 시스템 구조가 없는 현재에는 Core Product, Competition Demo 주 흐름, 현재 임무 채택 설계와 핵심 신뢰성 지표에서 제외한다.

## 소유와 비소유

소유 파일:

- `docs/workstreams/50-mitigation-policy/BRIEF.md`
- `docs/workstreams/50-mitigation-policy/RESEARCH.md`
- `docs/workstreams/50-mitigation-policy/CURRENT.md`

공통 schema, `tests/`, 루트 문서, 다른 Workstream 파일은 읽기 전용이다. 이 패키지는 변경 요청을 문서화할 뿐 직접 구현하지 않는다.

## 핵심 안전 규칙

1. 하나의 범용 `effectiveness_factor`로 서로 다른 완화를 계산하지 않는다.
2. ECC·scrubbing·TMR은 SEL·SEB·SEGR 증거를 대체하지 않는다.
3. 차폐 변경은 승인된 환경/수송 모델을 다시 실행하며 이전 선량에 임의 계수를 곱하지 않는다.
4. 부품 대체는 완화율이 아니라 BOM identity와 모든 시험 적용성을 새로 평가하는 입력 변경이다.
5. runtime 완화 결과는 `EXPERIMENTAL` 경계를 벗어나 현재 임무 판정에 사용하지 않는다.
7. `ASSUMED` 또는 `SYNTHETIC` 입력·정책·계수는 engineering comparison은 만들 수 있어도 최종 지원 판정에는 사용할 수 없다.
8. 정책 승인과 데이터 provenance는 독립 축이다. `APPROVED` 문자열은 합성·가정 값을 증거로 승격하지 않는다.
9. Stage 3·4 필수 입력이 없으면 placeholder를 만들지 않고 `NOT_EVALUATED`와 `HOLD`/`INSUFFICIENT_EVIDENCE`를 반환한다.

## Exit Gate 해석

이번 산출물의 Exit Gate는 다음 계약이 서로 모순 없이 문서화되는 것이다.

- 완화 전·후 값과 계산 provenance가 분리됨
- 각 완화가 영향 주는 failure mode와 영향 주지 않는 mode가 명시됨
- 미승인·합성·가정 정책으로 지원 판정을 만들 수 없음
- destructive SEE 공백을 비파괴성 완화로 숨길 수 없음
- 근거 없는 계수와 아직 없는 Stage 3·4 입력이 `ASSUMED/HOLD`에 남음
- 과거 runtime 계약은 실험 보존 범위로 명확히 분리됨

상태 선언은 `READY_FOR_REVIEW`까지만 한다. checklist, commit, push는 수행하지 않는다.
