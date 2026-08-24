# SPECTRA 18:00 제출 체크리스트

이 파일만 현재 제출 승인 Gate로 사용한다. 장기 과학 MVP와 제출 후 확장은 [`docs/MVP.md`](docs/MVP.md), 상세 이력은 Workstream `CURRENT.md`에 둔다.

## A. 이미 완료된 제출 기반

- [x] 프로젝트 범위·비범위·데이터 분류·EvidencePacket 계약
- [x] 결정론적 합성 TID·SEE·차폐·ECC·정책·Change Impact
- [x] Core 고정 공격 29건 False PASS 0 기준선
- [x] 실제 GCP Cloud Run Agent 3개·Workflows·Storage·IAM·Logging 합성 E2E
- [x] H06 event contract, H07 actual read-only receipt, H08 `LIVE_API` timeline data
- [x] 환경 intake/readiness gate와 실제 후보의 fail-closed receipt
- [x] `23LC1024-I/SN` COTS reference package와 `NOT_COMPARABLE / HOLD` gate
- [x] Product/Evidence Console의 local PDF/TXT·저장 GCP 기록·batch review
- [x] 발표 Phase 01~03 bounded workflow와 외부 blocker 표시
- [x] 실제 evidence·합성 fallback·미지원 범위의 구분

## B. 공격 작업 마무리

- [x] ASR-D02 Phase 1 control + 공격 4건 actual evidence 보존
- [x] `D02-02` generation 404 구조화 fail-closed 로컬 보완
- [x] `D02-05` expected exact-part identity hash binding 로컬 보완
- [x] 직접 테스트·YAML parse·기존 evidence 재평가
- [x] 최소 범위 새 GCP revision 배포
- [x] 새 deployment target identity·source hash 잠금
- [x] control + `D02-02/04/05/10` batch 재공격
- [x] False Accept 0 / False PASS 0 / unexpected 0 확인
- [x] 최종 attack evidence와 CURRENT/발표 수치 동기화

## C. 발표·데모

- [x] GCP 구조 뒤에 공격 방어·신뢰성 슬라이드 1장 추가
- [x] 공격 수치의 평가 범위와 `HOLD` 경계 인접 표시
- [x] slide 번호·로드맵 Phase 번호·발표 동선 동기화
- [x] localhost 1280×720 전 슬라이드 overflow·console 오류 0
- [x] Evidence Console 핵심 동선 smoke test
- [ ] 사람 7분 발표·탭 전환 리허설 1회 측정

## D. 문서·제출

- [x] README·PROJECT_OVERVIEW·MVP·ROADMAP·CHECKLIST 역할 정리
- [x] 과거 채팅/Workstream 진행 규칙을 현재 실행 기준에서 제거
- [x] Stage 1·2·5 완료, Stage 3·4·8 제한 완료, Stage 6·7·9 오늘 활성으로 재분류
- [x] Phase 01~03 bounded 완료와 외부 확장을 분리
- [x] 전체 로컬 회귀 1회
- [x] 비밀정보·private raw evidence·불필요한 생성물 Git 경계 확인
- [x] `git diff --check` 및 최종 변경 검토
- [x] commit·push (`516701c`, `origin/main`)
- [x] 제출 파일·URL 최종 확인

## 제출 후 Backlog — 오늘 Gate 아님

- ASR-D02 나머지 12건, IAM/OIDC·test endpoint 공격
- 실제 SPENVIS/NASA connector와 승인 environment contract
- exact flight/test suffix·lot/die·TID/SEE evidence packet
- Document AI·Gemini·authenticated HITL
- 실제 CAD/3D shielding, Cloud SQL·BigQuery·KMS, penetration test
- 사용자 인터뷰·가격·절감 시간 검증

## 제출 판정

- `READY_TO_SUBMIT`: B·C·D의 미완료 항목이 모두 닫힘
- `SUBMISSION_BLOCKED`: 배포 재검증 또는 발표/문서 QA가 실패
- 실제 방사선 보증 상태는 제출 여부와 무관하게 `HOLD`
