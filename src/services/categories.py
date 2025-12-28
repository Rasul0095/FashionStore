from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.schemas.categories import CategoriesAdd, CategoriesPatch
from src.services.base import BaseService


class CategoryService(BaseService):
    async def get_categories(self):
        return await self.db.categories.get_all()

    async def get_category(self, category_id: int):
        return await self.db.categories.get_one(id=category_id)

    async def add_category(self, data: CategoriesAdd):
        category = await self.db.categories.add(data)
        await self.db.commit()
        return category

    async def update_category(self, data: CategoriesPatch, category_id: int, exclude_unset: bool = False):
        try:
            await self.db.categories.get_one(id=category_id)
        except NoResultFound:
            raise HTTPException(404, "Категория не найдена")

        await self.db.categories.exit(data, exclude_unset=exclude_unset, id=category_id)
        await self.db.commit()

    async def delete_category(self, category_id: int):
        try:
            await self.db.categories.get_one(id=category_id)
        except NoResultFound:
            raise HTTPException(404, "Категория не найдена")

        products = await self.db.products.get_all(category_id=category_id)
        for product in products:
            await self.db.reviews.delete(product_id=product.id)

        await self.db.products.delete(category_id=category_id)
        await self.db.categories.delete(id=category_id)
        await self.db.commit()