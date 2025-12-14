from fastapi import  APIRouter, Body

from src.api.dependencies import DBDep
from src.schemas.brands import BrandsAdd
from src.services.brands import BrandService

router = APIRouter(prefix="/brands", tags=["Бренды"])

@router.get("")
async def get_brands(db:DBDep):
    return await BrandService(db).get_brands()


@router.get("{brand_id}")
async def get_brand(db:DBDep, brand_id: int):
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
    )
):
    brand = await BrandService(db).add_brand(brand_data)
    return {"status": "OK", "data": brand}

