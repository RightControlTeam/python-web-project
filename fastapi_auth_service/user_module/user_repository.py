from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from user_module.user import User
from typing import Optional

from user_module.user_schemas import UserUpdateRequest


class UserRepository:
    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()


    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()


    async def get_range(self, db: AsyncSession, offset: int = 0, limit: int = 10) -> list[User]:
        query = select(User).offset(offset).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


    async def create(self, db: AsyncSession, new_user: User) -> User:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def delete(self, db: AsyncSession, user_id: int):
        user = await self.get_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True

    async def update(self, db: AsyncSession, user: User):
        updated_user = await db.merge(user)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user

