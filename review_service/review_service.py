from typing import Optional, List
from models import Review
from database import db
from review_service.review_repository import ReviewRepository
from schemas import ReviewCreateRequest, ReviewUpdateRequest
import httpx

# где-то тут надо будет добавить проверку существования пользователей и товаров
# обращением к другим сервисам

class ReviewService:
    DJANGO_API_URL = "http://localhost:8080/api/product/"

    @staticmethod
    async def verify_product_exists(product_id: int) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{ReviewService.DJANGO_API_URL}{product_id}/")
                return response.status_code == 200
            except httpx.RequestError:
                return False

    @staticmethod
    async def verify_user_exists(user_id: int) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8001/users/{user_id}/", timeout=5)
                return response.status_code == 200
        except httpx.RequestError:
            return False

    @staticmethod
    async def create(data, user_id: int) -> Optional[Review]:
        if not await ReviewService.verify_product_exists(data.product_id):
            return None
        if not await ReviewService.verify_user_exists(user_id):
            return None

        new_review = Review(
            product_id=data.product_id,
            user_id=user_id,
            text=data.text,
            rating=data.rating,
            status='active'
        )
        return ReviewRepository.create(new_review)

    @staticmethod
    def find_by_id(review_id: int) -> Optional[Review]:
        return Review.query.get(review_id)

    @staticmethod
    def find_by_product_id(product_id: int) -> List[Review]:
        return Review.query.filter_by(product_id=product_id, status='active').all()

    @staticmethod
    def get_by_user_id(user_id: int) -> List[Review]:
        return Review.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_review(data, review_id: int, user_id: int) -> Optional[Review]:
        review = Review.query.get(review_id)
        if not review or review.user_id != user_id or review.status == 'deleted':
            return None

        review.text = data.text
        review.rating = data.rating
        db.session.commit()

        return review


    @classmethod
    def delete_by_id(cls, review_id: int, user_id: int, is_admin: bool) -> bool:
        review = Review.query.get(review_id)
        if not review or review.status == 'deleted':
            return False

        if is_admin or review.user_id == user_id:
            review.status = 'deleted'
            db.session.commit()
            return True

        return False
