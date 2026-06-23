import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ai.asr import get_asr_service
from ai.llm import get_llm_service
from ai.tts import get_tts_service
from app.core.config import get_xiaoxi_tts_voice, settings
from app.schemas.resume import (
    ResumeAnalyzeRequest,
    ResumeAnalyzeResponse,
    ResumeAssistantMessage,
    ResumeAssistantResponse,
    ResumePolishRequest,
    ResumePolishResponse,
)


router = APIRouter(prefix="/api/resume", tags=["简历工坊"])

RESUME_ASSISTANT_SYSTEM_PROMPT = """你是简历工坊里的小曦，专门帮助大学生完善简历和练习面试。

你只能使用本次请求提供的信息：当前简历、目标岗位/JD、当前悬浮窗聊天记录、用户本轮输入。不要读取或假设其他聊天页的历史。

工作方式：
1. 默认处理简历补充、润色和结构优化。用户提供大学经历时，先追问关键缺口，再给可直接填入简历的表达。不能编造学校、公司、奖项、指标、项目结果或技术栈。
2. 如果用户提到“面试模拟”“模拟面试”“开始面试”“面试练习”等意图，切换为面试官模式。
3. 面试官模式总共 10 题。每次只输出 1 个问题，问题要结合简历、用户基本情况、目标岗位/JD、项目技术栈和当前市场对岗位的常见要求。可以对上一题追问，也可以换到新的简历/JD问题。
4. 当悬浮窗历史里已经有 10 次用户面试回答后，输出评分和修改措施，不再继续提问。
5. 评分必须包含：总分/100、维度评分、主要优势、主要风险、简历修改建议、面试表达改进建议、下一轮练习重点。
6. 语气保持小曦的人设：温和、直接、专业。不要寒暄过长，不要输出 Markdown 代码块。
"""


def _generate_resume_reply(prompt: str, max_chars: int = 2200) -> str:
    try:
        llm = get_llm_service()
        reply = llm.generate(
            prompt,
            {"label": "neutral"},
            history=[],
            knowledge_context=None,
        ).strip()
        return reply[:max_chars]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _generate_resume_assistant_llm(user_prompt: str, max_chars: int = 3600) -> str:
    try:
        llm = get_llm_service()
        resp = llm.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": RESUME_ASSISTANT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.45,
            max_tokens=900,
        )
        reply = (resp.choices[0].message.content or "").strip()
        return reply[:max_chars] or "我没能生成有效回复。你可以再补充一点经历或岗位信息。"
    except Exception as exc:
        print(f"[Resume Assistant LLM Error] {exc}")
        return "当前简历助手暂时连接失败。你可以先继续补充经历，稍后我再帮你整理。"


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


