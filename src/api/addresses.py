from fastapi import APIRouter, Body

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.addresses import AddressesAddRequest, AddressesUpdate, AddressesPatch
from src.services.addresses import AddressService

router = APIRouter(prefix="/addresses", tags=["Адреса"])

@router.get("")
async def get_addresses(db: DBDep):
    return await AddressService(db).get_addresses()


@router.get("/{user_id}")
async def get_address(db: DBDep, user_id: UserIdDep):
    return await AddressService(db).get_address(user_id)


@router.post("")
async def add_address(
    user_id: UserIdDep,
    db: DBDep,
    address_data: AddressesAddRequest = Body(
        openapi_examples={
            "Домашний адрес": {
                "value": {
                    "address_line": "ул. Ленина, д. 15, кв. 42",
                    "city": "Москва",
                    "postal_code": "125009",
                    "country": "Россия",
                }
            },
            "Рабочий адрес": {
                "value": {
                    "address_line": "пр. Мира, д. 100, офис 305",
                    "city": "Санкт-Петербург",
                    "postal_code": "190000",
                    "country": "Россия",
                }
            },
        }
    )):
    address = await AddressService(db).add_address(user_id, address_data)
    return {"status": "OK", "data": address}


@router.put("/{address_id}")
async def exit_address(
    address_id: int,
    user_id: UserIdDep,
    db: DBDep,
    address_data: AddressesUpdate,
):
    await AddressService(db).exit_address(address_id, user_id, address_data)
    return {"status": "OK"}


@router.patch("/{address_id}")
async def partial_change_address(
    address_id: int,
    user_id: UserIdDep,
    db: DBDep,
    address_data: AddressesPatch,
):
    await AddressService(db).partial_change_address(address_id, user_id, address_data, exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    user_id: UserIdDep,
    db: DBDep,
):
    await AddressService(db).delete_address(address_id, user_id)
    return {"status": "OK"}
