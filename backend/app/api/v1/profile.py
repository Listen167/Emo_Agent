import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.time import utc_now
from app.models.message import UserProfile
from app.schemas.profile import ProfileEbtiUpdate, ProfileUpdate, UserProfileItem


router = APIRouter(prefix="/api/profile", tags=["个人资料"])

ALLOWED_AVATAR_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _asset_url(path_value: Optional[str]) -> Optional[str]:
    if not path_value:
        return None
    path = Path(path_value)
    relative_path = Path(*path.parts[1:]) if path.parts and path.parts[0] == "data" else path
    return f"/data/{relative_path.as_posix()}"


def _clean_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    clean = value.strip()
    return clean or None


def _to_item(profile: UserProfile) -> UserProfileItem:
    return UserProfileItem(
        id=profile.id,
        session_id=profile.session_id,
        nickname=profile.nickname,
        avatar_url=_asset_url(profile.avatar_path),
        motto=profile.motto,
        gender=profile.gender,
        ebti_type=profile.ebti_type,
        ebti_name=profile.ebti_name,
        ebti_avatar=profile.ebti_avatar,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


async def _get_or_create_profile(session_id: str, db: AsyncSession) -> UserProfile:
    clean_session_id = session_id.strip()
    if not clean_session_id:
        raise HTTPException(status_code=400, detail="缺少 session_id")

    result = await db.execute(select(UserProfile).where(UserProfile.session_id == clean_session_id))
    profile = result.scalar_one_or_none()
    if profile is not None:
        return profile

    profile = UserProfile(
        session_id=clean_session_id,
        nickname="胶片旅人",
        motto="记录每一次快门的心跳",
        gender=None,
        updated_at=utc_now(),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("", response_model=UserProfileItem)
async def get_profile(session_id: str, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_profile(session_id, db)
    return _to_item(profile)


@router.put("", response_model=UserProfileItem)
async def update_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_profile(payload.session_id, db)
    profile.nickname = _clean_optional(payload.nickname) or "胶片旅人"
    profile.motto = _clean_optional(payload.motto)
    profile.gender = _clean_optional(payload.gender)
    profile.updated_at = utc_now()
    await db.commit()
    await db.refresh(profile)
    return _to_item(profile)


@router.post("/avatar", response_model=UserProfileItem)
async def upload_avatar(
    session_id: str = Form(...),
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not avatar.filename:
        raise HTTPException(status_code=400, detail="缺少头像文件")
    suffix = Path(avatar.filename).suffix.lower()
    if suffix not in ALLOWED_AVATAR_SUFFIXES:
        raise HTTPException(status_code=400, detail="只支持 jpg、png、webp、gif 头像")

    profile = await _get_or_create_profile(session_id, db)
    avatar_dir = settings.MEDIA_DIR / "profiles" / profile.session_id
    avatar_dir.mkdir(parents=True, exist_ok=True)
    file_path = avatar_dir / f"{uuid.uuid4().hex}{suffix}"
    with open(file_path, "wb") as f:
        f.write(await avatar.read())

    old_avatar_path = profile.avatar_path
    profile.avatar_path = str(Path("media") / "profiles" / profile.session_id / file_path.name)
    profile.updated_at = utc_now()
    await db.commit()
    await db.refresh(profile)

    if old_avatar_path:
        old_file = settings.DATA_DIR / old_avatar_path
        old_file.unlink(missing_ok=True)

    return _to_item(profile)


@router.put("/ebti", response_model=UserProfileItem)
async def update_ebti(payload: ProfileEbtiUpdate, db: AsyncSession = Depends(get_db)):
    profile = await _get_or_create_profile(payload.session_id, db)
    profile.ebti_type = payload.ebti_type.strip().upper()
    profile.ebti_name = _clean_optional(payload.ebti_name)
    profile.ebti_avatar = _clean_optional(payload.ebti_avatar)
    profile.updated_at = utc_now()
    await db.commit()
    await db.refresh(profile)
    return _to_item(profile)
