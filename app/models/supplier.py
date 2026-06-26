from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    region = Column(String(50), nullable=False, index=True)
    tier = Column(Integer, nullable=False, default=3)
    lead_time_mean = Column(Float, nullable=False, default=7.0)
    lead_time_std = Column(Float, nullable=False, default=2.0)
    on_time_rate = Column(Float, nullable=False, default=0.9)

    # NOTE: Legacy model — not part of the current DataCo architecture.
    # The shipments relationship is disabled because the current Shipment model
    # has no supplier_id FK. Re-enable if Supplier is integrated into DataCo.
    # shipments = relationship("Shipment", back_populates="supplier")
