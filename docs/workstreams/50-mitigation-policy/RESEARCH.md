# 50 Mitigation & Policy — 계약 조사와 결정론적 설계

## 1. 기술 요약

SPECTRA의 완화 엔진은 “완화를 선택했으므로 위험이 줄었다”가 아니라 **사건 발생률, 논리 오류, 복구 횟수, 장애시간, 파괴성 손상**을 별도 출력으로 계산해야 한다. 동일한 방법도 설계·시험 조건이 없으면 수치화할 수 없으며, 임의의 잔여 계수는 `ASSUMED`로 남고 최종 지원 판정에는 쓰이지 않는다.

NASA의 RHA 지침은 shielding을 TID/TNID, EDAC·scrubbing을 SEU, watchdog/reset을 SEFI, latch-up detection/reset을 일부 SEL, derating을 SEB/SEGR에 연결한다. 또한 SEL 보호회로는 prompt failure와 latent damage에 대해 검증돼야 하며 SEL rate가 높으면 복구 자체가 시스템을 교란할 수 있다고 밝힌다. 이 출처들은 **적용 방향**을 뒷받침하지만 특정 SPECTRA 설계의 수치 효과를 제공하지 않는다.

이번 문서의 식은 엔진 계약이다. 실제 계산 완료를 뜻하지 않는다. Stage 3·4 실제 입력이 없으므로 모든 예시는 `SYNTHETIC` 또는 식별자 수준 명세이며 최종 상태는 `HOLD`다.

## 2. 조사 범위와 출처 사용 원칙

조사일은 2026-08-20이며 NASA·ESA/ESCIES의 공식 문서만 근거로 사용했다.

