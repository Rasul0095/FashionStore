from fastapi import APIRouter, Body, UploadFile, File, Query

from src.api.dependencies import DBDep, UserIdDep, require_permission
from src.core.permissions import Permission
from src.schemas.reviews import ReviewsAddRequest, ReviewsPatch
from src.services.reviews import ReviewService


router = APIRouter(prefix="/reviews", tags=["Отзывы и рейтинги"])

@router.get("")
async def get_reviews(
    db:DBDep,
    user_id: int = require_permission(Permission.VIEW_REVIEWS),
    target_user_id: int | None = Query(None, description="ID пользователя (только для админов)")
):
    return await ReviewService(db).get_user_reviews(user_id, target_user_id)


@router.get("/{review_id}")
async def get_review(
    db:DBDep,
    review_id: int,
    user_id: int = require_permission(Permission.VIEW_REVIEWS)):
    return await ReviewService(db).get_review(review_id, user_id)


@router.post("")
async def add_review(
    db: DBDep,
    product_id: int,
    review_data: ReviewsAddRequest = Body(
        openapi_examples={
            "Положительный отзыв": {
                "summary": "Высокая оценка товара",
                "value": {
                    "rating": 5,
                    "comment": "Отличный товар, всем рекомендую! Качество на высоте."
                }
            },
            "Средний отзыв": {
                "summary": "Нейтральная оценка",
                "value": {
                    "rating": 3,
                    "comment": "Нормальный товар, но есть небольшие недочёты."
                }
            },
            "Негативный отзыв": {
                "summary": "Низкая оценка",
                "value": {
                    "rating": 1,
                    "comment": "Товар не соответствует описанию, качество плохое."
                }
            }
        }
    ),
    user_id: int = require_permission(Permission.CREATE_REVIEWS),

):
    review = await ReviewService(db).add_review(user_id, product_id, review_data)
    return {"status": "OK", "data": review}


@router.post("/{review_id}/images-reviews")
async def add_review_images(
    db: DBDep,
    review_id: int,
    images: list[UploadFile] = File(..., description="Список изображений отзыва"),
    user_id: int = require_permission(Permission.MODERATE_REVIEWS),

):
    await ReviewService(db).add_review_images(user_id, review_id, images)
    return {
        "status": "OK",
        "message": f"Загрузка {len(images)} изображений начата",
        "product_id": review_id}


@router.put("/{review_id}")
async def exit_review(
    db: DBDep,
    review_id: int,
    review_data: ReviewsPatch,
    user_id: int = require_permission(Permission.MODERATE_REVIEWS),

):
    await ReviewService(db).update_review(user_id, review_id, review_data)
    return {"status": "OK"}


@router.patch("/{review_id}")
async def partial_change_review(
    db: DBDep,
    review_id: int,
    review_data: ReviewsPatch,
    user_id: int = require_permission(Permission.MODERATE_REVIEWS),

):
    await ReviewService(db).update_review(user_id, review_id, review_data, exclude_unset=True)
    return {"status": "OK"}


@router.delete("/{review_id}")
async def delete_review(
    db: DBDep,
    review_id: int,
    user_id: int = require_permission(Permission.DELETE_REVIEWS),
):
    await ReviewService(db).delete_review(review_id)
    return {"status": "OK"}
