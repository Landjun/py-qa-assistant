from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import follow_up as follow_crud
from app.crud import student as student_crud
from app.schemas.follow_up import FollowUpCreate, FollowUpOut

router = APIRouter(prefix="/api/follow-ups", tags=["follow-ups"])


@router.get("/{student_id}")
def list_followups(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    rows = follow_crud.list_by_student(db, student_id)
    return success_response([FollowUpOut.model_validate(x).model_dump() for x in rows])


@router.post("")
def create_followup(payload: FollowUpCreate, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    row = follow_crud.create(db, payload)
    # sync student next follow time and interaction snapshot
    student.last_interaction_at = payload.follow_time
    student.next_follow_time = payload.next_follow_time
    db.commit()
    return success_response(FollowUpOut.model_validate(row).model_dump(), "follow-up created")
