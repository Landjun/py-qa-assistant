"""会话 & 消息 CRUD 服务层。"""
import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message

logger = logging.getLogger("app.services.conversation")


async def create_conversation(
    db: AsyncSession, title: str = "新会话", user_id: int = 0
) -> Conversation:
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_or_create_conversation(
    db: AsyncSession,
    conversation_id: int | None,
    first_message: str,
    user_id: int = 0,
) -> Conversation:
    """获取已有会话（归属一致才复用），否则自动创建新会话。"""
    if conversation_id is not None:
        conv = await db.get(Conversation, conversation_id)
        if conv and conv.user_id == user_id:
            return conv
        if conv:
            logger.warning(
                "conversation_id=%d 归属不匹配，自动创建新会话（user_id=%d）",
                conversation_id, user_id,
            )
        else:
            logger.warning("conversation_id=%d 不存在，自动创建新会话", conversation_id)

    title = first_message[:20].strip() or "新会话"
    return await create_conversation(db, title, user_id)


async def list_conversations(db: AsyncSession, user_id: int) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation(db: AsyncSession, conversation_id: int) -> Conversation | None:
    return await db.get(Conversation, conversation_id)


async def get_conversation_messages(
    db: AsyncSession, conversation_id: int
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def delete_conversation(
    db: AsyncSession, conversation_id: int, user_id: int
) -> bool:
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        return False
    if conv.user_id != user_id:
        raise PermissionError("无权限删除他人会话")
    await db.delete(conv)
    await db.commit()
    return True


async def add_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    extra: dict | None = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        extra_json=json.dumps(extra, ensure_ascii=False) if extra else None,
    )
    db.add(msg)
    conv = await db.get(Conversation, conversation_id)
    if conv:
        from datetime import datetime, timezone
        conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)
    return msg
