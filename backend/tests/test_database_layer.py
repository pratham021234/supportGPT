import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.repositories.base import BaseRepository
from app.schemas.common import PaginationParams, FilterParams
from app.models.ticket import Ticket
from pydantic import BaseModel
import uuid
import datetime

# Setup in-memory sqlite
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

class CreateTicketSchema(BaseModel):
    title: str
    description: str
    workspace_id: uuid.UUID
    priority: str = "LOW"
    status: str = "OPEN"

class UpdateTicketSchema(BaseModel):
    title: str

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session):
    repo = BaseRepository[Ticket, CreateTicketSchema, UpdateTicketSchema](Ticket)
    
    workspace_id = uuid.uuid4()
    obj_in = CreateTicketSchema(title="Test Ticket", description="Desc", workspace_id=workspace_id)
    
    # Test Create
    ticket = await repo.create(db_session, obj_in=obj_in)
    assert ticket.id is not None
    assert ticket.title == "Test Ticket"
    
    # Test Get
    retrieved = await repo.get(db_session, id=ticket.id)
    assert retrieved is not None
    assert retrieved.id == ticket.id
    
    # Test Get Multi
    multi = await repo.get_multi(db_session)
    assert len(multi) == 1

@pytest.mark.asyncio
async def test_repository_soft_delete(db_session):
    repo = BaseRepository[Ticket, CreateTicketSchema, UpdateTicketSchema](Ticket)
    workspace_id = uuid.uuid4()
    
    obj_in = CreateTicketSchema(title="Test Ticket", description="Desc", workspace_id=workspace_id)
    ticket = await repo.create(db_session, obj_in=obj_in)
    
    # Delete (soft delete because Ticket has is_deleted)
    await repo.delete(db_session, id=ticket.id)
    
    # Get should return None because is_deleted=True
    retrieved = await repo.get(db_session, id=ticket.id)
    assert retrieved is None

@pytest.mark.asyncio
async def test_repository_paginated(db_session):
    repo = BaseRepository[Ticket, CreateTicketSchema, UpdateTicketSchema](Ticket)
    workspace_id = uuid.uuid4()
    
    obj_in = CreateTicketSchema(title="Test Ticket 1", description="Desc", workspace_id=workspace_id)
    await repo.create(db_session, obj_in=obj_in)
    
    obj_in2 = CreateTicketSchema(title="Test Ticket 2", description="Desc", workspace_id=workspace_id)
    await repo.create(db_session, obj_in=obj_in2)
    
    pagination = PaginationParams(page=1, limit=1)
    result = await repo.get_paginated(db_session, pagination=pagination)
    
    assert result["total"] == 2
    assert len(result["items"]) == 1
    assert result["pages"] == 2
