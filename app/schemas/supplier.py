from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupplierSchema(BaseModel):
    id: int
    name: str
    region: str
    tier: int
    lead_time_mean: float
    on_time_rate: float
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}
