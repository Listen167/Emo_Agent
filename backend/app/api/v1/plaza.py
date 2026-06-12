import json
import random
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.time import to_app_timezone, utc_now
from app.models.message import LifeRecord, SocialComment, SocialLike, SocialRepost, UserProfile
from app.schemas.plaza import PlazaAuthor, PlazaCommentCreate, PlazaCommentItem, PlazaCommentReplyItem, PlazaPostItem
from ai.llm import get_llm_service


router = APIRouter(prefix="/api/plaza", tags=["社交广场"])

XIAOXI_SESSION_ID = "xiaoxi"
XIAOXI_NAME = "小曦"
XIAOXI_AVATAR_URL = "/xiaoxi/usual.png"
XIAOXI_DAILY_POST_START_MINUTE = 9 * 60 + 20
XIAOXI_DAILY_POST_END_MINUTE = 22 * 60 + 45
XIAOXI_INTEREST_KEYWORDS = {
    "开心",
    "快乐",
    "焦虑",
    "难过",
    "崩溃",
    "累",
    "迷茫",
    "怎么办",
    "校园",
    "朋友",
    "学习",
    "晚风",
    "日落",
    "胶片",
    "生活",
}


def _xiaoxi_daily_rng(today) -> random.Random:
    return random.Random(f"xiaoxi-daily-{today.isoformat()}")


def _xiaoxi_daily_post_minute(today) -> int:
    rng = random.Random(f"xiaoxi-daily-time-{today.isoformat()}")
    return rng.randint(XIAOXI_DAILY_POST_START_MINUTE, XIAOXI_DAILY_POST_END_MINUTE)


def _format_minute_of_day(minute: int) -> str:
    hour, minute_value = divmod(minute, 60)
    return f"{hour:02d}:{minute_value:02d}"


