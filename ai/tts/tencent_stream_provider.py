import asyncio
import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import AsyncIterator
from urllib.parse import quote, urlencode

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from .text import sanitize_for_tts


_HOST = "tts.cloud.tencent.com"
_PATH = "/stream_wsv2"


def _speed_for_emotion(emotion: str) -> float:
    return {
        "happy": 0.6,
        "sad": -0.4,
        "angry": 0.4,
        "anxious": 0.2,
        "neutral": settings.TENCENT_TTS_SPEED,
        "surprised": 0.8,
    }.get(emotion, settings.TENCENT_TTS_SPEED)


def _emotion_category(emotion: str) -> str:
    return {
        "happy": "happy",
        "sad": "sad",
        "angry": "angry",
        "anxious": "fear",
        "neutral": "neutral",
        "surprised": "amaze",
    }.get(emotion, "neutral")


def _voice_type(voice: str | None) -> int:
    if voice and voice.strip().isdigit():
        return int(voice.strip())
    return settings.TENCENT_STREAM_TTS_VOICE_TYPE or settings.TENCENT_TTS_VOICE_TYPE


def _build_ws_url(session_id: str, emotion: str, voice: str | None = None) -> str:
    if not settings.TENCENTCLOUD_APP_ID:
        raise RuntimeError("missing TENCENTCLOUD_APP_ID")
    if not settings.TENCENTCLOUD_SECRET_ID or not settings.TENCENTCLOUD_SECRET_KEY:
        raise RuntimeError("missing TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY")

    timestamp = int(time.time())
    params: dict[str, object] = {
        "Action": "TextToStreamAudioWSv2",
        "AppId": int(settings.TENCENTCLOUD_APP_ID),
        "Codec": settings.TENCENT_STREAM_TTS_CODEC,
        "EnableSubtitle": False,
        "Expired": timestamp + settings.TENCENT_STREAM_TTS_EXPIRED_SECONDS,
        "SampleRate": settings.TENCENT_STREAM_TTS_SAMPLE_RATE,
        "SecretId": settings.TENCENTCLOUD_SECRET_ID,
        "SessionId": session_id,
        "Speed": _speed_for_emotion(emotion),
        "Timestamp": timestamp,
        "VoiceType": _voice_type(voice),
        "Volume": settings.TENCENT_TTS_VOLUME,
    }
    if settings.TENCENT_TTS_FAST_VOICE_TYPE:
        params["VoiceType"] = 200000000
        params["FastVoiceType"] = settings.TENCENT_TTS_FAST_VOICE_TYPE
    if settings.TENCENT_TTS_ENABLE_EMOTION:
        params["EmotionCategory"] = _emotion_category(emotion)
        params["EmotionIntensity"] = settings.TENCENT_TTS_EMOTION_INTENSITY
    if settings.TENCENT_TTS_SEGMENT_RATE:
        params["SegmentRate"] = settings.TENCENT_TTS_SEGMENT_RATE

    sorted_items = sorted(params.items(), key=lambda item: item[0])
    query_for_sign = "&".join(f"{key}={value}" for key, value in sorted_items)
    sign_text = f"GET{_HOST}{_PATH}?{query_for_sign}"
    digest = hmac.new(
        settings.TENCENTCLOUD_SECRET_KEY.encode("utf-8"),
        sign_text.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    query = urlencode(sorted_items)
    return f"wss://{_HOST}{_PATH}?{query}&Signature={quote(signature, safe='')}"


def _ensure_sentence(text: str) -> str:
    clean = sanitize_for_tts(text)
    if not clean:
        return ""
    if clean[-1] in "。！？；.!?;\n":
        return clean
    return f"{clean}。"


class TencentStreamTTSClient:
    def __init__(self, emotion: str, voice: str | None = None) -> None:
        self.emotion = emotion
        self.voice = voice
        self.session_id = str(uuid.uuid4())
        self._queue: asyncio.Queue[dict] = asyncio.Queue()
        self._text_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._task: asyncio.Task | None = None

    async def __aenter__(self):
        self._task = asyncio.create_task(self._run())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.finish()
        if self._task:
            await self._task

    async def send_text(self, text: str) -> None:
        clean = _ensure_sentence(text)
        if clean:
            await self._text_queue.put(clean)

    async def finish(self) -> None:
        await self._text_queue.put(None)

    async def events(self) -> AsyncIterator[dict]:
        while True:
            event = await self._queue.get()
            yield event
            if event.get("type") in {"tts_done", "tts_error"}:
                return

    async def _run(self) -> None:
        try:
            import websockets

            url = _build_ws_url(self.session_id, self.emotion, self.voice)
            async with websockets.connect(url, max_size=None) as ws:
                ready = False
                sender_task = asyncio.create_task(self._send_loop(ws))
                async for message in ws:
                    if isinstance(message, bytes):
                        await self._queue.put(
                            {
                                "type": "audio_delta",
                                "codec": settings.TENCENT_STREAM_TTS_CODEC,
                                "data": base64.b64encode(message).decode("ascii"),
                            }
                        )
                        continue

                    data = json.loads(message)
                    if data.get("code", 0) != 0:
                        await self._queue.put({"type": "tts_error", "message": data.get("message", "腾讯云流式语音错误")})
                        sender_task.cancel()
                        return
                    if data.get("ready") == 1 and not ready:
                        ready = True
                        await self._queue.put({"type": "tts_ready"})
                    if data.get("final") == 1:
                        await self._queue.put({"type": "tts_done"})
                        await ws.close()
                        await sender_task
                        return
        except ImportError:
            await self._queue.put({"type": "tts_error", "message": "缺少依赖 websockets，请运行 pip install websockets"})
        except Exception as exc:
            await self._queue.put({"type": "tts_error", "message": str(exc)})

    async def _send_loop(self, ws) -> None:
        while True:
            text = await self._text_queue.get()
            if text is None:
                await ws.send(
                    json.dumps(
                        {
                            "session_id": self.session_id,
                            "message_id": str(uuid.uuid4()),
                            "action": "ACTION_COMPLETE",
                            "data": "",
                        },
                        ensure_ascii=False,
                    )
                )
                return
            await ws.send(
                json.dumps(
                    {
                        "session_id": self.session_id,
                        "message_id": str(uuid.uuid4()),
                        "action": "ACTION_SYNTHESIS",
                        "data": text,
                    },
                    ensure_ascii=False,
                )
            )
