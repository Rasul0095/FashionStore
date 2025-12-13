from fastapi import APIRouter, Body
from src.api.dependencies import DBDep
from src.schemas.categories import CategoriesAdd
from src.services.categories import CategoryService


router = APIRouter(prefix="/categories", tags=["Категории"])

@router.get("")
async def get_categories(db:DBDep):
    return await CategoryService(db).get_categories()


@router.get("/{category_id}")
async def get_category(db:DBDep, category_id: int):
    return await CategoryService(db).get_category(category_id)


@router.post("")
async def add_category(
    db: DBDep,
    category_data: CategoriesAdd = Body(
        openapi_examples={
            "Одежда": {
                "value": {
                    "name": "Верхняя одежда",
                    "slug": "outerwear",
                    "product_type": "clothing"
                }
            },
            "Обувь": {
                "value": {
                    "name": "Кроссовки",
                    "slug": "sneakers",
                    "product_type": "footwear"
                }
            },
            "Аксессуары": {
                "value": {
                    "name": "Сумки",
                    "slug": "bags",
                    "product_type": "accessory"
                }
            }
        }
    )):
    category = await CategoryService(db).add_category(category_data)
    return {"status": "OK", "data": category}

