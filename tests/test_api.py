import pytest
from unittest.mock import patch
from app.schemas import LLMDecision

MOCK_LLM_APPROVE = LLMDecision(
    decision="approve",
    confidence=0.95,
    reason="Clear business travel with receipt provided."
)

MOCK_LLM_LOW_CONFIDENCE = LLMDecision(
    decision="approve",
    confidence=0.55,
    reason="Description too vague to determine business purpose."
)

MOCK_LLM_REJECT = LLMDecision(
    decision="reject",
    confidence=0.96,
    reason="Personal shopping items violate expense policy."
)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auto_approved_small_amount(client):
    response = client.post("/expenses", json={
        "employee_id": "emp_1",
        "amount": 20.0,
        "category": "meals",
        "description": "Team lunch outing",
        "expense_date": "2026-10-18"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "auto_approved"


def test_auto_rejected_missing_receipt(client):
    response = client.post("/expenses", json={
        "employee_id": "emp_1",
        "amount": 200.0,
        "category": "travel",
        "description": "Client site visit",
        "expense_date": "2026-10-18"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "auto_rejected"


def test_llm_confident_approve(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_APPROVE):
        response = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 180.0,
            "category": "travel",
            "description": "Uber to client office for onsite visit",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    assert response.status_code == 200
    assert response.json()["status"] == "confident_approved"


def test_llm_low_confidence_routes_to_human(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_LOW_CONFIDENCE):
        response = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 520.0,
            "category": "client_entertainment",
            "description": "Team gathering expenses",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    assert response.status_code == 200
    assert response.json()["status"] == "pending_human_review"


def test_llm_confident_reject(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_REJECT):
        response = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 300.0,
            "category": "other",
            "description": "Personal shopping items for home",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    assert response.status_code == 200
    assert response.json()["status"] == "confident_rejected"


def test_get_expense_not_found(client):
    response = client.get("/expenses/nonexistent-id")
    assert response.status_code == 404


def test_get_expense_by_id(client):
    create = client.post("/expenses", json={
        "employee_id": "emp_1",
        "amount": 20.0,
        "category": "meals",
        "description": "Team lunch outing",
        "expense_date": "2026-10-18"
    })
    expense_id = create.json()["id"]
    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["id"] == expense_id


def test_get_audit_trail(client):
    create = client.post("/expenses", json={
        "employee_id": "emp_1",
        "amount": 20.0,
        "category": "meals",
        "description": "Team lunch outing",
        "expense_date": "2026-10-18"
    })
    expense_id = create.json()["id"]
    response = client.get(f"/expenses/{expense_id}/audit")
    assert response.status_code == 200
    assert response.json()["expense_id"] == expense_id
    assert len(response.json()["history"]) >= 1


def test_human_approve(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_LOW_CONFIDENCE):
        create = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 520.0,
            "category": "client_entertainment",
            "description": "Team gathering expenses",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    expense_id = create.json()["id"]

    response = client.post(f"/review/{expense_id}/approve", json={
        "manager_id": "manager_john",
        "note": "Verified with employee"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "human_approved"


def test_human_reject(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_LOW_CONFIDENCE):
        create = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 520.0,
            "category": "client_entertainment",
            "description": "Team gathering expenses",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    expense_id = create.json()["id"]

    response = client.post(f"/review/{expense_id}/reject", json={
        "manager_id": "manager_john",
        "note": "Cannot verify business purpose"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "human_rejected"


def test_approve_already_approved_expense(client):
    with patch("app.main.evaluate_expense_with_llm", return_value=MOCK_LLM_LOW_CONFIDENCE):
        create = client.post("/expenses", json={
            "employee_id": "emp_1",
            "amount": 520.0,
            "category": "client_entertainment",
            "description": "Team gathering expenses",
            "expense_date": "2026-10-18",
            "receipt_url": "http://example.com/receipt.pdf"
        })
    expense_id = create.json()["id"]

    client.post(f"/review/{expense_id}/approve", json={
        "manager_id": "manager_john"
    })

    # Try to approve again — should fail with 400
    response = client.post(f"/review/{expense_id}/approve", json={
        "manager_id": "manager_john"
    })
    assert response.status_code == 400