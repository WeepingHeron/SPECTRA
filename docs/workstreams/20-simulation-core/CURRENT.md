# 20 Simulation Core Handoff

## Intended Session Owner

`20-simulation-core`

현재 파일은 잘못된 운영 안내로 채팅 10에서 먼저 생성됐다. 구현 내용은 보존하지만, 채팅 20이 파일과 검증 결과를 직접 인수·재확인하기 전에는 Workstream 20의 완료 후보로 인정하지 않는다.

## Status

`INTEGRATED`

채팅 20은 2026-08-19에 미추적 후보 파일 전부를 직접 읽고 수정 전 검증을 재실행한 뒤 소유권을 인수했다. 초기 구현의 구조를 보존하면서 발견한 계약·False PASS 위험을 수정하고 전체 검증을 완료했다.

2026-08-19 Stage 번호 정렬 요청에 따라 공통 계약을 Stage 1, Simulation Core 합성 Vertical Slice를 Stage 2로 통일했다. 코드 식별자·docstring·오류 메시지·README·결과 schema 설명·인수인계 명칭만 변경했으며 계산과 판정 의미는 변경하지 않았다.

## Stage 번호 정렬 변경 파일

- `src/spectra_sim/contracts.py`
- `src/spectra_sim/engine.py`
- `src/spectra_sim/see.py`
- `src/spectra_sim/units.py`
- `simulation/run_demo.py`
- `simulation/README.md`
- `simulation/schemas/simulation-result.schema.json`
- `tests/simulation/run_all.py`
- `docs/workstreams/20-simulation-core/BRIEF.md`
- `docs/workstreams/20-simulation-core/CURRENT.md`

## 인수 과정과 수정 전 기준선

- Git 기준선: `main...origin/main`, Workstream 20 후보 전체는 미추적, 별도 사용자 변경 `.obsidian/`도 미추적
- 소유 범위 밖 `.obsidian/`, 루트 문서, `schemas/`, `docs/contracts/`, Workstream 10·00 파일은 수정하지 않음
- 후보 파일 전부와 필수 계약 문서를 직접 읽고 완결성·계약 호환성을 검토함
- 수정 전 `python3 tests/schema/validate_contracts.py`: 정상 1개와 실패 27개, exit code 0
- 수정 전 `python3 tests/simulation/run_all.py`: Simulation 13개, 데모 5개 시나리오, exit code 0
- 인수 시 발견 위험: Stage 1 의미 검증 미호출, 입력 배열 index 하드코딩, 음수·비유한 계산값, 중복 입력 종류, 합성 모델 설정 변조 방어 누락

## 구현한 Vertical Slice

- Stage 1 EvidencePacket을 입력으로 받는 결정론적 합성 엔진
- 분리된 TID, SEE, 단위 변환, 정책, 입력 계약 모듈
- 1·2·3·4 mm 합성 차폐 lookup과 기간 변화 TID 비교
- ECC 사용·미사용의 raw/residual SEU 비교
- TID margin, residual SEU 한도, 파괴성 SEE, 정책 승인 rule
- Stage 2 결과 JSON Schema와 결과 EvidencePacket
- 합성 계산이 수치 조건을 만족해도 `HOLD`를 유지하는 보증 gate
- 실행 전·후 Stage 1 JSON Schema와 semantic gate 검증
- 입력 종류의 동적 index trace와 종류별 정확히 1개 제한
- 음수·비유한 값, 잘못된 component 연결과 비지원 완화의 fail-closed 처리
- 합성 모델 분류·계수·이산 lookup 무결성 검증
- 파일을 쓰지 않는 CLI 비교와 전체 단일 검증 명령

## 변경 파일

- `src/spectra_sim/__init__.py`
- `src/spectra_sim/contracts.py`
- `src/spectra_sim/engine.py`
- `src/spectra_sim/policy.py`
- `src/spectra_sim/see.py`
- `src/spectra_sim/tid.py`
- `src/spectra_sim/units.py`
- `simulation/config/synthetic-model.json`
- `simulation/schemas/simulation-result.schema.json`
- `simulation/run_demo.py`
- `simulation/README.md`
- `tests/simulation/test_vertical_slice.py`
- `tests/simulation/run_all.py`
- `docs/workstreams/20-simulation-core/BRIEF.md`
- `docs/workstreams/20-simulation-core/CURRENT.md`

