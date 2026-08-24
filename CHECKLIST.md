# SPECTRA 단계별 체크리스트

Stage별 주관 Workstream과 첫 채팅 번호는 [`ROADMAP.md`](ROADMAP.md)의 **Stage–Workstream–Session 대응표**를 따른다.

## 체크 규칙

- `[x]`는 문서, 파일, 실행 로그 또는 검토 기록으로 재확인할 수 있을 때만 표시한다.
- 코드가 존재하는 것과 검증이 완료된 것을 구분한다.
- 합성 결과는 실제 모델·시험 검증 완료로 계산하지 않는다.
- 각 단계의 **Exit Gate**가 모두 충족되기 전 다음 단계를 완료로 표시하지 않는다.

## MVP 통합 Gate

상세 범위는 [`docs/MVP.md`](docs/MVP.md)를 따른다. 이 목록은 Stage 전체 완료와 별개로, 데모 가능한 한 개 실제 Evidence-to-Decision 제품 경로를 판정한다.

- [x] EvidencePacket·입력·출력 계약 기준선
- [x] 결정론적 합성 TID·SEE 기준선과 재현 테스트
- [x] 고정 공격 세트의 평가 가능 항목에서 False PASS 0
- [x] 합성 Product UI와 안전한 offline fallback
- [ ] 권리·provenance가 확인된 실제 환경 산출물 1개
- [ ] exact-part 시험 증거 묶음 1개와 원문 locator
- [x] 결정론적 완화·사용자 정책 engine 합성 기준선
- [x] 변경 전·후 결과와 무효화 근거 생성
- [x] UI가 검증된 결과 JSON·EvidencePacket을 소비
- [ ] 5분 사용자 실행과 설명 가능성 검증
- 근거가 부족한 작업은 `HOLD` 또는 `INSUFFICIENT_EVIDENCE`로 기록한다.

## 발표 로드맵 확장 기능 Gate

- [x] 7개 확장 화면을 `Roadmap Lab` 단일 진입점에 연결
- [x] Phase 1 source intake와 COTS 후보 registry를 decision-ineligible·fail-closed로 구현
- [x] NASA public DB용 local snapshot hash·locator·rights·exact-part intake gate와 공격 테스트 구현
- [x] Phase 2 합성 document candidate 검토와 processor별 AI readiness gate 구현
- [x] Phase 3 generated Change Impact, CAD linkage readiness와 H05 security posture 화면 구현
- [x] 화면별 `IMPLEMENTED_BOUNDED / READINESS_ONLY / BLOCKED_EXTERNAL`와 최종 `HOLD` 경계 표시
- [ ] 실제 SPENVIS/NASA connector와 production COTS evidence library
- [ ] Document AI·Gemini API, authenticated HITL와 actual audit trail
- [ ] 실제 CAD parser·3D shielding 계산, KMS 운영과 승인된 penetration test

위 완료 표시는 로컬 합성 workflow와 readiness gate에 한정한다. 외부 권리·승인·과학적 교차검산이 필요한 항목은 완료 처리하지 않는다.

## Stage 1 — 프로젝트 계약과 기준선

### 문서와 범위

- [x] 프로젝트 폴더 `/Users/taehoon/Desktop/IAA/SPECTRA` 확인
- [x] `PROJECT_OVERVIEW.md` 작성
- [x] `ROADMAP.md` 작성
- [x] `CHECKLIST.md` 작성
- [x] Control Tower Workstream 책임과 검토 규칙 작성
- [x] Workstream·채팅 세션·작업 패키지 구분 규칙 작성
- [x] Control Tower 세션 시작 템플릿 작성
- [ ] 프로젝트 한 문장 정의 팀 검토
- [ ] 초기 사용자·지원 궤도·지원 부품 범위 확정
- [ ] 제외 범위와 책임 한계 팀 검토

### 프로젝트 기반

- [x] Git 저장소 초기화 또는 기존 저장소 확인
- [ ] 기본 폴더 구조 확정
- [ ] 로컬 실행 환경과 버전 고정
- [ ] 비밀정보·대용량 원문 파일 관리 정책 작성
- [ ] 의사결정 기록 형식 작성

