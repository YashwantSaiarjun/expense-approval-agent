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