from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.core.time import to_app_timezone


class PlazaAuthor(BaseModel):
    session_id: str
    nickname: str
    avatar_url: Optional[str] = None
    ebti_type: Optional[str] = None
    ebti_name: Optional[str] = None


class PlazaPostItem(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    mood_label: Optional[str] = None
    location: Optional[str] = None
    tags: list[str] = []
    media_url: Optional[str] = None
    author: PlazaAuthor
    like_count: int = 0
    comment_count: int = 0
    repost_count: int = 0
    liked: bool = False
    xiaoxi_liked: bool = False
    reposted: bool = False
    published_at: Optional[datetime] = None
    created_at: datetime

    @field_serializer("published_at", "created_at")
    def serialize_time(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return to_app_timezone(value).isoformat()


class PlazaCommentCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=800)


class PlazaCommentReplyItem(BaseModel):
    id: int
    record_id: int
    parent_id: int
    reply_to_comment_id: Optional[int] = None
    reply_to_author: Optional[PlazaAuthor] = None
    author: PlazaAuthor
    author_type: str
    content: str
    like_count: int = 0
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()


class PlazaCommentItem(BaseModel):
    id: int
    record_id: int
    parent_id: Optional[int] = None
    reply_to_comment_id: Optional[int] = None
    reply_to_author: Optional[PlazaAuthor] = None
    author: PlazaAuthor
    author_type: str
    content: str
    like_count: int = 0
    reply_count: int = 0
    replies: list[PlazaCommentReplyItem] = Field(default_factory=list)
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()
