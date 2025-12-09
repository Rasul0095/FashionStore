from src.models import RoleOrm
from src.repositories.base import BaseRepository
from src.schemas.roles import Role


class RolesRepository(BaseRepository):
    model = RoleOrm
    schemas = Role