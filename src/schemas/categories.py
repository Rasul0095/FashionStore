from pydantic import BaseModel
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
