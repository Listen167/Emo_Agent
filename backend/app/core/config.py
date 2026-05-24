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
    MEDIA_DIR: Path = DATA_DIR / "media"
    MEME_PATH: Path = DATA_DIR / "memes.json"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{(DATA_DIR / 'chat.db').as_posix()}"
    LLM_BASE_URL: str = "http://localhost:8080/v1"
    LLM_API_KEY: str = "empty"
    LLM_MODEL: str = "deepseek-chat"
    AUDIO_EMOTION_WEIGHT: float = 0.65
    RAG_ENABLED: bool = False
    RAG_EMBEDDING_ENABLED: bool = True
    RAG_EMBEDDING_MODEL_DIR: Path = PROJECT_ROOT / "models" / "bge-small-zh-v1.5"
    RAG_KEYWORD_WEIGHT: float = 0.35
    RAG_VECTOR_WEIGHT: float = 0.65
    TTS_ENABLED: bool = True
    TTS_PROVIDER: str = "edge"
    TTS_VOICE: str = "zh-CN-YunxiNeural"
    TTS_ALLOW_WINDOWS_FALLBACK: bool = False
    KOKORO_MODEL_DIR: Path = PROJECT_ROOT / "models" / "kokoro-zh"
    KOKORO_VOICE: str = "zf_001"
    KOKORO_LANG_CODE: str = "z"
    KOKORO_DEVICE: str | None = None
    KOKORO_SAMPLE_RATE: int = 24000
    KOKORO_SPEED: float = 1.0
    KNOWLEDGE_RAW_DIR: Path = PROJECT_ROOT / "knowledge" / "raw"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
