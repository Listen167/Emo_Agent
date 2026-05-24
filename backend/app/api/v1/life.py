import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.message import LifeRecord
from app.schemas.life import LifeRecordItem


router = APIRouter(prefix="/api/life", tags=["生活记录"])

ALLOWED_MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _parse_tags(tags: Optional[str]) -> list[str]:
    if not tags:
        return []
    return [tag.strip() for tag in tags.replace("，", ",").split(",") if tag.strip()]


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
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    clean_content = content.strip()
    if not clean_content:
        raise HTTPException(status_code=400, detail="生活记录内容不能为空")

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

    record = LifeRecord(
        session_id=session_id,
        title=title.strip() if title else None,
        content=clean_content,
        mood_label=mood_label.strip() if mood_label else None,
        location=location.strip() if location else None,
        tags=json.dumps(_parse_tags(tags), ensure_ascii=False),
        media_path=media_path,
    )
    db.add(record)
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
    await db.delete(record)
    await db.commit()

    if media_path:
        file_path = settings.DATA_DIR / media_path
        file_path.unlink(missing_ok=True)

    return {"ok": True}