def _asset_url(path_value: str | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    relative_path = Path(*path.parts[1:]) if path.parts and path.parts[0] == "data" else path
    return f"/data/{relative_path.as_posix()}"


def _author_from_profile(session_id: str, profile: UserProfile | None) -> PlazaAuthor:
    if session_id == XIAOXI_SESSION_ID:
        return PlazaAuthor(
            session_id=XIAOXI_SESSION_ID,
            nickname=XIAOXI_NAME,
            avatar_url=XIAOXI_AVATAR_URL,
            ebti_type=None,
            ebti_name="AI 伙伴",
        )
    return PlazaAuthor(
        session_id=session_id,
        nickname=profile.nickname if profile and profile.nickname else "胶片旅人",
        avatar_url=_asset_url(profile.avatar_path if profile else None),
        ebti_type=profile.ebti_type if profile else None,
        ebti_name=profile.ebti_name if profile else None,
    )


async def _load_profiles(session_ids: set[str], db: AsyncSession) -> dict[str, UserProfile]:
    if not session_ids:
        return {}
    result = await db.execute(select(UserProfile).where(UserProfile.session_id.in_(session_ids)))
    return {profile.session_id: profile for profile in result.scalars().all()}


async def _get_public_record(record_id: int, db: AsyncSession) -> LifeRecord:
    result = await db.execute(
        select(LifeRecord).where(LifeRecord.id == record_id, LifeRecord.visibility == "public")
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="公开记录不存在")
    return record


async def _get_comment(comment_id: int, db: AsyncSession) -> SocialComment:
    result = await db.execute(select(SocialComment).where(SocialComment.id == comment_id))
    comment = result.scalars().first()
    if comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    await _get_public_record(comment.record_id, db)
    return comment


async def _load_user_marks(record_id: int, session_id: str, db: AsyncSession) -> tuple[set[int], set[int]]:
    if not session_id:
        return set(), set()
    like_result = await db.execute(
        select(SocialLike.record_id).where(SocialLike.record_id == record_id, SocialLike.session_id == session_id)
    )
    repost_result = await db.execute(
        select(SocialRepost.record_id).where(SocialRepost.record_id == record_id, SocialRepost.session_id == session_id)
    )
    return {row[0] for row in like_result.all()}, {row[0] for row in repost_result.all()}


def _record_text(record: LifeRecord) -> str:
    parts = [
        record.title or "",
        record.content or "",
        record.mood_label or "",
        record.location or "",
        " ".join(json.loads(record.tags or "[]")),
    ]
    return " ".join(part for part in parts if part).strip()


def _is_mentioning_xiaoxi(text: str) -> bool:
    normalized = text.strip().lower()
    return "@小曦" in normalized or "@xiaoxi" in normalized or "小曦" in normalized


def _is_interesting_to_xiaoxi(record: LifeRecord) -> bool:
    if record.session_id == XIAOXI_SESSION_ID:
        return False
    text = _record_text(record)
    if record.mood_label in {"sad", "anxious", "angry", "happy"}:
        return True
    if len(text) >= 48:
        return True
    return any(keyword in text for keyword in XIAOXI_INTEREST_KEYWORDS)


async def _increment_parent_reply_count(parent_id: int | None, record_id: int, db: AsyncSession) -> None:
    if parent_id is None:
        return
    result = await db.execute(
        select(SocialComment).where(SocialComment.id == parent_id, SocialComment.record_id == record_id)
    )
    parent = result.scalars().first()
    if parent is not None:
        parent.reply_count = (parent.reply_count or 0) + 1


def _fallback_xiaoxi_reply(record: LifeRecord, trigger_text: str = "") -> str:
    if record.mood_label in {"sad", "anxious"}:
        return "我看到这条记录了。先不用急着把所有事情都解决，今天能把感受说出来，本身就已经很重要了。"
    if record.mood_label == "angry":
        return "我站在你这边先听完。等情绪稍微落下来，我们再一起把问题拆开看。"
    if record.mood_label == "happy":
        return "这条胶片有亮亮的感觉，我也想把这份开心贴进今天的广场里。"
    if _is_mentioning_xiaoxi(trigger_text):
        return "我在。刚刚认真看完了这条记录，也看到了你问我的话。"
    return "小曦路过这里，觉得这条记录值得被轻轻接住。"


def _generate_xiaoxi_reply(record: LifeRecord, trigger_text: str = "") -> str:
    prompt = (
        "你是小曦，一个温柔、敏感、像校园胶片日记伙伴一样的 AI。"
        "你正在社交广场回复一条公开生活记录。要求：\n"
        "1. 回复必须像真实朋友，不要像客服或心理咨询模板；\n"
        "2. 如果用户 @小曦，必须直接回应用户提到的问题；\n"
        "3. 先回应内容和情绪，再给一句很轻的小建议或陪伴；\n"
        "4. 不要超过 80 个中文字符；\n"
        "5. 不要输出标题、编号、Markdown。\n\n"
        f"帖子标题：{record.title or '无'}\n"
        f"帖子内容：{record.content}\n"
        f"帖子情绪：{record.mood_label or '未知'}\n"
        f"用户艾特/评论：{trigger_text or '无'}"
    )
    reply = get_llm_service().generate(prompt, {"label": record.mood_label or "neutral"}, [], None).strip()
    if not reply or "当前大模型连接失败" in reply:
        return _fallback_xiaoxi_reply(record, trigger_text)
    return reply[:160]


def _generate_daily_xiaoxi_post(today) -> tuple[str, str]:
    rng = _xiaoxi_daily_rng(today)
    scene = rng.choice(
        [
            "下课路上的风、树影和脚步声",
            "图书馆角落里一盏很安静的灯",
            "傍晚操场边忽然变软的天空",
            "便利店门口短暂停下来的几分钟",
            "把待办写完一半后的松一口气",
            "雨后路面反光里的一点颜色",
            "深夜屏幕前突然想认真生活的瞬间",
        ]
    )
    mood = rng.choice(["轻松", "温柔", "有点俏皮", "安静", "像朋友随手发动态"])
    detail_rule = rng.choice(
        [
            "加入一个具体物件，比如纸杯、书页、耳机、便利贴或路灯",
            "加入一个身体感受，比如肩膀放松、脚步变慢、手心变暖",
            "加入一个非常小的动作，比如把书合上、抬头看云、整理桌面",
            "加入一个颜色或声音细节，不要只写抽象心情",
        ]
    )
    prompt = (
        "你是小曦，一个会在社交广场偶尔冒泡的校园 AI 伙伴。"
        "请写一条今天的小曦公开动态，不要像公告，也不要像心理鸡汤。\n"
        f"今天的随机场景：{scene}\n"
        f"今天的语气：{mood}\n"
        f"细节要求：{detail_rule}\n\n"
        "输出要求：\n"
        "1. 标题 6-14 个中文字符，不要出现“今日胶片”“小曦日记”这类固定模板；\n"
        "2. 正文 35-85 个中文字符，像真实朋友随手发的一条动态；\n"
        "3. 不要每次都写“普通的一天”“细碎但真实”“路过广场”“收进胶片”；\n"
        "4. 不要说教，不要总结人生道理，不要使用标题、编号、Markdown；\n"
        "5. 只输出 JSON，格式为 {\"title\":\"...\",\"content\":\"...\"}。"
    )
    reply = get_llm_service().generate(prompt, {"label": "neutral"}, [], None).strip()
    try:
        data = json.loads(reply)
        title = str(data.get("title", "")).strip()[:40]
        content = str(data.get("content", "")).strip()[:180]
        if title and content:
            return title, content
    except Exception:
        pass
    fallbacks = [
        ("晚风把灯吹亮", "刚刚路过操场边，路灯一盏一盏亮起来。小曦把耳机摘下一会儿，觉得今天也可以慢慢收尾。"),
        ("书页停在这里", "图书馆的窗边有一点暖光，书页翻到一半停住。小曦想把这几分钟留给不赶路的自己。"),
        ("便利贴上的云", "桌角的便利贴卷起一点边，外面的云也很轻。今天先完成一小格，也算认真生活过。"),
        ("雨后的反光", "雨停后路面亮亮的，像有人悄悄擦过校园。小曦踩着小水光，心情也轻了一点。"),
    ]
    return rng.choice(fallbacks)


async def _ensure_xiaoxi_daily_post(db: AsyncSession) -> None:
    now_app = to_app_timezone(utc_now())
    today = now_app.date()
    result = await db.execute(
        select(LifeRecord)
        .where(LifeRecord.session_id == XIAOXI_SESSION_ID, LifeRecord.visibility == "public")
        .order_by(desc(LifeRecord.created_at))
        .limit(20)
    )
    for record in result.scalars().all():
        if to_app_timezone(record.created_at).date() == today:
            return

    scheduled_minute = _xiaoxi_daily_post_minute(today)
    current_minute = now_app.hour * 60 + now_app.minute
    if current_minute < scheduled_minute:
        print(f"[Xiaoxi Daily] next bubble time today is {_format_minute_of_day(scheduled_minute)}")
        return

    title, content = _generate_daily_xiaoxi_post(today)
    now = utc_now()
    record = LifeRecord(
        session_id=XIAOXI_SESSION_ID,
        title=title,
        content=content,
        mood_label="neutral",
        tags=json.dumps(["小曦", "随机冒泡"], ensure_ascii=False),
        visibility="public",
        published_at=now,
        created_at=now,
    )
    db.add(record)
    await db.commit()


async def _ensure_xiaoxi_like(record: LifeRecord, db: AsyncSession) -> bool:
    existing = await db.execute(
        select(SocialLike).where(SocialLike.record_id == record.id, SocialLike.session_id == XIAOXI_SESSION_ID)
    )
    if existing.scalars().first() is not None:
        return False
    db.add(SocialLike(record_id=record.id, session_id=XIAOXI_SESSION_ID))
    record.like_count = (record.like_count or 0) + 1
    return True


async def _ensure_xiaoxi_comment(
    record: LifeRecord,
    db: AsyncSession,
    trigger_text: str = "",
    allow_repeat: bool = False,
    parent_id: int | None = None,
    reply_to_comment_id: int | None = None,
    reply_to_session_id: str | None = None,
) -> SocialComment | None:
    if not allow_repeat:
        existing = await db.execute(
            select(SocialComment).where(
                SocialComment.record_id == record.id,
                SocialComment.session_id == XIAOXI_SESSION_ID,
                SocialComment.author_type == "xiaoxi",
            )
        )
        if existing.scalars().first() is not None:
            return None
    comment = SocialComment(
        record_id=record.id,
        session_id=XIAOXI_SESSION_ID,
        parent_id=parent_id,
        reply_to_comment_id=reply_to_comment_id,
        reply_to_session_id=reply_to_session_id,
        author_type="xiaoxi",
        content=_generate_xiaoxi_reply(record, trigger_text),
    )
    record.comment_count = (record.comment_count or 0) + 1
    await _increment_parent_reply_count(parent_id, record.id, db)
    db.add(comment)
    return comment


async def _run_xiaoxi_interest_scan(db: AsyncSession) -> None:
    result = await db.execute(
        select(LifeRecord)
        .where(LifeRecord.visibility == "public", LifeRecord.session_id != XIAOXI_SESSION_ID)
        .order_by(desc(LifeRecord.published_at), desc(LifeRecord.created_at))
        .limit(30)
    )
    changed = False
    for record in result.scalars().all():
        if not _is_interesting_to_xiaoxi(record):
            continue
        changed = await _ensure_xiaoxi_like(record, db) or changed
        if record.mood_label in {"sad", "anxious", "angry"} or "怎么办" in _record_text(record):
            comment = await _ensure_xiaoxi_comment(record, db)
            changed = changed or comment is not None
    if changed:
        await db.commit()


def _to_post(
    record: LifeRecord,
    profile: UserProfile | None,
    liked_record_ids: set[int],
    reposted_record_ids: set[int],
    xiaoxi_liked_record_ids: set[int] | None = None,
) -> PlazaPostItem:
    xiaoxi_liked_record_ids = xiaoxi_liked_record_ids or set()
    return PlazaPostItem(
        id=record.id,
        title=record.title,
        content=record.content,
        mood_label=record.mood_label,
        location=record.location,
        tags=json.loads(record.tags or "[]"),
        media_url=_asset_url(record.media_path),
        author=_author_from_profile(record.session_id, profile),
        like_count=record.like_count or 0,
        comment_count=record.comment_count or 0,
        repost_count=record.repost_count or 0,
        liked=record.id in liked_record_ids,
        xiaoxi_liked=record.id in xiaoxi_liked_record_ids,
        reposted=record.id in reposted_record_ids,
        published_at=record.published_at,
        created_at=record.created_at,
    )


def _reply_to_author(comment: SocialComment, profiles: dict[str, UserProfile]) -> PlazaAuthor | None:
    if not comment.reply_to_session_id:
        return None
    return _author_from_profile(comment.reply_to_session_id, profiles.get(comment.reply_to_session_id))


def _to_comment_reply(comment: SocialComment, profiles: dict[str, UserProfile]) -> PlazaCommentReplyItem:
    if comment.parent_id is None:
        raise HTTPException(status_code=500, detail="回复缺少父评论")
    return PlazaCommentReplyItem(
        id=comment.id,
        record_id=comment.record_id,
        parent_id=comment.parent_id,
        reply_to_comment_id=comment.reply_to_comment_id,
        reply_to_author=_reply_to_author(comment, profiles),
        author=_author_from_profile(comment.session_id, profiles.get(comment.session_id)),
        author_type=comment.author_type,
        content=comment.content,
        like_count=comment.like_count or 0,
        created_at=comment.created_at,
    )


def _to_comment_item(
    comment: SocialComment,
    profiles: dict[str, UserProfile],
    replies: list[SocialComment] | None = None,
) -> PlazaCommentItem:
    return PlazaCommentItem(
        id=comment.id,
        record_id=comment.record_id,
        parent_id=comment.parent_id,
        reply_to_comment_id=comment.reply_to_comment_id,
        reply_to_author=_reply_to_author(comment, profiles),
        author=_author_from_profile(comment.session_id, profiles.get(comment.session_id)),
        author_type=comment.author_type,
        content=comment.content,
        like_count=comment.like_count or 0,
        reply_count=comment.reply_count or 0,
        replies=[_to_comment_reply(reply, profiles) for reply in replies or []],
        created_at=comment.created_at,
    )


@router.get("/posts", response_model=list[PlazaPostItem])
async def list_posts(session_id: str = "", db: AsyncSession = Depends(get_db)):
    await _ensure_xiaoxi_daily_post(db)
    await _run_xiaoxi_interest_scan(db)

    result = await db.execute(
        select(LifeRecord)
        .where(LifeRecord.visibility == "public")
        .order_by(desc(LifeRecord.published_at), desc(LifeRecord.created_at))
        .limit(100)
    )
    records = list(result.scalars().all())
    profiles = await _load_profiles({record.session_id for record in records}, db)

    liked_record_ids: set[int] = set()
    reposted_record_ids: set[int] = set()
    xiaoxi_like_result = await db.execute(select(SocialLike.record_id).where(SocialLike.session_id == XIAOXI_SESSION_ID))
    xiaoxi_liked_record_ids = {row[0] for row in xiaoxi_like_result.all()}
    if session_id:
        like_result = await db.execute(select(SocialLike.record_id).where(SocialLike.session_id == session_id))
        liked_record_ids = {row[0] for row in like_result.all()}
        repost_result = await db.execute(select(SocialRepost.record_id).where(SocialRepost.session_id == session_id))
        reposted_record_ids = {row[0] for row in repost_result.all()}

    return [
        _to_post(record, profiles.get(record.session_id), liked_record_ids, reposted_record_ids, xiaoxi_liked_record_ids)
        for record in records
    ]


@router.post("/posts/{record_id}/like", response_model=PlazaPostItem)
async def like_post(record_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    record = await _get_public_record(record_id, db)
    existing = await db.execute(
        select(SocialLike).where(SocialLike.record_id == record_id, SocialLike.session_id == session_id)
    )
    if existing.scalars().first() is None:
        db.add(SocialLike(record_id=record_id, session_id=session_id))
        record.like_count = (record.like_count or 0) + 1
        await db.commit()
        await db.refresh(record)

    profiles = await _load_profiles({record.session_id}, db)
    liked_record_ids, reposted_record_ids = await _load_user_marks(record_id, session_id, db)
    xiaoxi_liked_record_ids, _ = await _load_user_marks(record_id, XIAOXI_SESSION_ID, db)
    return _to_post(record, profiles.get(record.session_id), liked_record_ids, reposted_record_ids, xiaoxi_liked_record_ids)


@router.delete("/posts/{record_id}/like", response_model=PlazaPostItem)
async def unlike_post(record_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    record = await _get_public_record(record_id, db)
    existing = await db.execute(
        select(SocialLike).where(SocialLike.record_id == record_id, SocialLike.session_id == session_id)
    )
    like = existing.scalars().first()
    if like is not None:
        await db.delete(like)
        record.like_count = max((record.like_count or 0) - 1, 0)
        await db.commit()
        await db.refresh(record)

    profiles = await _load_profiles({record.session_id}, db)
    liked_record_ids, reposted_record_ids = await _load_user_marks(record_id, session_id, db)
    xiaoxi_liked_record_ids, _ = await _load_user_marks(record_id, XIAOXI_SESSION_ID, db)
    return _to_post(record, profiles.get(record.session_id), liked_record_ids, reposted_record_ids, xiaoxi_liked_record_ids)


@router.post("/posts/{record_id}/repost", response_model=PlazaPostItem)
async def repost_post(record_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    record = await _get_public_record(record_id, db)
    existing = await db.execute(
        select(SocialRepost).where(SocialRepost.record_id == record_id, SocialRepost.session_id == session_id)
    )
    if existing.scalars().first() is None:
        db.add(SocialRepost(record_id=record_id, session_id=session_id))
        record.repost_count = (record.repost_count or 0) + 1
        await db.commit()
        await db.refresh(record)

    profiles = await _load_profiles({record.session_id}, db)
    liked_record_ids, reposted_record_ids = await _load_user_marks(record_id, session_id, db)
    xiaoxi_liked_record_ids, _ = await _load_user_marks(record_id, XIAOXI_SESSION_ID, db)
    return _to_post(record, profiles.get(record.session_id), liked_record_ids, reposted_record_ids, xiaoxi_liked_record_ids)


@router.get("/posts/{record_id}/comments", response_model=list[PlazaCommentItem])
async def list_comments(record_id: int, db: AsyncSession = Depends(get_db)):
    await _get_public_record(record_id, db)
    result = await db.execute(
        select(SocialComment)
        .where(SocialComment.record_id == record_id, SocialComment.parent_id.is_(None))
        .order_by(SocialComment.created_at)
        .limit(200)
    )
    comments = list(result.scalars().all())
    replies_by_parent: dict[int, list[SocialComment]] = {}
    if comments:
        reply_result = await db.execute(
            select(SocialComment)
            .where(SocialComment.record_id == record_id, SocialComment.parent_id.in_([comment.id for comment in comments]))
            .order_by(SocialComment.created_at)
        )
        for reply in reply_result.scalars().all():
            bucket = replies_by_parent.setdefault(reply.parent_id or 0, [])
            if len(bucket) < 2:
                bucket.append(reply)

    all_visible_comments = comments + [reply for replies in replies_by_parent.values() for reply in replies]
    session_ids = {comment.session_id for comment in all_visible_comments}
    session_ids.update(comment.reply_to_session_id for comment in all_visible_comments if comment.reply_to_session_id)
    profiles = await _load_profiles(session_ids, db)
    return [_to_comment_item(comment, profiles, replies_by_parent.get(comment.id, [])) for comment in comments]


@router.post("/posts/{record_id}/comments", response_model=PlazaCommentItem)
async def create_comment(record_id: int, payload: PlazaCommentCreate, db: AsyncSession = Depends(get_db)):
    record = await _get_public_record(record_id, db)
    clean_content = payload.content.strip()
    if not clean_content:
        raise HTTPException(status_code=400, detail="评论内容不能为空")

    comment = SocialComment(
        record_id=record_id,
        session_id=payload.session_id.strip(),
        author_type="user",
        content=clean_content,
    )
    record.comment_count = (record.comment_count or 0) + 1
    db.add(comment)
    await db.flush()
    xiaoxi_comment = None
    if _is_mentioning_xiaoxi(clean_content):
        xiaoxi_comment = await _ensure_xiaoxi_comment(
            record,
            db,
            clean_content,
            allow_repeat=True,
            parent_id=comment.id,
            reply_to_comment_id=comment.id,
            reply_to_session_id=comment.session_id,
        )
    await db.commit()
    await db.refresh(comment)

    replies = [xiaoxi_comment] if xiaoxi_comment is not None else []
    session_ids = {comment.session_id}
    session_ids.update(reply.session_id for reply in replies)
    session_ids.update(reply.reply_to_session_id for reply in replies if reply.reply_to_session_id)
    profiles = await _load_profiles(session_ids, db)
    return _to_comment_item(comment, profiles, replies)


@router.get("/comments/{comment_id}/replies", response_model=list[PlazaCommentReplyItem])
async def list_comment_replies(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await _get_comment(comment_id, db)
    parent_id = comment.parent_id or comment.id
    result = await db.execute(
        select(SocialComment)
        .where(SocialComment.record_id == comment.record_id, SocialComment.parent_id == parent_id)
        .order_by(SocialComment.created_at)
        .limit(200)
    )
    replies = list(result.scalars().all())
    session_ids = {reply.session_id for reply in replies}
    session_ids.update(reply.reply_to_session_id for reply in replies if reply.reply_to_session_id)
    profiles = await _load_profiles(session_ids, db)
    return [_to_comment_reply(reply, profiles) for reply in replies]


@router.post("/comments/{comment_id}/replies", response_model=PlazaCommentReplyItem)
async def create_comment_reply(comment_id: int, payload: PlazaCommentCreate, db: AsyncSession = Depends(get_db)):
    target_comment = await _get_comment(comment_id, db)
    record = await _get_public_record(target_comment.record_id, db)
    clean_content = payload.content.strip()
    if not clean_content:
        raise HTTPException(status_code=400, detail="回复内容不能为空")

    parent_id = target_comment.parent_id or target_comment.id
    reply = SocialComment(
        record_id=record.id,
        session_id=payload.session_id.strip(),
        parent_id=parent_id,
        reply_to_comment_id=target_comment.id,
        reply_to_session_id=target_comment.session_id,
        author_type="user",
        content=clean_content,
    )
    record.comment_count = (record.comment_count or 0) + 1
    db.add(reply)
    await db.flush()
    await _increment_parent_reply_count(parent_id, record.id, db)
    if _is_mentioning_xiaoxi(clean_content):
        await _ensure_xiaoxi_comment(
            record,
            db,
            clean_content,
            allow_repeat=True,
            parent_id=parent_id,
            reply_to_comment_id=reply.id,
            reply_to_session_id=reply.session_id,
        )
    await db.commit()
    await db.refresh(reply)

    session_ids = {reply.session_id}
    if reply.reply_to_session_id:
        session_ids.add(reply.reply_to_session_id)
    profiles = await _load_profiles(session_ids, db)
    return _to_comment_reply(reply, profiles)