### 데이터·판정 계약

- [x] 데이터 분류 enum 정의
  - [x] `PUBLISHED`
  - [x] `CALCULATED`
  - [x] `ASSUMED`
  - [x] `SYNTHETIC`
  - [x] `CUSTOMER_VERIFIED`
- [x] `EvidencePacket` 스키마 작성
- [x] 임무·BOM·시험·완화·정책 입력 스키마 작성
- [x] 판정 상태와 우선순위 규칙 작성
- [x] 단위 체계와 변환 정책 작성
- [x] False PASS 정의와 최소 검증 세트 작성

### Exit Gate

- [ ] 범위와 비범위를 팀원이 동일하게 설명할 수 있음
- [x] 모든 값에 데이터 분류를 부여할 수 있음
- [ ] 인증·시험 대체를 주장하지 않음을 검토함

## Stage 2 — 합성 Vertical Slice

### 통합

- [x] 합성 시뮬레이터를 프로젝트 내부 재현 가능 기준선으로 구현

> 외부 합성 데모·CSV는 원본 위치가 제공되지 않아 이관 대상에서 제외했다. 결과 대시보드와 완화 선택 UI는 Stage 8 Product & Dashboard에서 구현한다.
- [x] TID, SEE, 정책 판정 모듈 분리
- [x] 입력·출력 JSON Schema 적용
- [x] 로컬 실행과 테스트 명령 README 작성

### 시뮬레이션

- [x] 차폐 두께 변화에 따른 TID 비교
- [x] 임무 기간 변화에 따른 TID 비교
- [x] ECC 유무에 따른 잔여 SEU 비교
- [x] 사용자 SEE 허용 한도 커스텀 입력
- [x] TID 설계 계수 커스텀 입력
- [x] 파괴성 SEE 증거 누락 시 HOLD
- [x] 지원 범위 밖 입력 시 `OUT_OF_MODEL_SCOPE`

### 테스트

- [x] 정상 시나리오
- [x] TID 시험 한계 부족
- [x] SEE 단면적 누락
- [x] 파괴성 SEE 증거 누락
- [x] 사용자 허용 한도 초과
- [x] 범위 밖 외삽 요청
- [x] 단위 오류
- [x] 합성 데이터 표시 누락

### Exit Gate

- [x] 한 명령으로 시뮬레이션 재현
- [x] 한 명령으로 전체 테스트 통과
- [x] 모든 합성 값에 `SYNTHETIC` 표시
- [x] 합성 검증 세트 False PASS 0건

## Stage 3 — 실제 환경·TID 모델

> 2026-08-20 Control Tower 확인: Git 밖 실제 SPENVIS 원본 9개, checksum, 실제-format parser와 intake fail-closed H02는 검증했다. 아래 완료 표시는 commit·통합 요건과 provider reference·권리·승인 raw manifest·과학 교차검산이 남아 있어 이번 회차에 변경하지 않는다. 제품 contract는 계속 `HOLD`다.

### 조사와 계약

- [ ] 첫 지원 궤도 확정
- [x] 환경·TID 모델 후보 비교
- [x] SPENVIS 이용 조건과 상업·자동화 제약 확인
- [ ] 모델 입력 필드와 단위 확정
- [ ] 출력 파일·메타데이터·해시 스키마 확정
- [ ] 불확실성·신뢰수준 표시 규칙 확정

### 구현

- [ ] 실제 모델 출력 샘플 확보
- [ ] 원본 모델 출력 불변 저장
- [ ] 출력 파서 구현
- [ ] 단위 정규화 구현
- [ ] 모델명·버전·입력·생성시점 저장
- [ ] 결과 해시와 실행 ID 생성
- [ ] TID 계산 화면에 출처 연결

### 검증

- [ ] 대표 시나리오 수동 계산 또는 공식 출력과 비교
- [ ] 반복 실행 재현성 확인
- [ ] 입력 범위 경계 테스트
- [ ] 오래된 모델·출력 탐지
- [ ] 합성값과 실제 모델값 혼용 차단

### Exit Gate

- [ ] 실제 환경 결과를 원문까지 추적 가능
- [ ] 결과 재현 또는 고정 출력 무결성 확인 가능
- [ ] 범위 밖 입력에서 안전하게 판정 보류

