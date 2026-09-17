from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str
    raw_content: str

class DocumentAnalysis(BaseModel):
    topics: List[str] = []
    benefits: List[str] = []
    applications: List[str] = []
    technologies: List[str] = []
    thirty_day_content_plan: List[str] = []

class DocumentResponse(BaseModel):
    id: str
    project_id: str
    title: str
    raw_content: str
    topics: List[str] = []
    benefits: List[str] = []
    applications: List[str] = []
    technologies: List[str] = []
    content_plan: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True
