from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_serializer

from app.core.time import to_app_timezone


class LifeRecordItem(BaseModel):
    id: int
    session_id: str
    title: Optional[str] = None
    content: str
    mood_label: Optional[str] = None
    location: Optional[str] = None
    tags: list[str] = []
    media_url: Optional[str] = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()
