from fastapi import APIRouter, Query, Body, UploadFile, File
from src.api.dependencies import DBDep, PaginationDep
from src.schemas.products import ProductsAddRequest, ProductsPatch
from src.services.products import ProductService

router = APIRouter(prefix="/products", tags=["Товары"])

@router.get("")
async def get_products(
    db:DBDep,
    pagination: PaginationDep,
    name: str | None = Query(None, description="Название товара"),
    description: str | None = Query(None, description="Описание товара"),
    product_type: str | None = Query(None, description="Тип товара (clothing, footwear, accessory)"),
):
    return await ProductService(db).get_products(pagination, name, description, product_type)


@router.get("{product_id}")
async def get_product(db:DBDep, product_id: int):
    return await ProductService(db).get_product(product_id)


@router.post("")
async def add_product(
    db: DBDep,
    category_id: int,
    brand_id: int,
    product_data: ProductsAddRequest = Body(
        openapi_examples={
            "Футболка (Одежда)": {
                "summary": "Мужская футболка",
                "value": {
                    "name": "Футболка хлопковая",
                    "price": 1999.99,
                    "stock_quantity": 100,
                    "product_type": "clothing",
                    "description": "Мягкая хлопковая футболка",
                    "size": "M",
                    "color": "Черный",
                    "gender": "male",
                    "material": "Хлопок 100%",
                }
            },
            "Джинсы (Одежда)": {
                "summary": "Женские джинсы",
                "value": {
                    "name": "Джинсы скинни",
                    "price": 4999.99,
                    "stock_quantity": 50,
                    "product_type": "clothing",
                    "description": "Узкие джинсы с высокой талией",
                    "size": "S",
                    "color": "Синий",
                    "gender": "female",
                    "material": "Деним",
                }
            },
            "Куртка (Одежда)": {
                "summary": "Зимняя куртка",
                "value": {
                    "name": "Пуховая куртка",
                    "price": 12999.99,
                    "stock_quantity": 30,
                    "product_type": "clothing",
                    "description": "Теплая зимняя куртка с пуховым наполнителем",
                    "size": "L",
                    "color": "Красный",
                    "gender": "unisex",
                    "material": "Нейлон, пух",
                }
            },
            "Кроссовки (Обувь)": {
                "summary": "Беговые кроссовки",
                "value": {
                    "name": "Кроссовки для бега",
                    "price": 8999.99,
                    "stock_quantity": 75,
                    "product_type": "footwear",
                    "description": "Легкие кроссовки с амортизацией",
                    "size": "42",
                    "color": "Белый",
                    "gender": "male",
                    "material": "Сетка, резина",
                }
            },
            "Туфли (Обувь)": {
                "summary": "Кожаные туфли",
                "value": {
                    "name": "Кожаные туфли офисные",
                    "price": 6999.99,
                    "stock_quantity": 40,
                    "product_type": "footwear",
                    "description": "Классические кожаные туфли",
                    "size": "39",
                    "color": "Черный",
                    "gender": "male",
                    "material": "Натуральная кожа",
                }
            },
            "Сандалии (Обувь)": {
                "summary": "Летние сандалии",
                "value": {
                    "name": "Сандалии пляжные",
                    "price": 2999.99,
                    "stock_quantity": 60,
                    "product_type": "footwear",
                    "description": "Легкие сандалии для пляжа",
                    "size": "36",
                    "color": "Бежевый",
                    "gender": "female",
                    "material": "Эко-кожа",
                }
            },
            "Сумка (Аксессуар)": {
                "summary": "Кожаная сумка",
                "value": {
                    "name": "Сумка через плечо",
                    "price": 5999.99,
                    "stock_quantity": 25,
                    "product_type": "accessory",
                    "description": "Стильная кожаная сумка",
                    "size": "Средняя",
                    "color": "Коричневый",
                    "gender": "female",
                    "material": "Натуральная кожа",
                }
            },
            "Ремень (Аксессуар)": {
                "summary": "Кожаный ремень",
                "value": {
                    "name": "Ремень классический",
                    "price": 1999.99,
                    "stock_quantity": 80,
                    "product_type": "accessory",
                    "description": "Кожаный ремень с металлической пряжкой",
                    "size": "L",
                    "color": "Черный",
                    "gender": "male",
                }
            },
            "Шарф (Аксессуар)": {
                "summary": "Шерстяной шарф",
                "value": {
                    "name": "Шарф зимний",
                    "price": 2499.99,
                    "stock_quantity": 45,
                    "product_type": "accessory",
                    "description": "Теплый шерстяной шарф",
                    "size": "180x30 см",
                    "color": "Серый",
                    "gender": "unisex",
                    "material": "Шерсть 80%, акрил 20%",
                }
            }
        }
    ),
):
    product = await ProductService(db).add_product(category_id, brand_id, product_data)
    return {"status": "OK", "data": product}


@router.post("/{product_id}/images")
async def add_product_images(
    product_id: int,
    db: DBDep,
    images: list[UploadFile] = File(..., description="Список изображений товара"),
):
    await ProductService(db).add_product_images(product_id, images)
    return {
        "status": "OK",
        "message": f"Загрузка {len(images)} изображений начата",
        "product_id": product_id}


@router.put("/{product_id}")
async def exit_product(
    db: DBDep,
    product_id: int,
    category_id: int,
    brand_id: int,
    product_data: ProductsPatch
):
    await ProductService(db).update_product(product_id, category_id, brand_id, product_data)
    return {"status": "OK"}


@router.patch("/{product_id}")
async def exit_product(
    db: DBDep,
    product_id: int,
    category_id: int,
    brand_id: int,
    product_data: ProductsPatch):

    await ProductService(db).update_product(
        product_id,
        category_id,
        brand_id,
        product_data,
        exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{product_id}")
async def delete_product(db: DBDep, product_id: int):
    await ProductService(db).delete_product(product_id)
    return {"status": "OK"}
