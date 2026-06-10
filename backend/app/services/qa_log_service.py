"""QA 日志服务：QALogContext 收集链路步骤，save_log 异步持久化到数据库。

设计原则：日志写入不能阻塞主流程，任何异常都只记录不上抛。
"""
import json
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger("app.services.qa_log")


@dataclass
class LogStep:
    step_name: str
    service_name: str
    input_data: dict
    output_data: dict
    duration_ms: int
    status: str  # "SUCCESS" | "FAILED"
    error_message: str = ""


class QALogContext:
    """单次问答请求的日志上下文，贯穿整个 pipeline。"""

    def __init__(self, conversation_id: int | None, question: str, user_id: int | None = None) -> None:
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.question = question
        self.resolved_question = question
        self.intent = ""
        self.status = "SUCCESS"
        self.total_duration_ms = 0
        self.source_count = 0
        self.final_answer = ""
        self.steps: list[LogStep] = []
        self._t0 = time.monotonic()

    def add_step(self, step: LogStep) -> None:
        self.steps.append(step)
        if step.status == "FAILED":
            self.status = "FAILED"

    def finalize(self, final_answer: str = "", source_count: int = 0) -> None:
        self.total_duration_ms = int((time.monotonic() - self._t0) * 1000)
        self.final_answer = final_answer[:2000] if final_answer else ""
        self.source_count = source_count


def _safe_json(data: dict) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception:
        return "{}"


async def save_log(ctx: QALogContext) -> None:
    """将 QALogContext 持久化到数据库（由 BackgroundTask 调用，失败不影响主流程）。"""
    from app.db.database import AsyncSessionLocal
    from app.models.qa_log import QALog, QALogStep

    async with AsyncSessionLocal() as db:
        try:
            log = QALog(
                user_id=ctx.user_id,
                conversation_id=ctx.conversation_id,
                question=ctx.question[:500],
                resolved_question=ctx.resolved_question[:500],
                intent=ctx.intent,
                status=ctx.status,
                total_duration_ms=ctx.total_duration_ms,
                source_count=ctx.source_count,
                final_answer=ctx.final_answer,
            )
            db.add(log)
            await db.flush()

            for step in ctx.steps:
                db.add(
                    QALogStep(
                        log_id=log.id,
                        step_name=step.step_name,
                        service_name=step.service_name,
                        input_json=_safe_json(step.input_data),
                        output_json=_safe_json(step.output_data),
                        duration_ms=step.duration_ms,
                        status=step.status,
                        error_message=step.error_message,
                    )
                )

            await db.commit()
            logger.info(
                "QA 日志保存: log_id=%d status=%s steps=%d",
                log.id,
                ctx.status,
                len(ctx.steps),
            )
        except Exception:
            logger.exception("QA 日志保存失败")
