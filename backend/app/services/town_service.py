import random
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.asr import get_asr_service
from ai.llm import get_llm_service
from ai.tts import get_tts_service
from app.core.config import settings
from app.core.time import utc_now
from app.models.message import NPCAffinity


@dataclass(frozen=True)
class TownNPC:
    name: str
    title: str
    persona: str
    voice: str
    tts_id: str


NPCS = {
    "奕琳": TownNPC(
        name="奕琳",
        title="Python工程师",
        persona="你是奕琳，一位理性、耐心的 Python 工程师。回答要清楚、实用，语气自然亲切。",
        voice="zh-CN-XiaoxiaoNeural",
        tts_id="yilin",
    ),
    "梓敏": TownNPC(
        name="梓敏",
        title="产品经理",
        persona="你是梓敏，一位善于倾听和拆解需求的产品经理。回答要有条理，关注用户真实目标。",
        voice="zh-CN-XiaoyiNeural",
        tts_id="zimin",
    ),
    "敏惠": TownNPC(
        name="敏惠",
        title="UI设计师",
        persona="你是敏惠，一位审美敏锐、表达温柔的 UI 设计师。回答要具体，并能给出设计视角。",
        voice="zh-CN-liaoning-XiaobeiNeural",
        tts_id="minhui",
    ),
}


