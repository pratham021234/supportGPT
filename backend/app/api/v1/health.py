from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.dependencies.db import get_db
import redis.asyncio as redis
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def health_check():
    """Basic health check indicating the process is alive."""
    return {"status": "ok", "service": "supportgpt-backend"}

@router.get("/live")
async def liveness_probe():
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}

@router.get("/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Readiness probe for Kubernetes ensuring dependencies are accessible."""
    deps = {
        "database": "unknown",
        "redis": "unknown"
    }
    status_code = 200
    
    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        deps["database"] = "ok"
    except Exception as e:
        logger.error(f"Database readiness failed: {e}")
        deps["database"] = "error"
        status_code = 503
        
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        deps["redis"] = "ok"
    except Exception as e:
        logger.error(f"Redis readiness failed: {e}")
        deps["redis"] = "error"
        status_code = 503
        
    response = {
        "status": "ready" if status_code == 200 else "unready",
        "dependencies": deps
    }
    
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=status_code, content=response)
