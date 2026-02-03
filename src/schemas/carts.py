from pydantic import BaseModel
from datetime import datetime


class CartsAdd(BaseModel):
    user_id: int
    created_at: datetime
    updated_at: datetime


class Cart(CartsAdd):
    id: int
