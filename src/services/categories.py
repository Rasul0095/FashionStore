from src.schemas.categories import CategoriesAdd
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