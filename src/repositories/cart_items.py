from src.repositories.base import BaseRepository
from src.models.cart_items import CartItemOrm
from src.repositories.mappers.mappers import CartItemDataMapper


class CartItemsRepository(BaseRepository):
    model = CartItemOrm
    mapper = CartItemDataMapper
