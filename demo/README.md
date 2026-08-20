# SPECTRA Offline HTML Demo

내일 발표용 Workstream 80 오프라인 데모다. 서버, 네트워크, 설치, 외부 폰트·asset 없이 `index.html` 한 파일로 동작한다.

## 실행

Finder에서 `demo/index.html`을 더블클릭하거나 브라우저의 **파일 열기**로 연다. 로컬 서버는 필요 없다.

- `←` / `→`: 이전·다음 화면
- `Page Up` / `Page Down`, `Space`: 화면 이동
- 마우스·트랙패드 위/아래 스크롤: 이전·다음 화면
- 화면 아래 버튼: 이전·다음 화면
- 3번 화면: 엔진이 이미 검증한 1·2·4 mm와 범위 밖 5 mm snapshot 선택
- 5번 화면: 엔진이 이미 검증한 ECC ON/OFF snapshot 선택
- 새로고침: 첫 화면부터 재시작

## 발표 흐름

| 화면 | 핵심 메시지 | 권장 누적 시간 |
|---:|---|---:|
| 1 | 끊어진 환경 계산–BOM–시험 PDF–완화·승인 | 0:45 |
| 2 | 합성 LEO 임무와 합성 단일 부품 identity | 1:30 |
| 3 | 1·2·4 mm 합성 TID와 5 mm `OUT_OF_MODEL_SCOPE` | 2:35 |
| 4 | TID/SEU 계산 가능성과 실제 파괴성 SEE 증거 공백 분리 | 3:30 |
| 5 | raw SEU와 ECC 적용 후 residual SEU 분리 | 4:30 |
| 6 | `engineering_gate=PASS`여도 assurance `HOLD` | 5:35 |
| 7 | Evidence Chain과 실제 데이터·GCP 0 상태 | 6:30 |

핵심 설명은 6분 30초에 끝내고, 마지막 30초는 화면 전환 또는 돌발 상황 여유로 둔다. Q&A 3분은 이 데모 시간에 포함하지 않는다.

## H02 화면 원칙

- 한글은 Mac 오프라인에서 사용 가능한 `Apple SD Gothic Neo` 우선 system font stack을 사용한다.
- 상단에는 텍스트 `SPECTRA`만 남기고 전역 상태 badge를 두지 않는다.
- `SYNTHETIC / NOT PHYSICAL EVIDENCE / ASSURANCE: HOLD`는 6번 화면에서 한 번 명확히 설명한다.
- 수치 화면의 작은 `SYNTHETIC` 표시는 계속 유지한다.
- 2번 화면은 “승인 BOM 0건. 화면의 부품 identity는 합성이며, 실제 추천이 아닙니다.”로 축약한다.

## 고정된 신뢰성 경계

- 모든 수치와 선택지는 `SYNTHETIC` Stage 2 결과다.
- 브라우저 JavaScript는 물리 계산을 하지 않는다. `spectra_sim` 실행 결과 snapshot 중 화면 표시값만 내장한다.
- 모든 선택에서 assurance는 `HOLD`다.
- `engineering_gate=PASS`는 합성 조건 비교 결과이며 방사선 보증 PASS가 아니다.
- 5 mm는 값을 추정하지 않고 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`로 닫는다.
- 합성 fixture의 `SEL` 표시는 정책 경로 테스트용이며 실제 파괴성 SEE 증거가 아니다.
- 실제 환경 모델 run, 승인 BOM, 시험 PDF, 실제 수치, 실제 GCP resource는 모두 0이다.
- JavaScript가 실행되지 않으면 7개 화면이 세로 문서로 모두 노출되는 정적 fallback이 동작한다.

## 내장 snapshot

| 시나리오 | run | shielded TID | raw SEU | residual SEU | processing | engineering | assurance |
|---|---|---:|---:|---:|---|---|---|
| 1 mm + ECC | `sim-d5a72077d684f459` | 8.0 | 0.063072 | 0.0063072 | `VALID` | `PASS` | `HOLD` |
| 2 mm + ECC | `sim-3cc00f2c824db56d` | 6.0 | 0.063072 | 0.0063072 | `VALID` | `PASS` | `HOLD` |
| 4 mm + ECC | `sim-ddf29f8ab807196d` | 3.5 | 0.063072 | 0.0063072 | `VALID` | `PASS` | `HOLD` |
| 2 mm + no ECC | `sim-b74d7317282b2a82` | 6.0 | 0.063072 | 0.063072 | `VALID` | `PASS` | `HOLD` |
| 5 mm + ECC | `sim-27e031f2388ab6fc` | — | — | — | `OUT_OF_MODEL_SCOPE` | `NOT_EVALUATED` | `HOLD` |

원본 재현:

```bash
cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 simulation/run_demo.py
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
```

`index.html`은 발표 안정성을 위해 self-contained snapshot을 사용한다. 향후 엔진 계약이나 기준 fixture가 바뀌면 위 명령으로 결과를 다시 확인하고 내장 snapshot과 run ID를 함께 갱신해야 한다.

## Product UI — H05 result binding

`product.html`은 발표 슬라이드가 아니라 3단계 `검토 조건 → 수치 변화 → 보증 판단` 제품 프로토타입이다. 아래 생성 파일을 로컬 `<script>`로 읽으므로 Finder에서 직접 열어도 핵심 경로가 동작한다.

- `data/mvp-product-result.json`: 검증과 향후 HTTP 소비를 위한 정규 JSON
- `data/mvp-product-result.js`: 같은 payload를 담은 `file://` 전용 전역 wrapper

