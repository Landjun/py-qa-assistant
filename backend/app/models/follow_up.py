"""Follow-up records."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    follow_time = Column(DateTime, nullable=False)
    follow_method = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    student_feedback = Column(Text, nullable=True)
    judgment = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    next_follow_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    student = relationship("Student", back_populates="follow_ups")
