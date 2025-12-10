from os import access

from passlib.context import CryptContext
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.schemas.users import UserAddRequest, UserAdd, UserLogin
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def get_me(self, user_id: int):
        user = await self.db.users.get_one_or_none(id=user_id)
        return {
            "id": user.id,
            "email": user.email,
            "role_id": user.role_id,
            "first_name": user.first_name,
            "last_name": user.last_name}

    async def register_user(self, data: UserAddRequest, role_name: str = "user"):
        if await self.db.users.get_by_email(data.email):
            raise ValueError("Такой email уже существует")

        role = await self.db.roles.get_by_name(role_name)
        if not role:
            raise ValueError(f"Роль '{role_name}' не существует")
        hashed_password = AuthService().hashed_password(data.password)
        user_data = UserAdd(
            role_id=role.id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow())
        await self.db.users.add(user_data)
        await self.db.commit()

    async def login_user(self, data: UserLogin):
        user = await self.db.users.get_with_hashed_password(email=data.email)
        tokens = self.create_tokens_pair({
            "user_id": user.id,
            "role_id": user.role_id,
            "email": user.email,})
        return tokens

    async def refresh_tokens(self, refresh_token: str):
        payload = self.verify_token_type(refresh_token, "refresh")
        user = await self.db.users.get_one(id=payload["user_id"])
        return self.create_tokens_pair({
            "user_id": user.id,
            "role_id": user.role_id,
            "email": user.email, })

    async def get_user_permissions(self, user_id: int):
        return await self.db.users.get_current_user_role_for_permissions(user_id)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp":expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_tokens_pair(self, data: dict):
        """Создает пару access + refresh токенов"""
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def verify_token_type(self, token: str, token_type: str = "access"):
        """Проверяет тип токена"""
        payload = self.decode_token(token)
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail=f"Недопустимый тип токена")
        return payload

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hashed_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")