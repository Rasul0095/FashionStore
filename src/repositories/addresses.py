from src.models import AddressOrm
from src.repositories.base import BaseRepository
from src.schemas.addresses import Address


class AddressesRepository(BaseRepository):
    model = AddressOrm
    schemas = Address
