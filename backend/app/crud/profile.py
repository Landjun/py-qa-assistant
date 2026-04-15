"""CRUD for student profiles."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.schemas.profile import ProfileUpsert


def get_by_student_id(db: Session, student_id: int) -> Profile | None:
    stmt = select(Profile).where(Profile.student_id == student_id)
    return db.scalar(stmt)


def upsert_profile(db: Session, student_id: int, payload: ProfileUpsert) -> Profile:
    profile = get_by_student_id(db, student_id)
    if profile is None:
        profile = Profile(student_id=student_id, **payload.model_dump())
        db.add(profile)
    else:
        for key, val in payload.model_dump().items():
            setattr(profile, key, val)
    db.commit()
    db.refresh(profile)
    return profile
