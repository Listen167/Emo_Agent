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
            if "visibility" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN visibility VARCHAR(20) DEFAULT 'private'"))
            if "like_count" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN like_count INTEGER DEFAULT 0"))
            if "comment_count" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN comment_count INTEGER DEFAULT 0"))
            if "repost_count" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN repost_count INTEGER DEFAULT 0"))
            if "published_at" not in life_column_names:
                await conn.execute(text("ALTER TABLE life_records ADD COLUMN published_at DATETIME"))

            comment_columns = await conn.execute(text("PRAGMA table_info(social_comments)"))
            comment_column_names = {row[1] for row in comment_columns.fetchall()}
            comment_alters = {
                "parent_id": "ALTER TABLE social_comments ADD COLUMN parent_id INTEGER",
                "reply_to_comment_id": "ALTER TABLE social_comments ADD COLUMN reply_to_comment_id INTEGER",
                "reply_to_session_id": "ALTER TABLE social_comments ADD COLUMN reply_to_session_id VARCHAR(36)",
                "like_count": "ALTER TABLE social_comments ADD COLUMN like_count INTEGER DEFAULT 0",
                "reply_count": "ALTER TABLE social_comments ADD COLUMN reply_count INTEGER DEFAULT 0",
            }
            for column_name, alter_sql in comment_alters.items():
                if column_name not in comment_column_names:
                    await conn.execute(text(alter_sql))

            profile_columns = await conn.execute(text("PRAGMA table_info(user_profiles)"))
            profile_column_names = {row[1] for row in profile_columns.fetchall()}
            profile_alters = {
                "nickname": "ALTER TABLE user_profiles ADD COLUMN nickname VARCHAR(40)",
                "avatar_path": "ALTER TABLE user_profiles ADD COLUMN avatar_path VARCHAR(255)",
                "motto": "ALTER TABLE user_profiles ADD COLUMN motto VARCHAR(160)",
                "gender": "ALTER TABLE user_profiles ADD COLUMN gender VARCHAR(20)",
                "ebti_type": "ALTER TABLE user_profiles ADD COLUMN ebti_type VARCHAR(12)",
                "ebti_name": "ALTER TABLE user_profiles ADD COLUMN ebti_name VARCHAR(40)",
                "ebti_avatar": "ALTER TABLE user_profiles ADD COLUMN ebti_avatar VARCHAR(255)",
                "updated_at": "ALTER TABLE user_profiles ADD COLUMN updated_at DATETIME",
            }
            for column_name, alter_sql in profile_alters.items():
                if column_name not in profile_column_names:
                    await conn.execute(text(alter_sql))
