from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.core.permissions import Permission
from src.schemas.order_items import OrderItemsAdd, OrderItemsAddRequest
from src.schemas.orders import OrdersUpdate
from src.services.base import BaseService

class OrderItemService(BaseService):
    async def get_my_order_items(self, user_id: int, target_user_id: int = None):
        target = target_user_id or user_id
        if target != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        orders = await self.db.orders.get_filtered(user_id=target)
        if not orders:
            return []

        order_ids = [order.id for order in orders]
        return await self.db.order_items.get_by_order_ids(order_ids)

    async def get_order_item(self, item_id: int, user_id: int):
        try:
            item = await self.db.order_items.get_one(id=item_id)
        except NoResultFound:
            raise HTTPException(404, "Элемент заказа не найден")

        # Получаем заказ этого элемента
        try:
            order = await self.db.orders.get_one(id=item.order_id)
        except NoResultFound:
            raise HTTPException(404, "Заказ не найден")

        # Проверяем права: либо владелец заказа, либо админ
        if order.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        return item

    async def add_items_to_order(self, order_id: int, items: list[OrderItemsAddRequest], user_id: int):
        """Добавить товары в существующий заказ"""
        try:
            order = await self.db.orders.get_one(id=order_id)
        except NoResultFound:
            raise HTTPException(404, "Заказ не найден")

        # 1. Проверить статус заказа
        if order.status != "pending":
            raise HTTPException(400, f"Заказ в статусе {order.status} нельзя изменять")

        # 2. Проверить права
        if order.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        # 3. Добавить каждый товар
        added_items = []
        for item in items:
            product = await self.db.products.get_one(id=item.product_id)

            if product.stock_quantity < item.quantity:
                raise HTTPException(400, f"Недостаточно {product.name}")

            order_item = OrderItemsAdd(
                order_id=order_id,
                product_id=product.id,
                quantity=item.quantity,
                final_price=product.price,
            )
            await self.db.order_items.add(order_item)
            added_items.append(order_item)

        # 4. Обновить сумму заказа
        total = sum(item.final_price * item.quantity for item in added_items)
        await self.db.orders.exit(
            OrdersUpdate(total_amount=order.total_amount + total),
            id=order_id,
            exclude_unset=True
        )
        await self.db.commit()
        return {
            "message": f"Добавлено {len(added_items)} товаров",
            "total_added": total,
            "new_total": order.total_amount + total
        }