# SPECTRA Offline HTML Demo

## H27 3-Step Roadmap Demo 실행 안내

`roadmap-lab.html`은 발표 직후 40초 안에 제품을 이해시키는 세 단계 guided demo다. 기존 7개 기능 카드는 주 화면에서 제거하고 `자료 연결 → AI 보조 검토 → 판단과 다음 행동`만 남겼다. 발표 자료와 같은 검은 배경·큰 제목·얇은 구분선·흰색 선택 상태를 사용한다.

| 시연 단계 | 발표자가 말할 핵심 | 화면 결론 |
|---|---|---|
| 01 자료 연결 | 계산 전에 환경·부품·권리 identity를 확인한다. | `아직 계산하지 않음 / HOLD` |
| 02 AI 보조 검토 | AI 값은 증거가 아니라 source-bound 검토 후보다. | `REVIEW_REQUIRED / HOLD` |
| 03 판단과 다음 행동 | 변경 영향과 남은 근거 공백을 함께 보여 준다. | `FINAL ASSURANCE / HOLD` |

각 단계에서는 제목과 오른쪽 `SPECTRA ANSWER`만 설명한다. 기존 7개 상세 route는 삭제하지 않고 오른쪽 아래 `Q&A ↗` 링크로만 제공한다. 본 발표에서 열지 않는다.

저장소 루트에서 localhost를 loopback에만 bind한다.

```bash
cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8765/demo/roadmap-lab.html`을 열고 하단 `다음` 버튼을 두 번 누른다. 마지막 화면의 `처음부터 다시 보기`로 초기 상태를 복원한다.

직접 테스트:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_evidence_source_intake
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_cots_candidate_library
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_document_review_workflow
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_ai_processing_readiness
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_change_impact_demo
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_cad_linkage_readiness
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_security_posture
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_roadmap_lab
```

이 묶음에는 실제 SPENVIS/NASA connector, production COTS library, Document AI/Gemini API 호출, authenticated HITL, 실제 CAD parser·3D shielding 계산, KMS 서명 운영 또는 penetration test가 없다. guided demo와 상세 화면의 로컬 test 통과는 실제 environment/part contract, suitability 또는 방사선 assurance 완료를 뜻하지 않는다.

## H19 Readiness Receipt Integration

`workspace.html`은 공용 `readiness-receipt.schema.json` dispatcher의 v1 두 종류를 별도 upstream test module import 없이 로컬 파일 선택 경로에서 읽는다. 예시는 `data/readiness-environment-hold-v1.json`과 `data/readiness-part-contract-not-implemented-v1.json`이다.

- Environment v1은 `HOLD_NOT_ISSUED`, Part v1은 `CONTRACT_NOT_IMPLEMENTED`만 표시한다.
- source class/purpose, processing 상태, blocker code와 blocker별 담당 역할·다음 행동만 표시한다.
- receipt ID, source record ID, 공학 수치, suitability, actual output reference와 낙관 판정은 표시·export하지 않는다.
- unknown version·kind, cross-kind field, malformed nested type, 빈 blocker, `PASS` blocker, issuance/implementation/decision-use/assurance 상향은 식별자와 세부값을 숨긴 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫는다.
- 이 receipt는 실제 environment/part contract 본문이나 assurance evidence가 아니다. 실제 contract와 실제 evidence는 계속 0건이다.

## H18 Evidence Review Workspace

`workspace.html`은 발표 deck·Product prototype과 분리된 오프라인 evidence readiness 검토 화면이다. 사용자가 `data/review-workspace-synthetic.json`처럼 H18 로컬 intake 형식에 맞는 JSON을 명시적으로 선택하면 브라우저 메모리에서만 읽고, Environment·Exact Part·TID·SEL·SEB·SEGR·Rights·Scientific Crosscheck의 coverage와 blocking gap 담당 역할·다음 행동을 표시한다.

```bash
cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8765/demo/workspace.html`을 연 뒤 **로컬 JSON 열기**로 sample을 선택한다. `file://`에서도 외부 요청 없이 동작하지만, viewport·console 검토에는 localhost가 편리하다. 입력은 업로드·저장하지 않으며 Reset은 식별자와 export 링크를 지운 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 돌아간다.

