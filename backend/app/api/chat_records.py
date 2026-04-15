from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import chat_record as chat_crud
from app.crud import student as student_crud
from app.schemas.chat_record import ChatRecordCreate, ChatRecordOut

router = APIRouter(prefix="/api/chat-records", tags=["chat-records"])


@router.get("/{student_id}")
def list_student_chats(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    rows = chat_crud.list_by_student(db, student_id)
    return success_response([ChatRecordOut.model_validate(x).model_dump() for x in rows])


@router.post("")
def create_chat(payload: ChatRecordCreate, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    row = chat_crud.create(db, payload)
    return success_response(ChatRecordOut.model_validate(row).model_dump(), "chat created")


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    row = chat_crud.get(db, chat_id)
    if not row:
        raise HTTPException(status_code=404, detail="chat record not found")
    chat_crud.delete(db, row)
    return success_response(None, "chat deleted")
