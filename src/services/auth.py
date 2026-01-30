from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.core.permissions import Permission
from src.exceptions.exception import ObjectAlreadyExistsException, UserAlreadyExistsException, \
    RoleNotExistsException, EmailNotRegisteredException, IncorrectPasswordException, UserRoleNotAssignedException, \
    UserRoleNotAssignedHTTPException, TokenExpiredHTTPException, IncorrectTokenHTTPException, \
    WrongTokenTypeHTTPException, ObjectNotFoundException, \
    PermissionDeniedHTTPException, CannotDeleteSelfHTTPException, UserNotFoundHTTPException
from src.schemas.users import UserAddRequest, UserAdd, UserLogin, UserUpdate
from src.services.base import BaseService
from src.services.roles import RoleService


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
        role = await RoleService(self.db).get_role_with_check(role_name)
        hashed_password = AuthService().hashed_password(data.password)
        user_data = UserAdd(
            role_id=role.id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow())
        try:
            await self.db.users.add(user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as ex:
            raise UserAlreadyExistsException from ex

    async def login_user(self, data: UserLogin):
        user = await self.db.users.get_with_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException
        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException
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
        try:
            return await self.db.users.get_current_user_role_for_permissions(user_id)
        except UserRoleNotAssignedException:
            raise UserRoleNotAssignedHTTPException

    async def get_user_with_check(self, user_id: int):
        try:
            return await self.db.users.get_one(id=user_id)
        except ObjectNotFoundException:
            raise UserNotFoundHTTPException

    async def update_user(self, user_id: int, data: UserUpdate, current_user_id: int):
        # Проверяем что пользователь существует
        await self.get_user_with_check(user_id)
        if user_id != current_user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(current_user_id)
            if Permission.EDIT_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.EDIT_USERS.value)

        if data.role_id is not None:
            permissions = await self.db.users.get_current_user_role_for_permissions(current_user_id)
            if Permission.EDIT_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.EDIT_USERS.value)

        try:
            await self.db.roles.get_one(id=data.role_id)
        except ObjectNotFoundException:
            raise RoleNotExistsException
        await self.db.users.exit(data, exclude_unset=True, id=user_id)
        await self.db.commit()

    async def delete_user(self, user_id: int, current_user_id: int):
        if user_id == current_user_id:
            raise CannotDeleteSelfHTTPException
        permissions = await self.db.users.get_current_user_role_for_permissions(current_user_id)
        if Permission.DELETE_USERS.value not in permissions:
            raise PermissionDeniedHTTPException(Permission.DELETE_USERS.value)
        await self.get_user_with_check(user_id)
        # 1. Удалить заказы пользователя
        orders = await self.db.orders.get_filtered(user_id=user_id)
        for order in orders:
            # Удалить товары в заказах
            await self.db.order_items.delete(order_id=order.id)
            # Удалить сам заказ
            await self.db.orders.delete(id=order.id)
        # 2. Удалить адреса
        await self.db.addresses.delete(user_id=user_id)
        # 3. Удалить корзину
        cart = await self.db.carts.get_one_or_none(user_id=user_id)
        if cart:
            await self.db.cart_items.delete(cart_id=cart.id)
            await self.db.carts.delete(id=cart.id)
        # 4. Удалить отзывы
        await self.db.reviews.delete(user_id=user_id)
        # 5. Удалить пользователя
        await self.db.users.delete(id=user_id)
        await self.db.commit()

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
            raise WrongTokenTypeHTTPException
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
        except jwt.ExpiredSignatureError:
            raise TokenExpiredHTTPException
        except jwt.DecodeError:
            raise IncorrectTokenHTTPException