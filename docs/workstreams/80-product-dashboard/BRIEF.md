# 80 Product & Dashboard — Workstream Brief

## 역할

Product & Dashboard Workstream은 검증된 입력·계산·증거·판정 계약을 사용자가 한 흐름으로 이해하게 만드는 제품 표현을 소유한다. 수치나 최종 판정을 새로 계산하지 않으며, 증거 공백과 실패 상태를 성공처럼 렌더링하지 않는다.

## 이번 작업 패키지

- 세션: `80-product-dashboard`
- 목적: 내일 발표용 self-contained 오프라인 HTML Vertical Slice
- 흐름: 문제 → Mission/BOM → 환경·차폐 → 부품 증거 → 완화 → `HOLD` → Evidence Chain
- 실행 조건: 서버·네트워크·설치·CDN·원격 asset 없음

## 소유 범위

- `demo/`
- `docs/workstreams/80-product-dashboard/BRIEF.md`
- `docs/workstreams/80-product-dashboard/CURRENT.md`

공통 `src/`, `simulation/`, `schemas/`, `tests/`, 루트 문서와 다른 Workstream은 읽기 전용 의존성이다. 공통 코드 변경, checklist 완료, `VERIFIED`, `INTEGRATED`, commit·push는 이번 작업 범위가 아니다.

## 제품 계약

- 한 화면은 한 주장만 전달한다.
- 모든 수치에는 `SYNTHETIC`을 노출한다.
- `engineering_gate=PASS`와 assurance `HOLD`를 분리한다.
- 차폐와 ECC 선택은 기존 엔진 snapshot만 전환한다.
- 범위 밖 입력은 값 없이 `OUT_OF_MODEL_SCOPE/HOLD`로 표시한다.
- 실제 환경·부품·시험·GCP가 0임을 마지막 화면에서 숨기지 않는다.
- JavaScript 실패 시 전체 메시지가 정적 문서로 남는다.

## 검증 명령

```bash
python3 tests/schema/validate_contracts.py
python3 tests/simulation/run_all.py
```

브라우저에서는 오프라인 파일 직접 열기, 키보드·버튼·선택 상태, console error 0, 1440×900과 1920×1080 레이아웃을 확인한다. 작업 채팅은 `READY_FOR_REVIEW`까지만 선언한다.
