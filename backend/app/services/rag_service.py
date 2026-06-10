"""RAG 问答服务：意图路由 → 知识库检索 / 闲聊 / 反馈处理 → DeepSeek 答疑。"""
import dataclasses
import json
import logging
import re
import time
from dataclasses import dataclass, field

from openai import APIConnectionError, APIError, AsyncOpenAI, AuthenticationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services import conversation_service, retrieval_service

logger = logging.getLogger("app.services.rag")


# ─── 数据类 ────────────────────────────────────────────────────────────────────

@dataclass
class SourceInfo:
    document_id: int
    chunk_id: int
    source: str
    score: float
    image_path: str | None = None


@dataclass
class BugDetail:
    error_type: str
    plain_explanation: str
    likely_causes: list[str]
    fix_steps: list[str]
    before_code: str
    after_code: str
    need_more_info: bool
    need_more_info_fields: list[str]


@dataclass
class LessonInfo:
    lesson_no: int
    lesson_id: int
    title: str
    summary: str | None
    assets: list[dict]  # [{"asset_type":..., "filename":..., "url":...}]


@dataclass
class RAGAnswer:
    useful: bool
    content: str
    beginner_explanation: str
    code_example: str
    sources: list[SourceInfo] = field(default_factory=list)
    no_retrieval: bool = False
    bug_detail: "BugDetail | None" = None
    lesson_fallback: bool = False  # True → lesson-scoped search had no results, fell back to global


# ─── 系统提示词 ────────────────────────────────────────────────────────────────

_PYTHON_QA_SYSTEM = """\
你是 Python 学习答疑客服助手。
你需要根据【知识库内容】和【用户问题】回答用户。

回复原则：
1. 中文回复。
2. 先用大白话解释。
3. 再给最小代码示例。
4. 回答必须尽量依据【知识库内容】。
5. 如果知识库内容不足以回答，不要胡编，返回 useful=false。
6. 如果知识库内容相关，返回 useful=true。
7. 适合 Python 初学者。
8. 不超过 500 字。"""

_BUG_HELP_SYSTEM = """\
你是 Python 报错排查教练。
你的任务不是只给答案，而是帮助初学者看懂报错、定位原因、完成修复。

## 回复原则

1. 先判断报错类型。
2. 用一句大白话解释这个报错是什么意思。
3. 说明最可能的原因。
4. 给出最小修复步骤。
5. 如有必要，给出修复前和修复后的代码。
6. 不要编造用户没有提供的代码。
7. 如果信息不足，说明还缺什么信息。
8. 回复适合 Python 初学者。
9. 中文回复。

输出 JSON，不得包含其他文本：

{
  "useful": true,
  "error_type": "报错类型，例如 ModuleNotFoundError",
  "plain_explanation": "大白话解释",
  "likely_causes": ["原因1", "原因2"],
  "fix_steps": ["步骤1", "步骤2"],
  "before_code": "修复前代码，没有则为空字符串",
  "after_code": "修复后代码，没有则为空字符串",
  "need_more_info": false,
  "need_more_info_fields": [],
  "sources": []
}"""


def _build_bug_user_msg(error_content: str, history_text: str, knowledge_context: str) -> str:
    return f"""## 输入

【用户报错内容】
{error_content}

【对话历史】
{history_text}

【知识库检索结果】
{knowledge_context}"""

_CHAT_SYSTEM = """\
你是 Python 学习答疑客服助手，正在和用户进行轻松的日常交流。

规则：
1. 用中文友好回复。
2. 回复简洁（不超过 50 字）。
3. 如果用户有 Python 学习需求，鼓励提问。

输出 JSON，不得包含其他文本：
{
  "useful": true,
  "content": "你的回复",
  "beginner_explanation": "",
  "code_example": ""
}"""

_FEEDBACK_CONTENT = "感谢您的反馈！我们会认真记录并持续改进，如有 Python 学习问题随时欢迎提问。"


