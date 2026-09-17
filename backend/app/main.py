from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .models import * # noqa: F401, F403
from .api.v1.router import api_router
from .services.scheduler_service import start_scheduler, stop_scheduler
from .services.ollama_service import ollama_service

# Initialize SQLite database schema
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background scheduler
    if settings.ENABLE_SCHEDULER:
        start_scheduler()
    yield
    # Shutdown: Clean up background scheduler
    if settings.ENABLE_SCHEDULER:
        stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Free AI Social Media Content Engine using FastAPI, Ollama, and SQLite",
    lifespan=lifespan
)

# CORS middleware for Flutter Android / Web connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def root_health():
    ai_status = await ollama_service.check_health()
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "database": "sqlite_connected",
        "ai_engine": ai_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
