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
