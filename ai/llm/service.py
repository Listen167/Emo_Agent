from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import settings


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "chat_system.md"


class LLMService:
    def __init__(self) -> None:
        self.client = OpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
        self.system_template = PROMPT_PATH.read_text(encoding="utf-8")
        self.emotion_prompts = {
            "happy": "用户情绪偏积极。保持轻松真诚，可以放大成就感，但不要强行玩梗。",
            "sad": "用户情绪偏低落。先共情和接住感受，再给一个小而可执行的建议。",
            "angry": "用户可能有愤怒或不满。先承认其边界和感受，避免说教，帮助梳理事实与下一步。",
            "anxious": "用户可能焦虑或压力较大。先降低紧张感，再把问题拆成可处理的小步骤。",
            "neutral": "用户情绪较平稳。保持自然、清晰、有帮助，避免过度煽情。",
            "surprised": "用户可能惊讶或困惑。先回应意外感，再帮助确认事实和选择。",
        }
        self.fallback_replies = {
            "happy": "听起来这件事让你状态不错。可以先把这个积极变化记下来，也许它能帮你找到最近真正有效的节奏。",
            "sad": "我能感觉到你现在不太好受。先不用急着解决所有问题，可以先说说最压着你的那一件事是什么。",
            "angry": "这件事确实可能让人很不舒服。我们可以先把发生了什么、你最在意的点、下一步能做什么分开看。",
            "anxious": "先把注意力放回当下。你可以告诉我最担心的具体结果是什么，我再帮你拆成几个可执行的小步骤。",
            "neutral": "我明白。你可以继续补充一点背景，我会结合你的状态和上下文给你更具体的建议。",
            "surprised": "这确实有点出乎意料。我们先确认关键事实，再判断它对你接下来的安排有什么影响。",
        }

    def build_system_prompt(self, emotion_label: str) -> str:
        strategy = self.emotion_prompts.get(emotion_label, self.emotion_prompts["neutral"])
        return self.system_template.format(emotion_label=emotion_label, emotion_strategy=strategy)

    def build_messages(
        self,
        user_input: str,
        emotion: dict,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
    ) -> list[ChatCompletionMessageParam]:
        emotion_label = str(emotion.get("label", "neutral"))
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.build_system_prompt(emotion_label)}
        ]

        if knowledge_context:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "以下是可参考的校园知识库检索结果。回答时只使用与用户问题相关的部分；"
                        "如果资料不足，请明确说明。\n\n"
                        "如果问题需要跨片段推理，例如“某比赛能加多少分”，必须先根据竞赛级别体系判断比赛级别，"
                        "再根据推免加分办法查找对应级别和获奖等次的加分。"
                        "如果用户没有提供获奖等次、赛事阶段、个人/团队排名，需要明确追问或列出不同情况。\n"
                        f"{knowledge_context}"
                    ),
                }
            )

        for item in history or []:
            role = item.get("role", "")
            content = item.get("content", "").strip()
            if role == "user" and content:
                messages.append({"role": "user", "content": content})
            elif role == "assistant" and content:
                messages.append({"role": "assistant", "content": content})

        messages.append({"role": "user", "content": user_input.strip()})
        return messages

    def generate(
        self,
        user_input: str,
        emotion: dict,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
    ) -> str:
        clean_input = user_input.strip()
        emotion_label = str(emotion.get("label", "neutral"))
        if not clean_input:
            return "我刚才没有听清你的内容。你可以再说一遍，或者直接用文字告诉我。"

        try:
            resp = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=self.build_messages(clean_input, emotion, history, knowledge_context),
                temperature=0.65,
                max_tokens=300,
            )
            content = (resp.choices[0].message.content or "").strip()
            return content or self.fallback_replies.get(emotion_label, self.fallback_replies["neutral"])
        except Exception as exc:
            print(f"[LLM Error] {exc}")
            return self.fallback_replies.get(emotion_label, self.fallback_replies["neutral"])


_llm_service = LLMService()


def get_llm_service() -> LLMService:
    return _llm_service
