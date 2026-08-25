# SPECTRA 수동 업로드 테스트 데이터

이 폴더에는 `SYNTHETIC TEST FIXTURE`와 공식 NASA·ESA·Microchip 자료를 바탕으로 로컬에서 작성한 `PUBLISHED SOURCE SUMMARY`가 함께 있다. 후자는 실제 공개값의 출처를 보존하지만 원 보고서 복제본이나 방사선 보증 근거는 아니다.

## 공통 실행 방법

1. `http://127.0.0.1:8765/demo/evidence-console.html?presentation=1`을 연다.
2. `문서 1개 검사`에서 시험할 파일을 선택한다.
3. 별도 표시가 없으면 주문형번은 `23LC1024-I/SN`, 제조사는 `Microchip Technology`를 그대로 사용한다. 임무 계획 문서는 두 입력을 비워도 된다.
4. 별도 표시가 없으면 처리 권리 확인 체크박스를 켠다.
5. `실제 로컬 검사 실행`을 누르고 후보, 중단 위치, 이유와 다음 행동을 확인한다.

모든 시나리오의 최종 판단은 `HOLD`가 정상이다. 현재 콘솔은 문서 후보를 추출하지만 승인 BOM과 시험 조건까지 자동 결속하지 않기 때문이다.

## 파일별 목적과 예상 결과

| 파일 | 확인할 동작 | 예상 핵심 결과 |
|---|---|---|
| `01_정상후보_부품제조사_사건5종.txt` | 정확한 부품·제조사와 TID/SEU/SEL/SEB/SEGR 추출 | 후보 7개, `VALID`, 최종 `HOLD` |
| `02_부분근거_TID_SEU만.txt` | 파괴성 SEE 언급이 없는 부분 자료 | 후보 4개, `VALID`, 최종 `HOLD` |
| `03_부품번호불일치_다른주문형번.txt` | 찾는 주문형번과 문서의 주문형번 불일치 | 주문형번 후보 없음, 나머지만 추출, `HOLD` |
| `04_제조사누락_부품번호와사건만.txt` | 제조사 문자열이 없는 문서 | 제조사 후보 없음, 나머지만 추출, `HOLD` |
| `05_공격방어_프롬프트주입.txt` | 문서 내부 승인 지시문 방어 | `CONTENT_REJECTED`, 후보 0개, `PROMPT_INJECTION_PATTERN_DETECTED` |
| `06_권리미확인용_체크박스끄고실행.txt` | 처리 권리 미확인 경계 | 체크박스를 끄고 실행하면 `PROVENANCE_FAILURE`, 후보 0개 |
| `07_빈근거_부품과사건표기없음.txt` | 찾을 근거가 없는 문서 | 후보 0개, 값을 만들어내지 않고 `HOLD` |
| `08_복합PDF_합성부품_SYNTHETIC-PART-001.pdf` | 표·다단·차트·각주가 섞인 PDF 파싱 | 주문형번 `SYNTHETIC-PART-001`, 제조사 `SYNTHETIC MANUFACTURER`로 바꾸면 후보 7개, `VALID`, 최종 `HOLD` |
| `09_손상PDF_텍스트추출실패.pdf` | 손상된 PDF의 fail-closed 처리 | `DATA_UNAVAILABLE`, 후보 0개, `PDF_TEXT_EXTRACTION_FAILED` |
| `10_실제공개값_NASA_Micron_MT29F4T08CTHBBM5_TID.txt` | NASA가 공개한 COTS 3D NAND TID 관측값 | LDC·시료 수·39 krad(Si) 실패 지점 추출, 최종 `HOLD` |
| `11_실제공개값_NASA_Hynix_H25QFT8F4A9R-BDF_SEE.txt` | NASA가 공개한 COTS 3D NAND SEE 관측값 | LET·온도·에너지·단면적 추출, 최종 `HOLD` |
| `12_실제공개값_ESA_Micron_MT29F32G08CBACA_TID_SEE.txt` | ESA가 공개한 COTS NAND TID·SEE 요약 | 전압·온도·시료 수·약 20 krad 추출, lot 미상으로 `HOLD` |
| `13_실제임무계획_NASA_Landsat9_궤도수명.txt` | NASA Landsat 9 임무 조건 | 임무명·태양동기궤도·705 km·98.2°·5년 추출, 환경 계산 부재로 `HOLD` |
| `14_실제임무계획_ESA_Sentinel2_궤도수명.txt` | ESA Sentinel-2 임무 조건 | 임무명·태양동기궤도·786 km·98.5°·7년 추출, 환경 계산 부재로 `HOLD` |
| `15_실제부품명세_Microchip_23LC1024.txt` | Microchip 공식 상용 SRAM 명세 | 주문형번·제조사·2.5–5.5 V·동작온도 추출, 방사선 시험 부재로 `HOLD` |

`06`은 파일 내용이 아니라 콘솔의 권리 체크박스 상태를 시험한다. 체크박스를 켜면 일반 후보 추출 시나리오로 처리된다.

`10`~`15`는 원 보고서 자체가 아니라 공식 공개자료의 사실값을 짧게 옮긴 `PUBLISHED SOURCE SUMMARY`다. 각 파일 안에 원문 URL을 적었으며, 관측 실패 지점이나 근사 내성을 보증 rating으로 승격하지 않는다. `13`~`14`의 궤도·기간은 임무 조건이지 방사선 환경 계산값이 아니다.

실행할 때는 파일별 입력값을 다음처럼 바꾼다.

- `10`: `MT29F4T08CTHBBM5` / `Micron`
- `11`: `H25QFT8F4A9R-BDF` / `Hynix`
- `12`: `MT29F32G08CBACA` / `Micron`
- `13`~`14`: 주문형번과 제조사를 비워서 실행
- `15`: `23LC1024-I/SN` / `Microchip Technology`

`문서별 결과표` 메뉴는 이 폴더의 15개 문서와 manifest를 GCP 공개 읽기 전용 버킷에서 불러온다. 문서별 처리 경로·현재 결과·보류 지점과 세 입력 연결 결과를 표시하며, 마지막 `공개 객체 확인` 행에서 공개 객체 수·HTTP 상태·catalog/audit generation을 확인할 수 있다.
