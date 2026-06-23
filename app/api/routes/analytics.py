from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas.analytics import (
    AnalyticsRequest,
    AnalyticsResponse,
    CategoryAnalyticsResponse,
    ProductAnalyticsResponse,
    GeographyAnalyticsResponse,
    ShipmentAnalyticsResponse,
    SupplierAnalyticsResponse,
)
from app.core.database import get_db
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get(
    "/kpis",
    response_model=AnalyticsResponse,
    summary="Get KPIs",
    description="Retrieve top-level KPIs: revenue, orders, customers, products, delay rate, avg lead time",
)
async def get_kpis(
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    region: str | None = Query(None, description="Filter by region"),
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    """Get KPI summary for the organization."""
    try:
        request = AnalyticsRequest(start_date=start_date, end_date=end_date, region=region)
        service = AnalyticsService(db)
        return service.get_kpis(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KPI calculation failed: {str(e)}")


@router.get(
    "/categories",
    response_model=CategoryAnalyticsResponse,
    summary="Get Category Analytics",
    description="Revenue and order metrics by category",
)
async def get_category_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    region: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> CategoryAnalyticsResponse:
    """Get analytics breakdown by category."""
    try:
        request = AnalyticsRequest(start_date=start_date, end_date=end_date, region=region)
        service = AnalyticsService(db)
        return service.get_category_analytics(request, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category analytics failed: {str(e)}")


@router.get(
    "/products",
    response_model=ProductAnalyticsResponse,
    summary="Get Product Analytics",
    description="Top products by units sold and revenue",
)
async def get_product_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    region: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> ProductAnalyticsResponse:
    """Get top products ranked by revenue."""
    try:
        request = AnalyticsRequest(start_date=start_date, end_date=end_date, region=region)
        service = AnalyticsService(db)
        return service.get_product_analytics(request, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product analytics failed: {str(e)}")


@router.get(
    "/geography",
    response_model=GeographyAnalyticsResponse,
    summary="Get Geography Analytics",
    description="Revenue and delay metrics by region and country",
)
async def get_geography_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    region: str | None = Query(None),
    db: Session = Depends(get_db),
) -> GeographyAnalyticsResponse:
    """Get analytics breakdown by geography."""
    try:
        request = AnalyticsRequest(start_date=start_date, end_date=end_date, region=region)
        service = AnalyticsService(db)
        return service.get_geography_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geography analytics failed: {str(e)}")


@router.get(
    "/shipments",
    response_model=ShipmentAnalyticsResponse,
    summary="Get Shipment Analytics",
    description="Performance KPIs and breakdown by shipping mode",
)
async def get_shipment_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
) -> ShipmentAnalyticsResponse:
    """Get shipment performance metrics and mode breakdown."""
    try:
        request = AnalyticsRequest(start_date=start_date, end_date=end_date)
        service = AnalyticsService(db)
        return service.get_shipment_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shipment analytics failed: {str(e)}")
