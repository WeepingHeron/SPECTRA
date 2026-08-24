# SPECTRA 최신 발표 패키지 독립 Audit

## 평가 전제

지정된 현재 파일을 직접 검토했다.

- 발표자료: `/Users/taehoon/Desktop/IAA/SPECTRA/demo/index.html`
- Product Demo: `/Users/taehoon/Desktop/IAA/SPECTRA/demo/roadmap-lab.html`
- 대본: `/Users/taehoon/Downloads/spectra_7min_presentation_script_v3.md`

Product Demo는 정적 화면과 코드 경로만 평가했다. 마지막 UI 변경 후 실제 브라우저 회귀가 완료됐다고 보지 않았다. 실제 environment contract 0건, 승인 BOM 기반 exact-part evidence 0건, 실제 후보 판단 미사용, 최종 assurance `HOLD`를 전제로 채점했다.

## 1. 총점과 항목별 점수

| 평가 항목 | 배점 | 점수 | 판단 |
|---|---:|---:|---|
| Multi-Agent 아키텍처 및 GCP 인프라 | 35 | **30** | 역할·실패 경계와 저장 실행 기록은 강하지만 실제 evidence 기반 완주와 운영 보안은 미완성 |
| 할루시네이션 방어·신뢰성 | 20 | **17** | hash·권리·exact target·coverage·HOLD가 일관되지만 실제 승인 체계와 브라우저 회귀가 남음 |
| 비즈니스 임팩트·문제정의 | 30 | **23** | Excel/PDF 검토 문제와 변경 재검사 가치는 명확하나 KPI·비용·운영 통합은 미검증 |
| 팀 시너지·프레젠테이션 | 15 | **12** | 자료와 대본의 흐름은 좋지만 7분 시연 조작이 과밀하고 코드와 조작 큐 사이 불일치가 있음 |
| **총점** | **100** | **82** | **CONDITIONAL GO** |

1인 발표라는 이유로 감점하지 않았다. 이 항목은 사람 수가 아니라 역할 분리, 검증 책임, 발표 전달력으로 평가했다.

### 주요 가점 근거

- Mission·Parts·Assurance Agent가 숫자 생성자가 아니라 서로 다른 evidence 책임과 실패 경계를 소유한다고 명확히 설명한다.
- Slide 10은 1–3번 저장 실행 기록과 4–5번 동작 예시를 구별하며, snapshot·not live·not pen test·not KMS를 화면에서 밝힌다.
- Product Demo는 파일 열기, hash, 출처·권리, 대상 일치, 적용 범위, 안전 종료의 여섯 관문을 코드로 구분한다.
- 실제 SPENVIS·TI bundle 후보는 권리와 외부 승인 anchor가 없어 3번에서 멈추고, TI PDF 추출 후보는 식별 후보를 얻어도 시험 적용성이 닫히지 않아 5번에서 멈추도록 설계됐다.
- 변경 종류에 따라 재검사 시작점을 달리한다. ECC는 판단 규칙, 차폐는 적용 범위, 부품 교체는 대상 일치부터 다시 연다.
- 대본은 실제 계약·승인 evidence 0건, ROI 미측정, actual candidate 판단 미사용, 최종 HOLD를 일관되게 유지한다.

### 주요 감점 근거

- Product Demo는 로컬 UI이며 GCP Multi-Agent 실행 및 실제 승인 workflow와 연결된 운영 화면이 아니다.
- 실제 candidate 버튼은 원본 PDF·bundle을 현장에서 새로 처리하는 기능이 아니라 사전에 생성된 receipt를 불러오는 경로다. 이를 “실시간 실제 PDF 분석”처럼 표현하면 즉시 감점된다.
- KMS 서명, 실제 사용자 RBAC, reviewer 인증, 보존·폐기, 승인 위임, 침투시험, 장애 복구가 미완성이다.
- 비용, 처리시간, 반려율, 지원 인력, SLA가 측정되지 않았다.
- 실제 브라우저 회귀와 사람 낭독·클릭 리허설이 모두 `NOT_MEASURED`다.

## 2. 비전문가가 30초 안에 이해하는 한 문장

> SPECTRA는 AI가 우주부품의 안전성을 대신 판정하는 제품이 아니라, 흩어진 Excel·PDF·시험 근거가 같은 임무와 정확한 부품에 적용되는지 확인하고, 하나라도 부족하거나 바뀌면 승인을 HOLD하는 검토 플랫폼입니다.

이 문장은 문제, 제품 기능, 안전 경계와 조직 내 역할을 동시에 전달한다.

## 3. 발표자료–대본–시연 연결성

