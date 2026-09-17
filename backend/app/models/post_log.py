import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from ..core.database import Base

class PostLog(Base):
    __tablename__ = "post_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    action = Column(String(50), default="publish_attempt")  # publish_attempt, retry, success, failure
    status = Column(String(50), nullable=False)  # success, error
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
