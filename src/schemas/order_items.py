from pydantic import BaseModel

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