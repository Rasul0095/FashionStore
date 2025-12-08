from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint, Enum, JSON, Text
from datetime import datetime
from typing import Optional
from src.database import Base


class ProductOrm(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]  = mapped_column(nullable=False)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    price: Mapped[float] = mapped_column(CheckConstraint("price > 0"), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(CheckConstraint("stock_quantity >= 0"), default=0)

    # Тип товара - ограниченный набор значений
    product_type: Mapped[str] = mapped_column(Enum("clothing", "footwear", "accessory", name="product_type"))

    description: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[Optional[str]] # для одежды и обуви
    color: Mapped[Optional[str]]
    gender: Mapped[Optional[str]]
    material: Mapped[Optional[str]] # для аксессуаров
    sku: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    images: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)