from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from src.database import Base


class CategoryOrm(Base):
	__tablename__ = "categories"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]  = mapped_column(unique=True)
	slug: Mapped[str]  = mapped_column(unique=True)
	product_type: Mapped[str] = mapped_column(Enum("clothing", "footwear", "accessory", name="product_type"))