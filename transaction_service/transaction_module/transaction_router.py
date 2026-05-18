from fastapi import APIRouter, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from transaction_service.core.database import get_async_session
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest, TransactionResponse
from  transaction_service.transaction_module.transaction_manager import TransactionManager

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transaction_router.post(
    path="/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    request: CreateTransactionRequest,
    db: AsyncSession = Depends(get_async_session),
    authorization: str = Header(...)
):
    return await TransactionManager.create(db, request, authorization)



@transaction_router.get(
    path="/{tr_id}",
    response_model=TransactionResponse,
)
async def get_by_id(
    tr_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    return await TransactionManager.get_by_id(db, tr_id)


@transaction_router.get(
    path="/",
    response_model= list[TransactionResponse]
)
async def get_range(
    offset: int = 0,
    limit: int = 10,
    order_id: int = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_async_session)
):
    return await TransactionManager.get_range(db, offset, limit, order_id, user_id)