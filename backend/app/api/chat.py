"""问答接口（含意图识别 + 路由 + 会话持久化）。"""
import dataclasses
import logging
import time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.chat import QAResponse
from app.models.user import User
from app.services import conversation_service, deepseek_service, intent_service, qa_log_service, rag_service
from app.services.auth_service import get_current_user, require_roles
from app.services.intent_service import IntentResult
from app.services.qa_log_service import QALogContext

logger = logging.getLogger("app.api.chat")
router = APIRouter(prefix="/api/chat", tags=["chat"])


class AskRequest(BaseModel):
    message: str
    conversation_id: int | None = None


# ─── /ask 响应模型 ────────────────────────────────────────────────────────────

class SourceInfoOut(BaseModel):
    document_id: int
    chunk_id: int
    source: str
    score: float


class BugDetailOut(BaseModel):
    error_type: str
    plain_explanation: str
    likely_causes: list[str]
    fix_steps: list[str]
    before_code: str
    after_code: str
    need_more_info: bool
    need_more_info_fields: list[str]


class RAGAnswerOut(BaseModel):
    useful: bool
    content: str
    beginner_explanation: str
    code_example: str
    sources: list[SourceInfoOut]
    bug_detail: BugDetailOut | None = None


class RAGResponse(BaseModel):
    success: bool
    answer: RAGAnswerOut | None = None
    error: str = ""
    duration_ms: int = 0
    conversation_id: int | None = None
    intent: str = ""
    confidence: float = 0.0
    resolved_question: str = ""


# ─── /intent 响应模型 ─────────────────────────────────────────────────────────

class IntentResponse(BaseModel):
    confidence: float
    intent: str
    resolved_question: str
    reason: str


# ─── 内部工具 ─────────────────────────────────────────────────────────────────

async def _safe_recognize_intent(history_text: str, message: str, log_ctx=None) -> IntentResult:
    """意图识别，失败时降级为 PYTHON_QA，不向上层抛出异常。"""
    try:
        return await intent_service.recognize_intent(history_text, message, log_ctx=log_ctx)
    except Exception as e:
        logger.warning("意图识别失败，降级 PYTHON_QA: %s", e)
        return IntentResult(confidence=0.5, intent="PYTHON_QA", resolved_question=message, reason="识别失败，已降级")


# ─── 接口 ─────────────────────────────────────────────────────────────────────

@router.post("/intent", response_model=IntentResponse)
async def get_intent(
    req: AskRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_roles("admin", "teacher")),
) -> IntentResponse:
    """独立意图识别接口（调试 / 测试用）。"""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message 不能为空")

    history_text = "（无历史记录）"
    if req.conversation_id is not None:
        msgs = await conversation_service.get_conversation_messages(db, req.conversation_id)
        history_text = intent_service.format_history(msgs)

    try:
        result = await intent_service.recognize_intent(history_text, message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return IntentResponse(
        confidence=result.confidence,
        intent=result.intent,
        resolved_question=result.resolved_question,
        reason=result.reason,
    )


@router.post("/ask", response_model=RAGResponse)
async def ask_rag(
    req: AskRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RAGResponse:
    """意图识别 → 路由 → RAG 问答 / 闲聊 / 反馈处理，自动保存会话。"""
    message = req.message.strip()
    if not message:
        return RAGResponse(success=False, error="message 不能为空")

    t0 = time.monotonic()
    user_id = current_user.id

    # 1. 获取/创建会话（归属当前登录用户）
    conv = await conversation_service.get_or_create_conversation(
        db, req.conversation_id, message, user_id=user_id
    )

    # 初始化日志上下文
    log_ctx = QALogContext(conversation_id=conv.id, question=message, user_id=user_id)

    # 2. 获取历史消息，用于意图识别的指代消解
    history_msgs = await conversation_service.get_conversation_messages(db, conv.id)
    history_text = intent_service.format_history(history_msgs)

    # 3. 意图识别（失败自动降级）
    intent_result = await _safe_recognize_intent(history_text, message, log_ctx=log_ctx)

    # 4. 保存用户消息
    await conversation_service.add_message(db, conv.id, "user", message)

    resolved = intent_result.resolved_question or message
    log_ctx.intent = intent_result.intent
    log_ctx.resolved_question = resolved

    # 5. 根据意图路由处理
    try:
        answer, _ = await rag_service.route_by_intent(
            db, conv.id, resolved, intent_result.intent, history_text, log_ctx=log_ctx
        )
    except (ValueError, RuntimeError) as e:
        logger.warning("路由处理失败: %s", e)
        log_ctx.finalize("")
        background_tasks.add_task(qa_log_service.save_log, log_ctx)
        return RAGResponse(
            success=False, error=str(e),
            conversation_id=conv.id,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            resolved_question=resolved,
        )
    except Exception:
        logger.exception("路由处理未知错误")
        log_ctx.finalize("")
        background_tasks.add_task(qa_log_service.save_log, log_ctx)
        return RAGResponse(
            success=False, error="服务器内部错误",
            conversation_id=conv.id,
            intent=intent_result.intent,
        )

    duration_ms = int((time.monotonic() - t0) * 1000)
    log_ctx.finalize(answer.content, len(answer.sources))
    background_tasks.add_task(qa_log_service.save_log, log_ctx)

    logger.info("ask 完成: conv=%d intent=%s duration=%dms", conv.id, intent_result.intent, duration_ms)

    return RAGResponse(
        success=True,
        answer=RAGAnswerOut(
            useful=answer.useful,
            content=answer.content,
            beginner_explanation=answer.beginner_explanation,
            code_example=answer.code_example,
            sources=[SourceInfoOut(**dataclasses.asdict(s)) for s in answer.sources],
            bug_detail=(
                BugDetailOut(**dataclasses.asdict(answer.bug_detail))
                if answer.bug_detail else None
            ),
        ),
        duration_ms=duration_ms,
        conversation_id=conv.id,
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        resolved_question=resolved,
    )


@router.post("/simple", response_model=QAResponse)
async def simple_ask(
    req: AskRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_roles("admin", "teacher")),
) -> QAResponse:
    """直接调用 DeepSeek（不做意图识别，不检索知识库），保存会话。"""
    if not req.message.strip():
        return QAResponse(success=False, error="message 不能为空")

    question = req.message.strip()
    conv = await conversation_service.get_or_create_conversation(db, req.conversation_id, question)
    await conversation_service.add_message(db, conv.id, "user", question)

    start = time.monotonic()
    try:
        data = await deepseek_service.ask_structured(question)
        duration_ms = int((time.monotonic() - start) * 1000)
        await conversation_service.add_message(
            db, conv.id, "assistant", data.answer,
            extra={
                "question_type": data.question_type,
                "need_more_info": data.need_more_info,
                "duration_ms": duration_ms,
                "beginner_explanation": data.beginner_explanation,
                "code_example": data.code_example,
                "need_more_info_fields": data.need_more_info_fields,
            },
        )
        return QAResponse(success=True, data=data, duration_ms=duration_ms, conversation_id=conv.id)
    except (ValueError, RuntimeError) as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        return QAResponse(success=False, error=str(e), duration_ms=duration_ms, conversation_id=conv.id)
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.exception("simple_ask 未知错误")
        return QAResponse(success=False, error=f"服务器内部错误: {e}", duration_ms=duration_ms, conversation_id=conv.id)
