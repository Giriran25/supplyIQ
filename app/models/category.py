from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_category_id: Mapped[int] = mapped_column(nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        passive_deletes=True,
    )
