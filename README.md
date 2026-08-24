# SPECTRA

> **Space Parts Evidence, Component Traceability, Radiation Assurance**

SPECTRA는 위성 임무 조건, BOM, 방사선 환경 모델과 부품 시험 증거를 연결해 TID·SEE 위험과 증거 공백을 추적하는 방사선 보증 플랫폼이다. AI가 비행 적합성이나 인증을 대신 판정하지 않으며, 근거가 부족하거나 적용 범위를 벗어나면 안전하게 `HOLD`한다.

## 현재 통합 상태

현재 상태는 **`CORE MVP IN_PROGRESS / COMPETITION DEMO RELEASE IN_PROGRESS / ASSURANCE HOLD`**다.

제품 MVP의 정확한 입력·기능·완료 조건은 [`docs/MVP.md`](docs/MVP.md)에 정의한다. 현재 합성 Vertical Slice와 Product UI는 검증된 프로토타입이며, 실제 환경 산출물과 exact-part 시험 증거가 연결되기 전에는 MVP 완료로 부르지 않는다.

- **검증된 합성 Core:** TID·SEE, 차폐·ECC·판정 기준, EvidencePacket·Change Impact, Core 공격 29회에서 False PASS 0
- **실험 범위 회귀:** WATCHDOG·TMR·SEL runtime 공격 18회에서 False PASS 0 — 현재 Core 판단·주 발표와 분리
- **검증된 Competition 기반:** 교육용 GCP의 private Cloud Run Agent 3개, Workflows, Storage, IAM, Logging 합성 E2E와 입력 무결성 공격 차단
- **검증된 표현 계층:** generated 결과를 소비하는 Product UI, fail-closed 결과 전달 무결성, 13장 발표 deck의 localhost 화면·상호작용
- **미완료 실제 근거:** 승인된 환경 contract, 승인 BOM과 exact-part 시험 원문, 임무 적용성·파괴성 SEE coverage, 과학적 교차검산
- **미평가 배포 공격:** 실제 GCP `ASR-D02`

GCP 실행 성공과 합성 회귀 통과는 실제 환경·부품 증거 또는 방사선 적합성의 증명이 아니다. 누락·손상·범위 밖·무결성 실패는 `DATA_UNAVAILABLE`, `NOT_EVALUATED` 또는 `HOLD`로 닫는다.

Stage 3에는 Git 밖 실제 SPENVIS 원본 bundle과 parser 후보가, Stage 4에는 exact-part 후보 조사가 존재한다. 그러나 provider reference·권리·승인 raw manifest·승인 BOM·원문 적용성·필요 SEE 증거가 부족해 둘 다 제품 판단 입력으로 발행되지 않았고 `IN_PROGRESS/HOLD`다.

## 빠른 시작

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py
```

이 명령은 합성 Core와 비교 시나리오를 재현한다. 현재 주요 경로를 각각 확인하려면 다음 명령을 사용한다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/environment/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s platform/gcp-e2e-h04/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.product.test_product_data_binding
```

## 핵심 원칙

- 모든 값에 `PUBLISHED`, `CALCULATED`, `ASSUMED`, `SYNTHETIC`, `CUSTOMER_VERIFIED` 분류를 남긴다.
- 계산·단위 변환·정책 판정은 결정론적 코드가 담당한다.
- LLM은 증거 후보 탐색·구조화·설명에만 사용한다.
- 정확한 부품번호·공정·로트·시험 조건이 맞지 않거나 파괴성 SEE 증거가 없으면 자동 PASS하지 않는다.
- 합성값이나 가정값은 실제 증거나 지원 판정으로 사용할 수 없다.

## 문서 안내

- [프로젝트 소개](PROJECT_OVERVIEW.md)
- [로드맵](ROADMAP.md)
- [검증 체크리스트](CHECKLIST.md)
- [합성 Vertical Slice 실행·제한](simulation/README.md)
- [Workstream 운영 현황](docs/workstreams/README.md)
- [Control Tower 현재 상태](docs/workstreams/00-control-tower/CURRENT.md)

## 상태 표기

`READY_FOR_REVIEW`는 작업 세션의 제출 상태이고, `INTEGRATED`는 Control Tower가 독립 검증·통합한 상태다. 완료 표시는 실행 근거와 검증 기록이 있을 때만 변경한다.
