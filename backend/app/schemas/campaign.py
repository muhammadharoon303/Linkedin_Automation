from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CampaignCreate(BaseModel):
    title: str
    start_date: datetime
    end_date: datetime
    platforms: List[str] = ["linkedin", "tiktok"]
    posting_hours: List[int] = [9, 17]
    auto_posting: bool = True
    model: Optional[str] = "llama3.2:latest"

class CampaignResponse(BaseModel):
    id: str
    project_id: str
    title: str
    start_date: datetime
    end_date: datetime
    platforms: List[str]
    posting_hours: List[int]
    auto_posting: bool
    status: str
    created_at: datetime
    total_posts: Optional[int] = 0

    class Config:
        from_attributes = True
