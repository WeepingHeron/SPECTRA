# 80 Product & Dashboard — Current

## 상태

`VERIFIED — H09 Signed Zero Integrity / base 4920b6e`

H08의 production canonical preimage 방식과 numeric parity를 유지하면서 deep number comparison이 `+0/-0` 변조를 허용하던 결함을 H09로 보완했다. JSON number 비교는 `Object.is()`만 사용하며 signed zero가 다르면 대상 runtime record만 fail-closed한다. 실제 환경·부품·시험·GCP resource는 0이고 제품은 여전히 합성 오프라인 프로토타입이다.

## H09 Control Tower 독립 검증 — 2026-08-20

- 수정 범위가 `demo/product.html`, Product 테스트, README와 Workstream 80 문서에 한정되고 exporter·생성 JSON/JS·발표 HTML·공통 schema·runtime engine·Assurance 파일은 변경하지 않았음을 확인했다.
- Product binding 10개 테스트를 재실행해 기존 H08 numeric parity·stale-hash 공격, exporter byte determinism, JSON/wrapper exact, JavaScript syntax와 원격 dependency 0을 포함해 모두 통과했다.
- WATCHDOG result의 `true_target_event_count`만 `+0 → -0`으로 바꾸고 production preimage·result hash·sibling anchor를 유지한 직접 공격은 `RUNTIME_PREIMAGE_VALUE_MISMATCH`로 종료됐다. 대상 record는 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`였고 TMR과 H05 radiation residual `0.013072`는 유지됐다.
- 반대 방향 `-0 → +0`, 정상 negative-zero control과 H08 `p=0.001`·1e-6 경계 아래·위·1e-7 controls도 Product suite에서 통과했다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32`, 세 method의 `NOT_EVALUATED / HOLD`와 warning/error 0을 확인했다.
- H09는 공통 계약이나 engine을 바꾸지 않았으므로 지침에 따라 schema·simulation·environment·assurance 전체 회귀는 반복하지 않았다.

### 판정

H09 Signed Zero Integrity 패키지는 `VERIFIED`다. H05 Product binding의 기존 `VERIFIED`, H07 발표 note와 H08 production canonical preimage 보완을 유지한다. working tree commit·push와 Stage 8 완료를 의미하지 않으며 실제 environment·parts evidence와 GCP resource는 여전히 0, 최종 assurance는 `HOLD`다.

## H09 Signed Zero Integrity — 2026-08-20

### 구현

- `demo/product.html`의 `jsonDeepExact()` number 비교에서 `Object.is(left, right) || left === right`를 `Object.is(left, right)`로 교체했다.
- 일반 finite number와 같은 부호의 zero는 그대로 통과하고 `Object.is(+0, -0) === false`인 signed-zero 차이만 거부한다.
- Exporter, 생성 JSON/JS, `demo/index.html`, runtime calculator와 공통 계약은 변경하지 않았다.
- 브라우저는 runtime 계산식과 policy threshold를 재구현하지 않는다.

### 재현과 공격 결과

- 수정 전 WATCHDOG `computed_projection.true_target_event_count`만 `+0 → -0`으로 바꾸고 production preimage·result output hash·sibling anchor를 유지하면 `ready=true / VALID / HOLD`로 수용됐다.
- 수정 후 같은 공격은 WATCHDOG만 `ready=false`, `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`로 닫힌다.
- test-only direct record에서 preimage와 result가 모두 `-0.0/-0`인 정상 control은 `ready=true / HOLD`다. 이 control의 result만 `-0 → +0`으로 바꾸면 대상 record가 fail-closed한다.
- 두 공격 모두 다른 TMR/SEL record와 H05 radiation residual `0.013072`를 유지한다.
- H08 result/preimage 동시 변조, format-valid fake hash, `p=0.001`, 1e-6 아래·위, 1e-7 및 negative-zero input controls는 계속 통과한다.

### H09 검증

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding`: 10 tests 통과.
- JavaScript syntax, 원격 runtime dependency 0, exporter byte-identical, JSON/wrapper exact와 H08/H07 회귀를 같은 Product suite에서 확인했다.
- 수정 후 직접 재현에서 공격 WATCHDOG `ready=false`, TMR `ready=true`, H05 radiation residual `0.013072`를 관측했다.
- 지침에 따라 schema·simulation·environment·assurance 전체 회귀는 반복하지 않았다.
- 실제 browser 재확인은 작업 채팅의 `file://` URL 제약 때문에 미실행이다. H08 Control Tower가 검증한 정상 WATCHDOG/TMR/SEL 조작과 warning/error 0은 유지되며 H09 review에서 signed-zero 보완 후 실제 브라우저 재확인이 필요하다.
- `CONTRACT_CHANGE_REQUEST`: 없음.

## H08 Control Tower 독립 검증 — 2026-08-20

