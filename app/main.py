from fastapi import FastAPI, HTTPException
from uuid import uuid4
from app.schemas import ExpenseSubmission, ExpenseResponse

app = FastAPI(title="Expense Approval Agent")

@app.post("/expenses", response_model=ExpenseResponse)
def submit_expense(expense: ExpenseSubmission):
    expense_id = str(uuid4())
    # No DB yet — just proving validation + response shape works
    return ExpenseResponse(
        id=expense_id,
        status="submitted",
        message="Expense received and validated"
    )

@app.get("/health")
def health():
    return {"status": "ok"}