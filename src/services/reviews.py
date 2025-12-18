import uuid
from datetime import datetime
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import NoResultFound

from src.schemas.reviews import ReviewsAddRequest, ReviewsAdd, ReviewImagesUpdate, ReviewsPatch
from src.services.base import BaseService
from src.api.dependencies import UserIdDep


class ReviewService(BaseService):
    async def get_reviews(self):
        return await self.db.reviews.get_all()

    async def get_review(self, user_id: UserIdDep):
        return await self.db.reviews.get_filtered(user_id=user_id)

    async def add_review(self, user_id: UserIdDep, product_id: int, data: ReviewsAddRequest):
        try:
            await self.db.products.get_one(id=product_id)
        except NoResultFound:
            raise HTTPException(404, "Товар не найден")

        review_data = ReviewsAdd(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.utcnow(),
            **data.model_dump(),)
        review = await self.db.reviews.add(review_data)
        await self.db.commit()
        return review

    async def add_review_images(self, user_id: UserIdDep, review_id: int, images: list[UploadFile]):
        try:
            await self.db.reviews.get_one(id=review_id)
        except NoResultFound:
            raise HTTPException(404, "Отзыв не найден")

        UPLOAD_DIR = Path("src/static/images-reviews")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        # Сохраняем файлы локально
        saved_paths = []
        for img in images:
            data = await img.read()
            ext = Path(img.filename).suffix or '.jpg'
            unique_name = f"{review_id}_{uuid.uuid4()}{ext}"
            file_path = UPLOAD_DIR / unique_name

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)

            saved_paths.append(str(file_path))
        update_images = ReviewImagesUpdate(images=saved_paths)

        await self.db.reviews.exit(
            update_images,
            user_id=user_id,
            exclude_unset=True,
            id=review_id,
        )
        await self.db.commit()

        return {"saved_paths": saved_paths, "product_id": review_id}

    async def update_review(self,
        user_id: UserIdDep,
        review_id: int,
        data: ReviewsPatch,
        exclude_unset: bool = False):
        try:
            await self.db.reviews.get_one(id=review_id)
        except NoResultFound:
            raise HTTPException(404, "Отзыв не найден")

        await self.db.reviews.exit(data, exclude_unset=exclude_unset, id=review_id, user_id=user_id)
        await self.db.commit()

    async def delete_review(self, review_id: int):
        try:
            review = await self.db.reviews.get_one(id=review_id)
        except NoResultFound:
            raise HTTPException(404, "Отзыв не найден")

        if review.images:
            import os
            for image_path in review.images:
                if os.path.exists(image_path):
                    os.remove(image_path)

        await self.db.reviews.delete(id=review_id)
        await self.db.commit()




