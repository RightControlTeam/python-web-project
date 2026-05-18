from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi import HTTPException
from httpx import AsyncClient

from transaction_service.transaction_module.transaction_repository import TransactionRepository
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest
from transaction_service.transaction_module.transaction import Transaction

from shared.jwt_module import TokenClaims, decode_jwt

from shared.config import settings

DJANGO_URL = settings.DJANGO_BACKEND_URL

class TransactionManager:
    @staticmethod
    async def create( db: AsyncSession, request: CreateTransactionRequest, auth: str) -> Optional[Transaction]:
        async with AsyncClient() as client:
            response = await client.post(
                f"{DJANGO_URL}/api/users/balance/transaction/",
                json={
                    "amount": -request.cost,
                    "order_id": request.order_id
                },
                headers={"Authorization": auth}
            )

        claims: TokenClaims = decode_jwt(auth.replace("Bearer ", ""))
        if claims is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        new_tr: Transaction = Transaction(
            user_id = int(claims.sub),
            order_id = request.order_id,
            cost = request.cost,
            is_success = response.status_code == 200
        )

        return await TransactionRepository.create(db, new_tr)

    @staticmethod
    async def get_by_id(db: AsyncSession, tr_id: int) -> Transaction:
        return await TransactionRepository.get_by_id(db, tr_id)

    @staticmethod
    async def get_range(
            db: AsyncSession,
            offset: int = 0,
            limit: int = 10,
            order_id: int = None,
            user_id: int = None
    ) -> list[Transaction]:
        return await TransactionRepository.get_range(db, offset, limit, order_id, user_id)