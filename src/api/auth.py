from fastapi import APIRouter, Query, Response

from src.api.dependencies import DBDep, UserIdDep, require_permission
from src.core.permissions import Permission
from src.exceptions.exception import UserAlreadyExistsException, UserEmailAlreadyExistsHTTPException, EmailNotRegisteredException, \
    EmailNotRegisteredHTTPException, IncorrectPasswordException, IncorrectPasswordHTTPException, \
    UserNotFoundHTTPException, UserNotFoundException, RoleNotExistsException, RoleNotExistsHTTPException
from src.services.auth import AuthService
from src.schemas.users import UserAddRequest, UserLogin, RefreshRequest, UserUpdate

router = APIRouter(prefix="/auth", tags=["Аутентификация и Авторизация"])

@router.post("/register")
async def register_user(
    db: DBDep,
    user_data: UserAddRequest,
    role_name: str = Query(default="user", description="Role name (user, manager, admin)")
    ):
    try:
        await AuthService(db).register_user(user_data, role_name)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException
    except UserAlreadyExistsException:
        raise UserEmailAlreadyExistsHTTPException
    return {"status": "OK"}


@router.post("/login")
async def login_user(
    response: Response,
    db: DBDep,
    user_data: UserLogin
):
    try:
        tokens = await AuthService(db).login_user(user_data)
    except EmailNotRegisteredException:
        raise EmailNotRegisteredHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
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

@router.patch("/{user_id}")
async def partial_change_user(
    user_id: int,
    user_data: UserUpdate,
    db: DBDep,
    current_user_id: int = require_permission(Permission.EDIT_USERS)
):
    try:
        await AuthService(db).update_user(user_id, user_data, current_user_id)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException
    return {"status": "OK"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: DBDep,
    current_user_id: int = require_permission(Permission.DELETE_USERS)
):
    try:
        await AuthService(db).delete_user(user_id, current_user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "OK"}


