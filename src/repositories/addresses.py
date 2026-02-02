from src.models import AddressOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import AddressDataMapper


class AddressesRepository(BaseRepository):
    model = AddressOrm
    mapper = AddressDataMapper
