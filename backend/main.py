import argparse
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import asr, chat, growth, life, mood, plaza, profile, resume, town
from app.core.config import settings
from app.core.database import init_db


def _apply_runtime_tts_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--tts-mode", choices=["local", "api"], default=None)
    parser.add_argument("--tts-provider", choices=["edge", "windows", "kokoro", "tencent", "api"], default=None)
    parser.add_argument("--tts-voice", default=None)
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    if args.tts_provider:
        settings.TTS_PROVIDER = "tencent" if args.tts_provider == "api" else args.tts_provider
    elif args.tts_mode == "api":
        settings.TTS_PROVIDER = "tencent"
    elif args.tts_mode == "local":
        settings.TTS_PROVIDER = settings.TTS_LOCAL_PROVIDER

    if args.tts_voice:
        settings.TTS_VOICE = args.tts_voice

    os.environ["TTS_PROVIDER"] = settings.TTS_PROVIDER
    os.environ["TTS_VOICE"] = settings.TTS_VOICE
    print(f"[Runtime] TTS_PROVIDER={settings.TTS_PROVIDER}")
    return args


_runtime_args = _apply_runtime_tts_args()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.TTS_DIR.mkdir(parents=True, exist_ok=True)
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat.router)
app.include_router(asr.router)
app.include_router(growth.router)
app.include_router(life.router)
app.include_router(mood.router)
app.include_router(plaza.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(town.router)
app.mount("/data", StaticFiles(directory=str(settings.DATA_DIR)), name="data")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