- Product binding 10개 테스트, `p=0.001`, 1e-6 경계 아래·위, 1e-7 계열, `-0.0` control, 제출된 stale-hash 공격, JavaScript syntax, 원격 dependency 0과 생성물 hash를 독립 재실행해 통과했다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32`와 세 record의 `VALID / NOT_EVALUATED / HOLD`, warning/error 0을 확인했다.
- 추가 numeric edge 공격에서 WATCHDOG result 본문의 `true_target_event_count`만 `0`에서 `-0`으로 바꾸고 기존 production preimage·output hash·sibling anchor를 유지해도 consumer가 `ready=true`로 수용했다.
- 원인은 `jsonDeepExact()`의 number 비교가 `Object.is(left, right) || left === right`여서 `Object.is(0, -0)`의 불일치를 뒤의 `0 === -0`이 다시 허용하기 때문이다. 제출된 negative-zero control은 정상 결과가 통과하는지만 확인하고 `+0/-0` 본문 변조는 공격하지 않는다.
- 최종 assurance는 계속 `HOLD`라 낙관적 PASS로 승격되지는 않았지만, H08 필수 조건인 result 본문 변조 fail-closed와 production preimage exact binding을 충족하지 못한다.

### 판정

H08은 `CHANGES_REQUESTED`다. H05 Product binding의 기존 `VERIFIED`와 H07의 발표 note·stale-hash 보완 결과는 유지한다. H09에서는 JSON number 비교의 `+0/-0` 구분과 해당 공격 회귀만 직접 보완하며 전체 저장소 회귀는 반복하지 않는다.

## H08 Cross-runtime Canonical Number Parity — 2026-08-20

### 구현

- `demo/build_product_data.py`가 runtime result의 root `output_hash`를 제외한 객체를 Workstream 20의 `canonical_runtime_json()`으로 직렬화해 `integrity.output_hash_preimage`에 보존한다.
- JSON과 `file://` wrapper는 같은 payload에서 함께 생성되므로 preimage를 별도로 손으로 관리하지 않는다.
- `demo/product.html`은 Python number lexical form을 재구성하지 않는다. preimage UTF-8 SHA-256과 `result.output_hash`, preimage parsed value와 result body, sibling result/input/output anchor를 모두 독립 확인한다.
- 실패는 해당 method record만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫고 projection·result ID·input/output hash를 숨긴다. 다른 정상 runtime record와 H05 radiation 결과는 유지된다.
- 브라우저는 WATCHDOG/TMR/SEL 공식이나 policy threshold를 계산하지 않는다.
- H07에서 검증된 `demo/index.html`은 변경하지 않았다.

### Numeric parity control

| control | production projection | production/browser hash | consumer |
|---|---:|---|---|
| TMR `p=0.001` | `2.998e-06` | `sha256:f52eb2e2966c9e188d576a4bb24e47bb9d47743c9b89b34fe0461ce9868c9d76` | `ready=true / HOLD` |
| TMR `p=0.0005` | `7.4975e-07` | `sha256:15b26c811b5db8755ffbc5a14572d815aaad60bce7649b98081ce8f83b8ca73d` | `ready=true / HOLD` |
| TMR `p=0.0006` | `1.079568e-06` | `sha256:5a1f580fed38afadb8247a027333c566ed31a7afa9e393326e2ed19601a6a13b` | `ready=true / HOLD` |
| TMR `p=0.0002` | `1.19984e-07` | `sha256:a4000ff7b4206550fdee7843a970ef408389fae34b9fbc73cb7dd5d89076ddb5` | `ready=true / HOLD` |
| TMR `p=-0.0` | `0.0` | `sha256:2ff8447baf939c6092f9a2970ea7a57e208b9d051630bcce0b57fada5d19842e` | `ready=true / HOLD` |

`number` schema minimum 0은 `-0.0`을 유효 numeric value로 받아들이며 engine도 `VALID`와 projection `0.0`을 생성한다. 기존 WATCHDOG preimage는 integer-valued float `60.0`과 `0.0` lexical form을 명시적으로 보존한다.

### 공격 결과

- result 본문만 변조하고 preimage/hash 유지, preimage만 변조하고 result 유지, result와 preimage를 함께 변조하고 stale hash 유지, result·preimage·sibling hash에 같은 임의 format-valid hash 주입을 모두 대상 record `ready=false`로 닫는다.
- 실패 record는 projection `null`, result ID와 input/output hash `—`, assurance `HOLD`다.
- result object key 순서만 바꾼 동일 JSON value는 preimage parsed value와 deep exact match하므로 정상 통과한다.
- 모든 개별 공격에서 Product model과 H05 radiation residual은 정상 유지된다.

### 검증 상태

- Product binding 10 tests 통과: exporter 2회 byte-identical, JSON/wrapper exact, production API/schema exact, numeric parity 5 controls, preimage mutation 공격, JavaScript syntax, 원격 dependency 0, H07 발표 HTML SHA-256 회귀 포함.
- schema 14개, valid fixture 5개, invalid fixture 116개 통과.
- simulation 55 tests, environment 23 tests, raw-manifest preflight 2 tests 통과.
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 공격 실행 47개, control 4개, failure 0, false pass 0, `NOT_EVALUATED` 1.
- 생성 JSON SHA-256 `bb17e926f3c13dd5b37c12a4fc59826e2b061be7ee6ad45fe83675c30c0d6398`, JS SHA-256 `adc54afc2fcd1da792fc2cabc6079d16134e2557905b4d175e5007a576ad8a41`.
- H08에서 변경하지 않은 발표 HTML SHA-256 `96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5`.
- `git diff --check` 통과.
- 실제 browser 재확인은 작업 채팅의 `file://` URL 제약 때문에 미실행이다. H07 Control Tower가 검증한 세 runtime method·warning/error 0과 세 viewport 기준에서 `demo/index.html`은 H08 동안 byte 불변이다.
- `CONTRACT_CHANGE_REQUEST`: 없음. 공통 canonical contract를 변경하지 않고 production preimage를 Product payload 보조자료로 사용했다.

