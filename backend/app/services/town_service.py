import random
from dataclasses import dataclass

from ai.llm import get_llm_service


@dataclass(frozen=True)
class TownNPC:
    name: str
    title: str
    persona: str


NPCS = {
    "奕琳": TownNPC(
        name="奕琳",
        title="Python工程师",
        persona="你是奕琳，一位理性、耐心的 Python 工程师。回答要清楚、实用，语气自然亲切。",
    ),
    "梓敏": TownNPC(
        name="梓敏",
        title="产品经理",
        persona="你是梓敏，一位善于倾听和拆解需求的产品经理。回答要有条理，关注用户真实目标。",
    ),
    "敏惠": TownNPC(
        name="敏惠",
        title="UI设计师",
        persona="你是敏惠，一位审美敏锐、表达温柔的 UI 设计师。回答要具体，并能给出设计视角。",
    ),
}


class TownService:
    def __init__(self) -> None:
        self.llm_service = get_llm_service()
        self.idle_lines = [
            "今天小镇很安静，适合慢慢整理想法。",
            "我刚刚在想，怎样把事情做得更顺一点。",
            "如果你想聊聊，我就在这里。",
        ]

    def list_npcs(self) -> list[dict[str, str]]:
        return [
            {"name": npc.name, "title": npc.title}
            for npc in NPCS.values()
        ]

    def get_status(self) -> dict[str, str]:
        return {
            npc.name: random.choice(self.idle_lines)
            for npc in NPCS.values()
        }

    def chat(self, npc_name: str, message: str) -> dict[str, str | bool]:
        npc = NPCS.get(npc_name)
        if npc is None:
            raise ValueError(f"NPC '{npc_name}' 不存在")

        user_input = (
            f"{npc.persona}\n\n"
            "请以这个 NPC 的身份回复玩家。回复限制在 120 字以内，不要自称 AI，不要输出旁白。\n\n"
            f"玩家说：{message}"
        )
        reply = self.llm_service.generate(
            user_input=user_input,
            emotion={"label": "neutral"},
            history=None,
            knowledge_context=None,
        )
        return {
            "success": True,
            "npc_name": npc.name,
            "npc_title": npc.title,
            "message": reply,
        }


_town_service = TownService()


def get_town_service() -> TownService:
    return _town_service
