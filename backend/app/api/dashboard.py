from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import dashboard as dashboard_crud

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _serialize_student(row) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "current_stage": str(row.current_stage),
        "intent_level": row.intent_level,
        "owner": row.owner,
        "last_interaction_at": row.last_interaction_at.isoformat() if row.last_interaction_at else None,
        "next_follow_time": row.next_follow_time.isoformat() if row.next_follow_time else None,
    }


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    data = dashboard_crud.get_summary_numbers(db)
    data["recent_followed_students"] = [_serialize_student(x) for x in data["recent_followed_students"]]
    data["pending_follow_students"] = [_serialize_student(x) for x in data["pending_follow_students"]]
    return success_response(data)
