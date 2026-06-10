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
from app.services import conversation_service, course_service, deepseek_service, intent_service, lesson_resolver, qa_log_service, rag_service, vision_service
from app.services.auth_service import get_current_user, require_roles
from app.services.intent_service import IntentResult
from app.services.qa_log_service import LogStep, QALogContext
from app.services.rag_service import LessonInfo

logger = logging.getLogger("app.api.chat")
router = APIRouter(prefix="/api/chat", tags=["chat"])


class AskRequest(BaseModel):
    message: str = ""
    conversation_id: int | None = None
    image_base64: str | None = None


# ─── /ask 响应模型 ────────────────────────────────────────────────────────────

class SourceInfoOut(BaseModel):
    document_id: int
    chunk_id: int
    source: str
    score: float
    image_path: str | None = None


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
    image_understanding: dict | None = None
    lesson_context: dict | None = None


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
    """意图识别 → 路由 → RAG 问答 / 闲聊 / 反馈处理，自动保存会话。支持可选图片理解。"""
    message = req.message.strip()
    if not message and not req.image_base64:
        return RAGResponse(success=False, error="请输入问题或上传图片")

    t0 = time.monotonic()
    user_id = current_user.id

    # 1. 获取/创建会话（归属当前登录用户）
    conv_title = message or "图片提问"
    conv = await conversation_service.get_or_create_conversation(
        db, req.conversation_id, conv_title, user_id=user_id
    )

    # 初始化日志上下文
    log_ctx = QALogContext(conversation_id=conv.id, question=message, user_id=user_id)

    # 2. 图片理解（如有）
    image_understanding: dict | None = None
    effective_message = message
    if req.image_base64:
        try:
            image_understanding = await vision_service.describe_image(
                req.image_base64, user_hint=message, log_ctx=log_ctx
            )
            ocr = image_understanding.get("ocr_text", "").strip()
            summary = image_understanding.get("summary", "").strip()
            parts: list[str] = []
            if summary:
                parts.append(f"【图片内容】{summary}")
            if ocr:
                parts.append(f"【图中文字/代码】\n{ocr}")
            if message:
                parts.append(f"【用户问题】{message}")
            effective_message = "\n\n".join(parts) if parts else message
        except (ValueError, RuntimeError) as e:
            log_ctx.finalize("")
            background_tasks.add_task(qa_log_service.save_log, log_ctx)
            return RAGResponse(success=False, error=str(e), conversation_id=conv.id)

    if not effective_message:
        effective_message = "请根据图片内容解答"

    # 3. 获取历史消息，用于意图识别的指代消解
    history_msgs = await conversation_service.get_conversation_messages(db, conv.id)
    history_text = intent_service.format_history(history_msgs)

    # 4. 意图识别（失败自动降级）
    intent_result = await _safe_recognize_intent(history_text, effective_message, log_ctx=log_ctx)

    # 4.5 课节解析 — 从消息+历史中提取节次，并查库获取课节详情
    lesson_info: LessonInfo | None = None
    lesson_context: dict | None = None
    _lesson_no = lesson_resolver.extract_lesson_no(message, history_text)
    if _lesson_no is not None:
        _t_resolve = time.monotonic()
        _lesson_db = await course_service.find_lesson_by_no(db, _lesson_no)
        if _lesson_db:
            _assets = await course_service.list_assets(db, _lesson_db.id)
            _asset_list = [
                {"asset_type": a.asset_type, "filename": a.filename, "url": f"/static/{a.file_path}"}
                for a in _assets
            ]
            lesson_info = LessonInfo(
                lesson_no=_lesson_no,
                lesson_id=_lesson_db.id,
                title=_lesson_db.title,
                summary=_lesson_db.summary,
                assets=_asset_list,
            )
            lesson_context = {
                "lesson_no": _lesson_no,
                "title": _lesson_db.title,
                "summary": _lesson_db.summary,
                "assets": _asset_list,
                "fallback": False,
            }
            log_ctx.add_step(LogStep(
                step_name="lesson_resolve",
                service_name="lesson_resolver",
                input_data={"message": message[:200], "history_len": len(history_text)},
                output_data={"lesson_no": _lesson_no, "lesson_id": _lesson_db.id,
                             "title": _lesson_db.title, "asset_count": len(_assets)},
                duration_ms=int((time.monotonic() - _t_resolve) * 1000),
                status="SUCCESS",
            ))
        else:
            log_ctx.add_step(LogStep(
                step_name="lesson_resolve",
                service_name="lesson_resolver",
                input_data={"message": message[:200]},
                output_data={"lesson_no": _lesson_no, "error": "课程尚未初始化或课节不存在"},
                duration_ms=int((time.monotonic() - _t_resolve) * 1000),
                status="FAILED",
            ))

    # 5. 保存用户消息（仅保存原始文字，不存储 base64）
    user_msg_text = message if message else "（发送了一张图片）"
    await conversation_service.add_message(db, conv.id, "user", user_msg_text)

    resolved = intent_result.resolved_question or effective_message
    log_ctx.intent = intent_result.intent
    log_ctx.resolved_question = resolved

    # 6. 根据意图路由处理
    try:
        answer, _ = await rag_service.route_by_intent(
            db, conv.id, resolved, intent_result.intent, history_text,
            lesson_id=lesson_info.lesson_id if lesson_info else None,
            lesson_info=lesson_info,
            log_ctx=log_ctx,
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
            image_understanding=image_understanding,
        )
    except Exception:
        logger.exception("路由处理未知错误")
        log_ctx.finalize("")
        background_tasks.add_task(qa_log_service.save_log, log_ctx)
        return RAGResponse(
            success=False, error="服务器内部错误",
            conversation_id=conv.id,
            intent=intent_result.intent,
            image_understanding=image_understanding,
        )

    # 若课节检索降级了，更新 lesson_context 的 fallback 标志
    if lesson_context and answer.lesson_fallback:
        lesson_context["fallback"] = True

    duration_ms = int((time.monotonic() - t0) * 1000)
    log_ctx.finalize(answer.content, len(answer.sources))
    background_tasks.add_task(qa_log_service.save_log, log_ctx)

    logger.info("ask 完成: conv=%d intent=%s has_image=%s duration=%dms",
                conv.id, intent_result.intent, bool(req.image_base64), duration_ms)

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
        image_understanding=image_understanding,
        lesson_context=lesson_context,
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
