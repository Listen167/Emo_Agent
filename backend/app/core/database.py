from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from pathlib import Path

Base = declarative_base()

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
    Path("./data").mkdir(exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(MessageBase.metadata.create_all)