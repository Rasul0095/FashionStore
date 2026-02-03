from src.repositories.base import BaseRepository
from src.models.orders import OrderOrm
from src.repositories.mappers.mappers import OrderDataMapper


class OrdersRepository(BaseRepository):
    model = OrderOrm
    mapper = OrderDataMapper
