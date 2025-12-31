from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.core.permissions import Permission
from src.schemas.cart_items import CartItemsAdd, CartItemsAddRequest, CartItemsUpdate
from src.services.base import BaseService

class CartItemService(BaseService):
    async def get_my_cart_items(self, user_id: int, target_user_id: int = None):
        target = target_user_id if target_user_id else user_id
        if target != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")
        try:
            cart = await self.db.carts.get_one(user_id=target)
        except NoResultFound:
            return []
        return await self.db.cart_items.get_filtered(cart_id=cart.id)

    async def get_cart_item(self, item_id: int, user_id: int):
        # Получаем элемент корзины
        try:
            item = await self.db.cart_items.get_one(id=item_id)
        except NoResultFound:
            raise HTTPException(404, "Элемент корзины не найден")
        # Получаем корзину элемента
        try:
            cart = await self.db.carts.get_one(id=item.cart_id)
        except NoResultFound:
            raise HTTPException(404, "Корзина не найдена")

        if cart.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        return item

    async def add_cart_item(self, product_id: int, user_id: int, data: CartItemsAddRequest):
        cart = await self.db.carts.get_one(user_id=user_id)
        if not cart:
            cart = await self.db.carts.add(user_id)
        try:
            await self.db.products.get_one(id=product_id)
        except NoResultFound:
            raise HTTPException(404, "Товар не найден")

        cart_item_data = CartItemsAdd(
            **data.model_dump(),
            cart_id=cart.id,
            product_id=product_id
        )
        cart_item = await self.db.cart_items.add(cart_item_data)
        await self.db.commit()
        return cart_item

    async def update_cart_item(self, user_id: int, item_id: int, data: CartItemsUpdate, exclude_unset: bool = False):
        # Проверить что элемент принадлежит корзине пользователя
        try:
            item = await self.db.cart_items.get_one(id=item_id)
        except NoResultFound:
            raise HTTPException(404, "Элемент корзины не найден")

        try:
            cart = await self.db.carts.get_one(id=item.cart_id)
        except NoResultFound:
            raise HTTPException(404, "Корзина не найдена")

        if cart.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise HTTPException(403, "Недостаточно прав для редактирования корзины таваров")

        await self.db.cart_items.exit(
            data,
            exclude_unset=exclude_unset,
            id=item_id
        )
        await self.db.commit()

    async def delete_cart_item(self, item_id: int, user_id: int):
        try:
            item = await self.db.cart_items.get_one(id=item_id)
        except NoResultFound:
            raise HTTPException(404, "Элемент корзины не найден")

        try:
            cart = await self.db.carts.get_one(id=item.cart_id)
        except NoResultFound:
            raise HTTPException(404, "Корзина не найдена")

        if cart.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        await self.db.cart_items.delete(id=item_id)
        await self.db.commit()