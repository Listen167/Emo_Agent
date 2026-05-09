from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


url = settings.DATABASE_URL
if not url.startswith("sqlite+"):
    url = url.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    from app.models.message import Base as MessageBase

    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(MessageBase.metadata.create_all)
