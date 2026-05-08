from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from user_module.user_repository import UserRepository
from user_module.user_service import UserService
from user_module.user_schemas import UserRequest, UserResponse
from core.database import get_async_session

user_router = APIRouter(prefix="/users", tags=["users"])

async def get_user_service() -> UserService:
    repository = UserRepository()
    return UserService(repository)

@user_router.post(
    path="/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: UserRequest,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    return await service.create(db, request)


@user_router.get(
    path="/{user_id}",
    response_model=UserResponse,
)
async def get_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    return await service.get_by_id(db, user_id)


@user_router.get(
    path="/",
    response_model= list[UserResponse],
)
async def get_range(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    return await service.get_range(db, offset, limit)

