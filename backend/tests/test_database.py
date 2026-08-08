import pytest
from sqlalchemy import text
from app.core.database import Base

@pytest.mark.asyncio
async def test_database_connectivity(db_session):
    """Test basic database connectivity via the session"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_models_have_workspace_id():
    """Verify tenant isolation by checking if core models have workspace_id"""
    tenant_models = [
        "Agent", "Customer", "Ticket", "Conversation", "KnowledgeSource", "WorkspaceMember"
    ]
    
    for table_name, table in Base.metadata.tables.items():
        class_name = "".join(x.title() for x in table_name.split("_"))
        
        # A rough check if a known tenant-bound table has workspace_id
        if any(t.lower() in table_name.lower() for t in tenant_models):
            if table_name not in ["customers", "agents", "tickets", "conversations"]:
                continue
                
            has_workspace = "workspace_id" in table.columns
            assert has_workspace, f"Table {table_name} is missing workspace_id for tenant isolation!"

def test_metadata_tables_exist():
    """Test if SQLAlchemy metadata has discovered all our models"""
    tables = Base.metadata.tables.keys()
    assert "users" in tables
    assert "workspaces" in tables
    assert "agents" in tables
    assert "tickets" in tables
    assert len(tables) > 20 # Ensure all were imported correctly via __init__.py
