from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.town_service import get_town_service


router = APIRouter(prefix="/api/town", tags=["AI Town"])


class TownChatRequest(BaseModel):
    npc_name: str
    message: str


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
async def chat_with_npc(request: TownChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
        return get_town_service().chat(request.npc_name, request.message.strip())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {exc}")


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
