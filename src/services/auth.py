from passlib.context import CryptContext
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp":expire})
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
            raise HTTPException(status_code=401, detail=f"Invalid token type")
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