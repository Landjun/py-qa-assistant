"""Lifecycle stage change logs."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class StageLog(Base):
    __tablename__ = "stage_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    from_stage = Column(Text, nullable=True)
    to_stage = Column(Text, nullable=False)
    remark = Column(Text, nullable=True)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())

    student = relationship("Student", back_populates="stage_logs")
