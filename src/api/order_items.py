from fastapi import APIRouter, Query

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.schemas.order_items import OrderItemsAddRequest
from src.services.order_items import OrderItemService

router = APIRouter(prefix="/order-items", tags=["Товары в заказах"])

@router.get("")
async def get_my_order_items(
    db: DBDep,
    user_id: int = require_permission(Permission.VIEW_ORDER_ITEMS),
    target_user_id: int | None = Query(None, description="ID пользователя (только для админов)"),
):
    return await OrderItemService(db).get_my_order_items(user_id, target_user_id)

@router.get("/{item_id}")
async def get_order_item(
    db: DBDep,
    item_id: int,
    user_id: int = require_permission(Permission.VIEW_ORDER_ITEMS)
):
    return await OrderItemService(db).get_order_item(item_id, user_id)

@router.post("/{order_id}")
async def add_items_from_cart(
    db: DBDep,
    order_id: int,
    items: OrderItemsAddRequest,
    user_id: int = require_permission(Permission.MANAGE_ORDER_ITEMS),
):
    result = await OrderItemService(db).add_items_to_order(order_id, [items], user_id)
    return result