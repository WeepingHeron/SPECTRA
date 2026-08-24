# H11 Published Source Package

## 결론

공개 `23LC1024` 시험 논문의 실제 PDF bytes, 공식 DOI/locator, CC BY 4.0 표시와 action별 사용 조건을 하나의 deterministic source gate에 결속했다. 현재 로컬 원문은 `33,130,232` bytes와 SHA-256 `a6cee9eb8eaca8dab8636caf0ad4cd4248fbfccfab57c9ce9af2c7324969f373`가 모두 일치해 `READY_FOR_REFERENCE_REVIEW`에 도달한다.

package composer는 이 통과로 `SOURCE_ARTIFACT_MANIFEST_MISSING`과 `RIGHTS_SCOPE_UNRESOLVED`만 해소한다. 승인 SOIC와 시험 PDIP의 불일치, exact suffix/lot/die, mission environment, TID와 destructive SEE 공백은 그대로 남아 최종 상태는 `SOURCE_READY_COMPARISON_BLOCKED / NOT_COMPARABLE / HOLD`다.

## 공식 근거와 권리 범위

- JLU 공식 record: <https://jlupub.ub.uni-giessen.de/items/bacfbfc4-a5e7-46b1-b2a0-332d8231cc49>
- DOI: <https://doi.org/10.22029/jlupub-19623>
- license: <https://creativecommons.org/licenses/by/4.0/>

공식 record는 PDF와 `Attribution 4.0 International`을 함께 표시한다. CC BY 4.0의 저작권·유사권 범위에서 복제·공유·개작과 형식 변환을 허용하지만 attribution, license notice, 변경 표시와 no-endorsement 경계를 지켜야 한다. 특허·상표·privacy 등 비저작권 권리, 과학적 정확성과 exact-part 적용성은 이 gate가 확인하지 않는다.

## 구현

- source gate: `src/spectra_parts_adapter/published_artifact_gate.py`
- package composer: `src/spectra_parts_adapter/published_reference_package.py`
- candidate manifest: `references/23lc1024-published-source-candidate.json`
- reviewed anchors: `references/23lc1024-published-source-anchors.json`
- tests: `test_published_artifact_gate.py`, `test_published_reference_package.py`

source gate는 provider/DOI/record URL/artifact URL, 검토된 byte size/hash, license, attribution, 8개 action과 4개 조건, manifest/rights review anchor를 모두 검사한다. raw PDF는 Git 밖에 유지하고 receipt에는 bytes나 로컬 경로를 넣지 않는다.

## 공격 검증

- content/hash/size 변조
- candidate와 anchor 동시 재결속
- manifest/rights anchor 누락·변조
- allowlist host suffix 우회와 malformed port
- license·attribution·modification notice 변조
- action 누락·public-access 상속·조건 누락
- optimistic `FOR_DECISION/PASS`
- malformed type과 금지 필드
- source/comparison hash mismatch
- valid source를 이용한 comparison optimism 세탁

실제 PDF 경로를 포함한 source/package 17개와 기존 comparison/evidence 22개, 총 39개 인접 테스트가 통과했다. 이는 공개 reference source의 provenance·license scope 결속 검증이며 actual EvidencePacket, 부품 suitability 또는 radiation assurance 발행이 아니다.
