from src.schemas.brands import BrandsAdd
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