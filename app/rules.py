from enum import Enum
from app.schemas import ExpenseSubmission

class RuleOutcome(str, Enum):
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"
    NEEDS_AI_REVIEW = "needs_ai_review"

# Business thresholds — tune these to whatever policy you want
AUTO_APPROVE_LIMIT = 50.0      # under this, no review needed at all
HARD_REJECT_LIMIT = 5000.0     # above this, always reject (must be resubmitted via a different process)
RECEIPT_REQUIRED_ABOVE = 25.0  # expenses above this need a receipt

class RuleResult:
    def __init__(self, outcome: RuleOutcome, reason: str):
        self.outcome = outcome
        self.reason = reason

    def __repr__(self):
        return f"RuleResult(outcome={self.outcome}, reason='{self.reason}')"


def evaluate_deterministic_rules(expense: ExpenseSubmission) -> RuleResult:
    """
    Pure function: same input always produces same output.
    No AI, no randomness, no side effects — this is what makes it fast,
    cheap, and 100% auditable.
    """

    # Hard reject: over the absolute ceiling
    if expense.amount > HARD_REJECT_LIMIT:
        return RuleResult(
            RuleOutcome.AUTO_REJECTED,
            f"Amount ${expense.amount} exceeds hard limit of ${HARD_REJECT_LIMIT}"
        )

    # Hard reject: receipt required but missing
    if expense.amount > RECEIPT_REQUIRED_ABOVE and not expense.receipt_url:
        return RuleResult(
            RuleOutcome.AUTO_REJECTED,
            f"Receipt required for expenses over ${RECEIPT_REQUIRED_ABOVE}, none provided"
        )

    # Auto-approve: small, low-risk, has whatever info it needs
    if expense.amount <= AUTO_APPROVE_LIMIT:
        return RuleResult(
            RuleOutcome.AUTO_APPROVED,
            f"Amount ${expense.amount} is under auto-approve limit of ${AUTO_APPROVE_LIMIT}"
        )

    # Everything else is a judgment call
    return RuleResult(
        RuleOutcome.NEEDS_AI_REVIEW,
        f"Amount ${expense.amount} is above auto-approve limit but below hard reject — needs judgment"
    )