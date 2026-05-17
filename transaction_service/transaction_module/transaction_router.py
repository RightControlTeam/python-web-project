from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from transaction_service.core.database import get_async_session
from transaction_service.security.dependencies import get_current_user
from shared.jwt_module import TokenClaims

from transaction_service.transaction_module.transaction import Transaction
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transaction_router.post(
    path="/",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    request: CreateTransactionRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: TokenClaims = Depends(get_current_user)
):
    ...

@transaction_router.get(
    path="/{user_id}",
    response_model=Transaction,
)
async def get_by_id(
    transaction_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    ...

@transaction_router.get(
    path="/",
    response_model= list[Transaction]
)
async def get_range(
    offset: int = 0,
    limit: int = 10,
    order_id: int = None,
    db: AsyncSession = Depends(get_async_session),
):
    ...



