from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UserIdDep
from src.core.permissions import Permission
from src.schemas.addresses import AddressesAddRequest, AddressesAdd, AddressesUpdate, AddressesPatch
from src.services.base import BaseService


class AddressService(BaseService):
    async def get_addresses(self):
        return await self.db.addresses.get_all()

    async def get_address(self, address_id: int, user_id: int):
        try:
            address = await self.db.addresses.get_one(id=address_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден")

        # Проверяем что адрес принадлежит пользователю
        if address.user_id != user_id:
            # Проверяем есть ли право смотреть чужие адреса (админ/менеджер)
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise HTTPException(403, "Нет доступа к этому адресу")

        return address

    async def get_user_addresses(self, user_id: int, target_user_id: int = None):
        # Если не указан target_user_id, получаем свои адреса
        if target_user_id is None:
            return await self.db.addresses.get_filtered(user_id=user_id)

        # Проверяем права если запрашиваем чужие адреса
        if target_user_id != user_id:
            permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
            # Админ/менеджер с VIEW_USERS может смотреть чужие адреса
            if Permission.VIEW_USERS.value not in permissions:
                raise HTTPException(403, "Недостаточно прав для просмотра чужих адресов")

        return await self.db.addresses.get_filtered(user_id=target_user_id)

    async def add_address(self, user_id: UserIdDep, data: AddressesAddRequest):
        address_data = AddressesAdd(
            user_id=user_id, **data.model_dump()
        )
        address = await self.db.addresses.add(address_data)
        await self.db.commit()
        return address

    async def exit_address(self, address_id: int, user_id: UserIdDep, data: AddressesPatch):
        try:
            address = await self.db.addresses.get_one(id=address_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        if address.user_id == user_id:
            # Владелец меняет свой адрес
            await self.db.addresses.exit(
                data,
                exclude_unset=True,
                id=address_id,
                user_id=user_id  # защита: только свой
            )
            await self.db.commit()
            return

        permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
        if Permission.VIEW_USERS not in permissions:
            raise HTTPException(403, "Недостаточно прав для редактирования чужого адреса")

        # Админ меняет чужой адрес
        await self.db.addresses.exit(
            data,
            exclude_unset=True,
            id=address_id
        )
        await self.db.commit()

    async def partial_change_address(self,
        address_id: int,
        user_id: UserIdDep,
        data: AddressesPatch,
        exclude_unset: bool = False):
        try:
            address = await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        if address.user_id == user_id:
            # Владелец меняет свой адрес
            await self.db.addresses.exit(
                data,
                exclude_unset=exclude_unset,
                id=address_id,
                user_id=user_id  # защита: только свой
            )
            await self.db.commit()
            return

        permissions = await self.db.users.get_current_user_role_for_permissions(user_id)
        if Permission.VIEW_USERS not in permissions:
            raise HTTPException(403, "Недостаточно прав для редактирования чужого адреса")

        # Админ меняет чужой адрес
        await self.db.addresses.exit(
            data,
            exclude_unset=exclude_unset,
            id=address_id
        )
        await self.db.commit()

    async def delete_address(self, address_id: int, user_id: UserIdDep):
        try:
            await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        await self.db.addresses.delete(id=address_id, user_id=user_id)
        await self.db.commit()