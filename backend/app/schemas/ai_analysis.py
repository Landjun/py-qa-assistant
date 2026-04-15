from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMBase


class AIAnalyzeRequest(BaseModel):
    chat_record_id: Optional[int] = None
    chat_content: Optional[str] = None


class AIAnalysisOut(ORMBase):
    id: int
    student_id: int
    chat_record_id: Optional[int] = None
    stage: Optional[str] = None
    main_need: Optional[str] = None
    core_concerns: Optional[str] = None
    interest_direction: Optional[str] = None
    risk_points: Optional[str] = None
    recommended_course: Optional[str] = None
    recommended_action: Optional[str] = None
    tags: list[str] = []
    tags_json: Optional[str] = None
    summary: Optional[str] = None
    raw_json: Optional[str] = None
    created_at: datetime