이 화면의 `STRUCTURE_VALID`는 로컬 입력 형식을 읽었다는 뜻일 뿐 evidence 인증이나 assurance 결론이 아니다. 현재 실제 environment/part contract는 0건이며 `ACTUAL` 자기 선언, 인증되지 않은 issuance claim, unknown status, 중복 gap ID, 잘못된 nested type과 낙관 판정은 모두 세부값을 숨기고 `HOLD`로 닫는다. Audit export는 coverage status, stable gap code, owner role, action code와 fail-closed decision만 포함하며 case identity·설명 원문·raw evidence·로컬 경로·개인정보·실제 공학 수치는 제외한다.

직접 테스트:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_evidence_review_workspace
```

## 현재 기준선 — 2026-08-24

- `index.html`은 `Cover + 01~11 + Closing`, 총 13장의 현재 발표 deck이다. localhost 1280×720에서 전 장 overflow 0, console warning/error 0과 키보드·버튼·두께·ECC·GCP snapshot 상호작용을 Control Tower가 확인했다.
- Slide 10의 `TRUST & INTEGRITY`는 private IAM·input binding의 고정 GCP snapshot 범위와 자체 승인·낙관 승격·fail-closed의 로컬 회귀 범위를 함께 요약한다. 침투시험, KMS 서명 배포, 전체 보안 완성 또는 실제 방사선 보증을 뜻하지 않는다.
- `product.html`은 발표본과 별도의 5단계 제품 프로토타입이다. Product 직접 테스트 16개와 JavaScript syntax는 통과했지만 최신 H17의 실제 viewport 검증은 완료되지 않아 후보 상태다.
- 두 화면의 방사선 수치는 generated `SYNTHETIC` 결과이며 실제 환경·부품 assurance가 아니다. 5 mm와 손상·불일치 입력은 값을 만들지 않고 `NOT_EVALUATED/HOLD`로 닫는다.
- GCP 화면은 H05 Control Tower verified snapshot을 읽기 전용으로 표시한다. 버튼은 Workflow Console을 열지만 HTML이 새 실행을 트리거하거나 live 상태를 assurance로 해석하지 않는다.
- 아래 H02~H17 절은 구현 이력이다. 현재 동작이나 상태가 충돌하면 이 기준선, Control Tower `CURRENT.md`, generated payload 순서로 판단한다.

Workstream 80 오프라인 데모는 서버, 외부 폰트·asset 없이 로컬 snapshot wrapper로 동작한다. 발표 deck은 localhost 사용을 권장한다.

## 실행

Finder에서 `demo/index.html`을 더블클릭하거나 브라우저의 **파일 열기**로 연다. 로컬 서버는 필요 없다.

- `←` / `→`: 이전·다음 화면
- `Page Up` / `Page Down`, `Space`: 화면 이동
- 마우스·트랙패드 위/아래 스크롤: 이전·다음 화면
- 화면 아래 버튼: 이전·다음 화면
- 환경·차폐 화면: 엔진이 이미 검증한 1·2·4 mm와 범위 밖 5 mm snapshot 선택
- 부품·완화 화면: 2 mm 고정 ECC ON/OFF snapshot 선택
- 새로고침: 첫 화면부터 재시작

## Legacy H02 발표 흐름 — 현재 13장 deck 이전 이력

| 화면 | 핵심 메시지 | 권장 누적 시간 |
|---:|---|---:|
| 1 | 끊어진 환경 계산–BOM–시험 PDF–완화·승인 | 0:45 |
| 2 | 합성 LEO 임무와 합성 단일 부품 identity | 1:30 |
| 3 | 1·2·4 mm 합성 TID와 5 mm `OUT_OF_MODEL_SCOPE` | 2:35 |
| 4 | TID/SEU 계산 가능성과 실제 파괴성 SEE 증거 공백 분리 | 3:30 |
| 5 | raw SEU와 ECC 적용 후 residual SEU 분리 | 4:30 |
| 6 | `engineering_gate=PASS`여도 assurance `HOLD` | 5:35 |
| 7 | H05 Multi-Agent GCP Workflow와 실패 시 `HOLD` | 6:30 |

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
- 실제 환경 모델 run, 승인 BOM, 시험 PDF와 실제 방사선 수치는 0이다. GCP는 H05 검증 snapshot만 표시하며 live 조회하지 않는다.
- JavaScript가 실행되지 않으면 7개 화면이 세로 문서로 모두 노출되는 정적 fallback이 동작한다.

## 내장 snapshot

| 시나리오 | run | shielded TID | raw SEU | residual SEU | processing | engineering | assurance |
|---|---|---:|---:|---:|---|---|---|
| 1 mm scope | `sim-d5a72077d684f459` | 8.0 | — | — | `VALID` | `PASS` | `HOLD` |
| 2 mm + ECC · MVP Core | `mvp-cb826edb88ea5b67` | 6.0 | 0.063072 | 0.013072 | `VALID` | `NOT_EVALUATED` | `HOLD` |
| 4 mm scope | `sim-ddf29f8ab807196d` | 3.5 | — | — | `VALID` | `PASS` | `HOLD` |
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

`product.html`은 발표 슬라이드가 아니라 5단계 `검토 조건 → 수치 변화 → 보증 판단 → GCP 실행 → 결과 전달 무결성` 제품 프로토타입이다. 아래 생성 파일을 로컬 `<script>`로 읽으므로 Finder에서 직접 열어도 핵심 경로가 동작한다.

- `data/mvp-product-result.json`: 검증과 향후 HTTP 소비를 위한 정규 JSON
- `data/mvp-product-result.js`: 같은 payload를 담은 `file://` 전용 전역 wrapper