## Stage 4 — 실제 부품 TID·SEE 증거

> 2026-08-20 Control Tower 검증: Workstream 40 H04는 TI 공식 자료에서 exact catalog part `5962L1420901VXC`와 SEE 시험 문서의 base SMD `5962L1420901VX`를 분리하고, scoped search 안에서 exact test-article destructive SEE 증거를 찾지 못한 상태를 `PARTIAL_IDENTITY`·`HOLD`로 유지했다. 적용성 규칙 3개만 완료로 반영하며, 실제 증거 수집·정규화·권리 해결 항목은 체크하지 않는다.

### 데이터 수집

- [ ] 초기 실제 부품 5~10종 선정
- [ ] NASA GSFC 자료 수집
- [ ] NASA NEPP 자료 수집
- [ ] ESA 자료 수집
- [ ] 제조사 공개자료 수집
- [ ] 사용 권한과 라이선스 기록

### 정규화

- [ ] 정확한 부품번호
- [ ] 제조사
- [ ] 기능과 패키지
- [ ] 공정·다이 버전
- [ ] 로트·Date Code
- [ ] 시험 시설·일자
- [ ] 온도·바이어스·선량률
- [ ] TID 시험 범위와 성능 변화
- [ ] SEE 단면적–LET/에너지 데이터
- [ ] SEL·SEB·SEGR 증거
- [ ] 원문 페이지·표 위치와 해시

### 적용성 검토

- [x] 정확한 부품 일치 규칙
- [x] 유사 부품 후보와 확정 증거 분리
- [ ] 제조 공정 변경 탐지
- [ ] 시험 조건과 임무 조건 대조
- [x] 시험 범위 밖 외삽 금지
- [ ] 사람 검토·승인 이력 저장

### Exit Gate

- [ ] 모든 실제 수치가 원문 위치로 역추적됨
- [ ] 조건 불일치가 결과에 노출됨
- [ ] 증거 없는 부품을 자동 PASS하지 않음

## Stage 5 — 제한된 설계 가정 및 판정 엔진

> 2026-08-20 Control Tower 재검증: Workstream 20 H03는 결과 스키마를 공통 `processingStatus` `$ref`로 정렬하고 runtime processing 상태에서 `NOT_EVALUATED`를 제거했다. 전용 24개, simulation 55개와 전체 회귀를 재현했으며 합성·증거 부족 결과는 계속 `HOLD`다. 아래 표시는 H03가 직접 검증한 runtime·정책 안전 경계만 반영한다.

### Core 활성 범위

- [x] 차폐 변경 — 합성 이산 범위 기준선
- [ ] 내방사선 부품 교체
- [x] ECC 적용 전·후 비교 — 합성 기준선, 실제 효과 아님
- [x] 완화 방법별 적용 가능한 고장 유형 매핑 — ECC/SEU 경계

### Experimental runtime 보존

- [x] TMR 합성 계산·안전 경계 검증 — 현재 제품 판단·주 발표 제외
- [x] Watchdog·재부팅 합성 계산·안전 경계 검증 — 현재 제품 판단·주 발표 제외
- [x] SEL 전류 감지·전원 차단 합성 계산·안전 경계 검증 — 현재 제품 판단·주 발표 제외

### 정책

- [x] TID 설계 계수 — 합성 사용자 입력
- [ ] 최소 TID 잔여 마진
- [x] 최대 잔여 SEU 횟수 — 합성 사용자 입력
- [ ] 한 번 이상 SEU 발생 확률
- [x] 파괴성 SEE 증거 요구
- [ ] 판정 기준 출처·버전·적용 범위

### 신뢰성

- [x] 임의 완화율 입력 제거 또는 `ASSUMED` 처리
- [x] 완화 전·후 계산 분리
- [x] 미승인 정책으로 PASS 차단
- [x] ECC가 파괴성 SEE를 해결했다고 판단하지 않음
- [x] 정책 변경 영향 보고서 생성

### Exit Gate

- [x] 완화·정책 선택이 결정론적으로 결과에 반영됨
- [x] 모든 완화 계수에 근거 또는 가정 표시
- [x] 미승인 커스텀 정책에서 안전하게 보류

