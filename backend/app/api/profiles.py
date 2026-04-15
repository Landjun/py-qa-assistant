from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import profile as profile_crud
from app.crud import student as student_crud
from app.schemas.profile import ProfileOut, ProfileUpsert

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("/{student_id}")
def get_profile(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    row = profile_crud.get_by_student_id(db, student_id)
    if not row:
        return success_response(None, "profile not found")
    return success_response(ProfileOut.model_validate(row).model_dump())


@router.put("/{student_id}")
def upsert_profile(student_id: int, payload: ProfileUpsert, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    row = profile_crud.upsert_profile(db, student_id, payload)
    return success_response(ProfileOut.model_validate(row).model_dump(), "profile saved")
