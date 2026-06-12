from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.time import utc_now
from app.models.message import GrowthMemory, GrowthProfile, UserProfile
from app.schemas.growth import GrowthMemoryCreate, GrowthMemoryItem, GrowthProfileItem, GrowthProfileUpdate, GrowthStateItem


router = APIRouter(prefix="/api/growth", tags=["成长中心"])


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


async def _get_or_create_growth_profile(session_id: str, db: AsyncSession) -> GrowthProfile:
    clean_session_id = session_id.strip()
    if not clean_session_id:
        raise HTTPException(status_code=400, detail="缺少 session_id")

    result = await db.execute(select(GrowthProfile).where(GrowthProfile.session_id == clean_session_id))
    profile = result.scalar_one_or_none()
    if profile is not None:
        return profile

    profile = GrowthProfile(
        session_id=clean_session_id,
        nickname="胶片旅人",
        personality="warm",
        weekly_goal="每天留下一次真实记录",
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def _load_memories(session_id: str, db: AsyncSession) -> list[GrowthMemory]:
    result = await db.execute(
        select(GrowthMemory)
        .where(GrowthMemory.session_id == session_id)
        .order_by(desc(GrowthMemory.created_at), desc(GrowthMemory.id))
        .limit(200)
    )
    return list(result.scalars().all())


def _profile_item(profile: GrowthProfile) -> GrowthProfileItem:
    return GrowthProfileItem(
        session_id=profile.session_id,
        nickname=profile.nickname,
        current_state=profile.current_state,
        focus=profile.focus,
        personality=profile.personality or "warm",
        weekly_goal=profile.weekly_goal,
        setup_completed=bool(profile.setup_completed),
        private_mode=bool(profile.private_mode),
        anonymous_default=bool(profile.anonymous_default),
        crisis_guard=bool(profile.crisis_guard),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def _memory_item(memory: GrowthMemory) -> GrowthMemoryItem:
    return GrowthMemoryItem(
        id=memory.id,
        category=memory.category,
        content=memory.content,
        created_at=memory.created_at,
    )


async def _state_item(profile: GrowthProfile, db: AsyncSession) -> GrowthStateItem:
    memories = await _load_memories(profile.session_id, db)
    return GrowthStateItem(
        profile=_profile_item(profile),
        memories=[_memory_item(memory) for memory in memories],
    )


async def _sync_user_profile(profile: GrowthProfile, db: AsyncSession) -> None:
    nickname = _clean_optional(profile.nickname)
    if not nickname:
        return
    result = await db.execute(select(UserProfile).where(UserProfile.session_id == profile.session_id))
    user_profile = result.scalar_one_or_none()
    if user_profile is None:
        user_profile = UserProfile(session_id=profile.session_id, nickname=nickname)
        db.add(user_profile)
    else:
        user_profile.nickname = nickname
        user_profile.updated_at = utc_now()


@router.get("", response_model=GrowthStateItem)
async def get_growth_state(session_id: str, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_growth_profile(session_id, db)
    return await _state_item(profile, db)


@router.put("", response_model=GrowthStateItem)
async def update_growth_profile(payload: GrowthProfileUpdate, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_growth_profile(payload.session_id, db)

    if payload.nickname is not None:
        profile.nickname = _clean_optional(payload.nickname) or "胶片旅人"
    if payload.current_state is not None:
        profile.current_state = _clean_optional(payload.current_state)
    if payload.focus is not None:
        profile.focus = _clean_optional(payload.focus)
    if payload.personality is not None:
        profile.personality = _clean_optional(payload.personality) or "warm"
    if payload.weekly_goal is not None:
        profile.weekly_goal = _clean_optional(payload.weekly_goal) or "每天留下一次真实记录"
    if payload.setup_completed is not None:
        profile.setup_completed = payload.setup_completed
    if payload.private_mode is not None:
        profile.private_mode = payload.private_mode
    if payload.anonymous_default is not None:
        profile.anonymous_default = payload.anonymous_default
    if payload.crisis_guard is not None:
        profile.crisis_guard = payload.crisis_guard

    profile.updated_at = utc_now()
    await _sync_user_profile(profile, db)
    await db.commit()
    await db.refresh(profile)
    return await _state_item(profile, db)


@router.post("/memories", response_model=GrowthMemoryItem)
async def create_growth_memory(payload: GrowthMemoryCreate, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_growth_profile(payload.session_id, db)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="记忆内容不能为空")

    memory = GrowthMemory(
        session_id=profile.session_id,
        category=payload.category.strip() or "目标",
        content=content,
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return _memory_item(memory)


@router.delete("/memories/{memory_id}")
async def delete_growth_memory(memory_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GrowthMemory).where(GrowthMemory.id == memory_id, GrowthMemory.session_id == session_id.strip())
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail="记忆不存在")
    await db.delete(memory)
    await db.commit()
    return {"ok": True}


@router.delete("")
async def clear_growth_state(session_id: str, db: AsyncSession = Depends(get_db)):
    clean_session_id = session_id.strip()
    profile = await _get_or_create_growth_profile(clean_session_id, db)
    memories = await _load_memories(clean_session_id, db)
    for memory in memories:
        await db.delete(memory)
    await db.delete(profile)
    await db.commit()
    return {"ok": True}
