from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint, Enum
from datetime import datetime
from src.database import Base


class OrderOrm(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    status: Mapped[str] = mapped_column(
        Enum(
            "pending", "paid", "shipped", "delivered", "cancelled", name="order_status"
        ),
        default="pending",
    )

    total_amount: Mapped[float] = mapped_column(CheckConstraint("total_amount >= 0"))
    shipping_method: Mapped[str]
    payment_method: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
