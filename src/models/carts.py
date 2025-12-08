from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from datetime import datetime
from src.database import Base


class CartOrm(Base):
	__tablename__ = "carts"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)