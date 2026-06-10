from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.core.time import to_app_timezone


class ProfileUpdate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=80)
    nickname: Optional[str] = Field(None, max_length=40)
    motto: Optional[str] = Field(None, max_length=160)
    gender: Optional[str] = Field(None, max_length=20)


class ProfileEbtiUpdate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=80)
    ebti_type: str = Field(..., min_length=1, max_length=12)
    ebti_name: Optional[str] = Field(None, max_length=40)
    ebti_avatar: Optional[str] = Field(None, max_length=255)


class UserProfileItem(BaseModel):
    id: int
    session_id: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    motto: Optional[str] = None
    gender: Optional[str] = None
    ebti_type: Optional[str] = None
    ebti_name: Optional[str] = None
    ebti_avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_time(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()
