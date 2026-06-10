"""QA 日志查询接口。"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.qa_log import QALog, QALogStep
from app.models.user import User
from app.services.auth_service import require_roles

_admin_teacher = require_roles("admin", "teacher")

logger = logging.getLogger("app.api.logs")
router = APIRouter(prefix="/api/logs", tags=["logs"])


def _step_to_dict(step: QALogStep) -> dict:
    return {
        "id": step.id,
        "step_name": step.step_name,
        "service_name": step.service_name,
        "input_json": step.input_json,
        "output_json": step.output_json,
        "duration_ms": step.duration_ms,
        "status": step.status,
        "error_message": step.error_message,
        "created_at": step.created_at.isoformat(),
    }


def _log_to_dict(log: QALog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "conversation_id": log.conversation_id,
        "question": log.question,
        "resolved_question": log.resolved_question,
        "intent": log.intent,
        "status": log.status,
        "total_duration_ms": log.total_duration_ms,
        "source_count": log.source_count,
        "final_answer": log.final_answer,
        "created_at": log.created_at.isoformat(),
    }


def _log_detail_to_dict(log: QALog) -> dict:
    d = _log_to_dict(log)
    d["steps"] = [_step_to_dict(s) for s in log.steps]
    return d


@router.get("")
async def list_logs(
    keyword: str | None = Query(None, description="问题关键词"),
    intent: str | None = Query(None, description="意图类型"),
    status: str | None = Query(None, description="状态 SUCCESS/FAILED"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_teacher),
) -> dict:
    stmt = select(QALog).order_by(QALog.created_at.desc())
    if keyword:
        stmt = stmt.where(QALog.question.ilike(f"%{keyword}%"))
    if intent:
        stmt = stmt.where(QALog.intent == intent)
    if status:
        stmt = stmt.where(QALog.status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_log_to_dict(r) for r in rows],
    }


@router.get("/{log_id}")
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_teacher),
) -> dict:
    stmt = select(QALog).where(QALog.id == log_id).options(selectinload(QALog.steps))
    log = (await db.execute(stmt)).scalar_one_or_none()
    if log is None:
        raise HTTPException(status_code=404, detail="日志不存在")
    return _log_detail_to_dict(log)