## Stage 6 — 독립 보증·평가 기준선

> 2026-08-21 범위 정렬: 검증된 47개 실행 중 29개는 Core schema·evidence·MVP/ECC 공격, 18개는 experimental WATCHDOG·TMR·SEL runtime 공격이다. 두 profile 모두 과거 검증은 유지하지만 발표와 Core 신뢰성 수치에서는 구분한다. 실제 GCP `ASR-D02`는 `NOT_EVALUATED`다.

### 공격·오류 테스트

- [x] 유사 부품번호 오탐
- [x] 제조사·로트 불일치
- [x] 단위 변환 오류
- [ ] 시험 표 잘못 추출
- [ ] 출처 링크 손상
- [x] 파일 해시 불일치
- [ ] 오래된 모델 출력
- [x] SEE 증거 누락
- [x] 파괴성 SEE 증거 누락
- [x] 범위 밖 외삽
- [x] 미승인 정책 우회
- [x] 계산·증거·정책 모듈 상충

### 지표

- [x] False PASS 0건
- [x] 고정 합성 control의 계산 재현율 100%
- [ ] 근거 링크·페이지 정확도 측정
- [ ] 부품 식별 정확도 측정
- [ ] 필수 필드 추출 정확도 측정
- [ ] 변경 영향 탐지율 측정
- [ ] 결정론적 검증 처리시간 측정

### Exit Gate

- [x] 고정 독립 검증 세트에서 False PASS 0건
- [x] 평가된 고정 세트의 모든 실패가 설명 가능한 상태로 종료
- [x] 고정 합성 입력의 계산·증거·정책 결과를 반복 재현

## Stage 7 — Multi-Agent·GCP

> Competition Demo Release 필수 Stage. 교육용 GCP project `iceu-686`, 기본 region `asia-northeast3`을 사용하되 실제 생성된 resource·실행·로그만 완료 증거로 인정한다.

> 2026-08-24 범위 정렬: H04에서 발견한 Core 중복 계산, body-hash 결합 우회, runtime endpoint 교체 가능성은 H05에서 보완했다. H05 로컬 12 tests, 실제 Cloud Run/Workflow revision, production Core parity, 본문·SHA 동시 위조와 endpoint override 차단을 독립 재확인했고 발표 deck의 합성 snapshot 표시도 검증했다. 최종 코드·문서 통합은 완료했지만 Stage 7은 Workstream 60 `ASR-D02`와 비용 기준선 전까지 완료로 승격하지 않는다.

### 에이전트

- [x] Mission Environment Agent 계약 — 합성 H05 경로
- [x] Parts Evidence Agent 계약 — 합성 H05 경로
- [x] Independent Assurance Agent 계약 — 합성 H05 경로
- [x] Orchestrator 고정 workflow 계약
- [x] 에이전트 입력·출력 Schema 검증
- [x] 타임아웃·재시도·실패 상태 정의
- [x] 상충 결과 처리 규칙

### GCP

- [x] GCP 프로젝트 `iceu-686`·리전 `asia-northeast3` 고정
- [ ] 예산 경보·비용 기준선
- [x] Cloud Storage 합성 입력·결과 경로
- [x] Cloud Run Agent·production Core 서비스
- [x] Workflows 오케스트레이션
- [x] IAM 최소권한
- [x] 로그·추적·오류 모니터링

### 확장 후보 — 최소 E2E 이후

- [ ] Document AI 추출 파이프라인
- [ ] Vertex AI 증거 구조화·설명
- [ ] Cloud SQL 증거·승인 이력
- [ ] BigQuery 검증·품질 지표
- [ ] KMS 고객 데이터 암호화

### Exit Gate

- [x] End-to-End GCP 합성 실행 증거 확보
- [x] 에이전트별 책임과 장애 격리 시연
- [x] 에이전트 실패가 최종 PASS로 전파되지 않음
- [ ] Stage 6 공격 세트가 배포 경로에서도 통과
- [ ] 비용 기준선과 데모 예산 확인

## Stage 8 — 제품·대시보드

