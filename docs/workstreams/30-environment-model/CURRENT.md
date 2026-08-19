# 30 Environment Model Handoff

## Status

`INTEGRATED`

이번 상태는 **Stage 3 조사·계약 준비 산출물의 검증·Git 통합**이다. 실제 모델 실행, 출력 확보, parser 구현, schema 변경 또는 Stage 3 완료를 뜻하지 않는다. 상업 이용·자동화·재배포는 별도 `HOLD`다.

## 조사 범위와 소유 파일

- 읽은 기준선: `PROJECT_OVERVIEW.md`, `ROADMAP.md`, `CHECKLIST.md`, Workstream 운영 문서, Control Tower current, Workstream 10 brief/current, `STAGE1_CONTRACT.md`, Stage 1 schemas
- 조사 당시 참고한 후보였고, Control Tower 검토 시 통합 기준선으로 재확인한 파일: `docs/workstreams/20-simulation-core/CURRENT.md`
- 생성 파일:
  - `docs/workstreams/30-environment-model/BRIEF.md`
  - `docs/workstreams/30-environment-model/RESEARCH.md`
  - `docs/workstreams/30-environment-model/CURRENT.md`
- 공통 schema, 계약, 루트 문서, Stage 2 코드·테스트는 수정하지 않았다.
- 작업 채팅 제출 당시에는 commit·push하지 않았으며, 이후 Control Tower가 독립 검증과 통합을 담당했다.

## 공식 출처와 확인 결과

- SPENVIS 공식 home/help/약관에서 등록형 웹 사용, project 단위 input/output 보존, orbit→radiation sources→SHIELDOSE-2 흐름, HTML/ASCII 출력과 현재 platform version을 확인했다.
- SPENVIS 약관은 commercial purpose에 Institute 또는 ESA permission을 요구하고, 발표·출판 acknowledgement와 사용자 백업 책임을 명시한다.
- 공개 문서에서 운영 SPENVIS 사이트의 무인 API 허가와 output 재배포 권리를 확인하지 못했다.
- OLTARIS 공식 home/user guide에서 승인형 계정, circular Earth orbit, HZETRN transport, silicon dose, ASCII 다운로드, job ID·TARIS version·submission time provenance를 확인했다.
- 공개 OLTARIS 자료에서 API, 상업 이용, 기본 보존기간, output 재배포 조건을 확인하지 못했다.
- 상세 URL, 출처별 날짜·주장·제약과 재현 절차는 `RESEARCH.md`에 기록했다.

## 권장 첫 모델 경로

- 사람 주도 SPENVIS web run과 로컬 후처리
- Earth circular LEO, 고정 altitude/inclination, single segment
- 제안 baseline: AE9/AP9 v1.50 Mean + 명시적 solar fluence model/config + SHIELDOSE-2
- spherical Al, Si target, 1/2/3/4 `mm_Al_equivalent`
- orbit/trapped/solar/dose report와 ASCII 원본을 하나의 immutable bundle로 해시
- Mean 결과는 uncertainty bound가 아니므로 그 자체로 assurance 지원 판정에 사용하지 않음
- solar source가 없으면 total mission TID로 명명하지 않고 `HOLD`

## Stage 3 계약 초안과 영향

- input에는 orbit class/body/segment, epoch/end/duration, 전체 model chain, run mode/confidence, geometry/target, operator/access mode, terms state가 필요하다.
- output에는 source별 dose, raw file manifest, model chain, tool/job version, parser version, input/output/bundle SHA-256와 실행·다운로드 시각이 필요하다.
- 기존 `RADIATION_ENVIRONMENT.particle_flux` 필수 scalar는 TID-only 경로와 맞지 않으므로 dummy 값을 넣지 않고 Workstream 10 변경 요청으로 남겼다.
- 기존 단일 `model_name/model_version`과 `calculation_run`으로는 외부 model chain과 raw artifact manifest를 충분히 표현하지 못한다.
- Stage 2 합성 기준선은 통합됐지만, 실제 환경 adapter 연결은 Workstream 10 계약 변경 승인 뒤로 미룬다.
- Stage 4는 source-complete Si mission dose만 TID 시험 범위 비교에 사용하고, Stage 5 design factor는 model uncertainty를 대체하지 않으며, Stage 6은 drift·hash·parser fail-closed와 model-policy를 독립 검증해야 한다.

## 데이터·권리·자동화 상태

