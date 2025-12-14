from src.models import BrandOrm
from src.repositories.base import BaseRepository
from src.schemas.brands import Brand

class BrandsRepository(BaseRepository):
    model = BrandOrm
    schemas = Brand
