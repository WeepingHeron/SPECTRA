# 30 Environment Model — Workstream Brief

## 역할

Environment Model Workstream은 Stage 3의 실제 환경·TID 모델 경로를 조사하고, 승인된 모델 출력이 SPECTRA 계약으로 들어오기 전의 실행·원본·provenance 경계를 정의한다. 모델 수치를 창작하거나 방사선 적합성을 판정하지 않는다.

## 이번 세션 범위

- SPENVIS와 OLTARIS의 공식 문서·이용 조건 비교
- 첫 지원 궤도와 TID 모델 체인의 제한
- 사람 실행, 자동화, 상업 이용, 보관·재배포 상태 구분
- 입력·출력·실행 ID·해시·staleness 초안
- Stage 2·4·5·6과 공통 계약에 필요한 변경 요청 기록

실제 계정 로그인, 모델 실행, 출력 확보, 파서·schema·시뮬레이션 구현은 이번 세션 범위가 아니다. 조사 시작 당시 Stage 2 후보는 Git 통합 전이었으나, Control Tower 검토 시점에는 합성 기준선이 통합됐다. 실제 모델 adapter는 공통 계약 변경 전까지 연결하지 않는다.

## 소유 파일

- `docs/workstreams/30-environment-model/BRIEF.md`
- `docs/workstreams/30-environment-model/CURRENT.md`
- `docs/workstreams/30-environment-model/RESEARCH.md`

공통 `schemas/`, `docs/contracts/`, 루트 문서와 다른 Workstream 파일은 읽기 전용이다. 변경 필요성은 `RESEARCH.md`의 계약 변경 요청으로 전달한다.

## 안전 경계

- 실제 모델 결과가 없는 예시는 실제 수치처럼 제시하지 않는다.
- 원본 출력과 입력 보고서가 함께 해시되지 않으면 `PROVENANCE_FAILURE`다.
- 모델 범위 밖 입력은 외삽하지 않고 `OUT_OF_MODEL_SCOPE`로 종료한다.
- 이용 권한, 자동화 권한, 상업 이용 또는 재배포 권리가 확인되지 않은 사용 방식은 `HOLD`다.
- 이 Workstream은 `READY_FOR_REVIEW`까지만 요청한다. `VERIFIED`, `INTEGRATED`, 루트 체크리스트 갱신과 commit·push는 Control Tower가 담당한다.

## 현재 권장 방향

첫 후보는 **등록 사용자가 SPENVIS 웹 UI에서 단일 원형 LEO·단일 구간을 수동 실행하고, AE9/AP9 v1.50 설정과 태양입자 모델 설정을 고정한 뒤 SHIELDOSE-2의 Si/Al 단순 차폐 결과 및 모든 입력 보고서를 원본 번들로 내려받아 로컬에서 검증·파싱하는 경로**다.

이 선택은 조사·비상업 평가용 후보일 뿐이다. SPENVIS 상업 목적 사용은 사전 허가가 필요하고, 공개 문서에서 무인 자동 호출 및 출력 재배포 권한을 확인하지 못했으므로 제품 연결은 `HOLD`다.
