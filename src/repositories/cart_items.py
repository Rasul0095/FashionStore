from src.repositories.base import BaseRepository
from src.models.cart_items import CartItemOrm
from src.schemas.cart_items import CartItem


class CartItemsRepository(BaseRepository):
    model = CartItemOrm
    schemas = CartItem
