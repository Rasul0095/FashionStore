from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserAddRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    created_at: datetime

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

class RefreshRequest(BaseModel):
    refresh_token: str