두 파일은 각각 관리하지 않는다. `build_product_data.py`가 기존 `run_mvp_decision()` 결과와 Stage 2의 1·4·5 mm scope 결과를 하나의 payload로 만든 뒤, 정렬된 compact JSON으로 함께 기록한다. 생성 시각·UUID·절대 경로를 새로 넣지 않아 같은 계약과 입력에서는 byte-identical하다.

```bash
cd /Users/taehoon/Desktop/IAA/SPECTRA
PYTHONDONTWRITEBYTECODE=1 python3 demo/build_product_data.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/product/test_product_data_binding.py
```

2 mm ECC 미적용/적용 비교는 통합 MVP의 `baseline / variant`에 직접 결합된다. 현재 생성 기준선에서 residual logical errors는 각각 `0.063072 / 0.013072`, aggregate engineering gate는 `NOT_EVALUATED`, assurance는 두 경우 모두 `HOLD`다. 1·4 mm와 범위 밖 5 mm는 기존 Stage 2 engine 결과를 함께 소비하며, 5 mm는 metrics 없이 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`다.

브라우저 코드는 payload의 값·상태·공백·식별자를 표시하고 형식을 검사할 뿐 물리 계산, 보간, 임계값 평가 또는 정책 판정을 수행하지 않는다. wrapper가 없거나 손상됐거나 `HOLD` 불변식이 깨지면 모든 수치를 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다. 실제 환경 모델 run, 승인 BOM, 시험 원문, 실제 수치와 GCP resource는 여전히 0이다.

## H06 Runtime mitigation binding

H06 exporter는 Workstream 20의 production API `evaluate_runtime_mitigation()`을 세 검증 fixture에 직접 호출하고 결과 전체를 기존 payload의 `runtime_mitigation_results` collection에 추가한다.

| method | 정규 projection | 상태 |
|---|---|---|
| `WATCHDOG` | false activation 1, reboot 1, downtime 60 s | `SYNTHETIC / NOT_EVALUATED / HOLD` |
| `TMR` | input `p=0.1`, system failure probability `0.028` | `SYNTHETIC / NOT_EVALUATED / HOLD` |
| `SEL_PROTECTION` | true 1 + false 1, power cycles 2, downtime 32 s | `SYNTHETIC / NOT_EVALUATED / HOLD` |

`product.html`의 “수치 변화” 단계에서 `방사선 수치 / Runtime 완화`를 전환한 뒤 세 method를 선택한다. UI는 API가 반환한 `computed_projection`, policy evaluation, stable error codes, equation/result/packet ID와 input/output hash를 표시만 한다. TMR 공식, downtime 합산, policy threshold는 브라우저에서 재계산하지 않는다.

각 runtime record는 exporter가 만든 `integrity` anchor와 result의 result ID·input hash·output hash가 일치해야 한다. collection 누락·unknown method는 runtime collection 전체를, 개별 schema/state/hash/projection 손상은 해당 record만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫고 수치와 ID를 숨긴다. 기존 MVP, 1·4·5 mm, Evidence Coverage와 Change Impact 경로는 그대로 유지한다.

## H07 Runtime result content integrity

H07은 sibling integrity anchor의 문자열 일치만 신뢰하던 결함을 닫았지만, 브라우저가 Python canonical number lexical form을 재구성하는 방식은 H08에서 폐기했다. JavaScript와 Python의 지수 표기 경계가 달라 정상 production result를 잘못 거부할 수 있기 때문이다.

정적 HTML은 JavaScript 실행 전부터 runtime 값을 `—`로 두고 `HOLD`를 표시한다. 따라서 content 검증이 끝나기 전이나 스크립트 오류 시에도 낙관적인 runtime 수치가 먼저 노출되지 않는다. 이 검증은 결과 무결성 확인일 뿐 WATCHDOG/TMR/SEL 공식이나 policy threshold를 브라우저에서 재구현하지 않는다.

## H08 Cross-runtime canonical number parity

Exporter는 각 runtime record의 `integrity.output_hash_preimage`에 production `canonical_runtime_json()`이 만든 정확한 UTF-8 canonical JSON preimage를 함께 기록한다. 이 값은 보조 무결성 자료이며 runtime result contract나 계산 결과를 바꾸지 않는다.

브라우저 consumer는 record를 표시하기 전에 세 조건을 모두 확인한다.

1. canonical preimage의 self-contained SHA-256이 `result.output_hash`와 exact match
2. preimage를 `JSON.parse()`한 값이 result에서 root `output_hash`만 제외한 객체와 JSON type/value 기준 deep exact match
3. sibling result/input/output anchor가 result와 exact match

어느 조건이든 실패하면 해당 method만 projection·result ID·input/output hash를 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다. 정상 TMR `p=0.001 → 2.998e-06`, 1e-6 아래·위, 1e-7 계열 및 음수 0 입력 control도 production hash와 consumer hash가 일치한다. `demo/index.html`은 H08에서 변경하지 않는다.

## H09 Signed zero integrity

Preimage parsed number와 result body number의 deep comparison은 `Object.is()`를 사용한다. 따라서 일반 finite number와 integer-valued float의 값 비교는 유지하면서 `+0`과 `-0`은 서로 다른 in-memory number로 취급한다. result만 `+0 → -0` 또는 `-0 → +0`으로 바꾸고 preimage/hash/anchor를 유지하면 해당 record가 fail-closed된다. Exporter, 생성 JSON/JS와 발표 HTML은 H09에서 변경하지 않는다.
