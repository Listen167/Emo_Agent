from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ChatResponse, HistoryItem
from app.services.conversation_orchestrator import get_conversation_orchestrator


async def process_chat(
    text: Optional[str],
    audio_path: Optional[str],
    session_id: Optional[str],
    db: AsyncSession,
) -> ChatResponse:
    return await get_conversation_orchestrator().process_chat(text, audio_path, session_id, db)


async def get_history(session_id: str, db: AsyncSession) -> list[HistoryItem]:
    return await get_conversation_orchestrator().get_history(session_id, db)
