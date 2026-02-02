from src.models import BrandOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BrandDataMapper


class BrandsRepository(BaseRepository):
    model = BrandOrm
    mapper = BrandDataMapper
