from fastapi import APIRouter
from src.api.dependencies import DBDep, UserIdDep, require_permission
from src.core.permissions import Permission
from src.services.carts import CartService

router = APIRouter(prefix="/carts", tags=["Корзина"])

@router.get("")
async def get_my_cart(db: DBDep, user_id: int = require_permission(Permission.MANAGE_CART)):
    return await CartService(db).get_my_cart(user_id)


@router.post("")
async def add_cart(
    db: DBDep,
    user_id: UserIdDep,
):
    cart = await CartService(db).add_cart(user_id)
    return {"status": "OK", "data": cart}


@router.delete("")
async def delete_cart(db: DBDep, user_id: int = require_permission(Permission.MANAGE_CART)):
    await CartService(db).delete_my_cart(user_id)
    return {"status": "OK"}
