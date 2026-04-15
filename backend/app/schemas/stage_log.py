from datetime import datetime
from typing import Optional

from app.schemas.common import ORMBase


class StageLogOut(ORMBase):
    id: int
    student_id: int
    from_stage: Optional[str] = None
    to_stage: str
    remark: Optional[str] = None
    changed_at: datetime
