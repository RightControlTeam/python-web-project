from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from transaction_service.transaction_module.transaction_repository import TransactionRepository
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest
from transaction_service.transaction_module.transaction import Transaction

from shared.config import settings

DJANGO_URL = settings.DJANGO_BACKEND_URL

class TransactionManager:
    @staticmethod
    async def create( db: AsyncSession, request: CreateTransactionRequest, user_id: int) -> Optional[Transaction]:
        new_tr: Transaction = Transaction(
            user_id = request.user_id,
            order_id = request.order_id,
            cost = request.cost,
            is_success = True # need to check
        )
        #need to apply payment to uer if success
        return await TransactionRepository.create(db, new_tr)

    @staticmethod
    async def get_by_id(db: AsyncSession, tr_id: int) -> Transaction:
        return await TransactionRepository.get_by_id(db, tr_id)

    @staticmethod
    async def get_range(
            db: AsyncSession,
            offset: int = 0,
            limit: int = 10,
            order_id: int = None
    ) -> list[Transaction]:
        return await TransactionRepository.get_range(db, offset, limit, order_id)