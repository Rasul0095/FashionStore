from datetime import datetime
import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from sqlalchemy import func, select, update

from src.models import CartOrm
from src.models.cart_items import CartItemOrm
from src.models.products import ProductOrm


def get_update_stock_for_cart_query(user_id: int):
    """Обновления остатков товаров в корзине"""
    cart_subquery = (
        select(CartOrm.id)
        .where(CartOrm.user_id == user_id)
        .scalar_subquery()
    )

    cart_items_cte = (
        select(
            CartItemOrm.product_id,
            CartItemOrm.quantity,
        )
        .join(ProductOrm, ProductOrm.id == CartItemOrm.product_id)
        .where(
            CartItemOrm.cart_id == cart_subquery,
            ProductOrm.stock_quantity >= CartItemOrm.quantity
        )
        .cte("cart_items_cte")
    )

    update_stmt = (
        update(ProductOrm)
        .values(
            stock_quantity=ProductOrm.stock_quantity - cart_items_cte.c.quantity
        )
        .where(ProductOrm.id == cart_items_cte.c.product_id)
        .returning(ProductOrm.id)
    )

    return update_stmt

def check_product_availability_and_calculate_simple(user_id: int):
    cart_query = (
        select(
            CartItemOrm.product_id,
            CartItemOrm.quantity,
            ProductOrm.price,
            ProductOrm.stock_quantity,
            ProductOrm.name,
            (ProductOrm.stock_quantity >= CartItemOrm.quantity).label("available")
        )
        .join(ProductOrm, ProductOrm.id == CartItemOrm.product_id)
        .join(CartOrm, CartOrm.id == CartItemOrm.cart_id)
        .where(CartOrm.user_id == user_id)
    ).cte("cart_query")

    summary_query = (
        select(
            func.sum(cart_query.c.price * cart_query.c.quantity)
            .filter(cart_query.c.available == True).label("total_amount"),
            func.count().filter(cart_query.c.available == True).label("available_items"),
            func.count().label("total_items")
        )
        .select_from(cart_query)
    )
    return summary_query

def generate_sku(product_type: str, brand_id: int, category_id: int) -> str:
    # Пример: CLOTH-NIKE-123-20241217-ABC123
    timestamp = datetime.now().strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:6].upper()
    return f"{product_type[:5].upper()}-{brand_id}-{category_id}-{timestamp}-{unique}"

def generate_order_number(user_id: int) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}-{user_id:06d}"

async def save_uploaded_files(
        files: list[UploadFile],
        prefix: str,
        upload_dir: str = "src/static"
) -> list[str]:
    UPLOAD_DIR = Path(upload_dir)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for file in files:
        data = await file.read()
        ext = Path(file.filename).suffix or '.jpg'
        unique_name = f"{prefix}_{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / unique_name

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(data)

        saved_paths.append(str(file_path))

    return saved_paths