## 계산과 판정 경계

- 합성 TID: 기준 TID × 기간 비율 × 이산 차폐 계수
- 합성 SEE: flux × cross section × 수량 × 기간 × 합성 exposure scale
- 잔여 SEE: raw SEE × ECC 완화 계수
- `engineering_gate`: 합성 조건 비교용 `PASS/FAIL/NOT_EVALUATED`
- `assurance_decision`: 모든 합성 실행에서 `HOLD`
- `OUT_OF_MODEL_SCOPE`: 1~4 mm 이외 차폐나 지원하지 않는 차폐 단위
- `INVALID_INPUT`: EvidencePacket 스키마·의미 오류, 호환되지 않는 단위, 중복 종류, 음수·비유한 입력
- `MODEL_FAILURE`: 합성 모델 설정 또는 생성 EvidencePacket 계약 실패

## 검증 결과

- 실행 명령: `python3 tests/schema/validate_contracts.py` — exit code 0
- 실행 명령: `python3 tests/simulation/run_all.py` — exit code 0
- Stage 1: 스키마 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개 검증
- Stage 2: 테스트 19개 통과
- 비교 CLI: 차폐 1·2·4 mm, ECC on/off, 5 mm 범위 밖 시나리오 재현

최종 Stage 1 실제 출력:

```text
SCHEMAS: 9 checked
ENUM CONTRACTS: 4 axes checked
VALID FIXTURES: 1 passed
INVALID FIXTURES: 27 rejected with expected codes
RESULT: READY_FOR_REVIEW candidate
```

최종 Simulation 실제 요약:

```text
Ran 19 tests in 0.766s
OK
```

실제 비교 출력:

```text
scenario                 status               shielded_tid_krad  residual_seu  engineering    assurance
shield-1mm-ecc           VALID                8                  0.0063072      PASS           HOLD
shield-2mm-ecc           VALID                6                  0.0063072      PASS           HOLD
shield-4mm-ecc           VALID                3.5                0.0063072      PASS           HOLD
shield-2mm-no-ecc        VALID                6                  0.063072       PASS           HOLD
out-of-scope-5mm         OUT_OF_MODEL_SCOPE   -                  -              NOT_EVALUATED  HOLD
```

## 검증한 실패·경계

- TID 시험 한계 부족
- SEE 단면적 누락
- 파괴성 SEE 증거 누락
- 사용자 residual SEU 한도 초과
- 미승인 정책
- 5 mm 차폐 외삽 요청
- 호환되지 않는 기간 단위
- 필수 입력·trace가 없는 심각하게 손상된 packet
- 합성 데이터 표시 누락·지원 판정 승격 방지
- 합성 `engineering_gate=PASS` 결과를 `SUPPORTED_WITH_MITIGATION`으로 변조하는 공격
- Stage 1 semantic 오염과 중복 trace ID
- 입력 7종 배열 재정렬과 동적 provenance pointer
- 중복 필수 입력 종류
- 음수 duration·flux와 무한대 정책 한도
- 합성 모델의 `data_class` 변조
- 동일 입력의 byte-equivalent 결과 재현

## 수동 교차검산

fixture의 합성 입력 `TID=10 krad(Si)`, 설계계수 2, 차폐계수 `0.8/0.6/0.45/0.35`를 독립 산술로 계산했다.

```text
manual_tid_1_2_3_4mm=[8.0, 6.0, 4.5, 3.5]
manual_required_tid_factor2=[16.0, 12.0, 9.0, 7.0]
manual_raw_seu=0.063072
manual_residual_ecc_0.1=0.0063072
```

기간 0.5년과 2년은 기준 1년 대비 각각 0.5배와 2배이며, 테스트에서 required TID `6.0/24.0`, raw SEU `0.031536/0.126144`로 교차검산했다.

## 데이터 분류와 출처

- 실제 데이터: 없음
- 합성 데이터: 모델 설정, 입력 fixture, 모든 계산 결과가 `SYNTHETIC`
- `CALCULATED` 실제 근거: 없음
- 합성 계수: 차폐 lookup과 SEE exposure scale은 `simulation/config/synthetic-model.json`에 명시
- 최종 EvidencePacket: `SYNTHETIC_ONLY` 차단 gap과 `HOLD` 유지

