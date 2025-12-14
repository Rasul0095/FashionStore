from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.schemas.brands import BrandsAdd, BrandsPatch
from src.services.base import BaseService


class BrandService(BaseService):
    async def get_brands(self):
        return await self.db.brands.get_all()

    async def get_brand(self, brand_id: int):
        return await self.db.brands.get_one(id=brand_id)

    async def add_brand(self, data: BrandsAdd):
        brand = await self.db.brands.add(data)
        await self.db.commit()
        return brand

    async def update_brand(self, data: BrandsPatch, brand_id: int, exclude_unset: bool = False):
        try:
            await self.db.categories.get_one(id=brand_id)
        except NoResultFound:
            raise HTTPException(404, "Бренд не найден")

        await self.db.brands.exit(data, exclude_unset=exclude_unset, id=brand_id)
        await self.db.commit()

    async def delete_brand(self, brand_id: int):
        try:
            await self.db.categories.get_one(id=brand_id)
        except NoResultFound:
            raise HTTPException(404, "Бренд не найден")

        await self.db.brands.delete(id=brand_id)
        await self.db.commit()
