from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserAddRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    role_id: int
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    created_at: datetime


class UserMeResponse(BaseModel):
    id: int
    role_id: int
    first_name: str
    last_name: str
    email: EmailStr


class User(BaseModel):
    id: int
    role_id: int
    first_name: str
    last_name: str
    email: EmailStr


class UserWithHashedPassword(User):
    hashed_password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = Field(None, description="Только для админов")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role_id: int


class RefreshRequest(BaseModel):
    refresh_token: str
