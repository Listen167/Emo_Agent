from typing import Optional

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
