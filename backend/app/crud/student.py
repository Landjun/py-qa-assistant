"""CRUD for students and stage changes."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stage_log import StageLog
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


def get_students(db: Session) -> list[Student]:
    return list(db.scalars(select(Student).order_by(Student.created_at.desc())).all())


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def create_student(db: Session, payload: StudentCreate) -> Student:
    obj = Student(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_student(db: Session, student: Student, payload: StudentUpdate) -> Student:
    for key, val in payload.model_dump().items():
        setattr(student, key, val)
    db.commit()
    db.refresh(student)
    return student


def change_stage(db: Session, student: Student, to_stage: str, remark: str | None) -> StageLog:
    from_stage = student.current_stage
    student.current_stage = to_stage
    log = StageLog(student_id=student.id, from_stage=from_stage, to_stage=to_stage, remark=remark)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
