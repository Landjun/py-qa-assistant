from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import student as student_crud
from app.schemas.stage_log import StageLogOut
from app.schemas.student import StageUpdateRequest, StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("")
def list_students(db: Session = Depends(get_db)):
    rows = student_crud.get_students(db)
    return success_response([StudentOut.model_validate(x).model_dump() for x in rows])


@router.post("")
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    row = student_crud.create_student(db, payload)
    return success_response(StudentOut.model_validate(row).model_dump(), "student created")


@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    row = student_crud.get_student(db, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="student not found")
    return success_response(StudentOut.model_validate(row).model_dump())


@router.put("/{student_id}")
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    row = student_crud.get_student(db, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="student not found")
    updated = student_crud.update_student(db, row, payload)
    return success_response(StudentOut.model_validate(updated).model_dump(), "student updated")


@router.post("/{student_id}/stage")
def change_stage(student_id: int, payload: StageUpdateRequest, db: Session = Depends(get_db)):
    row = student_crud.get_student(db, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="student not found")
    log = student_crud.change_stage(db, row, payload.to_stage.value, payload.remark)
    return success_response(StageLogOut.model_validate(log).model_dump(), "stage changed")
