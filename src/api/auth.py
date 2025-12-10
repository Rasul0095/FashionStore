from fastapi import APIRouter, Query, Response

from src.api.dependencies import DBDep, UserIdDep
from src.services.auth import AuthService
from src.schemas.users import UserAddRequest, UserLogin, RefreshRequest

router = APIRouter(prefix="/auth", tags=["Аутентификация и Авторизация"])

@router.post("/register")
async def register_user(
    db: DBDep,
    user_data: UserAddRequest,
    role_name: str = Query(default="user", description="Role name (user, manager, admin)")
    ):
    await AuthService(db).register_user(user_data, role_name)
    return {"status": "OK"}


@router.post("/login")
async def login_user(
    response: Response,
    db: DBDep,
    user_data: UserLogin
):
    tokens = await AuthService(db).login_user(user_data)
    response.set_cookie("access_token", tokens["access_token"])
    response.set_cookie("refresh_token", tokens["refresh_token"])
    return {"access_token": tokens["access_token"]}


@router.post("/refresh")
async def refresh_tokens(
    response: Response,
    db: DBDep,
    refresh_token: RefreshRequest
):
    tokens = await AuthService(db).refresh_tokens(refresh_token.refresh_token)
    response.set_cookie("access_token", tokens["access_token"])
    response.set_cookie("refresh_token", tokens["refresh_token"], secure=False)
    return {"access_token": tokens["access_token"]}


@router.get("/me")
async def get_me(
    db: DBDep,
    user_id: UserIdDep,
):
    return await AuthService(db).get_me(user_id)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "OK"}

