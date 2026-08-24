# SPECTRA Core Product MVP Contract

## 상태

`DEFINED — IN_PROGRESS`

현재 합성 Vertical Slice와 Product UI는 검증된 프로토타입이지만 MVP는 아니다. MVP 완료에는 권리와 출처가 확인된 실제 환경 산출물 1개와 정확한 부품 증거 묶음 1개가 같은 Evidence Chain을 통과해야 한다.

## MVP가 증명할 한 가지

**소형위성 보증 담당자가 한 개 임무와 한 개 정확한 부품을 검토할 때, 흩어진 환경·시험 근거와 제한된 차폐·ECC 가정을 재현 가능한 판정과 다음 행동으로 연결할 수 있다.**

MVP는 부품의 비행 적합성을 인증하지 않는다. 최종 결과가 `HOLD`여도 근거 공백, 차단 규칙과 다음 행동이 정확하면 정상적인 제품 결과다.

## 기준 사용자와 기준 사례

- 사용자: 소형위성 팀의 미션 보증 또는 전자부품 검토 담당자 1명
- 임무: 고정된 LEO 기준 임무 1개
- BOM: exact orderable part number가 확인된 부품 1개
- 환경: 사람이 실행하거나 합법적으로 제공받은 실제 모델 산출물 1개
- 부품 증거: 권리 상태와 원문 locator가 확인된 TID 또는 SEE 시험자료 1묶음
- 비교: 지원 범위 안의 차폐 조건 2개 이상과 ECC 적용 전·후
- 판정 기준: TID 설계 계수, 잔여 SEU 한계와 파괴성 SEE 요구가 명시된 기준 1개

실제 환경 산출물과 부품 증거 원문은 Git에 넣지 않는다. 저장 권리가 확인되기 전에는 외부 격리 위치에서 관리하고 저장 위치·generation·SHA-256·rights reference만 manifest로 연결한다.

## 사용자가 수행하는 흐름

```text
기준 임무와 BOM 1개 불러오기
→ 환경 산출물과 부품 시험 증거의 출처·권리·identity 검증
→ 결정론적 TID·SEE 계산
→ 차폐 또는 ECC 변경 전·후 비교
→ 명시된 판정 기준과 독립 Assurance Gate 적용
→ Evidence Coverage·HOLD 이유·다음 행동 확인
→ EvidencePacket과 Change Impact JSON 내보내기
```

## MVP 필수 기능

1. 고정된 기준 임무·BOM을 불러오고 계약 위반 입력을 거부한다.
2. 실제 환경 산출물의 모델·버전·입력·실행 ID·원본 hash를 추적한다.
3. 정확한 부품 identity와 시험 조건·사건 유형·원문 위치를 표시한다.
4. TID와 비파괴성 SEE 계산을 결정론적으로 재현한다.
5. 차폐 또는 ECC 변경 전·후를 비교하되 각 완화의 failure-mode 경계를 지킨다.
6. 파괴성 SEE, 권리, 판정 기준 또는 필수 provenance가 빠지면 낙관 판정을 차단한다.
7. Evidence Coverage Matrix에서 확인된 근거와 공백을 함께 보여 준다.
8. 한 가지 변경이 어떤 입력·계산·판정·증거를 무효화했는지 보여 준다.
9. UI가 hard-coded 표시값이 아니라 검증된 결과 JSON을 소비한다.
10. EvidencePacket과 Change Impact 결과를 내려받을 수 있다.

## MVP Exit Gate

- [ ] 실제 환경 산출물 1개가 권리·provenance·hash 검증을 통과한다.
- [ ] 실제 exact-part 시험 증거 묶음 1개가 identity·조건·locator 검증을 통과한다.
- [ ] 동일 입력의 TID·SEE·차폐·ECC·판정 결과가 반복 실행에서 일치한다.
- [ ] 변경 전·후 결과와 무효화된 근거가 machine-readable 결과로 남는다.
- [ ] 누락·오염·범위 밖·미승인 입력이 모두 `HOLD` 또는 `NOT_EVALUATED`로 닫힌다.
- [ ] 고정 Assurance 세트에서 False PASS가 0건이다.
- [ ] Product UI가 실제 결과와 합성 fallback을 명확히 구분한다.
- [ ] 사용자가 5분 안에 사례를 실행하고 “왜 이 판정인가”와 “다음에 무엇을 해야 하나”를 찾을 수 있다.
- [ ] 결과 JSON과 원문 locator를 UI에서 추적할 수 있다.
- [ ] 전체 실행·검증 명령과 알려진 한계가 문서화된다.

## 현재 이미 확보된 기반

- Stage 1: EvidencePacket과 v2 계약·공격 fixture
- Stage 2: 결정론적 합성 TID·SEE Vertical Slice
- Stage 5 일부: 합성 차폐·ECC·판정 기준 Decision Engine과 Change Impact
- Stage 6 일부: Core 공격 29회와 별도 experimental runtime 공격 18회에서 False PASS 0; 실제 GCP `ASR-D02`는 `NOT_EVALUATED`
- Stage 7 일부: 교육용 GCP의 private Cloud Run Agent 3개·Workflows·Storage·IAM·Logging 합성 E2E H05
- Stage 8 일부: generated 결과를 소비하는 합성 Product UI와 안전한 offline fallback

## MVP 완료를 위해 남은 핵심

- Stage 3: 첫 실제 환경 산출물의 수동 import·검증 adapter
- Stage 4: 첫 exact-part 시험 증거 묶음과 적용성 gate
- Stage 5: 실제 근거에 적용할 판정 기준의 출처·버전·적용 범위 확정
- Stage 6: 실제 evidence path와 고정 revision GCP 공격 검증
- Stage 8: 실제 contract를 합성 fallback과 구분해 연결하고 원문 locator를 노출

## MVP에서 제외

- 모든 궤도·부품·시험 유형 지원
- 자동 웹 수집과 권리 미확인 PDF 저장
- 자동 부품 추천 또는 비행 적합성 인증
- 3D 수송·복잡 형상 차폐 해석
- 다중 사용자·결제·조직 관리·대량 BOM
- 프로덕션 수준 고가용성·고객 데이터 운영
- LLM이 수치·완화율·최종 판정을 생성하는 기능

Multi-Agent와 GCP는 방사선 계산의 과학적 성립 조건은 아니므로 **Core Product MVP**와 완료 판정을 분리한다. 다만 현재 대회 채점에서는 필수이므로 **Competition Demo Release**에는 실제 Agent별 실행, Cloud Run·Cloud Storage, 오케스트레이션, IAM과 로그 증거가 반드시 필요하다. 로컬 mock이나 아키텍처 그림만으로 이 Release를 완료 처리하지 않는다.

WATCHDOG·TMR·SEL 보호의 합성 runtime 계산은 현재 Core MVP와 Competition Demo 주 흐름에 포함하지 않는다. 과거 검증 결과는 실험적 확장으로 보존하며 실제 장비 구현·현재 임무 채택·효과 입증을 주장하지 않는다.
