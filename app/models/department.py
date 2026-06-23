from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_department_id: Mapped[int] = mapped_column(nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="department",
        passive_deletes=True,
    )
