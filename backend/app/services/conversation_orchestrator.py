import asyncio
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.asr import get_asr_service
from ai.emotion import get_emotion_service
from ai.llm import get_llm_service
from ai.rag.service import get_rag_service
from ai.tts import get_tts_service
from app.core.config import settings
from app.core.time import utc_now
from app.models.message import ChatMessage, MoodLog
from app.schemas.chat import ChatResponse, EmotionResult, HistoryItem


EBTI_TEST_URL = "/ebti-test/index.html"


def is_ebti_request(text: str) -> bool:
    normalized = text.lower()
    has_test_intent = any(term in normalized for term in ("测试", "测一下", "测测", "人格", "性格", "test"))
    has_ebti = "ebti" in normalized
    has_mbti = "mbti" in normalized
    return has_ebti or (has_mbti and has_test_intent)


class ConversationOrchestrator:
    def __init__(self) -> None:
        self.asr_service = get_asr_service()
        self.emotion_service = get_emotion_service()
        self.llm_service = get_llm_service()
        self.tts_service = get_tts_service()
        self.rag_service = get_rag_service()

    async def process_chat(
        self,
        text: Optional[str],
        audio_path: Optional[str],
        session_id: Optional[str],
        db: AsyncSession,
    ) -> ChatResponse:
        sid = session_id or str(uuid.uuid4())
        final_text, audio_probs = await self._resolve_user_text(text, audio_path)
        display_user_text = final_text or ("[语音未识别出文本]" if audio_path else "")

        text_probs = None
        if final_text:
            text_probs = await asyncio.to_thread(self.emotion_service.predict_text, final_text)

        fused = self.emotion_service.fuse(audio_probs, text_probs, settings.AUDIO_EMOTION_WEIGHT)
        context_messages = await self._load_recent_context(sid, db)
        knowledge_context = await self._load_knowledge_context(final_text)
        if knowledge_context:
            print(f"[RAG] context loaded, chars={len(knowledge_context)}")
        elif final_text and settings.RAG_ENABLED:
            print("[RAG] no context matched")

        reply = await self._generate_reply(final_text, fused, context_messages, knowledge_context)
        tts_path = await self._synthesize_reply(reply, sid, fused["label"])

        user_msg, ai_msg = await self._save_messages(db, sid, audio_path, display_user_text, fused, reply, tts_path)
        return ChatResponse(
            session_id=sid,
            text=reply,
            user_text=display_user_text,
            emotion=EmotionResult(**fused),
            tts_audio_url=self._build_tts_audio_url(tts_path),
            user_created_at=user_msg.created_at,
            assistant_created_at=ai_msg.created_at,
        )

    async def get_history(self, session_id: str, db: AsyncSession) -> list[HistoryItem]:
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
                tts_audio_url=self._build_tts_audio_url(message.tts_audio_path),
                created_at=message.created_at,
            )
            for message in messages
        ]

    async def _resolve_user_text(self, text: Optional[str], audio_path: Optional[str]):
        final_text = (text or "").strip()
        audio_probs = None
        if audio_path:
            transcribed_text, audio_probs = await asyncio.to_thread(self.asr_service.transcribe, audio_path)
            if not final_text and transcribed_text:
                final_text = transcribed_text.strip()
        return final_text, audio_probs

    async def _load_recent_context(self, session_id: str, db: AsyncSession, limit: int = 10) -> list[dict[str, str]]:
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

    async def _load_knowledge_context(self, final_text: str) -> str | None:
        if not final_text or not settings.RAG_ENABLED:
            return None
        return await asyncio.to_thread(self.rag_service.retrieve_context, final_text)

    async def _generate_reply(
        self,
        final_text: str,
        fused_emotion: dict,
        context_messages: list[dict[str, str]],
        knowledge_context: str | None,
    ) -> str:
        if not final_text:
            return "我刚才没有听清你的内容。你可以再说一遍，或者直接用文字告诉我。"
        if is_ebti_request(final_text):
            return (
                "可以，EBTI 测试入口已经准备好。点击下面的“开始 EBTI 测试”按钮，"
                f"回答完题目后页面会自动生成你的结果。\n\n测试地址：{EBTI_TEST_URL}"
            )
        return await asyncio.to_thread(
            self.llm_service.generate,
            final_text,
            fused_emotion,
            context_messages,
            knowledge_context,
        )

    async def _synthesize_reply(self, reply: str, session_id: str, emotion_label: str) -> str | None:
        if not reply.strip() or not settings.TTS_ENABLED:
            return None
        path = await asyncio.to_thread(self.tts_service.synthesize, reply, session_id, emotion_label)
        return path or None

    async def _save_messages(
        self,
        db: AsyncSession,
        session_id: str,
        audio_path: Optional[str],
        user_text: str,
        fused_emotion: dict,
        reply: str,
        tts_path: str | None,
    ) -> tuple[ChatMessage, ChatMessage]:
        created_at = utc_now()
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content_type="audio" if audio_path else "text",
            content=user_text,
            emotion_label=fused_emotion["label"],
            emotion_conf=fused_emotion["confidence"],
            created_at=created_at,
        )
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content_type="text",
            content=reply,
            tts_audio_path=tts_path,
            created_at=utc_now(),
        )
        mood_log = MoodLog(
            session_id=session_id,
            mood_label=fused_emotion["label"],
            mood_score=fused_emotion["confidence"],
            source="chat",
            note=user_text[:120],
            created_at=created_at,
        )
        db.add_all([user_msg, ai_msg, mood_log])
        await db.commit()
        await db.refresh(user_msg)
        await db.refresh(ai_msg)
        return user_msg, ai_msg

    def _build_tts_audio_url(self, tts_path: Optional[str]) -> Optional[str]:
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


_conversation_orchestrator = ConversationOrchestrator()


def get_conversation_orchestrator() -> ConversationOrchestrator:
    return _conversation_orchestrator
