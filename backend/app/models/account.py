import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean
from ..core.database import Base

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = Column(String(50), nullable=False)  # linkedin, twitter, bluesky, etc.
    account_name = Column(String(255), nullable=False)
    account_urn = Column(String(255), nullable=True)  # e.g., urn:li:person:xyz for LinkedIn
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