## H07 Control Tower 독립 검증 — 2026-08-20

- 제출된 stale projection·policy·stable code·anchor·format-valid fake hash 공격은 모두 대상 record를 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫았고, 정상 고정 WATCHDOG·TMR·SEL control은 production hash와 일치했다.
- Product 9개, schema 14/5/116, simulation 55개, environment 23개, raw-manifest preflight 2개를 재실행해 모두 통과했다.
- assurance manifest 1.2.0은 22 case 중 21개 평가, 공격 실행 47개, control 4개, failure 0, False PASS 0이며 실제 GCP `ASR-D02` 1개는 `NOT_EVALUATED`다.
- 실제 브라우저에서 WATCHDOG `1/1/60`, TMR `0.1/0.028`, SEL `1+1/2/32` 전환과 `VALID / NOT_EVALUATED / HOLD`, warning/error 0을 확인했다.
- 발표용 `.slide4-note`는 1280×720, 1440×900, 1920×1080 모두 line count 1, document horizontal overflow 0이었다.
- 추가 유효 경계값 TMR `p=0.001`은 production에서 `processing_status=VALID`, result schema error 0, projection `2.998e-06`과 output hash `sha256:f52e...d76`을 생성했다. 브라우저는 같은 number를 `0.000002998`로 직렬화해 `sha256:e7e2...791`을 계산하고 정상 record를 `ready=false`로 거부했다.
- 원인은 Python과 JavaScript의 JSON number lexical representation 차이이며, 현재 path별 integer-to-float 보정만으로 production canonical bytes를 일반적으로 재현할 수 없다.

### 판정

H07은 `CHANGES_REQUESTED`다. stale-hash False PASS와 발표 문구 줄바꿈은 해소됐지만 schema-valid production result를 오탐 거부하는 canonical parity 결함이 남아 있다. H05의 기존 `VERIFIED` 기준선은 유지한다.

## H07 Runtime Result Integrity Remediation — 2026-08-20

### 구현

- `demo/product.html`이 root `output_hash`를 제외한 runtime result 본문을 재귀 key 정렬, compact separator, UTF-8 규칙으로 canonicalize하고 self-contained SHA-256으로 검증한다.
- 재계산 content hash와 `result.output_hash` 비교가 필수이며 sibling integrity anchor는 보조 검사로 유지한다.
- 정적 runtime 영역은 검증 전부터 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, 수치·ID·hash `—`로 시작한다. 정상 검증을 통과한 record만 화면 model에 투영된다.
- 개별 record 검증 실패는 해당 method만 닫으며 다른 정상 runtime record와 H05 radiation result는 유지한다.
- WATCHDOG/TMR/SEL 계산식, downtime 합산, policy threshold는 브라우저에서 계산하지 않는다.
- `demo/index.html`의 지정 안내 문구에 `slide4-note` class를 부여해 공통 `.lead`를 바꾸지 않고 desktop에서 `max-width:none; white-space:nowrap`을 적용했다. 900 px 이하에서는 안전한 줄바꿈을 허용한다.

### 결함 재현과 공격 결과

- 수정 전: WATCHDOG `downtime_total_seconds`만 `60 → 999`로 바꾸고 기존 result/sibling hash를 유지하면 `ready=true`, `downtime=999`가 관측됐다.
- 수정 후 projection 본문만 변조, policy만 변조, stable code만 변조, projection+sibling anchor 변조, projection+result/sibling hash를 같은 format-valid 가짜 값으로 변조한 경우 모두 대상 record가 `ready=false`로 닫혔다.
- 실패 record는 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`, projection `null`, result ID와 input/output hash `—`로 관측됐다.
- runtime result의 object key 순서만 역전한 동일 content는 세 canonical production hash와 일치하며 정상 통과했다.

### H07 검증 결과

- Product binding 9 tests 통과. exporter 2회 byte-identical, JSON/wrapper 동일성, production API/schema exact match, canonical content hash, 모든 H07 mutation과 검증 전 정적 비노출을 포함한다.
- schema 14개, valid fixture 5개, invalid fixture 116개 통과.
- simulation 55 tests, environment 23 tests, raw-manifest preflight 2 tests 통과.
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 공격 실행 47개, control 4개, failure 0, false pass 0, `NOT_EVALUATED` 1.
- JavaScript syntax와 원격 runtime dependency 0 검사 통과.
- `git diff --check` 통과.
- 생성 JSON SHA-256 `83275c83ad1dd1f6e81a0b372c4c5f6a45760fa2d4ba279e52481531f14078d9`, JS SHA-256 `c63565b46438200da5df82d4b8c810adbb7a260efc6bd8f8097416a22cf75c97`.
- 변경된 발표 HTML SHA-256 `96e87c621f49e039a6997a1bbd0fa7d79baa2a17cbcb853b57c85c43318ba5e5`.

### 작업 채팅 미실행 항목과 Control Tower 보완

- 작업 채팅은 로컬 `file://` 보안 정책 때문에 실제 viewport·console을 재현하지 못했지만, Control Tower가 `demo/`만 임시 localhost로 제공해 독립 검증했다.
- 세 desktop viewport의 `.slide4-note` line count 1, horizontal overflow 0과 Product UI warning/error 0은 확인됐다.
- 남은 제한은 실제 browser viewport가 아니라 위 Python/JavaScript canonical number parity다.
- `CONTRACT_CHANGE_REQUEST`: 없음. production runtime calculator, schema, Assurance 파일은 읽기 전용으로 유지했다.

