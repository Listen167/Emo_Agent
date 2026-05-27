import asyncio
import uuid
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from .text import sanitize_for_tts


_EDGE_TTS_ENABLED = True
_EDGE_RATE_BY_EMOTION = {
    "happy": "+8%",
    "sad": "-8%",
    "angry": "+4%",
    "anxious": "+2%",
    "neutral": "+0%",
    "surprised": "+8%",
}


async def _save_with_edge_tts(text: str, out_path: Path, emotion: str, voice: str | None = None) -> None:
    import edge_tts

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice or settings.TTS_VOICE,
        rate=_EDGE_RATE_BY_EMOTION.get(emotion, "+0%"),
    )
    await communicator.save(str(out_path))


def synthesize(text: str, session_id: str, emotion: str, voice: str | None = None) -> str:
    global _EDGE_TTS_ENABLED

    clean_text = sanitize_for_tts(text)
    if not clean_text or not _EDGE_TTS_ENABLED:
        return ""

    out_dir = settings.TTS_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{emotion}_{uuid.uuid4().hex[:10]}.mp3"

    try:
        asyncio.run(_save_with_edge_tts(clean_text, out_path, emotion, voice))
        if out_path.exists() and out_path.stat().st_size > 0:
            return str(Path("tts") / session_id / out_path.name)
        raise RuntimeError("edge-tts output file is empty")
    except Exception as exc:
        message = str(exc)
        print(f"[TTS Edge Error] {message}")
        out_path.unlink(missing_ok=True)
        if "403" in message or "Invalid response status" in message:
            _EDGE_TTS_ENABLED = False
        return ""
