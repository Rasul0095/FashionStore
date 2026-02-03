from src.core.permissions import Permission
from src.exceptions.exception import (
    PermissionDeniedHTTPException,
    ObjectNotFoundException,
    CartItemNotFoundException,
    NotAllProductsAvailableHTTPException,
)
from src.repositories.utils import check_product_availability_and_calculate_simple
from src.schemas.cart_items import CartItemsAdd, CartItemsAddRequest, CartItemsUpdate
from src.services.auth import AuthService
from src.services.base import BaseService
from src.services.carts import CartService
from src.services.products import ProductService


class CartItemService(BaseService):
    async def get_my_cart_items(self, user_id: int, target_user_id: int = None):
        target = target_user_id if target_user_id else user_id
        if target != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        cart = await CartService(self.db).get_cart_user_with_check(target)
        return await self.db.cart_items.get_filtered(cart_id=cart.id)

    async def get_cart_item(self, item_id: int, user_id: int):
        # Получаем элемент корзины
        item = await self.get_cart_item_with_check(item_id)
        # Получаем корзину элемента
        cart = await CartService(self.db).get_cart_with_check(item.cart_id)

        if cart.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        return item

    async def add_cart_item(
        self, product_id: int, user_id: int, data: CartItemsAddRequest
    ):
        cart = await self.db.carts.get_one_or_none(user_id=user_id)
        if not cart:
            cart = await CartService(self.db).add_cart(user_id)

        # 1. Сначала добавляем
        await ProductService(self.db).get_product_with_check(product_id)
        cart_item_data = CartItemsAdd(
            **data.model_dump(), cart_id=cart.id, product_id=product_id
        )
        cart_item = await self.db.cart_items.add(cart_item_data)

        # 2. Потом проверяем всю корзину
        query = check_product_availability_and_calculate_simple(user_id)
        result = await self.db.session.execute(query)
        summary = result.first()

        # 3. Если что-то недоступно - откатываем добавление
        if summary.available_items < summary.total_items:
            await self.db.rollback()
            raise NotAllProductsAvailableHTTPException()

        await self.db.commit()
        return cart_item

    async def update_cart_item(
        self,
        user_id: int,
        item_id: int,
        data: CartItemsUpdate,
        exclude_unset: bool = False,
    ):
        # Проверить что элемент принадлежит корзине пользователя
        item = await self.get_cart_item_with_check(item_id)
        cart = await CartService(self.db).get_cart_with_check(item.cart_id)

        if cart.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        await self.db.cart_items.exit(data, exclude_unset=exclude_unset, id=item_id)
        await self.db.commit()

    async def delete_cart_item(self, item_id: int, user_id: int):
        item = await self.get_cart_item_with_check(item_id)
        cart = await CartService(self.db).get_cart_with_check(item.cart_id)

        if cart.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        await self.db.cart_items.delete(id=item_id)
        await self.db.commit()

    async def get_cart_item_with_check(self, item_id: int):
        try:
            return await self.db.cart_items.get_one(id=item_id)
        except ObjectNotFoundException:
            raise CartItemNotFoundException
