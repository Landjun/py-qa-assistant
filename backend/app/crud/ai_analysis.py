"""CRUD for AI analysis records."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis


def create(db: Session, payload: dict) -> AIAnalysis:
    obj = AIAnalysis(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_by_student(db: Session, student_id: int) -> list[AIAnalysis]:
    stmt = select(AIAnalysis).where(AIAnalysis.student_id == student_id).order_by(AIAnalysis.created_at.desc())
    return list(db.scalars(stmt).all())
