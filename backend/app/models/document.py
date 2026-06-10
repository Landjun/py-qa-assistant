"""文档 & 分块 ORM 模型。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, default="markdown")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faiss_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title_path: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)  # numpy float32 bytes
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