## H16 H05 GCP Workflow snapshot

`build_gcp_snapshot.py`는 Workstream 70의 H05 evidence 세 파일을 읽어 하나의 정규 payload를 만들고, `data/h05-gcp-snapshot.json`과 `data/h05-gcp-snapshot.js`를 함께 생성한다. source path·source schema version·evidence의 마지막 관측 시각·canonical preimage·SHA-256을 보존하며, 생성 시각이나 로컬 절대 경로를 새로 만들지 않는다.

발표 07과 Product 04는 이 snapshot에서 project·region·Workflow revision, 세 Cloud Run Agent revision, 정상·위조·endpoint override execution, Storage·Logging·IAM·Core parity를 읽어 표시한다. Console 링크는 검증된 project/region/workflow로 연결하지만 로컬 HTML이 GCP API를 live 조회하는 것은 아니다. 실제 환경 run과 승인 BOM·시험 원문은 0건이고 비용은 `NOT_QUERIED`, 최종 보증 판단은 `HOLD`다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 demo/build_gcp_snapshot.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding
```

## H17 Core 값과 화면 정렬

발표 ECC 비교와 Product는 같은 generated MVP payload에서 `raw_seu=0.063072`, `residual_logical_errors=0.013072`를 읽는다. 과거 Stage 2 residual은 현재 발표 UI에서 사용하지 않는다. Product 05는 runtime WATCHDOG 값이 아니라 MVP Core variant의 Residual SEU가 전달 중 바뀌는 합성 사본을 기존 Core 기록과 대조하고, 불일치하면 숫자와 식별자를 숨긴 채 `HOLD`로 닫는다.

Product 보증 판단의 상·하 카드는 같은 4열 grid를 사용한다. 발표 07은 6단계 역할, GCP 배포 요약, 정상 `HOLD`와 변조 차단 `HOLD`만 주 화면에 표시하고 revision·execution·stable code는 접힌 기술 상세로 내린다.

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

`product.html`의 “수치 변화” 단계에서 `방사선 수치 / 고장 대응 방법`을 전환한 뒤 자동 재시작(WATCHDOG)·3중 다수결(TMR)·과전류 전원 보호(SEL 대응)를 선택한다. UI는 API가 반환한 `computed_projection`, policy evaluation, stable error codes, equation/result/packet ID와 input/output hash를 표시만 한다. TMR 공식, downtime 합산, policy threshold는 브라우저에서 재계산하지 않는다.

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

## H10 Assurance attack demo

`product.html`의 `수치 변화 → Assurance 공격`에서 H09 consumer의 fail-closed 동작을 약 60~90초로 조작할 수 있다.

1. 정상 WATCHDOG의 `false activation / reboot / downtime`, 상태와 ID·hash를 확인한다.
2. `공격 입력 만들기`를 눌러 원본이 아닌 고정 deep clone에서 downtime만 `60 → 999`로 바꾼 `UNTRUSTED` 미리보기를 만든다.
3. `동일 consumer로 검증`을 누르면 H09 `resolveProductData()`가 WATCHDOG만 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD`로 닫고 수치·ID·hash를 숨긴다.
4. TMR·SEL과 방사선 residual 유지 상태를 확인한 뒤 `정상 원본으로 Reset`한다.

