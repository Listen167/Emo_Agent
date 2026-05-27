import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.town_service import get_town_service


router = APIRouter(prefix="/api/town", tags=["AI Town"])


class TownChatRequest(BaseModel):
    npc_name: str
    message: str
    player_id: str = "player"


@router.get("/")
async def root():
    return {
        "service": "AI Town",
        "status": "running",
        "endpoints": {
            "chat": "/api/town/chat",
            "npcs": "/api/town/npcs",
            "npcs_status": "/api/town/npcs/status",
        },
    }


@router.post("/chat")
async def chat_with_npc(request: TownChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
        return await get_town_service().chat(
            db,
            request.npc_name,
            request.message.strip(),
            request.player_id,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {exc}")


@router.post("/chat/audio")
async def chat_with_npc_audio(
    npc_name: str = Form(...),
    player_id: str = Form("player"),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        suffix = Path(audio.filename or "recording.wav").suffix.lower() or ".wav"
        upload_dir = get_town_service_upload_dir()
        file_path = upload_dir / f"{uuid.uuid4().hex}{suffix}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        text = await get_town_service().transcribe_audio(str(file_path))
        if not text:
            raise HTTPException(status_code=400, detail="语音未识别出文本")

        response = await get_town_service().chat(db, npc_name, text, player_id)
        response["user_text"] = text
        return response
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"语音对话处理失败: {exc}")


@router.get("/npcs")
async def list_npcs():
    npcs = get_town_service().list_npcs()
    return {
        "npcs": npcs,
        "total": len(npcs),
    }


@router.get("/npcs/status")
async def get_npcs_status():
    return {
        "dialogues": get_town_service().get_status(),
        "last_update": "now",
        "next_update_in": 30,
    }


@router.get("/npcs/{npc_name}/affinity")
async def get_npc_affinity(
    npc_name: str,
    player_id: str = "player",
    db: AsyncSession = Depends(get_db),
):
    try:
        affinity_info = await get_town_service().get_affinity(db, npc_name, player_id)
        return {
            "npc_name": npc_name,
            "player_id": player_id,
            **affinity_info,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/affinities")
async def get_affinities(
    player_id: str = "player",
    db: AsyncSession = Depends(get_db),
):
    return {
        "player_id": player_id,
        "affinities": await get_town_service().get_all_affinities(db, player_id),
    }


@router.put("/npcs/{npc_name}/affinity")
async def set_npc_affinity(
    npc_name: str,
    affinity: float,
    player_id: str = "player",
    db: AsyncSession = Depends(get_db),
):
    try:
        affinity_info = await get_town_service().set_affinity(db, npc_name, affinity, player_id)
        return {
            "npc_name": npc_name,
            "player_id": player_id,
            **affinity_info,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


def get_town_service_upload_dir() -> Path:
    from app.core.config import settings

    upload_dir = settings.UPLOAD_DIR / "town"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
