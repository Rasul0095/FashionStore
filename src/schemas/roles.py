from typing import Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

from src.core.permissions import Permission


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

class RoleUpdate(BaseModel):
    description: str | None = Field(None)
    permissions: Optional[Dict[Permission, bool]] = Field(
        default=None,
        examples=[{
            "view_products": True,
            "view_orders": True,
            "manage_cart": True
        ,}],)

class RolePatch(BaseModel):
    description: str | None = Field(None)
    permissions: Optional[Dict[Permission, bool]] = Field(
        default=None,
        examples=[{
            "view_products": True,
            "view_orders": True,
            "manage_cart": True
        ,}],)
