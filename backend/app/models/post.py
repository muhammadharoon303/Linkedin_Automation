import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    platform = Column(String(50), nullable=False)  # linkedin, tiktok, twitter, instagram, youtube, bluesky
    day_number = Column(Integer, default=1)
    topic = Column(String(255), nullable=False)
    hook = Column(Text, default="")
    content = Column(Text, nullable=False)
    status = Column(String(50), default="scheduled")  # draft, scheduled, published, failed
    scheduled_time = Column(DateTime, nullable=False)
    published_time = Column(DateTime, nullable=True)
    auto_publish = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    media_path = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")
