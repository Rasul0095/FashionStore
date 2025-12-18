from pydantic import BaseModel
from datetime import datetime

class ReviewsAddRequest(BaseModel):
    rating: int
    comment: str | None
    images: list[str] = []

class ReviewsAdd(BaseModel):
    user_id: int
    product_id: int
    rating: int
    comment: str | None
    images: list[str] | None = []
    created_at: datetime

class Review(ReviewsAdd):
    id: int

class ReviewImagesUpdate(BaseModel):
    images: list[str]

class ReviewsPatch(BaseModel):
    rating: int | None = None
    comment: str | None = None
    images: list[str] | None = None