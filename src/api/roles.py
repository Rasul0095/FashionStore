from fastapi import APIRouter, Body

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.exceptions.exception import RoleNotExistsException, RoleNotExistsHTTPException
from src.schemas.roles import RoleAdd, RolePatch, RoleUpdate
from src.services.roles import RoleService


router = APIRouter(prefix="/roles", tags=["Роли"])

@router.get("")
async def get_roles(db:DBDep, user_id: int = require_permission(Permission.VIEW_ROLES)):
    return await RoleService(db).get_roles()


@router.get("/{role_name}")
async def get_role(
    db:DBDep,
    role_name: str,
    user_id: int = require_permission(Permission.VIEW_ROLES)):
    try:
        return await RoleService(db).get_role(role_name)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException


@router.post("")
async def add_role(db:DBDep, role_data: RoleAdd = Body(
    openapi_examples={
        "Admin": {
            "value": {
                "name": "admin",
                "description": "Системный администратор с полными правами"
            }
        },
        "Manager": {
            "value": {
                "name": "manager",
                "description": "Менеджер магазина"
            }
        },
        "User": {
            "value": {
                "name": "user",
                "description": "Постоянный клиент"
            }
        },

    }),
    user_id: int = require_permission(Permission.MANAGE_ROLES)):
    roles = await RoleService(db).add_role(role_data)
    return {"status": "OK", "data": roles}


@router.put("/{role_name}")
async def exit_role(
    db: DBDep,
    role_name: str,
    role_data: RoleUpdate,
    user_id: int = require_permission(Permission.MANAGE_ROLES)):
    try:
        await RoleService(db).exit_role(role_name, role_data)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException
    return {"status": "OK"}


@router.patch("/{role_name}")
async def partial_change_role(
    db:DBDep,
    role_name: str,
    role_data: RolePatch,
    user_id: int = require_permission(Permission.MANAGE_ROLES)):
    try:
        await RoleService(db).partial_change_role( role_name, role_data,  exclude_unset=True)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException
    return {"status": "OK"}


@router.delete("/{role_name}")
async def delete_role(
    db: DBDep,
    role_name: str,
    user_id: int = require_permission(Permission.MANAGE_ROLES)):
    try:
        await RoleService(db).delete_role(role_name)
    except RoleNotExistsException:
        raise RoleNotExistsHTTPException
    return {"status": "OK"}