- 실제 모델 output: 없음
- 실제 환경 수치: 없음
- synthetic 예시: 없음
- 비상업 수동 조사: 계정·약관 준수 전제의 다음 단계 후보
- SPENVIS commercial use: permission 전 `HOLD`
- SPENVIS/OLTARIS automated submission: 공개 권한 확인 전 `HOLD`
- raw/derived output redistribution: 서면 확인 전 `HOLD`
- 로컬 hash·manifest·parser·schema validation 자동화: 허용 후보
- 민감 mission/BOM 정보의 외부 tool 업로드: 데이터 처리 조건 확인 전 금지

## HOLD와 알려진 한계

- solar fluence model과 confidence, AE9/AP9 uncertainty policy가 아직 승인되지 않았다.
- representative circular LEO의 실제 altitude/inclination/start/duration 값은 Control Tower 결정이 필요하다.
- SPENVIS help 일부는 오래됐으므로 실제 계정 UI와 first-run report로 재확인해야 한다.
- model output format·단위·version signature는 실제 run 전 확정할 수 없다.
- SPENVIS/OLTARIS 간 비교 수치와 과학적 타당성 검증을 수행하지 않았다.
- Stage 2 통합 코드와 다시 대조했으나, `particle_flux` 필수 scalar와 외부 model-chain provenance 계약이 해결되지 않아 adapter 호환성은 아직 `HOLD`다.

## 재현 가능한 조사 방법

1. `RESEARCH.md`의 공식 출처 표 URL을 연다.
2. 각 페이지에서 scope/input/output/access/rights 문구와 표시된 갱신일을 확인한다.
3. terms·guide에서 `API`, `automation`, `commercial`, `redistribution`, `retention`을 검색하고 없는 항목은 `UNCONFIRMED`로 유지한다.
4. 실제 계정 접근 뒤 UI와 report가 다르면 새 source record와 access date를 추가한다.
5. 실제 출력 전에는 numeric result나 placeholder provenance를 만들지 않는다.

## Control Tower 확인 요청

- SPENVIS 수동·비상업 research run을 Stage 3 첫 후보로 승인할지 결정해 달라.
- 대표 circular LEO 하나의 altitude, inclination, start/end와 duration을 승인해 달라.
- Workstream 60과 함께 AE9/AP9 run mode 및 solar model/confidence 정책을 정해 달라.
- Workstream 10에 TID-only variant, model chain, raw artifact manifest 변경 요청을 전달해 달라.
- SPENVIS/OLTARIS 운영자에게 commercial/automation/retention/redistribution 조건을 서면 문의할 담당자를 정해 달라.
- 공통 환경 계약 변경과 실제 모델 출력 검증 전에는 구현 연결 또는 Stage 3 완료를 선언하지 말아 달라.
- 독립 검토 후에만 `VERIFIED` 또는 `INTEGRATED`를 판단해 달라.

## Control Tower 독립 검증 — 2026-08-19

- 판정: `INTEGRATED` — **조사·계약 준비 패키지**만 검증·통합했다. Stage 3 구현 또는 실제 TID 경로 완료 판정이 아니다.
- 공식 출처: SPENVIS home/terms/help 11개와 OLTARIS home/user guide/기술보고서 3개의 접근성을 재확인했다.
- 내용 대조: SPENVIS 등록·무료 사용, 상업 목적 사전 허가, acknowledgement·백업 책임, AE9/AP9 v1.50 run mode, 단일 segment, SHIELDOSE-2·ASCII 출력 주장을 공식 원문에서 재현했다.
- OLTARIS 대조: 승인형 계정, circular Earth orbit, HZETRN, silicon dose, ASCII ZIP, Grid Engine ID·TARIS version·submission time을 공식 원문에서 재현했다.
- 계약 대조: 현재 `RADIATION_ENVIRONMENT.particle_flux` 필수값, 단일 `model_name/model_version`, 제한된 `calculation_run`으로는 TID-only 외부 model chain을 안전하게 표현할 수 없다는 변경 요청이 실제 schema와 일치한다.
- False PASS 검토: 실제 출력·수치·가짜 hash를 만들지 않았고, 상업·자동화·재배포·불확실성 정책이 미확인인 경로를 모두 `HOLD`로 유지했다.
- 현재 한계: 실제 계정 실행 0건, 실제 환경 출력 0건, 과학적 교차검산 0건이다.

## Git 통합

- 브랜치: `main`
- 검증된 통합 commit: `c26b15a` — `docs(env): integrate verified Stage 3 model research`
- 원격: `origin` (`https://github.com/WeepingHeron/SPECTRA.git`), push 완료
- 제외: 사용자 소유의 미추적 `.obsidian/`과 병렬 작업 중인 `docs/workstreams/40-parts-evidence/`
