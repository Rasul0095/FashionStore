from pydantic import BaseModel
from enum import Enum

class RoleName(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class RoleAdd(BaseModel):
    name: RoleName
    description: str | None = None
    permissions: dict = {}

class Role(RoleAdd):
    id: int