## H06 Control Tower 독립 검증 — 2026-08-20

- Product binding 9개, schema 14/5/116, simulation 55개, environment 23개, raw-manifest preflight 2개를 재실행해 모두 통과했다.
- assurance manifest 1.2.0은 22 case 중 21개 평가, 공격 실행 47개, control 4개, failure 0, False PASS 0이며 실제 GCP `ASR-D02` 1개는 `NOT_EVALUATED`다.
- WATCHDOG record의 `computed_projection.downtime_total_seconds`만 `60`에서 `999`로 바꾸고 기존 `result.output_hash`와 sibling integrity anchor를 그대로 둔 독립 공격에서 UI consumer가 `ready=true`와 변조된 `999`를 반환했다.
- 현재 consumer는 sibling anchor와 result의 hash 문자열이 같은지만 확인하고 runtime result 본문으로부터 canonical SHA-256을 다시 계산하지 않는다. 따라서 형식상 정상인 stale hash가 content integrity를 증명하지 못한다.
- 보완 회차는 브라우저에서 production canonical 규칙으로 본문 hash를 독립 검증하고, 검증 전 수치를 렌더링하지 않으며, 실패 record만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫아야 한다.
- 발표용 `demo/index.html`의 SEL·SEB·SEGR 근거 안내 문구는 넓은 화면에서 한 줄로 보이도록 전용 text box 폭도 함께 보완한다.

### 판정

H06는 `CHANGES_REQUESTED`다. H05 Product result binding의 `VERIFIED` 기준선에는 영향을 주지 않으며, 수정 회차도 완료 상태 상한은 `READY_FOR_REVIEW`다.

## H06 Runtime Mitigation Result Binding — 2026-08-20

### 구현

- `demo/build_product_data.py`가 `evaluate_runtime_mitigation()`을 세 Workstream 20 fixture에 직접 호출한다.
- 기존 H05 payload에 명시적 `runtime_mitigation_results` collection을 추가하고 각 record에 fixture reference, 필요한 control input, integrity anchor와 production result 전체를 보존한다.
- result에는 method, equation ID, result ID, processing/engineering/assurance, data class, normalized counts, computed/declared projection 비교, policy evaluation, stable error codes, input/output hash가 원형 그대로 들어간다.
- Product UI의 “수치 변화” 단계에 `방사선 수치 / Runtime 완화` 보기를 추가했다. 기존 방사선 경로는 기본값으로 유지하고 runtime 보기에서 WATCHDOG·TMR·SEL 보호를 선택한다.
- 세 runtime 결과 모두 수치 바로 위에 `SYNTHETIC / NOT_EVALUATED / HOLD`를 표시한다. `VALID` 계산 결과를 assurance support로 표현하지 않는다.
- stable error code는 사람이 읽는 다음 행동과 짝지어 표시하지만 새 판정·근거·추천을 만들지 않는다.
- 브라우저는 production projection을 포맷해 표시할 뿐 WATCHDOG/TMR 공식, downtime 합산, policy threshold를 재계산하지 않는다.

### 정규 runtime 기준선

| method | equation / result | projection | 상태 |
|---|---|---|---|
| WATCHDOG | `WATCHDOG_TRUE_FALSE_PATH_V1` / `runtime-56ed7f4695cfe899` | false activation 1, reboot 1, downtime 60 s | `VALID / NOT_EVALUATED / HOLD` |
| TMR | `TMR_3P2_MINUS_2P3_V1` / `runtime-14be42f0ba024e6a` | p=0.1, system failure probability 0.028 | `VALID / NOT_EVALUATED / HOLD` |
| SEL_PROTECTION | `SEL_TRUE_FALSE_PATH_V1` / `runtime-6363f78ef979b057` | true 1 + false 1, power cycles 2, downtime 32 s | `VALID / NOT_EVALUATED / HOLD` |

세 record의 `data_class`는 `SYNTHETIC`이다. policy는 `DRAFT`, approval/evidence eligibility는 false이며 stable codes는 `BLOCKING_EVIDENCE_GAP`, `MITIGATION_APPLICABILITY_UNRESOLVED`, `NON_EVIDENTIARY_MITIGATION`, `NON_EVIDENTIARY_POLICY`, `POLICY_NOT_APPROVED`다.

### Fail-closed binding

