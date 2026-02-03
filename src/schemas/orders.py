from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrdersAddRequest(BaseModel):
    status: OrderStatus
    shipping_method: str
    payment_method: str


class OrdersAdd(BaseModel):
    user_id: int
    address_id: int
    order_number: str
    status: OrderStatus
    total_amount: float
    shipping_method: str
    payment_method: str
    created_at: datetime
    updated_at: datetime


class Order(OrdersAdd):
    id: int


class OrdersUpdate(BaseModel):
    total_amount: float


class OrderStatusUpdateRequest(BaseModel):
    status: str


class OrderStatusUpdate(BaseModel):
    status: str
    updated_at: datetime


class OrdersPut(BaseModel):
    total_amount: float
    shipping_method: str
    payment_method: str


class OrdersPatch(BaseModel):
    total_amount: float | None = Field(None)
    shipping_method: str | None = Field(None)
    payment_method: str | None = Field(None)
