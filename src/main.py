import sys
from pathlib import Path

import uvicorn
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from src.api.addresses import router as router_address
from src.api.brands import router as router_brand
from src.api.categories import router as router_category
from src.api.products import router as router_product
from src.api.roles import router as router_role
from src.api.auth import router as router_auth

app = FastAPI()

app.include_router(router_address)
app.include_router(router_brand)
app.include_router(router_category)
app.include_router(router_product)
app.include_router(router_role)
app.include_router(router_auth)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)