# ─── JSON 工具 ─────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\{[\s\S]+\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {"useful": True, "content": text, "beginner_explanation": "", "code_example": ""}


def _build_rag_user_msg(knowledge_context: str, question: str) -> str:
    return f"""【知识库内容】
{knowledge_context}

【用户问题】
{question}

输出 JSON，不得包含其他文本：

{{
  "useful": true,
  "content": "直接给用户看的回答",
  "beginner_explanation": "更大白话的解释",
  "code_example": "最小代码示例，没有则为空字符串"
}}"""


# ─── DeepSeek 调用 ─────────────────────────────────────────────────────────────

def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)


async def _call_deepseek(system: str, user_msg: str, temperature: float = 0.3, max_tokens: int = 1500, log_ctx=None) -> dict:
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请检查 .env 文件")

    t0 = time.monotonic()
    input_data = {
        "model": settings.deepseek_model,
        "system_preview": system[:100],
        "user_preview": user_msg[:200],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    def _log(output_data: dict, status: str, error_message: str = "") -> None:
        if log_ctx is None:
            return
        from app.services.qa_log_service import LogStep
        log_ctx.add_step(LogStep(
            step_name="deepseek_generation",
            service_name="deepseek",
            input_data=input_data,
            output_data=output_data,
            duration_ms=int((time.monotonic() - t0) * 1000),
            status=status,
            error_message=error_message,
        ))

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        usage = response.usage
        logger.info("DeepSeek 响应: tokens=%s", usage)
        parsed = _extract_json(raw)
        _log({
            "content_preview": raw[:300],
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }, "SUCCESS")
        return parsed
    except AuthenticationError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError("DeepSeek API Key 无效，请确认密钥是否正确") from e
    except APIConnectionError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError(f"无法连接 DeepSeek，请检查网络: {e}") from e
    except APIError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError(f"DeepSeek API 错误: {e.message}") from e


# ─── 私有 AI 处理函数（不管理会话） ────────────────────────────────────────────

def _lesson_system_suffix(lesson_info: "LessonInfo") -> str:
    suffix = f"\n\n【当前课节】第 {lesson_info.lesson_no} 节：{lesson_info.title}"
    if lesson_info.summary:
        suffix += f"\n知识点摘要：{lesson_info.summary}"
    suffix += "\n请围绕该节知识点回答。界面已为学员展示课件/代码下载链接，无需在文字中重复列出链接。"
    return suffix


async def _rag_answer(
    db: AsyncSession,
    question: str,
    system_prompt: str,
    lesson_id: int | None = None,
    lesson_info: "LessonInfo | None" = None,
    log_ctx=None,
) -> RAGAnswer:
    """知识库检索 + DeepSeek，返回 RAGAnswer（不管理会话）。

    当 lesson_id 指定时先做课节限定检索，若无结果自动降级为全库检索（lesson_fallback=True）。
    """
    if lesson_info:
        system_prompt = system_prompt + _lesson_system_suffix(lesson_info)

    lesson_fallback = False
    retrieval_results = []
    no_retrieval = False

    try:
        retrieval_results, _ = await retrieval_service.search(
            db, question, top_k=3, score_threshold=0.5,
            lesson_id=lesson_id, log_ctx=log_ctx,
        )
        if not retrieval_results and lesson_id is not None:
            # 课节内无匹配内容 → 降级全库
            lesson_fallback = True
            logger.info("课节 %d 无检索结果，降级全库检索", lesson_id)
            retrieval_results, _ = await retrieval_service.search(
                db, question, top_k=3, score_threshold=0.5, log_ctx=log_ctx,
            )
        no_retrieval = len(retrieval_results) == 0
        logger.info("RAG 检索: %d 条结果 lesson_fallback=%s", len(retrieval_results), lesson_fallback)
    except Exception as e:
        logger.warning("检索异常，降级无上下文: %s", e)
        no_retrieval = True

    sources: list[SourceInfo] = []
    if retrieval_results:
        parts: list[str] = []
        for r in retrieval_results:
            parts.append(f"【来源：{r.source}】\n{r.content}")
            sources.append(SourceInfo(document_id=r.document_id, chunk_id=r.chunk_id, source=r.source, score=r.score, image_path=r.image_path))
        knowledge_context = "\n\n".join(parts)
        if lesson_fallback and lesson_info:
            knowledge_context = (
                f"（第 {lesson_info.lesson_no} 节课件暂未入库，以下为通用知识库内容）\n\n"
                + knowledge_context
            )
    else:
        knowledge_context = "（暂无相关知识库内容，请根据 Python 基础知识尽量回答）"

    user_msg = _build_rag_user_msg(knowledge_context, question)
    logger.info("RAG DeepSeek: knowledge_len=%d", len(knowledge_context))
    parsed = await _call_deepseek(system_prompt, user_msg, log_ctx=log_ctx)

    return RAGAnswer(
        useful=bool(parsed.get("useful", True)),
        content=str(parsed.get("content", "")),
        beginner_explanation=str(parsed.get("beginner_explanation", "")),
        code_example=str(parsed.get("code_example", "")),
        sources=sources,
        no_retrieval=no_retrieval,
        lesson_fallback=lesson_fallback,
    )


async def _bug_rag_answer(
    db: AsyncSession,
    question: str,
    history_text: str = "（无历史记录）",
    lesson_id: int | None = None,
    lesson_info: "LessonInfo | None" = None,
    log_ctx=None,
) -> RAGAnswer:
    """BUG_HELP 专用：知识库检索 + 报错排查教练提示词，返回带 BugDetail 的 RAGAnswer。"""
    bug_system = _BUG_HELP_SYSTEM
    if lesson_info:
        bug_system = bug_system + _lesson_system_suffix(lesson_info)

    lesson_fallback = False
    no_retrieval = False
    retrieval_results = []
    try:
        retrieval_results, _ = await retrieval_service.search(
            db, question, top_k=3, score_threshold=0.4,
            lesson_id=lesson_id, log_ctx=log_ctx,
        )
        if not retrieval_results and lesson_id is not None:
            lesson_fallback = True
            retrieval_results, _ = await retrieval_service.search(
                db, question, top_k=3, score_threshold=0.4, log_ctx=log_ctx,
            )
        no_retrieval = len(retrieval_results) == 0
        logger.info("BUG 检索: %d 条结果", len(retrieval_results))
    except Exception as e:
        logger.warning("BUG 检索异常: %s", e)
        no_retrieval = True

    sources: list[SourceInfo] = []
    if retrieval_results:
        parts: list[str] = []
        for r in retrieval_results:
            parts.append(f"【来源：{r.source}】\n{r.content}")
            sources.append(SourceInfo(document_id=r.document_id, chunk_id=r.chunk_id, source=r.source, score=r.score, image_path=r.image_path))
        knowledge_context = "\n\n".join(parts)
    else:
        knowledge_context = "（暂无相关知识库内容）"

    user_msg = _build_bug_user_msg(question, history_text, knowledge_context)
    logger.info("BUG DeepSeek: knowledge_len=%d", len(knowledge_context))
    parsed = await _call_deepseek(bug_system, user_msg, max_tokens=2000, log_ctx=log_ctx)

    bug_detail = BugDetail(
        error_type=str(parsed.get("error_type", "")),
        plain_explanation=str(parsed.get("plain_explanation", "")),
        likely_causes=[str(c) for c in parsed.get("likely_causes", [])],
        fix_steps=[str(s) for s in parsed.get("fix_steps", [])],
        before_code=str(parsed.get("before_code", "")),
        after_code=str(parsed.get("after_code", "")),
        need_more_info=bool(parsed.get("need_more_info", False)),
        need_more_info_fields=[str(f) for f in parsed.get("need_more_info_fields", [])],
    )

    content = bug_detail.plain_explanation or str(parsed.get("content", ""))

    return RAGAnswer(
        useful=bool(parsed.get("useful", True)),
        content=content,
        beginner_explanation="",
        code_example=bug_detail.after_code,
        sources=sources,
        no_retrieval=no_retrieval,
        bug_detail=bug_detail,
        lesson_fallback=lesson_fallback,
    )


async def _chat_answer(question: str, log_ctx=None) -> RAGAnswer:
    """闲聊模式：直接调用 DeepSeek，不检索知识库。"""
    try:
        parsed = await _call_deepseek(_CHAT_SYSTEM, question, temperature=0.7, max_tokens=300, log_ctx=log_ctx)
    except Exception as e:
        logger.warning("CHAT DeepSeek 失败，使用默认回复: %s", e)
        parsed = {"useful": True, "content": "你好！有什么 Python 学习问题需要帮助吗？", "beginner_explanation": "", "code_example": ""}

    return RAGAnswer(
        useful=True,
        content=str(parsed.get("content", "你好！")),
        beginner_explanation="",
        code_example="",
        sources=[],
        no_retrieval=True,
    )


def _feedback_answer() -> RAGAnswer:
    """反馈处理：直接返回感谢信息，不调用 DeepSeek。"""
    return RAGAnswer(
        useful=True,
        content=_FEEDBACK_CONTENT,
        beginner_explanation="",
        code_example="",
        sources=[],
        no_retrieval=True,
    )


# ─── 公开接口 ──────────────────────────────────────────────────────────────────

async def route_by_intent(
    db: AsyncSession,
    conv_id: int,
    resolved_question: str,
    intent: str,
    history_text: str = "（无历史记录）",
    lesson_id: int | None = None,
    lesson_info: "LessonInfo | None" = None,
    log_ctx=None,
) -> tuple[RAGAnswer, int]:
    """根据意图路由到对应 AI 处理，保存 AI 回复，返回 (answer, duration_ms)。"""
    t0 = time.monotonic()

    if intent == "FEEDBACK":
        answer = _feedback_answer()
    elif intent == "CHAT":
        answer = await _chat_answer(resolved_question, log_ctx=log_ctx)
    elif intent == "BUG_HELP":
        answer = await _bug_rag_answer(
            db, resolved_question, history_text,
            lesson_id=lesson_id, lesson_info=lesson_info, log_ctx=log_ctx,
        )
    else:  # PYTHON_QA (default)
        answer = await _rag_answer(
            db, resolved_question, _PYTHON_QA_SYSTEM,
            lesson_id=lesson_id, lesson_info=lesson_info, log_ctx=log_ctx,
        )

    duration_ms = int((time.monotonic() - t0) * 1000)

    extra: dict = {
        "type": "rag",
        "intent": intent,
        "useful": answer.useful,
        "beginner_explanation": answer.beginner_explanation,
        "code_example": answer.code_example,
        "sources": [dataclasses.asdict(s) for s in answer.sources],
        "no_retrieval": answer.no_retrieval,
        "duration_ms": duration_ms,
    }
    if answer.bug_detail is not None:
        extra["bug_detail"] = dataclasses.asdict(answer.bug_detail)

    await conversation_service.add_message(db, conv_id, "assistant", answer.content, extra=extra)

    logger.info("route_by_intent: intent=%s sources=%d no_retrieval=%s duration=%dms",
                intent, len(answer.sources), answer.no_retrieval, duration_ms)
    return answer, duration_ms


async def ask_with_rag(
    db: AsyncSession,
    message: str,
    conversation_id: int | None = None,
) -> tuple[RAGAnswer, int, int]:
    """（兼容旧接口）完整 RAG 流程，默认走 PYTHON_QA，返回 (answer, duration_ms, conv_id)。"""
    t0 = time.monotonic()
    conv = await conversation_service.get_or_create_conversation(db, conversation_id, message)
    await conversation_service.add_message(db, conv.id, "user", message)
    answer, llm_ms = await route_by_intent(db, conv.id, message, "PYTHON_QA")
    duration_ms = int((time.monotonic() - t0) * 1000)
    return answer, duration_ms, conv.id
