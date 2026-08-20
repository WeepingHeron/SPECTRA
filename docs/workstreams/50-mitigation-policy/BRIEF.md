# 50 Mitigation & Policy — Workstream Brief

## 역할

Workstream 50은 완화 구조와 사용자 정책을 **고장 유형별 결정론적 입력·판정 계약**으로 만든다. 완화 방법의 존재, 계산 가능한 효과, 정책 통과를 서로 분리하며 LLM이 완화율이나 최종 판정을 생성하지 못하게 한다.

현재 Stage 3의 실제 환경·차폐 출력과 Stage 4의 승인 BOM·실제 시험 증거가 없으므로, 이번 패키지는 계약 조사와 설계 명세까지만 제공한다. Stage 5 구현 완료, 실제 완화 효과, 비행 적합성 또는 `SUPPORTED_WITH_MITIGATION`은 주장하지 않는다.

## 이번 범위

- 차폐, 부품 대체, ECC, scrubbing, TMR, watchdog/reboot, checkpoint/retry, SEL current limiting/power cycling, spare switching의 failure-mode 경계
- 완화별 입력·출력·단위·계산식 또는 계산 불가 조건
- TID design factor, residual SEU, downtime/reboot, destructive SEE 요구의 정책 계약
- 조직 기본 policy pack, custom exception, 승인·폐기·대체 이력
- `PUBLISHED`, `CALCULATED`, `ASSUMED`, `SYNTHETIC`, `CUSTOMER_VERIFIED`의 판정 사용 조건
- 정상·누락·오염·정책 우회·failure-mode substitution 공격 fixture 명세
- Workstream 10·20·40·60 전달 요구사항

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
5. watchdog, reboot, checkpoint, retry, spare switching은 사건 발생 자체가 아니라 복구·가용성에 영향을 준다.
6. SEL current limiting/power cycling은 SEL 검출·차단·복구·잠재 손상 시험이 확인된 범위에서만 인정한다.
7. `ASSUMED` 또는 `SYNTHETIC` 입력·정책·계수는 engineering comparison은 만들 수 있어도 최종 지원 판정에는 사용할 수 없다.
8. 정책 승인과 데이터 provenance는 독립 축이다. `APPROVED` 문자열은 합성·가정 값을 증거로 승격하지 않는다.
9. Stage 3·4 필수 입력이 없으면 placeholder를 만들지 않고 `NOT_EVALUATED`와 `HOLD`/`INSUFFICIENT_EVIDENCE`를 반환한다.
10. watchdog와 SEL protection의 false activation/trip을 검증된 0으로 간주하지 않으며 true/false 경로를 count와 downtime에 모두 합산한다.
11. TMR 제한식 `3p²-2p³`의 출력은 동일 평가 window의 `system_failure_probability`이며 success probability, reliability, availability로 이름을 바꾸지 않는다.

## Exit Gate 해석

이번 산출물의 Exit Gate는 다음 계약이 서로 모순 없이 문서화되는 것이다.

- 완화 전·후 값과 계산 provenance가 분리됨
- 각 완화가 영향 주는 failure mode와 영향 주지 않는 mode가 명시됨
- 미승인·합성·가정 정책으로 지원 판정을 만들 수 없음
- destructive SEE 공백을 비파괴성 완화로 숨길 수 없음
- 근거 없는 계수와 아직 없는 Stage 3·4 입력이 `ASSUMED/HOLD`에 남음
- watchdog true/false activation이 같은 window에서 별도 계산되고 reboot·downtime에 합산됨
- TMR 제한식의 failure probability 의미와 `p=0`, `0.1`, `1` 경계가 고정됨

상태 선언은 `READY_FOR_REVIEW`까지만 한다. checklist, commit, push는 수행하지 않는다.
