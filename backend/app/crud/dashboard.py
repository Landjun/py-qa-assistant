"""Aggregations for dashboard summary."""
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.follow_up import FollowUp
from app.models.student import Student


def get_summary_numbers(db: Session) -> dict:
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    total_students = db.scalar(select(func.count(Student.id))) or 0
    high_intent_count = db.scalar(select(func.count(Student.id)).where(Student.intent_level == "高")) or 0
    pending_follow_count = db.scalar(
        select(func.count(Student.id)).where(Student.next_follow_time.is_not(None), Student.next_follow_time <= now)
    ) or 0
    closed_deals_count = db.scalar(select(func.count(Student.id)).where(Student.current_stage == "已成交")) or 0
    weekly_new_followups = db.scalar(select(func.count(FollowUp.id)).where(FollowUp.created_at >= week_start)) or 0

    recent_students_stmt = (
        select(Student)
        .where(Student.last_interaction_at.is_not(None))
        .order_by(Student.last_interaction_at.desc())
        .limit(10)
    )
    pending_students_stmt = (
        select(Student)
        .where(or_(Student.next_follow_time.is_(None), Student.next_follow_time <= now))
        .order_by(Student.next_follow_time.asc())
        .limit(10)
    )

    return {
        "total_students": total_students,
        "high_intent_count": high_intent_count,
        "pending_follow_count": pending_follow_count,
        "closed_deals_count": closed_deals_count,
        "weekly_new_followups": weekly_new_followups,
        "recent_followed_students": list(db.scalars(recent_students_stmt).all()),
        "pending_follow_students": list(db.scalars(pending_students_stmt).all()),
    }
