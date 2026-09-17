import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    raw_content = Column(Text, nullable=False)
    
    # Structured extracted metadata from Ollama
    topics_json = Column(Text, default="[]")          # List of extracted core topics
    benefits_json = Column(Text, default="[]")        # List of key benefits
    applications_json = Column(Text, default="[]")    # Practical use-cases
    technologies_json = Column(Text, default="[]")    # Tools, tech stack
    content_plan_json = Column(Text, default="[]")    # 30-day plan items/angles

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="documents")
