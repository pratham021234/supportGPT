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
from app.api.v1.health import router as health_router
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

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
