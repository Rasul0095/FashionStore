from fastapi import HTTPException
from datetime import datetime
import logging
from sqlalchemy.exc import NoResultFound

from src.core.permissions import Permission
from src.repositories.utils import generate_order_number, check_product_availability_and_calculate_simple
from src.schemas.orders import OrdersAddRequest, OrdersAdd, OrderStatusUpdateRequest, OrderStatusUpdate
from src.schemas.products import ProductUpdate
from src.services.base import BaseService
from src.api.dependencies import UserIdDep
from src.tasks.tasks import send_order_status_notification_task


class OrderService(BaseService):
    async def get_my_orders(self, user_id: int, target_user_id: int = None):
        target = target_user_id if target_user_id else user_id
        if target != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        return await self.db.orders.get_filtered(user_id=target)

    async def get_order(self, order_id: int, user_id: int):
        try:
            order = await self.db.orders.get_one(id=order_id)
        except NoResultFound:
            raise HTTPException(404, "Заказ не найден")
        if order.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")
        return order

    async def add_order(self, user_id: UserIdDep, address_id: int, data: OrdersAddRequest):
        try:
            cart = await self.db.carts.get_one(user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Корзина не найдена")

        # 1. Проверка наличия товаров
        query = check_product_availability_and_calculate_simple(user_id)
        result = await self.db.session.execute(query)
        summary = result.first()

        if not summary or summary.total_items == 0:
            raise HTTPException(400, "Корзина пуста")

        if summary.available_items < summary.total_items:
            raise HTTPException(400, "Не все товары доступны в нужном количестве")

        # 2. Проверка адреса
        try:
            await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или не принадлежит вам")

        # 3. Создание заказа (используем total_amount из проверки)
        order_number = generate_order_number(user_id)
        order_data = OrdersAdd(
            **data.model_dump(),
            user_id=user_id,
            address_id=address_id,
            order_number=order_number,
            total_amount=summary.total_amount,  # Используем расчетную сумму
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        order = await self.db.orders.add(order_data)

        # 4. Обновление остатков
        updated = await self.update_product_stock(user_id)
        if updated != summary.available_items:
            await self.db.rollback()
            raise HTTPException(500, "Ошибка при обновлении остатков")

        # 5. Очистка корзины
        await self.db.cart_items.delete(cart_id=cart.id)

        await self.db.commit()
        return order

    async def update_product_stock(self, user_id: int):
        # 1. Получаем корзину
        cart = await self.db.carts.get_one_or_none(user_id=user_id)
        if not cart:
            return 0
        # 2. Получаем товары корзины
        cart_items = await self.db.cart_items.get_filtered(cart_id=cart.id)
        updated_count = 0
        for item in cart_items:
            # 3. Получаем текущий товар
            product = await self.db.products.get_one_or_none(id=item.product_id)
            if not product:
                continue
            # 4. Проверяем наличие
            if product.stock_quantity < item.quantity:
                continue
            # 5. Обновляем остаток
            update_data = ProductUpdate(
                stock_quantity=product.stock_quantity - item.quantity,
                updated_at=datetime.utcnow()
            )
            await self.db.products.exit(
                update_data,
                id=item.product_id,
                exclude_unset=True
            )
            updated_count += 1
        return updated_count

    async def change_order_status(self, order_id: int, status_data: OrderStatusUpdateRequest, user_id: int):
        try:
            order = await self.db.orders.get_one(id=order_id)
        except NoResultFound:
            raise HTTPException(404, "Заказ не найден")

        if order.user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав")

        valid_statuses = ["pending", "paid", "processing", "shipped", "delivered", "cancelled"]
        if status_data.status not in valid_statuses:
            raise HTTPException(400, f"Недопустимый статус. Допустимо: {', '.join(valid_statuses)}")

        # Сохраняем старый статус ДО изменения
        old_status = order.status

        # Проверяем логику по СТАРОМУ статусу
        if old_status == "cancelled":
            raise HTTPException(400, "Отмененный заказ можно только вернуть")
        if old_status == "delivered":
            raise HTTPException(400, "Доставленный заказ можно только вернуть")

        # Обновляем статус
        update_data = OrderStatusUpdate(
            status=status_data.status,
            updated_at=datetime.utcnow(),
        )
        await self.db.orders.exit(update_data, id=order_id, exclude_unset=True)

        # Получаем ОБНОВЛЕННЫЙ заказ для уведомления
        updated_order = await self.db.orders.get_one(id=order_id)

        # Отправляем уведомление с НОВЫМ статусом
        if status_data.status in ["shipped", "delivered"]:
            await self.send_status_notification(updated_order, status_data.status)

        await self.db.commit()

        return {
            "order_id": order_id,
            "old_status": old_status,  # старый статус
            "new_status": status_data.status,  # новый статус
            "message": "Статус обновлен"
        }

    async def send_status_notification(self, order, new_status: str):
        # 1. Получить данные пользователя
        try:
            user = await self.db.users.get_one(id=order.user_id)
        except NoResultFound:
            return

        # 2. Подготовить данные
        notification_data = {
            "order_id": order.id,
            "order_number": order.order_number,
            "user_id": user.id,
            "user_email": user.email,
            "old_status": order.status,
            "new_status": new_status,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        try:
            send_order_status_notification_task.delay(notification_data)
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление: {e}")

