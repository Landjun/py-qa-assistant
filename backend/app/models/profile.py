"""Profile model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_type = Column(Text, nullable=True)
    main_goal = Column(Text, nullable=True)
    main_concerns = Column(Text, nullable=True)
    interest_direction = Column(Text, nullable=True)
    risk_tags = Column(Text, nullable=True)
    recommended_course = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="profile")
