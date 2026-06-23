import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from ai.asr import get_asr_service
from app.core.config import settings
from app.schemas.asr import ASRTranscribeResponse


router = APIRouter(prefix="/api/asr", tags=["本地语音识别"])


@router.post("/transcribe", response_model=ASRTranscribeResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="缺少语音文件")

    suffix = Path(audio.filename).suffix.lower() or ".wav"
    upload_dir = settings.UPLOAD_DIR / "asr"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4().hex}{suffix}"

    try:
        with open(file_path, "wb") as f:
            f.write(await audio.read())
        text, _audio_probs = get_asr_service().transcribe(str(file_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ASRTranscribeResponse(text=(text or "").strip())
