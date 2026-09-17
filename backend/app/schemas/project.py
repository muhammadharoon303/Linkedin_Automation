from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""
    target_audience: Optional[str] = "Tech professionals and founders"
    tone_preference: Optional[str] = "Professional & Thought-Provoking"

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
