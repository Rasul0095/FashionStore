from pydantic import BaseModel, Field


class OrderItemsAddRequest(BaseModel):
    product_id: int
    quantity: int


class OrderItemsAdd(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    final_price: float


class OrderItem(OrderItemsAdd):
    id: int


class OrderItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, le=101)
