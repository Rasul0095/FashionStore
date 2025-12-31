from pydantic import BaseModel, Field

class CartItemsAddRequest(BaseModel):
    quantity: int = Field(default=1, ge=1)
    selected_size: str | None = None

class CartItemsAdd(BaseModel):
    cart_id: int
    product_id: int
    quantity: int
    selected_size: str | None = None

class CartItem(CartItemsAdd):
    id: int

class CartItemsUpdate(BaseModel):
    quantity: int | None = Field(default=1, ge=1)
    selected_size: str | None = None