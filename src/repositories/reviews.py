from src.repositories.base import BaseRepository
from src.models.reviews import ReviewOrm
from src.schemas.reviews import Review


class ReviewsRepository(BaseRepository):
    model = ReviewOrm
    schemas = Review
