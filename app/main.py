from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from app.schemas import ExpenseSubmission, ExpenseResponse
from app.rules import evaluate_deterministic_rules, RuleOutcome
from app.db import get_db, engine
from app.models import Base, Expense, AuditLog, ExpenseStatus
from app.llm import evaluate_expense_with_llm
from fastapi import FastAPI, Depends, HTTPException
from app.schemas import ExpenseSubmission, ExpenseResponse, ReviewAction, ExpenseDetail
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PolicyPilot — Expense Approval Agent")

CONFIDENCE_THRESHOLD = 0.90

@app.post("/expenses", response_model=ExpenseResponse)
def submit_expense(expense: ExpenseSubmission, db: Session = Depends(get_db)):
    expense_id = str(uuid4())
    rule_result = evaluate_deterministic_rules(expense)

    status_map = {
        RuleOutcome.AUTO_APPROVED: ExpenseStatus.AUTO_APPROVED,
        RuleOutcome.AUTO_REJECTED: ExpenseStatus.AUTO_REJECTED,
        RuleOutcome.NEEDS_AI_REVIEW: ExpenseStatus.AI_REVIEW,
    }
    final_status = status_map[rule_result.outcome]
    llm_decision = None
    llm_confidence = None
    llm_reason = None

    if rule_result.outcome == RuleOutcome.NEEDS_AI_REVIEW:
        llm_result = evaluate_expense_with_llm(expense)
        llm_decision = llm_result.decision
        llm_confidence = llm_result.confidence
        llm_reason = llm_result.reason

        if llm_confidence >= CONFIDENCE_THRESHOLD:
            final_status = (
                ExpenseStatus.CONFIDENT_APPROVED
                if llm_result.decision == "approve"
                else ExpenseStatus.CONFIDENT_REJECTED
            )
        else:
            final_status = ExpenseStatus.PENDING_HUMAN_REVIEW

    db_expense = Expense(
        id=expense_id,
        employee_id=expense.employee_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        expense_date=str(expense.expense_date),
        receipt_url=expense.receipt_url,
        status=final_status,
        llm_decision=llm_decision,
        llm_confidence=llm_confidence,
        llm_reason=llm_reason,
    )
    db.add(db_expense)

    audit = AuditLog(
        id=str(uuid4()),
        expense_id=expense_id,
        from_status=None,
        to_status=final_status.value,
        actor="system:rules_engine" if rule_result.outcome != RuleOutcome.NEEDS_AI_REVIEW else "system:llm",
        reason=llm_reason or rule_result.reason,
    )
    db.add(audit)
    db.commit()

    return ExpenseResponse(
        id=expense_id,
        status=final_status.value,
        message=llm_reason or rule_result.reason
    )

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/review/pending", response_model=List[ExpenseDetail])
def get_pending_reviews(db: Session = Depends(get_db)):
    pending = db.query(Expense).filter(
        Expense.status == ExpenseStatus.PENDING_HUMAN_REVIEW
    ).all()
    return pending


@app.post("/review/{expense_id}/approve", response_model=ExpenseResponse)
def approve_expense(expense_id: str, action: ReviewAction, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != ExpenseStatus.PENDING_HUMAN_REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Expense is not pending review, current status: {expense.status}"
        )

    old_status = expense.status.value
    expense.status = ExpenseStatus.HUMAN_APPROVED

    audit = AuditLog(
        id=str(uuid4()),
        expense_id=expense_id,
        from_status=old_status,
        to_status=ExpenseStatus.HUMAN_APPROVED.value,
        actor=f"manager:{action.manager_id}",
        reason=action.note or "Approved by manager",
    )
    db.add(audit)
    db.commit()

    return ExpenseResponse(
        id=expense_id,
        status=ExpenseStatus.HUMAN_APPROVED.value,
        message=f"Expense approved by manager {action.manager_id}"
    )


@app.post("/review/{expense_id}/reject", response_model=ExpenseResponse)
def reject_expense(expense_id: str, action: ReviewAction, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != ExpenseStatus.PENDING_HUMAN_REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Expense is not pending review, current status: {expense.status}"
        )

    old_status = expense.status.value
    expense.status = ExpenseStatus.HUMAN_REJECTED

    audit = AuditLog(
        id=str(uuid4()),
        expense_id=expense_id,
        from_status=old_status,
        to_status=ExpenseStatus.HUMAN_REJECTED.value,
        actor=f"manager:{action.manager_id}",
        reason=action.note or "Rejected by manager",
    )
    db.add(audit)
    db.commit()

    return ExpenseResponse(
        id=expense_id,
        status=ExpenseStatus.HUMAN_REJECTED.value,
        message=f"Expense rejected by manager {action.manager_id}"
    )