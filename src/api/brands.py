from fastapi import  APIRouter, Body

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.schemas.brands import BrandsAdd, BrandsPatch
from src.services.brands import BrandService

router = APIRouter(prefix="/brands", tags=["Бренды"])

@router.get("")
async def get_brands(db:DBDep, user_id: int = require_permission(Permission.VIEW_BRANDS)):
    return await BrandService(db).get_brands()


@router.get("{brand_id}")
async def get_brand(
    db:DBDep,
    brand_id: int,
    user_id: int = require_permission(Permission.VIEW_BRANDS)):
    return await BrandService(db).get_brand(brand_id)


@router.post("")
async def add_brand(
    db: DBDep,
    brand_data: BrandsAdd = Body(
        openapi_examples={
            "Nike": {
                "summary": "Спортивный бренд",
                "value": {
                    "name": "Nike",
                    "description": "Американский производитель спортивной одежды и обуви"
                }
            },
            "Zara": {
                "summary": "Модный бренд одежды",
                "value": {
                    "name": "Zara",
                    "description": "Испанская сеть магазинов модной одежды"
                }
            },
            "Adidas": {
                "summary": "Спортивный бренд",
                "value": {
                    "name": "Adidas",
                    "description": "Немецкий производитель спортивной одежды и аксессуаров"
                }
            }
        }
    ),
    user_id: int = require_permission(Permission.MANAGE_BRANDS)
):
    brand = await BrandService(db).add_brand(brand_data)
    return {"status": "OK", "data": brand}

@router.put("/{brand_id}")
async def exit_brand(
    db:DBDep,
    brand_id: int,
    brand_data: BrandsPatch,
    user_id: int = require_permission(Permission.MANAGE_BRANDS)
):
    await BrandService(db).update_brand(brand_data, brand_id)
    return {"status": "OK"}


@router.patch("/{brand_id}")
async def partial_change_brand(
    db:DBDep,
    brand_id: int,
    brand_data: BrandsPatch,
    user_id: int = require_permission(Permission.MANAGE_BRANDS)
):
    await BrandService(db).update_brand(brand_data, brand_id, exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{brand_id}")
async def delete_brand(
    db:DBDep,
    brand_id: int,
    user_id: int = require_permission(Permission.DELETE_BRANDS)
):
    await BrandService(db).delete_brand(brand_id)
    return {"status": "OK"}
