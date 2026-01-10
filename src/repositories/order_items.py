from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.models.order_items import OrderItemOrm
from src.schemas.order_items import OrderItem


class OrderItemsRepository(BaseRepository):
    model = OrderItemOrm
    schemas = OrderItem

    async def get_by_order_ids(self, order_ids: list[int]):
        if not order_ids:
            return []

        query = select(self.model).filter(self.model.order_id.in_(order_ids))
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self.schemas.model_validate(model, from_attributes=True)
                for model in models]
