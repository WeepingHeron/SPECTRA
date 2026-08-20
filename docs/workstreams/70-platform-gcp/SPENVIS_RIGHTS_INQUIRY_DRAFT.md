# SPENVIS Rights and Run Reference Inquiry — Draft

## 사용 상태

`DRAFT_NOT_SENT`

이 초안은 SPENVIS team에 한 번의 서면 문의로 SPECTRA의 MVP research와 향후 commercial product에서 필요한 동작별 권리를 확인하기 위한 것이다. 이 문서는 허가가 아니며, 회신 전 모든 미확인 동작은 `HOLD`다.

## 영문 문의 초안

**Subject: Request for written clarification of SPENVIS output storage, processing, display, redistribution, and run-reference rights**

Dear SPENVIS Team,

We are developing SPECTRA, an evidence-traceability prototype for spacecraft radiation-assurance review. SPECTRA does not certify flight suitability and does not replace radiation testing. We have completed one human-operated SPENVIS research run through the registered web interface and downloaded the output files made available to that account. Before we store, process, display, or reuse any output in the prototype, we would like written clarification of the permissions and conditions that apply.

Could you please answer each row below separately? A “yes, subject to conditions” answer is welcome; please identify the applicable terms, attribution, audience, retention, volume, model-specific third-party restrictions, or permission process.

| Proposed action | Requested clarification |
|---|---|
| Non-commercial research | May our team use outputs from a human-operated registered-account run for an internal non-commercial MVP evaluation? |
| Commercial evaluation and product use | Is separate Institute or ESA permission required for internal commercial evaluation, a customer pilot, or a paid SPECTRA product? How should we request it? |
| Automation | May we automate run submission, batch execution, authenticated retrieval, or API access? If any automation is allowed, which documented endpoint, authentication method, rate limit, and volume limit apply? |
| Local private copy | May the account holder retain a private backup of the complete input/output bundle for provenance and reproducibility? |
| Private cloud storage | May that bundle be stored in a private Google Cloud Storage bucket with no public access, tenant isolation, access logging, retention/deletion controls, and no inclusion in source control? Please distinguish research and commercial use. |
| Automated extraction and processing | May approved private copies be parsed by deterministic software? May they be sent to Google Cloud Document AI or Vertex AI for extraction/structuring if access is restricted and the service is not used to train a public model? Please state any region, logging, subprocessors, or retention restrictions. |
| Internal display | May raw output excerpts, tables, charts, and derived values be displayed to authenticated project reviewers or customer-authorized users? Please distinguish complete raw output from limited excerpts and derived values. |
| External/public display | May raw excerpts, screenshots, charts, or derived results be shown in an external demonstration, presentation, publication, or public product UI? What acknowledgement and review conditions apply? |
| Raw-output redistribution | May complete or partial SPENVIS input/output files be delivered to another team member, customer, reviewer, or downloadable Evidence Packet? Please distinguish research, customer, and public recipients. |
| Derived-output redistribution | May normalized numerical values, calculations based on SPENVIS outputs, charts, summaries, hashes, and provenance metadata be shared with customers or the public when raw files are not redistributed? |
| Retention and deletion | Are there required or prohibited retention periods for downloaded input/output bundles? Must copies be deleted when an account, project, permission, or underlying model term changes? |
| Third-party models | Do AE9/AP9, SAPPHIRE, SHIELDOSE-2, or other models used through SPENVIS impose separate storage, processing, display, attribution, or redistribution conditions? |

For provenance, could you also advise how a downloaded bundle should identify one exact provider run?

- Is there a stable, provider-issued job/run ID in the UI, report, project backup, or downloadable metadata?
- If only a project reference is available, which project ID, timestamp, platform build, model configuration, or backup file should be preserved to identify the run unambiguously?
- May that reference and the SHA-256 hashes of downloaded files be stored and displayed as provenance metadata?

Our intended safeguards are: no public Cloud Storage access; no credentials or raw files in Git; immutable object generations and SHA-256 verification; action-specific access approval; short retention where permitted; and immediate display/processing suspension if permission expires or is withdrawn.

Please identify the SPENVIS Terms and Conditions, Rules of Conduct, acknowledgement language, and any separate written license or permission that should be attached to the approval record. If the answer depends on whether SPECTRA remains a non-commercial research prototype or becomes a commercial/customer service, please answer those scopes separately.

Thank you for your guidance.

Sincerely,

`[requester name / organization / registered account / contact]`

## 회신을 rights snapshot으로 전환할 때

회신 원문을 그대로 Git에 넣지 않는다. 권리 책임자는 승인된 저장소에 회신을 보존하고 다음 항목을 action별로 기록한다.

- rightsholder/issuer와 회신자 권한
- inquiry·reply 날짜와 stable reference
- research/commercial scope
- `FETCH`, `PRIVATE_STORE`, `PROCESS_DOCUMENT_AI`, `PROCESS_VERTEX_AI`, `DISPLAY_INTERNAL`, `DISPLAY_EXTERNAL`, `REDISTRIBUTE_RAW`, `REDISTRIBUTE_DERIVED`
- audience, tenant, region, purpose, retention/deletion, attribution
- third-party model별 추가 조건
- provider job/run reference 형식
- valid_from/valid_until/revocation 조건
- reviewer, independent approver, approval target hash와 history anchor

부분 회신이나 모호한 회신은 답하지 않은 action을 `UNCONFIRMED`로 유지한다. raw manifest 발행에는 최소 `FETCH`와 `PRIVATE_STORE`, active approval과 provider job reference가 필요하다.
