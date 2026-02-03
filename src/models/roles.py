from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON
from typing import Optional
from src.database import Base


class RoleOrm(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
