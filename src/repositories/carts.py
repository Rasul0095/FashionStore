from src.repositories.base import BaseRepository
from src.models.carts import CartOrm
from src.repositories.mappers.mappers import CartDataMapper


class CartsRepository(BaseRepository):
    model = CartOrm
    mapper = CartDataMapper
