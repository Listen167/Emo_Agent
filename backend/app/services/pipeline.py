import asyncio
import json
import random
import sys
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.message import ChatMessage
from app.schemas.chat import ChatResponse, EmotionResult, HistoryItem

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ai import asr, emotion, fusion, llm, tts


_meme_pool: list[str] = []
_memes_loaded = False


def _default_memes() -> list[str]:
    return [
        "尊嘟假嘟",
        "汗流浃背了吧",
        "CPU 烧了",
        "绷不住了",
        "有点东西",
        "直接破防",
        "笑不活了",
    ]


def load_memes() -> None:
    global _meme_pool, _memes_loaded
    if _memes_loaded:
        return

    path = Path(settings.MEME_PATH)
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                _meme_pool = [str(item).strip() for item in data if str(item).strip()]
    except Exception:
        _meme_pool = []

    if not _meme_pool:
        _meme_pool = _default_memes()

    _memes_loaded = True


def _build_tts_audio_url(tts_path: Optional[str]) -> Optional[str]:
    if not tts_path:
        return None

    path = Path(tts_path)
    if path.is_absolute():
        try:
            relative_path = path.resolve().relative_to(settings.DATA_DIR.resolve())
            return f"/data/{relative_path.as_posix()}"
        except ValueError:
            return None

    relative_path = Path(*path.parts[1:]) if path.parts and path.parts[0] == "data" else path
    return f"/data/{relative_path.as_posix()}"


async def _load_recent_context(session_id: str, db: AsyncSession, limit: int = 10) -> list[dict[str, str]]:
    result = await db.execute(
        select(ChatMessage.role, ChatMessage.content)
        .where(ChatMessage.session_id == session_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    rows = list(result.all())
    rows.reverse()

    return [
        {"role": role, "content": content}
        for role, content in rows
        if isinstance(content, str) and content.strip()
    ]


async def process_chat(
    text: Optional[str],
    audio_path: Optional[str],
    session_id: Optional[str],
    db: AsyncSession,
) -> ChatResponse:
    load_memes()
    sid = session_id or str(uuid.uuid4())

    final_text = (text or "").strip()
    audio_probs = None

    if audio_path:
        transcribed_text, audio_probs = await asyncio.to_thread(asr.transcribe, audio_path)
        if not final_text and transcribed_text:
            final_text = transcribed_text.strip()

    display_user_text = final_text or ("（未识别到有效语音）" if audio_path else "")

    text_probs = None
    if final_text:
        text_probs = await asyncio.to_thread(emotion.predict_text, final_text)

    fused = fusion.calculate(audio_probs, text_probs, settings.AUDIO_EMOTION_WEIGHT)
    context_messages = await _load_recent_context(sid, db)

    if final_text:
        meme = random.choice(_meme_pool)
        reply = await asyncio.to_thread(llm.generate, final_text, fused, meme, context_messages)
    else:
        reply = "我刚刚没太听清，你可以再说一遍，或者直接打字给我。"

    tts_path = None
    if reply.strip():
        tts_path = await asyncio.to_thread(tts.synthesize, reply, sid, fused["label"])

    user_msg = ChatMessage(
        session_id=sid,
        role="user",
        content_type="audio" if audio_path else "text",
        content=display_user_text,
        emotion_label=fused["label"],
        emotion_conf=fused["confidence"],
    )
    ai_msg = ChatMessage(
        session_id=sid,
        role="assistant",
        content_type="text",
        content=reply,
        tts_audio_path=tts_path,
    )
    db.add_all([user_msg, ai_msg])
    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(ai_msg)

    return ChatResponse(
        session_id=sid,
        text=reply,
        user_text=display_user_text,
        emotion=EmotionResult(**fused),
        tts_audio_url=_build_tts_audio_url(tts_path),
        user_created_at=user_msg.created_at,
        assistant_created_at=ai_msg.created_at,
    )


async def get_history(session_id: str, db: AsyncSession) -> list[HistoryItem]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(200)
    )
    messages = list(result.scalars().all())
    messages.reverse()

    return [
        HistoryItem(
            id=message.id,
            role=message.role,
            content_type=message.content_type,
            content=message.content,
            emotion_label=message.emotion_label,
            emotion_conf=message.emotion_conf,
            tts_audio_url=_build_tts_audio_url(message.tts_audio_path),
            created_at=message.created_at,
        )
        for message in messages
    ]
