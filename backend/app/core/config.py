from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudentVoiceAgent"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/chat.db"
    LLM_BASE_URL: str = "http://localhost:8080/v1"
    LLM_API_KEY: str = "empty"
    LLM_MODEL: str = "deepseek-chat"
    AUDIO_EMOTION_WEIGHT: float = 0.65
    TTS_VOICE: str = "zh-CN-YunxiNeural"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    MEME_PATH: str = str(Path(__file__).parent.parent.parent.parent / "data/memes.json")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()