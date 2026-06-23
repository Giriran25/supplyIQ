from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.risk import SupplierRiskResponse
from app.core.database import get_db
from app.services.risk import SupplierRiskService

router = APIRouter()


@router.get("/supplier/{supplier_id}", response_model=SupplierRiskResponse)
async def get_supplier_risk(supplier_id: int, db: Session = Depends(get_db)) -> SupplierRiskResponse:
    service = SupplierRiskService(db)
    result = service.get_supplier_risk(supplier_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return result