전체 연결성은 좋다. 발표자료 1–4장은 흩어진 evidence와 COTS 검증 문제를 설명하고, 5–8장은 identity·합성 계산·HOLD 원칙을 보여 준다. 9–10장은 결정론적 Core와 Multi-Agent 책임 분리를 제시하고, 11장에서 Product Demo로 이동해 실제 검토 workflow를 보여 준다. 대본 v3도 이 13장 순서를 그대로 따른다.

특히 Product Demo의 세 단계가 발표 주장과 잘 연결된다.

1. 파일 또는 receipt를 선택한다.
2. 여섯 안전 관문 중 어디에서 멈추는지 확인한다.
3. ECC·차폐·부품 변경 시 영향받은 관문부터 다시 연다.

다만 현장 시연 전에 반드시 해결해야 할 연결 오류가 있다.

- Product 초기 안내에는 “선택한 자료를 **다섯 관문**으로 확인합니다”라고 적혀 있지만, 코드·대본·실제 pipeline은 **여섯 관문**이다.
- 대본의 “검사 시작 → 세 후보를 차례로 클릭”만으로는 세 결과가 모두 실행되지 않는다. 후보를 바꿀 때마다 검사 상태가 초기화되므로 각 후보에서 `검사 시작`을 다시 눌러야 한다.
- “실제 후보 3개”는 실제 원본을 현장에서 새로 분석하는 것이 아니라 실제 후보의 사전 생성 receipt를 여는 것이다. 버튼과 발화 모두 “실제 후보 receipt”라고 해야 정확하다.
- 1분 35초 안에 합성 후보 3개, 실제 후보, TI PDF 후보, ECC 변경까지 모두 보여주는 것은 클릭·전환 지연을 고려하면 공격적인 구성이다.

## 4. 개선 우선순위

### P0 — 제출 전에 반드시 닫을 것

1. **최종 브라우저 회귀를 실행한다.** 발표용 해상도에서 Slide 11 링크, 새 탭, 예시·실제 후보 로딩, 후보별 재실행, Step 3 변경 재검사를 처음부터 끝까지 확인해야 한다. 현재는 구현 의도만 평가 가능하다.
2. **관문 수와 후보 성격을 일치시킨다.** “다섯 관문”을 여섯 관문으로 통일하고, “실제 후보 3개”가 사전 생성된 실제 후보 receipt라는 사실을 화면과 발화에 명시한다.
3. **시연 조작 큐를 실제 상태 전이와 맞춘다.** 후보를 바꿀 때마다 `검사 시작`을 다시 눌러야 한다. 전체를 보여주기보다 정상 control 1개와 실제 TI candidate 1개로 고정하는 편이 안전하다.

### P1 — 파일럿 신뢰성을 위해 필요한 것

1. reviewer ID, 역할, 요청·제외·검토 행동, prior receipt hash와 최종 receipt hash를 UI에서 볼 수 있는 승인·감사 화면으로 연결한다.
2. 실제 사용자 인증, RBAC, KMS 서명, evidence 보존·폐기, 권한 회수, 장애 복구 및 책임 인계 기준을 운영 contract로 만든다.
3. pilot KPI의 기준선을 먼저 측정한다. `case당 active review time`, `trace completeness`, `보완 return rate`에 현재값·목표·측정 책임자·측정 기간이 필요하다.

### P2 — 설득력과 구매 가능성을 높일 것

1. Slide 9의 Python·NumPy·SciPy 등 기술 목록보다 reviewer가 받는 검토 packet, HOLD 사유, 다음 행동을 우선 보여 준다.
2. 기존 Excel/PDF를 교체한다고 말하지 말고, 문서 저장소·BOM·승인 시스템 위에 evidence trace 계층으로 붙는 통합 모델을 제시한다.
3. 실제 파일럿 이후 GCP 사용료, 문서 처리량, 검토 지원 인력, 보존 비용과 예상 운영 SLA를 공개한다.

## 5. 7분 안에 자를 내용과 반드시 남길 장면

### 반드시 자를 내용 1개

**Slide 4의 1·4·5 mm 개별 차폐 설명을 자른다.**

Slide 6에서 범위 안 계산과 5 mm 차단을 다시 보여 주므로 내용이 중복된다. Slide 4는 “차폐 수치만으로 부품 적합성이 결정되지 않는다”라는 한 문장만 말하고 바로 넘기는 것이 좋다.

### 반드시 남길 장면 1개

**TI 328쪽 PDF 추출 receipt가 `5962L1420901VXC`, 제조사, TID 표지를 찾았음에도 5번 적용성 관문에서 HOLD되는 장면을 남긴다.**

