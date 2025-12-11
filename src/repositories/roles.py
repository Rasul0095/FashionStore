from sqlalchemy import select

from src.models import RoleOrm
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