def _parse_assistant_history(raw_history: str | None) -> list[ResumeAssistantMessage]:
    if not raw_history:
        return []
    try:
        parsed = json.loads(raw_history)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="悬浮窗历史格式错误") from exc
    if not isinstance(parsed, list):
        raise HTTPException(status_code=400, detail="悬浮窗历史必须是数组")
    messages: list[ResumeAssistantMessage] = []
    for item in parsed[-30:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append(ResumeAssistantMessage(role=role, content=content[:3000]))
    return messages


def _is_interview_intent(text: str, history: list[ResumeAssistantMessage]) -> bool:
    joined = "\n".join([*(message.content for message in history), text]).lower()
    has_start_signal = any(term in joined for term in ("面试模拟", "模拟面试", "开始面试", "面试练习", "mock interview", "interview"))
    has_question_signal = any(
        message.role == "assistant" and "/10" in message.content and "问题" in message.content
        for message in history
    )
    return has_start_signal or has_question_signal


def _count_interview_answers(history: list[ResumeAssistantMessage]) -> int:
    interview_started = False
    answer_count = 0
    for message in history:
        content = message.content.lower()
        if message.role == "user" and any(term in content for term in ("面试模拟", "模拟面试", "开始面试", "面试练习", "mock interview", "interview")):
            interview_started = True
            continue
        if interview_started and message.role == "user":
            answer_count += 1
    return answer_count


def _generate_resume_assistant_reply(
    user_text: str,
    resume_text: str,
    job_description: str | None,
    interview_role: str | None,
    history: list[ResumeAssistantMessage],
) -> tuple[str, str, int | None]:
    is_interview = _is_interview_intent(user_text, history)
    answer_count = _count_interview_answers(history) if is_interview else 0
    if is_interview and answer_count >= 10:
        mode = "interview_summary"
        next_question_index: int | None = None
        task_instruction = (
            "现在结束本轮模拟面试。请根据悬浮窗历史中用户的 10 次回答输出面试评分和修改措施。"
            "不要再提出第 11 个问题。"
        )
    elif is_interview:
        mode = "interview"
        next_question_index = min(answer_count + 1, 10)
        task_instruction = (
            f"现在处于面试官模式。请输出第 {next_question_index}/10 个问题。"
            "如果上一题回答值得追问，可以追问；否则围绕简历、岗位要求或项目技术栈切换到新的问题。"
            "只输出一个问题，问题前标注题号。"
        )
    else:
        mode = "resume"
        next_question_index = None
        task_instruction = (
            "现在处于简历润色/补充模式。请根据用户本轮输入和悬浮窗历史，帮助补全大学经历、提炼简历要点或给出可粘贴的改写。"
            "如果信息不足，先问 1-3 个关键问题；如果信息足够，直接给优化后的简历表达。"
        )

    history_text = "\n".join(f"{message.role}: {message.content}" for message in history[-20:]) or "无"
    prompt = (
        f"当前任务：{task_instruction}\n\n"
        f"目标岗位：{(interview_role or '').strip() or '未填写'}\n\n"
        f"当前简历：\n{resume_text.strip() or '未填写'}\n\n"
        f"目标岗位/JD：\n{(job_description or '').strip() or '未填写'}\n\n"
        f"悬浮窗历史：\n{history_text}\n\n"
        f"用户本轮输入：\n{user_text.strip()}"
    )
    reply = _generate_resume_assistant_llm(prompt, max_chars=3600)
    return reply, mode, next_question_index


async def _resolve_assistant_text(text: str | None, audio: UploadFile | None, session_id: str) -> str:
    final_text = (text or "").strip()
    if not final_text and audio and audio.filename:
        suffix = Path(audio.filename).suffix.lower() or ".wav"
        upload_dir = settings.UPLOAD_DIR / f"resume-{session_id}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{uuid.uuid4().hex}{suffix}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())
        transcribed_text, _ = get_asr_service().transcribe(str(file_path))
        final_text = (transcribed_text or "").strip()
    return final_text


@router.post("/polish", response_model=ResumePolishResponse)
async def polish_resume_text(payload: ResumePolishRequest):
    jd_part = (
        f"\n目标岗位 JD：\n{payload.job_description.strip()}\n"
        if payload.job_description and payload.job_description.strip()
        else ""
    )
    prompt = (
        "你是中文简历修改助手。请把下面的简历内容改写得更适合投递，要求：\n"
        "1. 保留真实信息，不编造公司、奖项、指标或技术栈；\n"
        "2. 优先使用动作 + 方法 + 结果的表达；\n"
        "3. 如果原文是多行经历，输出同样适合简历的多行要点；\n"
        "4. 不要输出解释、标题、寒暄或 Markdown 代码块，只输出可直接粘贴进简历的正文。\n"
        f"{jd_part}\n"
        f"简历板块：{payload.section}\n"
        f"原文：\n{payload.content.strip()}"
    )
    return ResumePolishResponse(text=_generate_resume_reply(prompt, max_chars=1800))


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume_match(payload: ResumeAnalyzeRequest):
    prompt = (
        "你是求职简历匹配分析助手。请基于简历和岗位 JD 做中文分析，要求：\n"
        "1. 不要编造简历里没有的信息；\n"
        "2. 输出四部分：匹配亮点、缺失关键词、建议改写、下一步补充材料；\n"
        "3. 每部分控制在 3 条以内，建议要具体可执行；\n"
        "4. 不要输出寒暄。\n\n"
        f"简历内容：\n{payload.resume_text.strip()}\n\n"
        f"岗位 JD：\n{payload.job_description.strip()}"
    )
    return ResumeAnalyzeResponse(analysis=_generate_resume_reply(prompt, max_chars=2600))


@router.post("/assistant", response_model=ResumeAssistantResponse)
async def resume_assistant(
    text: Optional[str] = Form(None),
    resume_text: str = Form(""),
    job_description: Optional[str] = Form(None),
    interview_role: Optional[str] = Form(None),
    history: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    enable_tts: bool = Form(True),
    audio: Optional[UploadFile] = File(None),
):
    sid = session_id or str(uuid.uuid4())
    user_text = await _resolve_assistant_text(text, audio, sid)
    if not user_text:
        raise HTTPException(status_code=400, detail="缺少文本或语音输入")

    assistant_history = _parse_assistant_history(history)
    reply, mode, question_index = _generate_resume_assistant_reply(
        user_text=user_text,
        resume_text=resume_text,
        job_description=job_description,
        interview_role=interview_role,
        history=assistant_history,
    )

    tts_url = None
    if enable_tts and settings.TTS_ENABLED and reply.strip():
        tts_path = get_tts_service().synthesize(reply, f"resume-{sid}", "neutral", get_xiaoxi_tts_voice())
        tts_url = _build_tts_audio_url(tts_path)

    return ResumeAssistantResponse(
        text=reply,
        user_text=user_text,
        mode=mode,
        interview_question_index=question_index,
        tts_audio_url=tts_url,
    )
