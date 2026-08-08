import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SupportGPT AI"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/supportgpt")
    
    # SECURITY
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # REDIS (for Rate Limiting)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # OAUTH (Google)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # EMAIL (Resend)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    
    # VECTOR DATABASE (Qdrant)
    QDRANT_URL: str = os.getenv("QDRANT_URL", ":memory:")  # Use local memory by default for dev
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    # AI PROVIDERS
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # FRONTEND
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"

settings = Settings()
