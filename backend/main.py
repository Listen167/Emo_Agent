import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import chat, life, mood, profile, resume, town
from app.core.config import settings
from app.core.database import init_db


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
app.include_router(life.router)
app.include_router(mood.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(town.router)
app.mount("/data", StaticFiles(directory=str(settings.DATA_DIR)), name="data")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
