# SPECTRA Synthetic Vertical Slice

이 디렉터리는 Stage 2의 결정론적 합성 기준선이다. 물리 모델이나 실제 방사선 시험 결과가 아니며 모든 입력·계수·출력은 `SYNTHETIC`이다.

## 한 명령 검증

```bash
python3 tests/simulation/run_all.py
```

이 명령은 다음을 순서대로 실행한다.

1. Stage 1 스키마·semantic gate·False PASS fixture 전체 검증
2. Stage 2 결과 스키마와 TID·SEE·정책 테스트
3. 차폐·ECC·범위 밖 입력 비교 CLI

비교 화면만 다시 보려면 다음을 실행한다.

```bash
python3 simulation/run_demo.py
```

## MVP Decision Engine

Workstream 50의 v2 ECC·정책 계약을 소비하는 고정 MVP 비교는 다음 명령으로 실행한다.

```bash
python3 simulation/run_mvp_decision.py simulation/fixtures/mvp-ecc-policy-v2.json
```

결과 전체는 canonical JSON으로 stdout에 출력된다. 선택한 EvidencePacket만 내보내거나 발표용 요약을 보려면 다음 옵션을 사용한다.

```bash
python3 simulation/run_mvp_decision.py --evidence-packet variant
python3 simulation/run_mvp_decision.py --summary
```

정규화 입력은 Stage 1 EvidencePacket v1.1과 `MITIGATION/USER_POLICY 2.0.0`을 먼저 검증한다. baseline은 ECC OFF·DRAFT policy, variant는 ECC ON·APPROVED 형식 policy다. ECC 효과는 범용 계수가 아니라 입력에 명시된 합성 multiplicity별 transition count로만 계산한다.

현재 Stage 3 실제 환경과 Stage 4 exact-part 증거가 없으므로 수치 비교가 재현되더라도 두 시나리오의 `engineering_gate`는 `NOT_EVALUATED`, `assurance_decision`은 `HOLD`다. 승인 문자열, ECC 결과 또는 합성값으로 이 상태를 승격하지 않는다. 결과의 `change_impact`는 입력·출력·규칙 변화와 무효화된 mitigation/policy 근거를 machine-readable 형식으로 보존한다.

두 명령 모두 프로젝트 파일을 생성하거나 수정하지 않는다.

## 결정론적 합성 계산

### TID

```text
shielded TID = reference TID × (mission years / reference years) × synthetic shielding factor
required TID = shielded TID × user design factor
```

차폐 계수는 `simulation/config/synthetic-model.json`에 있는 1·2·3·4 mm 이산 lookup만 사용한다. 중간값 보간과 범위 밖 외삽을 하지 않는다. 5 mm와 같은 입력은 `OUT_OF_MODEL_SCOPE`다.

### SEE

```text
raw SEU = particle flux × cross section × component count × duration seconds × synthetic exposure scale
residual SEU = raw SEU × mitigation factor
```

`see_exposure_scale`은 데모용 합성 계수이며 과학적 환경 계수가 아니다. ECC를 끄면 완화 계수는 1이다.

### 정책과 보증 판정

- `engineering_gate`는 합성 수치 안에서 TID margin, residual SEU, destructive SEE evidence, policy approval을 비교한 결과다.
- `engineering_gate=PASS`는 방사선 보증 지원 판정이 아니다.
- 합성 입력으로 실행한 모든 결과의 `assurance_decision`은 항상 `HOLD`다.
- 출력 EvidencePacket에는 `SYNTHETIC_ONLY` 차단형 evidence gap이 남는다.
- 입력 스키마 또는 Stage 1 의미 오류는 `INVALID_INPUT/HOLD`, 지원 lookup 밖 입력은 `OUT_OF_MODEL_SCOPE/HOLD`다.
- 합성 모델 설정의 분류·필수 필드·이산 lookup이 변조되면 `MODEL_FAILURE/HOLD`다.

## 코드 경계

- `src/spectra_sim/tid.py`: TID 계산과 차폐 범위
- `src/spectra_sim/see.py`: SEE 계산과 ECC 전후 비교
- `src/spectra_sim/policy.py`: 결정론적 정책 rule
- `src/spectra_sim/contracts.py`: 실행 전·후 EvidencePacket JSON Schema와 Stage 1 semantic gate 검증
- `src/spectra_sim/engine.py`: 입력 override, 계산, 결과와 EvidencePacket 구성
- `simulation/schemas/simulation-result.schema.json`: Stage 2 출력 계약

## 현재 한계

- 실제 환경 모델, 실제 부품 시험자료와 과학적 정확도 검증이 없다.
- 단일 부품과 `cm2/device` 단면적만 처리한다.
- 합성 1년은 365일로 고정한다.
- 차폐는 알루미늄 등가 1~4 mm 이산값만 지원한다.
- CLI 비교까지만 제공하며 제품 대시보드는 아직 구현하지 않았다.
- 기본 입력은 검증된 Stage 1 합성 fixture를 사용한다. 외부 합성 데모의 실제 위치는 제공되지 않아 가져오지 않았다.
- 런타임 의미 검증은 Stage 1 기준 구현인 `tests/schema/validate_contracts.py`를 직접 로드한다. 해당 파일이 없는 분리 배포에서는 안전하게 실패하므로, 패키징 시 검증 모듈을 제품 코드로 승격하는 공통 계약 변경이 필요하다.
