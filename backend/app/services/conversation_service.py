"""会话 & 消息 CRUD 服务层。"""
import json
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message

logger = logging.getLogger("app.services.conversation")

DEFAULT_USER_ID = 1


async def create_conversation(db: AsyncSession, title: str = "新会话") -> Conversation:
    conv = Conversation(user_id=DEFAULT_USER_ID, title=title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_or_create_conversation(
    db: AsyncSession, conversation_id: int | None, first_message: str
) -> Conversation:
    """获取已有会话，或自动创建新会话（标题取问题前 20 字）。"""
    if conversation_id is not None:
        conv = await db.get(Conversation, conversation_id)
        if conv:
            return conv
        logger.warning("conversation_id=%d 不存在，自动创建新会话", conversation_id)

    title = first_message[:20].strip() or "新会话"
    return await create_conversation(db, title)


async def list_conversations(db: AsyncSession) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == DEFAULT_USER_ID)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation_messages(
    db: AsyncSession, conversation_id: int
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def delete_conversation(db: AsyncSession, conversation_id: int) -> bool:
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        return False
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
    # 同时更新会话的 updated_at
    conv = await db.get(Conversation, conversation_id)
    if conv:
        from datetime import datetime, timezone
        conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)
    return msg
