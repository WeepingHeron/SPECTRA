# SPECTRA MVP Product Contract

## 상태

`DEFINED — IN_PROGRESS`

현재 합성 Vertical Slice와 Product UI는 검증된 프로토타입이지만 MVP는 아니다. MVP 완료에는 권리와 출처가 확인된 실제 환경 산출물 1개와 정확한 부품 증거 묶음 1개가 같은 Evidence Chain을 통과해야 한다.

## MVP가 증명할 한 가지

**소형위성 보증 담당자가 한 개 임무와 한 개 정확한 부품을 검토할 때, 흩어진 환경·시험·완화·정책 근거를 재현 가능한 판정과 다음 행동으로 연결할 수 있다.**

MVP는 부품의 비행 적합성을 인증하지 않는다. 최종 결과가 `HOLD`여도 근거 공백, 차단 규칙과 다음 행동이 정확하면 정상적인 제품 결과다.

## 기준 사용자와 기준 사례

- 사용자: 소형위성 팀의 미션 보증 또는 전자부품 검토 담당자 1명
- 임무: 고정된 LEO 기준 임무 1개
- BOM: exact orderable part number가 확인된 부품 1개
- 환경: 사람이 실행하거나 합법적으로 제공받은 실제 모델 산출물 1개
- 부품 증거: 권리 상태와 원문 locator가 확인된 TID 또는 SEE 시험자료 1묶음
- 비교: 지원 범위 안의 차폐 조건 2개 이상과 ECC 적용 전·후
- 정책: TID 설계 계수, 잔여 SEU 한계, 파괴성 SEE 요구를 포함한 승인 상태가 명시된 정책 1개

실제 환경 산출물과 부품 증거 원문은 Git에 넣지 않는다. 저장 권리가 확인되기 전에는 외부 격리 위치에서 관리하고 저장 위치·generation·SHA-256·rights reference만 manifest로 연결한다.

## 사용자가 수행하는 흐름

```text
기준 임무와 BOM 1개 불러오기
→ 환경 산출물과 부품 시험 증거의 출처·권리·identity 검증
→ 결정론적 TID·SEE 계산
→ 차폐 또는 ECC 변경 전·후 비교
→ 사용자 정책과 독립 Assurance Gate 적용
→ Evidence Coverage·HOLD 이유·다음 행동 확인
→ EvidencePacket과 Change Impact JSON 내보내기
```

## MVP 필수 기능

1. 고정된 기준 임무·BOM을 불러오고 계약 위반 입력을 거부한다.
2. 실제 환경 산출물의 모델·버전·입력·실행 ID·원본 hash를 추적한다.
3. 정확한 부품 identity와 시험 조건·사건 유형·원문 위치를 표시한다.
4. TID와 비파괴성 SEE 계산을 결정론적으로 재현한다.
5. 차폐 또는 ECC 변경 전·후를 비교하되 각 완화의 failure-mode 경계를 지킨다.
6. 파괴성 SEE, 권리, 정책 승인 또는 필수 provenance가 빠지면 낙관 판정을 차단한다.
7. Evidence Coverage Matrix에서 확인된 근거와 공백을 함께 보여 준다.
8. 한 가지 변경이 어떤 입력·계산·판정·증거를 무효화했는지 보여 준다.
9. UI가 hard-coded 표시값이 아니라 검증된 결과 JSON을 소비한다.
10. EvidencePacket과 Change Impact 결과를 내려받을 수 있다.

## MVP Exit Gate

- [ ] 실제 환경 산출물 1개가 권리·provenance·hash 검증을 통과한다.
- [ ] 실제 exact-part 시험 증거 묶음 1개가 identity·조건·locator 검증을 통과한다.
- [ ] 동일 입력의 TID·SEE·완화·정책 결과가 반복 실행에서 일치한다.
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
- Stage 6 일부: 평가 가능한 고정 공격 19개, False PASS 0
- Stage 8 일부: 합성 Product UI와 안전한 offline fallback

## MVP 완료를 위해 남은 핵심

- Stage 3: 첫 실제 환경 산출물의 수동 import·검증 adapter
- Stage 4: 첫 exact-part 시험 증거 묶음과 적용성 gate
- Stage 5: 결정론적 완화·정책 engine
- Stage 6: 새 engine과 실제 evidence path 공격 검증
- Stage 8: hard-coded snapshot을 결과 JSON 소비 방식으로 연결하고 EvidencePacket·Change Impact 노출

## MVP에서 제외

- 모든 궤도·부품·시험 유형 지원
- 자동 웹 수집과 권리 미확인 PDF 저장
- 자동 부품 추천 또는 비행 적합성 인증
- 3D 수송·복잡 형상 차폐 해석
- 다중 사용자·결제·조직 관리·대량 BOM
- 완전한 Multi-Agent 운영
- 프로덕션 수준 GCP 배포·고가용성·고객 데이터 운영
- LLM이 수치·완화율·최종 판정을 생성하는 기능

GCP와 Multi-Agent는 중요한 후속 Stage지만 MVP 제품 가치 검증의 필수 조건으로 묶지 않는다. 단, GCP를 사용한 MVP라고 발표하려면 실제 resource·실행 로그·IAM·비용 증거를 별도로 통과해야 한다.
