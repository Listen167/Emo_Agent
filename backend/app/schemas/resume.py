from typing import Literal, Optional

from pydantic import BaseModel, Field


class ResumePolishRequest(BaseModel):
    section: str = Field(..., min_length=1, max_length=40)
    content: str = Field(..., min_length=1, max_length=3000)
    job_description: Optional[str] = Field(None, max_length=3000)


class ResumePolishResponse(BaseModel):
    text: str


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, max_length=8000)
    job_description: str = Field(..., min_length=1, max_length=6000)


class ResumeAnalyzeResponse(BaseModel):
    analysis: str


class ResumeAssistantMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=3000)


class ResumeAssistantRequest(BaseModel):
    text: Optional[str] = Field(None, max_length=3000)
    resume_text: str = Field("", max_length=10000)
    job_description: Optional[str] = Field(None, max_length=6000)
    interview_role: Optional[str] = Field(None, max_length=80)
    history: list[ResumeAssistantMessage] = Field(default_factory=list, max_length=30)
    enable_tts: bool = True


class ResumeAssistantResponse(BaseModel):
    text: str
    user_text: str
    mode: Literal["resume", "interview", "interview_summary"]
    interview_question_index: Optional[int] = None
    interview_total: int = 10
    tts_audio_url: Optional[str] = None
