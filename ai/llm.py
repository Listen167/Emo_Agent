import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from openai import OpenAI
from app.core.config import settings

_client = OpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)

def generate(user_input: str, emotion: dict, meme: str) -> str:
    sys_map = {
        "happy": "用户现在很开心。回复要活泼、有网感，顺势玩梗。",
        "sad": "用户情绪低落。回复要温柔共情，像学长学姐安慰。",
        "angry": "用户有点暴躁。先顺毛安抚，别讲大道理。",
        "anxious": "用户焦虑紧张（可能DDL）。提供拆解建议，语气坚定。",
        "neutral": "正常交流，适度加入学生圈热梗。",
        "surprised": "用户惊讶。用开放探索语气回应。"
    }
    sys_prompt = f"""你是一个懂大学生语境的AI搭子。当前情绪：{emotion['label']}。
策略：{sys_map.get(emotion['label'], '')}
热梗：{meme} (自然融入1个即可)
要求：口语化、接地气、不超过120字。"""

    resp = _client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_input}],
        temperature=0.8, max_tokens=256
    )
    return resp.choices[0].message.content.strip()