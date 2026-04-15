"""CRUD for chat records."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_record import ChatRecord
from app.schemas.chat_record import ChatRecordCreate


def list_by_student(db: Session, student_id: int) -> list[ChatRecord]:
    stmt = select(ChatRecord).where(ChatRecord.student_id == student_id).order_by(ChatRecord.created_at.desc())
    return list(db.scalars(stmt).all())


def get(db: Session, chat_id: int) -> ChatRecord | None:
    return db.get(ChatRecord, chat_id)


def create(db: Session, payload: ChatRecordCreate) -> ChatRecord:
    obj = ChatRecord(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: ChatRecord) -> None:
    db.delete(obj)
    db.commit()
