import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings

from . import edge_provider, kokoro_provider, windows_provider
from .text import sanitize_for_tts


def synthesize(text: str, session_id: str, emotion: str) -> str:
    provider = settings.TTS_PROVIDER.lower().strip()

    if provider == "kokoro":
        return kokoro_provider.synthesize(text, session_id, emotion)

    if provider == "windows":
        return windows_provider.synthesize(text, session_id, emotion)

    if provider == "edge":
        path = edge_provider.synthesize(text, session_id, emotion)
        if path:
            return path
        if settings.TTS_ALLOW_WINDOWS_FALLBACK:
            return windows_provider.synthesize(text, session_id, emotion)
        print("[TTS] skipped local fallback. Set TTS_ALLOW_WINDOWS_FALLBACK=true to enable Windows TTS.")
        return ""

    print(f"[TTS] unknown provider: {settings.TTS_PROVIDER}")
    return ""
