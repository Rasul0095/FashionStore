from fastapi import HTTPException
from datetime import datetime

from src.api.dependencies import UserIdDep
from src.schemas.carts import CartsAdd, Cart
from src.services.base import BaseService

class CartService(BaseService):

    async def get_my_cart(self, user_id: int):
        existing = await self.db.carts.get_filtered(user_id=user_id)
        if not existing:
            raise HTTPException(400, "Корзины не существует")

        return await self.db.carts.get_filtered(user_id=user_id)

    async def add_cart(self, user_id: UserIdDep):
        cart_data = CartsAdd(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        cart = await self.db.carts.add(cart_data)
        await self.db.commit()
        return cart

    async def delete_my_cart(self, user_id: int):
        await self.db.carts.delete(user_id=user_id)
        await self.db.commit()