import asyncio
import sys
import os
import logging
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_schema():
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            # Check alembic version
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            if not version:
                logger.error("❌ Alembic migration state is missing or empty.")
                sys.exit(1)
            logger.info(f"✅ Alembic migration state is current: {version}")
            
            # Using run_sync for reflection
            def run_inspection(connection):
                inspector = inspect(connection)
                tables = inspector.get_table_names()
                
                # Verify core tables
                required_tables = [
                    "users", "workspaces", "agents", "conversations",
                    "tickets", "documents", "document_chunks"
                ]
                
                for table in required_tables:
                    if table not in tables:
                        logger.error(f"❌ Missing required table: {table}")
                        return False
                    logger.info(f"✅ Table '{table}' exists.")
                
                # Check indexes on users table
                indexes = inspector.get_indexes("users")
                index_names = [idx['name'] for idx in indexes]
                if not any("email" in idx for idx in index_names):
                    logger.error("❌ Missing index on users.email")
                    return False
                
                # Check enum types via raw SQL
                return True
                
            is_valid = await conn.run_sync(run_inspection)
            
            # Check Enums manually via raw SQL in async
            enum_query = """
            SELECT typname FROM pg_type WHERE typtype = 'e';
            """
            enums = await conn.execute(text(enum_query))
            enum_list = [e[0] for e in enums.fetchall()]
            
            required_enums = ['agentstatus', 'conversationstatus', 'ticketstatus']
            for req in required_enums:
                if req not in enum_list:
                    logger.error(f"❌ Missing PostgreSQL Enum: {req}")
                    is_valid = False
                else:
                    logger.info(f"✅ Enum '{req}' exists.")
            
            if is_valid:
                logger.info("🎉 Database validation passed completely!")
            else:
                logger.error("❌ Database validation failed.")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"❌ Database validation encountered an error: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(validate_schema())