공격 단계는 브라우저에서 공식, 정책 threshold 또는 hash를 다시 계산하지 않는다. production preimage·result output hash·sibling anchor를 그대로 둔 고정 clone을 기존 consumer에 전달할 뿐이다. `999`는 검증된 결과가 아니라 신뢰하지 않는 공격 입력 미리보기에서만 표시된다. 이 데모는 실제 공격자 인증·권한 모델, 암호학적 서명, 실제 방사선 assurance 또는 GCP 보안을 주장하지 않는다.

## H11 Deck wheel gesture와 초심자 문구

발표 deck의 wheel·trackpad 이동은 고정 시간 잠금 대신 **마지막 유효 wheel 이벤트 이후 180ms 무입력**을 한 gesture의 경계로 사용한다. 한 번 이동한 뒤 관성 이벤트가 620ms를 넘어 계속 들어오더라도 무입력 구간 전에는 추가 이동하지 않는다. 같은 stream의 짧은 반대 방향 노이즈도 즉시 되돌림으로 처리하지 않는다. `deltaY=0`에 가까운 trailing noise는 lock 생명주기를 연장하지 않으며, pixel/line/page delta mode를 UI 이동 단위로 정규화해 커서 이동 없이 일반 마우스 휠의 다음 독립 gesture도 받는다. 버튼, Arrow, Page Up/Down, Space, Home, End 동작은 유지된다.

03·04·06·07 화면에는 다음 오해를 닫는 짧은 한국어 문구만 보완했다.

- 설계계수 2는 `요구량 = 차폐 후 TID × 2` 관계이며 브라우저가 새 계산을 하는 것이 아니다.
- 이산 lookup은 등록된 1/2/3/4 mm만 쓰고, 5 mm는 물리적 불가능이 아니라 현재 합성 table 범위 밖이다.
- 합성 fixture 계산과 실제 보증 evidence를 분리한다.
- `PASS`는 합성 수치 조건에 한정되고 assurance는 계속 `HOLD`다.
- 파괴성 SEE 근거는 부품 기술과 정책상 필요한 event별 범위로 한정한다.
- 로컬 데모의 실측 GCP resource·호출·비용은 0이지만, 실제 배포 비용이 0이라는 뜻은 아니며 저장·실행·로그·전송 비용을 별도로 측정해야 한다.

## H12 독립 결과 검증 화면

H10의 공격 시연은 `02 수치 변화` mode에서 제거하고 독립된 `04 결과 검증` 화면으로 옮겼다. 현재 흐름은 다음과 같다.

1. `검토 조건`
2. `수치 변화`
3. `보증 판단`
4. `결과 검증`

3번 화면의 “그렇다면 화면에 들어온 결과 자체를 믿어도 될까요?” control로 4번에 진입한다. 4번 화면의 중심 원칙은 “화면에 들어온 숫자가 정상 계산 당시 기록과 다르면 그 숫자를 믿고 보여 주지 않는다”이다.

