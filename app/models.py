from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Text
from datetime import datetime, timezone
from app.db import Base
import enum

class ExpenseStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"
    AI_REVIEW = "ai_review"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"
    CONFIDENT_APPROVED = "confident_approved"
    CONFIDENT_REJECTED = "confident_rejected"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True)
    employee_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    expense_date = Column(String, nullable=False)
    receipt_url = Column(String, nullable=True)
    status = Column(SAEnum(ExpenseStatus), default=ExpenseStatus.SUBMITTED)
    llm_decision = Column(String, nullable=True)
    llm_confidence = Column(Float, nullable=True)
    llm_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)
    expense_id = Column(String, nullable=False)
    from_status = Column(String, nullable=True)
    to_status = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))