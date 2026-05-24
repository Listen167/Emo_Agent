from datetime import datetime, timezone
from zoneinfo import ZoneInfo


APP_TIMEZONE = ZoneInfo("Asia/Shanghai")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_app_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(APP_TIMEZONE)
