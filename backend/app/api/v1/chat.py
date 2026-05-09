import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.chat import ChatResponse, HistoryItem
from app.services.pipeline import get_history, process_chat


router = APIRouter(prefix="/api/chat", tags=["对话"])


@router.post("/send", response_model=ChatResponse)
async def send(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        if not (text and text.strip()) and not (audio and audio.filename):
            raise HTTPException(status_code=400, detail="缺少文本或语音输入")

        sid = session_id or str(uuid.uuid4())
        audio_path = None

        if audio and audio.filename:
            suffix = Path(audio.filename).suffix.lower() or ".wav"
            upload_dir = settings.UPLOAD_DIR / sid
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / f"{uuid.uuid4().hex}{suffix}"
            with open(file_path, "wb") as f:
                f.write(await audio.read())
            audio_path = str(file_path)

        return await process_chat(text, audio_path, sid, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=list[HistoryItem])
async def history(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_history(session_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
