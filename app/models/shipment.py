from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    shipped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    planned_transit_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    actual_transit_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    late_delivery_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    shipping_mode: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    order: Mapped["Order"] = relationship("Order", back_populates="shipments")
