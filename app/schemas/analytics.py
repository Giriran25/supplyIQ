from pydantic import BaseModel
from typing import Optional


class KPISchema(BaseModel):
    total_orders: int
    total_shipments: int
    avg_lead_time: Optional[float]
    delay_rate: Optional[float]
    total_inventory_items: int
