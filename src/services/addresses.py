from src.api.dependencies import UserIdDep
from src.core.permissions import Permission
from src.exceptions.exception import (
    ObjectNotFoundException,
    AddressNotFoundException,
    PermissionDeniedHTTPException,
    AddressInUseHTTPException,
)
from src.schemas.addresses import (
    AddressesAddRequest,
    AddressesAdd,
    AddressesPatch,
    AddressesUpdate,
)
from src.services.auth import AuthService
from src.services.base import BaseService


class AddressService(BaseService):
    async def get_addresses(self):
        return await self.db.addresses.get_all()

    async def get_address(self, address_id: int, user_id: int):
        address = await self.get_address_with_check(address_id)
        # Проверяем что адрес принадлежит пользователю
        if address.user_id != user_id:
            # Проверяем есть ли право смотреть чужие адреса (админ/менеджер)
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        return address

    async def get_user_addresses(self, user_id: int, target_user_id: int = None):
        # Если не указан target_user_id, получаем свои адреса
        if target_user_id is None:
            return await self.db.addresses.get_filtered(user_id=user_id)

        # Проверяем права если запрашиваем чужие адреса
        if target_user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            # Админ/менеджер с VIEW_USERS может смотреть чужие адреса
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        return await self.db.addresses.get_filtered(user_id=target_user_id)

    async def add_address(self, user_id: UserIdDep, data: AddressesAddRequest):
        address_data = AddressesAdd(user_id=user_id, **data.model_dump())
        address = await self.db.addresses.add(address_data)
        await self.db.commit()
        return address

    async def exit_address(
        self, address_id: int, user_id: UserIdDep, data: AddressesUpdate
    ):
        address = await self.get_address_with_check(address_id)

        if address.user_id == user_id:
            # Владелец меняет свой адрес
            await self.db.addresses.exit(
                data,
                exclude_unset=True,
                id=address_id,
                user_id=user_id,  # защита: только свой
            )
            await self.db.commit()
            return

        permissions = await AuthService(self.db).get_user_permissions(user_id)
        if Permission.VIEW_USERS not in permissions:
            raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        # Админ меняет чужой адрес
        await self.db.addresses.exit(data, exclude_unset=True, id=address_id)
        await self.db.commit()

    async def partial_change_address(
        self,
        address_id: int,
        user_id: UserIdDep,
        data: AddressesPatch,
        exclude_unset: bool = False,
    ):
        address = await self.get_address_with_check(address_id)

        if address.user_id == user_id:
            # Владелец меняет свой адрес
            await self.db.addresses.exit(
                data,
                exclude_unset=exclude_unset,
                id=address_id,
                user_id=user_id,  # защита: только свой
            )
            await self.db.commit()
            return

        permissions = await AuthService(self.db).get_user_permissions(user_id)
        if Permission.VIEW_USERS not in permissions:
            raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        # Админ меняет чужой адрес
        await self.db.addresses.exit(data, exclude_unset=exclude_unset, id=address_id)
        await self.db.commit()

    async def delete_address(self, address_id: int, user_id: UserIdDep):
        address = await self.get_address_with_check(address_id)

        if address.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        orders_with_address = await self.db.orders.get_filtered(address_id=address_id)
        if orders_with_address:
            order_ids = [order.id for order in orders_with_address]
            raise AddressInUseHTTPException(order_ids)
        await self.db.addresses.delete(id=address_id)
        await self.db.commit()

    async def get_address_with_check(self, address_id: int):
        try:
            return await self.db.addresses.get_one(id=address_id)
        except ObjectNotFoundException:
            raise AddressNotFoundException
