from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from transaction_service.transaction_module.transaction import Transaction
from typing import Optional


class TransactionRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, tr_id: int) -> Optional[Transaction]:
        query = select(Transaction).filter_by(id=tr_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_range(
        db: AsyncSession,
        offset: int = 0,
        limit: int = 10,
        order_id: int = None
    ) -> list[Transaction]:
        query = select(Transaction)
        if order_id is not None:
            query = query.filter_by(order_id=order_id)
        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, new_tr: Transaction) -> Transaction:
        db.add(new_tr)
        await db.commit()
        await db.refresh(new_tr)
        return new_tr

