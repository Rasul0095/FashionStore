from src.core.permissions import ROLE_PERMISSIONS
from src.services.base import BaseService
from src.schemas.roles import RoleAdd


class RoleService(BaseService):
    async def get_roles(self):
        return await self.db.roles.get_all()

    async def get_role(self, role_name: str):
        return await self.db.roles.get_one(name=role_name)

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