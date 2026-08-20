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
