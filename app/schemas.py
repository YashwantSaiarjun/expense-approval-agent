from pydantic import BaseModel, Field, field_validator
from datetime import date

class ExpenseSubmission(BaseModel):
    employee_id: str = Field(min_length=1)
    amount: float = Field(gt=0, description="Must be a positive number")
    category: str = Field(min_length=1)
    description: str = Field(min_length=5, max_length=500)
    expense_date: date
    receipt_url: str | None = None

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        allowed = {"travel", "meals", "office_supplies", "software", "client_entertainment", "other"}
        if v.lower() not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v.lower()


class ExpenseResponse(BaseModel):
    id: str
    status: str
    message: str

class LLMDecision(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=10, max_length=500)

class ReviewAction(BaseModel):
    manager_id: str = Field(min_length=1)
    note: str | None = None

class ExpenseDetail(BaseModel):
    id: str
    employee_id: str
    amount: float
    category: str
    description: str
    status: str
    llm_decision: str | None
    llm_confidence: float | None
    llm_reason: str | None

    class Config:
        from_attributes = True    