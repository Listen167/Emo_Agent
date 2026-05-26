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
            "happy": "用户情绪偏积极。保持自然轻快，但不要过度兴奋；先回应问题，再给出清晰结论。",
            "sad": "用户情绪偏低落。语气要温和、稳定，先承接情绪，再给出可执行的信息。",
            "angry": "用户情绪偏烦躁。避免说教和绕弯，直接解决问题，语气克制。",
            "anxious": "用户情绪偏焦虑。把信息拆清楚，减少不确定性，优先给明确步骤。",
            "neutral": "用户情绪平稳。保持简洁、准确、实用。",
            "surprised": "用户情绪偏惊讶。先澄清事实，再解释原因和下一步。",
        }
        self.fallback_replies = {
            "happy": "当前大模型连接失败，但我收到了你的消息。你可以稍后重试，或先补充更具体的问题。",
            "sad": "当前大模型连接失败。你可以先把最想解决的一点告诉我，恢复后我会优先处理。",
            "angry": "当前大模型连接失败。建议先检查后端日志里的 LLM Error、API Key、base_url 和模型名。",
            "anxious": "当前大模型连接失败。先不用反复改代码，优先检查网络、API Key、base_url 和模型名。",
            "neutral": "当前大模型连接失败，请稍后重试，或检查后端 LLM 配置。",
            "surprised": "当前大模型连接失败，所以没能生成完整回复。建议先看后端日志里的 LLM Error。",
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
                        "下面是从本地学校知识库检索到的资料。回答校园政策、竞赛级别、推免加分等问题时，"
                        "必须优先依据这些资料，不要泛泛建议用户去问教务处、辅导员或官网。\n"
                        "如果资料能支持结论，请直接给出结论，并说明依据来自哪一条资料。\n"
                        "如果资料只支持部分结论，请明确说“根据现有资料只能确定...”，不要编造缺失信息。\n"
                        "如果不同资料需要组合推理，请先确定竞赛级别，再根据加分表计算或说明还缺少获奖等次、成员排序。\n\n"
                        "本地知识库资料：\n"
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
            return "我刚才没有识别到有效内容。你可以再说一遍，或者直接用文字告诉我。"

        try:
            resp = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=self.build_messages(clean_input, emotion, history, knowledge_context),
                temperature=0.45,
                max_tokens=500,
            )
            content = (resp.choices[0].message.content or "").strip()
            return content or self.fallback_replies.get(emotion_label, self.fallback_replies["neutral"])
        except Exception as exc:
            print(f"[LLM Error] {exc}")
            return self.fallback_replies.get(emotion_label, self.fallback_replies["neutral"])


_llm_service = LLMService()


def get_llm_service() -> LLMService:
    return _llm_service
