from datetime import date

from pydantic import BaseModel


class MoodDay(BaseModel):
    date: date
    mood_label: str
    mood_score: float | None = None
    count: int
    source_count: dict[str, int]


class MoodSummary(BaseModel):
    days: list[MoodDay]
    total_count: int
    mood_count: dict[str, int]
