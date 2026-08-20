# 30 Environment Model Handoff — Round 03

## Status

`HOLD`

실제 SPENVIS artifact 1세트와 parser 검증은 확보했다. 실행이나 다운로드 오류는 없었다. 다만 provider 고유 job reference, action-specific 권리 승인과 raw artifact manifest v2가 없으므로 SPECTRA `RADIATION_ENVIRONMENT` 발행은 승인하지 않는다.

## 조사 범위와 소유 파일

- 고정 profile: Earth circular LEO, 550 km, 97.6 deg, 2027-01-01~2028-01-01, single segment
- TID points: centre of Al spheres, Si target, 1/2/3/4 mm Al
- 저장소 외부 로컬 원본 bundle: `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/`
- 저장소 문서: `/Users/taehoon/Desktop/IAA/SPECTRA/docs/workstreams/30-environment-model/`
- adapter: `/Users/taehoon/Desktop/IAA/SPECTRA/src/spectra_env_adapter/spenvis_shieldose2.py`
- 공통 schemas/contracts와 Stage 2·4·5·6 소유 파일은 수정하지 않았다.
- commit·push하지 않았다.

## 실제 실행 경로

1. SPENVIS orbit generator로 고정 LEO trajectory 생성
2. IRENE AE9/AP9로 trapped proton/electron flux 생성
3. SAPPHIRE로 solar particle mission fluence 생성
4. SHIELDOSE-2로 Al shielding 뒤 Si TID 계산

각 화면은 같은 계산의 반복이 아니라 다음 단계가 앞 단계의 산출물을 사용하는 연속 실행이었다.

## 공식 출처와 확인 결과

- 실제 SPENVIS build: `4.6.14.3582`
- dose model: SHIELDOSE-2 `2.10`
- project: `SPECTRA_MVP_LEO_001`
- mission interval, geometry, target, shielding points와 `mm`/`rad(Si)` 의미를 다운로드 report header에서 확인했다.
- AE9/AP9 `v1.50`은 UI 선택으로 관찰했지만 다운로드 report에서 exact version을 독립 확정하지 못했다.
- commercial, automation, cloud storage, display와 redistribution 권리는 서면 확인 전 `UNCONFIRMED`다.

## 확보한 원본

- 실제 artifact 9개
- bundle 크기: 약 1.1 MB
- artifact-set SHA-256: `aa299946677dc082fa48cfea4efa2501a10478a92fde04643c429ab77bbfc163`
- 개별 hash 목록: `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/SHA256SUMS`
- 추적 manifest: `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/local-evidence-manifest.json`

`raw/`의 HTML은 실행 입력과 설정을 보여 주는 report이고, TXT는 trajectory·flux·fluence·attenuation·dose 표를 담은 기계 판독용 출력이다. 최종 TID 표는 `spenvis_s2o.txt`, 해당 입력 report는 `spenvis_s2p.html`이다.

## 원본 보관 원칙

- 현재는 `/Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001/` 폴더를 통째로 보존한다.
- 저장소 내부 경로이지만 루트 `.gitignore`의 `.local/` 규칙으로 Git 추적에서 제외한다.
- 1.1 MB로 작으므로 삭제로 얻는 이점보다 provenance 손실 위험이 크다.
- Git 저장소에는 넣지 않는다.
- 장기 보관 시에는 개인 또는 프로젝트 전용 비공개 저장소에 폴더 구조를 유지해 복사하고, 복사 후 `shasum -a 256 -c SHA256SUMS`로 검증한다.
- SPENVIS의 cloud storage 및 redistribution 권리가 확인되기 전에는 공유 드라이브, 공개 링크, 저장소 또는 외부 배포 위치로 옮기지 않는다.

## Stage 3 계약 초안과 영향

- parser는 실제 comma-delimited SHIELDOSE-2 signature, exact units, geometry, target과 depth sequence를 검증한다.
- 1/2/3/4 mm 이산점만 허용하며 보간·외삽하지 않는다.
- raw manifest v2 없이는 `RAW_ARTIFACT_MANIFEST_V2_MISSING`이다.
- 권리 승인 없이는 `RIGHTS_APPROVAL_MISSING`이다.
- parse 성공 후에도 현재는 `CONTRACT_EMISSION_NOT_APPROVED`다.
- dummy particle flux나 가짜 model output은 만들지 않았다.

## 검증 결과

- SHA-256: 9/9 통과
- parser 및 HOLD gate: 8 tests 통과
- 실제 수치는 Git에 복제하지 않음
- synthetic 실제-output 사칭 없음

```bash
cd /Users/taehoon/Documents/Codex/SPECTRA/private-evidence/environment/spenvis/SPECTRA-SPENVIS-MVP-001
shasum -a 256 -c SHA256SUMS

cd /Users/taehoon/Desktop/IAA/SPECTRA
python3 tests/environment/run_all.py
```

## HOLD와 사용자 다음 행동

HOLD는 계산 실패가 아니라 권리와 provider provenance가 미확정이기 때문이다. 다음 행동은 SPENVIS team에 commercial use, automation, private/cloud storage, internal/external display, raw/derived output redistribution 허용 범위를 한 번의 서면 문의로 확인하는 것이다.
