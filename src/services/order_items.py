from datetime import datetime

from src.core.permissions import Permission
from src.exceptions.exception import PermissionDeniedHTTPException, ObjectNotFoundException, OrderItemNotFoundException, \
    OrderCannotModifiedHTTPException, NotAllProductsAvailableHTTPException, ProductAlreadyInOrderHTTPException, \
    NotEnoughProductHTTPException, OrderCannotDeletedHTTPException
from src.schemas.order_items import OrderItemsAdd, OrderItemsAddRequest, OrderItemUpdate
from src.schemas.orders import OrdersUpdate
from src.schemas.products import ProductUpdate
from src.services.auth import AuthService
from src.services.base import BaseService
from src.services.orders import OrderService
from src.services.products import ProductService


class OrderItemService(BaseService):
    async def get_my_order_items(self, user_id: int, target_user_id: int = None):
        target = target_user_id or user_id
        if target != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        orders = await self.db.orders.get_filtered(user_id=target)
        order_ids = [order.id for order in orders]
        return await self.db.order_items.get_by_order_ids(order_ids)

    async def get_order_item(self, item_id: int, user_id: int):
        item = await self.get_order_item_with_check(item_id)
        # Получаем заказ этого элемента
        order = await OrderService(self.db).get_order_with_check(item.order_id)
        # Проверяем права: либо владелец заказа, либо админ
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        return item

    async def add_items_to_order(self, order_id: int, items: list[OrderItemsAddRequest], user_id: int):
        """Добавить товары в существующий заказ"""
        order = await OrderService(self.db).get_order_with_check(order_id)

        if order.status != "pending":
            raise OrderCannotModifiedHTTPException(order.status)

        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        added_items = []
        for item in items:
            product = await ProductService(self.db).get_product_with_check(item.product_id)

            # 1. Проверить наличие
            if product.stock_quantity < item.quantity:
                raise NotAllProductsAvailableHTTPException

            # 2. Проверить, не добавлен ли уже этот товар в заказ
            existing = await self.db.order_items.get_one_or_none(
                order_id=order_id,
                product_id=item.product_id
            )
            if existing is not None:
                raise ProductAlreadyInOrderHTTPException(product.name)

            # 3. Обновить остатки
            update_data = ProductUpdate(
                stock_quantity=product.stock_quantity - item.quantity,
                updated_at=datetime.utcnow()
            )
            await self.db.products.exit(update_data, id=product.id, exclude_unset=True)

            # 4. Добавить в order_items
            order_item = OrderItemsAdd(
                order_id=order_id,
                product_id=product.id,
                quantity=item.quantity,
                final_price=product.price
            )
            await self.db.order_items.add(order_item)
            added_items.append(order_item)

        # 5. Обновить сумму заказа
        total = sum(item.final_price * item.quantity for item in added_items)
        await self.db.orders.exit(
            OrdersUpdate(
                total_amount=order.total_amount + total,
            ),
            id=order_id,
            exclude_unset=True
        )
        await self.db.commit()
        return {
            "message": f"Добавлено {len(added_items)} товаров",
            "total_added": total,
            "new_total": order.total_amount + total,
            "order_id": order_id
        }

    async def update_order_item(
            self, item_id: int, user_id: int, data: OrderItemUpdate,
            exclude_unset: bool = False
    ):
        item = await self.get_order_item_with_check(item_id)
        order = await OrderService(self.db).get_order_with_check(item.order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        if order.status != "pending":
            raise OrderCannotModifiedHTTPException

        product = await ProductService(self.db).get_product_with_check(item.product_id)
        if data.quantity > product.stock_quantity + item.quantity:
            quantity = product.stock_quantity + item.quantity
            raise NotEnoughProductHTTPException(product.name, quantity)

        # Обновить item
        await self.db.order_items.exit(data, id=item_id, exclude_unset=exclude_unset)

        # Обновить остатки
        stock_change = item.quantity - data.quantity
        if stock_change != 0:
            update_data = ProductUpdate(
                stock_quantity=product.stock_quantity + stock_change,
                updated_at=datetime.utcnow()
            )
            await self.db.products.exit(update_data, id=product.id, exclude_unset=True)

        # Пересчитать сумму
        await self.recalculate_order_total(order.id)
        await self.db.commit()

        updated_item = await self.get_order_item_with_check(item_id)
        return updated_item

    async def delete_order_item(self, item_id: int, user_id: int):
        item = await self.get_order_item_with_check(item_id)
        order = await OrderService(self.db).get_order_with_check(item.order_id)

        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        if order.status not in ["pending", "cancelled"]:
            raise OrderCannotDeletedHTTPException(order.status)

        product = await ProductService(self.db).get_product_with_check(item.product_id)
        update_data = ProductUpdate(
            stock_quantity=product.stock_quantity + item.quantity,
            updated_at=datetime.utcnow()
        )
        await self.db.products.exit(update_data, id=product.id, exclude_unset=True)
        await self.db.order_items.delete(id=item_id)
        await self.recalculate_order_total(order.id)
        await self.db.commit()
        return {"message": "Товар удален из заказа", "item_id": item_id}

    async def recalculate_order_total(self, order_id: int):
        """Пересчитать общую сумму заказа"""
        # Получить все items заказа
        items = await self.db.order_items.get_filtered(order_id=order_id)

        # Посчитать сумму
        total = sum(item.final_price * item.quantity for item in items)

        # Обновить заказ
        update_data = OrdersUpdate(total_amount=total)
        await self.db.orders.exit(update_data, id=order_id, exclude_unset=True)

    async def get_order_item_with_check(self, item_id: int):
        try:
            return await self.db.order_items.get_one(id=item_id)
        except ObjectNotFoundException:
            raise OrderItemNotFoundException
