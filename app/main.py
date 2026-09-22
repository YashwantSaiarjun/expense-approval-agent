from fastapi import FastAPI, HTTPException
from uuid import uuid4
from app.schemas import ExpenseSubmission, ExpenseResponse

app = FastAPI(title="Expense Approval Agent")

from app.rules import evaluate_deterministic_rules

from app.rules import evaluate_deterministic_rules

@app.post("/expenses", response_model=ExpenseResponse)
def submit_expense(expense: ExpenseSubmission):
    expense_id = str(uuid4())
    rule_result = evaluate_deterministic_rules(expense)
    return ExpenseResponse(
        id=expense_id,
        status=rule_result.outcome.value,
        message=rule_result.reason
    )

@app.get("/health")
def health():
    return {"status": "ok"}