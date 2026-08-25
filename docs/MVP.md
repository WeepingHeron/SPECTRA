# SPECTRA MVP 및 제출 Release 계약

## 두 완료 기준을 분리한다

### Core Product MVP — `HOLD / DEFERRED_EXTERNAL`

실제 환경 산출물 1개와 exact-part 시험 증거 1개를 같은 Evidence Chain에 연결해, TID·SEE·차폐·ECC·판정·변경 영향을 재현하는 과학적 제품 기준선이다.

아래 외부 증거가 없어 오늘 완료로 주장하지 않는다.

- 권리·provider reference·raw manifest가 확인된 실제 환경 contract
- exact suffix·package·process·die·lot와 시험 조건이 결속된 부품 증거
- 임무 적용성, TID와 필요한 파괴성 SEE coverage
- 독립 과학 교차검산과 실제 사용자 검증

정확한 결과가 `HOLD`인 것은 정상 제품 동작이지만, 실제 evidence가 없는 상태를 MVP 완료로 부르지는 않는다.

### Competition Submission Release — `RELEASE_VERIFIED`

오늘 18:00 제출 대상이다. 실제 GCP의 합성 Multi-Agent 실행, 결정론적 Core, fail-closed Product 흐름, bounded 확장 기능과 증거 한계를 하나의 발표·데모·문서 패키지로 제출한다.

완료 조건은 [`CHECKLIST.md`](../CHECKLIST.md)의 제출 Gate 하나만 사용한다.

## 기준 사용자와 데모 사례

- 사용자: 소형위성 팀의 미션 보증·전자부품 검토 담당자
- 임무: 고정 LEO 합성 사례 1개
- 부품: 현재 생산 COTS SRAM `Microchip 23LC1024-I/SN` catalog 검토 대상 1개
- 비교: 지원 범위 안의 차폐와 ECC 전·후
- 출력: Evidence Coverage, 계산 결과, `HOLD` 이유, 다음 행동, Change Impact
- GCP: Storage → Workflows → Mission/Parts/Assurance Agent → immutable result/log

구매 수량은 부품 identity·차폐·TID 적합성 입력이 아니다. 총 SEU를 계산하는 경우에만 별도 `analysis_device_count`를 사용한다.

## 제출 Release에 포함

1. 결정론적 합성 TID·SEU·차폐·ECC·정책 결과
2. EvidencePacket·readiness receipt·Change Impact 계약
3. COTS source/reference comparison과 exact-part 부족 시 `NOT_COMPARABLE / HOLD`
4. Product/Evidence Console의 Cloud Run/로컬 PDF·TXT 검사, 부분 검증 ledger, 저장 GCP 공격 기록과 공개 문서 카탈로그
5. 발표 Phase 01~03의 bounded workflow와 외부 blocker 표시
6. 실제 GCP Multi-Agent 실행·로그·generation/hash lineage
7. 공격 검증 결과, 발견된 결함과 deployed 보완 재검증 상태
8. 로드맵을 제외한 11장 발표본과 10분 대본, 발표 모드 Evidence Console

공개 발표본과 Console은 `spectra-demo-console` Cloud Run revision `00013-8vp`에서 제공한다. `문서 검사`는 요청 시 실제 규칙 기반 parser를 실행하고 기본 정보와 사건별 요구자료를 분리한다. `임무·부품·시험 연결`은 세 원문과 승인·권리 신뢰 앵커를 hash-bound한 고정 합성 입력으로 production Core를 실행하며, 핵심 결과를 `근거 연결 · TID·SEU 계산 · 최종 적용성 관문`으로 나눠 표시한다. 일반 Console에서는 사용자가 역할을 지정한 세 문서를 후보 검토 묶음으로 직접 올리고, 원문을 제외한 결정론적 검토 패킷 JSON을 내려받을 수 있지만 승인 결속 전까지 판단에 사용하지 않는다. `저장된 공격 검증`은 공개 쓰기 권한을 열지 않기 위해 독립 확인된 snapshot을 읽으며, `문서별 결과표`는 공개 GCP catalog를 읽는 경로다. 이 네 동작은 실제 방사선 보증 완료를 뜻하지 않는다.

## 제출 Release에서 제외

- 실제 비행 적합성 인증 또는 방사선 시험 대체
- 실제 SPENVIS/NASA production connector와 승인 evidence library
- Document AI·Gemini 실호출과 authenticated HITL
- 실제 CAD parser·3D shielding 계산
- Cloud SQL·BigQuery·KMS 운영, 침투시험, 프로덕션 고가용성
- 모든 궤도·부품 지원, 대량 BOM, 결제·조직 관리
- 사용자 인터뷰·가격·절감 효과를 검증된 수치처럼 제시하는 것
- 구매자·예산 책임자·도입 방식 또는 사람 팀 시너지를 확인 없이 주장하는 것

이 제외 항목은 실패한 제출 작업이 아니라 `POST_SUBMISSION` 또는 `DEFERRED_EXTERNAL` 범위다.
