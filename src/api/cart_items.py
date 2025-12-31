from fastapi import APIRouter, Query

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.schemas.cart_items import CartItemsAddRequest, CartItemsUpdate
from src.services.cart_items import CartItemService

router = APIRouter(prefix="/cart_items", tags=["Корзина товаров"])

@router.get("")
async def get_my_cart_items(
    db:DBDep,
    user_id: int = require_permission(Permission.VIEW_CART_ITEMS),
    target_user_id: int | None = Query(None, description="ID пользователя (только для админов)"),
):
    return await CartItemService(db).get_my_cart_items(user_id, target_user_id)

@router.get("/{cart_item_id}")
async def get_cart_item(
    db:DBDep,
    cart_item_id: int,
    user_id: int = require_permission(Permission.VIEW_CART_ITEMS),):
    return await CartItemService(db).get_cart_item(cart_item_id, user_id)


@router.post("")
async def add_cart_item(
    db: DBDep,
    product_id: int,
    cart_item_data: CartItemsAddRequest,
    user_id: int = require_permission(Permission.MANAGE_CART_ITEMS), ):
    cart_item = await CartItemService(db).add_cart_item(product_id, user_id, cart_item_data)
    return {"status": "OK", "data": cart_item}


@router.put("/{item_id}")
async def exit_cart_item(
    db: DBDep,
    item_id: int,
    cart_item_data: CartItemsUpdate,
    user_id: int = require_permission(Permission.MANAGE_CART_ITEMS),
):
    await CartItemService(db).update_cart_item(user_id, item_id, cart_item_data)
    return {"status": "OK"}


@router.patch("/{item_id}")
async def partial_change_cart_item(
    db: DBDep,
    item_id: int,
    cart_item_data: CartItemsUpdate,
    user_id: int = require_permission(Permission.MANAGE_CART_ITEMS),
):
    await CartItemService(db).update_cart_item(user_id, item_id, cart_item_data, exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{item_id}")
async def delete_cart_item(
    db:DBDep,
    item_id: int,
    user_id: int = require_permission(Permission.MANAGE_CART_ITEMS),
):
    await CartItemService(db).delete_cart_item(item_id, user_id)
    return {"status": "OK"}


