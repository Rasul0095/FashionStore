from sqlalchemy import select, func

from src.repositories.base import BaseRepository
from src.models.products import ProductOrm
from src.repositories.mappers.mappers import ProductDataMapper


class ProductsRepository(BaseRepository):
    model = ProductOrm
    mapper = ProductDataMapper

    async def get_search_by_name(self,
        name: str | None = None,
        description: str | None = None,
        product_type: str | None = None,
        limit: int = 5,
        offset: int = 0
    ):
        query = select(ProductOrm)
        if name:
            name_lower = name.strip().lower()
            query = query.filter(func.lower(ProductOrm.name).like(f"%{name_lower}%"))

        if description:
            description_lower = description.strip().lower()
            query = query.filter(func.lower(ProductOrm.description).like(f"%{description_lower}%"))

        if product_type:
            query = query.filter(ProductOrm.product_type == product_type.strip())

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        products = result.scalars().all()
        return [self.mapper.map_to_domain_entity(model) for model in products]
