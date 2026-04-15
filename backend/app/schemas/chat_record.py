from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMBase


class ChatRecordCreate(BaseModel):
    student_id: int
    content: str
    source: Optional[str] = None


class ChatRecordOut(ORMBase):
    id: int
    student_id: int
    content: str
    source: Optional[str] = None
    created_at: datetime