- collection 누락·method set 불일치·unknown method는 runtime collection 전체를 unavailable로 처리한다.
- 개별 record의 schema/runtime version, engine, method, result/equation ID, projection, declared comparison, policy summary, status/data class, stable codes, input/output hash 또는 integrity anchor가 손상되면 해당 record의 수치·ID·hash를 숨긴다.
- 모든 runtime fallback은 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`이며 다른 정상 record와 기존 H05 radiation result는 유지된다.
- Runtime result ID·hash·projection은 HTML에 중복 하드코딩하지 않는다.

### H06 테스트 범위

- exporter 2회 byte-identical과 저장 JSON/JS exact match
- JSON-wrapper payload 동일성
- 세 runtime result schema 통과
- production API 재호출 결과와 payload result/projection/ID/hash exact match
- WATCHDOG·TMR·SEL exact control 값 검증
- UI consumer의 세 method 선택 model과 metrics 투영
- collection 누락, 개별 projection 손상, unknown method, valid-shape hash 변조, optimistic assurance, schema version drift 공격의 fail-closed 결과
- 기존 MVP/scope/EvidencePacket/Change Impact H05 테스트 유지
- JavaScript syntax, 원격 runtime dependency 0, 발표용 `demo/index.html` SHA-256 불변

### H06 실행 결과

- Product binding 9 tests 통과
- schema 14개, valid fixture 5개, invalid fixture 116개 통과
- simulation 55 tests 통과(그중 runtime calculator 24 tests 포함)
- environment 23 tests 통과
- assurance manifest 1.2.0: 22 cases, 21 evaluated, 47 attack executions, 4 controls, failures 0, false passes 0, `NOT_EVALUATED` 1
- raw manifest preflight 2 tests 통과
- exporter 2회 JSON/JS 및 저장 artifact `cmp` 동일
- JSON SHA-256 `83275c83ad1dd1f6e81a0b372c4c5f6a45760fa2d4ba279e52481531f14078d9`
- JS SHA-256 `c63565b46438200da5df82d4b8c810adbb7a260efc6bd8f8097416a22cf75c97`
- `git diff --check` 통과
- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지

### 제한

- runtime 결과는 합성 fixture의 결정론적 control이며 실제 mitigation 성능이나 방사선 assurance 증거가 아니다.
- 자동 생성 정적 artifact이며 backend, 실제 evidence ingestion, GCP 저장은 없다.
- `CONTRACT_CHANGE_REQUEST`: 없음. Workstream 20 runtime calculator와 공통 schema는 읽기 전용으로 사용했다.

## H05 Product Result Binding — 2026-08-20

### 구현

- `demo/build_product_data.py`가 기존 `run_mvp_decision()`을 실행해 MVP baseline/variant 전체 결과를 보존한다.
- 같은 exporter가 기존 `run_simulation()`으로 1 mm, 4 mm, 범위 밖 5 mm scope 결과를 생성한다. 2 mm ECC OFF/ON은 MVP baseline/variant가 authoritative source이며 새 mitigation 계약을 예상하지 않는다.
- 하나의 payload를 key-sorted compact JSON으로 직렬화해 `demo/data/mvp-product-result.json`과 `globalThis.SPECTRA_MVP_PRODUCT_RESULT=...` wrapper를 함께 생성한다.
- exporter는 현재 시각, UUID, 머신별 절대 경로를 추가하지 않는다. engine fixture의 고정 `created_at`과 content-derived ID만 보존한다.
- `demo/product.html`은 로컬 wrapper를 읽어 case ID, baseline/variant, run/result ID, processing/engineering/assurance, TID/SEU metrics, blocking gaps, EvidencePacket ID, Change Impact ID와 invalidation을 표시한다.
- 브라우저는 값을 포맷하고 선택된 정규 record를 표시할 뿐 물리 계산·보간·외삽·임계값·정책 판정을 수행하지 않는다.
- payload 누락, 구조 손상, assurance 불변식 위반 또는 5 mm fail-closed 불변식 위반은 수치와 ID를 모두 숨기고 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다.

### H05 생성 기준선

| 구분 | ID | processing | engineering | assurance | 주요 결과 |
|---|---|---|---|---|---|
| MVP 전체 | `mvp-cb826edb88ea5b67` | `VALID` | `NOT_EVALUATED` | `HOLD` | case `mvp-synthetic-ecc-policy-001` |
| baseline · 2 mm ECC OFF | `result-2ac48c19edb2f179` | `VALID` | `NOT_EVALUATED` | `HOLD` | TID 6.0, residual 0.063072 |
| variant · 2 mm ECC ON | `result-619f2bd08363a162` | `VALID` | `NOT_EVALUATED` | `HOLD` | TID 6.0, residual 0.013072 |
| scope · 1 mm ECC ON | `sim-d5a72077d684f459` | `VALID` | `PASS` | `HOLD` | TID 8.0 |
| scope · 4 mm ECC ON | `sim-ddf29f8ab807196d` | `VALID` | `PASS` | `HOLD` | TID 3.5 |
| scope · 5 mm ECC ON | `sim-27e031f2388ab6fc` | `OUT_OF_MODEL_SCOPE` | `NOT_EVALUATED` | `HOLD` | metrics 없음 |

MVP variant의 수치 규칙 일부는 `PASS`지만 aggregate `engineering_gate`는 `NOT_EVALUATED`이며 assurance는 `HOLD`다. H04의 수기 Stage 2 ECC snapshot `0.0063072`를 Product UI의 2 mm variant 결과로 더 이상 사용하지 않는다. 발표용 `demo/index.html`의 동결 snapshot은 변경하지 않는다.

### H05 자동 검증

- Workstream 80 전용 테스트는 exporter 2회 byte 동일성, JSON-wrapper payload 동일성, MVP/simulation schema와 EvidencePacket semantic gate, UI consumer의 실제 payload 투영, 누락·손상 fallback, authoritative ID·metrics 중복 하드코딩 금지, JavaScript syntax, 원격 런타임 의존성 0을 검증한다.
- 기준 커밋 clean archive에 H05 소유 파일만 적용한 독립 실행에서 Product binding 7개 테스트가 통과했다.
- 같은 clean archive의 schema, simulation, environment, assurance, raw-manifest preflight 전체 회귀 결과는 H05 handoff에 명령과 실제 결과를 기록한다.
- 작업 트리에는 H05 시작 전부터 다른 Workstream이 수정 중인 공통 schema가 있으며, H05는 이를 수정·복원하지 않았다. 현재 작업 트리 회귀와 clean-baseline 회귀는 분리해서 기록한다.
- 발표용 `demo/index.html` SHA-256은 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880`이다.

