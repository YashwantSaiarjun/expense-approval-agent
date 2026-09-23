from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from app.schemas import ExpenseSubmission, ExpenseResponse
from app.rules import evaluate_deterministic_rules, RuleOutcome
from app.db import get_db, engine
from app.models import Base, Expense, AuditLog, ExpenseStatus

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PolicyPilot — Expense Approval Agent")

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

    db_expense = Expense(
        id=expense_id,
        employee_id=expense.employee_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        expense_date=str(expense.expense_date),
        receipt_url=expense.receipt_url,
        status=final_status,
    )
    db.add(db_expense)

    audit = AuditLog(
        id=str(uuid4()),
        expense_id=expense_id,
        from_status=None,
        to_status=final_status.value,
        actor="system:rules_engine",
        reason=rule_result.reason,
    )
    db.add(audit)
    db.commit()

    return ExpenseResponse(
        id=expense_id,
        status=final_status.value,
        message=rule_result.reason
    )

@app.get("/health")
def health():
    return {"status": "ok"}