- `정상 계산 결과`: 자동 복구 감시 기능(WATCHDOG)의 합성 서비스 중단 시간 `60초`
- `변경된 테스트 결과`: 원본을 보존한 테스트용 사본에서 결과 파일 숫자 하나만 `60 → 999초`로 변경
- `Product 판단`: 원래 기록과 불일치하면 숫자·result ID·input/output hash를 숨기고 `결과 사용 불가(DATA_UNAVAILABLE) / 평가하지 않음(NOT_EVALUATED) / 판단 보류(HOLD)`

control은 `결과 숫자 바꾸기 → 원래 계산 기록과 대조 → 정상 결과로 되돌리기` 순서다. 내부 구현은 H10의 `createAttackDemoController()`와 H09 `resolveProductData()`를 그대로 사용한다. 새 검증기·공식·정책·hash 규칙을 추가하지 않았으며 reason code와 preimage/hash 용어는 접힌 `기술 상세`에만 둔다. 이는 Product runtime result의 부분 불일치를 fail-closed로 처리하는 합성 시연이며 전자서명·해커 방어·과학 정확성·GCP 보안 검증이 아니다.

## H13 native wheel 이동과 숫자 변경 감지

H11·H12의 커스텀 wheel controller는 폐기했다. 해당 controller는 wheel 이벤트 사이의 180ms 무입력만 제스처 종료로 추정했기 때문에 장치의 잔여·관성 이벤트와 다음 독립 입력 사이에 충분한 공백이 없으면 `locked`가 계속 유지될 수 있었다. wheel 이벤트에는 장치 공통의 신뢰 가능한 제스처 종료 신호가 없으므로 multiplier나 timer를 다시 조정하지 않고 브라우저 기본 세로 스크롤과 `scroll-snap-stop: always`를 사용한다. 앱은 wheel 이벤트를 가로채지 않으며, 진행 표시는 native scroll이 정착한 가장 가까운 장을 따라간다. 버튼, Arrow, Page Up/Down, Space, Home, End와 양 끝 clamp는 유지한다.

Product 4단계 화면명은 `숫자 변경 감지`로 바꿨다. 주 화면은 `계산 직후 기록 60초 → 화면에 들어온 테스트 값 999초 → 서로 다름 → 숫자 숨김 → 판단 보류(HOLD)`만 설명한다. control은 `테스트용 숫자 바꾸기 → 두 기록 비교하기 → 정상 상태로 되돌리기` 순서다. H10의 `createAttackDemoController()`와 H09 `resolveProductData()`는 그대로 재사용하며, preimage·hash·reason code는 접힌 기술 상세에만 남긴다. 확인 범위는 계산 모듈에서 받은 결과 파일의 부분 불일치를 그대로 표시하지 않는지에 한정되며 60초의 과학적 정확성, 전자서명, 프로젝트 전체 보안 또는 GCP 보안을 검증하지 않는다.

## H14 화면 중심 신뢰성 스토리

갱신된 H14는 H13의 native scroll-snap을 최종 UX로 채택하지 않는다. JavaScript 실행 시 한 화면만 활성화되는 고정 deck으로 복귀했으며 wheel 입력은 타이머 없이 event timestamp·delta·mode만 쓰는 bounded intent controller가 처리한다. 첫 이동 뒤 긴 관성은 한 장으로 제한하고, 다음 입력은 150ms quiet gap, 감쇠 뒤 1.8배 새 impulse, 반대 방향의 명확한 impulse 또는 이동 시점에서 연장되지 않는 900ms hard age 이후 새 threshold impulse로 re-arm한다. trailing event가 release timer를 계속 미루는 H11/H12 구조는 사용하지 않으며 pointermove·hover·focus도 조건에 포함하지 않는다. 실제 장치 trace와 01↔07 acceptance 전에는 이 동작을 검증 완료로 주장하지 않는다.

발표 deck의 06 화면은 전문 assurance 표 대신 네 가지 안전장치를 한 화면에 보여 준다.

