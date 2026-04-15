from app.schemas.common import ORMBase


class DashboardStudentItem(ORMBase):
    id: int
    name: str
    current_stage: str
    intent_level: str | None = None
    owner: str | None = None
    last_interaction_at: str | None = None
    next_follow_time: str | None = None


class DashboardSummary(ORMBase):
    total_students: int
    high_intent_count: int
    pending_follow_count: int
    closed_deals_count: int
    weekly_new_followups: int
    recent_followed_students: list[DashboardStudentItem]
    pending_follow_students: list[DashboardStudentItem]
