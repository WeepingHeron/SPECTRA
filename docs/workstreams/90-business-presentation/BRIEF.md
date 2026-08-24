# 90 Business & Presentation — Workstream Brief

## 역할

SPECTRA의 기술 기준선, 필수 Multi-Agent·GCP 실행과 제품 UI를 발표·Q&A·사용자 검증 흐름으로 연결한다. 검증된 근거와 구현 범위를 설명하되, 실제 데이터·과학 정확도·고객 가치가 검증된 것처럼 확대하지 않는다.

## 공식 평가 기준

- Multi-Agent 아키텍처 및 GCP 인프라 완성도: 35점
- 할루시네이션 방어 및 무결점 신뢰성: 20점
- 비즈니스 임팩트 및 문제 정의: 30점
- 팀 시너지 및 프레젠테이션: 15점

## 책임 범위

- 문제 정의와 기존 도구 사이의 업무 공백 설명
- 발표 HTML과 Product UI의 시연 동선
- 발표 시간·Q&A·fallback 운영
- 구현·설계·미구현 경계
- Agent별 역할·장애 격리와 GCP E2E 증거의 검증 상태 설명
- NASA 근거와 사용자·비용·구매 가설 분리
- 사용자 인터뷰, pilot과 비즈니스 기준선

## 소유 산출물

- `/Users/taehoon/Downloads/SPECTRA_DEMO_PRESENTATION.md`
- `docs/workstreams/90-business-presentation/`

발표용 HTML과 Product UI 구현은 Workstream 80이 소유한다. 공용 schema·simulation·assurance와 Git 통합은 수정하지 않는다.

Workstream 70 H04가 독립 검증되기 전에는 실제 GCP resource명, execution ID, latency, 비용, 성공 횟수를 모두 `PENDING_H04_VERIFICATION`으로 둔다. Agent는 방사선 숫자나 최종 판정을 생성하는 역할이 아니라 환경·부품 증거·독립 보증의 책임을 분리하며, 계산과 gate는 결정론적 Core가 소유한다.

## 완료 경계

발표 원고와 Q&A가 검증돼도 Stage 9 비즈니스 검증 완료를 뜻하지 않는다. 사용자 인터뷰, 시간·비용 기준선, 구매 의사와 실제 pilot 결과는 별도 증거가 필요하다.
