from src.core.permissions import ROLE_PERMISSIONS
from src.exceptions.exception import RoleNotExistsException, ObjectNotFoundException
from src.services.base import BaseService
from src.schemas.roles import RoleAdd, RoleUpdate, RolePatch


class RoleService(BaseService):
    async def get_roles(self):
        return await self.db.roles.get_all()

    async def get_role(self, role_name: str):
        return await self.get_role_with_check(role_name)

    async def add_role(self, data: RoleAdd):
        role_name = data.name.value
        if role_name in ROLE_PERMISSIONS:
            permissions_dict = {
                perm.value: True
                for perm in ROLE_PERMISSIONS[role_name]}
        else:
            permissions_dict = {}
        role_data = RoleAdd(
            name=role_name,
            description=data.description,
            permissions=permissions_dict)
        role = await self.db.roles.add(role_data)
        await self.db.commit()
        return role

    async def exit_role(self, role_name: str, data: RoleUpdate):
        await self.get_role_with_check(role_name)
        await self.db.roles.exit(data, exclude_unset=True, name=role_name)
        await self.db.commit()

    async def partial_change_role(self, role_name: str, data: RolePatch, exclude_unset: bool = False):
        role = await self.get_role_with_check(role_name)
        update_dict = {}
        if data.description is not None:
            update_dict["description"] = data.description

        if data.permissions is not None:
            current_permissions = role.permissions or {}
            current_permissions.update(data.permissions)
            update_dict["permissions"] = current_permissions

        if not update_dict:
            return
        update_data = RolePatch(**update_dict)

        await self.db.roles.exit(update_data, exclude_unset=exclude_unset, name=role_name)
        await self.db.commit()

    async def delete_role(self, role_name: str):
        try:
            await self.db.roles.delete_role_with_current_name(role_name)
        except ObjectNotFoundException:
            raise RoleNotExistsException

    async def get_role_with_check(self, role_name: str):
        try:
            return await self.db.roles.get_one(name=role_name)
        except ObjectNotFoundException:
            raise RoleNotExistsException

