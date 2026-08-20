# SPECTRA MVP Environment Reference Path v1

## 결정

첫 실제 Environment Evidence Path의 입력 범위를 다음 하나로 고정한다.

| 항목 | 고정값 | 상태 |
|---|---|---|
| mission ID | `spectra-mvp-leo-001` | SPECTRA product baseline |
| orbit | Earth circular LEO, single segment | 지원 범위 |
| altitude | `550 km` | `ASSUMED` product input |
| inclination | `97.6 deg` | `ASSUMED` product input |
| validity | `2027-01-01T00:00:00Z` ~ `2028-01-01T00:00:00Z` | 365-day calendar interval |
| shield points | spherical Al `1/2/3/4 mm_Al_equivalent` | 이산점만 지원, 보간·외삽 금지 |
| target | silicon | `rad(Si)` 계열만 허용 |

이 값은 모델 결과나 실제 비행 임무가 아니다. 기존 합성 기준선과의 입력 호환을 위한 명시적 제품 가정이며, 모든 실제 dose 값과 분리한다. 기계 판독 기준은 `environment/reference-path-v1.json`이다.

## 2026-08-20 실제 실행 증거

위 profile을 사용한 사람 주도 SPENVIS 실행 1건을 확보했다. 다운로드된 9개 원본은 Git worktree 외부 로컬 경로 `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/raw/`에 보존했고, 각 byte size와 SHA-256은 같은 bundle의 `local-evidence-manifest.json`과 `SHA256SUMS`에 고정했다.

- provider build: `SPENVIS 4.6.14.3582`
- project: `SPECTRA_MVP_LEO_001`
- mission: `2027-01-01` ~ `2028-01-01`, 365 days
- TID path: `SHIELDOSE-2 2.10`, centre of Al spheres, Si target
- discrete shield points: `1/2/3/4 mm Al`
- artifact-set SHA-256: `aa299946677dc082fa48cfea4efa2501a10478a92fde04643c429ab77bbfc163`

이것은 실제 provider output이지만 아직 승인된 SPECTRA input은 아니다. provider job reference, 권리 approver와 raw artifact manifest v2가 없으므로 수치의 계약 발행은 `HOLD`다. 실제 dose 값은 권리 확인 전 Git 문서나 fixture로 복제하지 않는다.

## 고정 모델 실행 절차

공식 SPENVIS 도움말을 기준으로 다음 순서를 사용한다.

1. 등록 사용자가 SPENVIS 4.6.14에 로그인하고 새 project를 만든다.
2. Earth orbit generator에서 위 원형·단일 구간 mission을 입력한다.
3. AE9/AP9 `v1.50`, `Mean`, default AE9/AP9 energy grid를 실행한다.
4. SAPPHIRE `total fluence`, confidence `95%`, Earth stormy magnetic shielding을 실행한다.
5. SHIELDOSE-2에서 spherical Al, Si target, `1/2/3/4 mm`를 실행한다.
6. `spenvis_sap.html`, `spenvis_sao.txt`, `spenvis_ae9ap9.html`, `spenvis_tri.txt`, `spenvis_sep.html`, `spenvis_sef.txt`, `spenvis_seo.txt`, `spenvis_s2p.html`, `spenvis_s2o.txt`와 provider가 제공하는 project backup metadata를 내려받는다.
7. 실행 직후 provider job/project reference, submit/complete/download UTC, 실제 표시 platform/model build를 기록한다.

AE9/AP9 Mean은 uncertainty bound가 아니다. SAPPHIRE 95%와 stormy shielding은 SPECTRA 초기 engineering input이며 공식 권고나 최종 assurance policy로 승격하지 않는다. Control Tower/Workstream 60이 이 선택을 승인하기 전 결과는 `HOLD`다.

## 동작별 권리 판정 — 2026-08-20 재확인

| 동작 | 판정 | 공식 근거와 해석 |
|---|---|---|
| `LOCATOR` | `ALLOWED` | 공개 home/help/terms URL을 기록할 수 있다. |
| research use | `ALLOWED_WITH_CONDITIONS` | Rules of Conduct는 별도 합의가 없으면 개인·비상업 목적으로 제한하고 acknowledgement를 요구한다. |
| `FETCH` | `ALLOWED_WITH_CONDITIONS` | SPENVIS가 output download와 project backup을 제공하고 약관이 유용한 input/output 백업 책임을 사용자에게 둔다. 본인 계정의 본인 run을 수동 다운로드하는 범위로 제한한다. |
| `PRIVATE_STORE` | `ALLOWED_WITH_CONDITIONS` | 개인 사용 copy와 input/output backup 범위만 후보. 승인 tenant/zone, retention과 rights approver가 없으므로 SPECTRA evidence store ingest는 아직 `HOLD`다. |
| commercial use | `UNCONFIRMED` | Institute 또는 ESA permission이 필요하다. |
| automation | `UNCONFIRMED` | 운영 사이트 자동 호출 계약·rate limit·허용 endpoint를 확인하지 못했다. 수동 UI만 사용한다. |
| internal display | `UNCONFIRMED` | raw output을 제품 UI에 표시할 권리 범위를 확인하지 못했다. metadata-only 표시만 허용 후보다. |
| external display / redistribution | `UNCONFIRMED` | publication acknowledgement 의무는 있으나 raw/derived output 재배포 허가 범위는 명시되지 않았다. |

