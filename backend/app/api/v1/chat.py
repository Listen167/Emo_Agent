import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session, get_db
from app.schemas.chat import ChatResponse, HistoryItem
from app.services.pipeline import get_history, process_chat
from app.services.conversation_orchestrator import get_conversation_orchestrator


router = APIRouter(prefix="/api/chat", tags=["对话"])


def _json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


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


@router.websocket("/stream")
async def stream_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        text = str(payload.get("text") or "")
        session_id = str(payload.get("session_id") or "") or None
        if not text.strip():
            await websocket.send_json({"type": "error", "message": "缺少文本输入"})
            return

        async with async_session() as db:
            orchestrator = get_conversation_orchestrator()
            async for event in orchestrator.stream_chat_events(text, session_id, db):
                await websocket.send_json(_json_safe(event))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
