# 30 Environment Model Handoff — Round 03

## Status

`CHANGES_REQUESTED — H03 / evidence remains HOLD`

실제 SPENVIS artifact 1세트와 parser 검증은 확보했다. 그러나 provider job reference, action-specific 권리 승인과 raw artifact manifest v2가 없으므로 SPECTRA `RADIATION_ENVIRONMENT` 발행은 승인하지 않는다.

## H03 Control Tower 독립 검증 — 2026-08-20

- 외부 private bundle의 원본 9개 SHA-256을 `SHA256SUMS`로 재검증해 모두 일치했다.
- 상대 경로 순으로 정렬한 checksum line 집합의 SHA-256이 `aa299946677dc082fa48cfea4efa2501a10478a92fde04643c429ab77bbfc163`로 local manifest와 일치했다.
- 실제 `spenvis_s2o.txt`를 parser로 읽어 build `4.6.14.3582`, project `SPECTRA_MVP_LEO_001`, 365일 mission, centre-of-Al-spheres 4π, Si target, 1·2·3·4 mm와 `rad(Si)` signature를 재현했다. 수치는 문서·Git에 복제하지 않았다.
- schema 14개, fixture 3/83, simulation 31개, environment 8개, assurance 19 evaluated·2 `NOT_EVALUATED` 전체 회귀가 통과했다.
- parser 성공 후에도 후보 4개가 `HOLD_PENDING_PROVENANCE_AND_RIGHTS`를 유지하고 contract emission이 차단되는 점은 안전하다.
- 그러나 import request의 모든 필수 역할을 **동일 artifact ID와 동일 파일 경로 하나**에 매핑한 공격이 `SOURCE_COMPLETENESS_MISSING`이나 중복 오류 없이 parser까지 도달해 `CONTRACT_EMISSION_NOT_APPROVED`만 반환했다. 즉 final HOLD는 유지되지만 source-role completeness가 우회된다.

### H04 수정 요구

1. MVP의 필수 역할은 각각 정확히 한 번만 매핑되게 한다.
2. 서로 다른 필수 역할이 같은 artifact ID 또는 같은 resolved file path를 공유하면 stable 중복 오류로 거부한다.
3. manifest 자체의 중복 artifact ID를 dict 생성 전에 탐지해 거부한다.
4. missing role, duplicate role, duplicate artifact ID, cross-role same path 공격 테스트를 추가한다.
5. 실제 bundle의 9/9 hash·actual parser 성공·최종 `HOLD`와 기존 전체 회귀를 유지한다.

## 조사 범위와 소유 파일

- 고정 profile: Earth circular LEO, 550 km, 97.6 deg, 2027-01-01~2028-01-01, single segment
- TID points: centre of Al spheres, Si target, 1/2/3/4 mm Al
- 저장소 외부 로컬 원본 bundle: `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/`
- Control Tower 전달문: `docs/workstreams/30-environment-model/handoffs/HANDOFF-ROUND-03.md`
- 갱신: `REFERENCE_PATH.md`, `RESEARCH.md`, `CURRENT.md`, `CURRENT-03.md`
- adapter: `src/spectra_env_adapter/spenvis_shieldose2.py`, fail-closed gate와 environment tests
- 공통 schemas/contracts와 Stage 2·4·5·6 소유 파일은 수정하지 않았다.
- commit·push하지 않았다.

## 공식 출처와 확인 결과

- 공식 SPENVIS UI와 다운로드 report/ASCII를 대조했다.
- 실제 build는 `4.6.14.3582`, dose model은 SHIELDOSE-2 `2.10`이다.
- mission interval, geometry, target, shielding points와 `mm`/`rad(Si)` 의미를 원본 header에서 확인했다.
- 공식 terms/help에 근거해 수동 research/download는 조건부 후보지만 commercial, automation, cloud storage, display와 redistribution은 서면 확인 전 `UNCONFIRMED`다.

## 권장 첫 모델 경로

- 사람 주도 SPENVIS orbit → AE9/AP9 trapped → SAPPHIRE solar → SHIELDOSE-2
- 실제 output은 source-complete TID candidate로만 읽고 계약 입력으로 직접 발행하지 않는다.
- 1/2/3/4 mm 이산점만 허용하며 보간·외삽하지 않는다.

## Stage 3 계약 초안과 영향

- local manifest에 model/build/project/mission/artifact role/size/SHA-256를 고정했다.
- artifact-set SHA-256: `aa299946677dc082fa48cfea4efa2501a10478a92fde04643c429ab77bbfc163`
- parser는 실제 comma-delimited SHIELDOSE-2 signature, exact units, geometry, target과 depth sequence를 검증한다.
- raw manifest v2 없이는 `RAW_ARTIFACT_MANIFEST_V2_MISSING`; 권리 승인 없이는 `RIGHTS_APPROVAL_MISSING`; parse 후에도 `CONTRACT_EMISSION_NOT_APPROVED`다.
- 기존 `RADIATION_ENVIRONMENT`의 TID-only/model-chain/raw-manifest 호환 문제는 Workstream 10 변경 요청으로 유지한다. dummy particle flux는 만들지 않는다.

## 데이터·권리·자동화 상태

- 실제 artifact: 9개, Git 밖 보존, 개별 SHA-256 완료
- 실제 model output: 존재; 수치는 Git에 복제하지 않음
- synthetic/가짜 output: 없음
- 수동 fetch/local backup: 관찰됨
- commercial/automation/cloud storage/internal display/external display/redistribution: `UNCONFIRMED`
- raw artifact manifest v2: `HOLD_NOT_ISSUED`

## HOLD와 알려진 한계

- SPENVIS 고유 provider job reference가 다운로드 파일에서 확인되지 않는다.
- AE9/AP9 `v1.50` UI 선택은 operator 관찰과 일치하지만 다운로드 report에서 exact version을 독립 확정하지 못했다.
- rights approver, action grant hash, tenant/zone/object generation이 없어 raw manifest v2를 정직하게 만들 수 없다.
- 과학적 적합성·교차검산 또는 부품 radiation assurance 결론을 수행하지 않았다.
- local evidence manifest는 추적용이며 승인된 raw manifest v2를 사칭하지 않는다.

## 재현 가능한 검증

```bash
cd /Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001
shasum -a 256 -c SHA256SUMS

cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 -m unittest tests.environment.test_shieldose2_parser -v
python3 tests/environment/run_all.py
```

## Control Tower 확인 요청

1. local evidence bundle과 실제-format parser를 review 대상으로 받아 달라.
2. 권리 확인 전 `RADIATION_ENVIRONMENT` 발행 `HOLD`를 유지해 달라.
3. 사용자의 다음 행동은 SPENVIS team에 commercial/automation/storage/display/redistribution 범위를 한 번의 서면 문의로 확인하는 것이다.
