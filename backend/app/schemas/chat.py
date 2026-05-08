from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EmotionResult(BaseModel):
    label: str
    confidence: float
    audio_weight: float
    text_weight: float

class ChatResponse(BaseModel):
    session_id: str
    role: str = "assistant"
    text: str
    emotion: EmotionResult
    tts_audio_url: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    role: str
    content: str
    emotion_label: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True