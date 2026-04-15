"""CRUD for follow-up records."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.follow_up import FollowUp
from app.schemas.follow_up import FollowUpCreate


def list_by_student(db: Session, student_id: int) -> list[FollowUp]:
    stmt = select(FollowUp).where(FollowUp.student_id == student_id).order_by(FollowUp.follow_time.desc())
    return list(db.scalars(stmt).all())


def create(db: Session, payload: FollowUpCreate) -> FollowUp:
    obj = FollowUp(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
