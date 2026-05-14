from typing import Optional, List
from models import Review
from schemas import ReviewCreateRequest, ReviewUpdateRequest
from review_repository import ReviewRepository

# где-то тут надо будет добавить проверку существования пользователей и товаров
# обращением к другим сервисам

class ReviewService:
    @staticmethod
    def create(review_create_request: ReviewCreateRequest, user_id: int) -> Review:
        # создаем объект review, добавляем данные из запроса, добавляем id пользователя
        # id берем из токена
        ...

    @staticmethod
    def find_by_id(review_id: int) -> Optional[Review]:
        ...

    @staticmethod
    def find_by_product_id(product_id: int) -> List[Review]:
        ...

    @staticmethod
    def get_by_user_id(user_id: int) -> List[Review]:
        ...

    @staticmethod
    def update_review(review_update_request: ReviewUpdateRequest, review_id: int, user_id: int) -> Review:
        # в отличие от delete админ не должен уметь редактировать чужие отзывы
        # получаем отзыв по его id, сверяем id пользователя, обновляем дынные
        # id пользователя берем из токена, id отзыва из маршрута
        # делаем Update запрос в репозиторий
        ...

    @classmethod
    def delete_by_id(cls, review_id: int, user_id: int, is_admin: bool) -> bool:
        # true если удаление успешно, false если нет (отзыв не существует или уже удален)
        # надо учесть что админ может удалять чужие отзывы
        # передаем сюда, является ли пользователь админом и его id (все из токена берем в роутере)
        # как и в update cначала получаем отзыв по id и сверяемся
        ...