### 남은 제한

- 브라우저 viewport·console·실제 `file://` 조작은 이용 가능한 브라우저 제어 경로가 있을 때 재확인해야 한다.
- JSON/JS는 정적 build artifact이며 자동 refresh, backend, HTTP API, 실제 evidence ingestion은 없다.
- `CONTRACT_CHANGE_REQUEST`: 없음. H05는 공통 계약을 변경하지 않았다.

## H04 초심자 가시성 보완 — 2026-08-20

### 정보 구조 변경

- 단계명을 `검토 조건 / 수치 변화 / 보증 판단`으로 한국어 우선 표시하고 영문은 보조 표기로 이동
- 각 단계 최상단에 5초 안에 읽는 질문과 한 문장 답 배치
  - “어떤 임무와 부품을 검토하나요?”
  - “차폐와 ECC가 어떤 값을 바꾸나요?”
  - “수치 조건을 통과해도 왜 HOLD인가요?”
- `차폐 후 누적선량(TID)`, `완화 전 오류(SEU)`, `완화 후 잔여 오류`처럼 용어 바로 옆에 한국어 뜻 표시
- 차폐·ECC·5 mm 조작 직후 다음 해석 문장을 수치 카드 위에 크게 갱신
  - TID `8 → 6 → 3.5 krad` 감소
  - ECC 잔여 SEU `0.063072 → 0.0063072` 감소
  - 5 mm는 지원 범위 밖이라 값 추정 안 함
- 보증 판단을 `합성 수치 조건 통과 → 실제 근거 부족 → 판단 보류(HOLD) → 증거 4가지 확보` 인과 흐름으로 연결
- 기존 5행 Evidence Coverage와 별도 Action Plan을 환경·BOM identity·시험 원문·파괴성 SEE의 `공백 ↔ 다음 행동` 네 쌍으로 통합
- run ID·model·합성 policy approval은 접힌 “기술 세부정보”로 이동

### 가독성 경계

- 핵심 질문 27px 이상, 답 16px 이상, 카드 제목·상태 13px 이상, 보조문구 12px 이상
- 10px는 footer의 비핵심 메타정보에만 사용하고 9px·11px 일반 텍스트 제거
- 보조색을 `#929ca4`로 높여 기본 배경 `#050607` 대비 계산값 7.26:1 확보
- 1280×720에서는 글자를 줄이지 않고 contract note·상세 설명·기술 상세 본문을 후순위로 숨김

### H04 자동 검증

- 질문 3/3, 동적 해석 핵심문 3/3, 기술 용어 인접 한국어 설명 확인
- 검증된 run ID 5/5 exact match, assurance `HOLD` 5/5
- JavaScript syntax 통과, remote request API·지원 판정 승격 token 0
- schema 14개·정상 fixture 3개·실패 fixture 83개 통과
- simulation 19개와 비교 scenario 통과
- assurance 21 case: 19 evaluated PASS, 2 `NOT_EVALUATED`, failure 0, false pass 0
- `git diff --check` 통과
- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- 1280×720·1440×900 overflow, interaction, Reset, console error: Chrome 검증 필요

### H04 Control Tower 독립 검증 — 2026-08-20

- 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- `demo/product.html` inline script 2개 syntax 통과, 원격 reference 0, 고정 run ID 5개, 필수 한국어 label과 해석 문장 확인
- 9~11px 규칙은 footer용 10px 1개만 남고 핵심 문구에서 제거됨
- schema 14개·정상 fixture 3개·실패 fixture 83개 통과
- simulation 19개와 5개 합성 비교 scenario 통과
- assurance 21 case 중 19 evaluated, 2 `NOT_EVALUATED`, False PASS 0
- `git diff --check` 통과
- 사용자가 실제 UI의 단계 이동과 조작을 확인하고 현재 가시성을 프로토타입 기준선으로 수용함
- Workstream 90의 H02 준비 과정에서도 1·2·4·5 mm, ECC 미적용/적용, 단계 이동, Reset, 모든 최종 `HOLD`와 browser warning/error 0을 실제 조작으로 재확인함