| 출처 | 이 문서에서 사용하는 근거 | 사용하지 않는 것 |
|---|---|---|
| [NASA NESC-RP-19-01490 Phase II](https://ntrs.nasa.gov/api/citations/20220018183/downloads/20220018183.pdf) | shielding–TID/TNID, EDAC/scrubbing–SEU, watchdog/reset–SEFI, latch-up detection/reset–SEL, redundancy, SEB/SEGR derating의 구분 | 특정 부품의 완화율 또는 SPECTRA 기본 계수 |
| [NASA NESC Technical Bulletin 19-01-1](https://www.nasa.gov/wp-content/uploads/2015/04/techbul_19-01-1_120321-final.pdf) | reparable/irreparable SEE를 availability/reliability에 분리하고 recovery time과 mission mode를 고려해야 함 | 임의의 독립성·수리시간 가정 |
| [NASA SEE Criticality Analysis](https://nepp.nasa.gov/docuploads/6D728AF0-2817-4530-97555B6DCB26D083/seecai.pdf) | SEL current signature, 검출 지연, power cycling, spare switching의 사례별 설계 필요성 | current threshold나 recovery success의 일반값 |
| [NASA/TM-2019-220269](https://ntrs.nasa.gov/citations/20190002742) | upset rate와 recovery time이 중복 avionics의 가용성에 미치는 영향을 모델링해야 함 | SPECTRA 대상 시스템의 실제 고장률 |
| [NASA Reliability Engineers radiation tutorial](https://ntrs.nasa.gov/api/citations/20120011770/downloads/20120011770.pdf) | destructive SEE는 취약 부품·취약 조건 회피가 우선이며 기술·전압·온도·duty cycle·redundancy가 적용성을 좌우함 | 한 시험 조건을 다른 기술·운용 조건으로 외삽 |
| [ESCIES Radiation Standards index](https://escies.org/webdocument/showArticle%3Fid%3D229) | TID/SEE 시험과 ASIC/FPGA 완화가 서로 다른 표준·handbook 범위임 | 표준 목록만으로 개별 설계가 검증됐다는 주장 |

출처가 완화 방법을 권고해도 수치 효과는 `PUBLISHED`가 아니다. 수치가 원문에 있더라도 정확한 부품·설계·조건 적용성을 통과해야 한다.

## 3. 공통 용어와 계산 축

| 축 | 정의 | 대표 단위 |
|---|---|---|
| `incident_events` | 환경과 부품 단면적에서 계산한 완화 전 물리 사건 수/률 | `events/mission`, `events/s` |
| `logical_errors` | ECC/TMR 등 설계 경계를 통과해 사용자 기능에 노출된 오류 | `errors/mission`, `errors/s` |
| `recoveries` | watchdog, reboot, retry, power cycle, spare switch가 실행된 횟수 | `count/mission` |
| `downtime` | 복구와 전환으로 기능이 사용 불가한 누적 시간 | `s/mission` |
| `irreparable_events` | 복구로 제거할 수 없는 destructive SEE 또는 영구 기능 손실 | `events/mission` |
| `TID` | 재료 기준 누적 흡수선량 | `rad(Si)`, `krad(Si)`, `Gy(Si)` |

완화 전 값과 완화 후 값은 같은 필드에 덮어쓰지 않는다. 모든 계산은 `baseline_result_id`, `mitigated_result_id`, `calculation_run`, operand trace를 가진다.

## 4. 완화 방법 × failure mode 매핑

`DIRECT`는 해당 mode의 결정론적 수치 모델 후보, `RECOVERY`는 발생률이 아닌 복구/가용성 영향, `SUBSTITUTION`은 입력 전체 재평가, `CONDITIONAL`은 승인된 물리 모델이 있을 때만, `NONE`은 지원 근거로 사용할 수 없음을 뜻한다.

| 완화 방법 | TID | SEU | SEFI/SET 등 recoverable SEE | SEL | SEB | SEGR | 계약상 핵심 제한 |
|---|---|---|---|---|---|---|---|
| 차폐 변경 | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | 승인된 transport/geometry 재실행이 있을 때만. TID 감소율을 SEE에 복사 금지 |
| 부품 대체 | `SUBSTITUTION` | `SUBSTITUTION` | `SUBSTITUTION` | `SUBSTITUTION` | `SUBSTITUTION` | `SUBSTITUTION` | 새 exact PN/process/die/lot와 event별 증거를 전부 재평가 |
| ECC | `NONE` | `DIRECT` | 제한적 `DIRECT` | `NONE` | `NONE` | `NONE` | codeword·interleave·fault multiplicity·coverage가 필요. destructive SEE 대체 금지 |
| scrubbing | `NONE` | `DIRECT` | config upset에 제한적 `DIRECT` | `NONE` | `NONE` | `NONE` | scrub interval, read/write behavior, accumulation model 필요 |
| TMR | `NONE` | `DIRECT` | `DIRECT/RECOVERY` | `NONE` | `NONE` | `NONE` | 독립 domain, voter, common-mode, repair/scrub 조건 필요 |
| watchdog/reboot | `NONE` | `NONE` | `RECOVERY` | `NONE` | `NONE` | `NONE` | 검출 coverage와 reboot time을 availability에만 반영 |
| checkpoint/retry | `NONE` | `NONE` | `RECOVERY` | `NONE` | `NONE` | `NONE` | 검출된 recoverable computation에만 적용; silent corruption 제외 |
| SEL current limiting/power cycling | `NONE` | `NONE` | `NONE` | `RECOVERY` | `NONE` | `NONE` | 검출전류·trip delay·차단·복구·latent damage 시험 범위 필요 |
| spare switching | `NONE` | `NONE` | `RECOVERY` | 제한적 `RECOVERY` | 제한적 `RECOVERY` | 제한적 `RECOVERY` | 고장률을 낮추지 않음. 독립 전원/제어·공통원인·전환 성공 증거 필요 |

`SEFI/SET`는 현행 Stage 1 `failure_modes` enum에 없지만 watchdog/checkpoint 계약에 필요하다. Workstream 10에는 `SEFI`, `SET`, `FUNCTIONAL_INTERRUPT`, `SILENT_DATA_CORRUPTION`을 최소 검토 요청한다. enum이 확장되기 전에는 문자열을 `SEU`로 대체하지 않고 `SCHEMA_CHANGE_PENDING + HOLD`다.

## 5. 완화 입력·출력·단위·계산 계약

### 5.1 공통 `MITIGATION v2` envelope

| 필드 | 요구 | 의미 |
|---|---|---|
| `mitigation_id`, `schema_version`, `method` | 필수 | 안정 ID와 discriminated method union |
| `component_ids[]`, `architecture_scope` | 필수 | device/board/subsystem/system 적용 범위 |
| `target_failure_modes[]` | 필수 | 영향 주장 mode |
| `excluded_failure_modes[]` | 필수 | 명시적으로 영향 없음인 mode; destructive mode 누락 우회 방지 |
| `design_parameters` | 필수 | method별 typed object; 자유형 map 금지 |
| `effect_model` | 조건부 | `model_id`, version, equation ID, validity domain, input pointers |
| `verification_evidence_ids[]` | 조건부 | 실제 효과를 판정에 쓸 때 필수 |
| `applicability` | 필수 | `APPLICABLE`, `NOT_APPLICABLE`, `UNRESOLVED`와 조건 비교 |
| `metadata` | 필수 | 원본 `data_class`와 source/calculation origin |

현행 v1의 자유형 `parameters`와 범용 `effectiveness_factor`는 research/demo 입력 외에는 decision-ineligible이다. v2에서는 method별 typed parameter와 equation-specific output을 사용한다.

### 5.2 차폐 변경

- 입력: material, areal density 또는 equivalent thickness, 3D/sector geometry reference, component location, environment run, transport model/version, mission duration.
- 단위: `g/cm2` 또는 모델이 승인한 `mm_Al_equivalent`; 임의 상호변환 금지.
- 출력: `dose_before`, `dose_after`, 각 material basis와 `environment_run_id`; SEE를 계산할 때는 particle/energy/LET별 before/after spectrum.
- 계산: `dose_after = approved_transport(environment, geometry, material, location)`. 단순 `dose_before × factor`는 factor의 동일 geometry/energy/material 적용성이 검증된 경우만 허용.
- 계산 불가: 실제 Stage 3 run, geometry, material, 위치, model validity 중 하나라도 없으면 `SHIELDING_TRANSPORT_INPUT_MISSING` 또는 `OUT_OF_MODEL_SCOPE`; `NOT_EVALUATED + HOLD`.

### 5.3 부품 대체

- 입력: old/new BOM identity, quantity, application conditions, 모든 event evidence/applicability, manufacturing-change state.
- 출력: old/new evidence coverage와 각 계산을 별도 run으로 생성한 change impact. 완화 계수 출력 금지.
- 계산: `re_evaluate(new_component, same_mission, same_policy)` 후 판정 차이를 비교한다.
- 계산 불가: exact PN 또는 required process/die/lot, event evidence가 없으면 `REPLACEMENT_IDENTITY_UNRESOLVED`/`REPLACEMENT_EVIDENCE_MISSING`.
- 금지: old part의 cross-section/TID limit/approval을 new part에 복사.

### 5.4 ECC

- 입력: codeword bits, data/parity bits, correctable bit count `c`, detectable bit count `d`, interleave mapping, protected regions, upset multiplicity distribution by codeword, decoder behavior, uncorrectable-error behavior, verification evidence.
- 단위: bit/codeword, codewords, `errors/mission` 또는 `errors/s`.
- 출력: corrected, detected-uncorrectable, silent/uncorrected logical errors를 분리.
- 계산: 각 incident pattern `j`에 대해 검증된 transition probability/count `M[j,outcome]`를 적용해 `residual[outcome] = Σ incident[j] × M[j,outcome]`.
- 계산 불가: raw SEU 총량만 있고 codeword별 multiplicity/interleave/coverage가 없으면 `ECC_FAULT_DISTRIBUTION_MISSING`. 임의 `0.1` 같은 scalar는 `ARBITRARY_MITIGATION_FACTOR`.

### 5.5 Scrubbing

- 입력: memory/configuration size, upset rate의 denominator, scrub interval `τ`, coverage, correction capability, read/write duty, persistent/accumulating fault model, simultaneous/common-mode definition.
- 단위: `s`, bit/device/codeword, `errors/s`.
- 출력: scrub operations, corrected accumulation, uncorrectable accumulation, scrub-induced downtime.
- 계산 후보: 독립 Poisson 가정이 검증된 제한 범위에서 codeword별 `μ = λ_codeword × τ`, `P(K>c)=1-Σ(k=0..c)e^-μ μ^k/k!`; 전체 mission window에 합산한다.
- 계산 불가: 독립성, multiplicity, codeword mapping 또는 `τ`가 없으면 `SCRUB_MODEL_INPUT_MISSING`. Poisson 가정이 단지 `ASSUMED`이면 comparison만 가능하고 최종 support는 `HOLD`.

### 5.6 TMR

- 입력: replica count=3, voter 위치/중복 여부, independent fault domains, common-mode rate, repair/scrub interval, synchronization, protected state/output 범위, verification evidence.
- `p`의 의미: 정확히 정의된 동일 `evaluation_window` 안에서, repair 전에, 같은 failure criterion에 따라 **단일 replica가 실패할 무차원 확률**. `0 ≤ p ≤ 1`이며 window 시작·종료 또는 duration/unit을 함께 기록한다.
- 출력: 제한식의 출력명은 `system_failure_probability`로 고정한다. 단위는 무차원 probability/window이고, “세 독립 replica 중 둘 이상이 같은 evaluation window 안에서 실패할 확률”을 뜻한다.
- 계산 후보: 동일 window에서 replica failure가 독립이고 voter failure와 common-mode failure가 없으며 window 안 repair가 없다는 조건이 검증된 제한 모델만 `system_failure_probability = 3p²(1-p)+p³ = 3p²-2p³`를 사용한다.
- 경계: `p=0 → system_failure_probability=0`, `p=0.1 → 0.028`, `p=1 → 1`.
- 의미 분리: 위 값은 success probability, reliability 또는 availability가 아니다. 같은 binary/exhaustive 제한 모델에서 `system_success_probability = 1 - system_failure_probability`를 별도 출력할 수 있지만 이름과 operand를 보존해야 하며, reliability에는 시간에 따른 survival model, availability에는 repair·downtime state model이 추가로 필요하다.
- 일반 계산: voter/common-mode/repair state를 포함한 명시적 state-transition model.
- 계산 불가: independence, voter susceptibility, common-mode, repair state/window 중 하나라도 없으면 제한식을 실행하지 않고 `TMR_INDEPENDENCE_UNVERIFIED`, `TMR_VOTER_MODEL_MISSING`, `TMR_COMMON_MODE_MODEL_MISSING` 또는 `TMR_REPAIR_WINDOW_MISSING`; `NOT_EVALUATED + HOLD`.

### 5.7 Watchdog/reboot

- 입력: target recoverable modes, `evaluation_window`, protected-unit/watchdog scope, true-event count 또는 rate와 denominator, true-positive detection coverage, false-positive activation count 또는 rate와 denominator, true/false activation별 action-path fractions, detection latency, reset duration, boot/self-test duration, state restoration duration, retry limit, unrecovered fraction.
- 단위: coverage/path fraction은 무차원 `[0,1]`; rate는 `events` 또는 `activations` / (`watchdog`, `protected_unit` 또는 `subsystem`) / time; time은 `s`; 결과는 count/window와 `s/window`. rate의 denominator scope와 evaluation window는 반드시 명시한다.
- 출력: `true_positive_activation_count`, `false_positive_activation_count`, true/false path별 action count, `reboot_count_total`, `downtime_total`, unrecovered event를 분리한다.
- rate 정규화: `N_target(W) = λ_target × denominator_count × W`, `N_false(W) = λ_false_positive × denominator_count × W`. 이미 같은 scope/window의 검증된 count가 주어지면 rate와 중복 사용하지 않는다.
- true 경로: `N_true_activation = N_target(W) × true_positive_coverage`.
- path 경로: 각 class `c ∈ {true,false}`와 action path `j`에 대해 `N[c,j] = N_c_activation × path_fraction[c,j]`. 같은 class의 path fraction 합은 1이어야 하고 각 path의 action과 duration이 명시돼야 한다.
- 합산: `reboot_count_total = Σ_c Σ_(j: action=REBOOT) N[c,j]`; `downtime_total = Σ_c Σ_j N[c,j] × path_duration[c,j]`. true와 false activation은 두 결과에 모두 포함된다.
- 경계 사례: `N_target=0`, 같은 mission window의 `N_false=1`, false path=`REBOOT`, duration=`60 s`, fraction=`1`이면 `reboot_count_total=1`, `downtime_total=60 s`다.
- 계산 불가: target mode 입력, path별 시간/coverage 또는 false-positive count/rate·denominator·window·검증 모델 중 하나라도 없으면 false-positive를 0으로 두지 않고 `WATCHDOG_FALSE_POSITIVE_MODEL_MISSING` 또는 `RECOVERY_MODEL_INPUT_MISSING`; reboot와 downtime은 `NOT_EVALUATED + HOLD`. 검증된 0은 명시적 값과 evidence가 있을 때만 허용한다. SEU/SEL/SEB/SEGR 발생률을 감소시키지 않는다.

### 5.8 Checkpoint/retry

- 입력: detected recoverable job-failure rate, checkpoint interval, checkpoint integrity, rollback time, retry duration, maximum retries, retry success model, idempotency/side-effect policy.
- 단위: `s`, attempts/event, jobs/mission.
- 출력: lost work, retry count, recovered jobs, exhausted retries, downtime.
- 계산: 명시적 retry tree에서 각 path의 count/probability와 duration을 합산한다. 반복 독립 성공확률 모델은 독립성이 검증된 경우만 사용.
- 계산 불가: silent corruption detection, checkpoint integrity 또는 retry outcome model이 없으면 `CHECKPOINT_RETRY_INPUT_MISSING`.

### 5.9 SEL current limiting/power cycling

- 입력: device별 정상/SEL current signature, threshold, tolerance/hysteresis, sensor sampling 또는 analog trip latency, current limit, cutoff delay, off-time, restart time, maximum cycles, protection circuit independence, true SEL detection과 false-trip count/rate·denominator·evaluation window·action path, irradiation test에서 prompt failure·latent damage·post-test electrical 결과.
- 단위: `A`/`mA`, `ms`/`s`, cycles/mission, `events/mission`.
- 출력: detected SEL, missed SEL, `false_trip_count`, true/false path별 power cycle, `power_cycle_count_total`, `downtime_total`, unrecovered/latent-damage status.
- 계산: watchdog와 같은 true/false path 합산 계약을 사용한다. 검증된 조건 범위에서만 각 path의 `count × (trip_delay + off_time + restart_time)`을 합산하며 survival/recovery는 시험 기반 transition만 사용한다.
- 계산 불가: current signature, trip delay, recovery, latent-damage evidence 또는 false-trip count/rate·denominator·window·검증 모델이 없으면 누락값을 0으로 두지 않고 `SEL_PROTECTION_NOT_VALIDATED` 또는 `SEL_FALSE_TRIP_MODEL_MISSING`; false-trip과 total power-cycle/downtime은 `NOT_EVALUATED + HOLD`. 단순 power cycle 가능성은 destructive SEE evidence gap을 닫지 않는다.

### 5.10 Spare switching

- 입력: active/spare topology, cold/warm/hot state, independent power/control/clock, common-cause groups, spare exposure/dose, failure detection coverage, switch time, switch success, maximum switches, state synchronization.
- 단위: count, probability, `s/switch`, availability fraction.
- 출력: switch count, recovered service, exhausted spares, downtime, remaining redundancy state.
- 계산: 명시적 reliability/availability state machine으로만 수행한다. component incident rate는 그대로 보존한다.
- 계산 불가: independence/common cause, dormant spare susceptibility, transition success가 없으면 `SPARE_INDEPENDENCE_UNVERIFIED`.

## 6. 정책 pack 계약

### 6.1 `POLICY_PACK v2`

| 필드 | 요구 | 규칙 |
|---|---|---|
| `policy_pack_id`, `version`, `organization_id` | 필수 | immutable identity; 수정은 새 version |
| `scope` | 필수 | mission class, subsystem, component technology/function, valid time |
| `inherits_from` | 선택 | 정확한 parent version/hash; 순환 금지 |
| `rules[]` | 필수 | typed rule union과 단위·비교 연산자 |
| `approval_status` | 필수 | `DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `REVOKED`, `SUPERSEDED` |
| `approval_target_sha256` | 승인 시 필수 | policy content + scope + parent + rule projection |
| `approval_history[]` | 필수 | actor, role, action, timestamp, reason, previous hash, entry hash |
| `valid_from`, `valid_until` | 승인 시 필수 | 평가 시각이 범위 안이어야 함 |
| `metadata` | 필수 | provenance data class와 source/customer approval origin |

정책 rule 최소형:

- `TID_DESIGN_FACTOR`: dimensionless, `>= 1`.
- `MINIMUM_TID_MARGIN`: `rad(Si)`/`krad(Si)` 또는 ratio. 단위를 섞지 않는다.
- `MAXIMUM_RESIDUAL_SEU`: `errors/mission` 또는 `errors/s`; denominator/time window 필수.
- `MAXIMUM_PROBABILITY_AT_LEAST_ONE_SEU`: `[0,1]`, mission window와 계산 model ID 필수.
- `MAXIMUM_REBOOT_COUNT`: count/mission.
- `MAXIMUM_DOWNTIME`: `s/mission` 또는 availability fraction.
- `REQUIRED_EVENT_EVIDENCE`: SEL·SEB·SEGR을 각각 `REQUIRED`, `NOT_REQUIRED_WITH_APPROVED_RATIONALE`, `OUT_OF_TECHNOLOGY_SCOPE` 중 하나로 표현.
- `MAXIMUM_RECOVERY_CYCLES`, `REQUIRED_LATENT_DAMAGE_CHECK`, `REQUIRED_COMMON_CAUSE_ANALYSIS`.

boolean `require_destructive_see_evidence`는 SEL 하나만 있어도 destructive gate를 통과시킬 수 있으므로 v2에서는 금지한다. 어떤 mode가 기술적으로 불가능하다는 판단도 승인된 technology applicability 근거를 요구한다.

### 6.2 TID와 residual 정책 계산

```text
required_tid = mission_tid_after_shielding × tid_design_factor
tid_margin_abs = verified_part_tid_limit - required_tid
tid_margin_ratio = verified_part_tid_limit / required_tid  # required_tid > 0
```

`mission_tid_after_shielding`, factor, limit은 각각 provenance와 applicability를 가진 operand로 trace한다. factor가 조직 policy에서 왔더라도 policy 승인과 데이터 분류를 별도 검사한다.

SEU의 사건 수가 Poisson이라는 적용 가능한 모델이 승인된 경우에만:

```text
P(at least one residual event) = 1 - exp(-residual_expected_events)
```

분포 가정 또는 residual event 계산이 검증되지 않으면 probability rule은 `NOT_EVALUATED`다. expected count와 probability를 서로 대체하지 않는다.

### 6.3 Custom exception

`CUSTOM_EXCEPTION v2`는 default를 복사한 독립 policy가 아니라 다음 필드를 가진 좁은 override다.

- `exception_id`, target policy pack/version/hash, exact rule IDs
- target mission/subsystem/component와 valid time
- `requested_value`, `default_value`, 단위, relaxation 여부
- 변경 사유, compensating controls, blocking evidence gaps
- exception 적용 전/후 rule 결과와 assurance decision snapshot hash
- requester, independent approver(s), 역할 분리, timestamps
- `PENDING`, `APPROVED`, `REJECTED`, `REVOKED`, `EXPIRED`, `SUPERSEDED`
- immutable history와 external audit anchor

default보다 완화된 예외는 반드시 독립 승인과 유효기간을 요구한다. 승인되지 않았거나 만료·폐기된 예외는 적용하지 않으며 `CUSTOM_POLICY_NOT_APPROVED`와 `HOLD`다. 더 엄격한 값도 추적과 승인 없이 최종 support의 결정 policy로 사용하지 않는다.

## 7. 데이터 분류와 최종 판정 사용 가능성

| 분류 | 완화/정책에서의 의미 | `SUPPORTED_WITH_MITIGATION` operand 가능성 |
|---|---|---|
| `PUBLISHED` | 공식 원문에서 확인한 시험·설계·표준 값 | identity, locator, applicability, rights, review가 모두 유효할 때만 가능 |
| `CUSTOMER_VERIFIED` | 고객 설계·시험·조직 정책을 승인 절차로 확인 | tenant 권한, 승인 target/hash, scope, validity가 유효할 때만 가능 |
| `CALCULATED` | 고정 engine/version/input/output hash로 재현된 결과 | 모든 transitive operand가 decision-eligible이고 engine이 승인됐을 때만 가능 |
| `ASSUMED` | 아직 검증되지 않은 설계계수·독립성·coverage·시간·확률 | 불가. comparison 결과도 `ASSUMED`, `HOLD` |
| `SYNTHETIC` | demo/fixture/test 값 | 불가. engineering gate만 가능, assurance는 `HOLD` |

`CALCULATED`는 세탁 수단이 아니다. 입력 중 하나라도 `ASSUMED`/`SYNTHETIC`이면 출력은 계산 재현성을 가질 수 있어도 최종 지원 operand로는 부적격이다. 결과에는 `upstream_data_classes[]`와 차단 원인을 보존한다.

## 8. 결정론적 엔진과 LLM 경계

결정론적 코드가 소유한다:

- schema/semantic validation, 단위 변환, pointer/hash 검증
- method–failure mode allowlist와 excluded mode 검사
- TID/SEU/recovery/downtime/reliability 식 실행
- policy inheritance, exception 적용 순서, approval/expiry/revocation gate
- rule outcome, evidence gap, processing/assurance decision
- 동일 입력·엔진 버전의 byte-stable 결과

LLM이 할 수 있다:

- 원문에서 설계 파라미터와 locator 후보 추출
- 사람이 검토할 policy/exception 초안 작성
- 결정론적 결과와 차단 이유를 자연어로 설명
- 누락 증거와 다음 시험/설계 입력을 요약

LLM이 할 수 없다:

- failure mode 재분류, 임의 완화율·독립성·확률 생성
- approval status 변경 또는 승인자 대행
- missing Stage 3·4 입력 보간
- rule outcome/assurance decision 수정
- ECC/TMR/reboot로 destructive SEE gap을 닫기

## 9. Fail-closed 판정 순서

1. schema와 enum/typed union 검증
2. identity, provenance, rights, hash, review 검증
3. Stage 3 환경과 Stage 4 event evidence availability/applicability 검증
4. method–failure mode compatibility와 effect-model validity 검증
5. baseline 계산
6. mitigated 계산과 baseline/result 분리 검증
7. destructive SEE mode별 gate
8. policy pack inheritance와 approval/validity 검증
9. custom exception scope/approval/expiry 검증
10. 모든 rule이 `PASS`이고 모든 operand가 decision-eligible일 때만 optimistic assurance 검토

어느 단계든 처리 실패이면 이후 optimistic rule을 평가하지 않는다. 계산 가능하지만 증거가 부족하면 `VALID + INSUFFICIENT_EVIDENCE/HOLD`; 입력 자체가 잘못됐으면 `INVALID_INPUT + HOLD`; provenance/approval hash가 깨졌으면 `PROVENANCE_FAILURE + HOLD`다.

## 10. 핵심 오류 코드

| 코드 | 조건 | 안전 종료 |
|---|---|---|
| `MITIGATION_METHOD_MODE_MISMATCH` | 방법이 영향 주지 않는 mode에 연결 | `INVALID_INPUT + HOLD` |
| `ARBITRARY_MITIGATION_FACTOR` | equation/evidence 없는 범용 factor | `VALID + HOLD`, rule `NOT_EVALUATED` |
| `MITIGATION_EFFECT_EVIDENCE_MISSING` | 효과를 수치화하지만 검증 evidence 없음 | `INSUFFICIENT_EVIDENCE` |
| `NON_EVIDENTIARY_MITIGATION_OPERAND` | `ASSUMED`/`SYNTHETIC`을 support에 사용 | `HOLD` |
| `SHIELDING_TRANSPORT_INPUT_MISSING` | 실제 transport 입력/출력 누락 | `NOT_EVALUATED + HOLD` |
| `REPLACEMENT_EVIDENCE_MISSING` | 대체 부품의 새 evidence 누락 | `INSUFFICIENT_EVIDENCE` |
| `ECC_FAULT_DISTRIBUTION_MISSING` | codeword fault 분포/coverage 누락 | `NOT_EVALUATED + HOLD` |
| `SCRUB_MODEL_INPUT_MISSING` | interval/accumulation 모델 누락 | `NOT_EVALUATED + HOLD` |
| `TMR_INDEPENDENCE_UNVERIFIED` | replica/common-mode 독립성 미검증 | `NOT_EVALUATED + HOLD` |
| `TMR_VOTER_MODEL_MISSING` | voter failure/susceptibility 입력 누락 | `NOT_EVALUATED + HOLD` |
| `TMR_COMMON_MODE_MODEL_MISSING` | common-mode 입력 또는 검증 누락 | `NOT_EVALUATED + HOLD` |
| `TMR_REPAIR_WINDOW_MISSING` | `p`와 repair를 해석할 evaluation window 누락 | `NOT_EVALUATED + HOLD` |
| `TMR_OUTPUT_SEMANTIC_MISMATCH` | failure probability를 success/reliability/availability 필드로 대체 | `INVALID_INPUT + HOLD` |
| `RECOVERY_MODEL_INPUT_MISSING` | recovery coverage/time 누락 | `NOT_EVALUATED + HOLD` |
| `WATCHDOG_FALSE_POSITIVE_MODEL_MISSING` | 오탐 count/rate, denominator, window 또는 검증 모델 누락 | reboot/downtime `NOT_EVALUATED + HOLD` |
| `WATCHDOG_FALSE_POSITIVE_IGNORED` | false activation path가 total reboot/downtime에서 제외 | 계산 불일치 + `HOLD` |
| `SEL_PROTECTION_NOT_VALIDATED` | trip/recovery/latent damage 검증 누락 | `INSUFFICIENT_EVIDENCE/HOLD` |
| `SEL_FALSE_TRIP_MODEL_MISSING` | SEL protection false-trip 모델·분모·window 누락 | total cycle/downtime `NOT_EVALUATED + HOLD` |
| `SPARE_INDEPENDENCE_UNVERIFIED` | spare common-cause 경계 누락 | `NOT_EVALUATED + HOLD` |
| `DESTRUCTIVE_SEE_MODE_MISSING` | required SEL/SEB/SEGR 중 개별 증거 누락 | `INSUFFICIENT_EVIDENCE/HOLD` |
| `EVIDENCE_TYPE_SUBSTITUTION` | 다른 failure mode evidence로 대체 | `HOLD` |
| `POLICY_PACK_NOT_APPROVED` | pack 미승인/폐기/만료 | `HOLD` |
| `CUSTOM_POLICY_NOT_APPROVED` | exception 미승인/범위 밖/만료 | `HOLD` |
| `POLICY_APPROVAL_TARGET_MISMATCH` | 승인 후 내용·scope 변경 | `PROVENANCE_FAILURE + HOLD` |
| `POLICY_RELAXATION_NOT_DISCLOSED` | default보다 완화됐지만 relaxation false | `INVALID_INPUT + HOLD` |
| `POLICY_RULE_OPERAND_MISSING` | typed rule operand trace 누락 | `NOT_EVALUATED + HOLD` |
| `STAGE3_INPUT_UNAVAILABLE` | 실제 환경/차폐/SEE spectrum 없음 | `HOLD` |
| `STAGE4_INPUT_UNAVAILABLE` | 실제 BOM/event evidence 없음 | `INSUFFICIENT_EVIDENCE/HOLD` |

## 11. 최소 adversarial fixture 명세

모든 fixture 숫자와 artifact는 `SYNTHETIC`이다. “정상” fixture도 구조와 계산 재현성만 검증하며 assurance 기대값은 `HOLD`다.

| Fixture ID | 변이/목적 | 기대 코드와 결과 |
|---|---|---|
| `mitigation-v2-normal-synthetic-hold` | typed ECC + synthetic SEU/codeword 입력, 승인 형식 policy | engineering 계산 재현, `SYNTHETIC_ONLY`, assurance `HOLD` |
| `mitigation-v2-effect-input-missing` | ECC codeword multiplicity 제거 | `ECC_FAULT_DISTRIBUTION_MISSING`; `NOT_EVALUATED + HOLD` |
| `mitigation-v2-arbitrary-factor` | `effectiveness_factor: 0.1`만 삽입 | `ARBITRARY_MITIGATION_FACTOR`; support 금지 |
| `mitigation-v2-assumed-factor-laundered` | assumed factor로 계산한 output을 `CALCULATED`로 표기 | `NON_EVIDENTIARY_MITIGATION_OPERAND`; `HOLD` |
| `mitigation-v2-ecc-substituted-for-sel` | SEL requirement를 ECC PASS trace에 연결 | `EVIDENCE_TYPE_SUBSTITUTION`, `DESTRUCTIVE_SEE_MODE_MISSING`; `HOLD` |
| `mitigation-v2-scrub-substituted-for-seb` | scrubbing으로 SEB coverage PASS 생성 | 같은 두 코드; `HOLD` |
| `mitigation-v2-tmr-substituted-for-segr` | TMR로 SEGR evidence gap 제거 | 같은 두 코드; `HOLD` |
| `mitigation-v2-shielding-factor-cross-mode` | TID shielding factor를 모든 SEE mode에 복사 | `MITIGATION_METHOD_MODE_MISMATCH` 또는 `SHIELDING_TRANSPORT_INPUT_MISSING`; `HOLD` |
| `mitigation-v2-replacement-reuses-old-evidence` | 새 PN에 old evidence/approval pointer 유지 | `REPLACEMENT_EVIDENCE_MISSING`, Stage 4 identity conflict code; `HOLD` |
| `mitigation-v2-recovery-time-missing` | watchdog coverage는 있으나 reboot/restore time 누락 | `RECOVERY_MODEL_INPUT_MISSING`; downtime `NOT_EVALUATED` |
| `mitigation-v2-sel-latent-damage-hidden` | trip/recovery만 있고 post-test latent-damage 결과 제거 | `SEL_PROTECTION_NOT_VALIDATED`; `HOLD` |
| `mitigation-v2-spare-common-cause-hidden` | active/spare를 independent로 표시하되 동일 power group | `SPARE_INDEPENDENCE_UNVERIFIED`; `HOLD` |
| `policy-v2-approval-string-only` | synthetic pack의 status만 `APPROVED`로 변경 | `SYNTHETIC_POLICY_WITH_SUPPORT`, `POLICY_APPROVAL_TARGET_MISMATCH`; `HOLD` |
| `policy-v2-relaxed-threshold-undisclosed` | max residual SEU를 높이고 relaxation=false | `POLICY_RELAXATION_NOT_DISCLOSED`; `INVALID_INPUT + HOLD` |
| `policy-v2-exception-expired` | 승인 exception의 `valid_until` 경과 | `CUSTOM_POLICY_NOT_APPROVED`; default 적용 또는 `HOLD`, exception 적용 금지 |
| `policy-v2-exception-scope-bypass` | 다른 mission/component exception 재사용 | `CUSTOM_POLICY_NOT_APPROVED`; `HOLD` |
| `policy-v2-history-tampered` | 승인 후 rule/actor/time 변경, hash 유지 | `POLICY_APPROVAL_TARGET_MISMATCH` 또는 history tamper code; `PROVENANCE_FAILURE + HOLD` |
| `policy-v2-destructive-boolean-bypass` | SEL 하나로 legacy boolean destructive gate PASS | `DESTRUCTIVE_SEE_MODE_MISSING`; `HOLD` |
| `dependency-v2-stage3-placeholder` | 누락 spectrum을 zero synthetic flux로 채움 | `STAGE3_INPUT_UNAVAILABLE`, synthetic misrepresentation code; `HOLD` |
| `dependency-v2-stage4-mode-relabel` | SEU event type을 SEL로 이름만 변경 | `EVIDENCE_TYPE_SUBSTITUTION`; `HOLD` |

기존 H01 fixture 20개는 ID와 기대 결과를 그대로 유지한다. H02는 다음 9개 fixture를 추가한다.

| Fixture ID | 입력/변이와 paired 관계 | 기대 계산·코드 |
|---|---|---|
| `mitigation-v2-watchdog-false-positive-counted` | paired control: `N_target=0`, `N_false=1/mission`, false path `REBOOT`, fraction `1`, duration `60 s` | `true_positive_activation_count=0`, `false_positive_activation_count=1`, `reboot_count_total=1`, `downtime_total=60 s`; synthetic이므로 assurance `HOLD` |
| `mitigation-v2-watchdog-false-positive-ignored` | 직전 control에서 계산 입력은 유지하고 false path를 reboot/downtime 합계에서 제외해 optimistic policy PASS로 변이 | `WATCHDOG_FALSE_POSITIVE_IGNORED`; 계산 불일치, support 금지, `HOLD` |
| `mitigation-v2-tmr-boundary-p0` | 같은 window/독립성/voter/common-mode/repair 조건에서 `p=0` | `system_failure_probability=0`; synthetic `HOLD` |
| `mitigation-v2-tmr-boundary-p01` | 직전 fixture와 `p`만 `0.1`로 변경 | `system_failure_probability=0.028`; synthetic `HOLD` |
| `mitigation-v2-tmr-boundary-p1` | 직전 fixture와 `p`만 `1`로 변경 | `system_failure_probability=1`; synthetic `HOLD` |
| `mitigation-v2-tmr-failure-probability-relabeled-availability` | `p=0.1` 결과 `0.028`을 availability/reliability로 저장하거나 `0.972`로 뒤집어 failure output을 대체 | `TMR_OUTPUT_SEMANTIC_MISMATCH`; `INVALID_INPUT + HOLD` |
| `mitigation-v2-tmr-voter-model-missing` | `p=0.1` control에서 voter susceptibility/model만 제거 | `TMR_VOTER_MODEL_MISSING`; `NOT_EVALUATED + HOLD` |
| `mitigation-v2-tmr-common-mode-hidden` | `p=0.1` control에서 common-mode 입력을 제거하거나 0으로 가정 | `TMR_COMMON_MODE_MODEL_MISSING` 또는 `TMR_INDEPENDENCE_UNVERIFIED`; `NOT_EVALUATED + HOLD` |
| `mitigation-v2-sel-false-trip-model-missing` | SEL 보호 출력에서 false-trip count/rate·denominator·window를 제거하고 total cycle/downtime을 계산 | `SEL_FALSE_TRIP_MODEL_MISSING`; total cycle/downtime `NOT_EVALUATED + HOLD` |

Workstream 60은 H01 20개와 H02 9개, 총 29개 고유 fixture ID를 구현한다. watchdog attack/control은 false path 합산 여부만 달라야 하고, TMR `p=0`, `0.1`, `1` boundary fixture는 `p` 외 모든 operand와 window가 같아야 한다. 각 target error code가 실제로 관측돼야 하며 하나의 generic validation error만으로 통과시키지 않는다.

## 12. 아직 없는 Stage 3·4 의존 입력

### Stage 3

- 실제 mission TID after shielding와 완전한 model chain/run hash
- component 위치별 material/geometry/areal density 또는 승인 equivalent definition
- SEE용 particle species, energy spectrum/LET representation, angle/geometry, valid time
- shielding 전후 spectrum/선량을 같은 run scope에서 비교할 수 있는 provenance
- uncertainty/validity domain과 `APPLICABLE` 판정 입력

### Stage 4

- 승인 BOM의 exact manufacturer/orderable PN, process/die/lot/date-code 조건
- TID `maximum_within_spec_dose`와 시험 material/dose rate/bias/anneal/temperature
- SEU cross-section curve, bit/device denominator, event multiplicity·configuration/workload
- SEL current signature, trigger/limit/recovery/latent-damage/post-test 결과
- SEB·SEGR safe operating boundary와 bias/temperature/LET/range/angle 조건
- artifact bytes/hash, locator, rights, review/approval history, applicability status

위 값은 임의로 생성하지 않는다. 실제 run/원문이 없으면 `STAGE3_INPUT_UNAVAILABLE` 또는 `STAGE4_INPUT_UNAVAILABLE`다.

## 13. Workstream 전달 요구사항

### Workstream 10 — schema/contracts

- `MITIGATION v2` method-discriminated union과 typed parameters
- `POLICY_PACK v2`, `CUSTOM_EXCEPTION v2`, immutable approval/history/hash projection
- SEL·SEB·SEGR 개별 policy, SEFI/SET/recoverable mode enum 검토
- baseline/mitigated result와 transitive data-class operand trace
- v1 `effectiveness_factor`, free-form `parameters`, destructive boolean의 migration/금지 규칙
- 이 문서의 오류 코드와 semantic validation order

### Workstream 20 — deterministic engine

- incident/logical/recovery/downtime/irreparable 축을 분리한 result model
- equation registry와 method별 calculator; generic factor 제거
- watchdog/SEL protection의 true/false activation path 정규화·합산과 누락 시 `NOT_EVALUATED`
- TMR `system_failure_probability` 출력명, window 의미, boundary와 voter/common-mode/repair gate
- baseline과 mitigated run의 input/output hash, engine version, byte-stable output
- policy inheritance/exception/expiry evaluator와 before/after impact snapshot
- 미지원/누락 입력에서 `NOT_EVALUATED` 및 fail-closed status

### Workstream 40 — parts evidence

- ECC용 multiplicity/denominator/configuration, SEL 보호 검증용 current/recovery/latent-damage 필드
- TMR/spare/부품대체 applicability에 필요한 technology/process/common-mode 근거
- SEL·SEB·SEGR event별 독립 coverage와 substitution 방지 trace
- replacement 시 evidence 재사용 금지와 새로운 exact identity/applicability 결과

### Workstream 60 — assurance/evals

- 11절 fixture와 paired controls 구현
- H01 20개를 보존하고 H02 9개를 추가해 총 29개 고유 ID 검증
- target error code, processing status, assurance decision 동시 검증
- 계산 재현성, operand transitivity, policy hash/history tamper 검증
- ECC/scrub/TMR/reboot로 destructive evidence gap을 숨기는 조합 공격
- false PASS 0건과 false HOLD/expected HOLD를 분리한 결과 보고

## 14. 한계와 다음 질문

- 실제 environment/BOM/test/policy/effectiveness 데이터는 0건이다.
- 공통 schema와 엔진은 이번 문서의 v2 계약을 아직 구현하지 않았다.
- NASA/ESA 출처는 방법별 적용 범위를 뒷받침하지만 SPECTRA 설계의 수치 효과 검증은 아니다.
- ECC/TMR/scrubbing 식의 적용에는 fault multiplicity, independence, time window가 필요하며 현재 없다.
- watchdog/SEL false-positive·false-trip의 실제 rate, denominator, window와 path 검증 데이터는 현재 없다.
- 조직 policy owner, approver 역할 분리, 승인 저장소와 immutable audit anchor가 지정되지 않았다.
- Stage 3·4가 실제 입력을 제공한 뒤에도 Workstream 60의 독립 검증 전에는 `SUPPORTED_WITH_MITIGATION`을 허용할 수 없다.