class TownService:
    def __init__(self) -> None:
        self.llm_service = get_llm_service()
        self.tts_service = get_tts_service()
        self.asr_service = get_asr_service()
        self.idle_lines = [
            "今天小镇很安静，适合慢慢整理想法。",
            "我刚刚在想，怎样把事情做得更顺一点。",
            "如果你想聊聊，我就在这里。",
        ]

    def list_npcs(self) -> list[dict[str, str]]:
        return [
            {"name": npc.name, "title": npc.title, "voice": npc.voice}
            for npc in NPCS.values()
        ]

    def get_status(self) -> dict[str, str]:
        return {
            npc.name: random.choice(self.idle_lines)
            for npc in NPCS.values()
        }

    async def get_affinity(self, db: AsyncSession, npc_name: str, player_id: str = "player") -> dict[str, float | str]:
        row = await self._get_or_create_affinity(db, npc_name, player_id)
        return self._affinity_payload(row.affinity)

    async def get_all_affinities(self, db: AsyncSession, player_id: str = "player") -> dict[str, dict[str, float | str]]:
        return {
            npc_name: await self.get_affinity(db, npc_name, player_id)
            for npc_name in NPCS.keys()
        }

    async def set_affinity(
        self,
        db: AsyncSession,
        npc_name: str,
        affinity: float,
        player_id: str = "player",
    ) -> dict[str, float | str]:
        self._require_npc(npc_name)
        row = await self._get_or_create_affinity(db, npc_name, player_id)
        row.affinity = self._clamp_affinity(affinity)
        row.level = self._affinity_level(row.affinity)
        row.updated_at = utc_now()
        await db.commit()
        return self._affinity_payload(row.affinity)

    async def chat(
        self,
        db: AsyncSession,
        npc_name: str,
        message: str,
        player_id: str = "player",
    ) -> dict[str, str | bool | float | dict]:
        npc = NPCS.get(npc_name)
        if npc is None:
            raise ValueError(f"NPC '{npc_name}' 不存在")

        affinity_row = await self._get_or_create_affinity(db, npc_name, player_id)
        affinity_before = affinity_row.affinity
        affinity_level = self._affinity_level(affinity_before)
        affinity_modifier = self._affinity_modifier(affinity_before)

        user_input = (
            f"{npc.persona}\n\n"
            f"当前你和玩家的关系是：{affinity_level}，好感度 {affinity_before:.0f}/100。\n"
            f"请按这个关系状态调整语气：{affinity_modifier}\n\n"
            "请以这个 NPC 的身份回复玩家。回复限制在 120 字以内，不要自称 AI，不要输出旁白。\n\n"
            f"玩家说：{message}"
        )
        reply = self.llm_service.generate(
            user_input=user_input,
            emotion={"label": "neutral"},
            history=None,
            knowledge_context=None,
        )
        affinity_change = self._estimate_affinity_change(message)
        affinity_after = self._clamp_affinity(affinity_before + affinity_change)
        affinity_row.affinity = affinity_after
        affinity_row.level = self._affinity_level(affinity_after)
        affinity_row.updated_at = utc_now()
        await db.commit()
        tts_path = self._synthesize_reply(reply, npc)

        return {
            "success": True,
            "npc_name": npc.name,
            "npc_title": npc.title,
            "message": reply,
            "affinity": affinity_after,
            "affinity_level": affinity_row.level,
            "affinity_change": affinity_change,
            "affinity_info": self._affinity_payload(affinity_after),
            "tts_audio_url": self._build_tts_audio_url(tts_path),
            "voice": npc.voice,
        }

    async def transcribe_audio(self, audio_path: str) -> str:
        text, _audio_probs = self.asr_service.transcribe(audio_path)
        print(f"[TOWN ASR] {audio_path} -> {text}")
        return text.strip()

    def _synthesize_reply(self, reply: str, npc: TownNPC) -> str | None:
        if not reply.strip() or not settings.TTS_ENABLED:
            return None
        path = self.tts_service.synthesize(reply, f"town_{npc.tts_id}", "neutral", npc.voice)
        print(f"[TOWN TTS] npc={npc.name} voice={npc.voice} path={path}")
        return path or None

    def _build_tts_audio_url(self, tts_path: str | None) -> str | None:
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

    def _require_npc(self, npc_name: str) -> None:
        if npc_name not in NPCS:
            raise ValueError(f"NPC '{npc_name}' 不存在")

    async def _get_or_create_affinity(
        self,
        db: AsyncSession,
        npc_name: str,
        player_id: str,
    ) -> NPCAffinity:
        self._require_npc(npc_name)
        result = await db.execute(
            select(NPCAffinity).where(
                NPCAffinity.npc_name == npc_name,
                NPCAffinity.player_id == player_id,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            return row

        row = NPCAffinity(
            npc_name=npc_name,
            player_id=player_id,
            affinity=50.0,
            level=self._affinity_level(50.0),
            updated_at=utc_now(),
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    def _estimate_affinity_change(self, message: str) -> int:
        text = message.lower()
        positive_terms = ["谢谢", "感谢", "喜欢", "厉害", "真棒", "优秀", "帮帮", "请教", "开心", "你好", "辛苦"]
        negative_terms = ["讨厌", "糟糕", "太差", "垃圾", "笨", "闭嘴", "烦", "烂", "生气", "不喜欢"]

        positive_hits = sum(1 for term in positive_terms if term in text)
        negative_hits = sum(1 for term in negative_terms if term in text)
        if negative_hits > positive_hits:
            return max(-8, -3 * negative_hits)
        if positive_hits > 0:
            return min(6, 2 * positive_hits)
        return 0

    def _clamp_affinity(self, value: float) -> float:
        return max(0.0, min(100.0, value))

    def _affinity_level(self, affinity: float) -> str:
        if affinity >= 80:
            return "挚友"
        if affinity >= 60:
            return "亲密"
        if affinity >= 40:
            return "友好"
        if affinity >= 20:
            return "熟悉"
        return "陌生"

    def _affinity_modifier(self, affinity: float) -> str:
        if affinity >= 80:
            return "非常热情亲近，像熟悉的朋友一样愿意多分享。"
        if affinity >= 60:
            return "友好热情，会主动关心玩家。"
        if affinity >= 40:
            return "自然礼貌，保持正常友善交流。"
        if affinity >= 20:
            return "礼貌但略显生疏，回答更简洁。"
        return "冷淡疏离，不太主动延展话题。"

    def _affinity_payload(self, affinity: float) -> dict[str, float | str]:
        return {
            "affinity": affinity,
            "level": self._affinity_level(affinity),
            "modifier": self._affinity_modifier(affinity),
        }


_town_service = TownService()


def get_town_service() -> TownService:
    return _town_service
