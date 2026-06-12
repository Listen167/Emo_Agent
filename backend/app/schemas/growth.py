from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.core.time import to_app_timezone


class GrowthProfileUpdate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=80)
    nickname: Optional[str] = Field(None, max_length=40)
    current_state: Optional[str] = Field(None, max_length=100)
    focus: Optional[str] = Field(None, max_length=80)
    personality: Optional[str] = Field(None, max_length=20)
    weekly_goal: Optional[str] = Field(None, max_length=200)
    setup_completed: Optional[bool] = None
    private_mode: Optional[bool] = None
    anonymous_default: Optional[bool] = None
    crisis_guard: Optional[bool] = None


class GrowthMemoryCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=80)
    category: str = Field("目标", min_length=1, max_length=40)
    content: str = Field(..., min_length=1, max_length=500)


class GrowthProfileItem(BaseModel):
    session_id: str
    nickname: Optional[str] = None
    current_state: Optional[str] = None
    focus: Optional[str] = None
    personality: str = "warm"
    weekly_goal: Optional[str] = None
    setup_completed: bool = False
    private_mode: bool = True
    anonymous_default: bool = False
    crisis_guard: bool = True
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_time(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()


class GrowthMemoryItem(BaseModel):
    id: int
    category: str
    content: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()


class GrowthStateItem(BaseModel):
    profile: GrowthProfileItem
    memories: list[GrowthMemoryItem]
