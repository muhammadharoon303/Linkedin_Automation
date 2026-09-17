from fastapi import APIRouter
from .projects import router as projects_router
from .documents import router as documents_router
from .campaigns import router as campaigns_router
from .posts import router as posts_router
from .ai import router as ai_router
from .oauth import router as oauth_router
from .analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(campaigns_router)
api_router.include_router(posts_router)
api_router.include_router(ai_router)
api_router.include_router(oauth_router)
api_router.include_router(analytics_router)
