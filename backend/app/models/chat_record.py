"""Chat records imported from post-course communication."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ChatRecord(Base):
    __tablename__ = "chat_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    student = relationship("Student", back_populates="chat_records")
    analyses = relationship("AIAnalysis", back_populates="chat_record")
