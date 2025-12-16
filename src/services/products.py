from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from datetime import datetime

from src.schemas.products import ProductsAddRequest, ProductsAdd
from src.services.base import BaseService
from src.api.dependencies import PaginationDep
from src.repositories.utils import generate_sku

class ProductService(BaseService):
    async def get_products(self,
        pagination: PaginationDep,
        name: str | None = None,
        description: str | None = None,
        product_type: str | None = None,
    ):
        per_page = pagination.per_page or 5
        return await self.db.products.get_search_by_name(
            name=name,
            description=description,
            product_type=product_type,
            limit=per_page,
            offset=per_page * (pagination.page - 1),)

    async def get_product(self, product_id: int):
        try:
            await self.db.products.get_one(id=product_id)
        except NoResultFound:
            raise HTTPException(404, "Товар не найден")
        return await self.db.products.get_one_or_none(id=product_id)

    async def add_product(self, category_id: int, brand_id: int, data: ProductsAddRequest):
        try:
            await self.db.categories.get_one(id=category_id)
        except NoResultFound:
            raise HTTPException(404, "Категория не найдена")
        try:
            await self.db.categories.get_one(id=brand_id)
        except NoResultFound:
            raise HTTPException(404, "Бренд не найден")
        sku = generate_sku(data.product_type, category_id, brand_id)
        product_data = ProductsAdd(
            **data.model_dump(),
            brand_id=brand_id,
            category_id=category_id,
            sku=sku,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),)
        product = await self.db.products.add(product_data)
        await self.db.commit()
        return product