실제 Chrome의 지정 viewport overflow는 Control Tower가 독립 캡처하지 못했다. console warning/error 0과 전체 조작은 Workstream 90의 H02 준비 과정에서 재확인했다. 이후 멘토링 피드백이 들어오면 같은 채팅 80에서 새 UI 작업 패키지로 개선한다.

발표용 `demo/index.html`은 동결하고, 별도 `demo/product.html`에 Evidence-to-Decision Workspace를 구현했다. H01·H02 검증 이력은 아래에 보존한다. H03의 기능·snapshot·fail-closed 정적 계약은 통과했지만 실제 viewport·interaction·console 검증이 없고, 도메인 초심자 관점에서 정보 위계와 가시성이 부족해 H04 보완 전에는 `READY_FOR_REVIEW`로 승격하지 않는다.

## H03 Control Tower Review — 2026-08-20

- `demo/product.html` 존재와 발표용 `demo/index.html` SHA-256 `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지 확인
- inline script 2개 syntax 통과, 원격 reference 0, 고정 run ID 5개 확인
- schema 14개·정상 fixture 3개·실패 fixture 83개, simulation 19개, assurance 21 case 중 19 evaluated·2 `NOT_EVALUATED` 재실행 통과
- 1·2·4·5 mm, ECC ON/OFF, 최종 `HOLD`, JavaScript fallback 계약 확인
- 인앱 브라우저의 `file://` 접근이 보안 정책으로 차단되어 Control Tower의 실제 viewport·console 검증은 수행하지 못함
- 소스에 9~11px font-size 규칙이 15개 있고 영문 전문용어와 낮은 대비 보조문구가 많아, 주요 상태와 의미를 초심자가 빠르게 읽기 어렵다는 사용자 피드백을 재현 가능한 개선 요구로 수용

### H04 변경 방향

- 한국어 결론을 먼저 표시하고 영문 계약명은 보조로 둔다.
- 각 단계에서 “무엇을 입력했나 / 무엇이 달라졌나 / 왜 HOLD인가 / 다음에 무엇을 해야 하나” 중 하나를 가장 크게 보여 준다.
- 작은 글자·낮은 대비·동일한 카드 위계를 줄이고 기술 세부정보는 후순위로 이동한다.
- 발표용 `index.html`, 고정 snapshot과 fail-closed 동작은 변경하지 않는다.

## H03 Product UI Prototype

### 구현

- 슬라이드가 아닌 단일 application shell과 `Scenario → Analysis → Assurance` 3단계 workflow
- 합성 LEO 임무, 단일 부품 exact identity fixture, 승인 BOM 0건 표시
- 1·2·4·5 mm 차폐 선택과 2 mm 전용 ECC ON/OFF 비교
- 검증된 다섯 run만 소비하고 물리 계산·보간·외삽·판정을 브라우저에서 수행하지 않음
- 1·4·5 mm에서는 ECC OFF를 비활성화해 검증되지 않은 조합 생성 차단
- 5 mm는 값 없이 `OUT_OF_MODEL_SCOPE / NOT_EVALUATED / HOLD`
- Evidence Coverage에서 실제 환경 출력, 승인 BOM, 시험 원문, 파괴성 SEE와 실제 policy approval 공백 노출
- 환경 출력 확보 → exact identity 확인 → 권리 확인 원문 연결 → 파괴성 SEE 근거/시험 계획의 Action Plan
- stepper·이전/다음·숫자키 1/2/3·Alt+방향키와 `Reset demo` 지원
- JavaScript 미실행 시 `SYNTHETIC / NOT PHYSICAL EVIDENCE / ASSURANCE: HOLD` 안전 fallback

### H03 자동 검증 — 2026-08-20

