from src.exceptions.exception import (
    ObjectNotFoundException,
    BrandNotFoundException,
    CannotRemoveBrandHTTPException,
)
from src.schemas.brands import BrandsAdd, BrandsPatch
from src.services.base import BaseService


class BrandService(BaseService):
    async def get_brands(self):
        return await self.db.brands.get_all()

    async def get_brand(self, brand_id: int):
        return await self.get_brand_with_check(brand_id)

    async def add_brand(self, data: BrandsAdd):
        brand = await self.db.brands.add(data)
        await self.db.commit()
        return brand

    async def update_brand(
        self, data: BrandsPatch, brand_id: int, exclude_unset: bool = False
    ):
        await self.get_brand_with_check(brand_id)
        await self.db.brands.exit(data, exclude_unset=exclude_unset, id=brand_id)
        await self.db.commit()

    async def delete_brand(self, brand_id: int):
        brand = await self.get_brand_with_check(brand_id)
        products = await self.db.products.get_filtered(brand_id=brand_id)
        if products:
            product_ids = [p.id for p in products]
            raise CannotRemoveBrandHTTPException(brand.name, product_ids)
        await self.db.brands.delete(id=brand_id)
        await self.db.commit()

    async def get_brand_with_check(self, brand_id: int):
        try:
            return await self.db.brands.get_one(id=brand_id)
        except ObjectNotFoundException:
            raise BrandNotFoundException
