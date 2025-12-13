from typing import Optional
from pydantic import BaseModel

class AddressesAddRequest(BaseModel):
    address_line: str
    city: str
    postal_code: str
    country: str

class AddressesAdd(BaseModel):
    user_id: int
    address_line: str
    city: str
    postal_code: str
    country: str

class Address(AddressesAdd):
    id: int

class AddressesUpdate(BaseModel):
    address_line: str
    city: str
    postal_code: str
    country: str

class AddressesPatch(BaseModel):
    address_line: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

