from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.core.exceptions import setup_exception_handlers
from app.dependencies.rate_limit import init_redis, close_redis

from app.core.database import SessionLocal
from app.core.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    
    # Initialize DB (create roles and permissions)
    async with SessionLocal() as db:
        await init_db(db)
        
    yield
    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Required for OAuthlib
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)

setup_exception_handlers(app)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get(f"{settings.API_V1_STR}/health")
async def api_health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix=settings.API_V1_STR)
