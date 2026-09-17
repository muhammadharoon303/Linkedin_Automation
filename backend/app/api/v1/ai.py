from fastapi import APIRouter
from typing import Dict, Any
from ...schemas.ai import DirectGenerationRequest, DirectGenerationResponse, OllamaModelListResponse
from ...services.ollama_service import ollama_service

router = APIRouter(prefix="/ai", tags=["AI Engine"])

@router.get("/models", response_model=OllamaModelListResponse)
async def list_models():
    models = await ollama_service.list_models()
    return OllamaModelListResponse(models=models)

@router.get("/health")
async def check_ai_health() -> Dict[str, Any]:
    return await ollama_service.check_health()

@router.post("/generate", response_model=DirectGenerationResponse)
async def generate_direct_content(req: DirectGenerationRequest):
    content = await ollama_service.generate_post(
        platform=req.platform,
        topic=req.topic,
        reference_context=req.reference_context or "",
        tone=req.tone or "Professional & Insightful",
        hook_style=req.hook_style or "Contrarian / Thought-Provoking",
        emoji_density=req.emoji_density or "Minimal (1-3 relevant)",
        hashtag_count=req.hashtag_count if req.hashtag_count is not None else 3,
        call_to_action=req.call_to_action or "What are your thoughts on this? Let me know below!",
        target_audience=req.target_audience or "Tech professionals & founders",
        custom_instructions=req.custom_instructions or "",
        model=req.model
    )
    return DirectGenerationResponse(
        platform=req.platform,
        topic=req.topic,
        content=content,
        model_used=req.model or "default"
    )
