from datetime import datetime

from src.api.dependencies import UserIdDep
from src.exceptions.exception import CartNotExistsException, ObjectNotFoundException
from src.schemas.carts import CartsAdd
from src.services.base import BaseService

class CartService(BaseService):
    async def get_my_cart(self, user_id: int):
        existing = await self.db.carts.get_filtered(user_id=user_id)
        if not existing:
            raise CartNotExistsException
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
        cart = await self.get_cart_user_with_check(user_id)
        # Удалить все товары в корзине
        await self.db.cart_items.delete(cart_id=cart.id)
        # Удалить корзину
        await self.db.carts.delete(id=cart.id)
        await self.db.commit()

    async def get_cart_user_with_check(self, user_id: int):
        try:
            return await self.db.carts.get_one(user_id=user_id)
        except ObjectNotFoundException:
            raise CartNotExistsException

    async def get_cart_with_check(self, cart_id: int):
        try:
            return await self.db.carts.get_one(id=cart_id)
        except ObjectNotFoundException:
            raise CartNotExistsException