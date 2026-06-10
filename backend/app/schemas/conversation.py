"""会话 & 消息 Pydantic 模型。"""
from datetime import datetime

from pydantic import BaseModel


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    extra_json: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []
