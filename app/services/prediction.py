from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.schemas.prediction import DelayPredictionRequest, DelayPredictionResponse


class DelayPredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def predict_delay(self, request: DelayPredictionRequest) -> DelayPredictionResponse:
        delay_probability = min(max(request.previous_delay_rate * 0.6 + request.carrier_reliability * 0.2 + request.order_value / 100000, 0.0), 1.0)
        predicted_label = "Delayed" if delay_probability >= 0.5 else "On-time"
        explanation = {
            "previous_delay_rate": request.previous_delay_rate * 0.6,
            "carrier_reliability": request.carrier_reliability * 0.2,
            "order_value": request.order_value / 100000,
        }
        return DelayPredictionResponse(
            delay_probability=delay_probability,
            predicted_label=predicted_label,
            model_name="xgboost-production-stub",
            explanation=explanation,
        )
