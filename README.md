# SPECTRA

> **Space Parts Evidence, Component Traceability, Radiation Assurance**

SPECTRA는 위성 임무 조건, COTS 부품 증거, 방사선 계산과 완화 가정을 하나의 추적 가능한 Evidence Chain으로 연결하는 검증 플랫폼이다. 근거가 누락되거나 identity·hash·지원 범위가 맞지 않으면 적합성을 추측하지 않고 `HOLD`한다.

## 현재 제출 상태

**`SUBMISSION RELEASE ACTIVE / CORE ASSURANCE HOLD`**

오늘 18:00 제출의 기준은 장기 과학 MVP 완성이 아니라, 이미 구현한 확장 기능과 GCP Multi-Agent 데모를 사실에 맞게 고정하고 검증 가능한 제출물로 만드는 것이다.

| 상태 | 범위 |
|---|---|
| `COMPLETE` | 프로젝트 계약, 결정론적 합성 Core, 제한된 차폐·ECC·정책 엔진 |
| `SUBMISSION_COMPLETE_WITH_LIMITS` | 환경 intake gate, COTS reference gate, Product/Evidence Console, 발표 Phase 01~03 bounded workflow |
| `ACTIVE_TODAY` | 사람 낭독 리허설, 최종 변경 검토, commit·push·제출 |
| `DEFERRED_EXTERNAL` | 실제 SPENVIS contract, exact flight/test lot evidence, Document AI/Gemini, 실제 CAD/3D, KMS·침투시험, 사용자·가격 검증 |

실제 GCP `ASR-D02` 보완 배치는 새 locked Workflow `000006-d2a`에서 control 1건과 공격 4건을 평가했다. control은 로컬 Core와 canonical hash·semantic object가 일치했고, 네 공격은 모두 기대 stable code로 `SAFE_FAILURE`였다. 이 범위의 False Accept·False PASS·unexpected는 0이며, 나머지 12건은 제출 후 `NOT_EVALUATED`로 남는다.

## 제출 데모

- 발표: `http://127.0.0.1:8765/demo/index.html`
- 발표용 Evidence Console: `http://127.0.0.1:8765/demo/evidence-console.html?presentation=1`
- 상태 기준: [`ROADMAP.md`](ROADMAP.md)
- 제출 승인 Gate: [`CHECKLIST.md`](CHECKLIST.md)
- 제품·MVP 경계: [`docs/MVP.md`](docs/MVP.md)

## 주요 검증 명령

개발 중에는 변경 범위 테스트만 실행하고, 전체 회귀는 제출 직전에 한 번 실행한다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s platform/gcp-e2e-h04/tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.assurance.gcp_d02.test_run_live_phase1 tests.assurance.gcp_d02.test_reconcile_existing_evidence
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/simulation/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/environment/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.product.test_product_data_binding tests.product.test_evidence_review_workspace
```

## 신뢰성 경계

- 계산·단위 변환·정책·최종 Gate는 결정론적 코드가 담당한다.
- LLM은 증거 후보 탐색·구조화·설명에만 사용한다.
- `PUBLISHED`, `CALCULATED`, `ASSUMED`, `SYNTHETIC`, `CUSTOMER_VERIFIED`를 구분한다.
- COTS catalog identity나 유사 부품 시험은 exact-part 비행 적합성 증거가 아니다.
- BOM 구매 수량은 identity·차폐·TID 적용성에서 제외한다. 장치 수가 필요한 총 SEU 분석에서만 별도 `analysis_device_count`를 사용한다.
- False PASS 0은 명시된 평가 세트에만 적용하며 전체 침투시험이나 방사선 보증을 뜻하지 않는다.
- 저장 GCP 화면은 정상·body hash 위조·endpoint override 실행의 run ID를 구분하며, 정상 실행에만 저장된 correlation ID를 표시한다. 현재 Cloud를 조회하거나 새 실행을 만들지 않는다.
- 구매자·예산 책임자·도입 방식·ROI는 아직 검증하지 않았고, 사람 팀의 구성이나 협업 성과도 확인된 사실 없이 주장하지 않는다.

상세 역사와 개별 증거는 `docs/workstreams/*/CURRENT.md`와 `docs/workstreams/*/evidence/`에 보존한다. 현재 실행은 이 채팅에서 통합 관리하며, 과거 채팅 번호는 더 이상 로드맵 진행 단위로 사용하지 않는다.
