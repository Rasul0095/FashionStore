from fastapi import APIRouter, Body, Query

from src.api.dependencies import DBDep
from src.schemas.roles import RoleAdd
from src.services.roles import RoleService


router = APIRouter(prefix="/roles", tags=["Роли"])

@router.get("")
async def get_roles(db:DBDep):
    return await RoleService(db).get_roles()


@router.get("/{role_name}")
async def get_role(db:DBDep, role_name: str):
    return await RoleService(db).get_role(role_name)


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

    }
)):
    roles = await RoleService(db).add_role(role_data)
    return {"status": "OK", "data": roles}