## 알려진 한계

- 실제 환경 모델·시험 원문·과학적 정확도를 검증하지 않았다.
- 단일 부품, `cm2/device`, 365일 합성 연도만 지원한다.
- 차폐 lookup은 물리 모델이 아니며 보간·외삽하지 않는다.
- 기본 입력은 Workstream 10의 합성 fixture다. 문서에 언급된 외부 합성 데모는 위치가 없어 이관하지 않았다.
- CLI 비교만 구현했으며 제품 대시보드와 변경 영향 UI는 후속 작업이다.
- 잘못된 입력은 유효 EvidencePacket을 만들 수 없으므로 결과 envelope의 `evidence_packet`을 `null`로 두고 `INVALID_INPUT/HOLD`를 반환한다.
- Stage 1 semantic gate의 기준 구현이 현재 `tests/schema/validate_contracts.py`에 있으므로 분리 패키징 전에 공통 검증 모듈 승격이 필요하다. 현재 저장소에서 파일이 없거나 로드되지 않으면 fail-closed한다.
- 공통 계약 문서는 `docs/contracts/STAGE1_CONTRACT.md`, 본 합성 Vertical Slice는 Stage 2로 정렬했다. 번호 변경은 명칭과 식별자에만 적용했으며 수치 계산·판정 규칙·테스트 의미는 바꾸지 않았다.

## Control Tower 확인 요청

- 독립 환경에서 `python3 tests/simulation/run_all.py`를 재실행해 달라.
- 출력 JSON Schema와 내장 EvidencePacket을 각각 독립 검증해 달라.
- 합성 `engineering_gate=PASS`가 어떤 경로에서도 보증 지원 판정으로 승격되지 않는지 공격 테스트해 달라.
- 차폐·기간·ECC 변화와 고정 입력 재현성을 수동 교차검산해 달라.
- 독립 검증 전 루트 체크리스트를 완료 처리하지 말아 달라.
- `VERIFIED`, `INTEGRATED`, commit·push는 Control Tower 판단으로 남긴다.

## Control Tower 독립 검증 — 2026-08-19

- 판정: `INTEGRATED` — Stage 2의 **합성 기준선 패키지**만 통합했다. 실제 환경·부품 시험 근거 또는 방사선 보증의 통합을 뜻하지 않는다.
- 재실행: `python3 tests/schema/validate_contracts.py` — schema 9개, enum 축 4개, 정상 fixture 1개, 실패 fixture 27개가 기대대로 종료됨.
- 재실행: `python3 tests/simulation/run_all.py` — Stage 2 테스트 19개, 비교 CLI 5개 시나리오가 통과함.
- 수동 공격: `engineering_gate=PASS` 결과를 `SUPPORTED_WITH_MITIGATION`으로 변조했을 때 결과 schema와 Stage 1 semantic gate가 모두 거부했다. 4.1 mm 차폐는 `OUT_OF_MODEL_SCOPE/HOLD`, JSON 직렬화 불가 입력은 `INVALID_INPUT/HOLD`로 종료했다.
- 데이터 분류: 모델 설정·fixture·계산값은 모두 `SYNTHETIC`; 생성 결과의 `assurance_decision`은 모든 경로에서 `HOLD`다. 실제 물리값이나 시험값은 없다.
- 남은 범위: 외부 합성 데모/CSV/대시보드 이관은 원본 위치가 확인되지 않아 수행하지 않았고, 제품 UI도 후속 Stage 범위다.

## Git 통합

- 브랜치: `main`
- 검증된 통합 commit: `35f36a2` — `feat(sim): integrate verified synthetic Stage 2 baseline`
- 원격: `origin` (`https://github.com/WeepingHeron/SPECTRA.git`), push 완료
- 제외: 사용자 소유의 미추적 `.obsidian/`

## 다음 작업이 사용할 계약

- Workstream 30은 `RADIATION_ENVIRONMENT`와 shielding output을 실제 모델 provenance로 교체한다.
- Workstream 40은 `PART_TEST_EVIDENCE`를 정확한 부품·공정·로트와 원문 위치로 교체한다.
- 실제 provenance가 검증되기 전에는 `SUPPORTED_WITH_MITIGATION`을 만들지 않는다.
