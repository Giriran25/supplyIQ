from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional


class AnalyticsRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    region: Optional[str] = None
    supplier_id: Optional[int] = None


class KPIItem(BaseModel):
    name: str
    value: float
    target: Optional[float] = None


class AnalyticsResponse(BaseModel):
    kpis: List[KPIItem]
    metadata: dict[str, str] = {}


class SupplierMetric(BaseModel):
    supplier_id: int
    supplier_name: str
    risk_score: float
    reliability_score: float
    delay_rate: float
    on_time_rate: float


class SupplierAnalyticsResponse(BaseModel):
    suppliers: List[SupplierMetric]
    summary: dict[str, float]


class CategoryAnalyticsItem(BaseModel):
    category_id: int
    category_name: str
    product_count: int
    orders_count: int
    revenue: float
    avg_price: float


class CategoryAnalyticsResponse(BaseModel):
    categories: List[CategoryAnalyticsItem]


class ProductAnalyticsItem(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: float
    avg_unit_price: float


class ProductAnalyticsResponse(BaseModel):
    products: List[ProductAnalyticsItem]


class GeographyAnalyticsItem(BaseModel):
    region: str
    country: str | None = None
    revenue: float
    orders: int
    delay_rate: float


class GeographyAnalyticsResponse(BaseModel):
    geography: List[GeographyAnalyticsItem]


class ShipmentAnalyticsItem(BaseModel):
    shipping_mode: str
    shipments: int
    avg_planned_transit_days: float | None
    avg_actual_transit_days: float | None
    delay_rate: float


class ShipmentAnalyticsResponse(BaseModel):
    summary: dict[str, float]
    by_mode: List[ShipmentAnalyticsItem]
