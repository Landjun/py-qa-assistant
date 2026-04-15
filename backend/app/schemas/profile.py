from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMBase


class ProfileBase(BaseModel):
    user_type: Optional[str] = None
    main_goal: Optional[str] = None
    main_concerns: Optional[str] = None
    interest_direction: Optional[str] = None
    risk_tags: Optional[str] = None
    recommended_course: Optional[str] = None
    recommended_action: Optional[str] = None
    summary: Optional[str] = None


class ProfileUpsert(ProfileBase):
    pass


class ProfileOut(ORMBase, ProfileBase):
    id: int
    student_id: int
    updated_at: datetime
