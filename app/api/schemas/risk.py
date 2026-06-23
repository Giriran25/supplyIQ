from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List


class SupplierRiskResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    reliability_score: float
    risk_score: float
    risk_factors: Dict[str, float]
    recommendations: List[str]
