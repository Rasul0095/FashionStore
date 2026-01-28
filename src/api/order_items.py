from fastapi import APIRouter, Query

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.exceptions.exception import OrderItemNotFoundException, OrderItemNotFoundHHTPException, OrderNotFoundException, \
    OrderNotFoundHTTPException, ProductNotFoundException, ProductNotFoundHTTPException
from src.schemas.order_items import OrderItemsAddRequest, OrderItemUpdate
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
    try:
        return await OrderItemService(db).get_order_item(item_id, user_id)
    except OrderItemNotFoundException:
        raise OrderItemNotFoundHHTPException
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException

@router.post("/{order_id}")
async def add_items_from_cart(
    db: DBDep,
    order_id: int,
    items: OrderItemsAddRequest,
    user_id: int = require_permission(Permission.MANAGE_ORDER_ITEMS),
):
    try:
        result = await OrderItemService(db).add_items_to_order(order_id, [items], user_id)
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    return result


@router.put("/{item_id}")
async def update_order_item(
    db: DBDep,
    item_id: int,
    item_data: OrderItemUpdate,
    user_id: int = require_permission(Permission.MANAGE_ORDER_ITEMS),
):
    try:
        order_item = await OrderItemService(db).update_order_item(item_id, user_id, item_data)
    except OrderItemNotFoundException:
        raise OrderItemNotFoundHHTPException
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    return {"status": "OK", "data": order_item}


@router.patch("/{item_id}")
async def partial_update_order_item(
    db: DBDep,
    item_id: int,
    item_data: OrderItemUpdate,
    user_id: int = require_permission(Permission.MANAGE_ORDER_ITEMS),
):
    try:
        order_item = await OrderItemService(db).update_order_item(
        item_id, user_id, item_data, exclude_unset=True)
    except OrderItemNotFoundException:
        raise OrderItemNotFoundHHTPException
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    return {"status": "OK", "data": order_item}


@router.delete("/{item_id}")
async def delete_order_item(
    db: DBDep,
    item_id: int,
    user_id: int = require_permission(Permission.MANAGE_ORDER_ITEMS),
):
    try:
        order_item = await OrderItemService(db).delete_order_item(item_id, user_id)
    except OrderItemNotFoundException:
        raise OrderItemNotFoundHHTPException
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    return order_item