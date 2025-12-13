from src.models import AddressOrm
from src.repositories.base import BaseRepository
from src.schemas.addresses import Addresses


class AddressesRepository(BaseRepository):
    model = AddressOrm
    schemas = Addresses
