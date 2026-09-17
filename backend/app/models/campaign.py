import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    platforms_json = Column(Text, default='["linkedin", "tiktok"]')
    posting_hours_json = Column(Text, default='[9, 17]')
    auto_posting = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="campaigns")
    posts = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")
