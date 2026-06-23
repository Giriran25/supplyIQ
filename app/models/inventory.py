from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from sqlalchemy import func


class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)


class InventorySnapshot(Base, TimestampMixin):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    product = relationship("Product")
    warehouse = relationship("Warehouse")
