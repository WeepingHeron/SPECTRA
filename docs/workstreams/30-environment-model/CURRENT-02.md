# 30 Environment Model Handoff — Round 02

> Historical snapshot. 실제 실행·다운로드 이후의 현재 상태는 `CURRENT-03.md`를 따른다.

## Status

`HOLD`

고정 mission, 모델 실행 profile, rights matrix와 fail-closed intake adapter는 `READY_FOR_REVIEW` 후보 수준으로 작성했다. 그러나 실제 SPENVIS artifact, authenticated run, 승인 storage generation과 rights snapshot이 0건이므로 실제 Environment Evidence Path 자체는 `HOLD`다.

## 조사 범위와 소유 파일

- 생성:
  - `environment/reference-path-v1.json`
  - `src/spectra_env_adapter/__init__.py`
  - `src/spectra_env_adapter/gate.py`
  - `tests/environment/test_intake_gate.py`
  - `tests/environment/run_all.py`
  - `docs/workstreams/30-environment-model/REFERENCE_PATH.md`
  - `docs/workstreams/30-environment-model/CURRENT-02.md`
- 실제 raw/normalized fixture는 생성하지 않았다.
- 공통 schema, 루트 문서와 다른 Workstream 파일은 수정하지 않았다.
- commit·push하지 않았다.

## 고정 기준 경로

- `spectra-mvp-leo-001`
- Earth circular LEO, `550 km`, `97.6 deg`, single segment
- `2027-01-01T00:00:00Z`부터 365일
- spherical Al `1/2/3/4 mm_Al_equivalent`, silicon target
- SPENVIS 4.6.14, AE9/AP9 v1.50 Mean, SAPPHIRE total fluence 95%/stormy magnetic shielding, SHIELDOSE-2

Mission과 solar confidence는 실제 모델 결과가 아니라 `ASSUMED` SPECTRA product baseline이다. Assurance 승인 전 지원 판정에 사용하지 않는다.

## 권리 상태

- 개인·비상업 research와 본인 run의 수동 download/backup: 공식 약관상 조건부 후보
- commercial: Institute/ESA permission 전 `UNCONFIRMED`
- automation: 운영 API 허가 확인 전 `UNCONFIRMED`
- 승인 evidence store ingest: tenant/zone/retention/approver 부재로 `HOLD`
- internal/external display와 redistribution: 범위별 서면 확인 전 `UNCONFIRMED`

## Adapter와 검증 상태

- mission mismatch → `OUT_OF_MODEL_SCOPE`
- missing manifest/artifact/role, Git 내부 raw, schema/hash mismatch, rights grant 누락 → `PROVENANCE_FAILURE + HOLD`
- expired/revoked rights 또는 provider version drift → `STALE_EVIDENCE + HOLD`
- 실제 output signature 미검증 → `PARSER_NOT_CALIBRATED_ON_REAL_OUTPUT + MODEL_FAILURE + HOLD`
- 어떤 실패에서도 numeric environment를 생성하지 않는다.

검증 명령:

```bash
python3 tests/environment/run_all.py
python3 tests/schema/validate_contracts.py
```

2026-08-20 재현 결과:

- Environment intake gate: 5 tests, `OK`
- 공통 schema/semantic gate: schemas 14개, valid fixtures 3개, invalid fixtures 83개, exit code 0
- CLI missing-request probe: `IMPORT_REQUEST_MISSING`, `PROVENANCE_FAILURE`, `HOLD`, exit code 2

## 실제 artifact 상태

- 저장소 후보: 0건
- Downloads 후보: 0건
- 브라우저 authenticated SPENVIS session: 확인되지 않음
- provider run/project ID: 없음
- raw bytes/hash/manifest/storage generation: 없음
- normalized `RADIATION_ENVIRONMENT`: 없음

## HOLD 사유

1. 인증된 사람이 실행한 SPENVIS 결과가 없다.
2. 실제 byte를 둘 승인 tenant/zone/storage generation과 rights approver가 없다.
3. 실제 `spenvis_s2o.txt`가 없어 parser column/unit signature를 고정할 수 없다.
4. 공개 도움말만으로는 SAPPHIRE와 SHIELDOSE-2의 실제 run build/version을 확정할 수 없다.
5. 상업·자동화·표시·재배포 권리는 미확인이다.

## 사용자 행동 한 가지

본인 SPENVIS 계정으로 `REFERENCE_PATH.md`의 profile을 수동 실행하고 전체 project backup과 필수 7개 파일을 `/Users/taehoon/Downloads/SPECTRA-SPENVIS-MVP-001/`에 저장한 뒤 “다운로드 완료”라고 알려 달라.

이후 다음 회차에서 실제 bytes hash, source completeness, model build, run metadata와 rights snapshot을 검증한다. 권리·storage 조건이 부족하면 bytes를 이동하거나 Git에 넣지 않고 metadata-only `HOLD`를 유지한다.

## Control Tower 확인 요청

- reference mission과 SAPPHIRE 95%/stormy 설정을 초기 engineering baseline으로 승인할지 검토해 달라.
- raw manifest v2 artifact에 `role`을 직접 넣을지 adapter import index를 공통 계약으로 승격할지 결정해 달라.
- 실제 ingest 전 tenant/zone/storage/retention과 independent rights approver를 지정해 달라.
- 실제 artifact가 오기 전 Stage 3 또는 MVP environment gate를 완료 처리하지 말아 달라.
