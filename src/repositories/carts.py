from src.repositories.base import BaseRepository
from src.models.carts import CartOrm
from src.schemas.carts import Cart


class CartsRepository(BaseRepository):
    model = CartOrm
    schemas = Cart
