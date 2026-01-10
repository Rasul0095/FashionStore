from src.repositories.base import BaseRepository
from src.models.orders import OrderOrm
from src.schemas.orders import Order


class OrdersRepository(BaseRepository):
    model = OrderOrm
    schemas = Order
