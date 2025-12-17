from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ProductType(str, Enum):
    CLOTHING = "clothing"
    FOOTWEAR = "footwear"
    ACCESSORY = "accessory"

class ProductsAddRequest(BaseModel):
    name: str
    price: float
    stock_quantity: int
    product_type: ProductType
    description: str
    size: str | None = Field(None)
    color: str | None = Field(None)
    gender: str | None = Field(None)
    material: str | None = Field(None)
    is_active: bool = Field(default=True)
    images: list = []

class ProductsAdd(BaseModel):
    name: str
    brand_id: int
    category_id: int
    price: float
    stock_quantity: int
    product_type: ProductType
    description: str
    size: str | None = Field(None)
    color: str | None = Field(None)
    gender: str | None = Field(None)
    material: str | None = Field(None)
    sku: str
    is_active: bool = Field(default=True)
    images: list = []
    created_at: datetime
    updated_at: datetime

class Product(ProductsAdd):
    id: int

class ProductImagesUpdate(BaseModel):
    images: list[str]