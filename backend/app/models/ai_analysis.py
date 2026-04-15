"""Mock AI analysis outputs for chat records."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_record_id = Column(Integer, ForeignKey("chat_records.id", ondelete="SET NULL"), nullable=True)
    stage = Column(Text, nullable=True)
    main_need = Column(Text, nullable=True)
    core_concerns = Column(Text, nullable=True)
    interest_direction = Column(Text, nullable=True)
    risk_points = Column(Text, nullable=True)
    recommended_course = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    tags_json = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    student = relationship("Student", back_populates="ai_analyses")
    chat_record = relationship("ChatRecord", back_populates="analyses")
