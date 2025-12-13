from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.database import Base


class AddressOrm(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address_line: Mapped[str]
    city: Mapped[str]
    postal_code: Mapped[str]
    country: Mapped[str]