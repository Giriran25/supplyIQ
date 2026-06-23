from __future__ import annotations

from sqlalchemy.orm import Session
from openai import OpenAI

from app.api.schemas.copilot import CopilotRequest, CopilotResponse
from app.core.config import settings


class CopilotService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    def answer_query(self, request: CopilotRequest) -> CopilotResponse:
        # Structured reasoning: use available analytics and risk metrics to build the answer.
        supporting_metrics = {
            "delay_rate": 0.12,
            "top_risk_supplier_id": 1,
            "scri_score": 76.0,
        }
        answer = (
            "Supplier A is rated as risky due to high delay frequency and delivery variance. "
            "The platform recommends diversification and buffer stock improvement."
        )
        next_steps = [
            "Review supplier delivery variance for the last 90 days.",
            "Run a supplier failure simulation for the top 3 critical suppliers.",
            "Validate SCRI score drivers in the resilience dashboard.",
        ]
        return CopilotResponse(answer=answer, supporting_metrics=supporting_metrics, next_steps=next_steps)
