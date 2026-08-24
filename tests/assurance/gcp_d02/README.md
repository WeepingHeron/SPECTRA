# ASR-D02 deployed GCP preparation

This directory is an offline preparation package for the deployed GCP attack set. It does not call Google Cloud and does not convert `ASR-D02` from `NOT_EVALUATED`.

Run the preparation validator from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/gcp_d02/run_preparation.py
```

The validator checks that all IDs are unique, every attack has one declared intent and a fail-closed expected result, fixture references cover every attack, the evidence template contains no live result, and the False Accept/False PASS classifier distinguishes orchestration `SUCCEEDED` from business safety. It exits non-zero when the preparation contract drifts.

## H05 target lock and stop state

Control Tower identified and Workstream 60 recorded one exact H05 target tuple:

- project and region
- Workflow name, revision, and source SHA-256
- Mission, Parts, and Assurance Cloud Run revisions
- common or role-specific image digest
- lock timestamp and reviewer

The target is locked in `manifest.json`. The 2026-08-21 time/usage stop instruction arrived before any attack Workflow execution, Storage upload, endpoint request, or IAM probe. `ASR_D02_DEPLOYED_GCP_STOPPED_H05.json` records the read-only identity check and zero live attack counts; it is not a populated attack-result file. `ASR-D02` therefore remains `NOT_EVALUATED`, and live execution must not resume without a new explicit instruction.

## Evidence evaluation after live execution

Once a separately authorized live runner has executed every case and populated the copied template, evaluate the immutable evidence file offline:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/gcp_d02/run_preparation.py \
  --evaluate-evidence docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_EVIDENCE_H05.json
```

This command still makes no network request. It refuses an unlocked or incomplete target and requires every common and case-specific GCP observation before computing False Accept or False PASS counts.

## Required authority for the later live phase

The executing identity will need narrowly scoped authority to start and inspect the locked Workflow, create and retrieve Assurance-owned synthetic objects by exact generation, read the locked Workflow and Cloud Run revision identities, retrieve correlation-scoped logs, and read relevant IAM policies. It must not receive deployment mutation, service-account key creation, broad project administration, or access to private real evidence. Tokens and credential material must never be written to evidence JSON.

Agent invalid JSON, timeout, and HTTP failure cases require an Assurance-controlled test endpoint or test-only Workflow whose identity is recorded. They must not restore `test_mode`, `failure_role`, or endpoint override fields in the production Workflow.
