from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SupportGPT AI"
    API_V1_STR: str = "/api/v1"

    # DATABASE
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/supportgpt"

    # SECURITY
    JWT_SECRET_KEY: str = "supersecretkey-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # REDIS
    REDIS_URL: str = "redis://localhost:6379/0"

    # GOOGLE OAUTH
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # EMAIL
    RESEND_API_KEY: str = ""

    # VECTOR DATABASE
    QDRANT_URL: str = ":memory:"
    QDRANT_API_KEY: str = ""

    # AI
    GEMINI_API_KEY: str = ""

    # FRONTEND
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()