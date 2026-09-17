import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Explicitly load .env file from project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path, override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Social AI Automation Content Engine"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./social_ai.db"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    DEFAULT_OLLAMA_MODEL: str = "llama3.2:latest"
    ENABLE_SCHEDULER: bool = True
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/oauth/linkedin/callback"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
