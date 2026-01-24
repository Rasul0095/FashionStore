from sqlalchemy import select, delete, func

from src.exceptions.exception import  ObjectNotFoundException, UnableDeleteRoleHTTPException
from src.models import RoleOrm, UserOrm
from src.repositories.base import BaseRepository
from src.schemas.roles import Role


class RolesRepository(BaseRepository):
    model = RoleOrm
    schemas = Role

    async def get_by_name(self, role_name: str):
        query = (
            select(RoleOrm)
            .filter(RoleOrm.name == role_name)
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def delete_role_with_current_name(self, role_name: str):
        # 1. Найти роль
        role = await self.get_one(name=role_name)
        if not role:
            raise ObjectNotFoundException

        # 2. Проверить, есть ли пользователи с этой ролью
        users_count = await self.session.scalar(
            select(func.count()).select_from(UserOrm).where(UserOrm.role_id == role.id)
        )

        if users_count > 0:
            raise UnableDeleteRoleHTTPException

        stmt = delete(self.model).filter(self.model.id == role.id)
        await self.session.execute(stmt)
        await self.session.commit()