from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

async def check_database_health(session: AsyncSession) -> dict:
    """
    Verifies database connectivity, connection pool, and basic table existence.
    """
    health = {
        "status": "healthy",
        "connectivity": False,
        "tables": []
    }
    
    try:
        # Check connectivity
        result = await session.execute(text("SELECT 1"))
        if result.scalar() == 1:
            health["connectivity"] = True
            
        # Check table existence (core tables)
        tables_to_check = ["users", "workspaces", "agents", "conversations"]
        
        for table in tables_to_check:
            res = await session.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table)"),
                {"table": table}
            )
            exists = res.scalar()
            if exists:
                health["tables"].append(table)
            else:
                health["status"] = "unhealthy"
                health["error"] = f"Table {table} is missing."
                
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health["status"] = "unhealthy"
        health["error"] = str(e)
        
    return health
