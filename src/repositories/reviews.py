from src.repositories.base import BaseRepository
from src.models.reviews import ReviewOrm
from src.repositories.mappers.mappers import ReviewDataMapper


class ReviewsRepository(BaseRepository):
    model = ReviewOrm
    mapper = ReviewDataMapper
