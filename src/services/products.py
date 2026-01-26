from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import NoResultFound
from datetime import datetime

from src.exceptions.exception import ObjectNotFoundException, ProductNotFoundException
from src.schemas.products import ProductsAddRequest, ProductsAdd, ProductImagesUpdate, ProductsPatch
from src.services.base import BaseService
from src.api.dependencies import PaginationDep
from src.repositories.utils import generate_sku, save_uploaded_files
from src.services.brands import BrandService
from src.services.categories import CategoryService


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
        return await self.get_product_with_check(product_id)

    async def add_product(self,
        category_id: int,
        brand_id: int,
        data: ProductsAddRequest,):
        await CategoryService(self.db).get_category_with_check(category_id)
        await BrandService(self.db).get_brand_with_check(brand_id)
        sku = generate_sku(data.product_type, category_id, brand_id)
        product_data = ProductsAdd(
            **data.model_dump(),
            brand_id=brand_id,
            category_id=category_id,
            sku=sku,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        product = await self.db.products.add(product_data)
        await self.db.commit()
        return product

    async def add_product_images(self, product_id: int, images: list[UploadFile]):
        await self.get_product_with_check(product_id)
        saved_paths = await save_uploaded_files(
            files=images,
            prefix=f"review_{product_id}",
            upload_dir="src/static/images-products")

        update_data = ProductImagesUpdate(images=saved_paths)
        # Обновляем БД
        await self.db.products.exit(
            update_data,
            exclude_unset=True,
            id=product_id
        )
        await self.db.commit()
        return {"saved_paths": saved_paths, "product_id": product_id}

    async def update_product(self,
        product_id: int,
        category_id: int,
        brand_id: int,
        data: ProductsPatch,
        exclude_unset: bool = False):
        await self.get_product_with_check(product_id)
        await CategoryService(self.db).get_category_with_check(category_id)
        await BrandService(self.db).get_brand_with_check(brand_id)
        await self.db.products.exit(data, id=product_id, exclude_unset=exclude_unset)
        await self.db.commit()

    async def delete_product(self, product_id: int):
        product = await self.get_product_with_check(product_id)
        await self.db.cart_items.delete(product_id=product_id)
        await self.db.order_items.delete(product_id=product_id)
        await self.db.reviews.delete(product_id=product_id)

        if product.images:
            import os
            for image_path in product.images:
                if os.path.exists(image_path):
                    os.remove(image_path)
        await self.db.products.delete(id=product_id)
        await self.db.commit()

    async def get_product_with_check(self, product_id: int):
        try:
            return await self.db.products.get_one(id=product_id)
        except ObjectNotFoundException:
            raise ProductNotFoundException