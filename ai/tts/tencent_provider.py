import base64
import json
import uuid
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from .text import sanitize_for_tts


_SPEED_BY_EMOTION = {
    "happy": 0.6,
    "sad": -0.4,
    "angry": 0.4,
    "anxious": 0.2,
    "neutral": 0.0,
    "surprised": 0.8,
}

_EMOTION_CATEGORY = {
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "anxious": "fear",
    "neutral": "neutral",
    "surprised": "amaze",
}


def _clean_text_for_tencent(text: str) -> str:
    clean_text = sanitize_for_tts(text)
    if not clean_text:
        return ""
    max_chars = max(settings.TENCENT_TTS_MAX_CHARS, 1)
    if len(clean_text) <= max_chars:
        return clean_text

    clipped = clean_text[:max_chars]
    for mark in ("。", "！", "？", "；", ".", "!", "?", ";"):
        index = clipped.rfind(mark)
        if index >= max_chars // 2:
            return clipped[: index + 1].strip()
    return clipped.strip()


def _voice_type(voice: str | None) -> int:
    if voice and voice.strip().isdigit():
        return int(voice.strip())
    return settings.TENCENT_TTS_VOICE_TYPE


def synthesize(text: str, session_id: str, emotion: str, voice: str | None = None) -> str:
    clean_text = _clean_text_for_tencent(text)
    if not clean_text:
        return ""
    if not settings.TENCENTCLOUD_SECRET_ID or not settings.TENCENTCLOUD_SECRET_KEY:
        print("[TTS Tencent Error] missing TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY")
        return ""

    out_dir = settings.TTS_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    codec = settings.TENCENT_TTS_CODEC.lower().strip() or "mp3"
    out_path = out_dir / f"{emotion}_{uuid.uuid4().hex[:10]}.{codec}"

    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.tts.v20190823 import models, tts_client

        cred = credential.Credential(settings.TENCENTCLOUD_SECRET_ID, settings.TENCENTCLOUD_SECRET_KEY)
        http_profile = HttpProfile()
        http_profile.endpoint = "tts.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = tts_client.TtsClient(cred, settings.TENCENT_TTS_REGION, client_profile)

        params = {
            "Text": clean_text,
            "SessionId": f"{session_id}-{uuid.uuid4().hex[:8]}",
            "Volume": settings.TENCENT_TTS_VOLUME,
            "Speed": _SPEED_BY_EMOTION.get(emotion, settings.TENCENT_TTS_SPEED),
            "ProjectId": settings.TENCENT_TTS_PROJECT_ID,
            "ModelType": settings.TENCENT_TTS_MODEL_TYPE,
            "VoiceType": _voice_type(voice),
            "PrimaryLanguage": settings.TENCENT_TTS_PRIMARY_LANGUAGE,
            "SampleRate": settings.TENCENT_TTS_SAMPLE_RATE,
            "Codec": codec,
            "EnableSubtitle": False,
            "SegmentRate": settings.TENCENT_TTS_SEGMENT_RATE,
        }
        if settings.TENCENT_TTS_FAST_VOICE_TYPE:
            params["VoiceType"] = 200000000
            params["FastVoiceType"] = settings.TENCENT_TTS_FAST_VOICE_TYPE
        if settings.TENCENT_TTS_ENABLE_EMOTION:
            params["EmotionCategory"] = _EMOTION_CATEGORY.get(emotion, "neutral")
            params["EmotionIntensity"] = settings.TENCENT_TTS_EMOTION_INTENSITY

        req = models.TextToVoiceRequest()
        req.from_json_string(json.dumps(params, ensure_ascii=False))
        resp = client.TextToVoice(req)
        audio = base64.b64decode(resp.Audio)
        if not audio:
            raise RuntimeError("Tencent TTS returned empty audio")

        out_path.write_bytes(audio)
        return str(Path("tts") / session_id / out_path.name)
    except ImportError:
        print("[TTS Tencent Error] install dependency: pip install tencentcloud-sdk-python")
        out_path.unlink(missing_ok=True)
        return ""
    except Exception as exc:
        print(f"[TTS Tencent Error] {exc}")
        out_path.unlink(missing_ok=True)
        return ""
