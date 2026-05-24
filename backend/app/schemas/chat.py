from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_serializer

from app.core.time import to_app_timezone


class EmotionResult(BaseModel):
    label: str
    confidence: float
    audio_weight: float
    text_weight: float


class ChatResponse(BaseModel):
    session_id: str
    role: str = "assistant"
    text: str
    user_text: str = ""
    emotion: EmotionResult
    tts_audio_url: Optional[str] = None
    user_created_at: datetime
    assistant_created_at: datetime

    @field_serializer("user_created_at", "assistant_created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()


class HistoryItem(BaseModel):
    id: int
    role: str
    content_type: str
    content: str
    emotion_label: Optional[str]
    emotion_conf: Optional[float] = None
    tts_audio_url: Optional[str] = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_app_timezone(value).isoformat()
