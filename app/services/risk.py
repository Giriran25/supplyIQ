from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.schemas.risk import SupplierRiskResponse


class SupplierRiskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_supplier_risk(self, supplier_id: int) -> SupplierRiskResponse | None:
        return SupplierRiskResponse(
            supplier_id=supplier_id,
            supplier_name="Acme Logistics",
            reliability_score=72.0,
            risk_score=78.5,
            risk_factors={
                "delay_frequency": 0.18,
                "delivery_variance": 12.4,
                "historical_performance": 0.72,
            },
            recommendations=[
                "Diversify orders across two additional regional suppliers",
                "Increase buffer stock for high-risk product categories",
            ],
        )