1. `같은 입력 → 같은 결과`: 같은 고정 입력과 버전의 결과를 재현한다.
2. `지원 범위 밖 → 계산 안 함`: 등록되지 않은 5 mm를 보간·외삽하지 않는다.
3. `실제 근거 부족 → 판단 보류(HOLD)`: 합성 수치 조건이 PASS여도 실제 환경·승인 BOM·시험 원문이 0건이면 승인하지 않는다.
4. `전달된 숫자가 다름 → 숫자 숨김`: 계산 직후 60초와 화면 테스트 값 999초가 다르면 어느 값도 추측하지 않는다.

같은 화면의 `고정 합성 오류·공격 실행 47회 / 잘못 PASS한 경우 0`은 assurance manifest의 검증된 고정 합성 세트에만 적용된다. 실제 GCP, 실제 과학 정확성 전체 또는 모든 공격을 검증했다는 뜻이 아니다. 실제 환경·승인 BOM·시험 원문과 GCP resource는 계속 0이며 최종 assurance는 `HOLD`다.

Product `04 · 숫자 변경 감지`는 네 번째 안전장치의 상세 시연이다. 상단에 `신뢰성 안전장치 4/4 · 전달 중 숫자 변경`과 앞의 재현성·지원 범위·증거 공백 다음 단계라는 연결 문장을 표시한다. 주 카드에서는 `복구 중 서비스 중단 시간`을 먼저 설명하고 `WATCHDOG`는 접힌 기술 상세로 내렸다. H13의 세 카드·세 버튼과 기존 H10/H09 consumer 경로는 변경하지 않았다.

Product 02의 `Runtime 완화`는 `고장 대응 방법`으로 바꿨다. 선택지는 `자동 재시작(WATCHDOG)`, `3중 다수결(TMR)`, `과전류 전원 보호(SEL 대응)`이며 각 방법을 `문제가 생김 → 대응 동작 → 남는 영향·대가`로 설명한다. 자동 재시작의 재시작 횟수·중단 시간, TMR의 입력 확률·시스템 실패 가능성, SEL 대응의 전원 재시작·중단 시간은 기존 production runtime record에서 읽어 표시한다. stable code, processing/engineering 상태, equation/result/packet ID와 hash는 접힌 기술 상세에 둔다. 브라우저는 TMR 공식, downtime 합산 또는 정책 판정을 다시 계산하지 않는다.

## H15 표지와 Product 명료성 정리

발표 deck 앞에 번호 없는 `COVER`를 추가했다. 본문 01~07은 그대로 유지하며 활성 화면에는 짧은 opacity/translate CSS 진입 효과를 적용했다. `prefers-reduced-motion: reduce`에서는 효과를 제거한다. H14의 bounded wheel intent controller, 양 끝 clamp, 버튼·키보드 이동은 변경하지 않았다.

Product의 정상 상단 경계는 `합성 데모 · 실제 보증 아님 / 현재 결론 HOLD` 한 줄로 줄였다. 검토 조건은 실제 근거 현황을 `0건` 한 묶음으로 표시하고, 수치 변화는 동일 너비 TID/SEU/Residual SEU 카드와 ECC의 원인→동작→한계를 설명한다. 보증 판단은 `확인된 것 / 아직 필요한 것 / 그래서 내린 결정`으로 재구성하고 machine code·식별자·hash·invalidation은 접힌 기술 상세에 둔다.

사용자 결정에 따라 Product 02의 WATCHDOG/TMR/SEL runtime 탭과 control은 정상 발표 동선에서 제거했다. Stage 5 runtime engine, schema, fixture, 생성 payload와 H09/H10 consumer·무결성 코드는 삭제하거나 변경하지 않았으며 향후 system-level trade study용 실험적 계산 능력으로 보존한다. Product 04는 계산 결과의 전달 중 숫자 변경을 막는 별도 데이터 무결성 시연이며 runtime 하드웨어를 이해하거나 실제 장비가 동작한다고 전제하지 않는다.
