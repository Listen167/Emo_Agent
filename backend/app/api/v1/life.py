import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.time import utc_now
from app.models.message import LifeRecord, MoodLog, SocialComment, SocialLike, SocialRepost
from app.schemas.life import LifeRecordItem


router = APIRouter(prefix="/api/life", tags=["生活记录"])

ALLOWED_MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _parse_tags(tags: Optional[str]) -> list[str]:
    if not tags:
        return []
    return [tag.strip() for tag in tags.replace("，", ",").split(",") if tag.strip()]


def _normalize_visibility(value: Optional[str]) -> str:
    clean = (value or "private").strip().lower()
    return "public" if clean == "public" else "private"


def _media_url(media_path: Optional[str]) -> Optional[str]:
    if not media_path:
        return None
    path = Path(media_path)
    relative_path = Path(*path.parts[1:]) if path.parts and path.parts[0] == "data" else path
    return f"/data/{relative_path.as_posix()}"


def _to_item(record: LifeRecord) -> LifeRecordItem:
    return LifeRecordItem(
        id=record.id,
        session_id=record.session_id,
        title=record.title,
        content=record.content,
        mood_label=record.mood_label,
        location=record.location,
        tags=json.loads(record.tags or "[]"),
        media_url=_media_url(record.media_path),
        visibility=record.visibility or "private",
        like_count=record.like_count or 0,
        comment_count=record.comment_count or 0,
        repost_count=record.repost_count or 0,
        published_at=record.published_at,
        created_at=record.created_at,
    )


@router.post("/records", response_model=LifeRecordItem)
async def create_record(
    session_id: str = Form(...),
    title: Optional[str] = Form(None),
    content: str = Form(...),
    mood_label: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    visibility: Optional[str] = Form("private"),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    clean_content = content.strip()
    if not clean_content and not (image and image.filename):
        raise HTTPException(status_code=400, detail="生活记录内容或图片不能为空")
    if not clean_content:
        clean_content = "分享了一张生活胶片"

    media_path = None
    if image and image.filename:
        suffix = Path(image.filename).suffix.lower()
        if suffix not in ALLOWED_MEDIA_SUFFIXES:
            raise HTTPException(status_code=400, detail="只支持 jpg、png、webp、gif 图片")
        media_dir = settings.MEDIA_DIR / session_id
        media_dir.mkdir(parents=True, exist_ok=True)
        file_path = media_dir / f"{uuid.uuid4().hex}{suffix}"
        with open(file_path, "wb") as f:
            f.write(await image.read())
        media_path = str(Path("media") / session_id / file_path.name)

    clean_visibility = _normalize_visibility(visibility)
    record = LifeRecord(
        session_id=session_id,
        title=title.strip() if title else None,
        content=clean_content,
        mood_label=mood_label.strip() if mood_label else None,
        location=location.strip() if location else None,
        tags=json.dumps(_parse_tags(tags), ensure_ascii=False),
        media_path=media_path,
        visibility=clean_visibility,
        published_at=utc_now() if clean_visibility == "public" else None,
    )
    db.add(record)
    if record.mood_label:
        db.add(
            MoodLog(
                session_id=session_id,
                mood_label=record.mood_label,
                mood_score=None,
                source="life",
                note=record.title or record.content[:80],
            )
        )
    await db.commit()
    await db.refresh(record)
    return _to_item(record)


@router.get("/records", response_model=list[LifeRecordItem])
async def list_records(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LifeRecord)
        .where(LifeRecord.session_id == session_id)
        .order_by(desc(LifeRecord.created_at))
        .limit(100)
    )
    return [_to_item(record) for record in result.scalars().all()]


@router.delete("/records/{record_id}")
async def delete_record(record_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LifeRecord).where(LifeRecord.id == record_id, LifeRecord.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="记录不存在")

    media_path = record.media_path
    likes_result = await db.execute(select(SocialLike).where(SocialLike.record_id == record_id))
    comments_result = await db.execute(select(SocialComment).where(SocialComment.record_id == record_id))
    reposts_result = await db.execute(select(SocialRepost).where(SocialRepost.record_id == record_id))
    for like in likes_result.scalars().all():
        await db.delete(like)
    for comment in comments_result.scalars().all():
        await db.delete(comment)
    for repost in reposts_result.scalars().all():
        await db.delete(repost)
    await db.delete(record)
    await db.commit()

    if media_path:
        file_path = settings.DATA_DIR / media_path
        file_path.unlink(missing_ok=True)

    return {"ok": True}
