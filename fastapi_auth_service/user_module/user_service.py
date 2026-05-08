from sqlalchemy.ext.asyncio import AsyncSession

from user_module.user_repository import UserRepository
from user_module.user_schemas import UserRequest, UserResponse
from user_module.user import User
from user_module.user_mapper import user_to_response, user_from_request

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create(self, db: AsyncSession, request: UserRequest) -> UserResponse:
        user: User = user_from_request(request)
        await self.repository.create(db, user)
        return user_to_response(user)

    async def get_by_id(self, db: AsyncSession, user_id: int) -> UserResponse:
        user: User = await self.repository.get_by_id(db, user_id)
        return user_to_response(user)

    async def get_range(self, db: AsyncSession, offset: int = 0, limit: int = 10) -> list[UserResponse]:
        users: list[User] = await self.repository.get_range(db, offset, limit)
        return [user_to_response(i) for i in users]