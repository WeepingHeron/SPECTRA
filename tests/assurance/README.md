# Assurance attack runner

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/run_all.py
```

The command prints one JSON result document and exits non-zero when an evaluated
attack does not reach its expected fail-closed result, a recorded `actual` value
is stale, a deterministic control changes, or an optimistic False PASS appears.

`manifest.json` is both the attack specification and the recorded baseline. Each
entry has one intent, target contract, mutation, expected result and last
observed result. `DEPENDENCY_WAIT` entries are reported as `NOT_EVALUATED`; they
are not counted as passes or included in the False PASS denominator.

`ASR-D01` is an evaluated attack set that calls the Workstream 20 H02 MVP
Decision Engine. Its subattacks cover non-finite numbers, generic factors, ECC
distribution and failure-mode corruption, policy approval attacks, synthetic
support promotion, and Change Impact postcondition deletion. Engine errors are
normalized by this assurance runner to `INVALID_INPUT / NOT_EVALUATED / HOLD`;
post-result mutations must be rejected while the original engine result remains
`NOT_EVALUATED / HOLD`.

`ASR-D03` directly calls the Workstream 20 H03 production API
`evaluate_runtime_mitigation()`. Three synthetic controls separately pin the
WATCHDOG, TMR, and SEL_PROTECTION arithmetic while remaining
`VALID / NOT_EVALUATED / HOLD`. Eighteen single-intent attacks cover runtime
eligibility, declared-projection conflicts, method and evidence links, policy
hash/approval/history boundaries, and result postconditions. TMR eligibility
failures and missing or mis-scoped destructive-mode inputs must not emit a
computed projection. Result tampering is normalized to
`INVALID_INPUT / NOT_EVALUATED / HOLD` only after the runtime result schema has
rejected the mutated field.

The JSON summary reports top-level cases, evaluated attack executions,
evaluated controls, dependency-wait cases, False PASSes, and failures
separately. `ASR-D02` remains `NOT_EVALUATED` until real deployed GCP bytes,
generation metadata, and IAM behavior exist to attack.

The H04 deployed-GCP preparation package is isolated under `gcp_d02/`. Its
offline validator checks the prepared matrix, Assurance-owned synthetic fixture,
stable-code expectations, False Accept/False PASS rules, and empty evidence
template. It does not call GCP or add any execution to the main assurance
summary:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/assurance/gcp_d02/run_preparation.py
```
