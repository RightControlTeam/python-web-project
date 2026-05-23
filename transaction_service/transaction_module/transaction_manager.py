from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi import HTTPException
from httpx import AsyncClient

from transaction_service.transaction_module.transaction_repository import TransactionRepository
from transaction_service.transaction_module.transaction_schemas import CreateTransactionRequest
from transaction_service.transaction_module.transaction import Transaction
from transaction_service.core.logger import logger

from shared.jwt_module import TokenClaims, decode_jwt

from shared.config import settings

import asyncio

DJANGO_URL = settings.DJANGO_BACKEND_URL



class TransactionManager:
    @staticmethod
    async def _notify(transaction: Transaction):
        if transaction.is_success:
            message = f"Transaction {transaction.id}: Payment succeeded. Cost: {transaction.cost}"
        else:
            message = f"Transaction {transaction.id}: Payment failed. Cost: {transaction.cost}"

        async with AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{DJANGO_URL}/api/orders/transaction-notify/",
                json={
                    "transaction_id": transaction.id,
                    "order_id": transaction.order_id,
                    "user_id": transaction.user_id,
                    "success": transaction.is_success,
                    "cost": transaction.cost,
                    "message": message
                },
                headers={
                    "X-Notification-Key": settings.NOTIFICATION_KEY
                }
            )


    @staticmethod
    async def create( db: AsyncSession, request: CreateTransactionRequest, auth: str) -> Optional[Transaction]:
        logger.info(f"Transaction request: order_id={request.order_id}, cost={request.cost}")

        claims: TokenClaims = decode_jwt(auth.replace("Bearer ", ""))
        if claims is None:
            logger.error(f"Invalid token. order_id={request.order_id}")
            raise HTTPException(status_code=401, detail="Invalid token")

        async with AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{DJANGO_URL}/api/users/balance/transaction/",
                json={
                    "amount": -request.cost,
                    "order_id": request.order_id
                },
                headers={"Authorization": auth}
            )

        if response.status_code == 200:
            logger.info(f"Django API success. order_id={request.order_id}")
        else:
            logger.warning(f"Django API failed. order_id={request.order_id}, status={response.status_code}")

        new_tr: Transaction = Transaction(
            user_id = int(claims.sub),
            order_id = request.order_id,
            cost = request.cost,
            is_success = response.status_code == 200
        )
        result = await TransactionRepository.create(db, new_tr)
        logger.info(f"Transaction created. order_id={request.order_id}")

        asyncio.create_task(TransactionManager._notify(result))
        return result

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