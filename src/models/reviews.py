from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint, JSON
from typing import Optional
from datetime import datetime
from src.database import Base


class ReviewOrm(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(CheckConstraint("rating BETWEEN 1 AND 5"))
    comment: Mapped[Optional[str]]
    images: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)