from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.time import utc_now


class Base(DeclarativeBase):
    pass


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(10))
    content_type: Mapped[str] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    emotion_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emotion_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    tts_audio_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    mood_label: Mapped[str] = mapped_column(String(20), index=True)
    mood_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="chat")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avatar_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    motto: Mapped[str | None] = mapped_column(String(160), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ebti_type: Mapped[str | None] = mapped_column(String(12), nullable=True)
    ebti_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ebti_avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        index=True,
    )


class GrowthProfile(Base):
    __tablename__ = "growth_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(40), nullable=True)
    current_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    focus: Mapped[str | None] = mapped_column(String(80), nullable=True)
    personality: Mapped[str] = mapped_column(String(20), default="warm", server_default="warm")
    weekly_goal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    private_mode: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    anonymous_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    crisis_guard: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        index=True,
    )


class GrowthMemory(Base):
    __tablename__ = "growth_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    category: Mapped[str] = mapped_column(String(40), default="目标", server_default="目标")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class NPCAffinity(Base):
    __tablename__ = "npc_affinities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    npc_name: Mapped[str] = mapped_column(String(40), index=True)
    player_id: Mapped[str] = mapped_column(String(80), default="player", index=True)
    affinity: Mapped[float] = mapped_column(Float, default=50.0)
    level: Mapped[str] = mapped_column(String(20), default="友好")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class LifeRecord(Base):
    __tablename__ = "life_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), default="private", server_default="private", index=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    comment_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    repost_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class SocialLike(Base):
    __tablename__ = "social_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class SocialComment(Base):
    __tablename__ = "social_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    reply_to_comment_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    reply_to_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    author_type: Mapped[str] = mapped_column(String(20), default="user", server_default="user", index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    reply_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class SocialRepost(Base):
    __tablename__ = "social_reposts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    school: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    college: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True)