`ALLOWED_WITH_CONDITIONS`는 raw manifest v2의 즉시 `ALLOWED` grant가 아니다. 실제 snapshot에는 사용자 계정의 약관 동의, 대상 run, tenant, 목적, 보존 위치와 독립 approver가 고정돼야 한다.

## Provenance-complete bundle 조건

Git 밖의 승인 저장소에 다음이 모두 있어야 한다.

- 위 실행에서 생성된 raw bytes 9종과 각 byte size/SHA-256/MIME
- provider platform version/build, project/job reference와 UTC timestamps
- orbit/trapped/solar/dose model의 exact version/build/configuration hash
- raw manifest v2의 tenant/zone, create-only generation과 rights snapshot
- `FETCH`와 `PRIVATE_STORE` action grant
- artifact role과 manifest artifact ID를 연결하는 import request
- 실제 `spenvis_s2o.txt` signature에 대해 승인된 parser version/commit/output hash

현재 raw manifest v2에는 artifact `role`이 없으므로 adapter import request가 role을 별도로 매핑한다. 이 매핑이 없거나 중복·누락이면 `SOURCE_COMPLETENESS_MISSING` 또는 `RAW_MANIFEST_REFERENCE_MISSING`이다.

## 최소 adapter

`src/spectra_env_adapter/gate.py`는 실제 bundle을 읽기 전에 다음을 fail-closed로 검사한다.

- 기준 mission exact match
- raw root가 Git worktree 밖인지
- raw manifest v2 schema
- rights snapshot 유효성 및 `FETCH`/`PRIVATE_STORE`
- 필수 artifact role completeness
- manifest byte size/SHA-256와 실제 bytes 일치
- SPENVIS platform version allowlist

`src/spectra_env_adapter/spenvis_shieldose2.py`는 실제 `spenvis_s2o.txt`의 comma-delimited signature에 맞춰 calibration했다. provider build, project, mission interval, exact `mm`/Al thickness, `rad`/Si dose marker와 6-column table을 검증하며, 1/2/3/4 mm가 아니거나 단위·geometry·target이 달라지면 fail-closed한다. parser가 만든 값은 내부 candidate일 뿐이며 `contract_status=HOLD_PENDING_PROVENANCE_AND_RIGHTS`를 유지한다.

`gate.py`는 실제 file parse 뒤에도 raw manifest v2와 action-specific rights가 없으면 `CONTRACT_EMISSION_NOT_APPROVED + HOLD`로 종료한다. 즉 parser 성공은 `RADIATION_ENVIRONMENT` 발행 승인이 아니다.

실행 형식:

```bash
PYTHONPATH=src python3 -m spectra_env_adapter.gate /absolute/path/to/import-request.json
python3 tests/environment/run_all.py
```

import request는 실제 bundle 외부에 두고 최소한 `mission`, `raw_root`, `manifest_path`, `artifact_files[{role, artifact_id, path}]`를 가진다. 실제 bytes와 local manifest는 Git worktree 외부 전용 보관소에만 있으며, 승인된 raw manifest v2나 normalized contract output은 만들지 않았다.

## 현재 차단과 사용자 행동 한 가지

실제 artifact와 hash는 확보했다. 남은 직접 차단 사유는 **SPENVIS가 제공한 고유 job reference 부재, action-specific 서면 권리 승인 부재, 승인 tenant/object generation 기반 raw manifest v2 부재**다.

사용자가 해야 할 한 가지 행동:

> SPENVIS team에 commercial use, 자동화, private/cloud storage, 내부 표시, raw/derived output 재배포 허용 범위를 한 번의 서면 문의로 확인해 주세요.

그 전에는 local evidence bundle을 승인 raw manifest v2로 승격하거나 normalized `RADIATION_ENVIRONMENT`를 발행하지 않는다.

## 공식 출처

- [SPENVIS Terms and Conditions](https://www.spenvis.oma.be/conditions.php) — commercial permission, acknowledgement, backup responsibility
- [SPENVIS Rules of Conduct](https://www.spenvis.oma.be/regulation.php) — personal/non-commercial default and copying limits
- [Using the SPENVIS system](https://www.spenvis.oma.be/help/system/spenvis.html) — project persistence and HTML/ASCII outputs
- [AE9/AP9 help](https://www.spenvis.oma.be/help/models/ae9ap9.html) — versions, modes, single-segment limit and output files
- [Solar particle model help](https://www.spenvis.oma.be/help/models/sep.html) — SAPPHIRE, confidence and output files
- [Dose model help](https://www.spenvis.oma.be/help/models/dose.html) — shield depth, geometry, target and SHIELDOSE-2 outputs
- [Output format help](https://www.spenvis.oma.be/help/models/outputs.html) — downloadable ASCII format and metadata structure

접근일: `2026-08-20`.
