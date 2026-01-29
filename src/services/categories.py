from src.exceptions.exception import ObjectNotFoundException, CategoryNotFoundException, \
    CannotRemoveCategoryHTTPException
from src.schemas.categories import CategoriesAdd, CategoriesPatch
from src.services.base import BaseService


class CategoryService(BaseService):
    async def get_categories(self):
        return await self.db.categories.get_all()

    async def get_category(self, category_id: int):
        return await self.get_category_with_check(category_id)

    async def add_category(self, data: CategoriesAdd):
        category = await self.db.categories.add(data)
        await self.db.commit()
        return category

    async def update_category(self, data: CategoriesPatch, category_id: int, exclude_unset: bool = False):
        await self.get_category_with_check(category_id)
        await self.db.categories.exit(data, exclude_unset=exclude_unset, id=category_id)
        await self.db.commit()

    async def delete_category(self, category_id: int):
        category = await self.get_category_with_check(category_id)
        products = await self.db.products.get_filtered(category_id=category_id)
        if products:
            product_ids = [p.id for p in products]
            raise CannotRemoveCategoryHTTPException(category.name, product_ids)
        await self.db.categories.delete(id=category_id)
        await self.db.commit()

    async def get_category_with_check(self, category_id: int):
        try:
            return await self.db.categories.get_one(id=category_id)
        except ObjectNotFoundException:
            raise CategoryNotFoundException