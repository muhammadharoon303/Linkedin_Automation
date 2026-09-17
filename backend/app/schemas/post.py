from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    project_id: str
    campaign_id: Optional[str] = None
    platform: str
    day_number: int = 1
    topic: str
    hook: Optional[str] = ""
    content: str
    scheduled_time: datetime
    auto_publish: bool = True
    status: Optional[str] = "scheduled"

class PostUpdate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    auto_publish: Optional[bool] = None

class PostResponse(BaseModel):
    id: str
    project_id: str
    campaign_id: Optional[str] = None
    platform: str
    day_number: int
    topic: str
    hook: Optional[str] = ""
    content: str
    status: str
    scheduled_time: datetime
    published_time: Optional[datetime] = None
    auto_publish: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DailyContentGenerationRequest(BaseModel):
    project_id: str
    campaign_id: Optional[str] = None
    day_number: int = 1
    topic: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    model: Optional[str] = "llama3.2:latest"

class DualPlatformGenerationResponse(BaseModel):
    day_number: int
    topic: str
    linkedin_post: PostResponse
    tiktok_script: PostResponse
