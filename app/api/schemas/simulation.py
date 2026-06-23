from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class SimulationRequest(BaseModel):
    scenario_type: str
    supplier_id: Optional[int] = None
    product_id: Optional[int] = None
    region: Optional[str] = None
    impact_horizon_days: int = 30


class SimulationResponse(BaseModel):
    scenario_name: str
    revenue_impact: float
    inventory_impact: float
    delay_impact: float
    service_impact: float
    summary: str
