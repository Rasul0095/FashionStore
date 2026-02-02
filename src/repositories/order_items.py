from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.models.order_items import OrderItemOrm
from src.repositories.mappers.mappers import OrderItemDataMapper


class OrderItemsRepository(BaseRepository):
    model = OrderItemOrm
    mapper = OrderItemDataMapper

    async def get_by_order_ids(self, order_ids: list[int]):
        if not order_ids:
            return []

        query = select(self.model).filter(self.model.order_id.in_(order_ids))
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.mapper.map_to_domain_entity(model) for model in models]
