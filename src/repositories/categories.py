from src.models import CategoryOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CategoryDataMapper

class CategoriesRepository(BaseRepository):
    model = CategoryOrm
    mapper = CategoryDataMapper