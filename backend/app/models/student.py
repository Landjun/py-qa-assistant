"""Student model for post-course student operations."""
from sqlalchemy import Column, Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import StageEnum


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    wechat = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    course_name = Column(String(200), nullable=True)
    class_name = Column(String(200), nullable=True)
    graduation_date = Column(Date, nullable=True)
    current_direction = Column(String(200), nullable=True)
    current_stage = Column(Enum(StageEnum, native_enum=False), nullable=False, default=StageEnum.刚结课)
    intent_level = Column(String(50), nullable=True)
    owner = Column(String(100), nullable=True)
    last_interaction_at = Column(DateTime, nullable=True)
    next_follow_time = Column(DateTime, nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    chat_records = relationship("ChatRecord", back_populates="student", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="student", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="student", cascade="all, delete-orphan")
    stage_logs = relationship("StageLog", back_populates="student", cascade="all, delete-orphan")
