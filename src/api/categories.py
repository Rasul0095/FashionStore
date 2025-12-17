from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.categories import CategoriesAdd, CategoriesPatch
from src.services.categories import CategoryService


router = APIRouter(prefix="/categories", tags=["Категории"])

@router.get("")
@cache(expire=10)
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
            "Верхняя одежда": {
                "value": {
                    "name": "Верхняя одежда",
                    "slug": "outerwear",
                    "product_type": "clothing"
                }
            },
            "Футболки": {
                "summary": "Категория футболок",
                "value": {
                    "name": "Футболки",
                    "slug": "t-shirts",
                    "product_type": "clothing"
                }
            },
            "Джинсы": {
                "summary": "Категория джинсов",
                "value": {
                    "name": "Джинсы",
                    "slug": "jeans",
                    "product_type": "clothing"
                }
            },
            "Куртки": {
                "summary": "Категория курток",
                "value": {
                    "name": "Куртки",
                    "slug": "jackets",
                    "product_type": "clothing"
                }
            },
            "Кроссовки": {
                "value": {
                    "name": "Кроссовки",
                    "slug": "sneakers",
                    "product_type": "footwear"
                }
            },
            "Беговые кроссовки": {
                "summary": "Категория беговой обуви",
                "value": {
                    "name": "Беговые кроссовки",
                    "slug": "running-sneakers",
                    "product_type": "footwear"
                }
            },
            "Туфли": {
                "summary": "Категория туфель",
                "value": {
                    "name": "Туфли",
                    "slug": "shoes",
                    "product_type": "footwear"
                }
            },
            "Сандалии": {
                "summary": "Категория сандалий",
                "value": {
                    "name": "Сандалии",
                    "slug": "sandals",
                    "product_type": "footwear"
                }
            },
            "Сумки": {
                "summary": "Категория сумок",
                "value": {
                    "name": "Сумки",
                    "slug": "bags",
                    "product_type": "accessory"
                }
            },
            "Ремни": {
                "summary": "Категория ремней",
                "value": {
                    "name": "Ремни",
                    "slug": "belts",
                    "product_type": "accessory"
                }
            },
            "Шарфы": {
                "summary": "Категория шарфов",
                "value": {
                    "name": "Шарфы",
                    "slug": "scarves",
                    "product_type": "accessory"
                }
            },
            "Головные уборы": {
                "summary": "Категория головных уборов",
                "value": {
                    "name": "Головные уборы",
                    "slug": "hats",
                    "product_type": "accessory"
                }
            },
        }
    )):
    category = await CategoryService(db).add_category(category_data)
    return {"status": "OK", "data": category}


@router.put("/{category_id}")
async def exit_category(
    db:DBDep,
    category_id: int,
    category_data: CategoriesPatch,
):
    await CategoryService(db).update_category(category_data, category_id)
    return {"status": "OK"}


@router.patch("/{category_id}")
async def partial_change_category(
    db:DBDep,
    category_id: int,
    category_data: CategoriesPatch,
):
    await CategoryService(db).update_category(category_data, category_id, exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{category_id}")
async def delete_category(db:DBDep, category_id: int):
    await CategoryService(db).delete_category(category_id)
    return {"status": "OK"}