- `demo/product.html`: 3개 단계, 다섯 엔진 run ID와 표시값 exact match
- 외부 CDN·font·asset·network API 0, assurance 승격 token 0
- JavaScript syntax: bundled Node.js `--check` 통과
- `demo/index.html` SHA-256: `e49568a6d05e15d37427679fd784c86803c4f2b7f291d057f3fb26403deeb880` 유지
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py`: simulation 19개와 비교 scenario 통과
- `git diff --check`: 통과
- 1280×720·1440×900 overflow, 전체 조작, Reset, console error: 브라우저 검증 필요

기존 오프라인 HTML 데모의 사실·snapshot·조작 계약을 유지하면서 7분 발표용 한글 타이포그래피와 상태 표현을 정제했다. 별도 handoff는 없지만 Control Tower가 실제 산출물을 직접 재현해 H02 패키지를 검증했다. 이 판정은 발표 UI에 한정되며 Stage 8 전체 통합 완료를 뜻하지 않는다.

## H02 변경

- 한글 본문 stack을 `Apple SD Gothic Neo`, `Noto Sans KR`, system sans-serif 순서로 조정
- 제목 weight를 500으로 낮추고 자간 `-0.025em`, 행간 `1.14`, 최대 크기·너비를 함께 축소
- 첫 화면 제목–본문 여백 확대, 720px 높이 전용 제목·카드 밀도 보정
- 좌측 원형·사선 brand mark 제거, 상단 `SPECTRA` 텍스트만 유지
- 우측 상단 전역 상태 badge 제거
- 6번 화면에 `SYNTHETIC / NOT PHYSICAL EVIDENCE / ASSURANCE: HOLD` 전용 상태 설명 추가
- 2번 하단 문장을 “승인 BOM 0건. 화면의 부품 identity는 합성이며, 실제 추천이 아닙니다.”로 축약하고 1280px 이상 한 줄 유지
- 기존 7개 화면, wheel·키보드·버튼, 정적 fallback과 모든 합성 snapshot 유지

## H02 자동 검증 — 2026-08-20

- HTML 정적 계약: 7개 화면, brand mark 0, 전역 badge 0, 전용 assurance 상태 3/3, 원격 asset 0
- JavaScript syntax: bundled Node.js `--check` 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py`: simulation 19개와 5개 비교 scenario 통과
- `git diff --check`: 통과
- 브라우저 1280×720, 1440×900, 1920×1080: 7개 화면 overflow 0, 2번 문장 밀림 0
- wheel 01→02, Home/End 01↔07, 버튼 이동, console error 0 확인
- 5 mm `OUT_OF_MODEL_SCOPE/HOLD`, ECC OFF/ON `0.063072`/`0.0063072` exact match
- 별도 screenshot·handoff 제출은 없으며, 실제 7분 발표 시간은 발표자 리허설로 한 번 측정해야 한다.

## 구현 범위

- `demo/index.html`: 7개 화면 self-contained 발표 데모
- `demo/README.md`: 실행법, 발표 흐름, 신뢰성 경계, 내장 snapshot
- 좌우 키·Page Up/Down·Space·마우스·트랙패드 스크롤·화면 버튼 이동과 진행 표시
- 1·2·4 mm 및 범위 밖 5 mm 고정 snapshot 비교
- ECC ON/OFF 고정 snapshot 비교
- JavaScript 미실행 시 전체 화면 정적 fallback

## 소비한 합성 기준선

| 시나리오 | run ID | 핵심 결과 |
|---|---|---|
| 1 mm + ECC | `sim-d5a72077d684f459` | TID 8.0, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 2 mm + ECC | `sim-3cc00f2c824db56d` | TID 6.0, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 4 mm + ECC | `sim-ddf29f8ab807196d` | TID 3.5, residual SEU 0.0063072, `VALID/PASS/HOLD` |
| 2 mm + no ECC | `sim-b74d7317282b2a82` | raw=residual SEU 0.063072, `VALID/PASS/HOLD` |
| 5 mm + ECC | `sim-27e031f2388ab6fc` | 값 없음, `OUT_OF_MODEL_SCOPE/NOT_EVALUATED/HOLD` |

브라우저는 이 결과를 표시만 하며 물리식·보간·외삽·판정을 JavaScript로 재구현하지 않는다.

## 신뢰성 경계

- 합성 fixture의 수치·identity·SEL 표시는 실제 환경·부품·시험 증거가 아니다.
- `engineering_gate=PASS`는 합성 수치 조건 비교일 뿐 보증 PASS가 아니다.
- 모든 선택에서 assurance `HOLD`와 `SYNTHETIC`이 유지된다.
- 실제 환경 모델 run, 승인 BOM, 시험 원문·수치·artifact, policy operand와 GCP resource는 0이다.
- 실제 path는 provenance-complete 환경 출력, 승인 BOM과 event별 원문, rights gate, 독립 assurance, 이후 GCP 저장·감사 실행 순서다.

## Control Tower 독립 검증 — 2026-08-20

- `python3 tests/schema/validate_contracts.py`: schema 14개, 정상 fixture 3개, 실패 fixture 83개 통과
- `python3 tests/simulation/run_all.py`: simulation 19개 통과, 5개 시나리오 snapshot exact match
- 브라우저 7개 화면, 버튼·키보드·스크롤 전환과 console error 0 확인
- 1440×900 및 1920×1080에서 7개 화면의 가로·세로 overflow 0 확인
- 5 mm 입력은 값 없이 `OUT_OF_MODEL_SCOPE`; ECC OFF/ON은 `0.063072`/`0.0063072`로 전환되고 assurance `HOLD` 유지
- 외부 URL, CDN, 원격 asset, `fetch`, WebSocket 없음
- 흑백 중심 visual hierarchy와 축약 문구를 적용해 발표 화면의 텍스트 밀도를 낮춤

작업 채팅의 별도 handoff와 screenshot 폴더는 제출되지 않았다. 실제 산출물은 독립 재현 가능하므로 데모 패키지는 `VERIFIED`로 판정하지만, Stage 8의 실제 API·EvidencePacket·원문 연결과 변경 영향 UI는 여전히 미구현이다. commit·push하지 않았다.
