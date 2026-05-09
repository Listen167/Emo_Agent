from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        case_sensitive=True,
    )

    PROJECT_NAME: str = "StudentVoiceAgent"
    PROJECT_ROOT: Path = PROJECT_ROOT
    BACKEND_DIR: Path = BACKEND_DIR
    DATA_DIR: Path = DATA_DIR
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    TTS_DIR: Path = DATA_DIR / "tts"
    MEME_PATH: Path = DATA_DIR / "memes.json"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{(DATA_DIR / 'chat.db').as_posix()}"
    LLM_BASE_URL: str = "http://localhost:8080/v1"
    LLM_API_KEY: str = "empty"
    LLM_MODEL: str = "deepseek-chat"
    AUDIO_EMOTION_WEIGHT: float = 0.65
    TTS_VOICE: str = "zh-CN-YunxiNeural"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
