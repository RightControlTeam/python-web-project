from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from transaction_service.core.logger import logger
from transaction_service.user_module.user_repository import UserRepository
from transaction_service.user_module.user_service import UserService
from transaction_service.user_module.user_schemas import UserRequest, UserResponse
from transaction_service.security.login_schemas import LoginRequest, LoginResponse
from transaction_service.core.database import get_async_session
from transaction_service.security.dependencies import get_current_user
from transaction_service.security.login_schemas import TokenClaims

from .notifications import (
    send_registration_email,
    send_security_alert,
    send_cart_notification,
    send_order_cancel
)

from .user_schemas import OrderCancelNotification, CartNotification

from transaction_service.user_module.user_schemas import UserUpdateRequest

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
    logger.info(f" Создан новый пользователь: {user.username}")
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


@user_router.post(
    path="/login/",
    response_model=LoginResponse
)
async def login(
    request: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    response = await service.login(db, request)
    logger.info(f" Пользователь {request.username} вошел в систему")
    background_tasks.add_task(send_security_alert, request.username)

    return response


@user_router.get("/me/", response_model=UserResponse)
async def get_my_profile(
    current_user: TokenClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service)
):
    logger.info(f"Пользователь ID {current_user.sub} получает данные профиля")
    return await service.get_by_id(db, int(current_user.sub))


@user_router.post("/internal/notify-cart/")
async def notify_cart_addition(
    data: CartNotification,
    background_tasks: BackgroundTasks
):
    logger.info(f"Добавлен новый товар {data.product_name} в корзину  пользователя {data.username}")
    background_tasks.add_task(send_cart_notification, data.username, data.product_name)
    return {"status": "notification_queued"}


@user_router.post("/internal/notify-cancel-order/")
async def notify_order_cancel(
    data: OrderCancelNotification,
    background_tasks: BackgroundTasks
):
    logger.info(f"Отмену заказа №{data.order_id} для {data.username}")
    background_tasks.add_task(send_order_cancel, data.username, data.order_id)
    return {"status": "ok"}

@user_router.delete(path="/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        current_user: TokenClaims = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
        service: UserService = Depends(get_user_service),
):
    user_id = int(current_user.sub)
    await service.delete(db, user_id)
    logger.info(f" Пользователь удалён")

@user_router.put(path="/")
async def update_user(
    request: UserUpdateRequest,
    current_user: TokenClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    service: UserService = Depends(get_user_service),
):
    user_id = int(current_user.sub)
    updated_user = await service.update(db, request, user_id)
    logger.info("Данные обновлены")
    return updated_user
