from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import UserIdDep
from src.schemas.addresses import AddressesAddRequest, AddressesAdd, AddressesUpdate, AddressesPatch
from src.services.base import BaseService


class AddressService(BaseService):
    async def get_addresses(self):
        return await self.db.addresses.get_all()

    async def get_address(self, user_id: int):
        return await self.db.addresses.get_filtered(user_id=user_id)

    async def add_address(self, user_id: UserIdDep, data: AddressesAddRequest):
        address_data = AddressesAdd(
            user_id=user_id, **data.model_dump()
        )
        address = await self.db.addresses.add(address_data)
        await self.db.commit()
        return address

    async def exit_address(self, address_id: int, user_id: UserIdDep, data: AddressesUpdate):
        try:
            await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        await self.db.addresses.exit(
            data,
            exclude_unset=True,
            id=address_id,
            user_id=user_id)
        await self.db.commit()

    async def partial_change_address(self,
        address_id: int,
        user_id: UserIdDep,
        data: AddressesPatch,
        exclude_unset: bool = False):
        try:
            await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        await self.db.addresses.exit(
            data,
            exclude_unset=exclude_unset,
            id=address_id,
            user_id=user_id)
        await self.db.commit()

    async def delete_address(self, address_id: int, user_id: UserIdDep):
        try:
            await self.db.addresses.get_one(id=address_id, user_id=user_id)
        except NoResultFound:
            raise HTTPException(404, "Адрес не найден или доступ запрещен")

        await self.db.addresses.delete(id=address_id, user_id=user_id)
        await self.db.commit()