from fastapi import APIRouter
from src.api.dependencies import DBDep, UserIdDep, require_permission
from src.core.permissions import Permission
from src.exceptions.exception import CartNotExistsHTTPException, CartNotExistsException
from src.services.carts import CartService

router = APIRouter(prefix="/carts", tags=["Корзина"])


@router.get("")
async def get_my_cart(
    db: DBDep, user_id: int = require_permission(Permission.MANAGE_CART)
):
    try:
        return await CartService(db).get_my_cart(user_id)
    except CartNotExistsException:
        raise CartNotExistsHTTPException


@router.post("")
async def add_cart(
    db: DBDep,
    user_id: UserIdDep,
):
    cart = await CartService(db).add_cart(user_id)
    return {"status": "OK", "data": cart}


@router.delete("")
async def delete_cart(
    db: DBDep, user_id: int = require_permission(Permission.MANAGE_CART)
):
    try:
        await CartService(db).delete_my_cart(user_id)
    except CartNotExistsException:
        raise CartNotExistsHTTPException
    return {"status": "OK"}
