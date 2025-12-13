from src.models import CategoryOrm
from src.repositories.base import BaseRepository
from src.schemas.categories import Category

class CategoriesRepository(BaseRepository):
    model = CategoryOrm
    schemas = Category
