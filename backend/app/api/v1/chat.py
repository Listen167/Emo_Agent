from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, init_db
from app.services.pipeline import process_chat, get_history
from app.schemas.chat import ChatResponse, HistoryItem
from app.core.config import settings

router = APIRouter(prefix="/api/chat", tags=["对话"])

@router.on_event("startup")
async def startup():
    await init_db()

@router.post("/send", response_model=ChatResponse)
async def send(
    text: str = Form(None),
    audio: UploadFile = File(None),
    session_id: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    audio_path = None
    if audio:
        p = Path(f"./data/uploads/{session_id or 'tmp'}")
        p.mkdir(parents=True, exist_ok=True)
        audio_path = str(p / audio.filename)
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
            
    return await process_chat(text, audio_path, session_id, db)

@router.get("/history", response_model=list[HistoryItem])
async def history(session_id: str, db: AsyncSession = Depends(get_db)):
    return await get_history(session_id, db)