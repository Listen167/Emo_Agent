from pathlib import Path

from sqlalchemy import text
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
    from app.models.message import Base

    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if url.startswith("sqlite+"):
            knowledge_columns = await conn.execute(text("PRAGMA table_info(knowledge_chunks)"))
            knowledge_column_names = {row[1] for row in knowledge_columns.fetchall()}
            if "embedding" not in knowledge_column_names:
                await conn.execute(text("ALTER TABLE knowledge_chunks ADD COLUMN embedding TEXT"))

            life_columns = await conn.execute(text("PRAGMA table_info(life_records)"))
            life_column_names = {row[1] for row in life_columns.fetchall()}
            if "location" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN location VARCHAR(120)"))
            if "tags" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN tags TEXT"))
