"""Reusable assets for post-course operations."""
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    scene = Column(Text, nullable=True)
    stage = Column(Text, nullable=True)
    direction = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
