from fastapi import APIRouter, HTTPException

from ai.llm import get_llm_service
from app.schemas.resume import (
    ResumeAnalyzeRequest,
    ResumeAnalyzeResponse,
    ResumePolishRequest,
    ResumePolishResponse,
)


router = APIRouter(prefix="/api/resume", tags=["简历工坊"])


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
