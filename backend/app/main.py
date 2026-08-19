from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.core.exceptions import setup_exception_handlers
from app.dependencies.rate_limit import init_redis, close_redis
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.core.database import SessionLocal
from app.core.init_db import init_db
from app.api.v1.health import router as health_router
from app.services.scheduler_service import scheduler

from slowapi import Limiter, _rate_limit_exceeded_handler # type: ignore
from slowapi.util import get_remote_address # type: ignore
from slowapi.errors import RateLimitExceeded # type: ignore
from slowapi.middleware import SlowAPIMiddleware # type: ignore

limiter = Limiter(key_func=get_remote_address)

import sentry_sdk # type: ignore
from sentry_sdk.integrations.fastapi import FastApiIntegration # type: ignore
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration # type: ignore
from opentelemetry import trace # type: ignore
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor # type: ignore
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor # type: ignore
from opentelemetry.instrumentation.redis import RedisInstrumentor # type: ignore

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    
    # Initialize DB (create roles and permissions)
    async with SessionLocal() as db:
        await init_db(db)
        
    scheduler.start()
        
    yield
    
    scheduler.stop()
    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

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

# Initialize Sentry if configured
if getattr(settings, "SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Initialize OpenTelemetry if configured
if getattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", None):
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()

app.include_router(health_router, prefix="/health", tags=["Health"])

app.include_router(api_router, prefix=settings.API_V1_STR)
