from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from user_module.user_repository import UserRepository
from user_module.user_service import UserService
from user_module.user_schemas import UserRequest, UserResponse
from security.login_schemas import LoginRequest, LoginResponse
from core.database import get_async_session
from security.dependencies import get_current_user

from fastapi_auth_service.security.login_schemas import TokenClaims
from fastapi_auth_service.user_module.notifications import send_registration_email, send_security_alert, \
    send_cart_notification, send_order_cancel
from fastapi_auth_service.user_module.user_schemas import OrderCancelNotification, CartNotification

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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    user = await service.create(db, request)
    background_tasks.add_task(send_registration_email, user.username)

    return user

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


@user_router.post(path="/login/")
async def login(
    request: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    response = await service.login(db, request)
    background_tasks.add_task(send_security_alert, request.username)

    return response

@user_router.get("/me/", response_model=UserResponse)
async def get_my_profile(
    current_user: TokenClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    return await service.get_by_id(db, int(current_user.sub))

@user_router.post("/internal/notify-cart/")
async def notify_cart_addition(
    data: CartNotification,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_cart_notification, data.username, data.product_name)
    return {"status": "notification_queued"}


@user_router.post("/internal/notify-cancel-order/")
async def notify_order_cancel(
    data: OrderCancelNotification,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_order_cancel, data.username, data.order_id)
    return {"status": "ok"}