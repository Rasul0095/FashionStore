from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from src.database import Base


class BrandOrm(Base):
	__tablename__ = "brands"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(unique=True)
	description: Mapped[Optional[str]]