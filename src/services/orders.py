from datetime import datetime
import logging

from src.core.permissions import Permission
from src.exceptions.exception import PermissionDeniedHTTPException, ObjectNotFoundException, OrderNotFoundException, \
    ErrorUpdatingBalancesHTTPException, InvalidStatusHTTPException, ProductOutOfStockHTTPException, \
    OrderCannotModifiedHTTPException, OrderCannotDeletedHTTPException, CartEmptyHTTPException, \
 CancelledOrderHTTPException, DeliveredOrderHTTPException, AddressNotFoundException
from src.repositories.utils import generate_order_number, check_product_availability_and_calculate_simple, \
    get_update_stock_for_cart_query
from src.schemas.order_items import OrderItemsAdd
from src.schemas.orders import OrdersAddRequest, OrdersAdd, OrderStatusUpdateRequest, OrderStatusUpdate, OrdersPatch, \
    OrdersPut
from src.schemas.products import ProductUpdate
from src.services.addresses import AddressService
from src.services.auth import AuthService
from src.services.base import BaseService
from src.services.carts import CartService
from src.services.products import ProductService
from src.tasks.tasks import send_order_status_notification_task


class OrderService(BaseService):
    async def get_my_orders(self, user_id: int, target_user_id: int = None):
        target = target_user_id if target_user_id else user_id
        if target != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        return await self.db.orders.get_filtered(user_id=target)

    async def get_order(self, order_id: int, user_id: int):
        order = await self.get_order_with_check(order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        return order

    async def add_order(self, user_id: int, address_id: int, data: OrdersAddRequest):
        cart = await CartService(self.db).get_cart_user_with_check(user_id)
        # 1. Проверка наличия товаров
        query = check_product_availability_and_calculate_simple(user_id)
        result = await self.db.session.execute(query)
        summary = result.first()

        if not summary or summary.total_items == 0:
            raise CartEmptyHTTPException

        # 2. Проверка адреса
        address = await AddressService(self.db).get_address_with_check(address_id)
        if cart.user_id != address.user_id:
            raise AddressNotFoundException
        # 3. Получить товары корзины
        cart_items = await self.db.cart_items.get_filtered(cart_id=cart.id)

        # 3.1. Двойная проверка наличия перед обновлением
        for item in cart_items:
            product = await ProductService(self.db).get_product_with_check(item.product_id)
            if product.stock_quantity < item.quantity:
                await self.db.rollback()
                raise ProductOutOfStockHTTPException(product.name)

        # 4. Создать заказ
        order_number = generate_order_number(user_id)
        order_data = OrdersAdd(
            **data.model_dump(),
            user_id=user_id,
            address_id=address_id,
            order_number=order_number,
            total_amount=summary.total_amount,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        order = await self.db.orders.add(order_data)

        # 5. Создать order_items
        for item in cart_items:
            product = await ProductService(self.db).get_product_with_check(item.product_id)
            order_item = OrderItemsAdd(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                final_price=product.price
            )
            await self.db.order_items.add(order_item)

        # 6. Обновить остатки с блокировкой
        update_stmt = get_update_stock_for_cart_query(user_id)
        result = await self.db.session.execute(update_stmt)
        updated = len(result.all())

        if updated != summary.available_items:
            await self.db.rollback()
            raise ErrorUpdatingBalancesHTTPException

        # 7. Очистить корзину
        await self.db.cart_items.delete(cart_id=cart.id)

        await self.db.commit()
        return order

    async def change_order_status(self, order_id: int, status_data: OrderStatusUpdateRequest, user_id: int):
        order = await self.get_order_with_check(order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
        if status_data.status not in valid_statuses:
            status = ", ".join(valid_statuses)
            raise InvalidStatusHTTPException(status)

        if status_data.status and status_data.status != order.status:
            if order.status != "pending":
                raise OrderCannotModifiedHTTPException(order.status)

        old_status = order.status
        # Проверяем логику по СТАРОМУ статусу
        if old_status == "cancelled":
            raise CancelledOrderHTTPException
        if old_status == "delivered":
            raise DeliveredOrderHTTPException

        # Обновляем статус
        update_data = OrderStatusUpdate(
            status=status_data.status,
            updated_at=datetime.utcnow(),
        )
        await self.db.orders.exit(update_data, id=order_id, exclude_unset=True)

        # Отправляем уведомление с НОВЫМ статусом
        updated_order = await self.get_order_with_check(order_id)
        if status_data.status in ["shipped", "delivered", "paid"]:
            await self.send_status_notification(updated_order, status_data.status)
        await self.db.commit()
        return {
            "order_id": order_id,
            "old_status": old_status,  # старый статус
            "new_status": status_data.status,  # новый статус
            "message": "Статус обновлен"
        }
    async def exit_order(self, order_id: int, user_id: int, data: OrdersPut):
        order = await self.get_order_with_check(order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        if order.status != "pending":
            raise OrderCannotModifiedHTTPException(order.status)

        await self.db.orders.exit(data, id=order_id, exclude_unset=False)
        await self.db.commit()
        return order

    async def partial_change_order(self, order_id: int, user_id: int, data: OrdersPatch):
        order = await self.get_order_with_check(order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        if order.status != "pending":
            raise OrderCannotModifiedHTTPException(order.status)

        await self.db.orders.exit(data, id=order_id, exclude_unset=True)
        await self.db.commit()
        return order

    async def delete_order(self, order_id: int, user_id: int):
        order = await self.get_order_with_check(order_id)
        if order.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        if order.status not in ["pending", "cancelled"]:
            raise OrderCannotDeletedHTTPException(order.status)

        order_items = await self.db.order_items.get_filtered(order_id=order_id)
        for item in order_items:
            product = await ProductService(self.db).get_product_with_check(item.product_id)
            update_data = ProductUpdate(
                stock_quantity=product.stock_quantity + item.quantity,
                updated_at=datetime.utcnow())
            await self.db.products.edit(update_data, id=product.id, exclude_unset=True)

        # Удалить связанные order_items
        await self.db.order_items.delete(order_id=order_id)

        await self.db.orders.delete(id=order_id)
        await self.db.commit()
        return {"message": "Заказ удален", "order_id": order_id}

    async def send_status_notification(self, order, new_status: str):
        # 1. Получить данные пользователя
        user = await AuthService(self.db).get_user_with_check(order.user_id)

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

    async def get_order_with_check(self, order_id: int):
        try:
            return await self.db.orders.get_one(id=order_id)
        except ObjectNotFoundException:
            raise OrderNotFoundException
