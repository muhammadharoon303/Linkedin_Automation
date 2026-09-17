from pydantic import BaseModel
from typing import Optional, List

class DirectGenerationRequest(BaseModel):
    platform: str
    topic: str
    model: Optional[str] = "llama3.2:latest"
    tone: Optional[str] = "Professional & Insightful"
    hook_style: Optional[str] = "Contrarian / Thought-Provoking"
    emoji_density: Optional[str] = "Minimal (1-3 relevant)"
    hashtag_count: Optional[int] = 3
    call_to_action: Optional[str] = "What are your thoughts on this? Let me know below!"
    target_audience: Optional[str] = "Tech professionals & founders"
    custom_instructions: Optional[str] = ""
    reference_context: Optional[str] = ""

class DirectGenerationResponse(BaseModel):
    platform: str
    topic: str
    content: str
    model_used: str

class OllamaModelListResponse(BaseModel):
    models: List[str]
