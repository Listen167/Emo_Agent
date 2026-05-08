import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.models.message import ChatMessage
from app.schemas.chat import ChatResponse, EmotionResult, HistoryItem
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ai import asr, emotion, fusion, llm, tts

_meme_pool = []
def load_memes():
    global _meme_pool
    p = Path(settings.MEME_PATH)
    if p.exists():
        _meme_pool = json.loads(p.read_text(encoding="utf-8"))
    else:
        _meme_pool = ["尊嘟假嘟", "汗流浃背了吧老弟", "CPU烧了", "泰裤辣", "绝绝子", "破防了", "笑不活了"]

async def process_chat(
    text: Optional[str],
    audio_path: Optional[str],
    session_id: Optional[str],
    db: AsyncSession
) -> ChatResponse:
    load_memes()
    sid = session_id or str(uuid.uuid4())
    
    final_text = text or ""
    if audio_path and not final_text:
        final_text = await asyncio.to_thread(asr.transcribe, audio_path)

    audio_probs = None
    text_probs = None
    if audio_path:
        audio_probs = await asyncio.to_thread(emotion.predict_audio, audio_path)
    if final_text.strip():
        text_probs = await asyncio.to_thread(emotion.predict_text, final_text)

    fused = fusion.calculate(audio_probs, text_probs, settings.AUDIO_EMOTION_WEIGHT)

    meme = _meme_pool[uuid.uuid4().int % len(_meme_pool)]
    reply = await asyncio.to_thread(llm.generate, final_text, fused, meme)

    tts_path = None
    if reply.strip():
        tts_path = await asyncio.to_thread(tts.synthesize, reply, sid, fused["label"])

    user_msg = ChatMessage(
        session_id=sid, role="user", content_type="audio" if audio_path else "text",
        content=final_text, emotion_label=fused["label"], emotion_conf=fused["confidence"]
    )
    ai_msg = ChatMessage(session_id=sid, role="assistant", content_type="text", content=reply, tts_audio_path=tts_path)
    db.add_all([user_msg, ai_msg])
    await db.commit()

    tts_audio_url = f"/data/tts/{session_id}_{len(reply)}.wav" if tts_path else None
    return ChatResponse(session_id=sid, text=reply, user_text=final_text, emotion=fused, tts_audio_url=tts_audio_url)

async def get_history(session_id: str, db: AsyncSession) -> list[HistoryItem]:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(desc(ChatMessage.created_at)).limit(200)
    )
    return [HistoryItem.model_validate(m) for m in result.scalars().all()]