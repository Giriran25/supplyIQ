from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    market: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ship_city: Mapped[str] = mapped_column(String(100), nullable=False)
    ship_country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    zipcode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sales_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    profit_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    benefit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    sales_per_customer: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    shipments: Mapped[list["Shipment"]] = relationship(
        "Shipment",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
