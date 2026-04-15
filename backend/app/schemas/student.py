from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import StageEnum
from app.schemas.common import ORMBase


class StudentBase(BaseModel):
    name: str
    wechat: Optional[str] = None
    phone: Optional[str] = None
    course_name: Optional[str] = None
    class_name: Optional[str] = None
    graduation_date: Optional[date] = None
    current_direction: Optional[str] = None
    current_stage: StageEnum = StageEnum.刚结课
    intent_level: Optional[str] = None
    owner: Optional[str] = None
    last_interaction_at: Optional[datetime] = None
    next_follow_time: Optional[datetime] = None
    remark: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class StudentOut(ORMBase, StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime


class StageUpdateRequest(BaseModel):
    to_stage: StageEnum
    remark: Optional[str] = None
