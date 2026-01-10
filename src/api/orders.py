from fastapi import APIRouter, Query

from src.api.dependencies import DBDep, UserIdDep, require_permission
from src.core.permissions import Permission
from src.schemas.orders import OrdersAddRequest, OrderStatusUpdateRequest
from src.services.orders import OrderService

router = APIRouter(prefix="/orders", tags=["Заказы"])

@router.get("")
async def get_my_orders(
    db:DBDep,
    user_id: int = require_permission(Permission.VIEW_ORDERS),
    target_user_id: int | None = Query(None, description="ID пользователя (только для админов)"),

):
    return await OrderService(db).get_my_orders(user_id, target_user_id)


@router.get("/{order_id}")
async def get_order(
    db:DBDep,
    order_id: int,
    user_id: int = require_permission(Permission.VIEW_ORDERS)
):
    return await OrderService(db).get_order(order_id, user_id)


@router.post("")
async def add_order(
    db: DBDep,
    address_id: int,
    user_id: UserIdDep,
    order_data: OrdersAddRequest,
):
    order = await OrderService(db).add_order(user_id, address_id, order_data)
    return {"status": "OK", "data": order}


@router.post("/{order_id}/status")
async def change_order_status(
    db: DBDep,
    order_id: int,
    status_data: OrderStatusUpdateRequest,
    user_id: int = require_permission(Permission.MANAGE_ORDERS),
):
    return await OrderService(db).change_order_status(order_id, status_data, user_id)
