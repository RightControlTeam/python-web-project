from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from transaction_service.core.database import get_async_session
from transaction_service.security.dependencies import get_current_user
from shared.jwt_module import TokenClaims

from transaction_service.transaction_module.transaction import Transaction
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest, TransactionResponse
from transaction_service.transaction_module.transaction_repository import TransactionRepository

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])
transaction_repo = TransactionRepository()


@transaction_router.post(
    path="/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    request: CreateTransactionRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: TokenClaims = Depends(get_current_user)
):
    user_id_from_token = int(current_user.sub)
    
    transaction = Transaction(
        order_id=request.order_id,
        user_id=user_id_from_token,
        cost=request.cost,
        is_success=False
    )
    
    created = await transaction_repo.create(db, transaction)
    
    return TransactionResponse(
        id=created.id,
        order_id=created.order_id,
        user_id=created.user_id,
        cost=created.cost,
        is_success=created.is_success
    )

@transaction_router.get(
    path="/{transaction_id}",
    response_model=TransactionResponse,
)
async def get_by_id(
    transaction_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: TokenClaims = Depends(get_current_user),
):
    transaction = await transaction_repo.get_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    user_id_from_token = int(current_user.sub)
    if transaction.user_id != user_id_from_token:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TransactionResponse(
        id=transaction.id,
        order_id=transaction.order_id,
        user_id=transaction.user_id,
        cost=transaction.cost,
        is_success=transaction.is_success
    )

@transaction_router.get(
    path="/",
    response_model= list[TransactionResponse]
)
async def get_range(
    offset: int = 0,
    limit: int = 10,
    order_id: int = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: TokenClaims = Depends(get_current_user),
):
    user_id_from_token = int(current_user.sub)
    
    transactions = await transaction_repo.get_by_user_id(
        db, 
        user_id=user_id_from_token,
        offset=offset, 
        limit=limit,
        order_id=order_id
    )
    
    return [
        TransactionResponse(
            id=t.id,
            order_id=t.order_id,
            user_id=t.user_id,
            cost=t.cost,
            is_success=t.is_success
        ) for t in transactions
    ]



