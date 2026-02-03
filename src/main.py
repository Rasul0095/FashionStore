# ruff: noqa: E402
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import logging

import uvicorn

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.init import redis_connector
from src.api.addresses import router as router_address
from src.api.brands import router as router_brand
from src.api.categories import router as router_category
from src.api.cart_items import router as router_cart_item
from src.api.carts import router as router_cart
from src.api.order_items import router as roter_order_item
from src.api.orders import router as router_order
from src.api.products import router as router_product
from src.api.reviews import router as router_review
from src.api.roles import router as router_role
from src.api.auth import router as router_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_connector.connect()
    FastAPICache.init(RedisBackend(redis_connector._redis), prefix="fastapi-cache")
    yield
    await redis_connector.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_address)
app.include_router(router_brand)
app.include_router(router_category)
app.include_router(router_cart_item)
app.include_router(router_cart)
app.include_router(roter_order_item)
app.include_router(router_order)
app.include_router(router_product)
app.include_router(router_review)
app.include_router(router_role)
app.include_router(router_auth)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
