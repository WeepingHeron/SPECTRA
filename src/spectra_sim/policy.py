"""Fail-closed synthetic policy evaluation."""

DESTRUCTIVE_SEE_TYPES = {"SEL", "SEB", "SEGR"}


def evaluate_policy(
    required_tid: float,
    tested_tid_limit: float,
    residual_seu: float,
    maximum_residual_seu: float,
    evidence_types: list[str],
    require_destructive_see: bool,
    policy_approved: bool,
) -> list[dict]:
    destructive_present = bool(DESTRUCTIVE_SEE_TYPES.intersection(evidence_types))
    return [
        {
            "rule_id": "TID_MARGIN_V1",
            "outcome": "PASS" if tested_tid_limit >= required_tid else "FAIL",
        },
        {
            "rule_id": "SEU_POLICY_V1",
            "outcome": "PASS" if residual_seu <= maximum_residual_seu else "FAIL",
        },
        {
            "rule_id": "DESTRUCTIVE_SEE_V1",
            "outcome": "PASS"
            if (not require_destructive_see or destructive_present)
            else "FAIL",
        },
        {
            "rule_id": "POLICY_APPROVAL_V1",
            "outcome": "PASS" if policy_approved else "FAIL",
        },
    ]