이 장면 하나에 AI 추출, 원문 결속, exact-part 후보, 사람 검토 책임, 파괴성 SEE 공백과 fail-closed 원칙이 모두 들어 있다. 단, 현장에서 PDF를 새로 분석한 것처럼 말하지 말고 “사전에 생성한 실제 문서 추출 receipt를 다시 검토한다”고 설명해야 한다.

## 6. 시연 실패 위험과 fallback

**시연 실패 위험: 중간 이상**

근거는 다음과 같다.

- 마지막 UI 변경 뒤 브라우저 회귀가 실행되지 않았다.
- 발표자료에서 새 탭으로 Product Demo를 여는 전환이 있다.
- 후보를 바꾼 뒤 검사 버튼을 다시 누르는 상태 전이가 대본에 정확히 반영되지 않았다.
- `fetch` 실패를 위한 embedded fallback은 코드에 있지만 실제 발표 브라우저에서 최종 확인되지 않았다.
- 95초 안에 두 batch와 변경 재검사까지 수행해야 한다.

### 권장 fallback

- Product Demo 탭을 발표 전에 미리 열고 Step 1 초기 상태로 둔다.
- 정상 control과 TI PDF candidate 두 건만 시연한다.
- 첫 상호작용 오류가 발생하면 새로고침이나 현장 디버깅을 하지 않는다.
- 즉시 Slide 11로 돌아가 다음처럼 설명한다.

> “시연 화면은 지금 보신 여섯 관문을 사용합니다. 실제 TI 문서에서 부품번호·제조사·TID 표지 후보까지 추출했지만 시험 조건과 SEE 적용성이 닫히지 않아 5번에서 HOLD합니다. 오류 상황에서도 새 값을 만들거나 승인으로 승격하지 않습니다.”

Fallback에서도 actual assurance, live extraction 또는 브라우저 검증 완료를 주장해서는 안 된다.

## 7. 예상 심사 질문 5개와 짧은 모범답

### 1. 실제로 승인 가능한 environment나 부품 evidence가 있습니까?

> 없습니다. 실제 environment contract와 승인 BOM 기반 exact-part evidence는 모두 0건이며 최종 assurance는 HOLD입니다.

### 2. 시연에서 328쪽 PDF를 실시간으로 AI가 읽는 것입니까?

> 아닙니다. 로컬 처리로 미리 생성한 추출 receipt를 검토합니다. 부품번호·제조사·TID 표지는 승인되지 않은 후보이며 판단에는 사용하지 않습니다.

### 3. AI가 틀렸을 때 최종 책임은 누가 집니까?

> AI는 후보 추출과 근거 구조화를 지원할 뿐입니다. 결정론적 gate가 사용 가능 여부를 제한하고, 최종 승인은 인증된 조직 reviewer가 책임져야 합니다.

### 4. 기존 Excel·PDF 업무에 어떻게 넣습니까?

> 기존 자료원을 없애지 않고, 환경·BOM·시험 PDF·권리·승인 기록을 hash와 identity로 연결하는 검토 계층으로 붙입니다. 실제 연동 방식은 파일럿에서 검증해야 합니다.

### 5. 비용 절감이나 ROI는 얼마입니까?

> 아직 측정하지 않았습니다. 파일럿에서 active review time, trace completeness, 보완 return rate와 운영 비용을 함께 측정한 뒤 ROI를 제시하겠습니다.

## 8. 제출 판단

# **CONDITIONAL GO**

기술적 경계와 사업 문제는 제출 가능한 수준이다. 특히 실제 후보에서도 숫자를 낙관적으로 승격하지 않고 권리·identity·적용성 공백을 명확한 관문에서 HOLD하는 장면은 경쟁력이 있다.

다만 다음 세 조건을 닫기 전에는 무조건 GO로 판단하기 어렵다.

1. 마지막 UI 변경 이후 브라우저 전체 회귀 통과
2. 다섯/여섯 관문 불일치와 “실제 후보 receipt” 표현 교정
3. 정상 control → TI candidate → 변경 재검사의 축약 동선으로 7분 실측 리허설 완료

이 조건들이 닫히면 발표 제출은 GO로 전환할 수 있다. 실제 기업 도입과 실제 방사선 assurance는 별도이며 계속 `HOLD`다.

<oai-mem-citation>
<citation_entries>
MEMORY.md:175-178|note=[static inspection and browser validation were kept separate]
</citation_entries>
<rollout_ids>
01a01cc6-c962-7281-aaea-b62eb5c29dfc
</rollout_ids>
</oai-mem-citation>
