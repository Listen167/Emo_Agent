from collections import Counter, defaultdict
from calendar import monthrange
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.time import APP_TIMEZONE, to_app_timezone
from app.models.message import MoodLog
from app.schemas.mood import MoodDay, MoodSummary


router = APIRouter(prefix="/api/mood", tags=["心情"])

MOOD_PRIORITY = {
    "happy": 5,
    "neutral": 4,
    "surprised": 3,
    "anxious": 2,
    "sad": 1,
    "angry": 1,
}


def _dominant_mood(items: list[MoodLog]) -> str:
    counts = Counter(item.mood_label for item in items)
    return max(counts, key=lambda label: (counts[label], MOOD_PRIORITY.get(label, 0)))


@router.get("/calendar", response_model=MoodSummary)
async def mood_calendar(
    session_id: str,
    year: int | None = None,
    month: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(APP_TIMEZONE)
    target_year = year or now.year
    target_month = month or now.month
    target_month = max(1, min(target_month, 12))
    _, last_day = monthrange(target_year, target_month)
    start = datetime(target_year, target_month, 1, tzinfo=APP_TIMEZONE)
    end = datetime(target_year, target_month, last_day, 23, 59, 59, 999999, tzinfo=APP_TIMEZONE)

    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.session_id == session_id)
        .order_by(MoodLog.created_at)
    )
    logs = [
        log
        for log in result.scalars().all()
        if start <= to_app_timezone(log.created_at) <= end
    ]

    grouped: dict[str, list[MoodLog]] = defaultdict(list)
    for log in logs:
        day_key = to_app_timezone(log.created_at).date().isoformat()
        grouped[day_key].append(log)

    mood_days: list[MoodDay] = []
    for day_key, items in sorted(grouped.items()):
        mood_label = _dominant_mood(items)
        scores = [item.mood_score for item in items if item.mood_score is not None]
        source_count = Counter(item.source for item in items)
        mood_days.append(
            MoodDay(
                date=datetime.fromisoformat(day_key).date(),
                mood_label=mood_label,
                mood_score=sum(scores) / len(scores) if scores else None,
                count=len(items),
                source_count=dict(source_count),
            )
        )

    mood_count = Counter(log.mood_label for log in logs)
    return MoodSummary(days=mood_days, total_count=len(logs), mood_count=dict(mood_count))
