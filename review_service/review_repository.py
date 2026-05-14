from typing import Optional, List
from models import Review
from database import db

class ReviewRepository:
    @staticmethod
    def create(review: Review):
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def find_by_id(review_id: int) -> Optional[Review]:
        return Review.query.get(review_id)

    @staticmethod
    def find_by_product_id(product_id: str) -> List[Review]:
        return Review.query.filter_by(product_id=product_id).all()

    @staticmethod
    def get_by_user_id(user_id: int) -> List[Review]:
        return Review.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_review(review: Review):
        updated_review = db.session.merge(review)
        db.session.commit()
        return updated_review

    @classmethod
    def delete_by_id(cls, review_id: int) -> bool:
        review: Review = cls.find_by_id(review_id)
        if review is None:
            return False

        db.session.delete(review)
        db.session.commit()
        return True
