import pytest
from datetime import date
from app.schemas import ExpenseSubmission
from app.rules import evaluate_deterministic_rules, RuleOutcome

def make_expense(**overrides):
    defaults = dict(
        employee_id="emp_1",
        amount=30.0,
        category="meals",
        description="Team lunch outing",
        expense_date=date(2026, 9, 1),
        receipt_url=None,
    )
    defaults.update(overrides)
    return ExpenseSubmission(**defaults)


def test_small_amount_auto_approved():
    result = evaluate_deterministic_rules(make_expense(amount=20.0))
    assert result.outcome == RuleOutcome.AUTO_APPROVED


def test_large_amount_over_hard_limit_rejected():
    result = evaluate_deterministic_rules(make_expense(amount=6000.0))
    assert result.outcome == RuleOutcome.AUTO_REJECTED


def test_missing_receipt_above_threshold_rejected():
    result = evaluate_deterministic_rules(make_expense(amount=100.0, receipt_url=None))
    assert result.outcome == RuleOutcome.AUTO_REJECTED


def test_missing_receipt_below_threshold_still_approved():
    result = evaluate_deterministic_rules(make_expense(amount=20.0, receipt_url=None))
    assert result.outcome == RuleOutcome.AUTO_APPROVED


def test_midrange_amount_needs_ai_review():
    result = evaluate_deterministic_rules(make_expense(amount=300.0, receipt_url="http://receipts.com/1"))
    assert result.outcome == RuleOutcome.NEEDS_AI_REVIEW


def test_boundary_exact_auto_approve_limit():
    result = evaluate_deterministic_rules(make_expense(amount=50.0, receipt_url="http://receipts.com/1"))
    assert result.outcome == RuleOutcome.AUTO_APPROVED


def test_exact_receipt_threshold_boundary():
    # exactly at RECEIPT_REQUIRED_ABOVE (25.0) — rule uses '>', so 25.0 itself doesn't require receipt
    result = evaluate_deterministic_rules(make_expense(amount=25.0, receipt_url=None))
    assert result.outcome == RuleOutcome.AUTO_APPROVED


def test_just_above_receipt_threshold_requires_receipt():
    result = evaluate_deterministic_rules(make_expense(amount=25.01, receipt_url=None))
    assert result.outcome == RuleOutcome.AUTO_REJECTED


def test_exact_hard_reject_boundary():
    # exactly at HARD_REJECT_LIMIT (5000.0) — should NOT reject, since rule uses '>'
    result = evaluate_deterministic_rules(make_expense(amount=5000.0, receipt_url="http://x.com/r.pdf"))
    assert result.outcome == RuleOutcome.NEEDS_AI_REVIEW


def test_negative_amount_rejected_at_schema_level():
    # Pydantic's Field(gt=0) should block this before it ever reaches rules.py
    with pytest.raises(Exception):
        make_expense(amount=-10.0)


def test_zero_amount_rejected_at_schema_level():
    with pytest.raises(Exception):
        make_expense(amount=0)    