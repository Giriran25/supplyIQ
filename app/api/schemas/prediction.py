from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict


class DelayPredictionRequest(BaseModel):
    supplier_id: int
    product_id: int
    region: str
    lead_time_days: int
    order_value: float
    previous_delay_rate: float
    carrier_reliability: float


class DelayPredictionResponse(BaseModel):
    delay_probability: float = Field(..., ge=0.0, le=1.0)
    predicted_label: str
    model_name: str
    explanation: Dict[str, float]
