"""问答接口的请求 / 响应 Pydantic 模型。"""
from pydantic import BaseModel, Field


class QAData(BaseModel):
    question_type: str = "其他"
    answer: str = ""
    beginner_explanation: str = ""
    code_example: str = ""
    need_more_info: bool = False
    need_more_info_fields: list[str] = Field(default_factory=list)


class QAResponse(BaseModel):
    success: bool
    data: QAData | None = None
    error: str = ""
    duration_ms: int = 0
    conversation_id: int | None = None
