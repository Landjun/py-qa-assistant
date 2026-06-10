"""会话管理接口。"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.conversation import ConversationOut, MessageOut
from app.services import conversation_service

logger = logging.getLogger("app.api.conversations")
router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(db: AsyncSession = Depends(get_db)) -> ConversationOut:
    """新建空会话。"""
    conv = await conversation_service.create_conversation(db)
    return ConversationOut.model_validate(conv)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(db: AsyncSession = Depends(get_db)) -> list[ConversationOut]:
    """列出当前用户的所有会话（按最新更新排序）。"""
    convs = await conversation_service.list_conversations(db)
    return [ConversationOut.model_validate(c) for c in convs]


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: int, db: AsyncSession = Depends(get_db)
) -> list[MessageOut]:
    """获取指定会话的消息列表。"""
    messages = await conversation_service.get_conversation_messages(db, conversation_id)
    return [MessageOut.model_validate(m) for m in messages]


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    """删除会话及其所有消息。"""
    ok = await conversation_service.delete_conversation(db, conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
