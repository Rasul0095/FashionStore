from fastapi import UploadFile
from datetime import datetime

from src.core.permissions import Permission
from src.exceptions.exception import PermissionDeniedHTTPException, ObjectNotFoundException, ReviewNotFoundException
from src.repositories.utils import save_uploaded_files
from src.schemas.reviews import ReviewsAddRequest, ReviewsAdd, ReviewImagesUpdate, ReviewsPatch
from src.services.auth import AuthService
from src.services.base import BaseService
from src.api.dependencies import UserIdDep
from src.services.products import ProductService


class ReviewService(BaseService):
    async def get_user_reviews(self, user_id: int, target_user_id: int = None):
        if target_user_id is None:
            return await self.db.reviews.get_filtered(user_id=user_id)

        if target_user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS.value not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        return await self.db.reviews.get_filtered(user_id=target_user_id)

    async def get_review(self, review_id: int, user_id: int):
        review = await self.get_review_with_check(review_id)

        if review.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            # Админ/менеджер может смотреть все отзывы
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        return review

    async def add_review(self, user_id: UserIdDep, product_id: int, data: ReviewsAddRequest):
        await ProductService(self.db).get_product_with_check(product_id)
        review_data = ReviewsAdd(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.utcnow(),
            **data.model_dump(),)
        review = await self.db.reviews.add(review_data)
        await self.db.commit()
        return review

    async def add_review_images(self, user_id: UserIdDep, review_id: int, images: list[UploadFile]):
        review = await self.get_review_with_check(review_id)
        if review.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        saved_paths = await save_uploaded_files(
            files=images,
            prefix=f"review_{review_id}",
            upload_dir="src/static/images-reviews")

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
        review = await self.get_review_with_check(review_id)
        if review.user_id == user_id:
            # Владелец меняет свой адрес
            await self.db.reviews.exit(
                data,
                exclude_unset=exclude_unset,
                id=review_id,
                user_id=user_id
            )
            await self.db.commit()
            return

        permissions = await AuthService(self.db).get_user_permissions(user_id)
        if Permission.VIEW_USERS not in permissions:
            raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)

        await self.db.reviews.exit(data, exclude_unset=exclude_unset, id=review_id, user_id=user_id)
        await self.db.commit()

    async def delete_review(self, review_id: int, user_id: UserIdDep):
        review = await self.get_review_with_check(review_id)
        if review.user_id != user_id:
            permissions = await AuthService(self.db).get_user_permissions(user_id)
            if Permission.VIEW_USERS not in permissions:
                raise PermissionDeniedHTTPException(Permission.VIEW_USERS.value)
        if review.images:
            import os
            for image_path in review.images:
                if os.path.exists(image_path):
                    os.remove(image_path)
        await self.db.reviews.delete(id=review_id)
        await self.db.commit()

    async def get_review_with_check(self, review_id: int):
        try:
            return await self.db.reviews.get_one(id=review_id)
        except ObjectNotFoundException:
            raise ReviewNotFoundException




