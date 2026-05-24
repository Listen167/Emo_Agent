from dataclasses import dataclass
from datetime import datetime


@dataclass
class MoodSnapshot:
    label: str
    confidence: float
    created_at: datetime


class MemoryService:
    """Future home for long-term user profile and mood timeline logic."""

    def summarize_recent_mood(self, session_id: str) -> str | None:
        return None

    def record_mood(self, session_id: str, mood: MoodSnapshot) -> None:
        return None


_memory_service = MemoryService()


def get_memory_service() -> MemoryService:
    return _memory_service
