import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import ai_analysis as ai_crud
from app.crud import chat_record as chat_crud
from app.crud import profile as profile_crud
from app.crud import student as student_crud
from app.models.ai_analysis import AIAnalysis
from app.schemas.ai_analysis import AIAnalysisOut, AIAnalyzeRequest
from app.schemas.profile import ProfileUpsert
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _serialize_analysis(row) -> dict:
    data = AIAnalysisOut.model_validate(row).model_dump()
    try:
        data["tags"] = json.loads(row.tags_json) if row.tags_json else []
    except json.JSONDecodeError:
        data["tags"] = []
    return data


@router.post("/analyze/{student_id}")
def analyze_student(student_id: int, payload: AIAnalyzeRequest, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    chat_record = None
    chat_content = payload.chat_content or ""

    if payload.chat_record_id:
        chat_record = chat_crud.get(db, payload.chat_record_id)
        if not chat_record or chat_record.student_id != student_id:
            raise HTTPException(status_code=404, detail="chat record not found")
        chat_content = chat_content or chat_record.content

    if not chat_content:
        chats = chat_crud.list_by_student(db, student_id)
        if chats:
            chat_record = chats[0]
            chat_content = chat_record.content

    if not chat_content:
        raise HTTPException(status_code=400, detail="chat content is required")

    result = ai_service.analyze_chat(
        student_name=student.name,
        chat_content=chat_content,
        chat_record_id=chat_record.id if chat_record else payload.chat_record_id,
    )

    row = ai_crud.create(db, {"student_id": student_id, **result})
    return success_response(_serialize_analysis(row), "analysis created")


@router.get("/analyses/{student_id}")
def list_analyses(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    rows = ai_crud.list_by_student(db, student_id)
    return success_response([_serialize_analysis(x) for x in rows])


@router.post("/analyses/{analysis_id}/sync-profile")
def sync_analysis_to_profile(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(AIAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="analysis not found")

    student = student_crud.get_student(db, analysis.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    profile_payload = ProfileUpsert(
        summary=analysis.summary,
        main_goal=analysis.main_need,
        main_concerns=analysis.core_concerns,
        interest_direction=analysis.interest_direction,
        risk_tags=analysis.risk_points,
        recommended_course=analysis.recommended_course,
        recommended_action=analysis.recommended_action,
    )
    profile = profile_crud.upsert_profile(db, student.id, profile_payload)
    return success_response({"student_id": student.id, "profile_id": profile.id}, "synced to profile")
