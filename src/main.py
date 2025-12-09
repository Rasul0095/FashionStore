import sys
from pathlib import Path

import uvicorn
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from src.api.roles import router as router_role
from src.api.auth import router as router_auth

app = FastAPI()

app.include_router(router_role)
app.include_router(router_auth)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)