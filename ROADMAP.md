# SPECTRA 제출 Release 로드맵

## 목표

**2026-08-25 제출 Release의 bounded 구현과 외부 의존을 분리하고, 공격 보완·발표·공개 데모·문서·검증을 하나의 재현 가능한 단위로 고정한다.**

현재 실행은 이 채팅에서 통합 관리한다. Workstream 번호는 증거 소유 영역을 설명하는 역사적 태그일 뿐, 별도 채팅 완료를 기다리는 진행 단위가 아니다.

## 현재 상태

| 영역 | 현재 판정 | 제출 의미 |
|---|---|---|
| Stage 1 계약·기준선 | `COMPLETE` | 범위·데이터 분류·스키마·책임 경계 확정 |
| Stage 2 합성 Core | `COMPLETE` | 결정론적 TID·SEE·HOLD 기준선 재현 |
| Stage 3 환경 evidence | `SUBMISSION_COMPLETE_WITH_LIMITS` | parser/intake/readiness gate 완료; 실제 contract는 `DEFERRED_EXTERNAL` |
| Stage 4 COTS evidence | `SUBMISSION_COMPLETE_WITH_LIMITS` | `23LC1024-I/SN` reference gate 완료; exact flight/test packet은 `DEFERRED_EXTERNAL` |
| Stage 5 완화·정책 | `COMPLETE — SYNTHETIC_BOUNDED` | 차폐·ECC·정책·Change Impact Exit Gate 완료 |
| Stage 6 Assurance | `SUBMISSION_COMPLETE_WITH_LIMITS` | ASR-D02 control 1 + 공격 4 `PARTIAL_SAFE`; 나머지 12건은 제출 후 |
| Stage 7 GCP | `COMPLETE — SYNTHETIC_BOUNDED` | 보완 revision·Core parity·LIVE_API receipt 재수집 완료 |
| Stage 8 Product | `SUBMISSION_COMPLETE_WITH_LIMITS` | Cloud Run Console·부분 검증 ledger·공개 카탈로그·fallback 완료 |
| Stage 9 발표·제출 | `RELEASE_VERIFIED_EXCEPT_HUMAN_REHEARSAL` | 11장·10분 대본·공개 발표 모드 Console 완료; 최신 회귀·사람 낭독 실측 별도 확인 중 |

## 발표 확장 Phase 01~03

세 Phase는 모두 **`SUBMISSION_COMPLETE_WITH_LIMITS`**다. 오늘의 완료는 외부 서비스를 실제 운영했다는 뜻이 아니라, 입력·검토·변경 흐름과 fail-closed blocker를 작동하는 데모로 구현했다는 뜻이다.

| Phase | 제출 완료 범위 | 제출 후 확장 |
|---|---|---|
| 01 환경·COTS evidence | local source intake, NASA snapshot gate, COTS registry, 권리·identity·hash 차단 | 실제 SPENVIS/NASA connector, production evidence library |
| 02 AI 문서 검토 | 합성 document candidate, processor readiness, 사람 승인 전 격리 | Document AI·Gemini, authenticated HITL, actual audit trail |
| 03 변경·보안 | generated Change Impact, CAD linkage readiness, 보안 posture | 실제 CAD/3D 계산, KMS 운영, 승인 penetration test |

## 제출 Release 완료 내역

1. **공격 작업 동결 단위 완성**
   - 로컬 보완·최소 배포·새 target lock: 완료
   - control + `D02-02/04/05/10` batch 재검증: 완료
   - 결과: control pass 1, safe failure 4, False Accept 0, False PASS 0, unexpected 0
2. **발표 신뢰성 설명 정리 — 완료**
   - Slide 09에서 공격 횟수 카운터를 제거하고 Schema·Core·Identity·Hash·Fail-Closed·배포 격리 조치를 설명
3. **표현 정렬 — 완료**
   - 로컬 parser와 저장 GCP 경로를 분리하고, GCP snapshot의 정상·hash mismatch·endpoint override 결론을 먼저 표시
   - 실제 evidence 0건, 구매자·ROI 미검증, roadmap 발표 제외를 인접 표시
4. **공개 데모 — 완료**
   - `spectra-demo-console` Cloud Run에 발표·문서 검사·임무·부품·시험 연결·저장된 공격 검증·문서별 결과표 배포
   - 문서 검사는 live 실행, 임무·부품·시험 연결은 고정 합성 입력의 production Core live 실행, 공격 검증은 저장 snapshot, 문서별 결과표는 공개 카탈로그 live read로 구분
5. **최종 검증 — 완료**
   - unit 451개·Assurance 공격 47개 통합 기준선과 결과 정보 구조 직접 회귀 28개, 공개 URL 1280×720 발표·Console QA, 문서 정합성 및 revision `00013-8vp` 확인
   - 기존 7분본 구두 리허설은 완료; 사람 10분 낭독·탭 전환 리허설 2회는 `NOT_MEASURED`로 별도 유지

## 오늘 과감히 제외

- ASR-D02 나머지 12건과 별도 IAM/OIDC·test endpoint 공격
- 실제 환경 contract와 exact flight/test lot closure
- Document AI·Gemini·CAD/3D·Cloud SQL·BigQuery·KMS·침투시험
- 인터뷰·가격·절감 효과 검증
- WATCHDOG·TMR·SEL experimental runtime의 추가 확장

제외 항목은 [`CHECKLIST.md`](CHECKLIST.md)의 제출 실패로 계산하지 않는다. 상세 역사와 공격별 증거는 `docs/workstreams/*/CURRENT.md` 및 evidence JSON에 보존한다.
