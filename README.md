# SPECTRA

> **Space Parts Evidence, Component Traceability, Radiation Assurance**

SPECTRA는 위성 임무 조건, BOM, 방사선 환경 모델과 부품 시험 증거를 연결해 TID·SEE 위험과 증거 공백을 추적하는 방사선 보증 플랫폼이다. AI가 비행 적합성이나 인증을 대신 판정하지 않으며, 근거가 부족하거나 적용 범위를 벗어나면 안전하게 `HOLD`한다.

## 현재 통합 상태

Stage 2의 결정론적 **합성** Vertical Slice가 통합돼 있다.

제품 MVP의 정확한 입력·기능·완료 조건은 [`docs/MVP.md`](docs/MVP.md)에 정의한다. 현재 합성 Vertical Slice와 Product UI는 검증된 프로토타입이며, 실제 환경 산출물과 exact-part 시험 증거가 연결되기 전에는 MVP 완료로 부르지 않는다.

- TID·SEE·정책 계산 모듈과 입력·출력 Schema
- 차폐 두께, 임무 기간, ECC, 사용자 정책 비교
- 범위 밖 입력은 `OUT_OF_MODEL_SCOPE`, 누락·오염 입력은 `HOLD`
- 모든 입력·계수·결과는 `SYNTHETIC`; `engineering_gate=PASS`여도 `assurance_decision`은 항상 `HOLD`

실제 방사선 환경 출력, 실제 부품 시험 원문, 제품 대시보드는 아직 통합되지 않았다. 따라서 현재 결과는 물리 검증이나 방사선 보증 결론이 아니다.

Stage 3의 환경 모델 도구·권리 조사와 Stage 4의 부품 증거 출처·권리·식별·적용성 조사는 통합됐다. 두 Stage 모두 실제 모델 출력·승인 BOM·시험 원문·실제 수치가 0건이므로 구현 완료가 아니라 `IN_PROGRESS`다.

## 빠른 시작

```bash
python3 tests/simulation/run_all.py
```

이 명령은 Stage 1 계약 검증, Stage 2 테스트, 합성 비교 CLI를 순서대로 실행한다. 비교만 다시 보려면 다음을 실행한다.

```bash
python3 simulation/run_demo.py
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

## 상태 표기

`READY_FOR_REVIEW`는 작업 세션의 제출 상태이고, `INTEGRATED`는 Control Tower가 독립 검증·통합한 상태다. 완료 표시는 실행 근거와 검증 기록이 있을 때만 변경한다.