> 2026-08-20 Control Tower 검증: H10은 검증된 H09 consumer를 재사용해 정상 WATCHDOG `1 / 1 / 60 s` → `60 → 999 s` stale-preimage 공격 → 수치·ID·hash 비노출과 `DATA_UNAVAILABLE / NOT_EVALUATED / HOLD` → Reset을 두 desktop viewport에서 재현했다. 아래 완료 표시는 합성 Product·runtime integrity 데모에 한정하며 실제 API·원문 evidence·GCP resource 통합은 미완료다.

### 사용자 흐름

- [ ] 임무·BOM·차폐·완화·정책 입력 흐름
- [x] TID·SEE 결과와 완화 전후 비교
- [x] Evidence Coverage Matrix
- [ ] Evidence Packet 원문·계산 실행 추적
- [x] 변경 전후 영향 보고서
- [x] `HOLD`·증거 공백·미지원 범위 표시
- [x] 합성·실제 데이터 분류 표시

### 제품 신뢰성

- [x] 실패 상태가 성공 화면으로 렌더링되지 않음
- [x] 고정 결과 fallback
- [x] 네트워크 장애 대응
- [x] 알려진 한계 화면 노출

### Exit Gate

- [x] 핵심 흐름을 한 화면씩 이해 가능
- [x] 모든 주요 수치에서 출처 또는 데이터 분류로 이동 가능
- [x] 대표 시나리오를 반복 재현

## Stage 9 — 비즈니스·발표·최종 시연

> 2026-08-24 범위 정렬: 실제 발표 이력과 13장 deck의 시각·상호작용 검증은 존재한다. 다만 별도 시간 측정 리허설, 실제 인터뷰·pilot·가격·기준선은 각각 `NOT_MEASURED`, 0건 또는 `UNSET`이고 COTS·과학 주장의 출처·적용 범위도 미완료이므로 Stage 9 완료로 승격하지 않는다.

### 비즈니스 검증

- [ ] 잠재 사용자군 우선순위 선정
- [ ] 사용자 인터뷰 수행
- [ ] 현재 검토 시간·비용 기준선 확보
- [ ] 가장 가치 있는 산출물 확인
- [ ] 구매 단위와 가격 가설 검증
- [ ] 시험기관·부품사 연계 가능성 검토
- [ ] 기존 도구·컨설팅 비교 갱신

### 발표·시연

- [x] 문제와 물리적 위험 설명
- [x] 기존 도구 사이의 업무 공백 설명
- [x] 임무·BOM 입력 시연
- [x] TID·SEE 계산 시연
- [ ] 완화·정책 변경 시연
- [ ] Evidence Packet과 원문 추적 시연
- [x] 증거 누락 시 HOLD 시연
- [x] GCP·Multi-Agent 합성 snapshot 시연
- [x] 한계와 책임 경계 설명
- [x] 예상 질문과 근거 답변 준비

### 평가 기준 최종 점검

- [x] Multi-Agent 아키텍처 및 GCP 인프라 완성도 35점 증거
- [x] 할루시네이션 방어 및 무결점 신뢰성 20점 증거
- [x] 비즈니스 임팩트 및 문제 정의 30점 증거
- [x] 팀 시너지 및 프레젠테이션 15점 증거

### Exit Gate

- [ ] 사용자가 문제와 산출물 가치를 확인
- [ ] 절감 시간·비용 가설에 근거 존재
- [ ] Evidence Assurance라는 정체성이 분명함
- [ ] 모든 주요 수치에 출처 또는 데이터 분류 표시

## 현재 다음 작업

- [ ] SPENVIS provider reference·권리·승인 raw manifest·과학 교차검산을 갖춘 environment contract 1개
- [ ] 승인 BOM exact-part 1개와 권리 확인 원문·임무 적용성·필요 SEE coverage 연결
- [ ] 고정 revision 실제 GCP `ASR-D02` 수행 및 관찰 증거 검증
- [ ] 실제 contract를 합성 fallback과 구분해 Product Evidence-to-Decision 경로에 연결
- [ ] 사용자 1명의 5분 실행·판정 이유·다음 행동 탐색 측정
- [x] 최종 통합 단위 정리 후 전체 회귀, commit·push 완료
