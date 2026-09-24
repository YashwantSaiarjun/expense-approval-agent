from google import genai
from app.schemas import ExpenseSubmission, LLMDecision
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """
You are a strict enterprise expense policy reviewer.

POLICY RULES:
- Valid categories: travel, meals, office_supplies, software, client_entertainment, other
- Vague descriptions like "miscellaneous", "stuff", "other expenses" are suspicious
- Amounts over $200 require a clear, specific business justification
- Receipt must logically match the described expense
- Personal expenses disguised as business expenses must be rejected

CONFIDENCE SCORING GUIDE:
- 0.90 to 1.0  : Very clear case, obvious decision, no ambiguity
- 0.70 to 0.89 : Mostly clear but has minor ambiguity
- 0.50 to 0.69 : Genuinely unclear, could go either way
- Below 0.50   : Too ambiguous, human should decide

IMPORTANT:
- Return ONLY valid JSON, no extra text, no markdown, no backticks
- Your entire response must be exactly this shape:
{
  "decision": "approve" or "reject",
  "confidence": a float between 0.0 and 1.0,
  "reason": "one sentence explaining your decision"
}
"""

def evaluate_expense_with_llm(expense: ExpenseSubmission) -> LLMDecision:
    user_message = f"""
Evaluate this expense against company policy:

- Employee ID : {expense.employee_id}
- Amount      : ${expense.amount}
- Category    : {expense.category}
- Description : {expense.description}
- Date        : {expense.expense_date}
- Receipt     : {"provided" if expense.receipt_url else "not provided"}

Return your evaluation as JSON only.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_message}"
    )

    raw = response.text.strip()

    # Strip markdown code fences if Gemini adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    return LLMDecision(**parsed)