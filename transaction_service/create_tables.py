import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from transaction_service.core.database import Base
from shared.config import settings

async def create_all_tables():
    print(f"Connecting to: {settings.FASTAPI_DATABASE_URL}")
    engine = create_async_engine(settings.FASTAPI_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("All tables created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_all_tables())