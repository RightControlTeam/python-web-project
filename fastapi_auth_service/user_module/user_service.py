from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from fastapi_auth_service.user_module.user_repository import UserRepository
from fastapi_auth_service.user_module.user_schemas import UserRequest, UserResponse, UserUpdateRequest
from fastapi_auth_service.security.login_schemas import LoginRequest, LoginResponse
from fastapi_auth_service.security.password_hashing import verify_password
from fastapi_auth_service.security.token import generate_login_response
from fastapi_auth_service.user_module.user import User
from fastapi_auth_service.user_module.user_mapper import user_to_response, user_from_request
from fastapi_auth_service.security.password_hashing import hash_password


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create(self, db: AsyncSession, request: UserRequest) -> UserResponse:
        existing_user: User = await self.repository.get_by_username(db, request.username)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with username \"{request.username}\" already exists"
            )
        user: User = user_from_request(request)
        await self.repository.create(db, user)
        return user_to_response(user)


    async def get_by_id(self, db: AsyncSession, user_id: int) -> UserResponse:
        user: User = await self.repository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} does not exist"
            )
        return user_to_response(user)

    async def get_range(self, db: AsyncSession, offset: int = 0, limit: int = 10) -> list[UserResponse]:
        users: list[User] = await self.repository.get_range(db, offset, limit)
        return [user_to_response(i) for i in users]

    async def login(self, db: AsyncSession, request: LoginRequest) -> LoginResponse:
        user: User = await self.repository.get_by_username(db, request.username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username {request.username} does not exist"
            )
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Incorrect password"
            )
        return generate_login_response(user.id)

    async def delete(self, db: AsyncSession, user_id: int):
        user = await self.repository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} does not exist"
            )
        await self.repository.delete(db, user_id)
        return None

    async def update(self, db: AsyncSession, request: UserUpdateRequest, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User does not exist"
            )
        if request.username is not None:
            if request.username != user.username:
                existing_user: User = await self.repository.get_by_username(db, request.username)
                if existing_user is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"User with username \"{request.username}\" already exists"
                    )
            user.username=request.username
        if request.password is not None:
            user.password_hash=hash_password(request.password)
        await self.repository.update(db, user)
        return user_to_response(user)

