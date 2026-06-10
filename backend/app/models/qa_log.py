"""QA 日志数据模型：qa_logs（主记录）+ qa_log_steps（步骤明细）。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class QALog(Base):
    __tablename__ = "qa_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False, default="")
    resolved_question: Mapped[str] = mapped_column(Text, nullable=False, default="")
    intent: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUCCESS")
    total_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    final_answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False, index=True
    )

    steps: Mapped[list["QALogStep"]] = relationship(
        "QALogStep", back_populates="log", order_by="QALogStep.id"
    )


class QALogStep(Base):
    __tablename__ = "qa_log_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_id: Mapped[int] = mapped_column(Integer, ForeignKey("qa_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    input_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUCCESS")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    log: Mapped["QALog"] = relationship("QALog", back_populates="steps")
