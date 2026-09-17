import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from ..core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    target_audience = Column(String(255), default="Tech professionals and founders")
    tone_preference = Column(String(100), default="Professional & Thought-Provoking")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="project", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="project", cascade="all, delete-orphan")
