from typing import Annotated
from fastapi import Depends, Request, HTTPException, Query
from pydantic import BaseModel

from src.core.permissions import Permission
from src.utils.db_manager import DBManager
from src.database import async_session_maker
from src.services.auth import AuthService


class PaginationParams(BaseModel):
    page: Annotated[int, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]

def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Вы не предоставили токен доступа")
    return token

def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]

UserIdDep = Annotated[int, Depends(get_current_user_id)]

async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]

async def permission_checker(
    db: DBDep,
    permission: Permission,
    user_id: int  = UserIdDep
):
    # Получаем роль пользователя
    permissions = await AuthService(db).get_user_permissions(user_id=user_id)

    # Проверяем есть ли право
    if permission.value not in permissions:
        raise HTTPException(403, f"Требуется {permission.value} разрешение")

    return user_id

PermDep = Annotated[int, Depends(permission_checker)]

