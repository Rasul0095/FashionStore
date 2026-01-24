from fastapi import APIRouter, Body, Query

from src.api.dependencies import DBDep, require_permission
from src.core.permissions import Permission
from src.exceptions.exception import AddressNotFoundException, AddressNotFoundHTTPException
from src.schemas.addresses import AddressesAddRequest, AddressesUpdate, AddressesPatch
from src.services.addresses import AddressService

router = APIRouter(prefix="/addresses", tags=["Адреса"])

@router.get("")
async def get_addresses(
    db: DBDep,
    user_id: int  = require_permission(Permission.VIEW_ADDRESSES),
    target_user_id: int | None = Query(None, description="ID пользователя (только для админов)")
):
    return await AddressService(db).get_user_addresses(user_id, target_user_id)


@router.get("/{address_id}")
async def get_address(
    db: DBDep,
    address_id: int,
    user_id: int = require_permission(Permission.VIEW_ADDRESSES)):
    try:
        return await AddressService(db).get_address(address_id, user_id)
    except AddressNotFoundException:
        raise AddressNotFoundHTTPException


@router.post("")
async def add_address(
    db: DBDep,
    user_id: int = require_permission(Permission.MANAGE_ADDRESSES),
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
    db: DBDep,
    address_id: int,
    address_data: AddressesUpdate,
    user_id: int = require_permission(Permission.MANAGE_ADDRESSES),
):
    try:
        await AddressService(db).exit_address(address_id, user_id, address_data)
    except AddressNotFoundException:
        raise AddressNotFoundHTTPException
    return {"status": "OK"}


@router.patch("/{address_id}")
async def partial_change_address(
    address_id: int,
    db: DBDep,
    address_data: AddressesPatch,
    user_id: int = require_permission(Permission.MANAGE_ADDRESSES),

):
    try:
        await AddressService(db).partial_change_address(address_id, user_id, address_data, exclude_unset=True)
    except AddressNotFoundException:
        raise AddressNotFoundHTTPException
    return {"status": "OK"}


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    db: DBDep,
    user_id: int = require_permission(Permission.DELETE_ADDRESSES),
):
    try:
        await AddressService(db).delete_address(address_id, user_id)
    except AddressNotFoundException:
        raise AddressNotFoundHTTPException
    return {"status": "OK"}
