from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, case, cast, Float
from sqlalchemy.orm import Session

from app.api.schemas.analytics import (
    AnalyticsRequest,
    AnalyticsResponse,
    KPIItem,
    SupplierAnalyticsResponse,
    SupplierMetric,
    CategoryAnalyticsResponse,
    CategoryAnalyticsItem,
    ProductAnalyticsResponse,
    ProductAnalyticsItem,
    GeographyAnalyticsResponse,
    GeographyAnalyticsItem,
    ShipmentAnalyticsResponse,
    ShipmentAnalyticsItem,
)
from app.models import Category, Product, Order, OrderItem, Shipment


def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


class AnalyticsService:
    """Analytics service providing KPI and dimensional summaries.

    Design goals:
    - Push aggregates into the DB via SQLAlchemy to avoid transferring rows.
    - Keep methods small and composable so endpoints can call only needed pieces.
    - Use date filters and region filters from `AnalyticsRequest`.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_filters(self, request: AnalyticsRequest):
        filters = []
        start = _parse_date(request.start_date)
        end = _parse_date(request.end_date)
        if start:
            filters.append(Order.order_date >= start)
        if end:
            filters.append(Order.order_date <= end)
        if request.region:
            filters.append(Order.region == request.region)
        return filters

    def get_kpis(self, request: AnalyticsRequest) -> AnalyticsResponse:
        filters = self._base_filters(request)

        # Revenue: sum of order_items.line_total for matching orders
        revenue = (
            self.db.query(func.coalesce(func.sum(OrderItem.line_total), 0.0))
            .join(Order, Order.id == OrderItem.order_id)
            .filter(*filters)
            .scalar()
        ) or 0.0

        # Orders: count of distinct orders
        orders = int(self.db.query(func.count(Order.id)).filter(*filters).scalar() or 0)

        # Customers: distinct customers placing orders
        customers = int(
            self.db.query(func.count(func.distinct(Order.customer_id))).filter(*filters).scalar() or 0
        )

        # Products: distinct products sold in range (catalog size could be measured separately)
        products = int(
            self.db.query(func.count(func.distinct(OrderItem.product_id)))
            .join(Order, Order.id == OrderItem.order_id)
            .filter(*filters)
            .scalar()
            or 0
        )

        # Shipment delay rate and avg lead time (from shipments table)
        shipment_filters = []
        start = _parse_date(request.start_date)
        end = _parse_date(request.end_date)
        if start:
            shipment_filters.append(Shipment.shipped_at >= start)
        if end:
            shipment_filters.append(Shipment.shipped_at <= end)

        total_shipments = int(self.db.query(func.count(Shipment.id)).filter(*shipment_filters).scalar() or 0)
        late_shipments = int(
            self.db.query(func.count(Shipment.id)).filter(Shipment.late_delivery_risk == True, *shipment_filters).scalar() or 0
        )
        delay_rate = float(late_shipments) / total_shipments if total_shipments > 0 else 0.0

        avg_lead = (
            self.db.query(func.avg(cast(Shipment.actual_transit_days, Float))).filter(*shipment_filters).scalar()
        )
        avg_lead = float(avg_lead) if avg_lead is not None else 0.0

        kpis = [
            KPIItem(name="Revenue", value=float(revenue)),
            KPIItem(name="Orders", value=float(orders)),
            KPIItem(name="Customers", value=float(customers)),
            KPIItem(name="Products", value=float(products)),
            KPIItem(name="Delay Rate", value=delay_rate),
            KPIItem(name="Average Lead Time", value=avg_lead),
        ]

        return AnalyticsResponse(kpis=kpis, metadata={"computed_at": datetime.utcnow().isoformat()})

    def get_supplier_overview(self) -> SupplierAnalyticsResponse:
        # supplier table not present — return stub until supplier model exists
        suppliers = [
            SupplierMetric(supplier_id=1, supplier_name="Acme Logistics", risk_score=78.5, reliability_score=72.0, delay_rate=0.18, on_time_rate=0.82),
            SupplierMetric(supplier_id=2, supplier_name="Global Parts", risk_score=53.0, reliability_score=80.3, delay_rate=0.10, on_time_rate=0.90),
        ]
        return SupplierAnalyticsResponse(suppliers=suppliers, summary={"top_risk_supplier": 1})

    def get_category_analytics(self, request: AnalyticsRequest, limit: int = 50) -> CategoryAnalyticsResponse:
        filters = self._base_filters(request)

        q = (
            self.db.query(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.count(func.distinct(Product.id)).label("product_count"),
                func.count(func.distinct(Order.id)).label("orders_count"),
                func.coalesce(func.sum(OrderItem.line_total), 0.0).label("revenue"),
                func.coalesce(func.avg(cast(Product.price, Float)), 0.0).label("avg_price"),
            )
            .join(Product, Product.category_id == Category.id)
            .outerjoin(OrderItem, OrderItem.product_id == Product.id)
            .outerjoin(Order, Order.id == OrderItem.order_id)
            .filter(*filters)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .limit(limit)
        )

        rows = q.all()
        categories = [
            CategoryAnalyticsItem(
                category_id=int(r.category_id),
                category_name=r.category_name,
                product_count=int(r.product_count or 0),
                orders_count=int(r.orders_count or 0),
                revenue=float(r.revenue or 0.0),
                avg_price=float(r.avg_price or 0.0),
            )
            for r in rows
        ]

        return CategoryAnalyticsResponse(categories=categories)

    def get_product_analytics(self, request: AnalyticsRequest, limit: int = 100) -> ProductAnalyticsResponse:
        filters = self._base_filters(request)

        q = (
            self.db.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
                func.coalesce(func.sum(OrderItem.line_total), 0.0).label("revenue"),
                func.coalesce(func.avg(cast(OrderItem.unit_price, Float)), 0.0).label("avg_unit_price"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(*filters)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .limit(limit)
        )

        rows = q.all()
        products = [
            ProductAnalyticsItem(
                product_id=int(r.product_id),
                product_name=r.product_name,
                units_sold=int(r.units_sold or 0),
                revenue=float(r.revenue or 0.0),
                avg_unit_price=float(r.avg_unit_price or 0.0),
            )
            for r in rows
        ]

        return ProductAnalyticsResponse(products=products)

    def get_geography_analytics(self, request: AnalyticsRequest) -> GeographyAnalyticsResponse:
        filters = self._base_filters(request)

        q = (
            self.db.query(
                Order.region.label("region"),
                Order.ship_country.label("country"),
                func.coalesce(func.sum(OrderItem.line_total), 0.0).label("revenue"),
                func.count(func.distinct(Order.id)).label("orders"),
                func.sum(case((Shipment.late_delivery_risk == True, 1), else_=0)).label("late_shipments"),
                func.count(Shipment.id).label("total_shipments"),
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .outerjoin(Shipment, Shipment.order_id == Order.id)
            .filter(*filters)
            .group_by(Order.region, Order.ship_country)
            .order_by(func.sum(OrderItem.line_total).desc())
        )

        rows = q.all()
        geography = []
        for r in rows:
            total_shipments = int(r.total_shipments or 0)
            late = int(r.late_shipments or 0)
            delay_rate = float(late) / total_shipments if total_shipments > 0 else 0.0
            geography.append(
                GeographyAnalyticsItem(
                    region=r.region,
                    country=r.country,
                    revenue=float(r.revenue or 0.0),
                    orders=int(r.orders or 0),
                    delay_rate=delay_rate,
                )
            )

        return GeographyAnalyticsResponse(geography=geography)

    def get_shipment_analytics(self, request: AnalyticsRequest) -> ShipmentAnalyticsResponse:
        start = _parse_date(request.start_date)
        end = _parse_date(request.end_date)
        filters = []
        if start:
            filters.append(Shipment.shipped_at >= start)
        if end:
            filters.append(Shipment.shipped_at <= end)

        summary = (
            self.db.query(
                func.count(Shipment.id).label("shipments"),
                func.coalesce(func.avg(cast(Shipment.planned_transit_days, Float)), 0.0).label("avg_planned_transit_days"),
                func.coalesce(func.avg(cast(Shipment.actual_transit_days, Float)), 0.0).label("avg_actual_transit_days"),
                func.sum(case((Shipment.late_delivery_risk == True, 1), else_=0)).label("late_count"),
            )
            .filter(*filters)
            .one()
        )

        total = int(summary.shipments or 0)
        late = int(summary.late_count or 0)
        overall_delay_rate = float(late) / total if total > 0 else 0.0

        by_mode_q = (
            self.db.query(
                Shipment.shipping_mode.label("shipping_mode"),
                func.count(Shipment.id).label("shipments"),
                func.coalesce(func.avg(cast(Shipment.planned_transit_days, Float)), 0.0).label("avg_planned_transit_days"),
                func.coalesce(func.avg(cast(Shipment.actual_transit_days, Float)), 0.0).label("avg_actual_transit_days"),
                func.sum(case((Shipment.late_delivery_risk == True, 1), else_=0)).label("late_count"),
            )
            .filter(*filters)
            .group_by(Shipment.shipping_mode)
            .order_by(func.count(Shipment.id).desc())
        )

        by_mode = []
        for r in by_mode_q.all():
            shipments = int(r.shipments or 0)
            late_count = int(r.late_count or 0)
            delay = float(late_count) / shipments if shipments > 0 else 0.0
            by_mode.append(
                ShipmentAnalyticsItem(
                    shipping_mode=r.shipping_mode,
                    shipments=shipments,
                    avg_planned_transit_days=float(r.avg_planned_transit_days or 0.0),
                    avg_actual_transit_days=float(r.avg_actual_transit_days or 0.0),
                    delay_rate=delay,
                )
            )

        summary_dict = {
            "total_shipments": total,
            "overall_delay_rate": overall_delay_rate,
            "avg_planned_transit_days": float(summary.avg_planned_transit_days or 0.0),
            "avg_actual_transit_days": float(summary.avg_actual_transit_days or 0.0),
        }

        return ShipmentAnalyticsResponse(summary=summary_dict, by_mode=by_mode)
