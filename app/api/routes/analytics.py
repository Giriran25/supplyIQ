from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analytics import KPISchema
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.inventory import InventorySnapshot
from sqlalchemy import func

router = APIRouter()


@router.get("/kpis", response_model=KPISchema)
def get_kpis(db: Session = Depends(get_db)):
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_shipments = db.query(func.count(Shipment.id)).scalar() or 0
    avg_lead_time = db.query(func.avg(Shipment.lead_time_days)).scalar()
    delayed = db.query(func.count(Shipment.id)).filter(Shipment.delayed == True).scalar() or 0
    delay_rate = None
    if total_shipments:
        delay_rate = delayed / total_shipments
    total_inventory = db.query(func.coalesce(func.sum(InventorySnapshot.quantity), 0)).scalar() or 0

    return KPISchema(
        total_orders=int(total_orders),
        total_shipments=int(total_shipments),
        avg_lead_time=float(avg_lead_time) if avg_lead_time is not None else None,
        delay_rate=float(delay_rate) if delay_rate is not None else None,
        total_inventory_items=int(total_inventory),
    )
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.analytics import AnalyticsRequest, AnalyticsResponse, SupplierAnalyticsResponse
from app.core.database import get_db
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.post("/kpis", response_model=AnalyticsResponse)
async def get_kpis(request: AnalyticsRequest, db: Session = Depends(get_db)) -> AnalyticsResponse:
    service = AnalyticsService(db)
    return service.get_kpis(request)


@router.get("/suppliers", response_model=SupplierAnalyticsResponse)
async def get_supplier_analytics(db: Session = Depends(get_db)) -> SupplierAnalyticsResponse:
    service = AnalyticsService(db)
    return service.get_supplier_overview()
