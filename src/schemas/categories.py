from pydantic import BaseModel, Field
from enum import Enum


class ProductType(str, Enum):
    CLOTHING = "clothing"
    FOOTWEAR = "footwear"
    ACCESSORY = "accessory"


class CategoriesAdd(BaseModel):
    name: str
    slug: str
    product_type: ProductType


class Category(CategoriesAdd):
    id: int


class CategoriesPatch(BaseModel):
    name: str | None = Field(None)
    slug: str | None = Field(None)
    product_type: ProductType | None = Field(None)
