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
    ASR_LANGUAGE: str = "zh"
    ASR_DEVICE: str | None = None
    ASR_FORCE_SIMPLIFIED: bool = True
    RAG_ENABLED: bool = False
    RAG_EMBEDDING_ENABLED: bool = True
    RAG_EMBEDDING_MODEL_DIR: Path = PROJECT_ROOT / "models" / "bge-small-zh-v1.5"
    RAG_KEYWORD_WEIGHT: float = 0.35
    RAG_VECTOR_WEIGHT: float = 0.65
    TTS_ENABLED: bool = True
    TTS_PROVIDER: str = "edge"
    TTS_LOCAL_PROVIDER: str = "edge"
    TTS_VOICE: str = "zh-CN-YunxiNeural"
    XIAOXI_TTS_VOICE: str = ""
    TTS_ALLOW_WINDOWS_FALLBACK: bool = False
    TENCENTCLOUD_SECRET_ID: str = ""
    TENCENTCLOUD_SECRET_KEY: str = ""
    TENCENTCLOUD_APP_ID: int = 0
    TENCENT_TTS_REGION: str = "ap-guangzhou"
    TENCENT_TTS_VOICE_TYPE: int = 101016
    TENCENT_TTS_FAST_VOICE_TYPE: str = ""
    TENCENT_TTS_CODEC: str = "mp3"
    TENCENT_TTS_SAMPLE_RATE: int = 16000
    TENCENT_TTS_PRIMARY_LANGUAGE: int = 1
    TENCENT_TTS_MODEL_TYPE: int = 1
    TENCENT_TTS_PROJECT_ID: int = 0
    TENCENT_TTS_VOLUME: float = 0.0
    TENCENT_TTS_SPEED: float = 0.0
    TENCENT_TTS_SEGMENT_RATE: int = 0
    TENCENT_TTS_ENABLE_EMOTION: bool = False
    TENCENT_TTS_EMOTION_INTENSITY: int = 100
    TENCENT_TTS_MAX_CHARS: int = 150
    TENCENT_STREAM_TTS_ENABLED: bool = True
    TENCENT_STREAM_TTS_VOICE_TYPE: int = 101016
    TENCENT_STREAM_TTS_CODEC: str = "mp3"
    TENCENT_STREAM_TTS_SAMPLE_RATE: int = 16000
    TENCENT_STREAM_TTS_EXPIRED_SECONDS: int = 86400
    KOKORO_MODEL_DIR: Path = PROJECT_ROOT / "models" / "kokoro-zh"
    KOKORO_VOICE: str = "zf_001"
    KOKORO_LANG_CODE: str = "z"
    KOKORO_DEVICE: str | None = None
    KOKORO_SAMPLE_RATE: int = 24000
    KOKORO_SPEED: float = 1.0
    KNOWLEDGE_RAW_DIR: Path = PROJECT_ROOT / "knowledge" / "raw"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "*"]
    # 生产环境（CloudBase + 内网穿透）建议设置 CORS_ORIGINS=["*"]
    # 或指定具体域名: CORS_ORIGINS=["https://你的环境.tcloudbaseapp.com"]


settings = Settings()


def get_xiaoxi_tts_voice() -> str | None:
    return (settings.XIAOXI_TTS_VOICE or settings.TTS_VOICE or "").strip() or None
