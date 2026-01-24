from sqlalchemy import select
from pydantic import EmailStr
from sqlalchemy.exc import NoResultFound

from src.exceptions.exception import EmailNotRegisteredException, UserRoleNotAssignedException
from src.models import UserOrm, RoleOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User, UserWithHashedPassword


class UsersRepository(BaseRepository):
    model = UserOrm
    schemas = User

    async def get_with_hashed_password(self, email: EmailStr):
        query = select(UserOrm).filter_by(email=email)
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise EmailNotRegisteredException
        return UserWithHashedPassword.model_validate(model, from_attributes=True)

    async def get_current_user_role_for_permissions(self, user_id: int) -> dict:
        query = (
            select(RoleOrm.permissions)
            .join(UserOrm, UserOrm.role_id == RoleOrm.id)
            .filter(UserOrm.id == user_id)
        )
        result = await self.session.execute(query)
        permissions = result.scalar_one_or_none()
        if permissions is None:
            raise UserRoleNotAssignedException
        return permissions or {}

