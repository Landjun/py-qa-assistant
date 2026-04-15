from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMBase


class FollowUpCreate(BaseModel):
    student_id: int
    follow_time: datetime
    follow_method: Optional[str] = None
    content: str
    student_feedback: Optional[str] = None
    judgment: Optional[str] = None
    next_action: Optional[str] = None
    next_follow_time: Optional[datetime] = None


class FollowUpOut(ORMBase, FollowUpCreate):
    id: int
    created_at: datetime
