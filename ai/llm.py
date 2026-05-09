import sys
from pathlib import Path

from openai import OpenAI

sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.core.config import settings


_client = OpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
_EMOTION_PROMPTS = {
    "happy": "用户现在情绪很好，回复轻松一点，可以顺着开心的感觉聊下去。",
    "sad": "用户有点低落，先安抚情绪，再给温和回应，不要说教。",
    "angry": "用户有明显烦躁或生气，先接住情绪，语气稳一点，别拱火。",
    "anxious": "用户焦虑或紧张，先给安定感，再给简短可执行的建议。",
    "neutral": "正常交流，语气自然、口语化，像熟悉的同龄搭子。",
    "surprised": "用户有惊讶情绪，语气可以更灵动一点，顺着惊讶点回应。",
}
_FALLBACK_REPLIES = {
    "happy": "这波状态不错啊，听起来你现在挺上头的。展开说说，我陪你一起接着唠。",
    "sad": "先抱抱你，别一个人闷着。你愿意的话，把卡住你的点跟我说说，我们一起理。",
    "angry": "这事确实容易让人上火，我能接住。你先把最气的那一点说出来，我们先拆它。",
    "anxious": "先别急，事情一件一件来。你把最担心的点丢给我，我帮你一起排优先级。",
    "neutral": "我在，直接说就行。你想聊想问，或者想让我陪你分析都可以。",
    "surprised": "这下确实有点突然，挺有戏剧性的。你把来龙去脉说下，我跟你一起捋。",
}


def generate(user_input: str, emotion: dict, meme: str, history: list[dict[str, str]] | None = None) -> str:
    clean_input = user_input.strip()
    if not clean_input:
        return "我刚刚没太听清，你可以再说一遍，或者直接打字给我。"

    emotion_label = str(emotion.get("label", "neutral"))
    emotion_prompt = _EMOTION_PROMPTS.get(emotion_label, _EMOTION_PROMPTS["neutral"])
    sys_prompt = (
        "你是一个懂中国大学生日常表达的 AI 聊天搭子。\n"
        f"当前识别到的用户情绪：{emotion_label}\n"
        f"回复策略：{emotion_prompt}\n"
        f"可自然带入一个轻量网络梗：{meme}\n"
        "要求：\n"
        "1. 先接住用户当下情绪，再回应内容。\n"
        "2. 语气自然、口语化，不要像客服，也不要说教。\n"
        "3. 控制在 50 到 120 个中文字符。\n"
        "4. 不要输出分点、情绪标签、舞台说明或动作描写。\n"
        "5. 不要写（停顿）、（笑）、（拍拍肩）、[叹气]、*抱抱* 这类会被直接念出来的内容。"
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": sys_prompt}]
    for item in history or []:
        role = item.get("role", "")
        content = item.get("content", "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": clean_input})

    try:
        resp = _client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=256,
        )
        content = (resp.choices[0].message.content or "").strip()
        return content or _FALLBACK_REPLIES.get(emotion_label, _FALLBACK_REPLIES["neutral"])
    except Exception as exc:
        print(f"[LLM Error] {exc}")
        return _FALLBACK_REPLIES.get(emotion_label, _FALLBACK_REPLIES["neutral"])
